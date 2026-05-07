# -*- coding: utf-8 -*-
"""
서브원 1회 로그인 + 쿠키 저장 + 사이트 구조 분석
- Playwright headless=False (브라우저 창 띄움)
- 사용자가 직접 로그인 (1회)
- 로그인 후 쿠키 저장 → 이후 자동 크롤링
"""
import os
import sys
import json
import time
import re
import ctypes
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS = os.path.join(ROOT, "_secrets")
COOKIES = os.path.join(SECRETS, "cookies")
OUT = os.path.join(ROOT, "output", "subone")
os.makedirs(COOKIES, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
STORAGE = os.path.join(COOKIES, "serveone_storage.json")


def main():
    print("=" * 70)
    print("서브원 (ServeOne) — 1회 로그인 + 사이트 구조 분석")
    print("=" * 70)
    print("""
진행 안내:
  1. 브라우저 창이 자동으로 열립니다
  2. 평소처럼 로그인 (yjyoon)
  3. 로그인 후 가격이 보이는 페이지로 이동
     - 카테고리 클릭 또는 검색
  4. 이 콘솔로 돌아와서 Enter
""")
    input("준비되면 Enter — 브라우저 열림 ▶ ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()
        page.goto("https://store.serveone.co.kr/ssp/manager/login.do", timeout=20000)

        print()
        print(">>> 브라우저에서:")
        print("    1. ID: yjyoon, PW: youn041010!  로 로그인")
        print("    2. 로그인 완료되면 가격 보이는 카테고리·전문관 페이지로 이동")
        print("    3. 상품들이 화면에 보이면 멈춤")
        print()
        input(">>> 로그인 + 가격 보이는 페이지 도달했으면 Enter ▶ ")

        # 1. 쿠키 저장
        current_url = page.url
        title = page.title()
        print(f"\n현재 URL: {current_url}")
        print(f"제목: {title}")

        context.storage_state(path=STORAGE)
        print(f"✅ 쿠키 저장: {STORAGE}")

        # 2. 가격 추출
        text = page.evaluate("() => document.body.innerText")
        prices = re.findall(r"(\d{1,3}(?:,\d{3})+)\s*원", text)
        unique = sorted(set(int(p.replace(",", "")) for p in prices if int(p.replace(",", "")) >= 100))
        print(f"\n가격: {len(prices)}개 (유니크 {len(unique)})")
        if unique:
            print(f"  샘플: {unique[:10]}")

        # 3. 상품 link 추출
        prod_links = page.evaluate(r"""() => {
            const seen = new Set();
            return Array.from(document.querySelectorAll('a'))
                .filter(a => /\/pr\/pr-product-detail|\/pr\/pr-/i.test(a.href || ''))
                .map(a => ({text:(a.textContent||'').trim().slice(0,40), href:a.href}))
                .filter(c => { if (seen.has(c.href)) return false; seen.add(c.href); return true; })
                .slice(0, 30);
        }""")
        print(f"\n상품 링크: {len(prod_links)}")
        for l in prod_links[:10]:
            print(f"  '{l['text']:<25}' → {l['href'][:90]}")

        # 4. 카테고리 link 추출 (gnbCatgUrlMove 호출, /sa/disp 등)
        cats = page.evaluate(r"""() => {
            const seen = new Set();
            return Array.from(document.querySelectorAll('a, button'))
                .map(e => ({
                    text: (e.textContent||'').trim().slice(0,40),
                    href: e.href || '',
                    onclick: (e.getAttribute('onclick')||'').slice(0,200)
                }))
                .filter(c => c.text && (c.href.includes('/sa/disp') || c.href.includes('/pr/') ||
                                         /gnbCatgUrlMove|catgMove|catCd/i.test(c.onclick)))
                .filter(c => { const key = c.href + c.onclick; if (seen.has(key)) return false; seen.add(key); return true; })
                .slice(0, 30);
        }""")
        print(f"\n카테고리 후보: {len(cats)}")
        for c in cats[:15]:
            disp = c['onclick'][:80] if c['onclick'] else c['href'][:80]
            print(f"  '{c['text']:<25}' → {disp}")

        # 5. 페이지 스크린샷
        screenshot = os.path.join(OUT, f"after_login_{int(time.time())}.png")
        page.screenshot(path=screenshot)
        print(f"\n스크린샷: {screenshot}")

        # 분석 저장
        analysis = {
            "url": current_url,
            "title": title,
            "price_count": len(prices),
            "price_samples": unique[:20],
            "product_links": prod_links[:20],
            "categories": cats[:30],
            "timestamp": time.time(),
        }
        with open(os.path.join(OUT, "analysis.json"), "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"분석 결과: {OUT}/analysis.json")

        print()
        input("\n>>> 다른 페이지(전문관 등) 보고 싶으면 이동 후 Enter, 아니면 Enter로 종료 ▶ ")

        # 추가 분석 (현재 페이지가 다르면)
        if page.url != current_url:
            print(f"\n추가 분석: {page.url}")
            page.screenshot(path=os.path.join(OUT, f"second_page_{int(time.time())}.png"))

        browser.close()
    print("\n[완료] 다음: subone_crawl.py 작성 + 백그라운드 가동")


if __name__ == "__main__":
    main()
