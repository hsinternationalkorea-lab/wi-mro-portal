# -*- coding: utf-8 -*-
"""
서브원 카테고리 트리 깊이 크롤러 v3
- /ssp/search/cateSearch.do?disp_ctg_no=Cxx&ftDepth=N 패턴
- 자동 카테고리 ID 발굴 (C01~C30, depth 1~4)
- 페이지네이션 (page= 또는 무한스크롤)
- 제조사별 진입 (mnfrNo)
"""
import os
import sys
import json
import re
import time
import ctypes
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from supabase_client import SupabaseClient

if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

OUT = os.path.join(ROOT, "output", "subone")
os.makedirs(OUT, exist_ok=True)
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")
CRAWL_DELAY = 2.0


def map_to_wi(label, name=""):
    text = (label + " " + name).lower()
    if re.search(r"의료|구급", text): return "M"
    if re.search(r"베어링|볼트|너트|체결", text): return "F"
    if re.search(r"실험|크린|측정|분석|계측|연구|화학물질|랩", text): return "L"
    if re.search(r"청소|위생|와이퍼", text): return "C"
    if re.search(r"안전|소방|방재|보호|마스크|글러브|장갑|솔루션", text): return "S"
    if re.search(r"전선|전기|조명|전지|충전|자동제어|반도체", text): return "E"
    if re.search(r"포장|박스|운반|하역|공구함|작업대|특가", text): return "P"
    if re.search(r"공구|용접|연마|에어|절삭|배관|드릴|스마토", text): return "T"
    return "O"


def extract_products_from_page(page):
    return page.evaluate(r"""() => {
        const seen = new Set();
        const out = [];
        for (const a of document.querySelectorAll('a[href*="prdId="]')) {
            const m = (a.href || '').match(/prdId=([0-9]+)/);
            if (!m) continue;
            const pid = m[1];
            if (seen.has(pid)) continue;
            seen.add(pid);

            const card = a.closest('li, .item, .product, [class*=item], [class*=product], [class*=goods], div');
            if (!card) continue;
            const text = (card.innerText || '').trim();
            const priceMatch = text.match(/(\d{1,3}(?:,\d{3})+)\s*원/);
            const img = card.querySelector('img');

            let name = (a.textContent || '').trim();
            name = name.replace(/[\d,]+\s*원.*/, '').replace(/^\s*\d+\s*$/, '').trim();
            if (!name && img) name = img.alt || '';
            if (!name || name.length < 2) continue;

            out.push({
                source_id: pid,
                name: name.slice(0, 200),
                price: priceMatch ? parseInt(priceMatch[1].replace(/,/g, '')) : 0,
                img_src: img ? (img.src || img.dataset?.src || '') : '',
                href: a.href.startsWith('http') ? a.href : 'https://store.serveone.co.kr' + a.href,
            });
        }
        return out;
    }""")


