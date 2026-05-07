# WI MRO Portal

㈜홀세일인더스트리 MRO B2B 통합 카탈로그 + 견적 플랫폼.

## 구성
- **portal/app.py** — Streamlit 검색/카트/견적 + 관리자 페이지
- **crawlers/** — 크레텍, 서브원, 나비엠알오, 석림랩텍, 대한과학 크롤러
- **db/** — PostgreSQL 스키마 + 트리거
- **supabase_client.py** — Supabase REST API 클라이언트 (의존성 0)

## 데이터 출처 (2026-05-07 기준)
| Source | SKU 수 | 비고 |
|---|---|---|
| cretec | 25,376 | 대리점 회원 (정가/원가) |
| navimro | 9,731 | 회원 가격 |
| sercrim | 3,220 | 표시가 |
| subone | 2,598 | JSON API + 카테고리 코드 |
| daihan | 1,134 | 표시가 |
| wi_master | 100 | 직거래 시드 |
| **TOTAL** | **42,159** | |

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run portal/app.py
```

## 환경변수
`_secrets/.env` 또는 Streamlit Cloud secrets:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
