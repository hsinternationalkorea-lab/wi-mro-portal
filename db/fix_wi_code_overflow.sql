-- =====================================================================
-- WI 품번 오버플로우 패치
-- 문제: WH-O-9999, WH-T-9999 꽉 참 → 트리거가 WH-O-1000(중복) 반환
--       → 모든 신규 INSERT 가 HTTP 409 duplicate key 로 실패
-- 해결: 5자리 이상 자동 지원 + 충돌 시 재시도 LOOP + CHAR(1) 공백 패딩 제거
-- =====================================================================

CREATE OR REPLACE FUNCTION generate_wi_code(cat_code VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    next_num   INTEGER;
    new_code   VARCHAR;
    pad_len    INTEGER;
    attempts   INTEGER := 0;
    cat_clean  VARCHAR;
    prefix     VARCHAR;
    suffix_pos INTEGER;
BEGIN
    cat_clean  := TRIM(cat_code);
    prefix     := 'WH-' || cat_clean || '-';
    suffix_pos := LENGTH(prefix) + 1;

    LOOP
        attempts := attempts + 1;
        IF attempts > 50 THEN
            RAISE EXCEPTION 'WI code generation failed after 50 attempts for cat=%', cat_clean;
        END IF;

        -- prefix 로 미리 필터 → suffix 만 정수 변환
        SELECT COALESCE(MAX(CAST(SUBSTRING(wi_code FROM suffix_pos) AS INTEGER)), 0) + 1
        INTO next_num
        FROM products
        WHERE wi_code LIKE prefix || '%'
          AND SUBSTRING(wi_code FROM suffix_pos) ~ '^\d+$';

        -- 4자리 미만이면 0-pad, 9999 초과는 자릿수 자동 증가
        pad_len  := GREATEST(4, LENGTH(next_num::text));
        new_code := prefix || LPAD(next_num::text, pad_len, '0');

        -- 동시 INSERT 충돌 대응
        IF NOT EXISTS (SELECT 1 FROM products WHERE wi_code = new_code) THEN
            RETURN new_code;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- 검증 — 실행 결과 확인용
SELECT generate_wi_code('O') AS next_O,   -- 기대: WH-O-10000
       generate_wi_code('T') AS next_T,   -- 기대: WH-T-10000
       generate_wi_code('L') AS next_L,   -- 기대: WH-L-4970
       generate_wi_code('M') AS next_M;   -- 기대: WH-M-0039
