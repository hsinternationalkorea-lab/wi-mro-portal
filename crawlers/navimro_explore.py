# -*- coding: utf-8 -*-
"""
나비엠알오 페이지 구조 분석 — 카테고리 페이지의 진짜 상품 그리드 식별
- 문제: 모든 카테고리에서 같은 146건만 잡힘 (추천/사이드바)
- 목표: 카테고리별 고유 상품 영역의 셀렉터 발견
"""
import os
import sys
import json
import re
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "navimro_storage.json")
OUT = os.path.join(ROOT, "output", "navimro")
os.makedirs(OUT, exist_ok=True)


def main():
    if not os.path.exists(COOKIE):
        print(f"쿠키 없음: {COOKIE}")
        sys.exit(1)

    # 두 개의 다른 카테고리에 들어가서 prdId 비교 → 진짜 카테고리 영역 발견
    test_cats = [
        ("https://www.navimro.com/s/c-13/", "장갑/안전화/마스크"),
        ("https://www.navimro.com/s/c-15/", "전동/충전/에어공구"),
        ("https://www.navimro.com/s/c-16/", "용접/연마공구"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        all_results = []
        for url, label in test_cats:
            print(f"\n=== {label} ({url}) ===")
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(800)

            # 모든 prdId 링크의 위치 조사
            data = page.evaluate(r"""() => {
                const results = [];
                const seen = new Set();
                const links = document.querySelectorAll('a[href*="/g/"]');
                for (const a of links) {
                    const m = (a.href || '').match(/\/g\/(\d+)/);
                    if (!m) continue;
                    const gid = m[1];
                    if (seen.has(gid)) continue;
                    seen.add(gid);

                    // 이 링크의 ancestor chain 모두 수집 → 어느 컨테이너 안인지
                    const ancestors = [];
                    let el = a;
                    let depth = 0;
                    while (el && el !== document.body && depth < 12) {
                        const tag = el.tagName.toLowerCase();
                        const id = el.id ? '#' + el.id : '';
                        const cls = (el.className && typeof el.className === 'string')
                            ? '.' + el.className.split(/\s+/).filter(c=>c).slice(0,3).join('.')
                            : '';
                        ancestors.push(tag + id + cls);
                        el = el.parentElement;
                        depth++;
                    }
                    results.push({gid, ancestors: ancestors.slice(0, 8)});
                }
                return results;
            }""")
            print(f"  prdId 총: {len(data)}")

            # ancestor chain 빈도 카운트 (depth=2 즉 부모의 부모 컨테이너)
            from collections import Counter
            depth_counters = [Counter() for _ in range(8)]
            for d in data:
                for di, a in enumerate(d['ancestors'][:8]):
                    depth_counters[di][a] += 1

            print("\n  ancestor 빈도 (depth=3,4,5,6 - 컨테이너):")
            for di in [2, 3, 4, 5, 6]:
                top = depth_counters[di].most_common(5)
                print(f"    depth={di}:")
                for cont, cnt in top:
                    print(f"      [{cnt:>3}] {cont[:90]}")

            all_results.append({
                "url": url, "label": label,
                "total_prdid": len(data),
                "first_5_gids": [d['gid'] for d in data[:5]],
                "depth_3_top": depth_counters[3].most_common(5),
                "depth_4_top": depth_counters[4].most_common(5),
                "depth_5_top": depth_counters[5].most_common(5),
            })

        # 두 카테고리의 prdId 교집합 → 글로벌 추천 영역 (모두 공통)
        print("\n=== 카테고리 간 prdId 교집합 ===")
        if len(all_results) >= 2:
            sets = []
            for url, label in test_cats:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(700)
                gids = page.evaluate(r"""() => {
                    const seen = new Set();
                    for (const a of document.querySelectorAll('a[href*="/g/"]')) {
                        const m = (a.href || '').match(/\/g\/(\d+)/);
                        if (m) seen.add(m[1]);
                    }
                    return Array.from(seen);
                }""")
                sets.append((label, set(gids)))
                print(f"  {label}: {len(gids)} prdIds")

            common = set.intersection(*[s for _, s in sets])
            print(f"\n  모든 카테고리 공통: {len(common)}건 (추천/사이드바)")
            for label, s in sets:
                only = s - common
                print(f"  {label} 고유: {len(only)}건")

        with open(os.path.join(OUT, "selector_explore.json"), "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n결과: {OUT}/selector_explore.json")

        browser.close()


if __name__ == "__main__":
    main()
