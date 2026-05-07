# -*- coding: utf-8 -*-
"""
API 키 없이 코드 검증 — ItemMaster 로드 + 검색어 생성까지만 시뮬레이션
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poc_naver_search import load_items, make_query

print("=" * 70)
print("Dry Run — API 호출 없이 검색어 생성까지 검증")
print("=" * 70)

items = load_items()
print(f"\nItemMaster 로드: {len(items)} SKU")
print()
print(f"{'WI 품번':<12} {'카테고리':<5} {'우리단가':>10}  검색어")
print("-" * 70)

# 카테고리별 1~2개씩 샘플
sampled = {}
for it in items:
    cat = it["category"]
    if cat not in sampled:
        sampled[cat] = []
    if len(sampled[cat]) < 2:
        sampled[cat].append(it)

count = 0
for cat in sorted(sampled.keys()):
    for item in sampled[cat]:
        query = make_query(item)
        price = item["our_price"]
        print(f"{item['code']:<12} {cat:<5} {price:>10,}  {query}")
        count += 1
print()
print(f"샘플: {count}개 / 전체: {len(items)}개")
print()
print("[OK] 코드 정상. API 키 받으면 즉시 실행 가능.")
