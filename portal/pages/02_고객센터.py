# -*- coding: utf-8 -*-
"""
고객센터 — 시나리오 학습 모드 (2026-05 ~ 06 시험가동)

직원이 가상 손님 시나리오로 챗봇 학습 데이터를 만든다:
  1. 직원 이름 + 역할 선택
  2. 시나리오 카테고리 선택 (견적/납기/대체품/결제/컴플레인/기타)
  3. 가상 손님 메시지 + 모범 답변 함께 입력 → Supabase chat_logs 저장
  4. 누적 카운트 표시

한 달 후 (Phase 2):
  - 누적 로그에서 자주 묻는 질문 그룹화 → FAQ
  - Claude API + RAG 로 자동 응답
  - 외부 손님 실 사용 라이브
"""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from supabase_client import SupabaseClient

st.set_page_config(
    page_title="WI · 고객센터 학습",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────
# 외부 차단 가드 (app.py 와 동일 — session_state 공유)
# ────────────────────────────────────────────────────────────
if not st.session_state.get("access_granted"):
    st.warning("🔒 시험가동 중입니다. 메인 페이지에서 직원 코드를 먼저 입력해주세요.")
    if st.button("← 메인으로"):
        st.switch_page("app.py")
    st.stop()


# ────────────────────────────────────────────────────────────
# 시간대
# ────────────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
is_after_hours = now.hour >= 18 or now.hour < 9

st.title("💬 고객센터 학습 도구")
st.caption(
    f"현재 (KST): {now.strftime('%Y-%m-%d %H:%M')} · "
    f"{'🌙 AI 응대 시간' if is_after_hours else '🟢 직원 응대 시간'} · "
    f"세션: {st.session_state.get('session_id', '_')[:8]}"
)


# ────────────────────────────────────────────────────────────
# 직원 정보 + 시나리오 분류
# ────────────────────────────────────────────────────────────
EMPLOYEES = ["홍기정 (대표)", "윤여준 (영업)", "이효근 (기술/영업)", "신입사원 (학습)"]
ROLES = ["영업", "기술지원/CS", "관리자", "기타"]
SCENARIO_CATEGORIES = [
    "견적 문의",
    "납기/배송",
    "대체품 / 호환",
    "결제 조건 / 거래",
    "기술 사양 / 설치",
    "컴플레인 / 반품",
    "신규 거래 문의",
    "기타",
]

with st.sidebar:
    st.markdown("### 학습자 정보")
    employee = st.selectbox("직원", EMPLOYEES, key="cs_employee")
    role = st.selectbox("역할", ROLES, key="cs_role", index=0)
    st.markdown("---")
    st.markdown("### 학습 가이드")
    st.markdown(
        "**1.** 가상 손님 입장에서 질문 만들기  \n"
        "**2.** 그 질문에 대한 **모범 답변** 작성  \n"
        "**3.** [학습 데이터로 저장] 클릭  \n"
        "**4.** 누적되어 향후 AI 학습에 사용됨"
    )
    st.markdown("---")
    st.markdown("### 좋은 시나리오 팁")
    st.caption(
        "- 자주 받는 질문 우선  \n"
        "- 답변하기 까다로웠던 케이스  \n"
        "- 신입이 헷갈리는 질문  \n"
        "- 한 시나리오 = 한 가지 주제만"
    )


# ────────────────────────────────────────────────────────────
# 세션 정보
# ────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:12]
if "cs_today_count" not in st.session_state:
    st.session_state.cs_today_count = 0


# ────────────────────────────────────────────────────────────
# 메인 입력 폼
# ────────────────────────────────────────────────────────────
st.markdown("### 📝 시나리오 작성")

with st.form("training_form", clear_on_submit=True):
    fc1, fc2 = st.columns([1, 1])
    with fc1:
        scenario_type = st.selectbox("시나리오 카테고리", SCENARIO_CATEGORIES)
    with fc2:
        difficulty = st.select_slider(
            "난이도",
            options=["쉬움", "보통", "어려움"],
            value="보통",
            help="신입 기준 답변 난이도",
        )

    customer_msg = st.text_area(
        "🙋 가상 손님 질문",
        placeholder="예) 베어링 6204 ZZ 100개 견적 부탁드립니다. 납기는 언제까지 가능할까요?",
        height=100,
    )

    ideal_answer = st.text_area(
        "✅ 모범 답변 (학습 데이터)",
        placeholder="예) 안녕하세요. 6204 ZZ 베어링 100개 견적 가능합니다.\n"
                    "- 단가: NSK 기준 1,800원/EA (수량 할인 적용)\n"
                    "- 납기: 재고분 익일, 추가 발주 시 3~5영업일\n"
                    "- 결제: 월 마감 익월 말 또는 선결제 1% 할인\n"
                    "정식 견적서는 sales@wholesale-k.com 으로 보내드리겠습니다.",
        height=180,
    )

    tags = st.text_input(
        "태그 (쉼표 구분, 선택)",
        placeholder="예) 베어링, NSK, 견적, 100개",
        help="검색/그룹화용 키워드",
    )

    note = st.text_input(
        "내부 메모 (선택)",
        placeholder="예) 이 질문은 한 달에 5번 정도 옴, 단가 협상 여지 있음",
    )

    submitted = st.form_submit_button("💾 학습 데이터로 저장", type="primary", use_container_width=True)

    if submitted:
        if not customer_msg.strip() or not ideal_answer.strip():
            st.error("손님 질문 / 모범 답변 모두 입력 필요합니다.")
        else:
            try:
                client = SupabaseClient()
                base = {
                    "session_id": st.session_state.session_id,
                    "employee_name": employee,
                    "employee_role": role,
                    "scenario_type": scenario_type,
                    "difficulty": difficulty,
                    "tags": tags.strip() or None,
                    "internal_note": note.strip() or None,
                    "is_simulated": True,
                    "is_after_hours": is_after_hours,
                }
                client.insert("chat_logs", [
                    {**base, "role": "user", "message": customer_msg.strip()},
                    {**base, "role": "assistant", "message": ideal_answer.strip()},
                ])
                st.session_state.cs_today_count += 1
                st.success(f"✅ 저장 완료! 오늘 누적 {st.session_state.cs_today_count}건")
                st.balloons()
            except Exception as e:
                st.error(f"저장 실패: {e}")


# ────────────────────────────────────────────────────────────
# 누적 현황 (간단 통계)
# ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 누적 학습 현황")

try:
    client = SupabaseClient()
    all_logs = client.select(
        "chat_logs",
        select="employee_name,scenario_type,is_simulated,role",
        is_simulated="eq.true",
        role="eq.user",  # user 메시지만 카운트 (쌍이라 user/assistant 2개씩)
        limit="5000",
    )
    user_logs = all_logs if isinstance(all_logs, list) else []

    if user_logs:
        total = len(user_logs)
        by_employee = {}
        by_type = {}
        for r in user_logs:
            e = r.get("employee_name") or "?"
            t = r.get("scenario_type") or "?"
            by_employee[e] = by_employee.get(e, 0) + 1
            by_type[t] = by_type.get(t, 0) + 1
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("총 학습 데이터", f"{total:,}건")
        with sc2:
            top_emp = max(by_employee.items(), key=lambda x: x[1]) if by_employee else ("-", 0)
            st.metric("1등 직원", f"{top_emp[0]}", f"+{top_emp[1]}건")
        with sc3:
            top_type = max(by_type.items(), key=lambda x: x[1]) if by_type else ("-", 0)
            st.metric("최다 카테고리", f"{top_type[0]}", f"+{top_type[1]}건")

        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown("**직원별**")
            for emp, cnt in sorted(by_employee.items(), key=lambda x: -x[1]):
                st.markdown(f"- {emp}: **{cnt}**건")
        with ec2:
            st.markdown("**카테고리별**")
            for tp, cnt in sorted(by_type.items(), key=lambda x: -x[1]):
                st.markdown(f"- {tp}: **{cnt}**건")
    else:
        st.info("아직 학습 데이터가 없습니다. 위에서 첫 시나리오를 만들어보세요!")
except Exception as e:
    st.caption(f"(통계 조회 실패: {e})")


# ────────────────────────────────────────────────────────────
# 개발 메모
# ────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🔧 개발/운영 메모 (관리자)"):
    st.markdown(
        "**현재 단계**: Phase 1 — 학습 데이터 수집 (~2026-06)  \n"
        "**저장 위치**: Supabase `chat_logs` 테이블 (운영)  \n"
        "**다음 단계 (Phase 2)**:  \n"
        "- 누적 데이터에서 자주 묻는 질문 그룹화 → FAQ 자동 추출  \n"
        "- Claude API + RAG 로 답변 자동 생성  \n"
        "- 직원 답변 시간 단축, 야간 자동 응대  \n"
        "**Phase 3 (라이브)**: 외부 손님 실 사용, 직원 부재 시간 자동 응대"
    )
    st.caption(f"세션 ID: `{st.session_state.session_id}` · 현재 직원: {employee} ({role})")
