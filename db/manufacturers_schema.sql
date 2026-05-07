-- =====================================================================
-- 제조사 마스터 테이블 (공급망 인텔리전스)
-- 목표: 유통사 → 제조사 직거래로 마진 극대화
-- =====================================================================

CREATE TABLE IF NOT EXISTS manufacturers (
    id                  BIGSERIAL PRIMARY KEY,

    -- 식별
    name_normalized     VARCHAR(100) UNIQUE NOT NULL,  -- 소문자·공백제거 (매칭키)
    name_en             VARCHAR(100),                   -- 영문명
    name_ko             VARCHAR(100),                   -- 한글명

    -- 위치
    country             CHAR(2),                        -- ISO 코드 KR/JP/US/DE/CN
    headquarters_city   VARCHAR(50),

    -- 연락처 (수기 입력 또는 자동 검색)
    website             VARCHAR(255),
    sales_email         VARCHAR(100),
    sales_phone         VARCHAR(50),

    -- 비즈니스 인텔리전스
    is_direct_partner       BOOLEAN DEFAULT FALSE,      -- 직거래 중?
    direct_cost_known       BOOLEAN DEFAULT FALSE,      -- 직접 cost 데이터 보유?
    distribution_priority   INTEGER DEFAULT 0,          -- 0=normal, 1=high, 2=critical
    competitor_korea        VARCHAR(255),               -- 한국 경쟁 대리점 (있으면)

    -- 메타
    sku_count           INTEGER DEFAULT 0,              -- 우리 DB에 SKU 수 (트리거로 자동)
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mfr_country ON manufacturers(country);
CREATE INDEX IF NOT EXISTS idx_mfr_partner ON manufacturers(is_direct_partner) WHERE is_direct_partner;
CREATE INDEX IF NOT EXISTS idx_mfr_sku_count ON manufacturers(sku_count DESC);


-- products에 manufacturer_id FK 추가
ALTER TABLE products ADD COLUMN IF NOT EXISTS manufacturer_id BIGINT REFERENCES manufacturers(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_products_mfr ON products(manufacturer_id) WHERE manufacturer_id IS NOT NULL;

-- 정규화 함수 (이름 → 매칭키)
CREATE OR REPLACE FUNCTION normalize_mfr_name(raw TEXT)
RETURNS VARCHAR AS $$
BEGIN
    IF raw IS NULL OR raw = '' THEN RETURN NULL; END IF;
    -- 공백·특수문자 제거, 소문자
    RETURN LOWER(REGEXP_REPLACE(raw, '[^\w가-힣]', '', 'g'));
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- products 갱신 시 manufacturer_id 자동 연결 (manufacturer text → manufacturer_id)
CREATE OR REPLACE FUNCTION auto_link_manufacturer()
RETURNS TRIGGER AS $$
DECLARE
    norm VARCHAR;
    mfr_id BIGINT;
BEGIN
    IF NEW.manufacturer IS NULL OR NEW.manufacturer = '' THEN
        NEW.manufacturer_id := NULL;
        RETURN NEW;
    END IF;

    norm := normalize_mfr_name(NEW.manufacturer);
    IF norm IS NULL THEN RETURN NEW; END IF;

    -- 기존 제조사 찾기
    SELECT id INTO mfr_id FROM manufacturers WHERE name_normalized = norm;

    -- 없으면 자동 생성
    IF mfr_id IS NULL THEN
        INSERT INTO manufacturers (name_normalized, name_en, name_ko)
        VALUES (
            norm,
            -- 영문이면 name_en, 한글이면 name_ko로 저장
            CASE WHEN NEW.manufacturer ~* '^[A-Za-z0-9 .,&\-/()]+$' THEN NEW.manufacturer ELSE NULL END,
            CASE WHEN NEW.manufacturer ~* '^[A-Za-z0-9 .,&\-/()]+$' THEN NULL ELSE NEW.manufacturer END
        )
        ON CONFLICT (name_normalized) DO UPDATE SET updated_at = NOW()
        RETURNING id INTO mfr_id;
    END IF;

    NEW.manufacturer_id := mfr_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auto_link_mfr ON products;
CREATE TRIGGER trg_auto_link_mfr
    BEFORE INSERT OR UPDATE OF manufacturer ON products
    FOR EACH ROW
    EXECUTE FUNCTION auto_link_manufacturer();


-- sku_count 자동 갱신 (제조사별 SKU 수)
CREATE OR REPLACE FUNCTION refresh_mfr_sku_count()
RETURNS VOID AS $$
BEGIN
    UPDATE manufacturers m
    SET sku_count = (
        SELECT COUNT(*) FROM products p WHERE p.manufacturer_id = m.id
    ),
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql;


SELECT '제조사 마스터 테이블 설치 완료' as status;
