# -*- coding: utf-8 -*-
"""
3개 회원 사이트 통합 로그인 헬퍼 — 쿠키만 저장
사용:
    python3 crawlers/login_setup.py            # 쿠키 없는 사이트만
    python3 crawlers/login_setup.py --force    # 모두 새로 로그인 (기존 쿠키 덮어씀)
"""
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES = os.path.join(ROOT, "_secrets", "cookies")
os.makedirs(COOKIES, exist_ok=True)

FORCE = "--force" in sys.argv

SITES = [
    {
        "name": "cretec (크레텍)",
        "url": "https://ctx.cretec.kr/",
        "storage": "cretec_storage.json",
        "hint": "대리점 회원 ID/PW. 로그인 후 가격이 보이는 카테고리 페이지까지 들어가세요.",
    },
    {
        "name": "navimro (나비엠알오)",
        "url": "https://www.navimro.com/",
        "storage": "navimro_storage.json",
        "hint": "sales@wholesale-k.com PW. 로그인 후 회원 가격 보이는 카테고리까지.",
    },
    {
        "name": "subone (서브원)",
        "url": "https://store.serveone.co.kr/",
        "storage": "serveone_storage.json",
        "hint": "yjyoon 회원 PW. 로그인 후 카테고리 페이지까지.",
    },
]


def main():
    print("\n" + "=" * 70)
    print("  WI MRO — 3개 회원 사이트 통합 로그인 (쿠키 받기)")
    print("=" * 70)

    with sync_playwright() as p:
        for i, site in enumerate(SITES, 1):
            path = os.path.join(COOKIES, site["storage"])
            if os.path.exists(path) and not FORCE:
                print(f"\n[{i}/{len(SITES)}] ✓ {site['name']}: 쿠키 이미 있음 — 스킵")
                continue

            print(f"\n{'='*70}")
            print(f"  [{i}/{len(SITES)}] {site['name']}")
            print(f"{'='*70}")
            print(f"\n  안내: {site['hint']}")
            print(f"  URL: {site['url']}\n")
            input(f"  >>> 준비되면 Enter (브라우저 창 열림) ▶ ")

            browser = p.chromium.launch(headless=False, slow_mo=50)
            context = browser.new_context(
                locale="ko-KR",
                viewport={"width": 1400, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page = context.new_page()
            try:
                page.goto(site["url"], timeout=30000)
            except Exception as e:
                print(f"  ⚠ 페이지 로드 실패: {e}")
                print(f"  브라우저에서 직접 {site['url']} 들어가셔도 됩니다")

            print()
            print(f"  >>> 브라우저에서 로그인 → 가격 보이는 페이지까지 이동")
            print(f"  >>> 완료하면 이 터미널 창에서 Enter")
            input(f"  >>> Enter ▶ ")

            try:
                context.storage_state(path=path)
                print(f"  ✅ 쿠키 저장: {path}")
            except Exception as e:
                print(f"  ❌ 쿠키 저장 실패: {e}")
            finally:
                browser.close()

    print("\n" + "=" * 70)
    print("  ✅ 모든 작업 완료")
    print("=" * 70)
    print(f"\n  저장된 쿠키 파일:")
    for site in SITES:
        path = os.path.join(COOKIES, site["storage"])
        status = "✓" if os.path.exists(path) else "✗"
        print(f"    {status} {site['storage']}")
    print()


if __name__ == "__main__":
    main()
