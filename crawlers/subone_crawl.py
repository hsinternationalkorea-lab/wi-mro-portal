# -*- coding: utf-8 -*-
"""
서브원 (store.serveone.co.kr) 회원 크롤러 v2
- 쿠키 사용 (사용자 1회 로그인 완료)
- URL: /sa/disp/ssp-pw-jm-01.do?brndhlMainId=N (전문관)
        /pr/pr-product-detail.do?prdId=N (상품)
- robots.txt: Crawl-delay 3초
"""
import os
import sys
import json
import re
import time
import ctypes
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from supabase_client import SupabaseClient

if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

OUT = os.path.join(ROOT, "output", "subone")
os.makedirs(OUT, exist_ok=True)
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")
CRAWL_DELAY = 3.0


def map_to_wi(label, name=""):
    text = (label + " " + name).lower()
    if re.search(r"의료|구급", text): return "M"
    if re.search(r"베어링|볼트|너트|체결", text): return "F"
    if re.search(r"실험|크린|측정|분석|계측|연구|화학물질", text): return "L"
    if re.search(r"청소|위생|와이퍼", text): return "C"
    if re.search(r"안전|소방|방재|보호|마스크|글러브|장갑|솔루션", text): return "S"
    if re.search(r"전선|전기|조명|전지|충전|자동제어|omron|반도체", text): return "E"
    if re.search(r"포장|박스|운반|하역|공구함|작업대|특가", text): return "P"
    if re.search(r"공구|용접|연마|에어|절삭|배관|드릴|스마토", text): return "T"
    return "O"


def extract_products_from_page(page):
    """페이지에서 모든 prdId 상품 + 가격 추출"""
    return page.evaluate(r"""() => {
        const seen = new Set();
        const out = [];
        const links = document.querySelectorAll('a[href*="prdId="]');
        for (const a of links) {
            const m = (a.href || '').match(/prdId=(\d+)/);
            if (!m) continue;
            const pid = m[1];
            if (seen.has(pid)) continue;
            seen.add(pid);

            const card = a.closest('li, .item, .product, [class*=item], [class*=product], [class*=goods], div');
            if (!card) continue;
            const text = (card.innerText || '').trim();
            const priceMatch = text.match(/(\d{1,3}(?:,\d{3})+)\s*원/);
            const img = card.querySelector('img');

            let name = (a.textContent || '').trim();
            // 가격 라인 제거, 숫자만 있는 것도 제거
            name = name.replace(/[\d,]+\s*원.*/, '').replace(/^\s*\d+\s*$/, '').trim();
            if (!name && img) name = img.alt || '';
            if (!name || name.length < 2) continue;

            out.push({
                source_id: pid,
                name: name.slice(0, 200),
                price: priceMatch ? parseInt(priceMatch[1].replace(/,/g, '')) : 0,
                img_src: img ? (img.src || img.dataset?.src || '') : '',
                href: a.href.startsWith('http') ? a.href : 'https://store.serveone.co.kr' + a.href,
            });
        }
        return out;
    }""")


