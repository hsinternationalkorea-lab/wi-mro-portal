-- ItemMaster 100 SKU → products 마이그레이션
-- Supabase SQL Editor에서 실행

INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0001', 'wi_master', 'WH-C-0001',
    'C', '크린룸라텍스 300mm (12") M(8mil)', 'M(8mil)',
    '크린룸라텍스 300mm (12") M(8mil) M(8mil) 크린용품',
    90000, 108000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0002', 'wi_master', 'WH-C-0002',
    'C', '크린 와이퍼', 'WW-2309',
    '크린 와이퍼 WW-2309 크린용품',
    107000, 128400, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0003', 'wi_master', 'WH-C-0003',
    'C', '헤어캡', '10g',
    '헤어캡 10g 크린용품',
    38, 46, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0004', 'wi_master', 'WH-C-0004',
    'C', '방진복 라운드형 원피스', '백색 2XLARGE 귀망사부착',
    '방진복 라운드형 원피스 백색 2XLARGE 귀망사부착 크린용품',
    21000, 25200, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0005', 'wi_master', 'WH-C-0005',
    'C', '방진복 라운드형 원피스', '백색 5XLARGE 귀망사부착',
    '방진복 라운드형 원피스 백색 5XLARGE 귀망사부착 크린용품',
    25000, 30000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0006', 'wi_master', 'WH-C-0006',
    'C', '방진화', '백색, 260mm',
    '방진화 백색, 260mm 크린용품',
    35000, 42000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0007', 'wi_master', 'WH-C-0007',
    'C', '방진화', '백색, 270mm',
    '방진화 백색, 270mm 크린용품',
    35000, 42000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0008', 'wi_master', 'WH-C-0008',
    'C', '방진화', '백색, 280mm',
    '방진화 백색, 280mm 크린용품',
    35000, 42000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-E-0001', 'wi_master', 'WH-E-0001',
    'E', '손전등', '배터리 3500mAh, 케이블 포함',
    '손전등 배터리 3500mAh, 케이블 포함 전기조명',
    28500, 32775, 15.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-E-0002', 'wi_master', 'WH-E-0002',
    'E', 'PHILIPS전구', 'BULB 12-100W E26 ND (W) 60*(H)108mm 12W 6500K(주광색)',
    'PHILIPS전구 BULB 12-100W E26 ND (W) 60*(H)108mm 12W 6500K(주광색) 전기조명',
    5000, 5750, 15.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-E-0003', 'wi_master', 'WH-E-0003',
    'E', 'FOCUS LED콘조명', 'E39 F-75W Φ103*(H)327mm 75W 6500K E39',
    'FOCUS LED콘조명 E39 F-75W Φ103*(H)327mm 75W 6500K E39 전기조명',
    31000, 35650, 15.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-E-0004', 'wi_master', 'WH-E-0004',
    'E', 'LED작업등', 'SWL-240RF/60*270*38mm',
    'LED작업등 SWL-240RF/60*270*38mm 전기조명',
    53700, 61755, 15.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-E-0005', 'wi_master', 'WH-E-0005',
    'E', '케이블 타이', '4.8 (W)4.8*(L)200mm NYLON 백색',
    '케이블 타이 4.8 (W)4.8*(L)200mm NYLON 백색 전기조명',
    14000, 16100, 15.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-F-0001', 'wi_master', 'WH-F-0001',
    'F', '렌치볼트', 'M5*(L)8mm SUS304',
    '렌치볼트 M5*(L)8mm SUS304 체결부품',
    30, 35, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-F-0002', 'wi_master', 'WH-F-0002',
    'F', '렌치볼트', 'M5*(L)12mm SUS304',
    '렌치볼트 M5*(L)12mm SUS304 체결부품',
    33, 39, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0001', 'wi_master', 'WH-L-0001',
    'L', 'Squeeze bottle nozzle cap', '3-6628-12',
    'Squeeze bottle nozzle cap 3-6628-12 계측연구',
    8000, 9760, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0002', 'wi_master', 'WH-L-0002',
    'L', '방폭 전자 저울', 'HV-15KCEP',
    '방폭 전자 저울 HV-15KCEP 계측연구',
    1460500, 1781810, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0003', 'wi_master', 'WH-L-0003',
    'L', '방폭 전자 저울', 'HV-60KCEP',
    '방폭 전자 저울 HV-60KCEP 계측연구',
    1575500, 1922110, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0004', 'wi_master', 'WH-L-0004',
    'L', '비방폭 전자 저울', 'SWII-30CW',
    '비방폭 전자 저울 SWII-30CW 계측연구',
    207000, 252540, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0005', 'wi_master', 'WH-L-0005',
    'L', '종이컵 디스펜서 단일홀더', '화이트',
    '종이컵 디스펜서 단일홀더 화이트 계측연구',
    11000, 13420, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0006', 'wi_master', 'WH-L-0006',
    'L', 'Gas Vent B Type 1L', '레드',
    'Gas Vent B Type 1L 레드 계측연구',
    11000, 13420, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0007', 'wi_master', 'WH-L-0007',
    'L', 'Gas Vent B Type 1L', '라이트블루',
    'Gas Vent B Type 1L 라이트블루 계측연구',
    11000, 13420, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0008', 'wi_master', 'WH-L-0008',
    'L', 'Gas Vent B Type 1L', '코발트블루',
    'Gas Vent B Type 1L 코발트블루 계측연구',
    11000, 13420, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0009', 'wi_master', 'WH-L-0009',
    'L', 'Gas Vent B Type 1L', '퍼플',
    'Gas Vent B Type 1L 퍼플 계측연구',
    11000, 13420, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0010', 'wi_master', 'WH-L-0010',
    'L', 'Gas Vent B Type 1L', '오렌지',
    'Gas Vent B Type 1L 오렌지 계측연구',
    11000, 13420, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0011', 'wi_master', 'WH-L-0011',
    'L', '1/2" SUS Tubing', 'T23-184-117(SUB102)',
    '1/2" SUS Tubing T23-184-117(SUB102) 계측연구',
    42000, 51240, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0012', 'wi_master', 'WH-L-0012',
    'L', '1/4" SUS Tubing', 'T23-184-096(SUB104)',
    '1/4" SUS Tubing T23-184-096(SUB104) 계측연구',
    25500, 31110, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0013', 'wi_master', 'WH-L-0013',
    'L', '드와플라스크 6L', '5-244-12(D-6001W)',
    '드와플라스크 6L 5-244-12(D-6001W) 계측연구',
    650000, 793000, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0014', 'wi_master', 'WH-L-0014',
    'L', 'BW Ultra Probe', 'GA-Prob1-1',
    'BW Ultra Probe GA-Prob1-1 계측연구',
    145000, 176900, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-L-0015', 'wi_master', 'WH-L-0015',
    'L', 'TYGON hose', '15M',
    'TYGON hose 15M 계측연구',
    130000, 158600, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0001', 'wi_master', 'WH-M-0001',
    'M', '그린 포비돈 스틱 스왑 일회용', NULL,
    '그린 포비돈 스틱 스왑 일회용  의료구급',
    13000, 16250, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0002', 'wi_master', 'WH-M-0002',
    'M', '3M 종이반창고 마이크로포 의료용 테이프', '화이트',
    '3M 종이반창고 마이크로포 의료용 테이프 화이트 의료구급',
    13000, 16250, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0003', 'wi_master', 'WH-M-0003',
    'M', '㈜수성 붕대 3inch', '7.5*190cm',
    '㈜수성 붕대 3inch 7.5*190cm 의료구급',
    12000, 15000, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0004', 'wi_master', 'WH-M-0004',
    'M', '의료용 핀셋', NULL,
    '의료용 핀셋  의료구급',
    1550, 1938, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0005', 'wi_master', 'WH-M-0005',
    'M', '의료용 가위', NULL,
    '의료용 가위  의료구급',
    4000, 5000, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0006', 'wi_master', 'WH-M-0006',
    'M', '트위스트 지혈대', NULL,
    '트위스트 지혈대  의료구급',
    12000, 15000, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-M-0007', 'wi_master', 'WH-M-0007',
    'M', '마데카솔', NULL,
    '마데카솔  의료구급',
    5150, 6438, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-O-0001', 'wi_master', 'WH-O-0001',
    'O', 'ISE MOUNT 클립 다목적 후크', 'Green',
    'ISE MOUNT 클립 다목적 후크 Green 사무일반',
    6000, 7200, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-O-0002', 'wi_master', 'WH-O-0002',
    'O', 'WS-452CP 4인치 (위어스)', '260, 270mm',
    'WS-452CP 4인치 (위어스) 260, 270mm 사무일반',
    70000, 84000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-O-0003', 'wi_master', 'WH-O-0003',
    'O', '와이어키링', '1.5*150mm',
    '와이어키링 1.5*150mm 사무일반',
    580, 696, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0001', 'wi_master', 'WH-P-0001',
    'P', '철제 캐비넷 1단 락커', 'Gray',
    '철제 캐비넷 1단 락커 Gray 포장물류',
    120000, 141600, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0002', 'wi_master', 'WH-P-0002',
    'P', '화신 책철 750책철', '70*57mm',
    '화신 책철 750책철 70*57mm 포장물류',
    4690, 5534, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0003', 'wi_master', 'WH-P-0003',
    'P', '제전 에어캡', 'PE 0.04mm 50cm 50M',
    '제전 에어캡 PE 0.04mm 50cm 50M 포장물류',
    48000, 56640, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0004', 'wi_master', 'WH-P-0004',
    'P', '사각 말통', '5L',
    '사각 말통 5L 포장물류',
    2600, 3068, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0005', 'wi_master', 'WH-P-0005',
    'P', '파이프 배관 보온 테이프', '2M Gray',
    '파이프 배관 보온 테이프 2M Gray 포장물류',
    3850, 4543, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0006', 'wi_master', 'WH-P-0006',
    'P', '포장 비닐', '720*1200*0.06',
    '포장 비닐 720*1200*0.06 포장물류',
    370, 437, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0007', 'wi_master', 'WH-P-0007',
    'P', '포장 비닐', '500*800*0.06',
    '포장 비닐 500*800*0.06 포장물류',
    300, 354, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0008', 'wi_master', 'WH-P-0008',
    'P', '스트레치필름', '15mic 500mm 350M',
    '스트레치필름 15mic 500mm 350M 포장물류',
    44000, 51920, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0009', 'wi_master', 'WH-P-0009',
    'P', 'PP밴드', '(t)1mm*(W)18mm',
    'PP밴드 (t)1mm*(W)18mm 포장물류',
    17000, 20060, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0010', 'wi_master', 'WH-P-0010',
    'P', '에어캡', 'PE 0.04mm 100cm 50M',
    '에어캡 PE 0.04mm 100cm 50M 포장물류',
    28000, 33040, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0011', 'wi_master', 'WH-P-0011',
    'P', '제전 에어캡', 'PE 0.04mm 100cm 50M',
    '제전 에어캡 PE 0.04mm 100cm 50M 포장물류',
    48000, 56640, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0012', 'wi_master', 'WH-P-0012',
    'P', '논슬립테이프', '3M (W)50mm*(L)15m',
    '논슬립테이프 3M (W)50mm*(L)15m 포장물류',
    70000, 82600, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0013', 'wi_master', 'WH-P-0013',
    'P', '열 수축필름', '180mm',
    '열 수축필름 180mm 포장물류',
    75000, 88500, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0014', 'wi_master', 'WH-P-0014',
    'P', '(주)태진이엔지 부품보관함', 'EPB52C-2D',
    '(주)태진이엔지 부품보관함 EPB52C-2D 포장물류',
    1210000, 1427800, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0015', 'wi_master', 'WH-P-0015',
    'P', '(주)록희 적재대 캐비닛형,고정형선반', 'RCS-C5R',
    '(주)록희 적재대 캐비닛형,고정형선반 RCS-C5R 포장물류',
    790000, 932200, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-P-0016', 'wi_master', 'WH-P-0016',
    'P', '카파맥스 서류받침', '42300(K20103) 3단',
    '카파맥스 서류받침 42300(K20103) 3단 포장물류',
    17000, 20060, 18.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0001', 'wi_master', 'WH-S-0001',
    'S', '3M 안전블록', '나노락라이트 싱글(3101753) 1.5m',
    '3M 안전블록 나노락라이트 싱글(3101753) 1.5m 안전용품',
    210000, 262500, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0002', 'wi_master', 'WH-S-0002',
    'S', 'DAILOVE H200', 'S, L, LL',
    'DAILOVE H200 S, L, LL 안전용품',
    127500, 159375, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0003', 'wi_master', 'WH-S-0003',
    'S', '세이프티조거 카도르 ESD 다이얼 안전화 4인치', '260, 270mm',
    '세이프티조거 카도르 ESD 다이얼 안전화 4인치 260, 270mm 안전용품',
    84000, 105000, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0004', 'wi_master', 'WH-S-0004',
    'S', '3M 코팅장갑 슈퍼그립 200 그레이', 'LARGE',
    '3M 코팅장갑 슈퍼그립 200 그레이 LARGE 안전용품',
    2000, 2500, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0005', 'wi_master', 'WH-S-0005',
    'S', '디월트 보안경', 'DPG100-9D',
    '디월트 보안경 DPG100-9D 안전용품',
    10500, 13125, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0006', 'wi_master', 'WH-S-0006',
    'S', '일회용 마스크', '화이트',
    '일회용 마스크 화이트 안전용품',
    80, 100, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0007', 'wi_master', 'WH-S-0007',
    'S', 'Honeywell BW Ultra Deluxe Confined Space Kit', 'HU-CK-DL-EU',
    'Honeywell BW Ultra Deluxe Confined Space Kit HU-CK-DL-EU 안전용품',
    1450000, 1812500, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0001', 'wi_master', 'WH-T-0001',
    'T', '볼L렌치세트', 'PB212LH-10PR',
    '볼L렌치세트 PB212LH-10PR 공구류',
    98500, 120170, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0002', 'wi_master', 'WH-T-0002',
    'T', '몽키스패너', 'SWO-92',
    '몽키스패너 SWO-92 공구류',
    34000, 41480, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0003', 'wi_master', 'WH-T-0003',
    'T', '몽키스패너', 'ADHW6A',
    '몽키스패너 ADHW6A 공구류',
    142000, 173240, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0004', 'wi_master', 'WH-T-0004',
    'T', '방폭 몽키스패너', '125-1004',
    '방폭 몽키스패너 125-1004 공구류',
    46570, 56815, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0005', 'wi_master', 'WH-T-0005',
    'T', '방폭 몽키스패너', '125-1006',
    '방폭 몽키스패너 125-1006 공구류',
    62330, 76043, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0006', 'wi_master', 'WH-T-0006',
    'T', '방폭 몽키스패너', '125-1008',
    '방폭 몽키스패너 125-1008 공구류',
    77300, 94306, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0007', 'wi_master', 'WH-T-0007',
    'T', '방폭 몽키스패너', '125-1010',
    '방폭 몽키스패너 125-1010 공구류',
    100580, 122708, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0008', 'wi_master', 'WH-T-0008',
    'T', '방폭 몽키스패너', '125-1012',
    '방폭 몽키스패너 125-1012 공구류',
    154440, 188417, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0009', 'wi_master', 'WH-T-0009',
    'T', '방폭 콤비네이션렌치', '135-7',
    '방폭 콤비네이션렌치 135-7 공구류',
    17720, 21618, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0010', 'wi_master', 'WH-T-0010',
    'T', '방폭 콤비네이션렌치', '135-10',
    '방폭 콤비네이션렌치 135-10 공구류',
    24840, 30305, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0011', 'wi_master', 'WH-T-0011',
    'T', '방폭 콤비네이션렌치', '135-13',
    '방폭 콤비네이션렌치 135-13 공구류',
    30222, 36871, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0012', 'wi_master', 'WH-T-0012',
    'T', '방폭 콤비네이션렌치', '135-15',
    '방폭 콤비네이션렌치 135-15 공구류',
    32706, 39901, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0013', 'wi_master', 'WH-T-0013',
    'T', '방폭 콤비네이션렌치', '135-19',
    '방폭 콤비네이션렌치 135-19 공구류',
    38502, 46972, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0014', 'wi_master', 'WH-T-0014',
    'T', '방폭 콤비네이션렌치', '135-22',
    '방폭 콤비네이션렌치 135-22 공구류',
    81558, 99501, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0015', 'wi_master', 'WH-T-0015',
    'T', '방폭 콤비네이션렌치', '135-24',
    '방폭 콤비네이션렌치 135-24 공구류',
    54979, 67074, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0016', 'wi_master', 'WH-T-0016',
    'T', '방폭 콤비네이션렌치', '135-27',
    '방폭 콤비네이션렌치 135-27 공구류',
    78246, 95460, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0017', 'wi_master', 'WH-T-0017',
    'T', '방폭 콤비네이션렌치', '135-32',
    '방폭 콤비네이션렌치 135-32 공구류',
    105156, 128290, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0018', 'wi_master', 'WH-T-0018',
    'T', '방폭 콤비네이션렌치', '135-30',
    '방폭 콤비네이션렌치 135-30 공구류',
    95220, 116168, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0019', 'wi_master', 'WH-T-0019',
    'T', '방폭 콤비네이션렌치', '135-34',
    '방폭 콤비네이션렌치 135-34 공구류',
    123372, 150514, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0020', 'wi_master', 'WH-T-0020',
    'T', '방폭 콤비네이션렌치', '135-36',
    '방폭 콤비네이션렌치 135-36 공구류',
    144900, 176778, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0021', 'wi_master', 'WH-T-0021',
    'T', '방폭 콤비네이션렌치', '135-38',
    '방폭 콤비네이션렌치 135-38 공구류',
    156492, 190920, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0022', 'wi_master', 'WH-T-0022',
    'T', '방폭니퍼', '1100~1300N/mm2',
    '방폭니퍼 1100~1300N/mm2 공구류',
    89100, 108702, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0023', 'wi_master', 'WH-T-0023',
    'T', '방폭스패너', 'AB CW-16mm',
    '방폭스패너 AB CW-16mm 공구류',
    40200, 49044, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0024', 'wi_master', 'WH-T-0024',
    'T', '방폭렌치', 'NS S-A-13',
    '방폭렌치 NS S-A-13 공구류',
    510000, 622200, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0025', 'wi_master', 'WH-T-0025',
    'T', '트위스티드 육각 볼렌치', 'WH-T3',
    '트위스티드 육각 볼렌치 WH-T3 공구류',
    3737, 4559, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0026', 'wi_master', 'WH-T-0026',
    'T', '트위스티드 육각 볼렌치', 'WH-T4',
    '트위스티드 육각 볼렌치 WH-T4 공구류',
    4312, 5261, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0027', 'wi_master', 'WH-T-0027',
    'T', '트위스티드 육각 볼렌치', 'WH-T5',
    '트위스티드 육각 볼렌치 WH-T5 공구류',
    4887, 5962, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0028', 'wi_master', 'WH-T-0028',
    'T', '트위스티드 육각 볼렌치', 'WH-T6',
    '트위스티드 육각 볼렌치 WH-T6 공구류',
    5232, 6383, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0029', 'wi_master', 'WH-T-0029',
    'T', '이동식 사다리', 'ML-730HS',
    '이동식 사다리 ML-730HS 공구류',
    560000, 683200, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-T-0030', 'wi_master', 'WH-T-0030',
    'T', '테크트럭(무소음)', 'Green, 중',
    '테크트럭(무소음) Green, 중 공구류',
    55000, 67100, 22.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0008', 'wi_master', 'WH-S-0008',
    'S', '리튬 이온 배터리', 'TR-632E',
    '리튬 이온 배터리 TR-632E S · Safety (안전용품)',
    360000, 450000, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0009', 'wi_master', 'WH-S-0009',
    'S', '호스', 'BT-30',
    '호스 BT-30 S · Safety (안전용품)',
    76000, 95000, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0010', 'wi_master', 'WH-S-0010',
    'S', '필터커버', 'TR-6500FC',
    '필터커버 TR-6500FC S · Safety (안전용품)',
    13500, 16875, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-S-0011', 'wi_master', 'WH-S-0011',
    'S', '전동식 호흡보호구 호환 가방', 'BPK-HD',
    '전동식 호흡보호구 호환 가방 BPK-HD S · Safety (안전용품)',
    130000, 162500, 25.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-C-0009', 'wi_master', 'WH-C-0009',
    'C', '니트릴 장갑', 'L',
    '니트릴 장갑 L C · Cleanroom (크린용품)',
    175000, 210000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-O-0004', 'wi_master', 'WH-O-0004',
    'O', '무선 바코드스캐너', 'UV-6200',
    '무선 바코드스캐너 UV-6200 O · Office (사무일반)',
    50000, 60000, 20.0,
    TRUE, TRUE, 1.00
);
INSERT INTO products (
    wi_code, source_code, source_product_id,
    category_code, name_ko, spec,
    search_keywords,
    cost_price, list_price, margin_pct,
    is_directly_sold, is_published, quality_score
) VALUES (
    'WH-O-0005', 'wi_master', 'WH-O-0005',
    'O', 'USB 3.0', 'A to C타입',
    'USB 3.0 A to C타입 O · Office (사무일반)',
    4500, 5400, 20.0,
    TRUE, TRUE, 1.00
);

-- 총 100 건 삽입