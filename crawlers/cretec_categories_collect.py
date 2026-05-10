# -*- coding: utf-8 -*-
"""
크레텍 카테고리 트리 수집 → categories_full.json 생성

cretec_full_crawl.py 가 필요로 하는 사전 파일을 만든다.
입력: _secrets/cookies/cretec_storage.json (로그인 상태)
출력: output/cretec/categories_full.json — 형식 {"1":[[code,label]…], "2":…, "3":…, "4":…}

전략:
  1. 로그인 storage_state 로 ctx.cretec.kr 메인 진입
  2. #categoryBtn 클릭하여 트리 펼침
  3. DOM 에서 onclick="powerSearchCate('LEVEL', CODE)" 호출 패턴 모두 추출
  4. level 4(leaf) 가 너무 적으면 level 1~3 노드를 차례로 click 하여 lazy expand 후 재추출
  5. JSON 저장 + 디버그용 트리 HTML 일부 dump

사용:
    python crawlers/cretec_categories_collect.py
    python crawlers/cretec_categories_collect.py --headed   # 사이트 동작 디버깅 (창 띄움)
"""
import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

COOKIE = ROOT / "_secrets" / "cookies" / "cretec_storage.json"
OUT_DIR = ROOT / "output" / "cretec"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "categories_full.json"
DEBUG_HTML = OUT_DIR / "category_tree_debug.html"


def collect_from_dom(page):
    """현재 DOM 에서 powerSearchCate 호출 패턴 모두 추출"""
    return page.evaluate(r"""() => {
        const out = {1: [], 2: [], 3: [], 4: []};
        const seen = new Set();
        // (1) onclick 속성
        const all1 = Array.from(document.querySelectorAll('[onclick*="powerSearchCate"]'));
        // (2) href 의 javascript: 형태
        const all2 = Array.from(document.querySelectorAll('a[href*="powerSearchCate"]'));
        const all = [...all1, ...all2];
        for (const el of all) {
            const oc = el.getAttribute('onclick') || el.getAttribute('href') || '';
            const m = oc.match(/powerSearchCate\(\s*['"](\d+)['"]\s*,\s*(\d+)\s*\)/);
            if (!m) continue;
            const lvl = m[1];
            const code = m[2];
            const label = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100);
            const key = lvl + ':' + code;
            if (seen.has(key)) continue;
            seen.add(key);
            if (out[lvl]) out[lvl].push([code, label]);
        }
        return out;
    }""")


def expand_level(page, level):
    """주어진 level 의 노드들을 모두 click 하여 하위 level 펼치기 (lazy load 대응)"""
    clicked = page.evaluate(f"""() => {{
        const els = Array.from(document.querySelectorAll('[onclick*="powerSearchCate"]'));
        let n = 0;
        for (const el of els) {{
            const oc = el.getAttribute('onclick') || '';
            if (oc.match(/powerSearchCate\\(\\s*['"]{level}['"]/)) {{
                try {{ el.click(); n++; }} catch (e) {{}}
            }}
        }}
        return n;
    }}""")
    return clicked


