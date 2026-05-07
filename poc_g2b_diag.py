# -*- coding: utf-8 -*-
"""조달청 API 인증키 진단 — 4가지 형태 모두 시도"""
import urllib.request
import urllib.parse
import time

KEY = "566c0b28e67182926927e9beba5ab7ed14d7434902f21341826bb138e386865b"
BASE = "https://apis.data.go.kr/1230000/at/ShoppingMallPrdctInfoService"
PATH = "/getMASCntrctPrdctInfoList"

# 시도 4가지
attempts = [
    ("1. 키 그대로 + urllib quote", f"{BASE}{PATH}?serviceKey={urllib.parse.quote(KEY)}&numOfRows=3&pageNo=1&type=json"),
    ("2. 키 그대로 (인코딩 없음)",  f"{BASE}{PATH}?serviceKey={KEY}&numOfRows=3&pageNo=1&type=json"),
    ("3. 키 + 사파리 인코딩",      f"{BASE}{PATH}?serviceKey={urllib.parse.quote(KEY, safe='')}&numOfRows=3&pageNo=1&type=json"),
    ("4. URL 끝에 type 없이",     f"{BASE}{PATH}?serviceKey={KEY}&numOfRows=3&pageNo=1"),
]

print("=" * 70)
print("조달청 API 인증키 진단")
print("=" * 70)
print(f"키: {KEY[:20]}...{KEY[-10:]}")
print()

for name, url in attempts:
    print(f">>> {name}")
    print(f"    URL: {url[:100]}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WI-PriceIntel/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8")
            print(f"    ✅ HTTP {r.status} — 응답 {len(raw)}자")
            print(f"    내용: {raw[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.readable else ""
        print(f"    ❌ HTTP {e.code}: {e.reason}")
        if body:
            print(f"    응답: {body[:200]}")
    except Exception as e:
        print(f"    ❌ {type(e).__name__}: {e}")
    print()
    time.sleep(1)
