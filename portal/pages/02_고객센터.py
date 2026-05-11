# -*- coding: utf-8 -*-
"""
고객센터 — 직원 09:00~18:00 / AI 18:00~09:00 응대
- 케이스 스터디 학습 전 단계: 대화 로그 수집
- 학습 후: RAG 기반 자동 응답
"""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from supabase_client import SupabaseClient

st.set_page_config(
    page_title="WI · 고객센터",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 시간대 — KST 기준
# ============================================================
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
hour = now.hour
is_after_hours = hour >= 18 or hour < 9

# ============================================================
# 헤더
# ============================================================
st.title("💬 고객센터")
st.caption(f"현재 시각 (KST): {now.strftime('%Y-%m-%d %H:%M')} · {'🌙 AI 응대 시간' if is_after_hours else '🟢 직원 응대 시간'}")

# 시간대 안내
if is_after_hours:
    st.warning(
        "🌙 **현재 직원 부재 시간** (18:00 ~ 다음날 09:00)입니다.\n\n"
        "AI가 대신 답변드리지만, **현재는 학습 중**이라 정확도가 낮을 수 있습니다. "
        "남기신 문의는 자동 저장되어 다음날 직원이 검토 후 답변드립니다."
    )
else:
    st.success(
        "🟢 **직원 응대 시간** (09:00 ~ 18:00)입니다.\n\n"
        "빠른 응대를 위해 메일 또는 전화로 직접 연락해주세요. "
        "이 챗봇은 학습 데이터 수집 중이라 응답이 느릴 수 있습니다."
    )

# ============================================================
# 사이드바 — 빠른 연락
# ============================================================
with st.sidebar:
    st.markdown("### 운영 시간")
    st.markdown(
        "- 🟢 **직원 응대**: 09:00 ~ 18:00 (KST)\n"
        "- 🌙 **AI 응대**: 18:00 ~ 09:00 (KST, 학습 중)"
    )
    st.markdown("---")
    st.markdown("### 빠른 연락")
    st.markdown(
        "- ✉️ [sale@wholesale-k.com](mailto:sale@wholesale-k.com)\n"
        "- ✉️ [yjyoon@wholesale-k.com](mailto:yjyoon@wholesale-k.com)\n"
        "- 🌐 [https://portal.koreaene.co.kr](https://portal.koreaene.co.kr)"
    )
    st.markdown("---")
    st.markdown("### 자주 묻는 질문")
    st.markdown(
        "- 견적 요청 방법\n"
        "- 납기 문의\n"
        "- 대체품 문의\n"
        "- 결제 조건"
    )
    st.caption("(FAQ는 학습 데이터 모이면 자동 채워집니다)")

# ============================================================
# 챗봇
# ============================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:12]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요, ㈜홀세일인더스트리 고객센터입니다. 무엇을 도와드릴까요? "
                "(현재는 학습 중이라 응답이 제한적입니다.)"
            ),
        }
    ]

# 이력 표시
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력
if prompt := st.chat_input("문의 내용을 입력하세요"):
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 임시 응답 (학습 전 placeholder)
    if is_after_hours:
        response = (
            "문의 내용을 잘 받았습니다. **AI가 아직 학습 중**이라 정확한 답변이 어렵습니다.\n\n"
            "남기신 내용은 저장되어 **내일 오전 9시 이후 직원이 검토 후 답변**드리겠습니다.\n\n"
            "급하신 경우 메일(sale@wholesale-k.com)로 연락 부탁드립니다."
        )
    else:
        response = (
            "직원 응대 시간입니다. 더 빠른 응답을 위해 **메일 또는 전화**로 직접 연락 부탁드립니다.\n\n"
            "이 챗봇은 학습 데이터 수집 중이라 응답이 제한적입니다."
        )

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

    # 대화 로그 저장 (Supabase chat_logs 테이블 — 다음 단계에서 스키마 추가 후 활성화)
    try:
        client = SupabaseClient()
        client.insert("chat_logs", [
            {
                "session_id": st.session_state.session_id,
                "role": "user",
                "message": prompt,
                "is_after_hours": is_after_hours,
            },
            {
                "session_id": st.session_state.session_id,
                "role": "assistant",
                "message": response,
                "is_after_hours": is_after_hours,
            },
        ])
    except Exception:
        # chat_logs 테이블 없으면 조용히 패스 (다음 단계에서 추가)
        pass

# ============================================================
# 하단 안내 (개발 메모)
# ============================================================
st.markdown("---")
st.caption(
    "🔧 **개발 메모**: 이 챗봇은 케이스 스터디 학습 전 단계입니다. "
    "현재 모든 대화는 저장되어 학습 데이터로 사용됩니다. "
    "다음 단계: 이메일 이력 분석 → FAQ 자동 추출 → RAG 응답."
)
