# -*- coding: utf-8 -*-
"""
WI MRO Search Portal v0.3 — White Clean + 페이지네이션 + 필터 + Admin
"""
import os
import sys
import base64
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import SupabaseClient

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "static" / "WI_logo_official_fullcolor.png"
ADMIN_PASS = "wi2026"  # 시험가동 임시 비번 (정식은 Supabase Auth)


st.set_page_config(
    page_title="WI · 산업재 통합 검색",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def logo_data_uri():
    if not LOGO_PATH.exists():
        return None
    with open(LOGO_PATH, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"


LOGO_URI = logo_data_uri()


# CSS
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
:root {
    --wi-blue: #0089D0;
    --wi-slate: #2B3A4E;
    --wi-gray-1: #F8F9FB;
    --wi-gray-2: #E5E8EC;
    --wi-gray-3: #B0B5BD;
    --wi-text: #2B3A4E;
    --wi-text-sub: #6B7280;
}
html, body, [class*="css"], .stApp, .stMarkdown, p, span, div, a, button, input, label {
    font-family: 'Pretendard', -apple-system, system-ui, sans-serif !important;
    color: var(--wi-text);
}
.stApp { background: #ffffff; }
#MainMenu, footer, header[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 0 !important; max-width: 1400px; }

.topnav {
    border-bottom: 1px solid var(--wi-gray-2);
    padding: 16px 0;
    margin-bottom: 32px;
    display: flex; justify-content: space-between; align-items: center;
}
.topnav .brand { display: flex; align-items: center; gap: 12px; }
.topnav .brand img { height: 28px; }
.topnav .brand .name { font-size: 14px; font-weight: 600; }
.topnav .nav-right { font-size: 12px; color: var(--wi-text-sub); }

/* 메인 화면 mini 좌측 로고 (검색 후 화면에서만) */
.brand-mini { display: flex; align-items: center; gap: 8px; padding: 8px 0; }
.brand-mini img { height: 22px; }
.brand-mini .name { font-size: 13px; font-weight: 600; color: var(--wi-slate); letter-spacing: -0.3px; }

/* 우측 nav 버튼들 — 구글처럼 작고 깔끔 */
.nav-icon-row [data-testid="stButton"] button {
    padding: 6px 10px !important;
    font-size: 12px !important;
    height: 34px !important;
    min-height: 34px !important;
    border-radius: 17px !important;
    border: 1px solid var(--wi-gray-2) !important;
    background: #ffffff !important;
    color: var(--wi-text) !important;
    font-weight: 500 !important;
}
.nav-icon-row [data-testid="stButton"] button:hover {
    background: var(--wi-gray-1) !important;
    border-color: var(--wi-gray-3) !important;
}
.nav-icon-row [data-testid="stButton"] button[kind="primary"] {
    background: var(--wi-blue) !important;
    color: white !important;
    border-color: var(--wi-blue) !important;
}

.hero { text-align: center; padding: 48px 0 32px 0; }
.hero img.logo {
    width: 100%;
    max-width: 720px;
    height: auto;
    margin-bottom: 32px;
    display: block;
    margin-left: auto;
    margin-right: auto;
}
.hero .h1 { font-size: 32px; font-weight: 700; letter-spacing: -1px; margin-bottom: 8px; color: var(--wi-slate); }
.hero .h1 span { color: var(--wi-blue); }
.hero .sub { font-size: 14px; color: var(--wi-text-sub); margin-bottom: 32px; }

/* === Input 스타일링 (BaseWeb wrapper까지 모두 강제) === */
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input:invalid,
div[data-testid="stTextInput"] input:required,
div[data-testid="stTextInput"] input:focus:invalid,
div[data-testid="stTextInput"] input:focus-visible:invalid,
div[data-testid="stNumberInput"] input,
div[data-testid="stNumberInput"] input:invalid {
    height: 52px !important;
    font-size: 15px !important;
    border: 1px solid var(--wi-gray-2) !important;
    border-radius: 26px !important;
    padding: 0 24px !important;
    background: white !important;
    transition: all 0.15s;
    outline: none !important;
    box-shadow: none !important;
}

/* BaseWeb input wrapper — border만 제거, 높이는 input과 동일하게 */
div[data-testid="stTextInput"] [data-baseweb="input"],
div[data-testid="stTextInput"] [data-baseweb="base-input"],
div[data-testid="stNumberInput"] [data-baseweb="input"],
div[data-testid="stNumberInput"] [data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
    height: auto !important;
    min-height: 52px !important;
    overflow: visible !important;
}

/* stTextInput 컨테이너에 충분한 공간 확보 */
div[data-testid="stTextInput"] {
    min-height: 56px !important;
}
div[data-testid="stTextInput"] > div {
    overflow: visible !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextInput"] input:focus-visible {
    border-color: var(--wi-blue) !important;
    box-shadow: 0 0 0 3px rgba(0,137,208,0.1) !important;
    outline: none !important;
}

/* invalid/required 상태 — 모든 변형 명시적 차단 */
input:invalid,
input:required:invalid,
input:focus:invalid,
input:focus-visible:invalid,
input:not(:focus):invalid,
[aria-invalid="true"],
[data-baseweb="input"][aria-invalid="true"],
[data-baseweb="base-input"][aria-invalid="true"] {
    box-shadow: none !important;
    border-color: var(--wi-gray-2) !important;
    outline: none !important;
}
div[data-testid="stNumberInput"] input { height: 36px !important; border-radius: 4px !important; padding: 0 10px !important; }
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label { display: none !important; }

.stButton > button {
    background: white !important;
    color: var(--wi-text) !important;
    border: 1px solid var(--wi-gray-2) !important;
    border-radius: 18px !important;
    padding: 4px 14px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    height: 32px !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    border-color: var(--wi-blue) !important;
    color: var(--wi-blue) !important;
}

button[kind="primary"] {
    background: var(--wi-blue) !important;
    color: white !important;
    border: 1px solid var(--wi-blue) !important;
}

.results-head { padding: 20px 0 16px 0; border-bottom: 1px solid var(--wi-gray-2); margin-bottom: 24px; }
.results-head .count { font-size: 13px; color: var(--wi-text-sub); }
.results-head .query { font-size: 22px; font-weight: 600; margin-top: 4px; }

.product-card {
    border: 1px solid var(--wi-gray-2);
    background: white;
    padding: 16px;
    height: 100%;
    transition: border-color 0.15s;
    margin-bottom: 8px;
}
.product-card:hover { border-color: var(--wi-blue); }
.product-card .img-wrap {
    background: var(--wi-gray-1);
    height: 140px;
    margin: -16px -16px 12px -16px;
    display: flex; align-items: center; justify-content: center;
}
.product-card .img-wrap img { max-width: 80%; max-height: 80%; object-fit: contain; }
.product-card .name {
    font-size: 13px; font-weight: 600; line-height: 1.4;
    height: 36px; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}
.product-card .spec { font-size: 11px; color: var(--wi-text-sub); margin-top: 4px; height: 16px; overflow: hidden; }
.product-card .price { font-size: 16px; font-weight: 700; margin-top: 8px; }
.product-card .price .currency { font-weight: 500; font-size: 12px; color: var(--wi-text-sub); margin-right: 3px; }
.product-card .price .unit { font-weight: 500; font-size: 11px; color: var(--wi-text-sub); margin-left: 4px; }
.product-card .meta {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--wi-gray-2);
}
.product-card .mfr { font-size: 10px; color: var(--wi-text-sub); }
.product-card .wi-code { font-size: 10px; color: var(--wi-gray-3); font-family: monospace; }
.product-card .badge-direct {
    display: inline-block; background: rgba(0,137,208,0.08); color: var(--wi-blue);
    padding: 1px 6px; font-size: 9px; font-weight: 600; margin-left: 4px;
}
.product-card .admin-cost {
    margin-top: 6px; padding: 4px 8px; background: #FFF8E1;
    border-left: 3px solid #FFA000; font-size: 11px;
}
.product-card .admin-cost .label { color: #F57C00; font-weight: 600; }

/* 사이드바 필터 */
.filter-section { padding: 12px 0; border-bottom: 1px solid var(--wi-gray-2); }
.filter-section h4 { font-size: 12px; font-weight: 600; color: var(--wi-text-sub); margin-bottom: 8px; letter-spacing: 0.5px; text-transform: uppercase; }
.filter-section .item { font-size: 13px; padding: 4px 0; cursor: pointer; }
.filter-section .item:hover { color: var(--wi-blue); }
.filter-section .count { color: var(--wi-text-sub); font-size: 11px; margin-left: 4px; }

.pagination {
    display: flex; justify-content: center; gap: 4px; margin: 32px 0;
}
.footer {
    text-align: center; padding: 48px 0 24px 0; margin-top: 48px;
    border-top: 1px solid var(--wi-gray-2);
    font-size: 11px; color: var(--wi-text-sub);
}
.footer .tagline { font-size: 12px; font-weight: 500; margin-bottom: 8px; letter-spacing: 0.3px; }
</style>
""", unsafe_allow_html=True)


# DB
@st.cache_resource
def get_client():
    return SupabaseClient()


@st.cache_data(ttl=60)
def get_categories():
    c = get_client()
    cats = c.select("categories", select="code,name_ko,name_en,priority", order="priority")
    return cats if isinstance(cats, list) else []


@st.cache_data(ttl=60)
def get_total_count():
    c = get_client()
    import urllib.request, json
    url = c.url + '/rest/v1/products?select=count&is_published=eq.true'
    req = urllib.request.Request(url, headers={**c.headers, 'Prefer': 'count=exact'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return int(r.headers.get('Content-Range', '0/0').split('/')[-1])
    except Exception:
        return 0


@st.cache_data(ttl=30)
def search_with_count(query, category, manufacturer_filter, page, per_page, sort):
    """검색 + 총 건수 + 필터링 + 페이지네이션"""
    c = get_client()
    import urllib.request, json
    params = {
        "select": "id,wi_code,category_code,sub_category,name_ko,spec,manufacturer,primary_image_url,list_price,cost_price,margin_pct,price_unit,source_code,is_directly_sold,price_status",
        "is_published": "eq.true",
    }
    if query and query.strip():
        q = query.strip().replace("'", "''").replace("*", "")
        params["search_keywords"] = f"ilike.*{q}*"
    if category:
        params["category_code"] = f"eq.{category}"
    if manufacturer_filter:
        params["manufacturer"] = f"eq.{manufacturer_filter}"

    # 정렬 — 랜덤은 클라이언트 측 셔플 (세션 시드 기반)
    sort_map = {
        "랜덤": None,  # 클라이언트 셔플
        "관련도": "is_directly_sold.desc,quality_score.desc",
        "가격↑": "list_price.asc.nullslast",
        "가격↓": "list_price.desc.nullslast",
        "신상품": "created_at.desc",
        "WI품번": "wi_code.asc",
    }
    if sort_map.get(sort):
        params["order"] = sort_map[sort]
    else:
        # 랜덤 — id 기준 fetch 후 클라이언트에서 셔플
        params["order"] = "id.asc"

    # 카운트 (Range header)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    count_url = f"{c.url}/rest/v1/products?{qs}&select=count"
    req = urllib.request.Request(count_url, headers={**c.headers, "Prefer": "count=exact"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            total = int(r.headers.get("Content-Range", "0/0").split("/")[-1])
    except Exception:
        total = 0

    # 랜덤 정렬: 더 큰 batch 받아서 셔플 후 페이지 단위로 자르기
    if sort == "랜덤":
        # 최대 500개 fetch (큰 카테고리는 다 못 받지만 샘플로 충분)
        params["limit"] = "500"
        params["offset"] = "0"
        all_results = c.select("products", **params)
        if not isinstance(all_results, list):
            return [], 0
        # 세션 시드 기반 셔플 (페이지 이동에도 일관)
        import random as _rnd
        rng = _rnd.Random(st.session_state.random_seed)
        shuffled = list(all_results)
        rng.shuffle(shuffled)
        # 페이지 단위로 자르기
        start = page * per_page
        end = start + per_page
        return shuffled[start:end], total
    else:
        params["limit"] = str(per_page)
        params["offset"] = str(page * per_page)
        results = c.select("products", **params)
        return (results if isinstance(results, list) else [], total)


@st.cache_data(ttl=120)
def get_filter_options(query, category):
    """현재 검색 결과의 사이드바 필터 옵션"""
    c = get_client()
    params = {
        "select": "manufacturer,category_code,sub_category",
        "is_published": "eq.true",
        "limit": "1000",
    }
    if query and query.strip():
        q = query.strip().replace("'", "''").replace("*", "")
        params["search_keywords"] = f"ilike.*{q}*"
    if category:
        params["category_code"] = f"eq.{category}"
    results = c.select("products", **params)
    if not isinstance(results, list):
        return {"manufacturers": [], "sub_categories": []}
    from collections import Counter
    mfrs = Counter(p.get("manufacturer", "") for p in results if p.get("manufacturer"))
    subs = Counter(p.get("sub_category", "") for p in results if p.get("sub_category"))
    return {
        "manufacturers": mfrs.most_common(10),
        "sub_categories": subs.most_common(10),
    }


# 세션 상태
if "search_q" not in st.session_state: st.session_state.search_q = ""
if "selected_cat" not in st.session_state: st.session_state.selected_cat = None
if "page" not in st.session_state: st.session_state.page = 0
if "sort" not in st.session_state: st.session_state.sort = "랜덤"
if "random_seed" not in st.session_state:
    import random as _r
    st.session_state.random_seed = _r.randint(1, 99999)
if "mfr_filter" not in st.session_state: st.session_state.mfr_filter = None
if "show_quote_for" not in st.session_state: st.session_state.show_quote_for = None
if "view_detail_for" not in st.session_state: st.session_state.view_detail_for = None
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "cart" not in st.session_state: st.session_state.cart = {}  # {product_id: {qty, snapshot}}
if "view_cart" not in st.session_state: st.session_state.view_cart = False
if "view_admin_orders" not in st.session_state: st.session_state.view_admin_orders = False
if "admin_order_filter" not in st.session_state: st.session_state.admin_order_filter = "전체"


def upgrade_image_url(url, source_code=""):
    """이미지 URL을 더 큰 사이즈로 변환 (출처별 패턴)"""
    if not url:
        return url
    # 크레텍: -2-3.jpg (작은) → -1.jpg (큰)
    if "ctx.cretec.kr" in url:
        # /SBI_ITEM_IMG/3273006-2-3.jpg?14 → /SBI_ITEM_IMG/3273006-1.jpg
        m = re.search(r"/SBI_ITEM_IMG/(\d+)", url)
        if m:
            return re.sub(r"/SBI_ITEM_IMG/(\d+)[-\d]*\.(jpg|JPG|jpeg|png)", rf"/SBI_ITEM_IMG/\1-1.\2", url)
    # 석림랩텍: 보통 small/medium/big 폴더
    if "sercrim" in url or "labbazic" in url:
        return url.replace("/small/", "/big/").replace("_small", "_big")
    return url


import re


def add_to_cart(product, qty=1):
    pid = product["id"]
    if pid in st.session_state.cart:
        st.session_state.cart[pid]["qty"] += qty
    else:
        st.session_state.cart[pid] = {
            "qty": qty,
            "snapshot": {
                "id": pid,
                "wi_code": product.get("wi_code"),
                "name_ko": product.get("name_ko"),
                "spec": product.get("spec"),
                "manufacturer": product.get("manufacturer"),
                "primary_image_url": product.get("primary_image_url"),
                "list_price": product.get("list_price"),
                "cost_price": product.get("cost_price"),
                "price_unit": product.get("price_unit"),
            }
        }


def cart_count():
    return sum(item["qty"] for item in st.session_state.cart.values())


def cart_total():
    return sum((item["snapshot"].get("list_price") or 0) * item["qty"]
               for item in st.session_state.cart.values())


# URL 파라미터 복원 — 외부에서 ?q=, ?cat=, ?view= 로 직접 진입한 케이스만 처리
# (admin/admin_orders 자동 복원은 보안상 제거 — URL만으로 admin 권한 부여 X.
#  카드 클릭이 st.button 콜백 방식으로 바뀌어 session 손실도 더 이상 없음)
qp = st.query_params if hasattr(st, "query_params") else {}

# 검색 상태 복원 (카드 클릭으로 reload된 경우)
if qp.get("q") and not st.session_state.search_q:
    st.session_state.search_q = qp.get("q")
if qp.get("cat") and not st.session_state.selected_cat:
    st.session_state.selected_cat = qp.get("cat")
if qp.get("page"):
    try:
        st.session_state.page = int(qp.get("page"))
    except ValueError: pass
if qp.get("sort"):
    st.session_state.sort = qp.get("sort")
if qp.get("mfr") and not st.session_state.mfr_filter:
    st.session_state.mfr_filter = qp.get("mfr")


# 상단 네비 — 구글 스타일: 메인은 우측만, 검색 후엔 좌측에 작은 로고 추가
# 추가 메뉴 (placeholder): 🕒 최근 본 / ⭐ 찜 / ❓ 도움말 — 향후 실제 기능 연결
is_main_screen = not st.session_state.search_q and not st.session_state.selected_cat
admin_logged_in = st.session_state.is_admin == True
cart_n = cart_count()

# 추가 session_state 변수
if "view_help" not in st.session_state: st.session_state.view_help = False
if "recent_products" not in st.session_state: st.session_state.recent_products = []
if "favorites" not in st.session_state: st.session_state.favorites = set()

# 좌측(작은 로고 or 빈공간) + 우측(작은 메뉴) 2단 구조
nav_l, nav_r = st.columns([5, 5])

with nav_l:
    # 메인 화면에서는 좌측 비움 (hero가 가운데에서 큰 로고 표시) — 구글 메인처럼
    if not is_main_screen and LOGO_URI:
        st.markdown(
            f'<a href="/" target="_self" style="text-decoration:none;color:inherit;cursor:pointer">'
            f'<div class="brand-mini">'
            f'<img src="{LOGO_URI}"><span class="name">홀세일인더스트리</span>'
            f'</div></a>',
            unsafe_allow_html=True,
        )

with nav_r:
    # 우측 작은 메뉴 — 항상 표시 (메인/검색 후 동일)
    st.markdown('<div class="nav-icon-row">', unsafe_allow_html=True)
    if admin_logged_in:
        # 로그인 시: 의뢰 / 최근 / 찜 / 카트 / 로그아웃
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("📋 의뢰", use_container_width=True, key="nav_admin_orders",
                         help="견적 의뢰 관리",
                         type="primary" if st.session_state.view_admin_orders else "secondary"):
                st.session_state.view_admin_orders = True
                st.session_state.view_cart = False
                st.rerun()
        with c2:
            if st.button("🕒", use_container_width=True, key="nav_recent",
                         help=f"최근 본 상품 ({len(st.session_state.recent_products)})"):
                st.toast("최근 본 상품 — 곧 활성화", icon="🕒")
        with c3:
            if st.button("⭐", use_container_width=True, key="nav_fav",
                         help=f"찜 ({len(st.session_state.favorites)})"):
                st.toast("찜 — 곧 활성화", icon="⭐")
        with c4:
            cart_label = f"🛒 {cart_n}" if cart_n else "🛒"
            if st.button(cart_label, use_container_width=True, key="nav_cart_btn",
                         help="장바구니",
                         type="primary" if cart_n > 0 else "secondary"):
                st.session_state.view_cart = True
                st.rerun()
        with c5:
            if st.button("로그아웃", use_container_width=True, key="nav_admin_logout",
                         help="관리자 모드 종료"):
                st.session_state.is_admin = False
                st.session_state.view_admin_orders = False
                st.rerun()
    else:
        # 비로그인: 최근 / 찜 / 도움말 / 카트 / 관리자 로그인
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("🕒", use_container_width=True, key="nav_recent",
                         help=f"최근 본 상품 ({len(st.session_state.recent_products)})"):
                st.toast("최근 본 상품 — 곧 활성화", icon="🕒")
        with c2:
            if st.button("⭐", use_container_width=True, key="nav_fav",
                         help=f"찜 ({len(st.session_state.favorites)})"):
                st.toast("찜 — 곧 활성화", icon="⭐")
        with c3:
            if st.button("❓", use_container_width=True, key="nav_help",
                         help="도움말 / 가이드"):
                st.session_state.view_help = not st.session_state.view_help
                st.rerun()
        with c4:
            cart_label = f"🛒 {cart_n}" if cart_n else "🛒"
            if st.button(cart_label, use_container_width=True, key="nav_cart_btn",
                         help="장바구니",
                         type="primary" if cart_n > 0 else "secondary"):
                st.session_state.view_cart = True
                st.rerun()
        with c5:
            if st.button("관리자", use_container_width=True, key="nav_admin_login",
                         help="관리자 로그인"):
                st.session_state.is_admin = "pending"
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 도움말 펼침
if st.session_state.view_help:
    with st.expander("📖 도움말 / 빠른 가이드", expanded=True):
        st.markdown("""
        **WI MRO 통합 검색 — 사용법**

        - **검색**: 상품명, 모델번호, 브랜드로 통합 검색 (42,000+ SKU)
        - **카테고리**: 메인 화면 카테고리 버튼으로 분야별 탐색
        - **장바구니 🛒**: 마음에 드는 상품 담기 → 견적 의뢰로 일괄 전송
        - **최근 본 상품 🕒** (준비 중): 마지막 본 5~10개 빠른 접근
        - **찜 ⭐** (준비 중): 자주 찾는 SKU 저장

        **견적 요청 흐름:**
        1. 검색 / 카테고리로 상품 찾기 → 카드의 [상세] 클릭
        2. [카트 담기] → 우측 상단 🛒에서 일괄 확인
        3. [견적 요청] 버튼 → 회사명/담당자/요청사항 입력 → 전송
        4. 영업 담당자가 회신 (보통 1영업일 이내)

        **궁금하신 점은**: sales@wholesale-k.com
        """)
        if st.button("닫기", key="help_close"):
            st.session_state.view_help = False
            st.rerun()

# Admin 비번 입력
if st.session_state.is_admin == "pending":
    with st.form("admin_login"):
        st.markdown("**관리자 모드 진입**")
        pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("로그인"):
            if pw == ADMIN_PASS:
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("비밀번호가 틀립니다")
    st.stop()


# 상품 상세 — set 되어 있으면 다른 메인 UI 안 그리고 detail 화면만 표시 (modal-like)
if st.session_state.view_detail_for:
    # 상단 닫기 버튼
    bc1, _bc2 = st.columns([2, 8])
    with bc1:
        if st.button("← 검색 결과로 돌아가기", key="detail_close_top", use_container_width=True):
            st.session_state.view_detail_for = None
            st.rerun()
    st.markdown("---")
    show_product_detail(st.session_state.view_detail_for)
    st.stop()


# 메인 화면 vs 검색 결과
if not st.session_state.search_q and not st.session_state.selected_cat:
    # 메인
    hero_html = '<div class="hero">'
    if LOGO_URI:
        hero_html += f'<img class="logo" src="{LOGO_URI}">'
    hero_html += '<div class="h1">산업재 통합 검색</div>'
    hero_html += '<div class="sub">반도체·화학·산업현장에 필요한 모든 것을 한 곳에서</div></div>'
    st.markdown(hero_html, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([1, 4, 1])
    with sc2:
        q = st.text_input("search", placeholder="상품명, 모델번호, 브랜드", label_visibility="collapsed", key="main_search")
        if q:
            st.session_state.search_q = q
            st.session_state.page = 0
            st.rerun()

    cats = get_categories()
    cat_cols = st.columns(len(cats))
    for i, cat in enumerate(cats):
        with cat_cols[i]:
            if st.button(cat["name_ko"], key=f"cat_{cat['code']}", use_container_width=True):
                st.session_state.selected_cat = cat["code"]
                st.session_state.search_q = ""  # 카테고리 클릭 = 검색어 초기화
                st.session_state.mfr_filter = None
                st.session_state.page = 0
                st.rerun()

    # 통계
    total = get_total_count()
    st.markdown(f"""
<div style="text-align:center;margin-top:64px;padding:32px 0;border-top:1px solid var(--wi-gray-2)">
  <div style="font-size:28px;font-weight:700;color:var(--wi-slate);letter-spacing:-0.5px">{total:,}</div>
  <div style="font-size:11px;color:var(--wi-text-sub);margin-top:4px;letter-spacing:0.5px">REGISTERED SKU</div>
</div>
""", unsafe_allow_html=True)

else:
    # 검색 결과 화면 — 사이드바 필터 + 메인 그리드
    # 상단 검색바
    head_cols = st.columns([1, 5, 1, 1])
    with head_cols[0]:
        if st.button("처음으로", use_container_width=False):
            st.session_state.search_q = ""
            st.session_state.selected_cat = None
            st.session_state.mfr_filter = None
            st.session_state.page = 0
            st.session_state.show_quote_for = None
            st.session_state.view_detail_for = None
            # query params 모두 클리어 (reload 후 다시 복원되지 않게)
            for k in ["q", "cat", "page", "sort", "mfr", "view"]:
                if k in st.query_params:
                    del st.query_params[k]
            st.rerun()
    with head_cols[1]:
        new_q = st.text_input("search", value=st.session_state.search_q,
                              placeholder="검색어 입력", label_visibility="collapsed", key="result_search")
        if new_q != st.session_state.search_q:
            st.session_state.search_q = new_q
            st.session_state.page = 0
            st.rerun()
    with head_cols[2]:
        sort_options = ["랜덤", "관련도", "가격↑", "가격↓", "신상품", "WI품번"]
        new_sort = st.selectbox("정렬", sort_options,
                                 index=sort_options.index(st.session_state.sort),
                                 label_visibility="collapsed", key="sort_sel")
        if new_sort != st.session_state.sort:
            st.session_state.sort = new_sort
            st.session_state.page = 0
            # 랜덤 다시 선택 시 새 시드 (다양성)
            if new_sort == "랜덤":
                import random as _r
                st.session_state.random_seed = _r.randint(1, 99999)
            st.rerun()

    # 사이드바 + 본문
    side, main = st.columns([1, 5])

    with side:
        st.markdown('<div class="filter-section"><h4>분류</h4></div>', unsafe_allow_html=True)
        cats = get_categories()
        cur_cat_code = st.session_state.selected_cat
        for c in cats:
            label = f"  ✓ {c['name_ko']}" if cur_cat_code == c["code"] else f"  {c['name_ko']}"
            if st.button(label, key=f"sb_cat_{c['code']}", use_container_width=True):
                st.session_state.selected_cat = c["code"] if cur_cat_code != c["code"] else None
                st.session_state.search_q = ""  # 카테고리 클릭 = 검색어 초기화 (네비게이션 우선)
                st.session_state.page = 0
                st.session_state.mfr_filter = None
                # query param 도 동기화
                for k in ["q", "view", "page", "mfr"]:
                    if k in st.query_params:
                        del st.query_params[k]
                st.rerun()

        # 브랜드
        opts = get_filter_options(st.session_state.search_q, st.session_state.selected_cat)
        if opts["manufacturers"]:
            st.markdown('<div class="filter-section"><h4>브랜드</h4></div>', unsafe_allow_html=True)
            for mfr, cnt in opts["manufacturers"]:
                if not mfr: continue
                short = mfr[:15]
                label = f"✓ {short}" if st.session_state.mfr_filter == mfr else f"{short} ({cnt})"
                if st.button(label, key=f"mfr_{mfr}", use_container_width=True):
                    st.session_state.mfr_filter = mfr if st.session_state.mfr_filter != mfr else None
                    st.session_state.page = 0
                    st.rerun()

    with main:
        per_page = 24
        results, total = search_with_count(
            st.session_state.search_q,
            st.session_state.selected_cat,
            st.session_state.mfr_filter,
            st.session_state.page,
            per_page,
            st.session_state.sort,
        )

        # 헤더
        cat_label = ""
        if st.session_state.selected_cat:
            co = next((c for c in cats if c["code"] == st.session_state.selected_cat), None)
            if co:
                cat_label = co["name_ko"]
        head_q_parts = [st.session_state.search_q, cat_label, st.session_state.mfr_filter]
        head_q = " · ".join([p for p in head_q_parts if p]) or "전체"

        st.markdown(
            f'<div class="results-head"><div class="count">{total:,}건</div>'
            f'<div class="query">{head_q}</div></div>',
            unsafe_allow_html=True,
        )

        if not results:
            st.info("결과가 없습니다.")
        else:
            cols_per_row = 4
            for row_start in range(0, len(results), cols_per_row):
                cols = st.columns(cols_per_row)
                for col_idx, prod in enumerate(results[row_start:row_start + cols_per_row]):
                    with cols[col_idx]:
                        img_url = prod.get("primary_image_url") or ""
                        name = (prod.get("name_ko") or "")[:60]
                        spec = (prod.get("spec") or "")[:40]
                        mfr = (prod.get("manufacturer") or "")[:20]
                        list_p = prod.get("list_price")
                        cost_p = prod.get("cost_price")
                        margin = prod.get("margin_pct") or 0
                        unit = prod.get("price_unit") or "EA"
                        wi_code = prod.get("wi_code") or ""
                        is_direct = prod.get("is_directly_sold", False)
                        badge = '<span class="badge-direct">DIRECT</span>' if is_direct else ""
                        img_html = f'<img src="{img_url}">' if img_url else '<span style="color:#B0B5BD;font-size:11px">이미지 준비 중</span>'

                        if list_p:
                            price_html = f'<span class="currency">₩</span>{int(list_p):,}<span class="unit">/ {unit}</span>'
                        else:
                            price_html = '<span style="font-size:13px;color:var(--wi-text-sub)">가격 문의</span>'

                        # Admin 모드 — cost + 마진 또는 미확정 라벨
                        admin_block = ""
                        if st.session_state.is_admin == True:
                            ps = prod.get("price_status") or ""
                            if ps == "priced":
                                margin_color = "#388E3C" if margin >= 15 else "#F57C00"
                                admin_block = f"""
<div class="admin-cost">
  <span class="label">원가</span> ₩{int(cost_p or 0):,} ·
  <span style="color:{margin_color};font-weight:600">마진 {margin}%</span>
</div>"""
                            elif ps == "cost_unconfirmed":
                                admin_block = """
<div class="admin-cost">
  <span style="color:#999;font-size:10px;background:#F5F5F5;padding:2px 6px;border-radius:3px;font-weight:500">원가 미확정</span>
</div>"""
                            elif ps == "no_price":
                                admin_block = """
<div class="admin-cost">
  <span style="color:#E65100;font-size:10px;background:#FFF3E0;padding:2px 6px;border-radius:3px;font-weight:500">가격 미확정</span>
</div>"""

                        # 카드 (단순 div — full page navigation으로 인한 session 손실 방지)
                        st.markdown(f"""
<div class="product-card">
  <div class="img-wrap">{img_html}</div>
  <div class="name">{name}</div>
  <div class="spec">{spec}</div>
  <div class="price">{price_html}</div>
  <div class="meta">
    <span class="mfr">{mfr}{badge}</span>
    <span class="wi-code">{wi_code}</span>
  </div>
  {admin_block}
</div>
""", unsafe_allow_html=True)
                        # 액션: 상세 / 수량 / 카트 담기 (모두 st.button 콜백 — session_state 유지)
                        ac1, ac2, ac3 = st.columns([1, 1, 2])
                        with ac1:
                            if st.button("상세", key=f"view_{prod['id']}", use_container_width=True):
                                st.session_state.view_detail_for = prod
                                st.rerun()
                        with ac2:
                            qty = st.number_input("수량", min_value=1, value=1, step=1,
                                                  key=f"qty_{prod['id']}", label_visibility="collapsed")
                        with ac3:
                            if st.button("카트 담기", key=f"add_{prod['id']}", use_container_width=True):
                                add_to_cart(prod, qty)
                                st.toast(f"카트에 추가: {prod.get('name_ko','')[:20]} × {qty}")
                                st.rerun()

            # 페이지네이션
            total_pages = (total + per_page - 1) // per_page
            cur = st.session_state.page
            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                pcols = st.columns([1, 1, 2, 1, 1])
                with pcols[0]:
                    if st.button("← 이전", disabled=(cur == 0), use_container_width=True):
                        st.session_state.page = max(0, cur - 1)
                        st.rerun()
                with pcols[2]:
                    st.markdown(f'<div style="text-align:center;padding:8px 0;color:var(--wi-text-sub);font-size:13px">'
                               f'페이지 <strong>{cur+1}</strong> / {total_pages} '
                               f'<span style="margin-left:12px">총 {total:,}건</span></div>',
                               unsafe_allow_html=True)
                with pcols[4]:
                    if st.button("다음 →", disabled=(cur >= total_pages-1), use_container_width=True):
                        st.session_state.page = min(total_pages - 1, cur + 1)
                        st.rerun()


# Admin 의뢰 목록 페이지
if st.session_state.view_admin_orders and st.session_state.is_admin == True:
    st.markdown("---")
    st.markdown("## 견적 요청 관리")
    st.caption("Sales@wholesale-k.com — 영업팀 공용")

    c = get_client()
    # 필터
    fc1, fc2, fc3, _ = st.columns([1.5, 1.5, 1.5, 5])
    with fc1:
        new_filter = st.selectbox("상태",
            ["전체", "pending", "reviewed", "quoted", "ordered", "cancelled"],
            index=["전체", "pending", "reviewed", "quoted", "ordered", "cancelled"].index(st.session_state.admin_order_filter),
            label_visibility="collapsed", key="adm_filter")
        if new_filter != st.session_state.admin_order_filter:
            st.session_state.admin_order_filter = new_filter
            st.rerun()
    with fc2:
        if st.button("← 검색으로", use_container_width=True, key="adm_back"):
            st.session_state.view_admin_orders = False
            st.rerun()
    with fc3:
        if st.button("새로고침", use_container_width=True, key="adm_refresh"):
            st.cache_data.clear()
            st.rerun()

    # 의뢰 목록 조회
    params = {"select": "*", "order": "created_at.desc", "limit": "100"}
    if st.session_state.admin_order_filter != "전체":
        params["status"] = f"eq.{st.session_state.admin_order_filter}"
    requests = c.select("quote_requests", **params)
    if not isinstance(requests, list):
        requests = []

    # 통계
    if requests:
        from collections import Counter
        all_reqs = c.select("quote_requests", select="status", limit="500")
        status_count = Counter(r["status"] for r in all_reqs) if isinstance(all_reqs, list) else {}
        s1, s2, s3, s4, s5 = st.columns(5)
        for col, lbl, key in [
            (s1, "신규", "pending"), (s2, "검토중", "reviewed"),
            (s3, "견적완료", "quoted"), (s4, "발주", "ordered"),
            (s5, "취소", "cancelled"),
        ]:
            with col:
                cnt = status_count.get(key, 0)
                st.markdown(f'<div style="text-align:center;padding:12px;border:1px solid var(--wi-gray-2)">'
                           f'<div style="font-size:20px;font-weight:700;color:var(--wi-slate)">{cnt}</div>'
                           f'<div style="font-size:11px;color:var(--wi-text-sub);margin-top:2px">{lbl}</div>'
                           f'</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 의뢰 카드
    if not requests:
        st.info(f"의뢰가 없습니다 ({st.session_state.admin_order_filter}).")
    else:
        st.caption(f"총 {len(requests)}건")
        for req in requests:
            req_id = req["id"]
            req_no = req.get("request_no", "-")
            company = req.get("company", "")
            contact = req.get("contact_name", "")
            email = req.get("email", "")
            phone = req.get("phone", "")
            status = req.get("status", "pending")
            created = req.get("created_at", "")[:16].replace("T", " ")
            note = req.get("note") or ""
            delivery = req.get("delivery_request") or ""

            # 라인
            items = c.select("quote_request_items", request_id=f"eq.{req_id}", order="id.asc")
            items = items if isinstance(items, list) else []
            total_amt = sum((it.get("list_price") or 0) * (it.get("quantity") or 0) for it in items)
            total_cost = sum((it.get("cost_price") or 0) * (it.get("quantity") or 0) for it in items)
            margin_pct = ((total_amt - total_cost) / total_amt * 100) if total_amt else 0

            status_color = {
                "pending": "#FFA000", "reviewed": "#1976D2",
                "quoted": "#388E3C", "ordered": "#2B3A4E",
                "cancelled": "#9E9E9E"
            }.get(status, "#9E9E9E")
            status_label = {
                "pending": "신규", "reviewed": "검토중",
                "quoted": "견적완료", "ordered": "발주",
                "cancelled": "취소"
            }.get(status, status)

            with st.expander(
                f"**{req_no}**  ·  {company}  ·  {contact}  ·  ₩{int(total_amt):,}  "
                f"·  [{status_label}]  ·  {created}",
                expanded=(status == "pending"),
            ):
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    st.markdown(f"**고객**\n\n{company}\n\n{contact}")
                    if req.get("business_no"):
                        st.caption(f"사업자: {req['business_no']}")
                with hc2:
                    st.markdown(f"**연락처**\n\n📞 {phone}\n\n✉ {email}")
                with hc3:
                    st.markdown(f"**금액**\n\n표시 ₩{int(total_amt):,}\n\n원가 ₩{int(total_cost):,} (마진 {margin_pct:.1f}%)")

                if delivery:
                    st.info(f"희망 납기: {delivery}")
                if note:
                    st.markdown(f"**요청사항:** {note}")

                # 라인 테이블
                if items:
                    import pandas as pd
                    rows = []
                    for it in items:
                        rows.append({
                            "WI품번": it.get("wi_code", ""),
                            "상품명": it.get("name_ko", ""),
                            "규격": it.get("spec", ""),
                            "제조사": it.get("manufacturer", ""),
                            "수량": it.get("quantity", 0),
                            "단위": it.get("price_unit", "EA"),
                            "표시가": int(it.get("list_price") or 0),
                            "원가": int(it.get("cost_price") or 0),
                            "라인합": int((it.get("list_price") or 0) * (it.get("quantity") or 0)),
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                # 상태 변경 버튼
                bc1, bc2, bc3, bc4, bc5 = st.columns(5)
                with bc1:
                    if status != "reviewed" and st.button("검토중으로", key=f"st_rev_{req_id}", use_container_width=True):
                        c.update("quote_requests", {"id": req_id}, {"status": "reviewed"})
                        st.rerun()
                with bc2:
                    if status != "quoted" and st.button("견적완료", key=f"st_qt_{req_id}", use_container_width=True):
                        c.update("quote_requests", {"id": req_id}, {"status": "quoted"})
                        st.rerun()
                with bc3:
                    if status != "ordered" and st.button("발주완료", key=f"st_or_{req_id}", use_container_width=True):
                        c.update("quote_requests", {"id": req_id}, {"status": "ordered"})
                        st.rerun()
                with bc4:
                    if status != "cancelled" and st.button("취소", key=f"st_cn_{req_id}", use_container_width=True):
                        c.update("quote_requests", {"id": req_id}, {"status": "cancelled"})
                        st.rerun()
                with bc5:
                    mailto = f"mailto:{email}?subject=[WI MRO] 견적서 회신 - {req_no}&body={contact}님 안녕하세요,%0A%0A문의주신 {req_no} 건에 대한 견적서를 첨부드립니다.%0A%0A문의 사항이 있으시면 회신 부탁드립니다.%0A%0A감사합니다.%0A㈜홀세일인더스트리"
                    st.markdown(f'<a href="{mailto}" target="_blank" style="display:block;text-align:center;padding:6px;border:1px solid var(--wi-gray-2);text-decoration:none;color:var(--wi-text);border-radius:4px;font-size:12px">메일 회신</a>',
                               unsafe_allow_html=True)

    st.stop()


# 카트 페이지
if st.session_state.view_cart:
    st.markdown("---")
    st.markdown("## 🛒 장바구니")

    if not st.session_state.cart:
        st.info("장바구니가 비어있습니다.")
        if st.button("← 검색으로 돌아가기"):
            st.session_state.view_cart = False
            st.rerun()
    else:
        # 라인 표시
        for pid, item in list(st.session_state.cart.items()):
            snap = item["snapshot"]
            line_cols = st.columns([1, 4, 1, 1, 1])
            with line_cols[0]:
                if snap.get("primary_image_url"):
                    st.image(snap["primary_image_url"], width=80)
            with line_cols[1]:
                st.markdown(f"**{snap.get('name_ko','')}**")
                st.caption(f"{snap.get('spec','')}  ·  {snap.get('manufacturer','')}  ·  `{snap.get('wi_code','')}`")
            with line_cols[2]:
                new_qty = st.number_input("수량", min_value=1, value=item["qty"],
                                          key=f"cart_qty_{pid}", label_visibility="collapsed")
                if new_qty != item["qty"]:
                    st.session_state.cart[pid]["qty"] = new_qty
                    st.rerun()
            with line_cols[3]:
                line_total = (snap.get("list_price") or 0) * item["qty"]
                st.markdown(f"**₩{int(line_total):,}**")
                st.caption(f"개당 ₩{int(snap.get('list_price') or 0):,}")
            with line_cols[4]:
                if st.button("삭제", key=f"del_{pid}"):
                    del st.session_state.cart[pid]
                    st.rerun()

        st.markdown("---")
        # 합계
        total_amt = cart_total()
        st.markdown(f"### 총 {len(st.session_state.cart)}품목 · {cart_count()}개 · **₩{int(total_amt):,}**")

        # 일괄 견적 요청 폼
        st.markdown("### 견적 요청")
        st.caption("필수 항목 *  ·  영업일 1일 내 회신 드립니다")
        with st.form("quote_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                f_company = st.text_input(
                    "회사명 *",
                    placeholder="예: ㈜홀세일인더스트리",
                    help="실제 사업자등록증상의 회사명을 입력하세요",
                )
                f_name = st.text_input(
                    "담당자 *",
                    placeholder="예: 홍기정 / 구매팀 김민수 과장",
                    help="견적 회신 받을 분의 성함과 직책",
                )
                f_phone = st.text_input(
                    "연락처 *",
                    placeholder="예: 010-1234-5678",
                    help="휴대폰 또는 회사 직통번호",
                )
            with fc2:
                f_email = st.text_input(
                    "이메일 *",
                    placeholder="예: name@company.co.kr",
                    help="견적서·세금계산서 받을 메일 주소",
                )
                f_business_no = st.text_input(
                    "사업자등록번호",
                    placeholder="예: 123-45-67890",
                    help="신규 거래 시 필수 (사본 첨부 메일로 발송)",
                )
                f_delivery = st.text_input(
                    "희망 납기",
                    placeholder="예: 2주 이내 / 5월 20일까지",
                    help="없으면 표준 납기 기준 회신",
                )
            f_note = st.text_area(
                "요청사항",
                height=80,
                placeholder="예: 인보이스 별도 분리 요청, 특정 제조사 우선, 현장 직배송 가능 여부 등",
                help="견적 작성·납품에 참고할 추가 요청을 자유롭게 적어주세요",
            )

            submitted = st.form_submit_button("견적 요청 보내기", type="primary", use_container_width=True)
            if submitted:
                if not (f_company and f_name and f_phone and f_email):
                    st.error("회사명, 담당자, 연락처, 이메일은 필수입니다.")
                else:
                    # Supabase quote_requests INSERT
                    c = get_client()
                    req_payload = {
                        "company": f_company,
                        "contact_name": f_name,
                        "email": f_email,
                        "phone": f_phone,
                        "business_no": f_business_no or None,
                        "delivery_request": f_delivery or None,
                        "note": f_note or None,
                    }
                    try:
                        result = c.insert("quote_requests", req_payload)
                        if isinstance(result, list) and result:
                            req_id = result[0]["id"]
                            req_no = result[0].get("request_no", "")

                            # 라인 INSERT
                            for pid, item in st.session_state.cart.items():
                                snap = item["snapshot"]
                                line_payload = {
                                    "request_id": req_id,
                                    "product_id": pid,
                                    "wi_code": snap.get("wi_code"),
                                    "name_ko": snap.get("name_ko"),
                                    "spec": snap.get("spec"),
                                    "manufacturer": snap.get("manufacturer"),
                                    "primary_image_url": snap.get("primary_image_url"),
                                    "list_price": snap.get("list_price"),
                                    "cost_price": snap.get("cost_price"),
                                    "price_unit": snap.get("price_unit"),
                                    "quantity": item["qty"],
                                }
                                c.insert("quote_request_items", line_payload)

                            st.success(f"견적 요청 접수 완료 — **{req_no}**")
                            st.info("WI에서 영업일 기준 1일 내 회신드리겠습니다.")
                            st.session_state.cart = {}
                            st.session_state.view_cart = False
                        else:
                            st.error(f"오류: {result}")
                    except Exception as e:
                        st.error(f"오류: {e}")

        if st.button("← 검색 계속하기"):
            st.session_state.view_cart = False
            st.rerun()

    st.stop()  # 카트 화면이면 메인 화면 안 그림


# 상품 상세 모달 — st.dialog (페이지 전환과 무관하게 위에 띄움)
@st.dialog(" ", width="large")
def show_product_detail(prod):
    # 상세 데이터 다시 조회
    c = get_client()
    full_prod = c.select("products", id=f"eq.{prod['id']}", limit="1")
    if isinstance(full_prod, list) and full_prod:
        prod = full_prod[0]

    # 이미지 큰 사이즈 + fallback
    raw_img = prod.get("primary_image_url") or ""
    big_img = upgrade_image_url(raw_img, prod.get("source_code", ""))

    dc1, dc2 = st.columns([1, 1])
    with dc1:
        # 큰 이미지 (gallery 형식)
        if big_img:
            # 큰 사이즈가 깨지면 원본 fallback
            st.markdown(
                f'<img src="{big_img}" '
                f'onerror="this.onerror=null;this.src=\'{raw_img}\'" '
                f'style="width:100%;max-height:500px;object-fit:contain;background:#F8F9FB;border:1px solid #E5E8EC">',
                unsafe_allow_html=True,
            )
        else:
            st.info("이미지 준비 중")

    with dc2:
        name = prod.get("name_ko", "")
        st.markdown(f"### {name}")
        if prod.get("is_directly_sold"):
            st.markdown('<span style="background:rgba(0,137,208,0.08);color:#0089D0;padding:4px 12px;font-size:11px;font-weight:600">DIRECT · WI 직거래</span>', unsafe_allow_html=True)
        st.caption(f"WI 품번: `{prod.get('wi_code','-')}` · 출처: {prod.get('source_code','-')}")

        list_p = prod.get("list_price")
        unit = prod.get("price_unit") or "EA"
        if list_p:
            st.markdown(f"## ₩{int(list_p):,} <span style='font-size:14px;color:#6B7280'>/ {unit}</span>", unsafe_allow_html=True)
        else:
            st.markdown('## <span style="font-size:18px;color:#6B7280">가격 문의</span>', unsafe_allow_html=True)
            st.caption("정확한 가격은 WI에 견적 요청 또는 출처 사이트에서 확인하세요.")

        if st.session_state.is_admin == True:
            cost_p = prod.get("cost_price") or 0
            margin = prod.get("margin_pct") or 0
            ps = prod.get("price_status") or ""
            if ps == "priced":
                color = "#388E3C" if margin >= 15 else "#F57C00"
                st.markdown(
                    f'<div style="background:#FFF8E1;border-left:3px solid #FFA000;padding:10px 14px;margin:8px 0">'
                    f'<strong style="color:#F57C00">Admin</strong>  '
                    f'원가 ₩{int(cost_p):,} · '
                    f'<span style="color:{color};font-weight:600">마진 {margin}%</span></div>',
                    unsafe_allow_html=True,
                )
            elif ps == "cost_unconfirmed":
                st.markdown(
                    '<div style="background:#F5F5F5;border-left:3px solid #999;padding:10px 14px;margin:8px 0;color:#666">'
                    '<strong>Admin</strong>  원가 미확정 — 출처에 회원가만 노출되어 원가/표시가 분리 불가</div>',
                    unsafe_allow_html=True,
                )
            elif ps == "no_price":
                st.markdown(
                    '<div style="background:#FFF3E0;border-left:3px solid #E65100;padding:10px 14px;margin:8px 0;color:#666">'
                    '<strong style="color:#E65100">Admin</strong>  가격 미확정 — 출처에 가격 자체가 없음</div>',
                    unsafe_allow_html=True,
                )

        if prod.get("spec"):
            st.markdown(f"**규격/사양:** {prod['spec']}")
        if prod.get("manufacturer"):
            st.markdown(f"**제조사:** {prod['manufacturer']}")
        if prod.get("model_no"):
            st.markdown(f"**모델번호:** {prod['model_no']}")
        if prod.get("sub_category"):
            st.markdown(f"**분류:** {prod['sub_category']}")

        st.markdown("<br>", unsafe_allow_html=True)
        ac1, ac2, ac3 = st.columns([1, 2, 2])
        with ac1:
            qty_d = st.number_input("수량", min_value=1, value=1, step=1,
                                     key=f"detqty_{prod['id']}", label_visibility="collapsed")
        with ac2:
            if st.button("카트 담기", key=f"detadd_{prod['id']}", use_container_width=True, type="primary"):
                add_to_cart(prod, qty_d)
                st.toast(f"카트에 추가: {name[:20]} × {qty_d}")
                st.session_state.view_detail_for = None
                st.rerun()
        with ac3:
            source_url = prod.get("source_url")
            if source_url:
                st.markdown(
                    f'<a href="{source_url}" target="_blank" style="display:block;text-align:center;padding:6px;'
                    f'border:1px solid #E5E8EC;text-decoration:none;color:#2B3A4E;border-radius:4px;font-size:12px;'
                    f'height:32px;line-height:20px">출처 사이트 →</a>',
                    unsafe_allow_html=True,
                )


# URL ?view=ID 외부 직접 진입 처리 — view_detail_for 설정 후 다음 rerun에서 상단 detail 가드(line ~497)가 표시
qp_view = st.query_params.get("view") if hasattr(st, "query_params") else None
if qp_view and not st.session_state.view_detail_for:
    try:
        c = get_client()
        prod_data = c.select("products", id=f"eq.{int(qp_view)}", limit="1")
        if isinstance(prod_data, list) and prod_data:
            st.session_state.view_detail_for = prod_data[0]
        del st.query_params["view"]  # 처리 후 URL 정리
        st.rerun()
    except Exception:
        pass


# 견적 모달
if st.session_state.show_quote_for:
    prod = st.session_state.show_quote_for
    st.markdown("---")
    st.markdown(f"### 견적 요청 — {prod.get('name_ko', '')}")
    qc1, qc2 = st.columns(2)
    with qc1:
        st.text_input("회사명", key="q_company")
        st.text_input("담당자", key="q_name")
        st.text_input("연락처", key="q_phone")
    with qc2:
        st.text_input("이메일", key="q_email")
        st.number_input("수량", min_value=1, value=1, key="q_qty")
        st.text_area("요청 사항", height=80, key="q_note")
    bc1, bc2, _ = st.columns([1, 1, 4])
    with bc1:
        if st.button("견적 보내기", type="primary"):
            st.success("견적 요청이 접수되었습니다.")
            st.session_state.show_quote_for = None
    with bc2:
        if st.button("취소"):
            st.session_state.show_quote_for = None
            st.rerun()


# 푸터
st.markdown("""
<div class="footer">
  <div class="tagline">BUILT ON TRUST. DELIVERED WITH PRECISION.</div>
  ㈜홀세일인더스트리 · kjhong@wholesale-k.com
</div>
""", unsafe_allow_html=True)
