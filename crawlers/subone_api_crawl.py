# -*- coding: utf-8 -*-
"""
서브원 JSON API 직접 크롤러 (JACKPOT)
- /fo/co/main/select-main-category-list.do → 카테고리 트리
- /sa/disp/catg-best-prd-list.json → 카테고리별 베스트
- cateSearch.do?disp_ctg_no=C1000061 → 진짜 카테고리 코드로 검색
- 상품 상세 페이지 BFS → 관련상품 expand
"""
import os, sys, json, re, time, ctypes
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
DELAY = 1.5


def map_to_wi(label, name=""):
    text = (label + " " + name).lower()
    if re.search(r"의료|구급", text): return "M"
    if re.search(r"베어링|볼트|너트|체결", text): return "F"
    if re.search(r"실험|크린|측정|분석|계측|연구|화학물질|랩|시약", text): return "L"
    if re.search(r"청소|위생|와이퍼|걸레|쓰레기|세제", text): return "C"
    if re.search(r"안전|소방|방재|보호|마스크|글러브|장갑|솔루션|작업복|헬멧|보안경", text): return "S"
    if re.search(r"전선|전기|조명|전지|충전|배터리|반도체|콘센트|스위치|led|램프", text): return "E"
    if re.search(r"포장|박스|운반|하역|공구함|작업대|특가|사다리|선반|랙|결속", text): return "P"
    if re.search(r"공구|용접|연마|에어|절삭|배관|드릴|공작|렌치|드라이버|니퍼|커터", text): return "T"
    return "O"


def upsert_product(client, prod, label, seen_ids):
    """상품 1개 INSERT/UPDATE — 신규 시 1, 업데이트 시 0 반환"""
    pid = str(prod.get('source_id') or prod.get('prdId') or prod.get('prdIdView') or '')
    if not pid:
        return None, 0, 0
    pid = pid.lstrip('0') or pid  # 000000000003250963 → 3250963
    if pid in seen_ids:
        return pid, 0, 0
    seen_ids.add(pid)

    name = prod.get('name') or prod.get('prdNm') or ''
    if not name or len(name) < 2:
        return pid, 0, 0

    price = prod.get('price') or prod.get('prdPrc') or 0
    img = prod.get('img_src') or prod.get('prdImg') or ''
    href = prod.get('href') or f"https://store.serveone.co.kr/pr/pr-product-detail.do?prdId={pid}"
    mnfr = prod.get('mnfrNm') or ''
    wi_cat = map_to_wi(label, name)

    payload = {
        "source_code": "subone", "source_product_id": pid,
        "category_code": wi_cat, "sub_category": label[:100],
        "name_ko": name[:200],
        "manufacturer": mnfr[:100] if mnfr else None,
        "search_keywords": f"{name} {label} {mnfr}"[:500],
        "primary_image_url": img or None,
        "image_urls": [img] if img else [],
        "cost_price": price or None,
        "list_price": price or None,
        "margin_pct": 0, "currency": "KRW", "price_unit": "EA",
        "source_url": href,
        "is_directly_sold": False, "is_published": True, "quality_score": 0.85,
        "last_crawled_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        ex = client.select("products", select="id",
            **{"source_code": "eq.subone", "source_product_id": f"eq.{pid}"})
        if isinstance(ex, list) and ex:
            r = client.update("products", {"id": ex[0]["id"]}, payload)
            return pid, 0, 1
        else:
            r = client.insert("products", payload)
            if isinstance(r, list) and r:
                return pid, 1, 0
    except Exception:
        pass
    return pid, 0, 0


def extract_products_from_page(page):
    """카테고리/검색 페이지에서 상품 추출"""
    return page.evaluate(r"""() => {
        const seen = new Set(); const out = [];
        for (const a of document.querySelectorAll('a[href*="prdId="]')) {
            const m = (a.href || '').match(/prdId=([0-9]+)/);
            if (!m) continue;
            const pid = m[1].replace(/^0+/, '') || m[1];
            if (seen.has(pid)) continue;
            seen.add(pid);

            const card = a.closest('li, .item, .product, [class*=item], [class*=product], [class*=goods], div');
            if (!card) continue;
            const text = (card.innerText || '').trim();
            const priceMatch = text.match(/(\d{1,3}(?:,\d{3})+)\s*원/);
            const img = card.querySelector('img');
            let name = (a.textContent || '').trim();
            name = name.replace(/[\d,]+\s*원.*/, '').replace(/^\s*\d+\s*$/, '').trim();
            if (!name && img) name = img.alt || '';
            if (!name || name.length < 2) continue;

            out.push({
                source_id: pid, name: name.slice(0, 200),
                price: priceMatch ? parseInt(priceMatch[1].replace(/,/g, '')) : 0,
                img_src: img ? (img.src || img.dataset?.src || '') : '',
                href: a.href.startsWith('http') ? a.href : 'https://store.serveone.co.kr' + a.href,
            });
        }
        return out;
    }""")


