-- =====================================================================
-- WI MRO Catalog Portal — DB Schema v1
-- PostgreSQL 15+ (Supabase 호환)
-- =====================================================================
-- 핵심 컨셉: 카탈로그 매개자 (Catalog Broker)
--   - 우리 직거래 100 SKU + 외부 크롤링 수만 SKU
--   - 검색 → 노출 → 발주 → 우리가 공급사에서 조달
-- =====================================================================

-- 확장 활성화
CREATE EXTENSION IF NOT EXISTS pg_trgm;        -- 한국어 풀텍스트 fuzzy
CREATE EXTENSION IF NOT EXISTS vector;          -- pgvector (AI 임베딩)
CREATE EXTENSION IF NOT EXISTS unaccent;        -- 악센트 제거


-- =====================================================================
-- 1. 카테고리 (우리 분류 체계 - SOP)
-- =====================================================================
CREATE TABLE categories (
    code             CHAR(1) PRIMARY KEY,        -- S/C/T/M/P/E/L/F/O
    name_ko          VARCHAR(50) NOT NULL,
    name_en          VARCHAR(50) NOT NULL,
    priority         INTEGER NOT NULL,            -- M→F→L→C→S→E→P→T→O
    margin_pct       DECIMAL(4,2) NOT NULL,       -- 카테고리별 기본 마진
    description      TEXT
);

INSERT INTO categories VALUES
    ('M', '의료구급', 'Medical',          1, 25.0, '의료·구급 용품'),
    ('F', '체결부품', 'Fasteners',        2, 18.0, '볼트·너트·체결류'),
    ('L', '계측연구', 'Laboratory',       3, 22.0, '계측기·실험실 용품'),
    ('C', '크린용품', 'Cleanroom',        4, 20.0, '크린룸·정전기 방지'),
    ('S', '안전용품', 'Safety',           5, 25.0, '안전모·장갑·PPE'),
    ('E', '전기조명', 'Electrical',       6, 15.0, '전기·조명·전자부품'),
    ('P', '포장물류', 'Packaging',        7, 18.0, '포장·물류·창고용품'),
    ('T', '공구류',   'Tools',            8, 22.0, '수공구·전동공구'),
    ('O', '사무일반', 'Office',           9, 20.0, '사무용품·기타');


-- =====================================================================
-- 2. 데이터 소스 (출처 정보)
-- =====================================================================
CREATE TABLE sources (
    code             VARCHAR(20) PRIMARY KEY,    -- 'cretec', 'subone', 'mouser', ...
    name_ko          VARCHAR(50),
    type             VARCHAR(20),                 -- 'crawl' | 'api' | 'manual'
    base_url         VARCHAR(255),
    is_authoritative BOOLEAN DEFAULT FALSE,       -- 우리 직거래 마스터인가
    requires_login   BOOLEAN DEFAULT FALSE,
    crawl_delay_sec  INTEGER DEFAULT 5
);

INSERT INTO sources VALUES
    ('wi_master', 'WI 자체 카탈로그',  'manual', NULL, TRUE, FALSE, 0),
    ('cretec',    '크레텍',           'crawl',  'https://www.cretec.kr',  FALSE, TRUE, 20),
    ('subone',    '서브원',           'crawl',  'https://www.subone.co.kr', FALSE, TRUE, 20),
    ('mouser',    'Mouser',           'api',    'https://api.mouser.com', FALSE, FALSE, 2),
    ('digikey',   'Digi-Key',         'api',    'https://api.digikey.com', FALSE, FALSE, 2),
    ('naver',     '네이버 쇼핑',       'api',    'https://openapi.naver.com', FALSE, FALSE, 1),
    ('alibaba',   '알리바바',          'api',    'https://gw.api.alibaba.com', FALSE, FALSE, 2),
    ('g2b',       '조달청 나라장터',    'api',    'https://apis.data.go.kr', FALSE, FALSE, 1);


