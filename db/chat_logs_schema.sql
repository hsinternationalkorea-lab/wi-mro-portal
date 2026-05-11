-- ============================================================
-- chat_logs — 고객센터 챗봇 + 학습 데이터
-- 사용:
--   1. Supabase 대시보드 → SQL Editor
--   2. 이 파일 통째 붙여넣고 Run (idempotent — 여러 번 실행해도 안전)
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_logs (
    id              BIGSERIAL PRIMARY KEY,
    session_id      VARCHAR(50) NOT NULL,
    "timestamp"     TIMESTAMPTZ DEFAULT NOW(),
    role            VARCHAR(20) NOT NULL,                -- 'user' | 'assistant' | 'system' | 'admin_note'
    message         TEXT NOT NULL,
    is_after_hours  BOOLEAN,

    customer_email  VARCHAR(255),
    customer_company VARCHAR(100),

    intent_category VARCHAR(50),
    sentiment       VARCHAR(20),

    needs_human_followup BOOLEAN DEFAULT FALSE,
    followed_up_at  TIMESTAMPTZ,
    followed_up_by  VARCHAR(100)
);

-- ── 학습 모드용 컬럼 추가 (2026-05 시험가동) ──
ALTER TABLE chat_logs
    ADD COLUMN IF NOT EXISTS employee_name   TEXT,
    ADD COLUMN IF NOT EXISTS employee_role   TEXT,
    ADD COLUMN IF NOT EXISTS scenario_type   TEXT,
    ADD COLUMN IF NOT EXISTS difficulty      TEXT,
    ADD COLUMN IF NOT EXISTS tags            TEXT,
    ADD COLUMN IF NOT EXISTS internal_note   TEXT,
    ADD COLUMN IF NOT EXISTS is_simulated    BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS created_at      TIMESTAMPTZ DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_chat_session       ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_timestamp     ON chat_logs("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_chat_followup      ON chat_logs(needs_human_followup) WHERE needs_human_followup = TRUE;
CREATE INDEX IF NOT EXISTS idx_chat_after_hours   ON chat_logs(is_after_hours, "timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_chat_employee      ON chat_logs(employee_name);
CREATE INDEX IF NOT EXISTS idx_chat_scenario      ON chat_logs(scenario_type);
CREATE INDEX IF NOT EXISTS idx_chat_simulated     ON chat_logs(is_simulated);
CREATE INDEX IF NOT EXISTS idx_chat_created       ON chat_logs(created_at DESC);

-- ── RLS — 시험가동 단계: anon INSERT/SELECT 모두 허용 ──
-- (외부 차단은 portal 진입 가드로 처리, DB 측은 단순화)
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS chat_logs_anon_insert ON chat_logs;
CREATE POLICY chat_logs_anon_insert ON chat_logs
    FOR INSERT TO anon
    WITH CHECK (TRUE);

DROP POLICY IF EXISTS chat_logs_anon_select ON chat_logs;
CREATE POLICY chat_logs_anon_select ON chat_logs
    FOR SELECT TO anon
    USING (TRUE);

COMMENT ON TABLE chat_logs IS 'WI MRO 포털 고객센터 챗봇 + 학습 데이터 (Phase 1: 직원 시나리오 시뮬레이션 수집, Phase 2: AI 학습)';
