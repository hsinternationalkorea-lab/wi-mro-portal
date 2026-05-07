# -*- coding: utf-8 -*-
"""
Group_Hub 폴더 구조 v2 — 번호 prefix 추가 (시놀로지 정렬 친화)
실행 후 ~/Desktop/Group_Hub_v2.zip 생성
"""
import os
import zipfile
import shutil
from pathlib import Path

OUT_BASE = Path.home() / "Desktop" / "_group_hub_build_v2"
ZIP_OUT = Path.home() / "Desktop" / "Group_Hub_v2.zip"

FOLDERS = [
    # ============ _shared 그룹 공통 ============
    "Group_Hub/1_shared/1_mail/1_teams",
    "Group_Hub/1_shared/1_mail/2_wholesale",
    "Group_Hub/1_shared/1_mail/3_hs",
    "Group_Hub/1_shared/1_mail/4_naver",
    "Group_Hub/1_shared/2_standards/1_policies",
    "Group_Hub/1_shared/2_standards/2_brand",
    "Group_Hub/1_shared/2_standards/3_templates",
    "Group_Hub/1_shared/2_standards/4_compliance",
    "Group_Hub/1_shared/3_archive",
    "Group_Hub/1_shared/4_secrets_backup",
    "Group_Hub/1_shared/5_group_finance/1_consolidated_pl",
    "Group_Hub/1_shared/5_group_finance/2_tax_planning",
    "Group_Hub/1_shared/5_group_finance/3_audit",

    # ============ WI 유통 사업부 ============
    "Group_Hub/2_WI/1_catalog/1_db_dumps",
    "Group_Hub/2_WI/1_catalog/2_crawl_raw",
    "Group_Hub/2_WI/1_catalog/3_images",
    # 직거래 9개 (사용자 언급 순서)
    "Group_Hub/2_WI/1_catalog/4_direct_brands/1_Fitok",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/2_IEP",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/3_NewsonGale",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/4_Halcarbon",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/5_Uniphos",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/6_Twintec",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/7_Valmet",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/8_Atexon",
    "Group_Hub/2_WI/1_catalog/4_direct_brands/9_TESI",

    "Group_Hub/2_WI/2_customers",
    "Group_Hub/2_WI/3_suppliers/1_cretec",
    "Group_Hub/2_WI/3_suppliers/2_subone",
    "Group_Hub/2_WI/3_suppliers/3_navimro",
    "Group_Hub/2_WI/3_suppliers/4_sercrim",
    "Group_Hub/2_WI/3_suppliers/5_daihan",

    "Group_Hub/2_WI/4_quotes",
    "Group_Hub/2_WI/5_orders",
    "Group_Hub/2_WI/6_erp/1_customers",
    "Group_Hub/2_WI/6_erp/2_invoices",
    "Group_Hub/2_WI/6_erp/3_transactions",
    "Group_Hub/2_WI/6_erp/4_inventory",
    "Group_Hub/2_WI/7_finance/1_tax_filings",
    "Group_Hub/2_WI/7_finance/2_monthly_reports",
    "Group_Hub/2_WI/7_finance/3_audit",
    "Group_Hub/2_WI/8_hr/1_employees",
    "Group_Hub/2_WI/8_hr/2_payroll",
    "Group_Hub/2_WI/8_hr/3_recruitment",
    "Group_Hub/2_WI/9_reports/1_eumseong_weekly",
    "Group_Hub/2_WI/9_reports/2_customer_savings",
    "Group_Hub/2_WI/9_reports/3_monthly",
    "Group_Hub/2_WI/10_marketing/1_instagram",
    "Group_Hub/2_WI/10_marketing/2_content",
    "Group_Hub/2_WI/10_marketing/3_campaigns",
    "Group_Hub/2_WI/11_website/1_source",
    "Group_Hub/2_WI/11_website/2_content",
    "Group_Hub/2_WI/12_education",
    "Group_Hub/2_WI/13_projects/2026_Q2_portal_v1",

    # ============ TeamS 시공 사업부 ============
    "Group_Hub/3_TeamS/1_projects/1_active",
    "Group_Hub/3_TeamS/1_projects/2_completed",
    "Group_Hub/3_TeamS/1_projects/3_proposal",
    "Group_Hub/3_TeamS/2_customers",
    "Group_Hub/3_TeamS/3_partners",
    "Group_Hub/3_TeamS/4_materials/1_방폭부품",
    "Group_Hub/3_TeamS/4_materials/2_케이블",
    "Group_Hub/3_TeamS/4_materials/3_안전장비",
    "Group_Hub/3_TeamS/5_safety/1_kosha_reports",
    "Group_Hub/3_TeamS/5_safety/2_incident_reports",
    "Group_Hub/3_TeamS/5_safety/3_checklists",
    "Group_Hub/3_TeamS/5_safety/4_training",
    "Group_Hub/3_TeamS/6_certifications/1_kosha_18001",
    "Group_Hub/3_TeamS/6_certifications/2_방폭전기",
    "Group_Hub/3_TeamS/6_certifications/3_직원자격증",
    "Group_Hub/3_TeamS/7_erp/1_customers",
    "Group_Hub/3_TeamS/7_erp/2_invoices",
    "Group_Hub/3_TeamS/7_erp/3_transactions",
    "Group_Hub/3_TeamS/7_erp/4_inventory",
    "Group_Hub/3_TeamS/8_finance/1_tax_filings",
    "Group_Hub/3_TeamS/8_finance/2_monthly_reports",
    "Group_Hub/3_TeamS/8_finance/3_audit",
    "Group_Hub/3_TeamS/9_hr/1_employees",
    "Group_Hub/3_TeamS/9_hr/2_payroll",
    "Group_Hub/3_TeamS/9_hr/3_recruitment",
    "Group_Hub/3_TeamS/10_reports/1_daily_site",
    "Group_Hub/3_TeamS/10_reports/2_weekly",
    "Group_Hub/3_TeamS/10_reports/3_completion",
    "Group_Hub/3_TeamS/10_reports/4_monthly",
    "Group_Hub/3_TeamS/11_marketing",
    "Group_Hub/3_TeamS/12_website/1_source",
    "Group_Hub/3_TeamS/12_website/2_content",
    "Group_Hub/3_TeamS/13_education",
    "Group_Hub/3_TeamS/14_standards",
]


