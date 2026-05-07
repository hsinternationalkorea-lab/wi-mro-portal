# -*- coding: utf-8 -*-
"""
크레텍 카테고리 트리 → 우리 9개 카테고리 정확 매핑
- categories_full.json + category_tree.json 활용해서 leaf의 level1 root 추적
- level1 이름 기준으로 정확 매핑
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS_FILE = os.path.join(ROOT, "output", "cretec", "categories_full.json")
TREE_FILE = os.path.join(ROOT, "output", "cretec", "category_tree.json")


# 크레텍 1차 카테고리 → 우리 9개 매핑
LVL1_TO_WI = {
    "작업공구": "T",
    "절삭ㆍ금형ㆍ공작": "T",
    "전동ㆍ다몬ㆍ엔진ㆍ하역": "T",
    "에어ㆍ콤프레샤ㆍ유압": "T",
    "용접기자재": "T",  # 용접 = 공구의 일종
    "측정ㆍ측량ㆍ계측": "L",
    "안전용품": "S",
    "철물ㆍ원예ㆍ사무용품": "O",  # 혼합 — 운영자 검수 후 세분화
    "산업용품": "P",  # 호스, 고무판, 매트 위주
}

# 부분 일치 (특수문자 제거 후)
def normalize_name(name):
    return re.sub(r"[^\w가-힣]", "", str(name or ""))


def build_leaf_to_root():
    """
    leaf code(level 4) → level 1 카테고리 이름 매핑 dict 생성
    category_tree.json에서 추출 (이미 lvl1 -> subs 구조)
    """
    if not os.path.exists(TREE_FILE):
        print(f"[WARN] {TREE_FILE} 없음")
        return {}

    with open(TREE_FILE, encoding="utf-8") as f:
        tree = json.load(f)

    # category_tree.json은 lvl1 9개 + 각 subs (level 3, 4 mixed)
    # 더 정확한 추출은 categories_full.json HTML 파싱 시 부모 추적 필요
    # 임시: tree 활용해서 이름 매칭
    leaf_to_root = {}
    for entry in tree:
        lvl1_name = entry["lvl1"]
        for sub in entry["subs"]:
            text = sub["text"].strip()
            # "- xxx" 형태가 leaf
            if text.startswith("- "):
                leaf_name = normalize_name(text[2:])
                leaf_to_root[leaf_name] = lvl1_name
            else:
                # level 3 (parent of level 4) - 같은 root 적용
                leaf_to_root[normalize_name(text)] = lvl1_name

    return leaf_to_root


def map_to_wi(leaf_label, leaf_text=""):
    """
    크레텍 leaf 이름 → 우리 카테고리 코드
    1차: leaf 이름으로 root 추적 → root에서 매핑
    2차: 키워드 매칭 fallback
    """
    leaf_norm = normalize_name(leaf_label)

    # 1차: 이름으로 root 찾기
    leaf_to_root = _LEAF_TO_ROOT
    root = leaf_to_root.get(leaf_norm)
    if root:
        return LVL1_TO_WI.get(root, "O")

    # 2차: 키워드 (T 먼저 — 공구가 가장 다양하고 모호한 단어 많음)
    text = (leaf_label + " " + leaf_text).lower()

    # T (공구) — 우선 잡기
    if re.search(r"클램프|바이스|렌치|드라이버|스패너|망치|드릴|커터|니퍼|펜치|플라이어|톱|줄|소켓|연마|절삭|핸드툴|전동공구|에어공구|전동드릴|연삭|샌더|글라인더|용접|와이어|용접봉|컴비|ratchet|라쳇|혹"
                 r"|수공구|기계공구|장비공구|작업공구|핸드드릴|복스|컷팅|구리스|그리스|기름|루펜|핀펀치|핸들", text): return "T"
    if re.search(r"안전|보호구|마스크|보안경|헬멧|안전모|안전화|소방|구조|방독|방화|난연", text): return "S"
    if re.search(r"측정|계측|측량|토크|마이크로미터|버니어|레이저|광학|현미경|돋보기|저울", text): return "L"
    if re.search(r"의료|구급|응급|진료|약품", text): return "M"
    if re.search(r"\b볼트\b|\b너트\b|\b와셔\b|체결구|체결볼트", text): return "F"
    if re.search(r"크린룸|클린룸|방진|와이퍼|라텍스|니트릴|위생|일회용|크린", text): return "C"
    # E는 진짜 전기·조명만
    if re.search(r"전등|램프|조명|LED|전구|배터리|충전식라이트|충전라이트|헤드라이트|손전등|콘센트|소켓콘센트|멀티탭|전선|케이블타이|배선재", text): return "E"
    if re.search(r"포장|박스|상자|노끈|밴드|랩|비닐|호스|고무판|매트|결속", text): return "P"
    # 일반 공구 fallback
    if re.search(r"공구|핸드툴|전동", text): return "T"

    return "O"


# 모듈 import 시점에 빌드
_LEAF_TO_ROOT = build_leaf_to_root()
print(f"[category_map] leaf→root 매핑 {len(_LEAF_TO_ROOT)}개 로드", flush=True)


if __name__ == "__main__":
    # 테스트
    tests = [
        "가정용공구세트", "공구세트", "스마토천가방", "자전거공구세트",
        "니퍼", "롱노우즈플라이어", "다이아몬드연마공구", "안전모", "보안경",
        "임팩트소켓", "용접봉", "광학기기", "에어공구", "호스", "고무판",
    ]
    print("\n=== 매핑 테스트 ===")
    for t in tests:
        wi = map_to_wi(t)
        root = _LEAF_TO_ROOT.get(normalize_name(t), "(키워드 매칭)")
        print(f"  '{t}' → {wi} (root: {root})")
