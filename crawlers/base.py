# -*- coding: utf-8 -*-
"""
크롤러 베이스 모듈
- Supabase 연결 (REST 직접)
- 제품 upsert (insert or update)
- 정규화 (카테고리 매핑, 가격 + 마진 적용)
- 크롤링 로그
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# 상위 폴더의 supabase_client 사용
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import SupabaseClient


# 카테고리별 마진 (DB와 동기화)
CATEGORY_MARGIN = {
    "M": 25.0, "F": 18.0, "L": 22.0, "C": 20.0,
    "S": 25.0, "E": 15.0, "P": 18.0, "T": 22.0, "O": 20.0,
}


class CrawlerBase:
    def __init__(self, source_code):
        self.source = source_code
        self.client = SupabaseClient()
        self.run_id = None

    # ─────────────── 크롤링 실행 로깅 ───────────────
    def start_run(self, notes=""):
        body = {
            "source_code": self.source,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
        }
        result = self.client.insert("crawl_runs", body)
        if isinstance(result, list) and result:
            self.run_id = result[0]["id"]
            print(f"[crawl_runs #{self.run_id}] {self.source} 시작")
        return self.run_id

    def finish_run(self, status="success", added=0, updated=0, errors=None):
        if not self.run_id:
            return
        body = {
            "status": status,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "products_added": added,
            "products_updated": updated,
            "errors": errors or {},
        }
        self.client.update("crawl_runs", {"id": self.run_id}, body)
        print(f"[crawl_runs #{self.run_id}] {status}: +{added} ~{updated}")

    # ─────────────── 정규화 ───────────────
    def calc_list_price(self, cost_price, category_code):
        """원가 + 카테고리 마진 = 표시가"""
        if not cost_price:
            return None, None
        margin = CATEGORY_MARGIN.get(category_code, 20.0)
        list_price = round(cost_price * (1 + margin / 100))
        return list_price, margin

    def make_search_keywords(self, name_ko, spec="", manufacturer="", model_no=""):
        """pg_trgm 검색용 통합 키워드"""
        parts = [str(p or "").strip() for p in [name_ko, spec, manufacturer, model_no]]
        return " ".join(p for p in parts if p)[:500]

    # ─────────────── 제품 upsert ───────────────
    def upsert_product(self, product_data):
        """source + source_product_id로 중복 검사 후 INSERT or UPDATE"""
        existing = self.client.select(
            "products",
            select="id,wi_code",
            **{
                "source_code": f"eq.{self.source}",
                "source_product_id": f"eq.{product_data['source_product_id']}",
            },
        )

        # cost → list price 자동 계산
        if product_data.get("cost_price") and product_data.get("category_code"):
            lp, margin = self.calc_list_price(
                product_data["cost_price"],
                product_data["category_code"]
            )
            product_data["list_price"] = lp
            product_data["margin_pct"] = margin

        # 검색 키워드 자동 생성
        if not product_data.get("search_keywords"):
            product_data["search_keywords"] = self.make_search_keywords(
                product_data.get("name_ko", ""),
                product_data.get("spec", ""),
                product_data.get("manufacturer", ""),
                product_data.get("model_no", ""),
            )

        product_data["source_code"] = self.source
        product_data["last_crawled_at"] = datetime.now(timezone.utc).isoformat()

        if isinstance(existing, list) and existing:
            # UPDATE
            pid = existing[0]["id"]
            self.client.update("products", {"id": pid}, product_data)
            return ("updated", pid)
        else:
            # INSERT
            result = self.client.insert("products", product_data)
            if isinstance(result, list) and result:
                return ("inserted", result[0]["id"])
            return ("error", result)

    # ─────────────── 가격 시계열 기록 ───────────────
    def log_price(self, product_id, cost_price, list_price=None, source_price=None, stock_status=None):
        body = {
            "product_id": product_id,
            "cost_price": cost_price,
            "source_price": source_price,
            "list_price": list_price,
            "stock_status": stock_status,
        }
        self.client.insert("price_history", body)


if __name__ == "__main__":
    # 자체 테스트
    base = CrawlerBase("cretec")
    print("CrawlerBase 초기화 OK")
    print(f"  카테고리 마진: {CATEGORY_MARGIN}")
    print(f"  표시가 계산 예: 원가 100000, T카테고리 → {base.calc_list_price(100000, 'T')}")
