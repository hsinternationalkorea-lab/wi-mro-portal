# -*- coding: utf-8 -*-
"""
Group_Hub 폴더 구조 생성 + ZIP 압축
실행 후 ~/Desktop/Group_Hub.zip 생성됨 → 시놀로지에 업로드
"""
import os
import zipfile
from pathlib import Path

# 출력 위치 — 데스크탑
OUT_BASE = Path.home() / "Desktop" / "_group_hub_build"
ZIP_OUT = Path.home() / "Desktop" / "Group_Hub.zip"

FOLDERS = [
    # ============ _shared ============
    "Group_Hub/_shared/mail/teams",
    "Group_Hub/_shared/mail/wholesale",
    "Group_Hub/_shared/mail/hs",
    "Group_Hub/_shared/mail/naver",
    "Group_Hub/_shared/standards/policies",
    "Group_Hub/_shared/standards/brand",
    "Group_Hub/_shared/standards/templates",
    "Group_Hub/_shared/standards/compliance",
    "Group_Hub/_shared/archive",
    "Group_Hub/_shared/secrets_backup",
    "Group_Hub/_shared/group_finance/consolidated_pl",
    "Group_Hub/_shared/group_finance/tax_planning",
    "Group_Hub/_shared/group_finance/audit",

    # ============ WI 유통 사업부 ============
    "Group_Hub/WI/erp/customers",
    "Group_Hub/WI/erp/invoices",
    "Group_Hub/WI/erp/transactions",
    "Group_Hub/WI/erp/inventory",
    "Group_Hub/WI/hr/employees",
    "Group_Hub/WI/hr/payroll",
    "Group_Hub/WI/hr/recruitment",
    "Group_Hub/WI/finance/tax_filings",
    "Group_Hub/WI/finance/monthly_reports",
    "Group_Hub/WI/finance/audit",
    "Group_Hub/WI/catalog/db_dumps",
    "Group_Hub/WI/catalog/crawl_raw",
    "Group_Hub/WI/catalog/images",
    # 직거래 9개
    "Group_Hub/WI/catalog/direct_brands/Fitok",
    "Group_Hub/WI/catalog/direct_brands/IEP",
    "Group_Hub/WI/catalog/direct_brands/NewsonGale",
    "Group_Hub/WI/catalog/direct_brands/Halcarbon",
    "Group_Hub/WI/catalog/direct_brands/Uniphos",
    "Group_Hub/WI/catalog/direct_brands/Twintec",
    "Group_Hub/WI/catalog/direct_brands/Valmet",
    "Group_Hub/WI/catalog/direct_brands/Atexon",
    "Group_Hub/WI/catalog/direct_brands/TESI",
    "Group_Hub/WI/customers",
    "Group_Hub/WI/suppliers/cretec",
    "Group_Hub/WI/suppliers/subone",
    "Group_Hub/WI/suppliers/navimro",
    "Group_Hub/WI/suppliers/sercrim",
    "Group_Hub/WI/suppliers/daihan",
    "Group_Hub/WI/quotes",
    "Group_Hub/WI/orders",
    "Group_Hub/WI/reports/eumseong_weekly",
    "Group_Hub/WI/reports/customer_savings",
    "Group_Hub/WI/reports/monthly",
    "Group_Hub/WI/marketing/instagram",
    "Group_Hub/WI/marketing/content",
    "Group_Hub/WI/marketing/campaigns",
    "Group_Hub/WI/website/source",
    "Group_Hub/WI/website/content",
    "Group_Hub/WI/education",
    "Group_Hub/WI/projects/2026_Q2_portal_v1",

    # ============ TeamS 시공 사업부 ============
    "Group_Hub/TeamS/erp/customers",
    "Group_Hub/TeamS/erp/invoices",
    "Group_Hub/TeamS/erp/transactions",
    "Group_Hub/TeamS/erp/inventory",
    "Group_Hub/TeamS/hr/employees",
    "Group_Hub/TeamS/hr/payroll",
    "Group_Hub/TeamS/hr/recruitment",
    "Group_Hub/TeamS/finance/tax_filings",
    "Group_Hub/TeamS/finance/monthly_reports",
    "Group_Hub/TeamS/finance/audit",
    "Group_Hub/TeamS/projects/active",
    "Group_Hub/TeamS/projects/completed",
    "Group_Hub/TeamS/projects/proposal",
    "Group_Hub/TeamS/customers",
    "Group_Hub/TeamS/partners",
    "Group_Hub/TeamS/materials/방폭부품",
    "Group_Hub/TeamS/materials/케이블",
    "Group_Hub/TeamS/materials/안전장비",
    "Group_Hub/TeamS/certifications/kosha_18001",
    "Group_Hub/TeamS/certifications/방폭전기",
    "Group_Hub/TeamS/certifications/직원자격증",
    "Group_Hub/TeamS/safety/kosha_reports",
    "Group_Hub/TeamS/safety/incident_reports",
    "Group_Hub/TeamS/safety/checklists",
    "Group_Hub/TeamS/safety/training",
    "Group_Hub/TeamS/reports/daily_site",
    "Group_Hub/TeamS/reports/weekly",
    "Group_Hub/TeamS/reports/completion",
    "Group_Hub/TeamS/reports/monthly",
    "Group_Hub/TeamS/marketing",
    "Group_Hub/TeamS/website/source",
    "Group_Hub/TeamS/website/content",
    "Group_Hub/TeamS/education",
    "Group_Hub/TeamS/standards",
]


