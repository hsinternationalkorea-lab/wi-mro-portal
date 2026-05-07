# -*- coding: utf-8 -*-
"""
Group_Hub 추가 3개 폴더 (0_constitution + _registry + _admin) 스켈레톤 생성
- 기존 1_shared/2_WI/3_TeamS 영향 0%
- 출력: ~/Desktop/Group_Hub_constitution.zip → NAS Group_Hub/ 에 업로드 후 압축 풀기
"""
import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

OUT_BASE = Path.home() / "Desktop" / "_constitution_build"
ZIP_OUT = Path.home() / "Desktop" / "Group_Hub_constitution.zip"

TODAY = datetime.now().strftime("%Y-%m-%d")


# ===========================================================
# 0_constitution/ 본문 + ai_adapters/
# ===========================================================
CONSTITUTION_FILES = {
    "0_constitution/README.md": f"""# 회사 헌법 (Company Constitution)
**Last updated**: {TODAY}

이 폴더는 그룹 운영의 절대 규칙·정신·SOP를 담습니다.
모든 AI 페르소나(@dev, @sales 등)는 이 헌법을 시스템 프롬프트로 주입받습니다.

## 8개 본문
1. company_bible.md — 회사 정신·정체성
2. safety_rules.md — 안전 규칙 (절대 위반 X)
3. harness_rules.md — 8 역할 정의
4. permission_matrix.md — 역할별 권한
5. naming_convention.md — 명명 규칙
6. archive_taxonomy.md — 자료 분류 55+
7. new_legal_entity_setup.md — 신규 법인 추가 절차
8. new_division_setup.md — 신규 사업부 추가 절차

## 부속 4개
- harness_integration.md — harness ↔ 헌법 매핑
- ai_persona_template.md — 페르소나 작성 템플릿
- decision_log.md — 결정 이력
- ai_adapters/ — LLM별 어댑터 (Claude/ChatGPT/Gemini/한국LLM)
""",

    "0_constitution/company_bible.md": f"""# 회사 바이블 (Wholesale-K Group)
**Status**: 초안. Phase 2 (6월~) 사장님과 함께 본격 작성

## 그룹 정체성
- **㈜홀세일인더스트리 (WI)** — 유통 사업부, 산업재 B2B
- **팀에스 (TeamS)** — 시공 사업부, 방폭 전기공사
- 그룹명: Wholesale-K
- 슬로건: "Built on Trust. Delivered with Precision."
- 브랜드 컬러: WI Blue #0089D0, Slate #2B3A4E

## 핵심 가치
1. **데이터 자산화** — 사장 머리 → 시스템에 박음
2. **프로다운 신뢰** — 거래처에 5초만에 자료 제공
3. **사업자 분리 원칙** — WI ≠ TeamS (회계·세무 절대 분리)
4. **고객 우선** — 같은 매출에서 마진↑ 또는 매출↑ + 마진 유지
5. **인력 → 시스템** — 사람이 운영하는 회사 → 데이터가 운영하는 시스템

## 의사결정 우선순위
1. 안전 (KOSHA, 컴플라이언스)
2. 거래처 신뢰
3. 사업자 분리
4. 마진
5. 효율

## 미래 (500억 매출 목표)
- 2030 ₩500억 매출
- 시스템화로 인력 의존 ↓ → M&A 가치 ↑
- 사장 부재 시도 회사 운영 지속
""",

    "0_constitution/safety_rules.md": f"""# 안전 규칙 (Safety Rules)
**Last updated**: {TODAY}
**Status**: 절대 위반 금지

## 시놀로지 NAS 자료 보호
- 기존 폴더/파일 절대 삭제 X
- 수정도 사용자 명시 허락 후만
- 새 폴더 추가만 OK

## 사업자 분리
- WI 사업자 A ↔ TeamS 사업자 B 회계·세무 데이터 절대 혼합 X
- 이카운트 인스턴스 별도, API 키 별도

## 비밀 정보
- .env, API 키, 비번, 토큰 → 채팅창 절대 노출 X
- 사용자가 직접 복사·입력하도록 안내

## 금융·계약
- 200만원 이상 견적 외부 발송 = 사장님 승인 게이트
- 세금계산서 자동 발행 = 회계사 승인 후만
- 결재·입찰·계약 = 사용자 명시 허락 후만

## 외부 노출 금지
- raw 자료 (크롤링 원본 HTML/이미지)
- 자재 단가 (특히 공급사 대리점가)
- 견적 양식·내부 SOP
- 거래처 정보·연락처

## 돌이킬 수 없는 작업
- DB DROP, 파일 영구 삭제, 도메인 변경 등
- 한 번 더 확인 + "되돌릴 수 없음" 명시 후만 실행

## AI 자동 생성도 적용
- harness 자동 에이전트도 위 규칙 모두 강제
- _admin/scripts/permission_hook.sh가 검증
""",

    "0_constitution/harness_rules.md": f"""# 하네스 규칙 — 8 역할 정의
**Last updated**: {TODAY}

## 기본 8 역할 (모든 사업부 공통)

| 역할 | 담당 | 핵심 KPI |
|---|---|---|
| @dev | 개발/배포/시스템 운영 | 가동률, 배포 빈도, 버그 수 |
| @sales | 견적/거래처/영업 | 견적 처리 시간, 마진율 |
| @marketing | 콘텐츠/SNS/캠페인 | 도달, 전환율 |
| @finance | 회계/세무 | 마감 기한, 정확도 |
| @ops | 운영/SOP/보고서 | 자동화율, 보고서 발행 |
| @legal | 계약/법무/컴플라이언스 | 분쟁율, 컴플라이언스 |
| @support | 고객/직원 응대 | 응답 시간, 만족도 |
| @data | 분석/RAG/예측 | 정확도, 인사이트 |

## 사업부별 가변 에이전트 (예시)
### WI MRO
- @catalog_curator, @vendor_negotiator, @substitute,
  @customer_savings, @price_intel, @inventory_predictor, @quote_assembler

### TeamS Construction
- @architect, @code_reviewer, @tester, @safety_inspector

## 호출 패턴
```
@{{role}}:{{LE}}:{{DIV}} <action>

예: @sales:WI:MRO 견적 자동 작성
   @ops:WI:MRO 음성 주간보고서
   @data 카탈로그 가격 추세
```

## 상호 호출 규칙
- @sales가 @substitute 호출 (대체품)
- @ops가 @data 호출 (분석 자료)
- @finance가 @legal 호출 (계약 검토)

## 사장님 = 오케스트레이터
- 8 역할 위에서 큰 결정만
- "200만원 이상 외부 발송"은 항상 사장님 게이트 통과
""",

    "0_constitution/permission_matrix.md": f"""# 권한 매트릭스 (Permission Matrix)
**Last updated**: {TODAY}

## 사용자 권한
| 사용자 | 권한 |
|---|---|
| 사장님 | 전체 (오케스트레이터, 모든 결정) |
| 윤주임 | 견적/발주/거래처/시스템 |
| 영업팀 | 견적/거래처 조회 + 본인 작성 견적 |
| 구매팀 | 발주/재고 |
| 일반 직원 | 검색/본인 의뢰 |

## 에이전트 NAS 권한 (WI MRO 예시)
| 에이전트 | NAS 폴더 | DB |
|---|---|---|
| @dev | 전체 R + 코드 W | schema R |
| @sales | 4_quotes R/W, 5_orders R/W, 2_customers R | products R, quote_requests R/W |
| @ops | 9_reports R/W, 1_shared/standards R | crawl_runs R |
| @finance | 6_erp R/W, 7_finance R/W, 1_shared/group_finance R | - |
| @marketing | 10_marketing R/W | - |
| @legal | 1_shared/standards/compliance R | - |
| @support | 1_shared/mail R | quote_requests R |
| @data | 전체 R + 1_shared/archive R/W | DB 전체 R |
| @catalog_curator | 1_catalog R/W | products R/W |
| @substitute | 1_catalog R | products R |
| @customer_savings | 2_customers R/W, 9_reports R/W | quote_requests R |
| @price_intel | 1_catalog/crawl R/W | price_history R/W |
| @inventory_predictor | 6_erp R, 5_orders R/W | quote_requests R |
| @quote_assembler | 4_quotes R/W | quote_requests R/W |
| @vendor_negotiator | 3_suppliers R/W, 6_erp R | manufacturers R |

## 강제 메커니즘
- _admin/scripts/permission_hook.sh 가 모든 에이전트 작업 전 권한 검증
- 위반 시 → audit_log/permission_denied.log 기록 + 사용자 알림
""",

    "0_constitution/naming_convention.md": f"""# 명명 규칙
**Last updated**: {TODAY}

## SKU (WI 품번)
- 형식: `WH-{{Cat}}-{{NNNN}}`
- Cat: M / F / L / C / S / E / P / T / O
- 우선순위: M → F → L → C → S → E → P → T → O
- 4자리 부족 시 자동 5자리 (WH-O-10000)

## 견적서
- 형식: `WHQ-{{YYMM}}-{{NNN}}-R{{n}}`
- 예: WHQ-2605-001-R0 (2026-05 첫 견적, 0차)
- 리비전: R1, R2, ... (수정 시)

## 폴더
- 사업부: `div_NN_{{name}}` (예: div_01_mro)
- 프로젝트: `{{YYYY_QX}}_{{name}}` (예: 2026_Q2_portal_v1)
- 거래처: `{{customer_korean_name}}` (그대로)

## 파일
- 보고서: `{{type}}_{{YYYY-MM-DD}}.{{ext}}` (예: weekly_2026-05-08.xlsx)
- 백업: `{{name}}_backup_{{YYYYMMDD}}.zip`

## AI 페르소나
- 형식: `@{{role}}:{{LE}}:{{DIV}}`
- 예: @sales:WI:MRO

## ECount 거래처 코드
- 사업자별 별도 (WI ≠ TeamS)
- WI: A_{{nnnnn}}, TeamS: B_{{nnnnn}}
""",

    "0_constitution/archive_taxonomy.md": f"""# 자료 분류 체계 (Archive Taxonomy)
**Last updated**: {TODAY}

## 카테고리 (55+)
실제 운영 시 _registry/archive_routing.yml 참조

### 보고서 (8)
- weekly_eumseong (음성 주간)
- daily_briefing
- monthly_division
- quarterly_group
- customer_savings
- vendor_negotiation
- safety_kosha
- audit

### 마케팅 (6)
- instagram_card
- thread_post
- linkedin_article
- press_release
- product_brochure
- campaign_brief

### 거래 (8)
- quote (견적)
- order (발주)
- invoice (세금계산서)
- contract
- nda
- mou
- lease
- service_agreement

### 운영 (10)
- sop
- workflow
- meeting_minutes
- decision_log
- incident_report
- improvement_request
- onboarding_guide
- training_material
- audit_checklist
- safety_inspection

### 시공 (TeamS) (8)
- project_proposal
- design_drawing
- construction_log
- progress_photo
- material_list
- safety_briefing
- completion_report
- warranty

### 인사·재무 (7)
- payroll
- 4대보험
- tax_filing
- recruitment
- performance_review
- expense_report
- budget

### 기타 (8)
- email_archive
- chat_log
- raw_crawl
- db_dump
- screenshot
- video
- audio
- backup
""",

    "0_constitution/new_legal_entity_setup.md": """# 신규 법인 추가 절차

새 법인(예: 4_HS_Chemicals) 만들 때:

## 1. 사업자등록 + 기본 정보
- 사업자등록번호 발급
- 대표자, 주소, 업종
- 자매사 관계 명시

## 2. _registry/legal_entities.yml 등록
```yaml
- id: HS
  name: HS Chemicals
  business_no: "ZZZ-ZZ-ZZZZZ"
  representative: 홍기정
  address: ...
  ecount_com_code: ZZZ
  status: active
```

## 3. NAS 폴더 생성
- `Group_Hub/4_HS/` (또는 슬롯 5/6)
- `_ai/` `_meta/` `_archive/` 표준 하위

## 4. 사업부 슬롯 5개 (div_01~05)

## 5. _registry/ai_personas.yml 에 페르소나 추가
8 역할 + 사업부별 가변 에이전트

## 6. 권한 부여
- 시놀로지 공유 폴더 권한
- ECount 인스턴스 별도
- DB 사업자 분리

## 7. 메모리 sync
모든 AI 세션이 새 법인 인지하도록
""",

    "0_constitution/new_division_setup.md": """# 신규 사업부 추가 절차

기존 법인 안에 새 사업부 추가:

## 1. _registry/divisions.yml 등록
```yaml
WI:
  - id: div_01_mro
    name: MRO 통합 카탈로그
    status: active
  - id: div_02_TBD
    status: vacant_slot
```

## 2. NAS 폴더 생성
- `Group_Hub/2_WI/div_NN_{{name}}/`
- 표준 하위 13개 (catalog/customers/.../projects)
- _ai/ _meta/ _archive/

## 3. 사업부별 가변 에이전트
- 도메인 분석 → harness 자동 제안
- 사장님 검토 후 _registry/ai_personas.yml 등록

## 4. 권한 부여
- 사업부장 R/W
- 다른 사업부 직원 — 격리 (필요 시 read-only)

## 5. ECount 거래처 코드 분리
- 같은 법인이라도 사업부별 분류 가능
""",

    "0_constitution/harness_integration.md": f"""# Harness ↔ 헌법 매핑
**Last updated**: {TODAY}

## Tier 1 (메인) — 우리 헌법
- 8 역할 고정
- 안전 규칙
- 권한 매트릭스
- → harness 위에서 우선

## Tier 2 (보조) — Harness 자동 생성
- 사업부별 가변 에이전트 추천
- 도메인 분석 → 추가 페르소나 제안
- 사장님 검토 후 _registry 등록

## Tier 3 (라이브러리) — Harness-100
- _admin/harness_library/ 에 클론
- 검증된 100 production 패키지
- 즉시 활용 (우리 권한 매트릭스 강제)

## 위배 사항 보완 (스크립트 5개)
- nas_sync.sh — .claude/agents → NAS 동기화
- permission_hook.sh — harness 권한 강제
- archive_wrapper.sh — 생성물 표준 저장
- registry_extender.sh — 등록부 확장
- invocation_adapter.sh — 호출 패턴 변환

## 주의
- harness = Claude 전용 (AI 중립 양보)
- Standby 3 (ChatGPT/Gemini/한국 LLM)는 fallback
""",

    "0_constitution/ai_persona_template.md": """# AI 페르소나 작성 템플릿

새 페르소나 만들 때 이 템플릿 따름.

## 메타데이터
- ID: @{role}:{LE}:{DIV}
- 이름: 한국어 호칭 (예: "MRO 영업팀장")
- 소속 사업부:
- 도입 시점: Phase X
- 생성자: harness 자동 / 사장님 수동

## 역할 정의
- 한 줄 정의
- 핵심 작업 5~7개
- 트리거 (자동/수동/시간)

## 시스템 프롬프트 구성
1. 회사 헌법 (company_bible + safety_rules)
2. 본인 영역 바이블 (예: sales_bible)
3. 권한 매트릭스 (해당 부분만)
4. 호출 패턴 + 상호 호출 규칙
5. 출력 형식 표준

## 권한
- NAS 접근:
- DB 접근:
- 외부 API:

## 입력 / 출력
- 입력 데이터:
- 출력 형식:
- 저장 위치:

## KPI
- 측정 지표:
- 성공 기준:

## 위험 / 게이트
- 사용자 승인 필요한 작업:
- 자동 거부할 패턴:

## 학습 자료 (RAG)
- 임베딩할 문서:
- 업데이트 주기:
""",

    "0_constitution/decision_log.md": f"""# 결정 이력 (Decision Log)
**Format**: 시간순 (최신 위)

---

## 2026-05-08 (목) — Group_Hub 확장 + harness 정식 도입
- Design Studio + MRO 세션 동기화
- NAS에 0_constitution + _registry + _admin 추가 (기존 1_shared/2_WI/3_TeamS는 그대로)
- harness 정식 도입 (Phase 1.5부터)
- WI MRO 가변 에이전트 7개 정의 (@catalog_curator 등)
- AI 중립 양보 (harness = Claude 전용)
- 결정자: 사장님 (홍기정)

## 2026-05-07 (수) — 시험가동 D-1 결정
- 원가 미확정 라벨 (마진 0% 시 표시)
- UI 담백 유지 → 5/15 직원 회고 후 결정
- 원가절감 리포트 → Phase 2
- RLS 보안 → 시험가동 중 활성화
- 저렴한 유사상품 제안 (관리자 전용, P1.5) = 핵심 차별화
- Mac 24/7 헤드리스 워크스테이션 (5/14~)
- 시놀로지 NAS = 외장하드 대신
- ERP/HR/Finance 사업자별 완전 분리

## 2026-05-06 (화) — 시험가동 출발선
- Streamlit Cloud 배포 (wholesale-mro.streamlit.app)
- 42,159 SKU 카탈로그
- wi_code 오버플로우 SQL 패치
- GitHub repo (private→public 임시) - 5/14 자체호스팅 시 private 복귀

## 향후 추가 시 형식
### YYYY-MM-DD (요일) — 결정 제목
- 결정 내용
- 사유
- 결정자
- 영향 범위
- 회의 메모 위치 (NAS 경로)
""",

    # ai_adapters
    "0_constitution/ai_adapters/_vendor_neutral.md": """# AI 벤더 중립 원칙

모든 AI(Claude/ChatGPT/Gemini/한국LLM)에서 동일 결과 보장.

## 표준 인터페이스
- 입력: NAS 자료 + 헌법 + 권한
- 출력: 표준 형식 (Markdown / JSON / Excel)
- 호출: @{role}:{LE}:{DIV}

## 벤더별 어댑터
각 어댑터에서 LLM별 미세 조정:
- claude_adapter — 시스템 프롬프트 길이, 도구 사용법
- chatgpt_adapter — function calling 형식
- gemini_adapter — multi-modal 활용
- korean_llm_adapter — Naver HyperCLOVA, KT 믿음 등
""",

    "0_constitution/ai_adapters/_migration_guide.md": "# 벤더 교체 가이드\n\nClaude → 다른 LLM 전환 시 단계.\n\n(Phase 3 이후 작성)",
    "0_constitution/ai_adapters/claude_adapter.md": "# Claude 어댑터\n\nPrimary 벤더. 시스템 프롬프트 + Skills + Plugins 활용.",
    "0_constitution/ai_adapters/chatgpt_adapter.md": "# ChatGPT 어댑터\n\nStandby 1. Function calling 기반.",
    "0_constitution/ai_adapters/gemini_adapter.md": "# Gemini 어댑터\n\nStandby 2. Multi-modal (이미지·비디오) 강점.",
    "0_constitution/ai_adapters/korean_llm_adapter.md": "# 한국 LLM 어댑터\n\nStandby 3. HyperCLOVA / KT 믿음 / Solar.\n한국어 + 비즈니스 컨텍스트.",
}


