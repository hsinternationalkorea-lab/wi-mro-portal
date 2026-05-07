# -*- coding: utf-8 -*-
"""
대한과학 (mall.daihan-sci.com) 크롤러 v2 — 상품 상세 페이지 진입 모드
- /categories/alpha/all 한 번 → 1,630개 상품 URL 추출
- 각 상품 상세 페이지 60초 간격으로 진입 → 가격·사양 추출
- 27시간 자동 (밤사이 + 다음날)
- 중간 끊겨도 upsert로 이어서 가능
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

OUT = os.path.join(ROOT, "output", "daihan")
os.makedirs(OUT, exist_ok=True)
URL_LIST_FILE = os.path.join(OUT, "product_urls.json")
CRAWL_DELAY = 60.0  # robots.txt 준수


def map_to_wi(label, name=""):
    text = (label + " " + name).lower()
    if re.search(r"safety|안전|소화|구조|보호|마스크|방독|글러브|gloves?|nitrile|apparel", text): return "S"
    if re.search(r"medical|의료|구급|swab|lancet|scalpel|블레이드|syringe|주사", text): return "M"
    if re.search(r"clean|크린|방진|wiper|와이퍼|cleanroom", text): return "C"
    return "L"


def extract_url_list(page):
    """알파벳 페이지에서 1,630개 상품 URL 추출"""
    page.goto("https://mall.daihan-sci.com/categories/alpha/all", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)
    products = page.evaluate(r"""() => {
        const links = document.querySelectorAll('a[href*="/pdt/alpha/"]');
        const seen = new Set();
        const out = [];
        for (const a of links) {
            const m = (a.href || '').match(/\/pdt\/alpha\/([A-Z0-9.]+)/);
            if (!m) continue;
            const cid = m[1];
            if (seen.has(cid)) continue;
            seen.add(cid);
            const card = a.closest('li, .item, .product, [class*=item], div');
            const text = card ? (card.innerText || '').trim() : '';
            const img = card ? card.querySelector('img') : null;
            out.push({
                catalog_no: cid,
                name: (a.textContent || '').trim().slice(0, 200),
                fulltext: text.slice(0, 200),
                img_src: img ? img.src : '',
                href: a.href,
            });
        }
        return out;
    }""")
    return products


def extract_detail(page, url):
    """상품 상세 페이지에서 가격·사양 추출"""
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except Exception:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)

    info = page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        const priceMatch = text.match(/(\d{1,3}(?:,\d{3})+)\s*원/);
        // 큰 이미지
        const imgs = Array.from(document.querySelectorAll('img'))
            .filter(i => i.naturalWidth > 200 && i.naturalHeight > 200)
            .slice(0, 1);
        // 사양 (테이블)
        const tables = Array.from(document.querySelectorAll('table'));
        let spec = '';
        for (const t of tables) {
            const rows = Array.from(t.querySelectorAll('tr'));
            if (rows.length >= 2 && rows.length <= 30) {
                spec = rows.map(r => r.innerText.replace(/\n/g, ': ')).join(' | ').slice(0, 800);
                break;
            }
        }
        // 카테고리 (breadcrumb)
        const breadcrumb = Array.from(document.querySelectorAll('.breadcrumb a, .crumbs a, nav a'))
            .map(a => a.textContent.trim())
            .filter(t => t && t.length < 30)
            .slice(0, 5);
        return {
            price: priceMatch ? parseInt(priceMatch[1].replace(/,/g, '')) : 0,
            big_img: imgs.length ? imgs[0].src : '',
            spec: spec,
            breadcrumb: breadcrumb,
        };
    }""")
    return info


