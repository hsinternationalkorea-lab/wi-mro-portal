# -*- coding: utf-8 -*-
"""
크레텍 자동 로그인 + 사이트 구조 탐색
- .env의 CRETEC_USER/PASS로 자동 로그인
- 로그인 후 메인/검색/카테고리 페이지 구조 분석
- 결과 JSON으로 저장 → 다음 단계 수집 코드 작성용
"""
import os
import sys
import json
import time
import re
import ctypes
from playwright.sync_api import sync_playwright

# Windows 절전 방지 (작업 중 노트북 sleep 차단)
if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from supabase_client import load_env

SECRETS = os.path.join(ROOT, "_secrets")
COOKIES = os.path.join(SECRETS, "cookies")
OUT = os.path.join(ROOT, "output", "cretec")
os.makedirs(COOKIES, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

STORAGE = os.path.join(COOKIES, "cretec_storage.json")


def main():
    env = load_env()
    user = env.get("CRETEC_USER")
    pwd = env.get("CRETEC_PASS")
    if not user or not pwd:
        print("[ERROR] .env에 CRETEC_USER/PASS 없음")
        return

    print("=" * 70)
    print("크레텍 자동 로그인 + 사이트 분석")
    print("=" * 70)
    print(f"ID: {user[:3]}***")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        # bot detection 우회
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = context.new_page()

        # 1. 메인 페이지
        print("\n[1] 메인 페이지 로드")
        page.goto("https://www.cretec.kr/", timeout=20000)
        page.wait_for_load_state("networkidle", timeout=10000)
        print(f"   URL: {page.url}")
        print(f"   Title: {page.title()}")
        page.screenshot(path=os.path.join(OUT, "01_main.png"))

        # 2. 모든 링크에서 로그인 페이지 찾기
        print("\n[2] 로그인 진입 경로 탐색")
        login_links = page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a, button'));
                return links.filter(l => {
                    const t = (l.textContent||'').trim();
                    return /로그인|login|signin/i.test(t) && t.length < 20;
                }).map(l => ({
                    text: (l.textContent||'').trim(),
                    href: l.href || '',
                    onclick: l.onclick ? 'yes' : 'no',
                    cls: (l.className||'').toString().slice(0,80)
                }));
            }
        """)
        print(f"   로그인 후보 링크: {len(login_links)}개")
        for l in login_links[:5]:
            print(f"     '{l['text']}' → {l['href'][:80] if l['href'] else 'JS'}")

        # 3. 로그인 페이지 직접 시도
        login_urls_to_try = [
            "https://www.cretec.kr/kor/member/login.jsp",
            "https://www.cretec.kr/login",
            "https://www.cretec.kr/kor/login",
            "https://www.cretec.kr/member/login",
        ]
        if login_links and login_links[0]["href"]:
            login_urls_to_try.insert(0, login_links[0]["href"])

        for url in login_urls_to_try:
            try:
                print(f"\n[3] 로그인 페이지 시도: {url}")
                page.goto(url, timeout=15000)
                page.wait_for_load_state("networkidle", timeout=5000)
                # 비밀번호 input 있으면 진짜 로그인 페이지
                pw_count = page.locator("input[type=password]").count()
                if pw_count > 0:
                    print(f"   ✅ 로그인 페이지 발견 (password input {pw_count}개)")
                    page.screenshot(path=os.path.join(OUT, "02_login.png"))
                    break
                else:
                    print(f"   ⚠ password input 없음, 다음 시도")
            except Exception as e:
                print(f"   ❌ {e}")

        # 4. 로그인 form input 분석
        print("\n[4] 로그인 form 분석")
        form_info = page.evaluate("""
            () => {
                const inputs = Array.from(document.querySelectorAll('input'));
                return inputs.map(i => ({
                    type: i.type, name: i.name, id: i.id,
                    placeholder: i.placeholder,
                    required: i.required,
                    cls: (i.className||'').toString().slice(0,40)
                })).filter(i => i.type !== 'hidden' || i.name);
            }
        """)
        for f in form_info[:10]:
            print(f"   {f}")

        # 5. ID/PW 입력 시도
        print("\n[5] 자동 로그인 시도")
        try:
            # ID input — type=text 또는 name에 id/user 포함
            id_selectors = [
                "input[type=text][name*=id i]",
                "input[type=text][name*=user i]",
                "input[type=text][id*=id i]",
                "input[type=text][id*=user i]",
                "input[type=text]:not([name*=search i]):visible",
            ]
            id_input = None
            for sel in id_selectors:
                try:
                    if page.locator(sel).first.is_visible(timeout=1000):
                        id_input = sel
                        break
                except Exception:
                    continue

            pw_input = "input[type=password]"

            if id_input:
                print(f"   ID input: {id_input}")
                page.locator(id_input).first.fill(user)
                page.locator(pw_input).first.fill(pwd)

                # 로그인 버튼 찾기
                page.screenshot(path=os.path.join(OUT, "03_filled.png"))

                # 엔터 또는 로그인 버튼
                page.locator(pw_input).first.press("Enter")
                page.wait_for_load_state("networkidle", timeout=15000)
                page.wait_for_timeout(2000)

                print(f"   로그인 후 URL: {page.url}")
                page.screenshot(path=os.path.join(OUT, "04_after_login.png"))

                # 로그인 성공 검증 — 로그아웃 링크 또는 마이페이지 보이는가
                login_status = page.evaluate("""
                    () => {
                        const t = document.body.innerText;
                        return {
                            has_logout: /로그아웃|logout/i.test(t),
                            has_mypage: /마이페이지|mypage|my page/i.test(t),
                            has_username: /17090721/.test(t),
                            sample_text: t.slice(0, 500)
                        };
                    }
                """)
                if login_status["has_logout"] or login_status["has_mypage"]:
                    print(f"   ✅ 로그인 성공 (logout 링크 발견)")
                    # 쿠키 저장
                    context.storage_state(path=STORAGE)
                    print(f"   ✅ 쿠키 저장: {STORAGE}")
                else:
                    print(f"   ⚠ 로그인 성공 여부 모호. 샘플 텍스트:")
                    print(f"      {login_status['sample_text'][:200]}")
            else:
                print(f"   ❌ ID input 못 찾음")

        except Exception as e:
            print(f"   ❌ 로그인 실패: {type(e).__name__}: {e}")

        # 6. 로그인 후 화면 구조 분석
        print("\n[6] 로그인 후 페이지 구조")
        try:
            # 카테고리 메뉴 찾기
            categories = page.evaluate("""
                () => {
                    const all = Array.from(document.querySelectorAll('a, [role=menuitem]'));
                    return all.filter(a => {
                        const t = (a.textContent||'').trim();
                        return t.length > 1 && t.length < 20 && a.href;
                    }).slice(0, 30).map(a => ({
                        text: (a.textContent||'').trim(),
                        href: a.href
                    }));
                }
            """)
            # 카테고리 같은 패턴 (안전, 공구, 전기 등)
            cat_keywords = ["안전", "공구", "전기", "측정", "포장", "산업", "용접", "에너지", "베어링", "체결"]
            potential_cats = [c for c in categories if any(k in c["text"] for k in cat_keywords)]
            print(f"   카테고리 추정 링크: {len(potential_cats)}개")
            for c in potential_cats[:10]:
                print(f"     '{c['text']}' → {c['href'][:80]}")

            # 검색 input
            search_inp = page.evaluate("""
                () => {
                    const candidates = Array.from(document.querySelectorAll('input[type=search], input[name*=search i], input[placeholder*=검색], input[name*=keyword]'));
                    return candidates.map(i => ({
                        sel: 'name=' + (i.name || '') + ' id=' + (i.id || '') + ' placeholder=' + (i.placeholder || ''),
                        visible: i.offsetParent !== null
                    }));
                }
            """)
            print(f"\n   검색 input 후보: {len(search_inp)}")
            for s in search_inp[:5]:
                print(f"     {s}")

        except Exception as e:
            print(f"   분석 실패: {e}")

        # 결과 저장
        analysis = {
            "main_url": "https://www.cretec.kr/",
            "after_login_url": page.url,
            "login_success": login_status.get("has_logout", False) if 'login_status' in dir() else False,
            "form_inputs": form_info[:10],
            "categories": potential_cats[:20] if 'potential_cats' in dir() else [],
            "timestamp": time.time(),
        }
        with open(os.path.join(OUT, "analysis.json"), "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 분석 결과 저장: {OUT}/analysis.json")
        print(f"✅ 스크린샷 4개 저장: {OUT}/")

        browser.close()


if __name__ == "__main__":
    main()
