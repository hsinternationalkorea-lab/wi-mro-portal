# -*- coding: utf-8 -*-
"""
서브원 깊이 분석 v2
1) 상품 상세 페이지 → 관련상품 영역 발견
2) 메인/카테고리 페이지의 AJAX endpoint 캡처
3) GNB 클릭 시 실제 URL 추적
"""
import os, sys, json, re, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=COOKIE,
        user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
        locale="ko-KR", viewport={"width":1400,"height":900},
    )
    page = context.new_page()

    # 모든 네트워크 요청 캡처
    requests_log = []
    def handle_request(req):
        requests_log.append({
            'url': req.url,
            'method': req.method,
            'resource_type': req.resource_type,
        })
    page.on("request", handle_request)

    # === 1. 상품 상세 페이지 → 관련상품 영역 ===
    print("=" * 60)
    print("[1] 상품 상세 페이지 - 관련상품/연관상품 영역 발견")
    print("=" * 60)
    test_pids = ['3030274', '3808320', '8807261', '10403310']
    for pid in test_pids:
        url = f"https://store.serveone.co.kr/pr/pr-product-detail.do?prdId={pid}"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2500)
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(700)

            data = page.evaluate(r"""() => {
                const allLinks = document.querySelectorAll('a[href*="prdId="]');
                const seen = new Set();
                const grouped = {};
                for (const a of allLinks) {
                    const m = (a.href||'').match(/prdId=(\d+)/);
                    if (!m) continue;
                    if (seen.has(m[1])) continue;
                    seen.add(m[1]);

                    // 어느 컨테이너 안에 있는지
                    let cont = '?';
                    let el = a.parentElement;
                    let depth = 0;
                    while (el && el !== document.body && depth < 10) {
                        const cls = (el.className||'').toString();
                        const id = el.id||'';
                        if (cls.match(/related|recommend|together|view|history|관련/i) ||
                            id.match(/related|recommend|together|view|history/i)) {
                            cont = (el.tagName + (id ? '#'+id : '') + (cls ? '.'+cls.split(' ')[0] : '')).slice(0,60);
                            break;
                        }
                        el = el.parentElement;
                        depth++;
                    }
                    grouped[cont] = (grouped[cont] || 0) + 1;
                }
                return {
                    title: document.title.slice(0, 50),
                    total_unique: seen.size,
                    by_container: grouped,
                };
            }""")
            print(f"\n  prdId={pid}")
            print(f"    title:    {data['title']}")
            print(f"    총 unique: {data['total_unique']}")
            print(f"    by container:")
            for cont, cnt in sorted(data['by_container'].items(), key=lambda x:-x[1]):
                print(f"      [{cnt:>3}] {cont}")
        except Exception as e:
            print(f"  prdId={pid} ERR {str(e)[:80]}")

    # === 2. 메인 페이지 진입 - 모든 AJAX endpoint 캡처 ===
    print("\n" + "=" * 60)
    print("[2] 메인 페이지 AJAX/XHR endpoint 캡처")
    print("=" * 60)
    requests_log.clear()
    page.goto("https://store.serveone.co.kr/ssp/main/index.do",
              wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(3000)
    for _ in range(8):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(600)

    xhr = [r for r in requests_log if r['resource_type'] in ('xhr', 'fetch')]
    api_pattern = re.compile(r'/(api|ajax|json|do|act)\b', re.I)
    print(f"  총 XHR/fetch: {len(xhr)}")
    seen_paths = set()
    for r in xhr[:50]:
        path = r['url'].split('?')[0].replace('https://store.serveone.co.kr', '')
        if path in seen_paths: continue
        seen_paths.add(path)
        params = re.findall(r'[?&]([a-zA-Z]+)=', r['url'])
        print(f"  {r['method']:6} {path[:80]}  ?{','.join(sorted(set(params))[:5])}")

    # === 3. GNB 카테고리 메뉴 클릭 시뮬레이션 → 실제 URL 추적 ===
    print("\n" + "=" * 60)
    print("[3] GNB 카테고리 메뉴 클릭 시뮬레이션")
    print("=" * 60)
    requests_log.clear()
    page.goto("https://store.serveone.co.kr/ssp/main/index.do",
              wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)

    # 카테고리 메뉴 호버/클릭
    clicked = page.evaluate(r"""() => {
        // gnbCatgUrlMove 함수 호출 가능한 요소 클릭
        const triggers = document.querySelectorAll('[onclick*="gnbCatgUrlMove"], [onclick*="mainUrlMove"], [onclick*="catgMove"]');
        const calls = [];
        for (const t of triggers) {
            const onclick = t.getAttribute('onclick') || '';
            calls.push({
                text: (t.textContent||'').trim().slice(0, 30),
                onclick: onclick.slice(0, 200),
            });
        }
        return calls;
    }""")
    print(f"  gnbCatgUrlMove 호출 가능 요소: {len(clicked)}개")
    seen_onclicks = set()
    unique_calls = []
    for c in clicked:
        # URL만 추출 (다른 인자 무시)
        m = re.search(r"['\"]((?:https?:)?(?:/[\w./?&=%\-]+))['\"]", c['onclick'])
        if m:
            url = m.group(1)
            if url not in seen_onclicks:
                seen_onclicks.add(url)
                unique_calls.append({'text': c['text'], 'url': url})

    print(f"  unique URL: {len(unique_calls)}개")
    for u in unique_calls[:30]:
        print(f"    '{u['text']:<25}' → {u['url'][:90]}")

    # === 4. window.__INITIAL_STATE__ 또는 카테고리 데이터 변수 ===
    print("\n" + "=" * 60)
    print("[4] 페이지 JS 변수 - 카테고리 트리 데이터")
    print("=" * 60)
    js_data = page.evaluate(r"""() => {
        const result = {};
        for (const k of Object.keys(window)) {
            if (k.startsWith('_') || k.length < 3) continue;
            const v = window[k];
            if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
                try {
                    const json = JSON.stringify(v);
                    if (json.length > 100 && (
                        /catg|category|disp_ctg|prdId|상품|카테고리/i.test(k) ||
                        /catg|category|disp_ctg/i.test(json.slice(0, 1000))
                    )) {
                        result[k] = json.slice(0, 500);
                    }
                } catch(e) {}
            }
        }
        return result;
    }""")
    if js_data:
        for k, v in list(js_data.items())[:5]:
            print(f"  window.{k}:")
            print(f"    {v[:250]}")
    else:
        print("  카테고리 관련 글로벌 변수 없음")

    browser.close()
