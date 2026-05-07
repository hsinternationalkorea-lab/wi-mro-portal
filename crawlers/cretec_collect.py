# -*- coding: utf-8 -*-
"""
크레텍 CTX 이력상품 자동 수집
- 모든 거래처(카테고리) 순회
- 각 카테고리에서 1년치 거래 이력 추출
- 컬럼: 상품코드, 품명, 규격, 브랜드, 표준가, 공급단가, 공급가격, 이미지URL
- 즉시 DB upsert (cretec source)
"""
import os
import sys
import json
import time
import re
import ctypes
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from supabase_client import SupabaseClient

# 절전 방지
if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

COOKIE = os.path.join(ROOT, "_secrets", "cookies", "cretec_storage.json")
OUT = os.path.join(ROOT, "output", "cretec")
os.makedirs(OUT, exist_ok=True)

URL_HIST = "https://ctx.cretec.kr/CtxApp/sso/selectHistProdList.do"


def collect_history():
    client = SupabaseClient()

    # crawl_run 시작
    run = client.insert("crawl_runs", {
        "source_code": "cretec",
        "status": "running",
        "notes": "CTX 이력상품 수집 (1년치, 전체 거래처)",
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"[crawl_runs #{run_id}] 시작")

    all_products = []
    inserted = 0
    updated = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 Chrome/120",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()
        page.goto(URL_HIST, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)

        # 거래처(카테고리) 목록 추출
        categories = page.evaluate("""
() => {
    const items = Array.from(document.querySelectorAll('a, li, label, input[type=checkbox]'));
    const cats = [];
    for (const e of items) {
        const t = (e.textContent || '').trim();
        if (t.length < 3 || t.length > 60) continue;
        if (/^\\d+/.test(t) || /발주품|소모품|공장|현장|불필요|견적요청서|버슘|sct|발전기술|이지티엠|음성|반월|시화|구미|울산|동탄|파주|여수|청주|군산|반도체|발주/i.test(t)) {
            cats.push({
                text: t.slice(0, 60),
                onclick: e.getAttribute('onclick') || '',
                href: e.href || '',
                cls: (e.className || '').toString().slice(0, 50)
            });
        }
    }
    return cats;
}
""")

        # 중복 제거
        seen = set()
        unique_cats = []
        for c in categories:
            if c["text"] not in seen:
                seen.add(c["text"])
                unique_cats.append(c)
        print(f"\n거래처 카테고리: {len(unique_cats)}개 식별")
        for c in unique_cats[:30]:
            print(f"  '{c['text']}'")

        # 1년 + 50건 + 전체 거래처 + 조회
        print("\n=== 1년치 + 50건 + 전체 조회 ===")
        page.evaluate("""
() => {
    // 1년 버튼
    const btns1 = document.querySelectorAll('button, a, input');
    for (const b of btns1) {
        if ((b.textContent || b.value || '').trim() === '1년') { b.click(); break; }
    }
    // 페이지당 50
    const sels = document.querySelectorAll('select');
    for (const s of sels) {
        const opts = Array.from(s.options).map(o => o.value);
        if (opts.includes('50')) { s.value = '50'; s.dispatchEvent(new Event('change')); break; }
    }
}
""")
        page.wait_for_timeout(800)

        # 조회 버튼 클릭
        page.evaluate("""
() => {
    const btns = document.querySelectorAll('button, a, input');
    for (const b of btns) {
        const t = (b.textContent || b.value || '').trim();
        if (t === '조회') { b.click(); return; }
    }
}
""")
        page.wait_for_load_state("networkidle", timeout=20000)
        page.wait_for_timeout(5000)

        # 결과 건수
        total_text = page.evaluate("() => document.body.innerText")
        m = re.search(r"총\s*(\d+)\s*건", total_text)
        total_count = int(m.group(1)) if m else 0
        print(f"검색 결과: 총 {total_count}건")

        # 1페이지 행 추출
        page_rows = []

        def extract_current_page():
            """현재 페이지의 모든 행 추출"""
            rows_data = page.evaluate("""
() => {
    const rows = document.querySelectorAll('table tbody tr');
    return Array.from(rows).map(tr => {
        const cells = Array.from(tr.querySelectorAll('td'));
        if (cells.length < 5) return null;
        const img = tr.querySelector('img');
        return {
            cells: cells.map(td => (td.innerText || '').trim()),
            img_src: img ? img.src : '',
            row_html: tr.outerHTML.slice(0, 1000)
        };
    }).filter(r => r);
}
""")
            return rows_data

        rows = extract_current_page()
        print(f"1페이지 행: {len(rows)}")

        # 페이지네이션 — 모든 페이지 순회
        page_num = 1
        while True:
            current_rows = extract_current_page()
            print(f"  페이지 {page_num}: {len(current_rows)}행")
            for r in current_rows:
                if r and r["cells"]:
                    page_rows.append(r)

            # 다음 페이지 버튼
            has_next = page.evaluate("""
() => {
    const next = document.querySelector('a[onclick*=fnPaging], .paging a.next, .pagination .next');
    if (next && !next.classList.contains('disabled')) {
        next.click();
        return true;
    }
    return false;
}
""")
            if not has_next:
                break
            page.wait_for_timeout(2500)
            page_num += 1
            if page_num > 50:  # 안전장치
                break

        all_products = page_rows
        print(f"\n총 추출: {len(all_products)}행")

        # 첫 5개 샘플
        if all_products:
            print("\n샘플 5개:")
            for r in all_products[:5]:
                print(f"  cells({len(r['cells'])}): {r['cells'][:8]}")
                print(f"  img: {r['img_src'][:80]}")

        # 결과 저장 (DB 저장 전 디버그용)
        with open(os.path.join(OUT, "hist_raw.json"), "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        print(f"\nRaw JSON: {OUT}/hist_raw.json")

        page.screenshot(path=os.path.join(OUT, "hist_full_result.png"), full_page=True)
        browser.close()

    # crawl_runs 종료
    if run_id:
        client.update("crawl_runs", {"id": run_id}, {
            "status": "success",
            "products_added": inserted,
            "products_updated": updated,
            "notes": f"행 {len(all_products)}개 raw 추출 (DB 저장은 다음 단계)"
        })
    return all_products


if __name__ == "__main__":
    collect_history()