def main():
    headed = "--headed" in sys.argv
    if not COOKIE.exists():
        print(f"[FAIL] 로그인 cookie 없음: {COOKIE}")
        print("       먼저 crawlers/cretec_explore.py 로 cookie 저장 필요")
        sys.exit(1)

    print("=" * 60)
    print(f"크레텍 카테고리 수집  (headed={headed})")
    print(f"  cookie: {COOKIE}")
    print(f"  output: {OUT_FILE}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed, slow_mo=30 if headed else 0)
        context = browser.new_context(
            storage_state=str(COOKIE),
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()

        print("\n[1] ctx.cretec.kr/CtxApp/ 진입 (meta refresh 우회)")
        page.goto("https://ctx.cretec.kr/CtxApp/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)
        print(f"    URL: {page.url}")
        print(f"    Title: {page.title()}")

        # 본문 일부 — 로그인 페이지인지 메인인지 확인
        body_sample = page.evaluate("() => document.body.innerText.slice(0, 300).replace(/\\s+/g, ' ')")
        print(f"    body[0:300]: {body_sample}")
        # 로그인 페이지로 빠졌는지 단순 체크
        if any(k in body_sample for k in ["로그인", "아이디", "비밀번호", "Sign in", "Login"]):
            if "카테고리" not in body_sample:
                print("    !! 로그인 페이지로 보임 → cookie 만료 가능성")

        print("[2] #categoryBtn 클릭 + #dropDownCategory 펼침 (Bootstrap collapse)")
        try:
            page.evaluate("""() => {
                const btn = document.getElementById('categoryBtn');
                if (btn) btn.click();
                // collapse 영역 강제로 펼침 (Bootstrap 호환)
                const dd = document.getElementById('dropDownCategory');
                if (dd) {
                    dd.classList.add('show', 'in');
                    dd.classList.remove('collapse', 'collapsing');
                    dd.style.display = 'block';
                    dd.style.height = 'auto';
                }
            }""")
        except Exception as e:
            print(f"    !! click/expand 실패: {e}")
        # 펼침 + AJAX 로드 대기
        page.wait_for_timeout(4000)
        try:
            page.wait_for_selector("#dropDownCategory", timeout=5000)
            inner_len = page.evaluate("() => { const e=document.getElementById('dropDownCategory'); return e ? e.innerText.length : 0; }")
            print(f"    #dropDownCategory innerText 길이: {inner_len}")
        except Exception as e:
            print(f"    #dropDownCategory 대기 실패: {e}")

        print("[3] 1차 추출")
        cats = collect_from_dom(page)
        for lvl in ("1", "2", "3", "4"):
            print(f"    level {lvl}: {len(cats[lvl])}개")

        # leaf(level 4) 가 부족하면 단계별 expand
        if len(cats["4"]) < 100:
            print("\n[4] level 4 부족 → lazy expand 시도 (level 1 → 2 → 3 차례로 click)")
            for lvl in ("1", "2", "3"):
                clicked = expand_level(page, lvl)
                print(f"    level {lvl} click: {clicked}개 노드")
                page.wait_for_timeout(1500)
            cats = collect_from_dom(page)
            print("\n[5] 재추출")
            for lvl in ("1", "2", "3", "4"):
                print(f"    level {lvl}: {len(cats[lvl])}개")

        # 디버그: 트리 영역 outerHTML 저장 (selector 가 다를 수 있어 본문 일부도)
        try:
            html_part = page.evaluate(r"""() => {
                const candidates = ['#dropDownCategory', '#categoryArea', '#categoryBox', '.category-tree', '#category', 'nav', '#categoryBtn'];
                for (const sel of candidates) {
                    const el = document.querySelector(sel);
                    if (el && el.outerHTML.length > 300) return sel + '\n' + el.outerHTML.slice(0, 200000);
                }
                return 'NO_CONTAINER\n' + document.body.outerHTML.slice(0, 200000);
            }""")
            DEBUG_HTML.write_text(html_part, encoding="utf-8")
            print(f"\n    debug HTML: {DEBUG_HTML} ({DEBUG_HTML.stat().st_size:,} bytes)")
        except Exception as e:
            print(f"    debug HTML 저장 실패: {e}")

        # 저장
        OUT_FILE.write_text(json.dumps(cats, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✅ 저장: {OUT_FILE} ({OUT_FILE.stat().st_size:,} bytes)")
        for lvl in ("1", "2", "3", "4"):
            samples = cats[lvl][:3]
            print(f"   level {lvl}: {len(cats[lvl])}개  샘플: {samples}")

        if len(cats["4"]) < 50:
            print("\n⚠️  level 4 카테고리가 너무 적습니다.")
            print("   (사이트 DOM 변경 또는 lazy load 추가 동작 필요)")
            print(f"   {DEBUG_HTML} 를 분석해서 추출 selector 보정해주세요.")

        browser.close()


if __name__ == "__main__":
    main()
