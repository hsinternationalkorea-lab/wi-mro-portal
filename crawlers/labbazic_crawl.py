# -*- coding: utf-8 -*-
"""
석림랩텍 (LABbazic) 크롤러
- robots.txt: User-agent: * Allow: / (가장 우호적)
- URL 패턴:
  - 카테고리: /goods/goods_list.php?cateCd=XXX
  - 검색:   /goods/goods_search.php?keyword=XXX
- 비회원도 가격 노출 (시험 검증 OK)
- 우리 카테고리 매핑: 대부분 L (계측·실험·연구) — 석림랩텍 = 실험실 기자재 전문
"""
import os
import sys
import json
import re
import time
import ctypes
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from supabase_client import SupabaseClient

if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

OUT = os.path.join(ROOT, "output", "labbazic")
os.makedirs(OUT, exist_ok=True)
CRAWL_DELAY = 5.0


# 우리 카테고리 매핑 (석림랩텍 카테고리명 → 우리 9개)
def map_to_wi(label, name="", spec=""):
    text = (label + " " + name + " " + spec).lower()
    # 안전 (석림세이프티 산업안전)
    if re.search(r"안전|safety|소화|구조|보호|마스크|방독|방진(?!필터)|장갑|gloves?|nitrile|벽화", text):
        return "S"
    # 의료 (스왑·일회용 의료용품)
    if re.search(r"의료|medical|swab|lancet|scalpel|블레이드", text):
        return "M"
    # 측정·분석·계측
    if re.search(r"측정|계측|분석|analyzer|meter|electrode|chromatograph|cell|culture|blotting|membrane|filter", text):
        return "L"
    # 실험실 기자재 (default — 석림랩텍 자체가 실험실 전문)
    return "L"


def extract_categories(page):
    """석림랩텍 카테고리 트리 추출 (cateCd=XXX)"""
    # labbazic.com은 networkidle까지 가지 않을 때가 많아 domcontentloaded로 완화 + 60s 타임아웃 + 1회 재시도
    last_err = None
    for attempt in range(2):
        try:
            page.goto("https://www.labbazic.com/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            break
        except Exception as e:
            last_err = e
            print(f"[retry {attempt+1}/2] labbazic.com 첫 로드 실패: {e}", flush=True)
            page.wait_for_timeout(5000)
    else:
        raise last_err
    cats = page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll('a'));
        const seen = new Set();
        return links.filter(a => /cateCd=/i.test(a.href || ''))
            .map(a => {
                const m = (a.href || '').match(/cateCd=(\\d+)/);
                return {
                    code: m ? m[1] : null,
                    label: (a.textContent || '').trim(),
                    href: a.href,
                };
            })
            .filter(c => c.code && c.label)
            .filter(c => {
                if (seen.has(c.code)) return false;
                seen.add(c.code);
                return true;
            });
    }""")
    return cats


def parse_results(page):
    """석림랩텍 검색 결과 페이지에서 상품 추출"""
    return page.evaluate(r"""() => {
        const products = [];
        // 상품명 a 태그가 가장 신뢰성 높음
        // 카드 패턴 추출
        const cards = document.querySelectorAll('.item, .goods, [class*=goods][class*=item], li.goods');

        // fallback: 제품 링크 (goods_view.php) 기준
        const allLinks = document.querySelectorAll('a[href*="goods_view.php"]');
        const grouped = new Map();
        for (const a of allLinks) {
            // 가장 가까운 카드 컨테이너
            let card = a.closest('li, .item, .goods-card, [class*=goods], div');
            if (!card || card === document.body) continue;
            // 같은 카드는 한 번만
            if (grouped.has(card)) continue;
            grouped.set(card, true);
            const text = card.innerText || '';
            const name = (a.textContent || '').trim();
            // 가격 추출
            const priceMatch = text.match(/(\d{1,3}(?:,\d{3})+)\s*원/);
            const img = card.querySelector('img');
            // goodsNo 추출
            const goodsM = (a.href || '').match(/goodsNo=(\d+)/);
            products.push({
                source_id: goodsM ? goodsM[1] : null,
                name: name.slice(0, 200),
                price: priceMatch ? parseInt(priceMatch[1].replace(/,/g, '')) : 0,
                img_src: img ? img.src : '',
                href: a.href,
                fulltext: text.slice(0, 300),
            });
        }
        return products.filter(p => p.source_id && p.name);
    }""")


def main():
    client = SupabaseClient()

    # sources에 sercrim 추가 (없을 때만)
    existing = client.select("sources", code="eq.sercrim")
    if not (isinstance(existing, list) and existing):
        client.insert("sources", {
            "code": "sercrim",
            "name_ko": "석림랩텍 (LABbazic)",
            "type": "crawl",
            "base_url": "https://www.labbazic.com",
            "is_authoritative": False,
            "requires_login": False,
            "crawl_delay_sec": 5,
        })
        print("sources에 sercrim 추가")

    # crawl_runs 시작
    run = client.insert("crawl_runs", {
        "source_code": "sercrim",
        "status": "running",
        "notes": "석림랩텍 카탈로그 (cateCd 트리)"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    inserted = 0
    updated = 0
    started = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()

        # 카테고리 추출
        cats = extract_categories(page)
        # CLI: 처리할 카테고리 수
        if len(sys.argv) > 1:
            try:
                cats = cats[:int(sys.argv[1])]
            except ValueError:
                pass
        print(f"카테고리: {len(cats)}개", flush=True)

        for i, cat in enumerate(cats, 1):
            try:
                # 카테고리 페이지 진입 — domcontentloaded + 45s (networkidle은 자주 막힘)
                url = f"https://www.labbazic.com/goods/goods_list.php?cateCd={cat['code']}"
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(2000)

                products = parse_results(page)

                cat_ins = 0
                cat_upd = 0
                wi_cat = map_to_wi(cat["label"])

                for prod in products:
                    if not prod.get("source_id") or not prod.get("name"):
                        continue
                    try:
                        # 기존 체크
                        existing_p = client.select("products", select="id",
                            **{
                                "source_code": "eq.sercrim",
                                "source_product_id": f"eq.{prod['source_id']}"
                            })
                        payload = {
                            "source_code": "sercrim",
                            "source_product_id": prod["source_id"],
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
                            "quality_score": 0.80,
                            "last_crawled_at": datetime.now(timezone.utc).isoformat(),
                        }
                        if isinstance(existing_p, list) and existing_p:
                            client.update("products", {"id": existing_p[0]["id"]}, payload)
                            cat_upd += 1
                        else:
                            client.insert("products", payload)
                            cat_ins += 1
                    except Exception as e:
                        pass

                inserted += cat_ins
                updated += cat_upd
                if cat_ins + cat_upd > 0 or i % 20 == 0:
                    elapsed = time.time() - started
                    eta = (elapsed / i) * (len(cats) - i) / 60
                    print(f"  [{i}/{len(cats)}] {cat['label'][:25]:<25} +{cat_ins} ~{cat_upd} (누적 {inserted+updated}, ETA {eta:.0f}분)", flush=True)
            except Exception as e:
                print(f"  [{i}] ERROR {cat['label']}: {e}", flush=True)

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
    print(f"소요: {(time.time()-started)/60:.1f}분")


if __name__ == "__main__":
    main()