# 각 폴더에 README 추가 (빈 폴더는 ZIP에서 종종 누락됨)
README_CONTENT = {
    "_shared/mail": "# 그룹 메일 통합 모니터링\n4개 도메인 (teams / wholesale / hs / naver) IMAP 백업",
    "_shared/standards": "# 그룹 공통 정책\n양 사업부 동일 적용",
    "_shared/group_finance": "# 그룹 통합 재무\n연결 손익, 세무 전략, 그룹 감사",
    "_shared/archive": "# 과거 자산 (RAG용)\nPhase 3 임베딩 검색",
    "_shared/secrets_backup": "# 비밀 암호화 백업\n_secrets/.env, cookies 등 (암호 ZIP 권장)",

    "WI": "# 유통 사업부 (Wholesale Industry)\n사업자번호 A — 산업재 B2B\n\n## 핵심\n- catalog/ MRO 카탈로그 (포털)\n- direct_brands/ 직거래 9개 (Fitok·IEP·NewsonGale·Halcarbon·Uniphos·Twintec·Valmet·Atexon·TESI)\n- erp/ 이카운트 (사업자 A)",

    "WI/catalog/direct_brands": "# 직거래 9개 브랜드 (WI 핵심 차별화)\n- Fitok 가스 피팅·밸브\n- IEP 정밀 임피던스\n- NewsonGale 정전기 grounding\n- Halcarbon 화학물질\n- Uniphos 가스 검지\n- Twintec 클린룸\n- Valmet 자동제어\n- Atexon 방폭\n- TESI",

    "TeamS": "# 시공 사업부 (방폭 전기공사)\n사업자번호 B — 시공·프로젝트\n\n## 핵심\n- projects/ 시공 프로젝트 (active/completed/proposal)\n- safety/ KOSHA 안전관리\n- erp/ 이카운트 (사업자 B)",

    "TeamS/safety": "# 안전관리 (시공 사업부 핵심)\nKOSHA 18001, 방폭 안전, 사고 예방",
}


def main():
    OUT_BASE.parent.mkdir(parents=True, exist_ok=True)
    if OUT_BASE.exists():
        import shutil
        shutil.rmtree(OUT_BASE)
    OUT_BASE.mkdir(parents=True)

    # 폴더 + .keep 파일 생성
    for f in FOLDERS:
        full = OUT_BASE / f
        full.mkdir(parents=True, exist_ok=True)
        # .keep 파일로 빈 폴더 ZIP 보장
        (full / ".keep").write_text("", encoding="utf-8")

    # README 추가
    for rel, content in README_CONTENT.items():
        readme_path = OUT_BASE / "Group_Hub" / rel / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(content, encoding="utf-8")

    # ZIP 생성
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUT_BASE):
            for file in files:
                src = Path(root) / file
                arc = src.relative_to(OUT_BASE)
                zf.write(src, arc)

    # 통계
    folder_count = sum(1 for _ in OUT_BASE.rglob("*") if _.is_dir())
    file_count = sum(1 for _ in OUT_BASE.rglob("*") if _.is_file())
    zip_size_kb = ZIP_OUT.stat().st_size / 1024

    print(f"OK 폴더 생성: {folder_count}개")
    print(f"OK 파일 (.keep + README): {file_count}개")
    print(f"OK ZIP: {ZIP_OUT}  ({zip_size_kb:.1f} KB)")
    print()
    print("다음: 시놀로지 NAS File Station에 ZIP 업로드 → 우클릭 → 압축 풀기")


if __name__ == "__main__":
    main()