# ===========================================================
# _registry/ YAML 파일들
# ===========================================================
REGISTRY_FILES = {
    "_registry/README.md": "# Registry — 등록부\n\n그룹 자산의 master record.\nyml/yaml은 사람이 직접 편집 가능, 변경 시 _registry/version_history.md 자동 update.\n",

    "_registry/legal_entities.yml": """# 법인 등록부
# 변경 시 version_history.md에 기록

legal_entities:
  - id: WI
    name: 홀세일인더스트리
    name_en: Wholesale Industry
    business_no: "TBD"  # 사업자등록번호 입력 필요
    representative: 홍기정
    address: 경기도 시흥시 마산로100 이스페이스
    contact_phone: 031-372-3332
    contact_email: kjhong@wholesale-k.com
    ecount_com_code: TBD
    status: active
    division_slots_max: 5

  - id: TeamS
    name: 팀에스
    name_en: TeamS
    business_no: "TBD"
    representative: TBD
    address: 화성시 동탄
    ecount_com_code: TBD
    status: active
    division_slots_max: 5

  # 슬롯 3개 (신규 법인 대비)
  - id: TBD_4
    status: vacant_slot
  - id: TBD_5
    status: vacant_slot
  - id: TBD_6
    status: vacant_slot
""",

    "_registry/divisions.yml": """# 사업부 등록부

WI:
  - id: div_01_mro
    name: MRO 통합 카탈로그 + 견적
    status: active
    nas_path: 2_WI/div_01_mro
    portal_url: portal.koreaene.co.kr (Phase 2~)
    db_source_codes: [cretec, subone, navimro, sercrim, daihan, wi_master]
  - id: div_02_TBD
    status: vacant_slot
  - id: div_03_TBD
    status: vacant_slot
  - id: div_04_TBD
    status: vacant_slot
  - id: div_05_TBD
    status: vacant_slot

TeamS:
  - id: div_01_construction
    name: 방폭 전기공사
    status: active
    nas_path: 3_TeamS
  - id: div_02_TBD
    status: vacant_slot
  - id: div_03_TBD
    status: vacant_slot
  - id: div_04_TBD
    status: vacant_slot
  - id: div_05_TBD
    status: vacant_slot
""",

    "_registry/ai_personas.yml": """# AI 페르소나 등록부

# 8 기본 역할 (모든 사업부 공통)
base_roles:
  - id: dev
    name: 개발/배포/시스템
  - id: sales
    name: 견적/거래처/영업
  - id: marketing
    name: 콘텐츠/SNS
  - id: finance
    name: 회계/세무
  - id: ops
    name: 운영/SOP/보고서
  - id: legal
    name: 계약/법무/컴플라이언스
  - id: support
    name: 고객/직원 응대
  - id: data
    name: 분석/RAG/예측

# 사업부별 가변 에이전트
WI_div_01_mro:
  - id: catalog_curator
    name: 카탈로그 큐레이터
    phase: 1.5
  - id: vendor_negotiator
    name: 공급사 협상
    phase: 2
  - id: substitute
    name: 저렴한 유사상품 제안
    phase: 1.5
    star: true  # 핵심 차별화
  - id: customer_savings
    name: 거래처 원가절감 보고서
    phase: 2
  - id: price_intel
    name: 경쟁 가격 모니터링
    phase: 2_late
  - id: inventory_predictor
    name: 재고 예측
    phase: 3
  - id: quote_assembler
    name: 견적서 자동 작성
    phase: 2

TeamS_div_01_construction:
  - id: architect
    name: 도면·설계 검토
    phase: 2
  - id: code_reviewer
    name: 코드(전기·방폭) 점검
    phase: 2
  - id: tester
    name: 시공 테스트·QA
    phase: 2
  - id: safety_inspector
    name: KOSHA 안전 점검
    phase: 1.5
""",

    "_registry/ai_vendors.yml": """# AI 벤더 등록부

primary:
  vendor: anthropic_claude
  model: claude-sonnet-4-5
  api_endpoint: https://api.anthropic.com
  status: active

standby:
  - vendor: openai_chatgpt
    model: gpt-4-turbo
    role: fallback
  - vendor: google_gemini
    model: gemini-pro
    role: fallback
  - vendor: korean_llm
    model: HyperCLOVA / KT 믿음 / Solar
    role: 한국어 특화 fallback

# AI 중립 원칙: Claude 외 벤더로도 호출 가능 (어댑터 통해)
# 단, harness는 Claude 전용 (양보)
""",

    "_registry/archive_routing.yml": """# 자료 자동 라우팅 (55+ 카테고리)

routing:
  weekly_eumseong:
    target: 2_WI/div_01_mro/9_reports/1_eumseong_weekly/
  daily_briefing:
    target: 2_WI/div_01_mro/9_reports/3_monthly/  # 월간으로 통합
  customer_savings:
    target: 2_WI/div_01_mro/9_reports/2_customer_savings/
  quote:
    target: 2_WI/div_01_mro/4_quotes/
  invoice:
    target: 2_WI/div_01_mro/6_erp/2_invoices/
  instagram_card:
    target: 2_WI/div_01_mro/10_marketing/1_instagram/
  email_archive:
    target: 1_shared/1_mail/{domain}/
  raw_crawl:
    target: 2_WI/div_01_mro/1_catalog/2_crawl_raw/
  db_dump:
    target: 2_WI/div_01_mro/1_catalog/1_db_dumps/
  safety_kosha:
    target: 3_TeamS/5_safety/1_kosha_reports/
  project_proposal:
    target: 3_TeamS/1_projects/3_proposal/
  decision_log:
    target: 0_constitution/decision_log.md
  payroll_WI:
    target: 2_WI/8_hr/2_payroll/
  payroll_TeamS:
    target: 3_TeamS/9_hr/2_payroll/
  tax_filing_WI:
    target: 2_WI/7_finance/1_tax_filings/
  tax_filing_TeamS:
    target: 3_TeamS/8_finance/1_tax_filings/
  group_pl:
    target: 1_shared/5_group_finance/1_consolidated_pl/
  # ... (55+ 항목 추가 작성)
""",

    "_registry/harness_agents.yml": """# Harness 자동 생성 에이전트 추적

# harness가 생성한 에이전트는 여기 자동 등록
# 사장님 승인 후 ai_personas.yml로 승격

generated_by_harness:
  - id: example_agent
    parent_role: catalog_curator
    created_at: TBD
    approved_by: TBD
    nas_permission: ...
    status: pending_review

# 승인 흐름:
# 1. harness 자동 생성
# 2. 여기에 status=pending_review 등록
# 3. _admin/scripts/permission_hook.sh가 권한 검증
# 4. 사장님 승인 → ai_personas.yml로 이동
# 5. status=active
""",

    "_registry/version_history.md": f"""# 등록부 변경 이력

## {TODAY} — 초기 셋업
- legal_entities.yml: WI, TeamS 등록 + 슬롯 3개
- divisions.yml: WI/div_01_mro, TeamS/div_01_construction
- ai_personas.yml: 8 기본 + WI MRO 가변 7개 + TeamS 가변 4개
- ai_vendors.yml: Claude primary + Standby 3
- archive_routing.yml: 핵심 카테고리 + 슬롯
- harness_agents.yml: 빈 상태 (Phase 1.5부터 추가)

## 향후 추가 시 형식
### YYYY-MM-DD — 변경 내용 요약
- 파일: 무엇이 추가/수정/삭제됐는지
- 사유
- 사장님 승인: yes/no
""",
}