def main():
    client = SupabaseClient()
    if not os.path.exists(COOKIE): print("쿠키 없음"); sys.exit(1)

    run = client.insert("crawl_runs", {
        "source_code": "subone", "status": "running",
        "notes": "JSON API + cateSearch.do(C1000061) + 상세 BFS"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    inserted = updated = 0
    started = time.time()

    # 기존 subone seen_ids
    seen_ids = set()
    offset = 0
    while True:
        r = client._request("GET", "/products",
            params={"source_code":"eq.subone","select":"source_product_id",
                    "offset":offset,"limit":1000})
        if not isinstance(r, list) or not r: break
        seen_ids.update((x["source_product_id"] or '').lstrip('0') or x["source_product_id"]
                        for x in r if x.get("source_product_id"))
        if len(r) < 1000: break
        offset += 1000
    print(f"기존 subone seen: {len(seen_ids)}건", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        # 메인 페이지 진입 (세션 유지)
        page.goto("https://store.serveone.co.kr/ssp/main/index.do",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(3000)

        # === [1] JSON API: 카테고리 트리 받기 ===
        print("\n[1] JSON API → 카테고리 트리", flush=True)
        cat_tree_raw = page.evaluate(r"""async () => {
            const r = await fetch('/fo/co/main/select-main-category-list.do', {
                method: 'POST',
                headers: {'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','Accept':'application/json'},
                body: '{}',
            });
            return await r.json();
        }""")
        main_cats = (cat_tree_raw.get('model') or {}).get('mainCategoryList') or []
        print(f"  메인 카테고리 트리: {len(main_cats)}개")

        # 카테고리 코드 수집 (prdClcd, MAIN_URL 등)
        category_codes = []
        sample_keys = set()
        for c in main_cats[:5]:
            for k in c.keys():
                sample_keys.add(k)
        print(f"  샘플 키: {sorted(sample_keys)[:20]}")

        # MAIN_URL 추출 (직접 URL이 있는 경우)
        main_urls = []
        for c in main_cats:
            for k in c.keys():
                v = c.get(k)
                if isinstance(v, str) and 'prdId=' in v:
                    main_urls.append((c.get('TTL', '') or c.get('PRD_CLSF_NM_3', '') or '', v))

        print(f"  직접 상품 URL: {len(main_urls)}개")

        # === [2] catg-best-prd-list.json 으로 mainPrdExpsPstId 1~30 시도 ===
        print("\n[2] catg-best-prd-list.json (mainPrdExpsPstId 20001~20050)", flush=True)
        api_total_added = 0
        for pst_id in range(20001, 20051):
            try:
                resp = page.evaluate(rf"""async () => {{
                    const r = await fetch('/sa/disp/catg-best-prd-list.json', {{
                        method: 'POST',
                        headers: {{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest','Accept':'application/json'}},
                        body: JSON.stringify({{coCd:"1000",chnTpCd:"P",mallSprCd:"10",mainPrdExpsPstId:{pst_id}}}),
                    }});
                    if (!r.ok) return null;
                    return await r.json();
                }}""")
                if not resp: continue
                prods = resp.get('catgBestPrdList') or []
                if not prods: continue
                added_here = 0
                for prod in prods:
                    label = prod.get('prdClsfNm') or prod.get('mnfrNm') or f'PstId-{pst_id}'
                    pid, ins, upd = upsert_product(client, prod, label, seen_ids)
                    inserted += ins; updated += upd; added_here += ins
                if added_here > 0:
                    print(f"  pstId={pst_id} +{added_here} (총 {len(prods)}건) | 누적 {inserted+updated}", flush=True)
                api_total_added += added_here
            except Exception as e:
                pass
            time.sleep(0.2)
        print(f"  → API로 신규 {api_total_added}건", flush=True)

        # === [3] cateSearch.do — main_cats에서 발견된 진짜 카테고리 코드만 ===
        # (이전: brute force로 99999개 후보 × 3 ftDepth × 20 page = 38시간 → 매번 timeout
        #  → 발견된 코드만, ftDepth=1만, page 1~3만, 카테고리당 60초 예산)
        print("\n[3] cateSearch.do — discovered 카테고리만 (효율화)", flush=True)
        discovered_codes = set()
        for c in main_cats:
            for k in c.keys():
                v = c.get(k)
                if isinstance(v, str) and re.match(r'^C\d{6,8}$', v):
                    discovered_codes.add(v)
        print(f"  메인 트리에서 발견된 카테고리 코드: {len(discovered_codes)}개")

        # 시간 예산: subone 전체 budget = 100분 (180분 timeout 안에 끝나도록 안전 마진)
        BUDGET_PHASE3_SEC = 60 * 60   # 60분
        BUDGET_PER_CAT_SEC = 60       # 카테고리 당 1분
        BUDGET_PHASE4_SEC = 30 * 60   # 30분 (BFS 단계)
        phase3_start = time.time()
        cat_count = 0
        for code in sorted(discovered_codes):
            if time.time() - phase3_start > BUDGET_PHASE3_SEC:
                print(f"  ! Phase 3 예산({BUDGET_PHASE3_SEC//60}분) 초과 → 종료, 남은 {len(discovered_codes)-cat_count}개 카테고리 스킵", flush=True)
                break
            cat_count += 1
            cat_start = time.time()
            url = (f"https://store.serveone.co.kr/ssp/search/cateSearch.do"
                   f"?sort=RANK/DESC&disp_ctg_no={code}&ftDepth=1")
            cat_added = 0
            try:
                for pn in range(1, 4):  # 처음 3페이지만
                    if time.time() - cat_start > BUDGET_PER_CAT_SEC:
                        break
                    target = url + (f"&page={pn}" if pn > 1 else "")
                    page.goto(target, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(1200)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(500)
                    products = extract_products_from_page(page)
                    if not products:
                        break
                    new_in_page = 0
                    for prod in products:
                        pid, ins, upd = upsert_product(client, prod, code, seen_ids)
                        inserted += ins; updated += upd
                        if ins:
                            new_in_page += 1
                            cat_added += 1
                    if new_in_page == 0:
                        break  # 신규 없으면 다음 카테고리
            except Exception:
                pass
            if cat_added > 0:
                elapsed = time.time() - started
                print(f"  [{cat_count}/{len(discovered_codes)}] {code} +{cat_added} | 누적 {inserted+updated} | 경과 {elapsed/60:.1f}m", flush=True)
            time.sleep(DELAY)

        # === [4] 상세 페이지 BFS — 시간 남으면 ===
        # 어차피 매일 도는 cycle이라 일부만 처리해도 점진 누적
        budget_left = BUDGET_PHASE4_SEC - max(0, (time.time() - phase3_start) - BUDGET_PHASE3_SEC)
        if budget_left < 60:
            print(f"\n[4] BFS 스킵 (남은 예산 {budget_left:.0f}s)", flush=True)
        else:
            print(f"\n[4] 상세 페이지 BFS — 시간 예산 {budget_left/60:.0f}분", flush=True)
            phase4_start = time.time()
            # 매일 처음 500개만 (전체 12K+ 라 25일이면 한 사이클 — 충분히 fresh)
            bfs_queue = list(seen_ids)[:500]
            bfs_added = 0
            for i, pid in enumerate(bfs_queue, 1):
                if time.time() - phase4_start > budget_left:
                    print(f"  ! BFS 예산 초과 → 중단 ({i}/{len(bfs_queue)} 처리)", flush=True)
                    break
                try:
                    url = f"https://store.serveone.co.kr/pr/pr-product-detail.do?prdId={pid}"
                    page.goto(url, wait_until="domcontentloaded", timeout=12000)
                    page.wait_for_timeout(800)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(400)
                    products = extract_products_from_page(page)
                    page_added = 0
                    for prod in products:
                        if prod['source_id'] == pid:
                            continue
                        _, ins, upd = upsert_product(client, prod, "관련상품", seen_ids)
                        inserted += ins; updated += upd
                        if ins:
                            page_added += 1
                    if page_added > 0:
                        bfs_added += page_added
                    if i % 50 == 0:
                        elapsed = time.time() - phase4_start
                        eta = (elapsed/i) * (len(bfs_queue)-i) / 60
                        print(f"  BFS [{i}/{len(bfs_queue)}] | +{bfs_added} | 누적 {inserted+updated} | ETA {eta:.0f}m", flush=True)
                except Exception:
                    pass
                time.sleep(0.3)

        browser.close()

    if run_id:
        client.update("crawl_runs", {"id":run_id}, {
            "status":"success",
            "finished_at":datetime.now(timezone.utc).isoformat(),
            "products_added":inserted, "products_updated":updated,
        })
    print(f"\n=== 완료 === 신규 {inserted}, 업데이트 {updated}, 소요 {(time.time()-started)/60:.1f}분")


if __name__ == "__main__":
    main()
