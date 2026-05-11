# -*- coding: utf-8 -*-
"""
나비엠알오 (navimro.com) 크롤러
- 회원 로그인 (sales@wholesale-k.com)
- URL: /s/c-{ID}/ (카테고리), /g/{ID}/ (상품)
- 가격이 카드 텍스트에 노출 → 한 페이지에서 다 추출
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

OUT = os.path.join(ROOT, "output", "navimro")
os.makedirs(OUT, exist_ok=True)
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "navimro_storage.json")
CRAWL_DELAY = 5.0


# 나비엠알오 1차 카테고리 → WI 매핑
def map_to_wi(label, name=""):
    text = (label + " " + name).lower()
    if re.search(r"의료|구급", text): return "M"
    if re.search(r"베어링|볼트|너트|fa|체결", text): return "F"
    if re.search(r"실험|크린|측정|분석|계측", text): return "L"
    if re.search(r"청소|위생|와이퍼", text): return "C"
    if re.search(r"안전|장갑|마스크|소방|보호", text): return "S"
    if re.search(r"전선|전기|조명|랜턴|전지|충전", text): return "E"
    if re.search(r"테이프|랩|밴드|마대|포장|박스|운반|하역|바퀴|사다리|공구함|보관|작업대", text): return "P"
    if re.search(r"공구|용접|연마|엔진|건설|유압|에어|작업|원예|절삭|금형|공작|배관|공조|펌프|호스", text): return "T"
    return "O"


def extract_categories(page):
    """모든 c-{ID} 카테고리 링크 추출"""
    page.goto("https://www.navimro.com/", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)
    cats = page.evaluate(r"""() => {
        const seen = new Set();
        return Array.from(document.querySelectorAll('a[href*="/s/c-"]'))
            .map(a => {
                const m = (a.href || '').match(/\/s\/c-(\d+)/);
                return {
                    code: m ? m[1] : null,
                    label: (a.textContent || '').trim().slice(0, 50),
                    href: a.href,
                };
            })
            .filter(c => c.code && c.label && c.label.length < 50)
            .filter(c => {
                if (seen.has(c.code)) return false;
                seen.add(c.code);
                return true;
            });
    }""")
    return cats


def parse_products(page):
    """카테고리 페이지에서 상품 추출 — div.product-list 안의 li.item만 (양성 매칭)"""
    return page.evaluate(r"""() => {
        const seen = new Set();
        const out = [];
        // 진단 결과: depth=6 div.product-list, depth=4 ul.clearFix, depth=3 li.item — 84-85개
        // li.item 안의 a[href*="/g/"]만
        // li.item 자체를 카드 단위로 (a 텍스트는 빈 경우 많음)
        const cards = document.querySelectorAll('li.item');
        for (const card of cards) {
            const a = card.querySelector('a[href*="/g/"]');
            if (!a) continue;
            const m = (a.href || '').match(/\/g\/(\d+)/);
            if (!m) continue;
            const gid = m[1];
            if (seen.has(gid)) continue;
            seen.add(gid);

            const text = (card.innerText || '').trim();
            // 가격 추출
            const priceMatch = text.match(/([\d,]+)\s*원/);
            const price = priceMatch ? parseInt(priceMatch[1].replace(/,/g, '')) : 0;

            // 상품명 — card.innerText 에서 가격/나비엠알오 라벨 제거
            let name = text.replace(/나비엠알오/g, '')
                           .replace(/[\d,]+\s*원.*/s, '')
                           .replace(/\s+/g, ' ')
                           .trim();
            if (!name || name.length < 2) {
                const img = card.querySelector('img');
                name = (img?.alt || '').trim();
            }
            if (!name || name.length < 2) continue;

            // 이미지 추출 — navimro 는 lazy load 라 img.src 가 placeholder(pb-icon.png) 인 경우 다수
            // data-src / data-original 우선, placeholder 패턴 거르기
            const img = card.querySelector('img');
            let imgSrc = '';
            if (img) {
                imgSrc = img.dataset?.src || img.dataset?.original
                       || img.getAttribute('data-src') || img.getAttribute('data-original')
                       || img.src || '';
                // 명백한 placeholder/icon 거르기
                if (/pb-icon|placeholder|blank|spacer|loading\.gif/i.test(imgSrc)) {
                    const alt1 = img.dataset?.original || img.getAttribute('data-original');
                    const alt2 = img.dataset?.src || img.getAttribute('data-src');
                    imgSrc = (alt1 && !/pb-icon|placeholder/i.test(alt1)) ? alt1
                           : (alt2 && !/pb-icon|placeholder/i.test(alt2)) ? alt2
                           : '';
                }
            }
            out.push({
                source_id: gid,
                name: name.slice(0, 200),
                price: price,
                img_src: imgSrc,
                href: a.href,
            });
        }
        return out;
    }""")


def main():
    client = SupabaseClient()

    # sources에 navimro 추가
    existing = client.select("sources", code="eq.navimro")
    if not (isinstance(existing, list) and existing):
        client.insert("sources", {
            "code": "navimro", "name_ko": "나비엠알오 (navimro.com)",
            "type": "crawl", "base_url": "https://www.navimro.com",
            "is_authoritative": False, "requires_login": True, "crawl_delay_sec": 5,
        })

    run = client.insert("crawl_runs", {
        "source_code": "navimro", "status": "running",
        "notes": "나비엠알오 카테고리 트리 + 상품"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    inserted = 0
    updated = 0
    started = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        # 카테고리 추출
        cats = extract_categories(page)
        if len(sys.argv) > 1:
            try: cats = cats[:int(sys.argv[1])]
            except: pass
        print(f"카테고리: {len(cats)}개", flush=True)

        for i, cat in enumerate(cats, 1):
            try:
                # 페이지네이션 — 1페이지부터
                page_num = 1
                cat_ins, cat_upd = 0, 0
                while True:
                    if page_num == 1:
                        url = cat["href"]
                    else:
                        # ?page=N 또는 #page=N
                        url = cat["href"].rstrip('/') + f"/?page={page_num}"
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    except Exception:
                        page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    # 4초 대기 + 스크롤 5회 (lazy load 트리거)
                    page.wait_for_timeout(4000)
                    for _ in range(5):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(700)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(500)

                    products = parse_products(page)
                    # 디버그: 첫 페이지마다 상태 출력
                    if page_num == 1:
                        debug = page.evaluate(r"""() => ({
                            url: location.href,
                            li_item_a: document.querySelectorAll('li.item a[href*="/g/"]').length,
                            all_g: document.querySelectorAll('a[href*="/g/"]').length,
                            body_len: document.body.innerText.length
                        })""")
                        print(f"    [DBG cat={cat['code']}] url={debug['url']} li.item={debug['li_item_a']} all_g={debug['all_g']} body={debug['body_len']} parsed={len(products)}", flush=True)
                    if not products:
                        break

                    wi_cat = map_to_wi(cat["label"])
                    new_cnt = 0
                    for prod in products:
                        try:
                            existing_p = client.select("products", select="id",
                                **{
                                    "source_code": "eq.navimro",
                                    "source_product_id": f"eq.{prod['source_id']}"
                                })
                            payload = {
                                "source_code": "navimro",
                                "source_product_id": prod["source_id"][:50],
                                "category_code": wi_cat,
                                "sub_category": cat["label"][:100],
                                "name_ko": prod["name"],
                                "search_keywords": f"{prod['name']} {cat['label']}"[:500],
                                "primary_image_url": prod.get("img_src") or None,
                                "image_urls": [prod["img_src"]] if prod.get("img_src") else [],
                                "cost_price": prod.get("price") or None,
                                "list_price": prod.get("price") or None,
                                "margin_pct": 0,
                                "currency": "KRW",
                                "price_unit": "EA",
                                "source_url": prod.get("href"),
                                "is_directly_sold": False,
                                "is_published": True,
                                "quality_score": 0.85,
                                "last_crawled_at": datetime.now(timezone.utc).isoformat(),
                            }
                            if isinstance(existing_p, list) and existing_p:
                                client.update("products", {"id": existing_p[0]["id"]}, payload)
                                cat_upd += 1
                            else:
                                client.insert("products", payload)
                                cat_ins += 1
                                new_cnt += 1
                        except Exception:
                            pass

                    # 페이지네이션 — 신규 0이거나 너무 적으면 종료
                    if new_cnt == 0 or page_num >= 50:
                        break
                    page_num += 1

                inserted += cat_ins
                updated += cat_upd
                if cat_ins + cat_upd > 0 or i % 10 == 0:
                    elapsed = time.time() - started
                    eta = (elapsed / i) * (len(cats) - i) / 60
                    print(f"  [{i}/{len(cats)}] {cat['label'][:25]:<25} +{cat_ins} ~{cat_upd} (누적 {inserted+updated}, ETA {eta:.0f}분)", flush=True)
            except Exception as e:
                print(f"  [{i}] ERROR {cat['label']}: {str(e)[:80]}", flush=True)

            time.sleep(CRAWL_DELAY)

        browser.close()

    if run_id:
        client.update("crawl_runs", {"id": run_id}, {
            "status": "success",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "products_added": inserted,
            "products_updated": updated,
        })

    print(f"\n=== 완료 === 신규 {inserted}, 업데이트 {updated}, 소요 {(time.time()-started)/60:.1f}분")


if __name__ == "__main__":
    main()
