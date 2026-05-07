# -*- coding: utf-8 -*-
"""서브원 cateSearch.do URL 직접 진단"""
import os, sys, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=COOKIE,
        user_agent="Mozilla/5.0 Chrome/120",
        locale="ko-KR", viewport={"width":1400,"height":900},
    )
    page = context.new_page()

    # 직접 테스트할 URL들
    urls = [
        ("cateSearch C05", "https://store.serveone.co.kr/ssp/search/cateSearch.do?disp_ctg_no=C05&ftDepth=1"),
        ("cateSearch C01", "https://store.serveone.co.kr/ssp/search/cateSearch.do?disp_ctg_no=C01&ftDepth=1"),
        ("cateSearch w/ sort", "https://store.serveone.co.kr/ssp/search/cateSearch.do?sort=PRICE_YN/DESC,IMG_YN/DESC,RANK/DESC,ATTR_VAL_LIST/ASC&disp_ctg_no=C05&ftDepth=1"),
        ("기획상품관", "https://store.serveone.co.kr/sa/pmt/ssp-pw-pe-02-01.do"),
        ("기획상품관 page2", "https://store.serveone.co.kr/sa/pmt/ssp-pw-pe-02-01.do?page=2"),
        ("제조사 케이씨씨", "https://store.serveone.co.kr/sa/disp/ssp-pw-mn-01.do?mnfrNo=A1005030"),
    ]

    for label, url in urls:
        print(f"\n=== {label} ===")
        print(f"URL: {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2500)
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(800)
            data = page.evaluate(r"""() => {
                const seen = new Set();
                for (const a of document.querySelectorAll('a[href*="prdId="]')) {
                    const m = (a.href || '').match(/prdId=([0-9]+)/);
                    if (m) seen.add(m[1]);
                }
                const t = document.body.innerText.slice(0, 500);
                const totalMatch = (document.body.innerText || '').match(/(?:총|전체|검색결과|건수)[^\d]*(\d{1,3}(?:,\d{3})*)\s*(?:건|개)/);
                return {
                    title: document.title,
                    url: location.href,
                    products: seen.size,
                    totalText: totalMatch ? totalMatch[0] : '',
                    snippet: t.replace(/\s+/g, ' ').slice(0, 250),
                };
            }""")
            print(f"  title:    {data['title'][:60]}")
            print(f"  redirect: {data['url']}")
            print(f"  products: {data['products']}")
            print(f"  total:    {data['totalText']}")
            print(f"  snippet:  {data['snippet'][:200]}")
        except Exception as e:
            print(f"  ERR: {str(e)[:200]}")

    browser.close()
