# -*- coding: utf-8 -*-
"""
크레텍 1단계: 사용자 로그인 + 화면 구조 탐색
- Playwright headless=False로 실제 브라우저 띄움
- 사용자가 직접 로그인 (대리점 ID/PW)
- 로그인 후 쿠키 + storage 저장 (재로그인 불필요)
- 사용자가 가격 보이는 페이지로 이동
- 그 페이지의 URL + DOM 구조 자동 분석 → 다음 단계 코드 작성용
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.path.join(ROOT, "_secrets")
COOKIES_DIR = os.path.join(SECRETS_DIR, "cookies")
os.makedirs(COOKIES_DIR, exist_ok=True)
STORAGE_FILE = os.path.join(COOKIES_DIR, "cretec_storage.json")
SCREENSHOT_DIR = os.path.join(ROOT, "output", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def main():
    print("=" * 70)
    print("크레텍 — 1회 로그인 + 화면 구조 탐색")
    print("=" * 70)
    print("""
이 스크립트의 진행:
  1. 브라우저 창이 열립니다
  2. 사용자가 평소처럼 크레텍에 로그인 (대리점 ID/PW)
  3. 로그인 후 가격이 보이는 페이지로 이동 (검색 또는 카테고리)
  4. 이 콘솔에서 Enter 누르면 → 자동 분석 시작
  5. 쿠키 + 페이지 정보 저장 → 다음 단계에서 자동 사용
""")
    input("준비되면 Enter — 브라우저 열림 ▶ ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()
        page.goto("https://www.cretec.kr/", timeout=20000)

        print()
        print(">>> 브라우저에서:")
        print("    1. 우측 상단 또는 메뉴에서 [로그인] 클릭")
        print("    2. 대리점 ID/PW 입력")
        print("    3. 로그인 후 가격이 보이는 페이지로 이동")
        print("       (예: 카테고리 클릭 또는 검색)")
        print()
        input(">>> 가격 보이는 페이지 도달했으면 Enter ▶ ")

        # 1. 현재 URL + 쿠키 저장
        current_url = page.url
        title = page.title()
        print(f"\n현재 URL: {current_url}")
        print(f"제목: {title}")

        context.storage_state(path=STORAGE_FILE)
        print(f"✅ 쿠키 저장: {STORAGE_FILE}")

        # 2. 페이지 스크린샷
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"cretec_{int(time.time())}.png")
        page.screenshot(path=screenshot_path, full_page=False)
        print(f"✅ 스크린샷: {screenshot_path}")

        # 3. 페이지 구조 분석
        print("\n" + "=" * 70)
        print("페이지 구조 자동 분석")
        print("=" * 70)

        # 가격 패턴 ('XX,XXX원' 또는 'XX,XXX' 숫자)
        body_text = page.evaluate("() => document.body.innerText")
        import re
        prices = re.findall(r"(\d{1,3}(?:,\d{3})+)\s*원?", body_text)
        prices_unique = sorted(set(int(p.replace(",", "")) for p in prices if int(p.replace(",", "")) >= 100))
        print(f"\n가격 추출: 총 {len(prices)}개, 유니크 {len(prices_unique)}개")
        if prices_unique:
            print(f"  샘플: {prices_unique[:10]}")
            print(f"  최저: {prices_unique[0]:,}원, 최고: {prices_unique[-1]:,}원")

        # 상품명 후보
        product_selectors = [
            ".product-name", ".prd_name", ".item-name", ".goods-name",
            "a.title", "h3", "h4", ".name", ".tit",
            "[class*=product] [class*=name]", "[class*=goods] [class*=name]",
        ]
        print("\n상품명 selector 탐색:")
        for sel in product_selectors:
            try:
                elements = page.locator(sel).all()
                count = len(elements)
                if count >= 3:  # 의미있는 수의 결과만
                    samples = []
                    for el in elements[:5]:
                        try:
                            t = el.inner_text(timeout=500).strip()
                            if t and len(t) < 100:
                                samples.append(t[:50])
                        except:
                            pass
                    if samples:
                        print(f"  '{sel}' → {count}개")
                        for s in samples[:3]:
                            print(f"      └─ {s}")
            except Exception:
                pass

        # 이미지
        imgs = page.evaluate("""
            () => Array.from(document.images)
                .filter(i => i.naturalWidth > 100 && i.naturalHeight > 100)
                .slice(0, 5)
                .map(i => ({src: i.src, alt: i.alt, w: i.naturalWidth, h: i.naturalHeight}))
        """)
        print(f"\n상품 추정 이미지: {len(imgs)}개")
        for im in imgs[:3]:
            print(f"  {im['w']}x{im['h']} {im['src'][:80]}")

        # 페이지네이션 또는 무한스크롤 단서
        nav_clues = page.evaluate("""
            () => {
                const all = Array.from(document.querySelectorAll('a, button'));
                return all.filter(e => {
                    const t = (e.textContent || '').trim();
                    return /^\\d+$|다음|이전|next|prev|more/i.test(t) && t.length < 10;
                }).slice(0, 10).map(e => ({text: (e.textContent || '').trim(), href: e.href || ''}));
            }
        """)
        print(f"\n페이지네이션 단서: {len(nav_clues)}개")
        for n in nav_clues[:5]:
            print(f"  '{n['text']}' → {n['href'][:80]}")

        # 4. 결과 요약 저장 (다음 단계 코드 작성용)
        analysis = {
            "url": current_url,
            "title": title,
            "price_count": len(prices),
            "price_unique_count": len(prices_unique),
            "price_samples": prices_unique[:20] if prices_unique else [],
            "image_samples": imgs[:5],
            "nav_clues": nav_clues[:10],
            "timestamp": time.time(),
        }
        analysis_file = os.path.join(SCREENSHOT_DIR, "cretec_analysis.json")
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 분석 결과 저장: {analysis_file}")

        print()
        input("\n>>> 더 보고 싶은 페이지 있으면 이동 후 Enter, 아니면 Enter로 종료 ▶ ")

        # 두 번째 페이지 분석 (선택)
        if page.url != current_url:
            print(f"\n추가 분석: {page.url}")
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"cretec_2_{int(time.time())}.png"))

        browser.close()
    print("\n[완료] 다음 단계: 분석 결과 기반으로 자동 수집 코드 작성")


if __name__ == "__main__":
    main()
