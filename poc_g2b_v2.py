# -*- coding: utf-8 -*-
"""조달청 API — 키는 raw 형태로, 다른 파라미터만 인코딩"""
import json
import urllib.request
import urllib.parse
from datetime import date, timedelta

KEY = "566c0b28e67182926927e9beba5ab7ed14d7434902f21341826bb138e386865b"
BASE = "https://apis.data.go.kr/1230000/at/ShoppingMallPrdctInfoService"


def call(path, params):
    """키는 raw로 직접 URL에 붙이고, 나머지만 urlencode"""
    p = {"type": "json"}
    p.update(params)
    qs = urllib.parse.urlencode(p, encoding="utf-8")
    url = f"{BASE}{path}?serviceKey={KEY}&{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "WI-PriceIntel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}", "_body": e.read().decode("utf-8")[:300]}
    except Exception as e:
        return {"_error": str(e)}


end = date.today() - timedelta(days=1)
start = end - timedelta(days=90)  # 3개월
ds, de = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")

print(f"기간: {ds} ~ {de}\n")

# 다양한 파라미터 시험
tests = [
    ("일자단일 - 어제",                {"numOfRows": 5, "pageNo": 1, "inqryBgnDt": de, "inqryEndDt": de}),
    ("3개월 범위",                    {"numOfRows": 5, "pageNo": 1, "inqryBgnDt": ds, "inqryEndDt": de}),
    ("3개월 + 한글 키워드 (장갑)",     {"numOfRows": 5, "pageNo": 1, "inqryBgnDt": ds, "inqryEndDt": de, "prdctIdntNoNm": "장갑"}),
    ("3개월 + 분류 (안전)",          {"numOfRows": 5, "pageNo": 1, "inqryBgnDt": ds, "inqryEndDt": de, "prdctClsfcNoNm": "안전"}),
]

for name, params in tests:
    print(f">>> {name}")
    r = call("/getMASCntrctPrdctInfoList", params)
    if "_error" in r:
        print(f"   ❌ {r['_error']}: {r.get('_body', '')[:150]}")
        print()
        continue
    body = r.get("response", {}).get("body", {})
    total = body.get("totalCount", 0)
    items = body.get("items", [])
    print(f"   ✅ 총 {total}건")
    if items and isinstance(items, list):
        item = items[0]
        print(f"   필드 ({len(item)}개): {list(item.keys())}")
        # 가격 + 이름
        for k, v in list(item.items())[:15]:
            print(f"     {k}: {v}")
    print()