# ===========================================================
# _admin/ 보완 스크립트 + 폴더
# ===========================================================
ADMIN_FILES = {
    "_admin/README.md": """# 관리자 영역

- backups/        주기적 자동 백업 (DB dump, 메모리, NAS 스냅샷)
- audit_log/      모든 AI 작업 로그 (권한 위반 포함)
- secrets/        암호화된 비밀 (사용자 명시 허락 후만 접근)
- harness_library/  harness-100 클론 (Phase 1.5에 채움)
- scripts/        보완 스크립트 5개 (Phase 1.5 ~ 2 구현)

## 권한
- 사장님 + 윤주임만 R/W
- 다른 직원 거부
""",

    "_admin/backups/.keep": "",
    "_admin/audit_log/.keep": "",
    "_admin/secrets/.keep": "",
    "_admin/harness_library/.keep": "",

    "_admin/scripts/README.md": """# 보완 스크립트 (Phase 1.5 구현)

| 스크립트 | 역할 | 시점 |
|---|---|---|
| nas_sync.sh | .claude/agents ↔ NAS 양방향 sync | 5/14~ |
| permission_hook.sh | 모든 에이전트 작업 전 권한 검증 | 5/14~ |
| archive_wrapper.sh | 생성물 자동 archive_routing 저장 | 5/14~ |
| registry_extender.sh | 등록부 자동 확장 (사용자 승인 후) | Phase 2 |
| invocation_adapter.sh | 호출 패턴 변환 (LLM 벤더별) | Phase 2 |
| memory_sync.sh | .claude/projects 메모리 ↔ NAS sync | 5/14~ |
""",

    "_admin/scripts/nas_sync.sh": """#!/bin/bash
# nas_sync.sh — placeholder
# Phase 1.5 (5/14~)에 구현
# 역할: .claude/agents 폴더와 NAS Group_Hub/_admin/harness_library/ 양방향 sync
echo "TODO: implement at Phase 1.5"
""",

    "_admin/scripts/permission_hook.sh": """#!/bin/bash
# permission_hook.sh — placeholder
# 모든 에이전트 작업 전 호출 → 권한 매트릭스 검증
# 위반 시 audit_log에 기록 + reject
echo "TODO: implement at Phase 1.5"
""",

    "_admin/scripts/archive_wrapper.sh": """#!/bin/bash
# archive_wrapper.sh — placeholder
# AI 생성물을 archive_routing.yml에 따라 자동 저장
echo "TODO: implement at Phase 1.5"
""",

    "_admin/scripts/registry_extender.sh": """#!/bin/bash
# registry_extender.sh — placeholder
# 새 페르소나/사업부/법인 등록 자동화
echo "TODO: implement at Phase 2"
""",

    "_admin/scripts/invocation_adapter.sh": """#!/bin/bash
# invocation_adapter.sh — placeholder
# 호출 패턴 (@role:LE:DIV) → LLM별 시스템 프롬프트 변환
echo "TODO: implement at Phase 2"
""",

    "_admin/scripts/memory_sync.sh": """#!/bin/bash
# memory_sync.sh — placeholder
# Mac ~/.claude/projects/.../memory ↔ NAS Group_Hub/2_WI/div_01_mro/_ai/memory/
echo "TODO: implement at Phase 1.5"
""",
}


