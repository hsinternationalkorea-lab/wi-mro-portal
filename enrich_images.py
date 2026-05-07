# -*- coding: utf-8 -*-
"""
이미지 enrichment — 출처별 자동 매칭
- 우리 100 SKU + 크롤링 SKU 간 자동 매칭
- 매칭된 외부 SKU의 이미지 URL을 우리 SKU에 복사
- 같은 상품을 product_aliases로 매핑

매칭 알고리즘:
  1차: 제조사 + 모델번호 정확 일치
  2차: 품명 + 규격 텍스트 유사도 (Jaccard)
  3차: 운영자 수동 검수 후보
"""
import os
import sys
import re
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from supabase_client import SupabaseClient


def normalize(text):
    """공백·특수문자 제거, 소문자"""
    return re.sub(r"[^\w가-힣]", "", str(text or "").lower())


def text_sim(a, b):
    """SequenceMatcher 유사도 0~1"""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def enrich():
    c = SupabaseClient()

    # 1. 직거래 SKU (이미지 없는 것 우선)
    direct = c.select(
        "products",
        select="id,wi_code,name_ko,spec,manufacturer,primary_image_url",
        is_directly_sold="eq.true",
        limit="1000",
    )
    if not isinstance(direct, list):
        print("ERROR fetching direct products")
        return
    print(f"[1] 직거래 SKU: {len(direct)}건")
    no_image = [p for p in direct if not p.get("primary_image_url")]
    print(f"    이미지 없는 SKU: {len(no_image)}건")

    # 2. 외부 출처 (페이지네이션으로 모두 가져오기)
    import urllib.request, json
    external = []
    offset = 0
    batch = 1000
    while True:
        url = f"{c.url}/rest/v1/products?is_directly_sold=eq.false&select=id,wi_code,name_ko,spec,manufacturer,primary_image_url,source_code&limit={batch}&offset={offset}"
        req = urllib.request.Request(url, headers=c.headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            chunk = json.loads(r.read())
        if not chunk:
            break
        external.extend(chunk)
        offset += batch
        if len(chunk) < batch:
            break
    print(f"[2] 외부 출처 SKU: {len(external)}건 (페이지네이션 완료)")

    # 3. 매칭
    matched_count = 0
    for direct_p in no_image:
        d_name = normalize(direct_p["name_ko"])
        d_spec = normalize(direct_p["spec"])
        d_mfr = normalize(direct_p.get("manufacturer", ""))

        best = None
        best_score = 0

        for ext_p in external:
            if not ext_p.get("primary_image_url"):
                continue
            e_name = normalize(ext_p["name_ko"])
            e_spec = normalize(ext_p["spec"])
            e_mfr = normalize(ext_p.get("manufacturer", ""))

            # 1차: 제조사 매칭 보너스
            mfr_match = (d_mfr and e_mfr and d_mfr == e_mfr)

            # 텍스트 유사도
            name_sim = text_sim(d_name, e_name) if e_name else 0
            spec_sim = text_sim(d_spec, e_spec) if e_spec else 0

            score = name_sim * 0.6 + spec_sim * 0.3
            if mfr_match:
                score += 0.1

            # 부분 일치 보너스 (우리 품명이 크레텍 품명에 포함되거나 그 반대)
            if d_name and e_name:
                if d_name in e_name or e_name in d_name:
                    score += 0.15
                # 키워드 일치 (3자 이상 공통 단어)
                d_words = set(d_name[i:i+3] for i in range(len(d_name)-2))
                e_words = set(e_name[i:i+3] for i in range(len(e_name)-2))
                if d_words and e_words:
                    overlap = len(d_words & e_words) / min(len(d_words), len(e_words))
                    score += overlap * 0.1

            if score > best_score and score >= 0.55:  # 임계값 완화
                best_score = score
                best = ext_p

        if best:
            print(f"  [{direct_p['wi_code']}] {direct_p['name_ko'][:25]} ↔ "
                  f"[{best['source_code']}] {best['name_ko'][:25]} (sim={best_score:.2f})")
            # 이미지 복사
            c.update("products", {"id": direct_p["id"]}, {
                "primary_image_url": best["primary_image_url"],
            })
            # alias 매핑
            try:
                c.insert("product_aliases", {
                    "primary_product_id": direct_p["id"],
                    "alias_product_id": best["id"],
                    "similarity_score": round(best_score, 3),
                    "matching_method": "name_spec_text",
                    "verified_by_human": False,
                })
            except Exception:
                pass
            matched_count += 1

    print(f"\n[완료] {matched_count}/{len(no_image)}건 이미지 매칭")


if __name__ == "__main__":
    enrich()