README = {
    "1_shared": "# 그룹 공통 자산\n양 사업부 모두 활용",
    "1_shared/1_mail": "# 그룹 메일 통합 모니터링\n4개 도메인 IMAP 백업\n- 1_teams: 팀에스 도메인\n- 2_wholesale: 현재 WI 도메인\n- 3_hs: WI 전신 (역사적, 일부 활용)\n- 4_naver: HS 도메인 전 (역사적, 일부 활용)",
    "1_shared/2_standards": "# 그룹 공통 정책\n양 사업부 동일 적용",
    "1_shared/3_archive": "# 과거 자산 (RAG용)\nPhase 3 임베딩 검색",
    "1_shared/4_secrets_backup": "# 비밀 암호화 백업\n_secrets/.env, cookies (암호 ZIP 권장)",
    "1_shared/5_group_finance": "# 그룹 통합 재무\n연결 손익, 세무 전략, 그룹 감사\n⚠ 각 사업부 finance와 분리 — 통합 분석만",

    "2_WI": "# 유통 사업부 (Wholesale Industry)\n사업자번호 A — 산업재 B2B\n\n## 핵심\n- 1_catalog/ MRO 카탈로그 (포털 코어)\n- 1_catalog/4_direct_brands/ 직거래 9개\n- 6_erp/ 이카운트 (사업자 A)",
    "2_WI/1_catalog/4_direct_brands": "# 직거래 9개 브랜드 (WI 핵심 차별화)\n1. Fitok 가스 피팅·밸브\n2. IEP 정밀 임피던스\n3. NewsonGale 정전기 grounding\n4. Halcarbon 화학물질\n5. Uniphos 가스 검지\n6. Twintec 클린룸\n7. Valmet 자동제어\n8. Atexon 방폭\n9. TESI",

    "3_TeamS": "# 시공 사업부 (방폭 전기공사)\n사업자번호 B\n\n## 핵심\n- 1_projects/ 시공 프로젝트 (active/completed/proposal)\n- 5_safety/ KOSHA 안전관리 (시공 핵심)\n- 7_erp/ 이카운트 (사업자 B)",
    "3_TeamS/5_safety": "# 안전관리 (시공 사업부 핵심)\nKOSHA 18001, 방폭 안전, 사고 예방",
}


def main():
    if OUT_BASE.exists():
        shutil.rmtree(OUT_BASE)
    OUT_BASE.mkdir(parents=True)

    for f in FOLDERS:
        full = OUT_BASE / f
        full.mkdir(parents=True, exist_ok=True)
        (full / ".keep").write_text("", encoding="utf-8")

    for rel, content in README.items():
        readme_path = OUT_BASE / "Group_Hub" / rel / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(content, encoding="utf-8")

    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUT_BASE):
            for file in files:
                src = Path(root) / file
                arc = src.relative_to(OUT_BASE)
                zf.write(src, arc)

    folder_count = sum(1 for _ in OUT_BASE.rglob("*") if _.is_dir())
    file_count = sum(1 for _ in OUT_BASE.rglob("*") if _.is_file())
    print(f"OK 폴더 {folder_count}개")
    print(f"OK 파일 {file_count}개")
    print(f"OK ZIP: {ZIP_OUT}  ({ZIP_OUT.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