def main():
    if OUT_BASE.exists():
        shutil.rmtree(OUT_BASE)
    OUT_BASE.mkdir(parents=True)

    all_files = {**CONSTITUTION_FILES, **REGISTRY_FILES, **ADMIN_FILES}

    for rel, content in all_files.items():
        path = OUT_BASE / "Group_Hub" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUT_BASE):
            for file in files:
                src = Path(root) / file
                arc = src.relative_to(OUT_BASE)
                zf.write(src, arc)

    file_count = sum(1 for _ in OUT_BASE.rglob("*") if _.is_file())
    folder_count = sum(1 for _ in OUT_BASE.rglob("*") if _.is_dir())
    print(f"OK 폴더 {folder_count}개, 파일 {file_count}개")
    print(f"OK ZIP: {ZIP_OUT}  ({ZIP_OUT.stat().st_size/1024:.1f} KB)")
    print()
    print("다음:")
    print("1. 시놀로지 NAS Group_Hub/ 안에 ZIP 업로드")
    print("2. 우클릭 → 풀기 (덮어쓰기 X)")
    print("3. 결과: 0_constitution/ + _registry/ + _admin/ 추가됨")
    print("4. 기존 1_shared/2_WI/3_TeamS 영향 0% 보장")


if __name__ == "__main__":
    main()
