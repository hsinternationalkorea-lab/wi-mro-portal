-- =====================================================================
-- 견적 요청 테이블 (장바구니 → 일괄 견적)
-- =====================================================================

CREATE TABLE IF NOT EXISTS quote_requests (
    id              BIGSERIAL PRIMARY KEY,
    request_no      VARCHAR(20) UNIQUE,           -- 'QR-260504-001'

    -- 고객 정보
    company         VARCHAR(100) NOT NULL,
    contact_name    VARCHAR(50) NOT NULL,
    email           VARCHAR(100) NOT NULL,
    phone           VARCHAR(30),
    business_no     VARCHAR(20),                  -- 사업자등록번호

    -- 요청 상세
    note            TEXT,
    delivery_request VARCHAR(100),                -- 희망 납기

    -- 상태
    status          VARCHAR(20) DEFAULT 'pending', -- pending|reviewed|quoted|ordered|cancelled
    assigned_to     VARCHAR(50),                  -- WI 담당자

    -- 시점
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ,
    quoted_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_qr_status ON quote_requests(status);
CREATE INDEX IF NOT EXISTS idx_qr_created ON quote_requests(created_at DESC);


CREATE TABLE IF NOT EXISTS quote_request_items (
    id              BIGSERIAL PRIMARY KEY,
    request_id      BIGINT REFERENCES quote_requests(id) ON DELETE CASCADE,
    product_id      BIGINT REFERENCES products(id),

    -- 스냅샷 (제품이 나중에 바뀌어도 견적은 그대로)
    wi_code         VARCHAR(20),
    name_ko         VARCHAR(255),
    spec            TEXT,
    manufacturer    VARCHAR(100),
    primary_image_url VARCHAR(500),
    list_price      DECIMAL(12,2),                -- 표시가 시점
    cost_price      DECIMAL(12,2),                -- 원가 시점 (admin)
    price_unit      VARCHAR(20),

    -- 사용자 입력
    quantity        INTEGER NOT NULL DEFAULT 1,
    line_note       TEXT,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qri_request ON quote_request_items(request_id);


-- 자동 채번: QR-YYMMDD-NNN
CREATE OR REPLACE FUNCTION generate_quote_request_no()
RETURNS TRIGGER AS $$
DECLARE
    today_prefix VARCHAR;
    next_num INTEGER;
BEGIN
    today_prefix := 'QR-' || TO_CHAR(NOW(), 'YYMMDD') || '-';
    SELECT COALESCE(MAX(
        CASE
            WHEN request_no LIKE today_prefix || '%'
            THEN CAST(SUBSTRING(request_no FROM LENGTH(today_prefix) + 1) AS INTEGER)
            ELSE 0
        END
    ), 0) + 1
    INTO next_num
    FROM quote_requests;

    NEW.request_no := today_prefix || LPAD(next_num::text, 3, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_quote_request_no ON quote_requests;
CREATE TRIGGER trg_quote_request_no
    BEFORE INSERT ON quote_requests
    FOR EACH ROW
    WHEN (NEW.request_no IS NULL OR NEW.request_no = '')
    EXECUTE FUNCTION generate_quote_request_no();


SELECT '견적요청 테이블 설치 완료' as status;