-- =====================================================================
-- 3. 제품 카탈로그 (코어 테이블)
-- =====================================================================
CREATE TABLE products (
    -- 식별자
    id                  BIGSERIAL PRIMARY KEY,
    wi_code             VARCHAR(20) UNIQUE,         -- WH-{Cat}-{NNNN} 또는 외부소스+ID

    -- 출처
    source_code         VARCHAR(20) NOT NULL REFERENCES sources(code),
    source_product_id   VARCHAR(100),                -- 출처 측 고유 ID
    source_url          VARCHAR(500),
    UNIQUE(source_code, source_product_id),

    -- 분류
    category_code       CHAR(1) REFERENCES categories(code),
    sub_category        VARCHAR(100),

    -- 표시 정보
    name_ko             VARCHAR(255),
    name_en             VARCHAR(255),
    spec                TEXT,
    model_no            VARCHAR(100),
    manufacturer        VARCHAR(100),
    manufacturer_pn     VARCHAR(100),                 -- 제조사 부품번호

    -- 검색용
    search_keywords     TEXT,                         -- pg_trgm 인덱스 대상
    name_embedding      VECTOR(384),                  -- 한국어 임베딩 (sentence-transformers)

    -- 이미지 (저장 X, hot-link)
    image_urls          TEXT[],                       -- 원본 URL 배열
    primary_image_url   VARCHAR(500),                 -- 대표 이미지
    image_hash          VARCHAR(64),                  -- perceptual hash (중복 검출)
    image_embedding     VECTOR(512),                  -- CLIP 임베딩 (이미지 검색)

    -- 가격 (3단계)
    cost_price          DECIMAL(12,2),                -- 원가 (대리점가, 비공개)
    list_price          DECIMAL(12,2),                -- 표시가 (cost × margin)
    margin_pct          DECIMAL(4,2),                 -- 적용 마진율
    currency            CHAR(3) DEFAULT 'KRW',
    price_unit          VARCHAR(20),                  -- EA, BOX, M, KG ...
    pack_size           INTEGER DEFAULT 1,            -- 1박스에 몇 개 등

    -- 재고/납기
    stock_status        VARCHAR(20),                  -- 'in_stock'|'low'|'out'|'unknown'
    stock_qty           INTEGER,
    lead_time_days      INTEGER,
    source_country      CHAR(2) DEFAULT 'KR',

    -- 메타
    is_directly_sold    BOOLEAN DEFAULT FALSE,        -- TRUE = WI 직거래 100 SKU
    is_published        BOOLEAN DEFAULT FALSE,        -- 포털 노출 여부
    quality_score       DECIMAL(3,2) DEFAULT 0.5,     -- 데이터 신뢰도 0~1
    last_crawled_at     TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_products_search ON products USING GIN (search_keywords gin_trgm_ops);
CREATE INDEX idx_products_name_emb ON products USING ivfflat (name_embedding vector_cosine_ops);
CREATE INDEX idx_products_image_emb ON products USING ivfflat (image_embedding vector_cosine_ops);
CREATE INDEX idx_products_category ON products(category_code) WHERE is_published;
CREATE INDEX idx_products_source ON products(source_code);
CREATE INDEX idx_products_directly_sold ON products(is_directly_sold) WHERE is_directly_sold;


-- =====================================================================
-- 4. 가격 시계열
-- =====================================================================
CREATE TABLE price_history (
    id              BIGSERIAL PRIMARY KEY,
    product_id      BIGINT REFERENCES products(id) ON DELETE CASCADE,
    cost_price      DECIMAL(12,2),
    source_price    DECIMAL(12,2),
    list_price      DECIMAL(12,2),
    stock_status    VARCHAR(20),
    observed_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_price_history_product ON price_history(product_id, observed_at DESC);


-- =====================================================================
-- 5. 제품 별칭 (중복 SKU 매칭)
-- =====================================================================
-- 같은 제품을 여러 출처에서 가져왔을 때 매핑
CREATE TABLE product_aliases (
    id                  BIGSERIAL PRIMARY KEY,
    primary_product_id  BIGINT REFERENCES products(id) ON DELETE CASCADE,
    alias_product_id    BIGINT REFERENCES products(id) ON DELETE CASCADE,
    similarity_score    DECIMAL(4,3),                 -- 0~1
    matching_method     VARCHAR(50),                  -- 'manual'|'name_text'|'image_clip'|'mfr_pn'
    verified_by_human   BOOLEAN DEFAULT FALSE,
    verified_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(primary_product_id, alias_product_id)
);


-- =====================================================================
-- 6. 크롤링 로그 (작업 추적)
-- =====================================================================
CREATE TABLE crawl_runs (
    id              BIGSERIAL PRIMARY KEY,
    source_code     VARCHAR(20) REFERENCES sources(code),
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(20),                      -- 'running'|'success'|'failed'
    products_added  INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    errors          JSONB,
    notes           TEXT
);


-- =====================================================================
-- 7. 검색 쿼리 로그 (운영 분석용)
-- =====================================================================
CREATE TABLE search_queries (
    id              BIGSERIAL PRIMARY KEY,
    query_text      TEXT,
    user_id         UUID,                             -- Supabase Auth 연동
    result_count    INTEGER,
    clicked_product_id BIGINT REFERENCES products(id),
    searched_at     TIMESTAMPTZ DEFAULT NOW()
);


-- =====================================================================
-- 8. 트리거 — updated_at 자동 갱신
-- =====================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- =====================================================================
-- 9. RLS (Row Level Security) — 향후 고객 인증 시
-- =====================================================================
-- 일단 비활성. 검색 UI 만든 후 활성화.
-- ALTER TABLE products ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "공개 제품만 조회" ON products FOR SELECT USING (is_published);


-- =====================================================================
-- 끝
-- =====================================================================
