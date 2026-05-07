# -*- coding: utf-8 -*-
"""
Supabase REST API 직접 호출 클라이언트 (의존성 0)
- supabase-py 설치 이슈 우회
- urllib만 사용 (표준 라이브러리)
"""
import os
import json
import urllib.request
import urllib.parse


def load_env():
    """환경변수 로드 — 우선순위: Streamlit secrets > _secrets/.env > os.environ"""
    env = {}
    # 1. Streamlit Cloud secrets (배포 환경)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in ("SUPABASE_URL", "SUPABASE_ANON_KEY"):
                if k in st.secrets:
                    env[k] = st.secrets[k]
            if env.get("SUPABASE_URL") and env.get("SUPABASE_ANON_KEY"):
                return env
    except Exception:
        pass

    # 2. 로컬 _secrets/.env (개발 환경)
    env_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "_secrets", ".env"
    )
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
        if env.get("SUPABASE_URL") and env.get("SUPABASE_ANON_KEY"):
            return env

    # 3. 시스템 환경변수 (CI/CD)
    for k in ("SUPABASE_URL", "SUPABASE_ANON_KEY"):
        if k in os.environ:
            env[k] = os.environ[k]
    return env


class SupabaseClient:
    def __init__(self):
        env = load_env()
        self.url = env["SUPABASE_URL"]
        self.key = env["SUPABASE_ANON_KEY"]
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _request(self, method, path, params=None, body=None):
        import time as _time
        url = f"{self.url}/rest/v1{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode("utf-8") if body else None
        # DNS·네트워크 일시 장애 retry (3회)
        last_err = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
                with urllib.request.urlopen(req, timeout=15) as r:
                    content = r.read().decode("utf-8")
                    if not content:
                        return {"status": r.status, "ok": True}
                    return json.loads(content)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                return {"error": f"HTTP {e.code}", "body": err_body}
            except (urllib.error.URLError, OSError) as e:
                last_err = e
                if attempt < 2:
                    _time.sleep(2 ** attempt)  # 1s, 2s
                    continue
                return {"error": str(e)}

    def select(self, table, **params):
        return self._request("GET", f"/{table}", params)

    def insert(self, table, rows):
        return self._request("POST", f"/{table}", body=rows)

    def update(self, table, match, values):
        params = {f"{k}": f"eq.{v}" for k, v in match.items()}
        return self._request("PATCH", f"/{table}", params=params, body=values)


def test_connection():
    client = SupabaseClient()
    print(f"URL: {client.url}")
    print(f"Key: {client.key[:30]}...")
    print()
    # 가장 간단한 호출 — 빈 테이블 categories 조회
    result = client.select("categories", limit=5)
    if isinstance(result, dict) and result.get("error"):
        print(f"❌ 에러: {result['error']}")
        print(f"   응답: {result.get('body', '')[:300]}")
        return False
    print(f"✅ 연결 성공")
    print(f"   응답: {result if isinstance(result, list) else result}")
    if isinstance(result, list):
        if not result:
            print("   ⚠ categories 테이블이 비어있음 (스키마 미생성 또는 시드 미적용)")
        else:
            print(f"   카테고리 {len(result)}건 조회됨")
    return True


if __name__ == "__main__":
    test_connection()
