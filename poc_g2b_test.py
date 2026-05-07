# -*- coding: utf-8 -*-
"""
조달청 종합쇼핑몰 API 연결 테스트
- 9개 endpoint 모두 호출해서 응답 형식 + 데이터 샘플 확인
- 핵심: 어떤 endpoint가 우리 100 SKU 매칭에 가장 유용한지 식별
"""
import os
import json
import urllib.request
import urllib.parse

ENV = r"C:\Wholesale Industry\AI Assistant\MRO\PriceIntel\_secrets\.env"


def load_env():
    env = {}
    with open(ENV, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


env = load_env()
KEY = env["G2B_SERVICE_KEY"]
BASE = env["G2B_ENDPOINT"]

# 9개 endpoint
ENDPOINTS = [
    ("MAS 다수공급자계약",       "/getMASCntrctPrdctInfoList"),
    ("일반단가계약",            "/getUcntrctPrdctInfoList"),
    ("제3자단가계약",           "/getThptyUcntrctPrdctInfoList"),
    ("납품요구정보 현황",        "/getDlvrReqInfoList"),
    ("납품요구상세 현황",        "/getDlvrReqDtlInfoList"),
    ("종합쇼핑몰 품목등록",      "/getShoppingMallPrdctInfoList"),
    ("벤처나라 주문거래",        "/getVntrPrdctOrderDealDtlsInfoList"),
    ("특정품목조달내역",         "/getSpcifyPrdlstPrcureInfoList"),
    ("특정품목조달집계",         "/getSpcifyPrdlstPrcureTotList"),
]


def call(path, params=None):
    p = {"serviceKey": KEY, "numOfRows": 3, "pageNo": 1, "type": "json"}
    if params:
        p.update(params)
    qs = urllib.parse.urlencode(p, safe="-_.~")
    url = f"{BASE}{path}?{qs}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"_raw": raw[:500]}
    except Exception as e:
        return {"error": str(e)}


print("=" * 70)
print("조달청 종합쇼핑몰 API — 9개 Endpoint 테스트")
print("=" * 70)

for name, path in ENDPOINTS:
    print(f"\n>>> {name} ({path})")
    r = call(path)
    if "error" in r:
        print(f"   ❌ {r['error']}")
        continue
    if "_raw" in r:
        print(f"   📄 (XML) {r['_raw'][:200]}...")
        continue
    # JSON 응답 분석
    body = r.get("response", {}).get("body", {})
    header = r.get("response", {}).get("header", {})
    code = header.get("resultCode")
    msg = header.get("resultMsg")
    total = body.get("totalCount")
    items_raw = body.get("items", [])
    print(f"   결과: {code} / {msg} / 총 {total}건")
    if isinstance(items_raw, list) and items_raw:
        item = items_raw[0]
        print(f"   필드: {list(item.keys())[:8]}...")
        # 가격 관련 필드 hunt
        price_fields = [k for k in item.keys() if any(p in k.lower() for p in ["amt", "prc", "price", "단가", "금액"])]
        if price_fields:
            print(f"   💰 가격 필드: {price_fields}")
        # 샘플 데이터 일부
        sample = {k: item[k] for k in list(item.keys())[:5]}
        print(f"   샘플: {sample}")
    elif isinstance(items_raw, dict) and items_raw.get("item"):
        item = items_raw["item"]
        if isinstance(item, list) and item:
            item = item[0]
        print(f"   필드: {list(item.keys())[:8]}...")
        price_fields = [k for k in item.keys() if any(p in k.lower() for p in ["amt", "prc", "price"])]
        if price_fields:
            print(f"   💰 가격 필드: {price_fields}")
        sample = {k: item[k] for k in list(item.keys())[:5]}
        print(f"   샘플: {sample}")
    else:
        print(f"   ⚠ 결과 비어있음")