def get_total_count(page):
    """현재 검색 결과 총 건수 추출"""
    return page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        // "총 1,234건", "검색결과 1,234건" 패턴
        const m = text.match(/(?:총|검색결과)[^\d]*(\d{1,3}(?:,\d{3})*)\s*건/);
        return m ? parseInt(m[1].replace(/,/g, '')) : 0;
    }""")


def crawl_url(page, url, label, client, seen_ids, max_pages=20):
    """URL 진입 → 페이지네이션 따라가며 상품 추출 + DB 저장. 신규 카운트 반환"""
    cat_ins, cat_upd = 0, 0
    wi_cat = map_to_wi(label)

    for pn in range(1, max_pages + 1):
        # page 파라미터 추가
        if pn == 1:
            target = url
        else:
            sep = '&' if '?' in url else '?'
            target = f"{url}{sep}page={pn}"

        try:
            page.goto(target, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1500)
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500)
        except Exception as e:
            break

        products = extract_products_from_page(page)
        if not products:
            break

        new_in_page = 0
        for prod in products:
            if prod["source_id"] in seen_ids:
                continue
            seen_ids.add(prod["source_id"])
            new_in_page += 1
            try:
                ex = client.select("products", select="id",
                    **{"source_code": "eq.subone", "source_product_id": f"eq.{prod['source_id']}"})
                payload = {
                    "source_code": "subone", "source_product_id": prod["source_id"],
                    "category_code": wi_cat, "sub_category": label[:100],
                    "name_ko": prod["name"],
                    "search_keywords": f"{prod['name']} {label}"[:500],
                    "primary_image_url": prod.get("img_src") or None,
                    "image_urls": [prod["img_src"]] if prod.get("img_src") else [],
                    "cost_price": prod.get("price") or None,
                    "list_price": prod.get("price") or None,
                    "margin_pct": 0, "currency": "KRW", "price_unit": "EA",
                    "source_url": prod.get("href"),
                    "is_directly_sold": False, "is_published": True, "quality_score": 0.85,
                    "last_crawled_at": datetime.now(timezone.utc).isoformat(),
                }
                if isinstance(ex, list) and ex:
                    r = client.update("products", {"id": ex[0]["id"]}, payload)
                    if isinstance(r, list) or (isinstance(r, dict) and r.get("ok")):
                        cat_upd += 1
                else:
                    r = client.insert("products", payload)
                    if isinstance(r, list) and r:
                        cat_ins += 1
            except Exception:
                pass

        # 신규 0이면 종료 (페이지네이션 끝 또는 같은 상품 반복)
        if new_in_page == 0:
            break

    return cat_ins, cat_upd


def main():
    client = SupabaseClient()

    if not os.path.exists(COOKIE):
        print(f"❌ 쿠키 없음: {COOKIE}")
        sys.exit(1)

    run = client.insert("crawl_runs", {
        "source_code": "subone", "status": "running",
        "notes": "깊이 크롤링 — cateSearch.do + 제조사 + 기획"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    inserted = 0
    updated = 0
    started = time.time()

    # 이미 들어간 subone source_id 모두 로드 (중복 방지)
    seen_ids = set()
    offset = 0
    while True:
        r = client._request("GET", "/products",
            params={"source_code": "eq.subone", "select": "source_product_id",
                    "offset": offset, "limit": 1000})
        if not isinstance(r, list) or not r:
            break
        seen_ids.update(x["source_product_id"] for x in r if x.get("source_product_id"))
        if len(r) < 1000:
            break
        offset += 1000
    print(f"기존 subone seen: {len(seen_ids)}건", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        # === 1단계: cateSearch.do 카테고리 자동 발굴 ===
        # disp_ctg_no = C01~C30, ftDepth = 1
        print("\n=== [1] cateSearch.do disp_ctg_no=C01~C30 (depth=1) ===", flush=True)
        valid_categories = []
        for ci in range(1, 31):
            cno = f"C{ci:02d}"
            url = (f"https://store.serveone.co.kr/ssp/search/cateSearch.do"
                   f"?sort=RANK/DESC&disp_ctg_no={cno}&ftDepth=1")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(1500)
                # 페이지 제목/헤더에서 카테고리명 추출
                title = page.evaluate(r"""() => {
                    const h = document.querySelector('h1, h2, [class*=title], [class*=Title]');
                    return h ? (h.textContent||'').trim().slice(0, 50) : '';
                }""")
                total = get_total_count(page)
                if total > 0:
                    valid_categories.append({"cno": cno, "title": title or cno, "total": total, "url": url})
                    print(f"  {cno} '{title[:25]:<25}' 총 {total:,}건", flush=True)
                time.sleep(0.5)
            except Exception as e:
                pass

        print(f"\n유효 카테고리: {len(valid_categories)}개", flush=True)

        # === 2단계: 각 카테고리 크롤 ===
        print("\n=== [2] 카테고리별 크롤 ===", flush=True)
        for i, cat in enumerate(valid_categories, 1):
            label = cat["title"] or cat["cno"]
            try:
                cat_ins, cat_upd = crawl_url(page, cat["url"], label, client, seen_ids, max_pages=30)
                inserted += cat_ins
                updated += cat_upd
                elapsed = time.time() - started
                print(f"  [{i}/{len(valid_categories)}] {label[:25]:<25} "
                      f"+{cat_ins} ~{cat_upd} | 누적 {inserted+updated} ({len(seen_ids)} unique) | "
                      f"{elapsed/60:.1f}분", flush=True)
            except Exception as e:
                print(f"  [{i}] ERR {label}: {str(e)[:60]}", flush=True)
            time.sleep(CRAWL_DELAY)

        # === 3단계: 기획상품관 페이지네이션 깊이 ===
        print("\n=== [3] 기획상품관 깊이 크롤 ===", flush=True)
        pe_url = "https://store.serveone.co.kr/sa/pmt/ssp-pw-pe-02-01.do"
        cat_ins, cat_upd = crawl_url(page, pe_url, "기획상품관", client, seen_ids, max_pages=50)
        inserted += cat_ins; updated += cat_upd
        print(f"  기획상품관 +{cat_ins} ~{cat_upd}", flush=True)

        # === 4단계: 제조사별 진입 ===
        print("\n=== [4] 제조사 페이지 발굴 ===", flush=True)
        # 메인에서 모든 mnfrNo 링크 추출
        page.goto("https://store.serveone.co.kr/ssp/main/index.do",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)
        mnfr_links = page.evaluate(r"""() => {
            const seen = new Set();
            const out = [];
            for (const a of document.querySelectorAll('a[href*="mnfrNo="]')) {
                const m = (a.href || '').match(/mnfrNo=([A-Z0-9]+)/);
                if (!m) continue;
                if (seen.has(m[1])) continue;
                seen.add(m[1]);
                out.push({
                    mnfr: m[1],
                    label: (a.textContent||'').trim().slice(0,40),
                    href: a.href.startsWith('http') ? a.href : 'https://store.serveone.co.kr' + a.href,
                });
            }
            return out;
        }""")
        print(f"  제조사 링크: {len(mnfr_links)}개", flush=True)

        for i, m in enumerate(mnfr_links, 1):
            try:
                cat_ins, cat_upd = crawl_url(page, m["href"], m["label"] or m["mnfr"], client, seen_ids, max_pages=10)
                inserted += cat_ins; updated += cat_upd
                if cat_ins + cat_upd > 0:
                    print(f"    [{i}] {m['label'][:20]:<20} +{cat_ins} ~{cat_upd}", flush=True)
            except Exception:
                pass
            time.sleep(CRAWL_DELAY)

        browser.close()

    if run_id:
        client.update("crawl_runs", {"id": run_id}, {
            "status": "success",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "products_added": inserted, "products_updated": updated,
        })

    print(f"\n=== 완료 === 신규 {inserted}, 업데이트 {updated}, 소요 {(time.time()-started)/60:.1f}분")


if __name__ == "__main__":
    main()
