# -*- coding: utf-8 -*-
"""
서브원 검색 키워드 brute force 크롤러
- /ssp/search/cateSearch.do?disp_ctg_no=C05&searchKeyword=X
- 키워드 200개 자동 순회
- 밤새 돌리기 용
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
COOKIE = os.path.join(ROOT, "_secrets", "cookies", "serveone_storage.json")
CRAWL_DELAY = 1.5

# 200+ 산업재 키워드 (MRO 메인 카테고리 망라)
KEYWORDS = [
    # 안전/보호
    "안전모", "안전화", "안전화끈", "보안경", "고글", "방진마스크", "방독마스크", "마스크", "헬멧",
    "장갑", "코팅장갑", "내열장갑", "내화학장갑", "절단장갑", "용접장갑", "라텍스장갑", "니트릴장갑", "면장갑",
    "안전벨트", "안전로프", "추락방지", "안전띠", "안전화끈", "안전등", "구명조끼", "방한복", "작업복", "방진복",
    "귀마개", "귀덮개", "방한모", "토시", "각반", "보호의", "방화복",
    # 공구
    "스패너", "렌치", "복스알", "드라이버", "토크렌치", "L렌치", "복스셋", "스탠리",
    "니퍼", "플라이어", "롱노즈", "콤비네이션", "워터펌프", "롱로즈", "커터", "가위", "줄칼",
    "드릴", "임팩드릴", "전동드릴", "햄머드릴", "충전드릴", "드릴비트", "엔드밀",
    "그라인더", "샌더", "디스크그라인더", "벨트샌더", "직쏘", "원형톱", "지그쏘", "커팅소",
    "용접기", "용접봉", "용접마스크", "TIG용접", "MIG용접", "이산화용접",
    # 측정
    "버니어캘리퍼스", "마이크로미터", "다이얼게이지", "수평계", "줄자", "자", "직각자",
    "온도계", "압력계", "토크게이지", "타코미터", "테스터", "멀티미터", "오실로스코프",
    "현미경", "돋보기", "저울", "전자저울", "체적계",
    # 전기/조명
    "전선", "케이블", "케이블타이", "전원선", "릴선", "AC어댑터", "DC어댑터",
    "LED", "형광등", "전구", "할로겐", "랜턴", "후레쉬", "투광등", "비상등",
    "콘센트", "멀티탭", "스위치", "차단기", "릴레이", "솔레노이드",
    "배터리", "건전지", "충전기", "AA", "AAA",
    # 베어링/체결
    "베어링", "볼베어링", "스러스트", "리니어가이드", "샤프트", "커플링",
    "볼트", "너트", "와셔", "스프링와셔", "M3", "M4", "M5", "M6", "M8", "M10",
    "체인", "벨트", "기어", "스프로켓", "풀리",
    # 포장/물류
    "박스", "골판지", "에어캡", "뽁뽁이", "스트레치필름", "포장테이프", "박스테이프",
    "결속끈", "노끈", "PP밴드", "마대", "포대", "카트", "대차", "사다리",
    "선반", "랙", "팔레트", "지게차포크",
    # 청소/위생
    "와이퍼", "마대걸레", "청소기", "진공청소기", "쓰레기통", "휴지", "롤휴지",
    "세제", "세정제", "탈취제", "방향제", "왁스",
    # 화학/연구
    "화학물질", "솔벤트", "신너", "WD-40", "윤활유", "그리스", "구리스",
    "절삭유", "방청유", "에폭시", "본드", "실리콘", "글루건",
    "비커", "플라스크", "시린지", "피펫", "여과지", "샘플병",
    # 사무/기타
    "테이프", "스카치", "포스트잇", "라벨지", "카드포켓",
    "기계", "모터", "펌프", "압축기", "에어컴프레서", "송풍기", "팬",
    "히터", "발열체", "온도조절", "센서", "PLC",
    "공구함", "공구가방", "공구박스", "장비함",
]

def map_to_wi(kw):
    text = kw.lower()
    if re.search(r"의료|구급", text): return "M"
    if re.search(r"베어링|볼트|너트|체결|와셔", text): return "F"
    if re.search(r"실험|크린|측정|분석|계측|마이크|버니어|온도|압력|저울|현미경|비커|플라스크", text): return "L"
    if re.search(r"청소|위생|와이퍼|걸레|쓰레기|휴지|세제", text): return "C"
    if re.search(r"안전|소방|방재|보호|마스크|글러브|장갑|헬멧|보안경|로프|벨트|작업복|방진복|토시|각반|귀마개", text): return "S"
    if re.search(r"전선|전기|조명|전지|충전|배터리|콘센트|스위치|led|형광|전구|랜턴", text): return "E"
    if re.search(r"포장|박스|운반|하역|공구함|작업대|사다리|선반|랙|에어캡", text): return "P"
    if re.search(r"공구|용접|연마|에어|절삭|배관|드릴|스패너|렌치|드라이버|니퍼|플라이어|커터|그라인더|샌더|톱", text): return "T"
    return "O"


def extract_products(page):
    return page.evaluate(r"""() => {
        const seen = new Set(); const out = [];
        for (const a of document.querySelectorAll('a[href*="prdId="]')) {
            const m = (a.href || '').match(/prdId=([0-9]+)/);
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
    if not os.path.exists(COOKIE):
        print("쿠키 없음"); sys.exit(1)

    run = client.insert("crawl_runs", {
        "source_code": "subone", "status": "running",
        "notes": f"키워드 brute force ({len(KEYWORDS)}개)"
    })
    run_id = run[0]["id"] if isinstance(run, list) and run else None
    print(f"crawl_runs #{run_id}", flush=True)

    inserted = updated = 0
    started = time.time()

    # 기존 subone source_id 메모리 적재
    seen_ids = set()
    offset = 0
    while True:
        r = client._request("GET", "/products",
            params={"source_code": "eq.subone", "select": "source_product_id",
                    "offset": offset, "limit": 1000})
        if not isinstance(r, list) or not r: break
        seen_ids.update(x["source_product_id"] for x in r if x.get("source_product_id"))
        if len(r) < 1000: break
        offset += 1000
    print(f"기존 subone: {len(seen_ids)}건", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=COOKIE,
            user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120",
            locale="ko-KR", viewport={"width":1400,"height":900},
        )
        page = context.new_page()

        for ki, kw in enumerate(KEYWORDS, 1):
            url = f"https://store.serveone.co.kr/ssp/search/cateSearch.do?searchKeyword={kw}&ftDepth=1"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                # 무한스크롤 5회
                for _ in range(8):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(700)
                products = extract_products(page)

                wi_cat = map_to_wi(kw)
                kw_ins, kw_upd = 0, 0
                for prod in products:
                    if prod["source_id"] in seen_ids: continue
                    seen_ids.add(prod["source_id"])
                    try:
                        ex = client.select("products", select="id",
                            **{"source_code":"eq.subone", "source_product_id":f"eq.{prod['source_id']}"})
                        payload = {
                            "source_code":"subone", "source_product_id":prod["source_id"],
                            "category_code":wi_cat, "sub_category":kw[:100],
                            "name_ko":prod["name"],
                            "search_keywords":f"{prod['name']} {kw}"[:500],
                            "primary_image_url":prod.get("img_src") or None,
                            "image_urls":[prod["img_src"]] if prod.get("img_src") else [],
                            "cost_price":prod.get("price") or None,
                            "list_price":prod.get("price") or None,
                            "margin_pct":0, "currency":"KRW", "price_unit":"EA",
                            "source_url":prod.get("href"),
                            "is_directly_sold":False, "is_published":True, "quality_score":0.85,
                            "last_crawled_at":datetime.now(timezone.utc).isoformat(),
                        }
                        if isinstance(ex, list) and ex:
                            r = client.update("products", {"id":ex[0]["id"]}, payload)
                            kw_upd += 1
                        else:
                            r = client.insert("products", payload)
                            if isinstance(r, list) and r: kw_ins += 1
                    except Exception:
                        pass
                inserted += kw_ins; updated += kw_upd
                if kw_ins + kw_upd > 0 or ki % 10 == 0:
                    elapsed = time.time() - started
                    eta = (elapsed/ki) * (len(KEYWORDS)-ki) / 60
                    print(f"  [{ki}/{len(KEYWORDS)}] '{kw[:15]:<15}' +{kw_ins} ~{kw_upd} | total {inserted+updated} ({len(seen_ids)} unique) | ETA {eta:.0f}m", flush=True)
            except Exception as e:
                print(f"  [{ki}] ERR '{kw}': {str(e)[:60]}", flush=True)
            time.sleep(CRAWL_DELAY)

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
