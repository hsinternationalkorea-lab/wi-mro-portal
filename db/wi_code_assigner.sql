-- =====================================================================
-- WI 품번 자동 부여 시스템
-- 모든 신규 SKU는 WI 품번을 자동 발급받고 우리 포털에 노출됨
-- =====================================================================

-- 카테고리별 다음 번호 추적 (이미 시드된 100 SKU 이후부터)
CREATE OR REPLACE FUNCTION generate_wi_code(cat_code CHAR(1))
RETURNS VARCHAR AS $$
DECLARE
    next_num INTEGER;
    new_code VARCHAR;
BEGIN
    -- 해당 카테고리의 가장 큰 번호 찾기
    SELECT COALESCE(MAX(
        CASE
            WHEN wi_code ~ ('^WH-' || cat_code || '-\d+$')
            THEN CAST(SUBSTRING(wi_code FROM 6) AS INTEGER)
            ELSE 0
        END
    ), 0) + 1
    INTO next_num
    FROM products;

    new_code := 'WH-' || cat_code || '-' || LPAD(next_num::text, 4, '0');
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;


-- 크레텍 카테고리명 → 우리 카테고리 코드 매핑
CREATE OR REPLACE FUNCTION map_cretec_to_wi_category(cretec_label TEXT)
RETURNS CHAR(1) AS $$
BEGIN
    -- 우선순위: M → F → L → C → S → E → P → T → O
    cretec_label := COALESCE(cretec_label, '');

    -- M (의료) - 거의 없음, 그러나 안전관련 일부
    IF cretec_label ~* '의료|구급|응급' THEN RETURN 'M';

    -- F (체결부품) - 볼트/너트
    ELSIF cretec_label ~* '볼트|너트|와셔|체결|체인|훅|샤클' THEN RETURN 'F';

    -- L (계측) - 측정기/계측
    ELSIF cretec_label ~* '측정|계측|측량|광학|온도|압력|수평|레이저|현미경|돋보기|저울|토크|마이크로미터|버니어' THEN RETURN 'L';

    -- C (크린룸) - 크린/방진/장갑/와이퍼
    ELSIF cretec_label ~* '크린|클린|방진|와이퍼|라텍스|니트릴|위생|일회용|장갑(?!솜)' THEN RETURN 'C';

    -- S (안전) - 안전모/보안경/마스크/PPE
    ELSIF cretec_label ~* '안전|보호|마스크|보안경|헬멧|안전모|방독|방진(?!복)|PPE|소화|구조|사다리|밧줄|로프' THEN RETURN 'S';

    -- E (전기) - 전기/조명/배선/전선/배터리
    ELSIF cretec_label ~* '전기|전자|배선|전선|케이블(?!타이)|램프|조명|LED|전구|배터리|전동|충전|어댑터|콘센트|소켓|연결' THEN RETURN 'E';

    -- P (포장물류) - 포장/박스/노끈/캐비닛
    ELSIF cretec_label ~* '포장|박스|상자|노끈|밴드|랩|비닐|테이프(?!공구)|캐비넷|선반|적재|운반|대차|카트|밧줄|결속' THEN RETURN 'P';

    -- T (공구) - 공구/렌치/드라이버/스패너/펜치/니퍼/...
    ELSIF cretec_label ~* '공구|렌치|드라이버|스패너|망치|드릴|커터|니퍼|펜치|플라이어|톱|줄|가위|칼|스크류|샌더|그라인더|연마|절삭|용접|핸드툴|에어툴' THEN RETURN 'T';

    -- O (사무) - 기본값
    ELSE RETURN 'O';
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 자동 트리거: products INSERT 시 wi_code가 비어있으면 자동 생성
CREATE OR REPLACE FUNCTION auto_assign_wi_code()
RETURNS TRIGGER AS $$
DECLARE
    cat CHAR(1);
BEGIN
    -- wi_code가 이미 있으면 그대로 사용
    IF NEW.wi_code IS NOT NULL AND NEW.wi_code != '' THEN
        RETURN NEW;
    END IF;

    -- 카테고리 자동 매핑 (없으면 sub_category나 search_keywords로 추론)
    IF NEW.category_code IS NULL OR NEW.category_code = '' THEN
        NEW.category_code := map_cretec_to_wi_category(
            COALESCE(NEW.sub_category, '') || ' ' ||
            COALESCE(NEW.name_ko, '') || ' ' ||
            COALESCE(NEW.spec, '')
        );
    END IF;

    cat := NEW.category_code;
    NEW.wi_code := generate_wi_code(cat);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_auto_wi_code ON products;
CREATE TRIGGER trg_auto_wi_code
    BEFORE INSERT ON products
    FOR EACH ROW
    EXECUTE FUNCTION auto_assign_wi_code();


-- 검증
SELECT 'WI 품번 자동 부여 시스템 설치 완료' as status;