def main():
    client = SupabaseClient()

    if not os.path.exists(COOKIE):
        print(f"❌ 쿠키 없음: {COOKIE}")
        sys.exit(1)

    # sources 등록
    existing = client.select("sources", code="eq.subone")
    if not (isinstance(existing, list) and existing):
        client.insert("sources", {
            "code": "subone", "name_ko": "서브원 (store.serveone.co.kr)",
            "type": "crawl", "base_url": "https://store.serveone.co.kr",
            "is_authoritative": False, "requires_login": True, "crawl_delay_sec": 3,
        })

    run = client.insert("crawl_runs", {
        "source_code": "subone", "status": "running",
        "notes": "회원 모드 (쿠키 사용)"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    inserted = 0
    updated = 0
    started = time.time()
    seen_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        # 진입 URL 후보 — 메인 + 전문관 ID 자동 발견
        main_urls = [
            ("메인", "https://store.serveone.co.kr/ssp/main/index.do"),
        ]

        # 메인에서 brndhlMainId·brndhlSeq 추출
        page.goto(main_urls[0][1], wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(4000)
        # 스크롤로 lazy load 트리거
        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(700)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        # 카테고리·전문관 URL
        cat_urls = page.evaluate(r"""() => {
            const seen = new Set();
            const out = [];
            const links = Array.from(document.querySelectorAll('a'));
            for (const a of links) {
                const h = a.href || '';
                if (!/\/sa\/disp\/|\/sa\/pmt\//.test(h)) continue;
                if (seen.has(h)) continue;
                seen.add(h);
                out.push({label: (a.textContent||'').trim().slice(0,40), href: h});
            }
            // brndhlMainId 1~50 자동 생성 (못 찾은 것 보강)
            for (let id = 1; id <= 50; id++) {
                const u = `https://store.serveone.co.kr/sa/disp/ssp-pw-jm-01.do?brndhlMainId=${id}`;
                if (!seen.has(u)) {
                    out.push({label: `전문관-${id}`, href: u});
                    seen.add(u);
                }
            }
            return out;
        }""")
        all_urls = main_urls + [(c["label"], c["href"]) for c in cat_urls]

        # 메인에서 직접 보이는 상품도 우선 처리
        print(f"\n메인 페이지 상품 추출", flush=True)
        main_products = extract_products_from_page(page)
        print(f"  메인 상품: {len(main_products)}", flush=True)

        # CLI: 처리할 URL 수
        if len(sys.argv) > 1:
            try: all_urls = all_urls[:int(sys.argv[1])]
            except: pass

        print(f"\n방문할 URL: {len(all_urls)}개\n", flush=True)

        # 메인 상품 먼저 저장
        for prod in main_products:
            if prod["source_id"] in seen_ids: continue
            seen_ids.add(prod["source_id"])
            try:
                ex = client.select("products", select="id",
                    **{"source_code": "eq.subone", "source_product_id": f"eq.{prod['source_id']}"})
                payload = {
                    "source_code": "subone", "source_product_id": prod["source_id"],
                    "category_code": "O", "sub_category": "메인",
                    "name_ko": prod["name"],
                    "search_keywords": prod["name"][:500],
                    "primary_image_url": prod.get("img_src") or None,
                    "image_urls": [prod["img_src"]] if prod.get("img_src") else [],
                    "cost_price": prod.get("price") or None,
                    "list_price": prod.get("price") or None,
                    "margin_pct": 0, "currency": "KRW", "price_unit": "EA",
                    "source_url": prod.get("href"),
                    "is_directly_sold": False, "is_published": True, "quality_score": 0.85,
                    "last_crawled_at": datetime.now(timezone.utc).isoformat(),
                }
                if isinstance(ex, list) and ex:
                    client.update("products", {"id": ex[0]["id"]}, payload)
                    updated += 1
                else:
                    client.insert("products", payload)
                    inserted += 1
            except Exception:
                pass

        # 카테고리·전문관 순회
        for i, (label, url) in enumerate(all_urls[1:], 1):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2500)
                for _ in range(4):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(600)
                products = extract_products_from_page(page)

                wi_cat = map_to_wi(label)
                cat_ins, cat_upd = 0, 0
                for prod in products:
                    if prod["source_id"] in seen_ids: continue
                    seen_ids.add(prod["source_id"])
                    try:
                        ex = client.select("products", select="id",
                            **{"source_code": "eq.subone", "source_product_id": f"eq.{prod['source_id']}"})
                        payload = {
                            "source_code": "subone", "source_product_id": prod["source_id"],
                            "category_code": wi_cat, "sub_category": label[:100],
                            "name_ko": prod["name"],
                            "search_keywords": f"{prod['name']} {label}"[:500],
                            "primary_image_url": prod.get("img_src") or None,
                            "image_urls": [prod["img_src"]] if prod.get("img_src") else [],
                            "cost_price": prod.get("price") or None,
                            "list_price": prod.get("price") or None,
                            "margin_pct": 0, "currency": "KRW", "price_unit": "EA",
                            "source_url": prod.get("href"),
                            "is_directly_sold": False, "is_published": True, "quality_score": 0.85,
                            "last_crawled_at": datetime.now(timezone.utc).isoformat(),
                        }
                        if isinstance(ex, list) and ex:
                            client.update("products", {"id": ex[0]["id"]}, payload)
                            cat_upd += 1
                        else:
                            client.insert("products", payload)
                            cat_ins += 1
                    except Exception: pass

                inserted += cat_ins
                updated += cat_upd
                if cat_ins + cat_upd > 0 or i % 5 == 0:
                    elapsed = time.time() - started
                    eta = (elapsed / i) * (len(all_urls) - 1 - i) / 60
                    print(f"  [{i}/{len(all_urls)-1}] {label[:25]:<25} +{cat_ins} ~{cat_upd} (누적 {inserted+updated}, ETA {eta:.0f}분)", flush=True)
            except Exception as e:
                print(f"  [{i}] ERROR {label}: {str(e)[:60]}", flush=True)
            time.sleep(CRAWL_DELAY)

        browser.close()

    if run_id:
        client.update("crawl_runs", {"id": run_id}, {
            "status": "success",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "products_added": inserted, "products_updated": updated,
        })

    print(f"\n=== 완료 === 신규 {inserted}, 업데이트 {updated}, 소요 {(time.time()-started)/60:.1f}분")


if __name__ == "__main__":
    main()
