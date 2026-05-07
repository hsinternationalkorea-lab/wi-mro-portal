# -*- coding: utf-8 -*-
"""서브원 JSON API request body 캡처 → 직접 호출용 정보"""
import os, sys, json, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")
OUT = os.path.join(ROOT, "output", "subone")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=COOKIE,
        user_agent="Mozilla/5.0 Chrome/120",
        locale="ko-KR", viewport={"width":1400,"height":900},
    )
    page = context.new_page()

    # 모든 POST request의 body + response 캡처
    captures = []
    target_endpoints = [
        'select-main-menu-list',
        'select-main-category-list',
        'catg-best-prd-list',
        'ssp-pw-sm',
        'pmt-popup-list',
    ]

    def is_target(url):
        return any(t in url for t in target_endpoints)

    async def handle_response(response):
        try:
            if not is_target(response.url): return
            req = response.request
            body = req.post_data
            text = ""
            try:
                text = await response.text()
                text = text[:3000]
            except: pass
            captures.append({
                'url': response.url,
                'method': req.method,
                'request_body': body,
                'request_headers': {k:v for k,v in req.headers.items() if k.lower() in ('content-type','x-requested-with','accept')},
                'status': response.status,
                'response_body': text,
            })
        except: pass

    # 동기 버전만 사용
    sync_captures = []
    def sync_handler(response):
        if not is_target(response.url): return
        req = response.request
        try:
            text = response.text()[:3000] if response.ok else ""
        except: text = ""
        sync_captures.append({
            'url': response.url,
            'method': req.method,
            'request_body': req.post_data,
            'content_type': req.headers.get('content-type', ''),
            'accept': req.headers.get('accept', ''),
            'x_requested_with': req.headers.get('x-requested-with', ''),
            'status': response.status,
            'response_preview': text,
        })

    page.on("response", sync_handler)

    print("=" * 60)
    print("[1] 메인 페이지 진입 → API 호출 캡처")
    print("=" * 60)
    page.goto("https://store.serveone.co.kr/ssp/main/index.do",
              wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(5000)
    for _ in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)

    # 카테고리 메뉴 클릭 (전체 카테고리 보기)
    page.evaluate(r"""() => {
        // 전체보기/카테고리 메뉴 호버
        for (const e of document.querySelectorAll('[class*=catg], [class*=category], [class*=gnb]')) {
            try { e.dispatchEvent(new MouseEvent('mouseover', {bubbles:true})); } catch(err){}
            try { e.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true})); } catch(err){}
            try { e.click(); } catch(err){}
        }
    }""")
    page.wait_for_timeout(3000)

    print(f"\n캡처된 API 호출: {len(sync_captures)}건")
    for c in sync_captures[:30]:
        path = c['url'].replace('https://store.serveone.co.kr', '')
        print(f"\n  {c['method']} {path[:80]}  [{c['status']}]")
        if c['content_type']:
            print(f"    Content-Type: {c['content_type']}")
        if c['accept']:
            print(f"    Accept: {c['accept'][:60]}")
        if c['x_requested_with']:
            print(f"    X-Requested-With: {c['x_requested_with']}")
        if c['request_body']:
            print(f"    body: {c['request_body'][:200]}")
        if c['response_preview']:
            print(f"    response: {c['response_preview'][:300]}")

    # 결과 저장
    with open(os.path.join(OUT, "api_capture.json"), "w", encoding="utf-8") as f:
        json.dump(sync_captures, f, ensure_ascii=False, indent=2)
    print(f"\n저장: {OUT}/api_capture.json")

    browser.close()