def main():
    client = SupabaseClient()

    # sources에 daihan 추가 (없을 때)
    existing = client.select("sources", code="eq.daihan")
    if not (isinstance(existing, list) and existing):
        client.insert("sources", {
            "code": "daihan", "name_ko": "대한과학 (mall.daihan-sci.com)",
            "type": "crawl", "base_url": "https://mall.daihan-sci.com",
            "is_authoritative": False, "requires_login": False, "crawl_delay_sec": 60,
        })

    run = client.insert("crawl_runs", {
        "source_code": "daihan", "status": "running",
        "notes": "상품 상세 페이지 진입 모드 (가격 추출, 27시간)"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    started = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR", viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()

        # 1. URL 리스트 (캐시 또는 새로 추출)
        if os.path.exists(URL_LIST_FILE):
            with open(URL_LIST_FILE, encoding="utf-8") as f:
                url_list = json.load(f)
            print(f"캐시된 URL: {len(url_list)}개", flush=True)
        else:
            print("URL 리스트 추출 중...", flush=True)
            url_list = extract_url_list(page)
            with open(URL_LIST_FILE, "w", encoding="utf-8") as f:
                json.dump(url_list, f, ensure_ascii=False, indent=2)
            print(f"저장: {len(url_list)}개", flush=True)

        # CLI: 시작 인덱스 + 처리할 수
        start_idx = 0
        max_count = len(url_list)
        if len(sys.argv) > 1:
            try:
                max_count = int(sys.argv[1])
            except ValueError:
                pass
        if len(sys.argv) > 2:
            try:
                start_idx = int(sys.argv[2])
            except ValueError:
                pass

        targets = url_list[start_idx:start_idx + max_count]
        print(f"처리 범위: {start_idx} ~ {start_idx + len(targets)} (총 {len(url_list)})", flush=True)

        inserted = 0
        updated = 0
        for i, item in enumerate(targets, 1):
            global_i = start_idx + i
            cid = item.get("catalog_no")
            if not cid:
                continue

            # 이미 DB에 있는 SKU는 건너뛰기 (가격 있으면)
            check = client.select("products", select="id,cost_price",
                **{
                    "source_code": "eq.daihan",
                    "source_product_id": f"eq.{cid}"
                })
            already = False
            existing_id = None
            if isinstance(check, list) and check:
                existing_id = check[0]["id"]
                if check[0].get("cost_price") and check[0]["cost_price"] > 0:
                    already = True

            if already:
                if global_i % 50 == 0:
                    print(f"  [{global_i}/{len(url_list)}] {cid} 이미 가격 있음 — 건너뜀", flush=True)
                continue

            # 상세 페이지 진입
            try:
                detail = extract_detail(page, item["href"])
            except Exception as e:
                print(f"  [{global_i}/{len(url_list)}] {cid} ERROR: {str(e)[:60]}", flush=True)
                time.sleep(CRAWL_DELAY)
                continue

            price = detail.get("price", 0)
            spec = detail.get("spec", "")
            big_img = detail.get("big_img") or item.get("img_src", "")
            breadcrumb = " > ".join(detail.get("breadcrumb", [])[:3])

            wi_cat = map_to_wi(breadcrumb, item["name"])

            payload = {
                "source_code": "daihan",
                "source_product_id": cid[:100],
                "category_code": wi_cat,
                "sub_category": breadcrumb[:100] or "Daihan",
                "name_ko": item["name"],
                "spec": spec[:500] if spec else None,
                "search_keywords": f"{item['name']} {breadcrumb} {cid}"[:500],
                "primary_image_url": big_img or None,
                "image_urls": [big_img] if big_img else [],
                "cost_price": price or None,
                "list_price": price or None,
                "margin_pct": 0,
                "currency": "KRW",
                "price_unit": "EA",
                "source_url": item["href"],
                "is_directly_sold": False,
                "is_published": True,
                "quality_score": 0.85 if price else 0.6,
                "last_crawled_at": datetime.now(timezone.utc).isoformat(),
            }

            try:
                if existing_id:
                    client.update("products", {"id": existing_id}, payload)
                    updated += 1
                else:
                    client.insert("products", payload)
                    inserted += 1
                if global_i % 10 == 0 or price > 0:
                    elapsed = (time.time() - started) / 60
                    eta_h = (elapsed / i) * (len(targets) - i) / 60
                    p_str = f"₩{price:,}" if price else "(가격X)"
                    print(f"  [{global_i}/{len(url_list)}] {cid:<14} {p_str:<14} +{inserted} ~{updated} (ETA {eta_h:.1f}h)", flush=True)
            except Exception as e:
                print(f"  [{global_i}] DB ERROR: {str(e)[:60]}", flush=True)

            # robots.txt Crawl-delay 60s 엄격 준수
            time.sleep(CRAWL_DELAY)

        browser.close()

    if run_id:
        client.update("crawl_runs", {"id": run_id}, {
            "status": "success",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "products_added": inserted,
            "products_updated": updated,
        })

    print(f"\n=== 완료 ===")
    print(f"신규: {inserted}, 업데이트: {updated}")
    print(f"소요: {(time.time()-started)/3600:.1f}시간")


if __name__ == "__main__":
    main()
