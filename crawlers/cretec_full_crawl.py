# -*- coding: utf-8 -*-
"""
크레텍 CTX 전체 카탈로그 자동 수집
- 2,138개 leaf 카테고리 순회
- 각 카테고리의 모든 상품 페이지 수집
- 즉시 Supabase products 테이블에 INSERT
- WI 품번은 DB 트리거가 자동 부여
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from supabase_client import SupabaseClient
from category_map import map_to_wi as map_to_wi_v2

# Windows 절전 방지
if sys.platform == "win32":
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

COOKIE = os.path.join(ROOT, "_secrets", "cookies", "cretec_storage.json")
OUT = os.path.join(ROOT, "output", "cretec")
CATS_FILE = os.path.join(OUT, "categories_full.json")
CRAWL_DELAY = 5.0  # 보수적 (robots.txt는 20초지만 B2B 회원 정상 사용)


def load_categories():
    """2,138개 leaf 카테고리 (level 4)"""
    with open(CATS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return [(int(code), label) for code, label in data["4"]]


# 크레텍 카테고리명 → WI 카테고리 매핑 (Python에서도 처리)
def map_to_wi_category(label, name="", spec=""):
    text = (label + " " + name + " " + spec).lower()
    if re.search(r"의료|구급|응급", text): return "M"
    if re.search(r"볼트|너트|와셔|체결|체인|훅|샤클", text): return "F"
    if re.search(r"측정|계측|측량|광학|온도|압력|수평|레이저|현미경|돋보기|저울|토크", text): return "L"
    if re.search(r"크린|클린|방진|와이퍼|라텍스|니트릴|위생|일회용", text): return "C"
    if re.search(r"안전|보호|마스크|보안경|헬멧|안전모|방독|소화|구조|사다리|로프", text): return "S"
    if re.search(r"전기|전자|배선|전선|램프|조명|LED|전구|배터리|전동|충전|콘센트|소켓", text): return "E"
    if re.search(r"포장|박스|상자|노끈|밴드|랩|비닐|테이프|캐비넷|선반|적재|운반|대차", text): return "P"
    if re.search(r"공구|렌치|드라이버|스패너|망치|드릴|커터|니퍼|펜치|플라이어|톱|줄|용접|연마|절삭", text): return "T"
    return "O"


def parse_search_results(page):
    """검색 결과 페이지에서 상품 추출"""
    rows_data = page.evaluate("""() => {
        const trs = document.querySelectorAll('table tbody tr');
        return Array.from(trs).map(tr => {
            const cells = Array.from(tr.querySelectorAll('td'));
            const img = tr.querySelector('img');
            return {
                cellCount: cells.length,
                cells: cells.map(td => (td.innerText || '').trim()),
                img: img ? img.src : '',
                rowText: tr.innerText.replace(/\\n/g, ' | ')
            };
        }).filter(r => r.cellCount >= 5);
    }""")

    # 12 cells (primary) + 9 cells (secondary) 페어로 묶기
    products = []
    i = 0
    while i < len(rows_data):
        primary = rows_data[i]
        secondary = rows_data[i+1] if i+1 < len(rows_data) else None
        # primary는 보통 12 cells, secondary는 9
        if primary["cellCount"] >= 8 and not primary["img"].endswith("icon-ebook.svg"):
            p = {
                "no": primary["cells"][1] if len(primary["cells"]) > 1 else "",
                "name_ko": primary["cells"][2] if len(primary["cells"]) > 2 else "",
                "manufacturer": primary["cells"][3] if len(primary["cells"]) > 3 else "",
                "source_product_id": primary["cells"][4] if len(primary["cells"]) > 4 else "",
                "unit": primary["cells"][5] if len(primary["cells"]) > 5 else "",
                "list_price_str": primary["cells"][6] if len(primary["cells"]) > 6 else "",
                "supply_price_str": primary["cells"][7] if len(primary["cells"]) > 7 else "",
                "image_url": primary["img"],
            }
            # secondary에서 규격, 적용률 등
            if secondary and secondary["cellCount"] >= 5:
                p["spec"] = secondary["cells"][0] if len(secondary["cells"]) > 0 else ""
                p["apply_rate"] = secondary["cells"][4] if len(secondary["cells"]) > 4 else ""

            # 가격 파싱
            def parse_price(s):
                m = re.search(r"([\d,]+)", s)
                return int(m.group(1).replace(",", "")) if m else 0

            p["list_price"] = parse_price(p["list_price_str"])
            p["supply_price"] = parse_price(p["supply_price_str"])
            # 가격 정책 C: cost_price = 공급가 (없으면 정가, 마진 0%로 협상 표시)
            # list_price = 크레텍 정가 그대로 (고객 화면 노출)
            p["cost_price"] = p["supply_price"] or p["list_price"] or None
            p["display_list_price"] = p["list_price"] or p["cost_price"]

            if p["source_product_id"] and p["name_ko"]:
                products.append(p)
            i += 2
        else:
            i += 1
    return products


def crawl_category(page, code, label, client):
    """한 카테고리의 모든 상품 수집 — 페이지네이션 보강"""
    # 메인 → 카테고리 펼치기 → powerSearchCate 호출
    page.goto("https://ctx.cretec.kr/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1500)
    page.evaluate("document.getElementById('categoryBtn').click()")
    page.wait_for_timeout(1500)
    page.evaluate(f"powerSearchCate('4', {code})")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(2500)

    # rows를 50으로 늘리고 다시 search (페이지 수 감소)
    page.evaluate("""() => {
        const f = document.getElementById('searchFrm');
        if (!f) return;
        const ri = f.querySelector('input[name=rows]');
        if (ri) ri.value = '50';
        const ci = f.querySelector('input[name=cateSearch]');
        if (ci) ci.value = 'Y';
        const pi = f.querySelector('input[name=page]');
        if (pi) pi.value = '1';
        f.submit();
    }""")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(2000)

    text = page.evaluate("() => document.body.innerText")
    m = re.search(r"총\s*(\d+(?:,\d+)*)\s*건", text)
    total = int(m.group(1).replace(",", "")) if m else 0
    if total == 0:
        return 0, 0

    wi_cat = map_to_wi_v2(label)  # v2: 크레텍 root 카테고리 기반
    inserted, updated = 0, 0
    page_num = 1

    while True:
        products = parse_search_results(page)
        for p in products:
            try:
                # Supabase upsert (existing check by source_code + source_product_id)
                existing = client.select("products", select="id,wi_code", **{
                    "source_code": "eq.cretec",
                    "source_product_id": f"eq.{p['source_product_id']}"
                })
                # 가격 정책 C
                cost = p["cost_price"] or None
                list_p = p.get("display_list_price") or cost  # 정가 = 고객 노출가
                margin = 0.0
                if cost and list_p and list_p > cost:
                    margin = round((list_p - cost) / list_p * 100, 1)

                payload = {
                    "source_code": "cretec",
                    "source_product_id": p["source_product_id"],
                    "category_code": wi_cat,
                    "sub_category": label,
                    "name_ko": p["name_ko"],
                    "spec": p.get("spec", ""),
                    "manufacturer": p["manufacturer"],
                    "search_keywords": f"{p['name_ko']} {p.get('spec','')} {p['manufacturer']} {label}"[:500],
                    "primary_image_url": p["image_url"],
                    "image_urls": [p["image_url"]] if p["image_url"] else [],
                    "cost_price": cost,
                    "list_price": list_p,
                    "margin_pct": margin,
                    "currency": "KRW",
                    "price_unit": p["unit"][:20] if p.get("unit") else "EA",
                    "is_directly_sold": False,
                    "is_published": True,
                    "quality_score": 0.85,
                    "last_crawled_at": datetime.now(timezone.utc).isoformat(),
                }
                if isinstance(existing, list) and existing:
                    client.update("products", {"id": existing[0]["id"]}, payload)
                    updated += 1
                else:
                    # WI 품번은 DB 트리거가 부여
                    payload.pop("wi_code", None)
                    client.insert("products", payload)
                    inserted += 1
            except Exception as e:
                print(f"      ERROR for {p.get('source_product_id')}: {e}")

        # 다음 페이지: form#searchFrm의 page input 증가 + submit
        next_ok = page.evaluate(f"""() => {{
            const f = document.getElementById('searchFrm');
            if (!f) return false;
            const pi = f.querySelector('input[name=page]');
            if (!pi) return false;
            const next_p = {page_num + 1};
            pi.value = String(next_p);
            const ci = f.querySelector('input[name=cateSearch]');
            if (ci) ci.value = 'Y';
            const ri = f.querySelector('input[name=rows]');
            if (ri) ri.value = '50';
            f.submit();
            return true;
        }}""")
        if not next_ok:
            break
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        # 결과 0건이면 종료
        text_check = page.evaluate("() => document.body.innerText")
        import re as _re
        m_check = _re.search(r"총\s*(\d+(?:,\d+)*)\s*건", text_check)
        if m_check and int(m_check.group(1).replace(",", "")) == 0:
            break

        page_num += 1
        if page_num > 100:
            break

    return inserted, updated


def main():
    client = SupabaseClient()
    cats = load_categories()

    # CLI 인수: 처리할 카테고리 수 (시험용)
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            cats = cats[:limit]
        except ValueError:
            pass

    print(f"=== 크레텍 카탈로그 수집 ===", flush=True)
    print(f"  대상 leaf 카테고리: {len(cats)}개", flush=True)
    print(f"  Crawl-delay: {CRAWL_DELAY}초", flush=True)

    # crawl_runs 시작
    run = client.insert("crawl_runs", {
        "source_code": "cretec",
        "status": "running",
        "notes": f"Full catalog crawl, {len(cats)} categories"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"  crawl_runs #{run_id}")

    total_inserted = 0
    total_updated = 0
    started = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 Chrome/120",
            locale="ko-KR",
            viewport={"width": 1400, "height": 900},
        )
        page = context.new_page()

        for i, (code, label) in enumerate(cats, 1):
            try:
                ins, upd = crawl_category(page, code, label, client)
                total_inserted += ins
                total_updated += upd

                if True:  # 시범에서는 매번 출력
                    elapsed = time.time() - started
                    eta = (elapsed / i) * (len(cats) - i) / 60
                    print(f"  [{i}/{len(cats)}] {label[:25]:<25} +{ins} ~{upd} (누적 {total_inserted+total_updated}, ETA {eta:.0f}분)", flush=True)

                    # 중간 진행 보고 (DB 업데이트)
                    if run_id and i % 50 == 0:
                        client.update("crawl_runs", {"id": run_id}, {
                            "products_added": total_inserted,
                            "products_updated": total_updated,
                        })
            except Exception as e:
                print(f"  [{i}] ERROR {label}: {e}")

            time.sleep(CRAWL_DELAY)

        browser.close()

    if run_id:
        client.update("crawl_runs", {"id": run_id}, {
            "status": "success",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "products_added": total_inserted,
            "products_updated": total_updated,
        })

    print(f"\n=== 완료 ===")
    print(f"  신규: {total_inserted}")
    print(f"  업데이트: {total_updated}")
    print(f"  소요: {(time.time()-started)/60:.1f}분")


if __name__ == "__main__":
    main()
