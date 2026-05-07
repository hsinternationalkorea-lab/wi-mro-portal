# -*- coding: utf-8 -*-
"""navimro 페이지 — 진짜 selector 빠른 검증"""
import os, sys, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "navimro_storage.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=COOKIE,
        user_agent="Mozilla/5.0 Chrome/120",
        locale="ko-KR", viewport={"width":1400,"height":900},
    )
    page = context.new_page()

    page.goto("https://www.navimro.com/s/c-13/", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(4000)
    for _ in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)

    # 다양한 selector 시도
    res = page.evaluate(r"""() => {
        const results = {};
        const tries = [
            'a[href*="/g/"]',
            'li.item a[href*="/g/"]',
            'div.product-list a[href*="/g/"]',
            'div.product-list-area a[href*="/g/"]',
            'ul.clearFix > li a[href*="/g/"]',
            'ul.clearFix li a[href*="/g/"]',
            'div.product-list-area li a',
            // closest exclude tests
        ];
        for (const sel of tries) {
            const seen = new Set();
            for (const a of document.querySelectorAll(sel)) {
                const m = (a.href||'').match(/\/g\/(\d+)/);
                if (m) seen.add(m[1]);
            }
            results[sel] = seen.size;
        }
        // closest exclude only div.recommend
        let cnt2 = 0; const seen2 = new Set();
        for (const a of document.querySelectorAll('a[href*="/g/"]')) {
            if (a.closest('div.recommend')) continue;
            const m = (a.href||'').match(/\/g\/(\d+)/);
            if (m && !seen2.has(m[1])) { seen2.add(m[1]); cnt2++; }
        }
        results['NOT closest div.recommend'] = cnt2;
        // closest exclude only div.ca-reco
        let cnt3 = 0; const seen3 = new Set();
        for (const a of document.querySelectorAll('a[href*="/g/"]')) {
            if (a.closest('div.ca-reco')) continue;
            const m = (a.href||'').match(/\/g\/(\d+)/);
            if (m && !seen3.has(m[1])) { seen3.add(m[1]); cnt3++; }
        }
        results['NOT closest div.ca-reco'] = cnt3;
        return results;
    }""")
    print("c-13 selector test:")
    for sel, cnt in res.items():
        print(f"  [{cnt:>4}] {sel}")
    browser.close()
