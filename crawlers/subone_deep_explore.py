# -*- coding: utf-8 -*-
"""
서브원 카테고리 트리 깊이 탐색
- GNB(상단 카테고리) 호버 → 전체 카테고리 URL 수집
- 검색 페이지 URL 패턴 발견
- 카테고리당 상품 카운트 사전 측정
"""
import os
import sys
import json
import re
import time
import ctypes
from collections import Counter
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "subone")
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")
os.makedirs(OUT, exist_ok=True)

if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)


def main():
    if not os.path.exists(COOKIE):
        print(f"❌ 쿠키 없음: {COOKIE}")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        # 1. 메인 진입
        print("=" * 60)
        print("Subone 카테고리 트리 깊이 탐색")
        print("=" * 60)
        page.goto("https://store.serveone.co.kr/ssp/main/index.do",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        # 2. GNB 카테고리 메뉴 트리거 — 보통 마우스 hover 또는 클릭
        print("\n[1] 모든 카테고리 버튼/링크 트리거 시도")
        triggered = page.evaluate(r"""() => {
            const triggers = document.querySelectorAll(
                '[class*=gnb], [class*=GNB], [class*=category], [class*=Category],' +
                '[class*=catg], [class*=Catg], [class*=menu], [class*=Menu],' +
                'nav a, nav button, header a, header button'
            );
            for (const t of triggers) {
                try {
                    t.dispatchEvent(new MouseEvent('mouseover', {bubbles:true}));
                    t.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
                } catch(e) {}
            }
            return triggers.length;
        }""")
        print(f"  triggers fired: {triggered}")
        page.wait_for_timeout(2500)

        # 3. 모든 카테고리 후보 URL 수집 (href + onclick)
        all_links = page.evaluate(r"""() => {
            const out = [];
            const seen = new Set();
            // a 태그 — href + onclick
            for (const a of document.querySelectorAll('a, button, [onclick]')) {
                const href = a.href || '';
                const onclick = a.getAttribute('onclick') || '';
                const text = (a.textContent || '').trim().slice(0, 60);

                // onclick에서 URL 추출
                let extracted = href;
                const jsMatch = onclick.match(/['"]([^'"]*\/(?:sa|pr|ssp)\/[^'"]*)['"]/);
                if (jsMatch) extracted = jsMatch[1];

                if (!extracted) continue;
                if (!/\/(sa|pr|ssp)\//.test(extracted)) continue;
                // 절대 URL로 변환
                if (!extracted.startsWith('http')) {
                    extracted = 'https://store.serveone.co.kr' + extracted;
                }
                // 상품 상세는 제외
                if (/pr-product-detail/.test(extracted)) continue;
                // youtube 같은 미디어 페이지 제외
                if (/ssp-pw-yt/.test(extracted)) continue;

                const key = extracted.split('?')[0] + '|' + (extracted.match(/[?&](dispClsfNo|cateCd|brndhlMainId|brndhlSeq|catgNo|prdGrpId|searchKeyword)=([^&]+)/) || ['',''])[0];
                if (seen.has(key)) continue;
                seen.add(key);

                out.push({text, url: extracted, onclick: onclick.slice(0,150)});
            }
            return out;
        }""")
        print(f"\n[2] 카테고리 URL 후보: {len(all_links)}개")

        # URL 패턴별 분류
        pattern_counts = Counter()
        for link in all_links:
            # path만 추출
            path = link['url'].split('?')[0].replace('https://store.serveone.co.kr','')
            # 쿼리 키만 추출
            params = re.findall(r'[?&]([a-zA-Z]+)=', link['url'])
            pattern = path + ' ?' + ','.join(sorted(set(params))) if params else path
            pattern_counts[pattern] += 1

        print(f"\n[3] URL 패턴 분포:")
        for pat, cnt in pattern_counts.most_common(20):
            print(f"  {cnt:>3}건  {pat}")

        # 4. 각 패턴 샘플 — 진입 가능 여부 확인
        print(f"\n[4] 각 URL 패턴 샘플 (최대 30개)")
        sample_urls = []
        seen_pat = set()
        for link in all_links:
            path = link['url'].split('?')[0]
            params = re.findall(r'[?&]([a-zA-Z]+)=', link['url'])
            pattern = path + '|' + ','.join(sorted(set(params)))
            if pattern in seen_pat: continue
            seen_pat.add(pattern)
            sample_urls.append(link)
            if len(sample_urls) >= 30: break

        for s in sample_urls[:20]:
            print(f"  '{s['text'][:25]:<25}' → {s['url'][:100]}")

        # 5. 각 카테고리 후보를 실제 방문 → 상품 카운트
        print(f"\n[5] 카테고리별 상품 카운트 사전 측정 (상위 30개)")
        results = []
        for i, link in enumerate(all_links[:50]):
            try:
                page.goto(link['url'], wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(1500)
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(500)
                cnt = page.evaluate(r"""() => {
                    const seen = new Set();
                    for (const a of document.querySelectorAll('a[href*="prdId="]')) {
                        const m = (a.href || '').match(/prdId=(\d+)/);
                        if (m) seen.add(m[1]);
                    }
                    return seen.size;
                }""")
                results.append({'text': link['text'], 'url': link['url'], 'products': cnt})
                if cnt > 0:
                    print(f"  [{i+1:>2}] {cnt:>4} prods | '{link['text'][:25]:<25}' → {link['url'][:80]}")
            except Exception as e:
                print(f"  [{i+1}] ERR {str(e)[:60]} — {link['url'][:60]}")
            time.sleep(0.5)

        # 6. 검색 API 시도 — 키워드별 상품 추출
        print(f"\n[6] 검색 페이지 URL 패턴 시도")
        search_attempts = [
            "https://store.serveone.co.kr/sa/srch/ssp-sc-sl-01.do?searchKeyword=공구",
            "https://store.serveone.co.kr/pr/pr-product-list.do?searchKeyword=공구",
            "https://store.serveone.co.kr/sa/disp/ssp-pw-cm-01.do?searchKeyword=공구",
        ]
        for url in search_attempts:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(1500)
                cnt = page.evaluate(r"""() => {
                    const seen = new Set();
                    for (const a of document.querySelectorAll('a[href*="prdId="]')) {
                        const m = (a.href || '').match(/prdId=(\d+)/);
                        if (m) seen.add(m[1]);
                    }
                    return seen.size;
                }""")
                title = page.title()
                print(f"  {cnt:>4} prods | {url[:80]} | {title[:30]}")
            except Exception as e:
                print(f"  ERR  | {url[:80]} | {str(e)[:50]}")
            time.sleep(0.5)

        # 저장
        report = {
            "all_links": all_links,
            "patterns": dict(pattern_counts.most_common(30)),
            "category_results": sorted(results, key=lambda x: -x['products'])[:30],
        }
        out_path = os.path.join(OUT, "deep_explore.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {out_path}")

        browser.close()


if __name__ == "__main__":
    main()
