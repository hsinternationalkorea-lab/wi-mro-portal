-- =====================================================================
-- 원가 미확정 라벨 자동 부여
-- 정책: cost = list (마진 0%) 또는 NULL 인 SKU는 "원가 미확정" 표시
-- 자동 마진 적용 X — 솔직한 라벨이 직원/고객 신뢰
-- =====================================================================

-- 1. price_status 컬럼 추가
ALTER TABLE products ADD COLUMN IF NOT EXISTS price_status VARCHAR(20);

-- 2. 기존 데이터 일괄 분류
UPDATE products SET price_status =
  CASE
    WHEN cost_price IS NULL OR list_price IS NULL THEN 'no_price'
    WHEN cost_price = 0 OR list_price = 0 THEN 'no_price'
    WHEN cost_price = list_price THEN 'cost_unconfirmed'
    WHEN list_price > cost_price THEN 'priced'
    ELSE 'invalid'
  END;

-- 3. 트리거 함수
CREATE OR REPLACE FUNCTION update_price_status()
RETURNS TRIGGER AS $$
BEGIN
  NEW.price_status :=
    CASE
      WHEN NEW.cost_price IS NULL OR NEW.list_price IS NULL THEN 'no_price'
      WHEN NEW.cost_price = 0 OR NEW.list_price = 0 THEN 'no_price'
      WHEN NEW.cost_price = NEW.list_price THEN 'cost_unconfirmed'
      WHEN NEW.list_price > NEW.cost_price THEN 'priced'
      ELSE 'invalid'
    END;

  -- 마진 % 자동 계산 (priced 인 경우만)
  IF NEW.price_status = 'priced' THEN
    NEW.margin_pct := ROUND(((NEW.list_price - NEW.cost_price) / NEW.list_price * 100)::numeric, 1);
  ELSE
    NEW.margin_pct := 0;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. 트리거 등록 (INSERT + UPDATE)
DROP TRIGGER IF EXISTS trg_price_status ON products;
CREATE TRIGGER trg_price_status BEFORE INSERT OR UPDATE OF cost_price, list_price ON products
FOR EACH ROW EXECUTE FUNCTION update_price_status();

-- 5. 분포 확인
SELECT price_status, COUNT(*) AS cnt
FROM products
GROUP BY price_status
ORDER BY cnt DESC;
