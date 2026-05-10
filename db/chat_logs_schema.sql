-- ============================================================
-- 고객센터 챗봇 — 대화 로그 + 분석용 메타
-- 사용:
--   1. Supabase 대시보드 → SQL Editor
--   2. 이 파일 내용 붙여넣기 + Run
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_logs (
    id              BIGSERIAL PRIMARY KEY,
    session_id      VARCHAR(50) NOT NULL,                -- 같은 사용자 한 번 방문
    "timestamp"     TIMESTAMPTZ DEFAULT NOW(),
    role            VARCHAR(20) NOT NULL,                -- 'user' | 'assistant' | 'system'
    message         TEXT NOT NULL,
    is_after_hours  BOOLEAN,                              -- 영업외(18-9) 여부

    -- 사용자 식별 (옵션)
    customer_email  VARCHAR(255),
    customer_company VARCHAR(100),

    -- 분석용 메타 (LLM 사후 분류)
    intent_category VARCHAR(50),                          -- '견적' | '납기' | '대체품' | '결제' | '클레임' | '기타'
    sentiment       VARCHAR(20),                          -- 'positive' | 'neutral' | 'negative'

    -- 사람 후속 조치
    needs_human_followup BOOLEAN DEFAULT FALSE,
    followed_up_at  TIMESTAMPTZ,
    followed_up_by  VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_logs("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_chat_followup ON chat_logs(needs_human_followup) WHERE needs_human_followup = TRUE;
CREATE INDEX IF NOT EXISTS idx_chat_after_hours ON chat_logs(is_after_hours, "timestamp" DESC);

-- RLS (시험 단계: 익명도 INSERT 가능, SELECT은 관리자만)
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS chat_logs_anon_insert ON chat_logs;
CREATE POLICY chat_logs_anon_insert ON chat_logs
    FOR INSERT TO anon
    WITH CHECK (TRUE);

DROP POLICY IF EXISTS chat_logs_admin_select ON chat_logs;
CREATE POLICY chat_logs_admin_select ON chat_logs
    FOR SELECT TO authenticated
    USING (TRUE);

COMMENT ON TABLE chat_logs IS 'WI MRO 포털 고객센터 챗봇 대화 로그. AI 학습 데이터 + 사람 후속조치 추적';
