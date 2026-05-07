# -*- coding: utf-8 -*-
"""조달청 API 검색 파라미터 시험 — 일반적인 조달청 패턴으로 시도"""
import json
import urllib.request
import urllib.parse
from datetime import date, timedelta

KEY = "566c0b28e67182926927e9beba5ab7ed14d7434902f21341826bb138e386865b"
BASE = "https://apis.data.go.kr/1230000/at/ShoppingMallPrdctInfoService"


def call(path, params):
    p = {"serviceKey": KEY, "type": "json"}
    p.update(params)
    qs = urllib.parse.urlencode(p, safe="-_.~")
    url = f"{BASE}{path}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "WI-PriceIntel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}", "_body": e.read().decode("utf-8")[:300]}
    except Exception as e:
        return {"_error": str(e)}


# 어제 ~ 한 달 전 범위로 조회 (등록일자 기준)
end = date.today() - timedelta(days=1)
start = end - timedelta(days=30)
date_str_start = start.strftime("%Y%m%d")
date_str_end = end.strftime("%Y%m%d")

print("=" * 70)
print(f"검색 파라미터 시험 ({start} ~ {end})")
print("=" * 70)

# 시험 1: 다수공급자계약 — 등록일자 기간 조회 (일반적 파라미터명)
test_param_sets = [
    ("등록일자 (rgstDt)", {
        "numOfRows": 5, "pageNo": 1,
        "rgstDt": date_str_end,  # 단일 날짜
    }),
    ("조회기간 (inqryBgnDt/inqryEndDt)", {
        "numOfRows": 5, "pageNo": 1,
        "inqryBgnDt": date_str_start,
        "inqryEndDt": date_str_end,
    }),
    ("기간 + 분류 (안전)", {
        "numOfRows": 5, "pageNo": 1,
        "inqryBgnDt": date_str_start,
        "inqryEndDt": date_str_end,
        "prdctClsfcNoNm": "안전",
    }),
    ("기간 + 분류 (장갑)", {
        "numOfRows": 5, "pageNo": 1,
        "inqryBgnDt": date_str_start,
        "inqryEndDt": date_str_end,
        "prdctIdntNoNm": "장갑",
    }),
]

for name, params in test_param_sets:
    print(f"\n>>> {name}")
    r = call("/getMASCntrctPrdctInfoList", params)
    if "_error" in r:
        print(f"   ❌ {r['_error']}")
        if "_body" in r:
            print(f"   {r['_body']}")
        continue
    body = r.get("response", {}).get("body", {})
    total = body.get("totalCount", 0)
    items = body.get("items", [])
    print(f"   결과: {total}건")
    if items and isinstance(items, list):
        item = items[0] if items else None
        if item:
            keys = list(item.keys())
            print(f"   필드 ({len(keys)}개): {keys[:10]}")
            # 가격·이름 관련 필드
            interesting = [k for k in keys if any(p in k.lower() for p in
                ["amt","prc","price","prdct","품명","단가","name"])]
            if interesting:
                print(f"   주요 필드: {interesting}")
                for k in interesting[:5]:
                    print(f"     - {k}: {item[k]}")
