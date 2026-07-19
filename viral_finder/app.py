import os
import sys
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from search import search_videos, format_count, format_duration, format_date, PLATFORMS
from analyzer import get_video_info, get_transcript, download_audio, transcribe_with_whisper, get_comments
from comment_miner import mine_comments
from ad_advisor import generate_ad_strategy, GOAL_OPTIONS, CURRENCY_OPTIONS
from translator import translate_text, using_free_translation
from templates import analyze_and_generate_templates, generate_custom_hook
from recreate import generate_recreation_guide
from content_tools import (
    generate_ab_titles, generate_thumbnail_copy, generate_content_calendar,
    adapt_for_platforms, analyze_best_posting_time,
)
from storage import add_history, get_history, clear_history, add_favorite, get_favorites, remove_favorite, FAVORITE_TYPES
from paywall import is_unlocked, render_unlock_prompt, PLAN_FEATURES
from faceless import (
    find_niches, generate_script, generate_seo_package,
    generate_thumbnail_prompts, generate_storyboard,
    NICHE_CATEGORIES, SCRIPT_STYLES, SCRIPT_LENGTHS, THUMBNAIL_STYLES,
)
from security import sanitize_prompt_input, is_safe_thumbnail_url
from survey import render_survey, render_admin_dashboard
from analytics import track, render_analytics_dashboard
from i18n import t, SUPPORTED_LANGUAGES

# ══════════════════════════════════════════════════════════════════════════════
# 頁面設定
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="爆款影片獵手",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 初始化 session state
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True
if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = "繁體中文"


# ══════════════════════════════════════════════════════════════════════════════
# 主題系統 (黑×紅 + 深淺色切換)
# ══════════════════════════════════════════════════════════════════════════════

def _inject_theme(dark: bool):
    if dark:
        bg        = "#080808"
        card      = "#111111"
        sidebar   = "#0c0c0c"
        txt       = "#e8e8e8"
        txt_h     = "#ffffff"
        muted     = "#888888"
        accent    = "#E63946"
        accent2   = "#c1121f"
        border    = "#242424"
        inp_bg    = "#181818"
        metric_bg = "#131313"
        tab_bg    = "#111111"
        code_bg   = "#161616"
        shadow    = "rgba(230,57,70,0.25)"
        glow      = "rgba(230,57,70,0.15)"
        success_bg = "rgba(16,185,129,0.08)"
        info_bg   = "rgba(59,130,246,0.08)"
        warn_bg   = "rgba(245,158,11,0.08)"
        err_bg    = "rgba(239,68,68,0.08)"
    else:
        bg        = "#f8f8f8"
        card      = "#ffffff"
        sidebar   = "#f0f0f0"
        txt       = "#1a1a1a"
        txt_h     = "#0a0a0a"
        muted     = "#666666"
        accent    = "#DC2626"
        accent2   = "#991b1b"
        border    = "#e0e0e0"
        inp_bg    = "#ffffff"
        metric_bg = "#fff5f5"
        tab_bg    = "#f5f5f5"
        code_bg   = "#f9f9f9"
        shadow    = "rgba(220,38,38,0.2)"
        glow      = "rgba(220,38,38,0.1)"
        success_bg = "rgba(16,185,129,0.06)"
        info_bg   = "rgba(59,130,246,0.06)"
        warn_bg   = "rgba(245,158,11,0.06)"
        err_bg    = "rgba(239,68,68,0.06)"

    st.markdown(f"""
<style>
/* ── GLOBAL ── */
html, body, .stApp {{
    background-color: {bg} !important;
    color: {txt} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: {sidebar} !important;
    border-right: 1px solid {border} !important;
}}
[data-testid="stSidebar"] * {{
    color: {txt} !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    border-color: {border} !important;
}}

/* ── TOP HEADER BAR ── */
[data-testid="stHeader"] {{
    background: {bg} !important;
    border-bottom: 1px solid {border} !important;
}}

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4 {{
    color: {txt_h} !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}}
p, li, span, label {{
    color: {txt};
}}
.stMarkdown, .stText {{
    color: {txt};
}}

/* ── PRIMARY BUTTON (Red) ── */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, {accent} 0%, {accent2} 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.5rem 1.25rem !important;
    box-shadow: 0 4px 14px {shadow} !important;
    transition: all 0.2s cubic-bezier(.4,0,.2,1) !important;
}}
.stButton > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {shadow} !important;
    opacity: 0.95 !important;
}}
.stButton > button[kind="primary"]:active {{
    transform: translateY(0) !important;
}}

/* ── SECONDARY BUTTON ── */
.stButton > button:not([kind="primary"]),
button[data-testid="baseButton-secondary"] {{
    background: transparent !important;
    color: {txt} !important;
    border: 1px solid {border} !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s cubic-bezier(.4,0,.2,1) !important;
}}
.stButton > button:not([kind="primary"]):hover {{
    border-color: {accent} !important;
    color: {accent} !important;
    background: {glow} !important;
}}

/* ── LINK BUTTONS ── */
a[data-testid="stLinkButton"] button {{
    background: transparent !important;
    border: 1px solid {border} !important;
    color: {txt} !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}}
a[data-testid="stLinkButton"] button:hover {{
    border-color: {accent} !important;
    color: {accent} !important;
}}

/* ── INPUT FIELDS ── */
input, textarea, .stTextInput input, .stTextArea textarea {{
    background: {inp_bg} !important;
    color: {txt} !important;
    border: 1px solid {border} !important;
    border-radius: 10px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
input:focus, textarea:focus {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 3px {glow} !important;
    outline: none !important;
}}
input[type="password"] {{
    background: {inp_bg} !important;
    color: {txt} !important;
}}

/* ── SELECT BOX ── */
[data-testid="stSelectbox"] > div > div {{
    background: {inp_bg} !important;
    color: {txt} !important;
    border: 1px solid {border} !important;
    border-radius: 10px !important;
}}
[data-testid="stSelectbox"] svg {{
    fill: {muted} !important;
}}

/* Selectbox dropdown */
[data-testid="stSelectbox"] ul {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 10px !important;
}}
[data-testid="stSelectbox"] li {{
    color: {txt} !important;
}}
[data-testid="stSelectbox"] li:hover {{
    background: {glow} !important;
    color: {accent} !important;
}}

/* ── METRICS ── */
[data-testid="stMetric"] {{
    background: {metric_bg} !important;
    border: 1px solid {border} !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    transition: transform 0.2s, border-color 0.2s !important;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px) !important;
    border-color: {accent} !important;
    box-shadow: 0 4px 16px {glow} !important;
}}
[data-testid="stMetricValue"] {{
    color: {accent} !important;
    font-weight: 800 !important;
    font-size: 1.5rem !important;
}}
[data-testid="stMetricLabel"] {{
    color: {muted} !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {tab_bg} !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid {border} !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {muted} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border: none !important;
    padding: 8px 14px !important;
    transition: all 0.2s !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {txt} !important;
    background: {glow} !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {accent}, {accent2}) !important;
    color: white !important;
    box-shadow: 0 2px 10px {shadow} !important;
}}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stExpander"]:hover {{
    border-color: {accent} !important;
}}
[data-testid="stExpander"] > div:first-child {{
    border-bottom: 1px solid {border} !important;
    padding: 14px 16px !important;
}}
[data-testid="stExpander"] summary {{
    color: {txt} !important;
    font-weight: 600 !important;
}}
[data-testid="stExpander"] svg {{
    fill: {muted} !important;
}}

/* ── CONTAINERS / CARDS (border=True) ── */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
    border-radius: 16px !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background: {card} !important;
    border: 1px solid {border} !important;
    border-radius: 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {{
    border-color: {accent} !important;
    box-shadow: 0 4px 20px {glow} !important;
}}

/* ── ALERTS ── */
[data-testid="stAlert"][data-baseweb="notification"] {{
    border-radius: 12px !important;
    border-width: 1px !important;
}}
.stSuccess {{
    background: {success_bg} !important;
    border-color: #10b981 !important;
}}
.stInfo {{
    background: {info_bg} !important;
    border-color: #3b82f6 !important;
}}
.stWarning {{
    background: {warn_bg} !important;
    border-color: #f59e0b !important;
}}
.stError {{
    background: {err_bg} !important;
    border-color: #ef4444 !important;
}}

/* ── CODE BLOCKS ── */
code, pre {{
    background: {code_bg} !important;
    color: {accent} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
}}

/* ── DIVIDER ── */
hr {{
    border-color: {border} !important;
    margin: 1.25rem 0 !important;
}}

/* ── SPINNER ── */
[data-testid="stSpinner"] svg circle {{
    stroke: {accent} !important;
}}

/* ── RADIO & CHECKBOX ── */
[data-testid="stRadio"] label span, [data-testid="stCheckbox"] label span {{
    color: {txt} !important;
}}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {{
    background: transparent !important;
    color: {accent} !important;
    border: 1px solid {accent} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}
.stDownloadButton > button:hover {{
    background: {glow} !important;
    box-shadow: 0 2px 12px {shadow} !important;
}}

/* ── NUMBER INPUT ── */
[data-testid="stNumberInput"] input {{
    background: {inp_bg} !important;
    color: {txt} !important;
    border: 1px solid {border} !important;
    border-radius: 10px !important;
}}

/* ── MULTISELECT ── */
[data-testid="stMultiSelect"] > div {{
    background: {inp_bg} !important;
    border: 1px solid {border} !important;
    border-radius: 10px !important;
    color: {txt} !important;
}}

/* ── IMAGE CAPTIONS ── */
[data-testid="caption"] {{
    color: {muted} !important;
    font-size: 0.78rem !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{width: 5px; height: 5px;}}
::-webkit-scrollbar-track {{background: {bg};}}
::-webkit-scrollbar-thumb {{background: {border}; border-radius: 99px;}}
::-webkit-scrollbar-thumb:hover {{background: {accent};}}

/* ══════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════ */

/* Step badge */
.step-badge {{
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, {accent}, {accent2});
    color: white;
    font-size: 0.68rem;
    font-weight: 900;
    padding: 3px 13px;
    border-radius: 99px;
    margin-right: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    box-shadow: 0 2px 10px {shadow};
    vertical-align: middle;
}}

/* PRO badge */
.pro-badge {{
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, {accent}, #7f1d1d);
    color: white;
    font-size: 0.62rem;
    font-weight: 800;
    padding: 2px 10px;
    border-radius: 99px;
    margin-left: 8px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    vertical-align: middle;
}}

/* FREE badge */
.free-badge {{
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, #10b981, #047857);
    color: white;
    font-size: 0.62rem;
    font-weight: 800;
    padding: 2px 10px;
    border-radius: 99px;
    margin-left: 8px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    vertical-align: middle;
}}

/* Hero title gradient */
.hero-title {{
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1.1;
    background: linear-gradient(135deg, {accent} 0%, #ff6b6b 50%, {accent2} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}}

/* Stat card */
.stat-card {{
    background: {metric_bg};
    border: 1px solid {border};
    border-radius: 16px;
    padding: 16px 20px;
    text-align: center;
    transition: all 0.2s;
}}
.stat-card:hover {{
    border-color: {accent};
    box-shadow: 0 4px 20px {glow};
    transform: translateY(-2px);
}}
.stat-card .stat-value {{
    font-size: 1.8rem;
    font-weight: 800;
    color: {accent};
    line-height: 1;
}}
.stat-card .stat-label {{
    font-size: 0.72rem;
    color: {muted};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}}

/* Section header */
.section-header {{
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {muted};
    margin-bottom: 0.5rem;
}}
</style>
""", unsafe_allow_html=True)


# 注入主題
_inject_theme(st.session_state["dark_mode"])

# ══════════════════════════════════════════════════════════════════════════════
# 側邊欄
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo + 標題
    st.markdown(
        f'<div class="hero-title" style="font-size:1.5rem; padding: 0.5rem 0;">{t("app_title")}</div>',
        unsafe_allow_html=True,
    )
    st.caption(t("sidebar_caption"))
    st.divider()

    # ── 深淺色切換 + 語言選擇
    _col_mode, _col_lang = st.columns([1, 1])
    with _col_mode:
        mode_label = t("dark_mode") if st.session_state["dark_mode"] else t("light_mode")
        if st.button(mode_label, use_container_width=True):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()
    with _col_lang:
        new_lang = st.selectbox(
            t("language_label"),
            list(SUPPORTED_LANGUAGES.keys()),
            index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.get("ui_lang", "繁體中文")),
            label_visibility="collapsed",
            key="lang_selector",
        )
        if new_lang != st.session_state.get("ui_lang"):
            st.session_state["ui_lang"] = new_lang
            st.rerun()

    st.divider()

    # ── 方案狀態
    _unlock_all = os.environ.get("UNLOCK_ALL", "").lower() in ("1", "true", "yes")
    _gumroad_url = os.environ.get("GUMROAD_URL", "")
    if is_unlocked():
        _sub_status = st.session_state.get("_sub_status", "active")
        if _sub_status == "cancelled":
            st.warning(t("sub_cancelled"))
        elif _sub_status == "payment_failed":
            st.error(t("sub_payment_failed"))
            if _gumroad_url:
                st.link_button(t("manage_sub"), _gumroad_url, use_container_width=True)
        else:
            st.success(t("sub_active"), icon="🔓")
        # 全開模式不顯示登出按鈕（課程版不需要）
        if not _unlock_all and st.button(t("logout_pro"), use_container_width=True):
            from paywall import lock
            lock()
            st.session_state.pop("_license_key", None)
            st.session_state.pop("_sub_status", None)
            st.rerun()
    else:
        with st.expander(t("unlock_expander")):
            code_in = st.text_input(
                "Access Code",
                placeholder=t("access_code_placeholder"),
                key="sidebar_code",
            )
            if st.button(t("unlock_btn"), type="primary", use_container_width=True):
                from paywall import try_unlock
                try:
                    if try_unlock(code_in):
                        track("unlock_pro")
                        st.success(t("unlock_success"))
                        st.rerun()
                    else:
                        st.error(t("unlock_error"))
                except ValueError as e:
                    st.warning(str(e))
            # Gumroad 訂閱按鈕
            if _gumroad_url:
                st.link_button(t("buy_pro_monthly"), _gumroad_url, use_container_width=True)
                st.caption(t("purchase_hint"))

        st.markdown(f'<p class="section-header">{t("free_features_header")}</p>', unsafe_allow_html=True)
        for f in PLAN_FEATURES["free"]:
            st.markdown(f)
        st.markdown(f'<p class="section-header" style="margin-top:0.75rem;">{t("pro_features_header")}</p>', unsafe_allow_html=True)
        for f in PLAN_FEATURES["pro"]:
            st.markdown(f)

    st.divider()
    st.markdown(f'<p class="section-header">{t("settings_header")}</p>', unsafe_allow_html=True)

    _env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if _env_key:
        st.success(t("ai_enabled"), icon="🤖")
    else:
        api_key = st.text_input(
            t("api_key_label"),
            type="password",
            placeholder="sk-ant-...",
            help=t("api_key_help"),
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

    ig_session = st.text_input(
        t("ig_session_label"),
        type="password",
        placeholder="sessionid=...",
        help=t("ig_session_help"),
        key="ig_session",
    )

    whisper_model = st.selectbox(
        t("whisper_model_label"),
        ["tiny", "base", "small", "medium"],
        index=1,
        help=t("whisper_model_help"),
    )

    st.divider()

    # ── 管理員工具
    _admin_key = os.environ.get("ADMIN_KEY", "")
    if _admin_key:
        with st.expander(t("admin_tools")):
            import time as _time
            _adm_attempts = st.session_state.get("_adm_attempts", 0)
            _adm_last_fail = st.session_state.get("_adm_last_fail", 0.0)
            _ADM_MAX = 3
            _ADM_COOLDOWN = 300

            _adm_locked = (
                _adm_attempts >= _ADM_MAX
                and (_time.time() - _adm_last_fail) < _ADM_COOLDOWN
            )

            if _adm_locked:
                _wait = int(_ADM_COOLDOWN - (_time.time() - _adm_last_fail))
                st.error(f"⛔ 嘗試次數過多，請等待 {_wait} 秒")
            else:
                admin_input = st.text_input(t("admin_password"), type="password", key="admin_pw")
                if admin_input == _admin_key:
                    # 登入成功：重置計數
                    st.session_state["_adm_attempts"] = 0
                    admin_tab1, admin_tab2, admin_tab3 = st.tabs([
                        t("admin_tab_analytics"),
                        t("admin_tab_survey"),
                        t("admin_tab_codes"),
                    ])

                    with admin_tab1:
                        render_analytics_dashboard()

                    with admin_tab2:
                        render_admin_dashboard()

                    with admin_tab3:
                        import secrets, string
                        num_codes = st.number_input("產生幾組", min_value=1, max_value=50, value=5, step=1)
                        if st.button(t("generate_codes_btn"), use_container_width=True, type="primary"):
                            codes = []
                            for _ in range(int(num_codes)):
                                p1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                                p2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                                codes.append(f"VH-{p1}-{p2}")
                            st.code("\n".join(codes))
                            st.caption(t("generate_codes_hint"))

                elif admin_input:
                    st.session_state["_adm_attempts"] = _adm_attempts + 1
                    st.session_state["_adm_last_fail"] = _time.time()
                    remaining = _ADM_MAX - st.session_state["_adm_attempts"]
                    if remaining > 0:
                        st.error(f"{t('wrong_password')}（剩餘 {remaining} 次）")
                    else:
                        st.error(f"⛔ 已鎖定 {_ADM_COOLDOWN // 60} 分鐘")

# ══════════════════════════════════════════════════════════════════════════════
# 主標題區
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<h1 class="hero-title">{t("app_title")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p style="font-size:1.05rem; color: var(--text-color, #888); margin-top: 0.2rem; margin-bottom: 1.5rem;">'
    f'{t("app_subtitle")}</p>',
    unsafe_allow_html=True,
)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1：輸入影片
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<span class="step-badge">STEP 1</span> **{t("step1_title")}**',
    unsafe_allow_html=True,
)

# 試玩模式：橫幅 + 一鍵載入範例影片
from demo import is_demo, DEMO_URL
if is_demo():
    st.info(t("demo_banner"))
    if st.button(t("demo_load_btn"), type="primary"):
        st.session_state["current_url"] = DEMO_URL
        st.rerun()

input_mode = st.radio(
    "輸入方式",
    [t("input_link"), t("input_search")],
    horizontal=True,
    label_visibility="collapsed",
)

video_url = None

if input_mode == t("input_link"):
    c1, c2 = st.columns([4, 1])
    with c1:
        url_input = st.text_input(
            "url",
            value=st.session_state.get("analyze_url", ""),
            placeholder=t("url_placeholder"),
            label_visibility="collapsed",
        )
    with c2:
        go_btn = st.button(t("analyze_btn"), type="primary", use_container_width=True)

    if go_btn and url_input.strip():
        video_url = url_input.strip()
        st.session_state["current_url"] = video_url

else:
    sc1, sc2, sc3 = st.columns([3, 1.5, 1])
    with sc1:
        keyword = st.text_input(
            "keyword",
            placeholder=t("keyword_placeholder"),
            label_visibility="collapsed",
        )
    with sc2:
        platform = st.selectbox("platform", list(PLATFORMS.keys()), label_visibility="collapsed")
    with sc3:
        search_btn = st.button(t("search_btn"), type="primary", use_container_width=True)

    if search_btn and keyword.strip():
        track("search_video", {"platform": platform, "keyword": keyword.strip()})
        with st.spinner(f"{t('searching')} {platform}…"):
            videos = search_videos(keyword.strip(), platform, 9)

        if not videos:
            st.error(t("no_results"))
        else:
            st.success(f"✅ {t('search_btn')} **{len(videos)}**")
            cols_per_row = 3
            for row_start in range(0, len(videos), cols_per_row):
                row = videos[row_start: row_start + cols_per_row]
                cols = st.columns(cols_per_row)
                for col, video in zip(cols, row):
                    with col:
                        with st.container(border=True):
                            if is_safe_thumbnail_url(video.get("thumbnail", "")):
                                st.image(video["thumbnail"], use_container_width=True)
                            st.markdown(
                                f"**{video['title'][:45]}{'…' if len(video['title'])>45 else ''}**"
                            )
                            st.caption(f"📺 {video['channel']}")
                            m1, m2 = st.columns(2)
                            m1.metric("👁", format_count(video["view_count"]))
                            m2.metric("⏱", format_duration(video["duration"]))
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.link_button(t("watch_btn"), video["url"], use_container_width=True)
                            with col_b:
                                if st.button(
                                    t("select_btn"),
                                    key=f"sel_{video['id']}",
                                    use_container_width=True,
                                    type="primary",
                                ):
                                    st.session_state["current_url"] = video["url"]
                                    st.rerun()

# 讀取當前選中的 URL
if not video_url:
    video_url = st.session_state.get("current_url", "")

if not video_url:
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2：基本分析（免費）
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown(
    f'<span class="step-badge">STEP 2</span> **{t("step2_title")}** <span class="free-badge">FREE</span>',
    unsafe_allow_html=True,
)

_ig = st.session_state.get("ig_session", "")


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_info(url, ig):
    return get_video_info(url, ig)


with st.spinner(t("loading_info")):
    info = _fetch_info(video_url, _ig)

if "error" in info:
    st.error(f"❌ {info['error']}")
    if "429" in info["error"] or "instagram" in video_url.lower():
        st.info(t("ig_hint"))
    if st.button(t("change_video")):
        st.session_state.pop("current_url", None)
        st.rerun()
    st.stop()

# 記錄分析事件
track("analyze_video", {"platform": info.get("platform", "Unknown"), "title": info.get("title", "")[:30]})
add_history(video_url, info["title"], info["platform"], info["view_count"], info["thumbnail"])

# ── 影片資訊卡
col_img, col_meta = st.columns([1, 2])
with col_img:
    if is_safe_thumbnail_url(info.get("thumbnail", "")):
        st.image(info["thumbnail"], use_container_width=True)
    st.link_button(t("watch_original"), info["webpage_url"], use_container_width=True)

with col_meta:
    st.markdown(f"## {info['title']}")
    ch = (
        f"[{info['channel']}]({info['channel_url']})"
        if info.get("channel_url")
        else info["channel"]
    )
    st.markdown(f"📺 {ch}")
    if info.get("channel_follower_count"):
        st.markdown(f"👥 {t('subscribers')}：**{format_count(info['channel_follower_count'])}**")
    if info.get("upload_date"):
        st.markdown(f"📅 {format_date(info['upload_date'])}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👁", format_count(info["view_count"]))
    m2.metric("👍", format_count(info["like_count"]))
    m3.metric("💬", format_count(info["comment_count"]))
    m4.metric("⏱", format_duration(info["duration"]))

    if info.get("description"):
        with st.expander(t("description_expander")):
            st.text(info["description"][:1000])

# ── 逐字稿（免費）
st.markdown(t("transcript_header"))
sub_col, whisper_col = st.columns(2)
with sub_col:
    get_sub = st.button(t("get_subtitle_btn"), use_container_width=True)
with whisper_col:
    get_whisper = st.button(t("whisper_btn"), use_container_width=True, help=t("whisper_help"))

transcript_text = ""

if get_sub:
    track("get_transcript", {"platform": info.get("platform", "")})
    with st.spinner(t("getting_transcript")):
        entries, lang = get_transcript(video_url, ig_session=_ig)
    if not entries:
        st.warning(t("no_subtitles"))
    else:
        transcript_text = " ".join(e["text"] for e in entries)
        st.success(f"✅ {lang} — {len(entries)} segments")
        st.text_area("📜", transcript_text, height=250)
        st.session_state["transcript"] = transcript_text

if get_whisper:
    track("whisper_transcribe", {"platform": info.get("platform", "")})
    with st.spinner(t("downloading_audio")):
        try:
            tmpdir = tempfile.mkdtemp()
            audio_path = download_audio(video_url, tmpdir)
        except Exception as e:
            st.error(t("audio_fail", e=e))
            audio_path = None
    if audio_path:
        with st.spinner(f"Whisper ({whisper_model})…"):
            try:
                entries, lang = transcribe_with_whisper(audio_path, whisper_model)
                transcript_text = " ".join(e["text"] for e in entries)
                st.success(f"✅ {lang}")
                st.text_area("Whisper", transcript_text, height=250)
                st.session_state["transcript"] = transcript_text
            except Exception as e:
                st.error(t("whisper_fail", e=e))

# ── 翻譯
if st.session_state.get("transcript") or transcript_text:
    _txt = transcript_text or st.session_state.get("transcript", "")
    st.markdown(t("translate_header"))
    if using_free_translation():
        st.caption(t("free_translation_notice"))
    lang_choice = st.selectbox(
        "lang",
        ["繁體中文", "简体中文", "English", "日本語", "한국어",
         "Español", "Français", "Deutsch", "ภาษาไทย", "Tiếng Việt"],
        label_visibility="collapsed",
        key="trans_lang",
    )
    if st.button(t("translate_btn", lang=lang_choice), use_container_width=True):
        track("translate", {"lang": lang_choice})
        with st.spinner(t("translating")):
            try:
                result = translate_text(_txt, lang_choice)
                st.text_area("🌐", result, height=250)
                st.download_button(
                    t("download_translation"), result,
                    file_name="translation.txt", mime="text/plain",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(t("translation_fail", e=e))

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3：進階工具（PRO）
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown(
    f'<span class="step-badge">STEP 3</span> **{t("step3_title")}** <span class="pro-badge">PRO</span>',
    unsafe_allow_html=True,
)

if not is_unlocked():
    render_unlock_prompt("創作工具")
    st.stop()

# ── PRO tabs
(pro_tab1, pro_tab2, pro_tab_comments, pro_tab_ads, pro_tab3,
 pro_tab_faceless, pro_tab4, pro_tab5) = st.tabs([
    t("tab_analysis"),
    t("tab_recreation"),
    t("tab_comments"),
    t("tab_ads"),
    t("tab_tools"),
    t("tab_faceless"),
    t("tab_favorites"),
    t("tab_history"),
])

_transcript = st.session_state.get("transcript", "")


def _need_key() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error(t("need_api_key"))
        return True
    return False


# ── PRO TAB 1：爆款分析 + 模板
with pro_tab1:
    st.caption("AI 分析爆款原因，生成可複製的鉤子與拍攝模板")
    tmpl_platform = st.selectbox(
        "平台",
        ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "小紅書", "Bilibili"],
        key="tmpl_p",
    )
    tmpl_niche = st.text_input(t("your_topic"), placeholder="e.g. tech unboxing, fitness", key="tmpl_n")

    if st.button(t("generate_template_btn"), type="primary", use_container_width=True):
        if not _need_key():
            track("generate_template", {"platform": tmpl_platform, "topic": tmpl_niche})
            with st.spinner(t("analyzing")):
                try:
                    result = analyze_and_generate_templates(
                        title=info["title"], transcript=_transcript,
                        view_count=info["view_count"], like_count=info["like_count"],
                        channel=info["channel"], platform=tmpl_platform,
                        user_niche=tmpl_niche,
                    )
                    t1, t2, t3, t4, t5, t6 = st.tabs([
                        "🔥 爆款原因", "🪝 鉤子", "🎬 拍攝模板", "✂️ 剪輯", "📐 標題公式", "💡 主題靈感",
                    ])
                    with t1: st.markdown(result["virality_reasons"] or result["raw"])
                    with t2: st.markdown(result["hooks"])
                    with t3: st.markdown(result["shooting_template"])
                    with t4: st.markdown(result["editing_tips"])
                    with t5: st.markdown(result["title_formulas"])
                    with t6: st.markdown(result["topic_ideas"])

                    col_dl, col_fav = st.columns(2)
                    with col_dl:
                        st.download_button(
                            t("download_btn"), result["raw"],
                            file_name="template.md", mime="text/markdown",
                            use_container_width=True,
                        )
                    with col_fav:
                        if st.button(t("save_btn"), use_container_width=True, key="fav_tmpl"):
                            add_favorite("template", info["title"][:40], result["raw"])
                            track("add_favorite", {"type": "template"})
                            st.success(t("saved_msg"))
                except Exception as e:
                    st.error(t("gen_fail", e=e))

    st.divider()
    st.markdown("#### 🪝 Hook Generator")
    hk1, hk2, hk3 = st.columns(3)
    with hk1:
        hk_topic = st.text_input("主題", placeholder="我用AI一個月賺10萬", key="hk_t")
    with hk2:
        hk_platform = st.selectbox("平台", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube"], key="hk_p")
    with hk3:
        hk_style = st.selectbox("風格", ["好奇心", "震驚開場", "痛點共鳴", "反直覺", "數字衝擊"], key="hk_s")

    if st.button(t("gen_hook_btn"), type="primary", use_container_width=True):
        if not _need_key():
            track("custom_hook", {"platform": hk_platform, "topic": hk_topic})
            with st.spinner(t("generating")):
                hooks = generate_custom_hook(hk_topic, hk_platform, hk_style)
            st.markdown(hooks)
            if st.button(t("save_btn"), key="fav_hook"):
                add_favorite("hook", hk_topic[:40], hooks)
                st.success(t("saved_msg"))


# ── PRO TAB 2：重現指南
with pro_tab2:
    st.caption("AI 告訴你怎麼拍出一樣效果，含 Sora / Kling AI 生成 Prompt")
    rc_platform = st.selectbox(
        "平台",
        ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "小紅書", "Bilibili"],
        key="rc_p",
    )
    rc_tools = st.text_input(t("your_gear"), placeholder=t("gear_placeholder"), key="rc_t")

    if st.button(t("gen_recreation_btn"), type="primary", use_container_width=True):
        if not _need_key():
            track("recreation_guide", {"platform": rc_platform})
            with st.spinner(t("generating")):
                try:
                    rc_result = generate_recreation_guide(
                        title=info["title"], transcript=_transcript,
                        description=info.get("description", ""),
                        view_count=info["view_count"], platform=rc_platform,
                        thumbnail_url=info.get("thumbnail", ""), user_tools=rc_tools,
                    )
                    t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
                        "📱 拍攝", "💡 燈光", "📝 腳本", "✂️ 剪輯",
                        "🎵 音樂", "📦 器材", "🤖 AI Prompt", "🪜 步驟",
                    ])
                    with t1: st.markdown(rc_result["filming_setup"])
                    with t2: st.markdown(rc_result["lighting_scene"])
                    with t3: st.markdown(rc_result["script_breakdown"])
                    with t4: st.markdown(rc_result["editing"])
                    with t5: st.markdown(rc_result["music"])
                    with t6: st.markdown(rc_result["equipment"])
                    with t7: st.markdown(rc_result["ai_prompts"])
                    with t8: st.markdown(rc_result["steps"])

                    col_dl2, col_fav2 = st.columns(2)
                    with col_dl2:
                        st.download_button(
                            t("download_btn"), rc_result["raw"],
                            file_name="recreation.md", mime="text/markdown",
                            use_container_width=True,
                        )
                    with col_fav2:
                        if st.button(t("save_btn"), use_container_width=True, key="fav_rc"):
                            add_favorite("recreation", info["title"][:40], rc_result["raw"])
                            st.success(t("saved_msg"))
                except Exception as e:
                    st.error(t("gen_fail", e=e))


# ── PRO TAB：留言挖掘 → 內容點子
with pro_tab_comments:
    st.caption(t("comments_caption"))

    cm_c1, cm_c2 = st.columns([2, 1])
    with cm_c1:
        cm_max = st.slider(t("max_comments_label"), 30, 200, 100, 10, key="cm_max")
    with cm_c2:
        cm_lang = st.selectbox(
            "lang",
            ["繁體中文", "简体中文", "English", "Español"],
            label_visibility="collapsed",
            key="cm_lang",
        )

    if st.button(t("fetch_comments_btn"), type="primary", use_container_width=True):
        if not _need_key():
            track("mine_comments", {"platform": info.get("platform", ""), "max": cm_max})
            with st.spinner(t("fetching_comments")):
                comments, err = get_comments(video_url, cm_max, ig_session=_ig)

            if err or not comments:
                st.warning(t("no_comments", e=err or "沒有留言"))
            else:
                st.success(t("comments_found", n=len(comments)))
                st.session_state["mined_comments"] = comments

                with st.expander(t("top_comments_expander")):
                    for c in comments[:20]:
                        st.markdown(f"**👍 {format_count(c['like_count'])}** · {c['text'][:200]}")

                with st.spinner(t("mining_comments")):
                    try:
                        cm_result = mine_comments(comments, info.get("title", ""), cm_lang)

                        ct1, ct2, ct3, ct4 = st.tabs([
                            "🎯 風向", "😣 痛點", "❓ 疑問", "💡 影片點子",
                        ])
                        with ct1: st.markdown(cm_result["sentiment"] or cm_result["raw"])
                        with ct2: st.markdown(cm_result["pain_points"])
                        with ct3: st.markdown(cm_result["questions"])
                        with ct4: st.markdown(cm_result["ideas"])

                        st.divider()
                        with st.expander("📄 完整分析報告"):
                            st.markdown(cm_result["raw"])

                        col_cd, col_cf = st.columns(2)
                        with col_cd:
                            st.download_button(
                                t("download_btn"), cm_result["raw"],
                                file_name="comment_insights.md", mime="text/markdown",
                                use_container_width=True, key="dl_cm",
                            )
                        with col_cf:
                            if st.button(t("save_btn"), use_container_width=True, key="fav_cm"):
                                add_favorite("other", f"留言挖掘_{info['title'][:30]}", cm_result["raw"])
                                st.success(t("saved_msg"))
                    except Exception as e:
                        st.error(t("gen_fail", e=e))


# ── PRO TAB：廣告投放顧問
with pro_tab_ads:
    st.caption(t("ads_caption"))

    ad_r1c1, ad_r1c2 = st.columns(2)
    with ad_r1c1:
        ad_platform = st.selectbox(
            "platform",
            ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "小紅書", "Facebook", "Bilibili"],
            key="ad_platform", label_visibility="collapsed",
        )
    with ad_r1c2:
        ad_goal = st.selectbox(t("ad_goal_label"), GOAL_OPTIONS, index=3, key="ad_goal")

    ad_product = st.text_input(
        t("ad_product_label"),
        placeholder=t("ad_product_placeholder"),
        key="ad_product",
    )

    ad_r2c1, ad_r2c2, ad_r2c3 = st.columns([1.4, 1, 1])
    with ad_r2c1:
        ad_market = st.text_input(t("ad_market_label"), value="台灣", key="ad_market")
    with ad_r2c2:
        ad_budget = st.text_input(t("ad_budget_label"), value="10000", key="ad_budget")
    with ad_r2c3:
        ad_currency = st.selectbox(t("ad_currency_label"), CURRENCY_OPTIONS, key="ad_currency")

    ad_lang = st.selectbox(
        "ad_lang",
        ["繁體中文", "简体中文", "English", "Español"],
        label_visibility="collapsed", key="ad_lang",
    )

    if st.button(t("gen_ad_strategy_btn"), type="primary", use_container_width=True):
        if not _need_key():
            track("ad_strategy", {"platform": ad_platform, "goal": ad_goal, "budget": ad_budget})
            with st.spinner(t("generating_ads")):
                try:
                    ad_result = generate_ad_strategy(
                        title=info["title"], transcript=_transcript,
                        description=info.get("description", ""),
                        platform=ad_platform, goal=ad_goal,
                        monthly_budget=ad_budget, currency=ad_currency,
                        product=ad_product, target_market=ad_market,
                        output_lang=ad_lang,
                    )

                    at1, at2, at3, at4, at5, at6 = st.tabs([
                        "📊 總覽 + 平台", "👥 受眾", "✍️ 文案 + 素材",
                        "💰 預算出價", "📈 KPI + 路線圖", "⚠️ 避雷 + 清單",
                    ])
                    with at1:
                        st.markdown(ad_result["overview"] or ad_result["raw"])
                        st.markdown(ad_result["platform_split"])
                    with at2:
                        st.markdown(ad_result["targeting"])
                    with at3:
                        st.markdown(ad_result["ad_copy"])
                        st.divider()
                        st.markdown(ad_result["creative"])
                    with at4:
                        st.markdown(ad_result["bidding"])
                    with at5:
                        st.markdown(ad_result["kpi"])
                        st.divider()
                        st.markdown(ad_result["roadmap"])
                    with at6:
                        st.markdown(ad_result["mistakes"])
                        st.divider()
                        st.markdown(ad_result["checklist"])

                    st.divider()
                    with st.expander("📄 完整廣告策略報告"):
                        st.markdown(ad_result["raw"])

                    col_ad, col_af = st.columns(2)
                    with col_ad:
                        st.download_button(
                            t("download_btn"), ad_result["raw"],
                            file_name="ad_strategy.md", mime="text/markdown",
                            use_container_width=True, key="dl_ad",
                        )
                    with col_af:
                        if st.button(t("save_btn"), use_container_width=True, key="fav_ad"):
                            add_favorite("other", f"廣告策略_{info['title'][:30]}", ad_result["raw"])
                            st.success(t("saved_msg"))
                except Exception as e:
                    st.error(t("gen_fail", e=e))


# ── PRO TAB 3：內容工具
with pro_tab3:
    tool = st.radio(
        "tool",
        [t("ab_title"), t("thumbnail_copy"), t("calendar_30"), t("platform_adapt"), t("best_time")],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    def _gen_result(label: str, fn, fav_type: str, event_type: str, details: dict, *args, **kwargs):
        if _need_key():
            return
        track(event_type, details)
        with st.spinner(t("generating")):
            r = fn(*args, **kwargs)
        st.markdown(r)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                t("download_btn"), r,
                file_name=f"{label}.txt", mime="text/plain",
                use_container_width=True, key=f"dl_{label}",
            )
        with c2:
            if st.button(t("save_btn"), key=f"sv_{label}_{len(r)}", use_container_width=True):
                add_favorite(fav_type, label, r)
                st.success(t("saved_msg"))

    if tool == t("ab_title"):
        ab_t = st.text_input("t", value=info["title"], key="ab_t2", label_visibility="collapsed")
        ab_p = st.selectbox("p", list(PLATFORMS.keys()), key="ab_p2", label_visibility="collapsed")
        if st.button(f"✨ {t('ab_title')}", type="primary", use_container_width=True):
            _gen_result("AB", generate_ab_titles, "title", "ab_titles",
                        {"platform": ab_p, "topic": ab_t[:20]}, ab_t, ab_p)

    elif tool == t("thumbnail_copy"):
        tc_t = st.text_input("t", value=info["title"], key="tc_t2", label_visibility="collapsed")
        tc_s = st.selectbox("s", ["震驚", "好奇", "情緒", "數字", "對比"], key="tc_s2", label_visibility="collapsed")
        if st.button(f"✨ {t('thumbnail_copy')}", type="primary", use_container_width=True):
            _gen_result("thumbnail", generate_thumbnail_copy, "other", "thumbnail_copy",
                        {"topic": tc_t[:20]}, tc_t, tc_s)

    elif tool == t("calendar_30"):
        cal_n = st.text_input("n", placeholder="個人理財、健身…", key="cal_n2", label_visibility="collapsed")
        cal_p = st.selectbox("p", list(PLATFORMS.keys()), key="cal_p2", label_visibility="collapsed")
        if st.button(f"📅 {t('calendar_30')}", type="primary", use_container_width=True):
            _gen_result("calendar", generate_content_calendar, "calendar", "content_calendar",
                        {"platform": cal_p, "topic": cal_n[:20]}, cal_n, cal_p)

    elif tool == t("platform_adapt"):
        pa_c = st.text_area(
            "c", value=_transcript[:500] if _transcript else "",
            height=120, key="pa_c2", label_visibility="collapsed",
        )
        pa_p = st.selectbox("p", list(PLATFORMS.keys()), key="pa_p2", label_visibility="collapsed")
        if st.button(f"🔄 {t('platform_adapt')}", type="primary", use_container_width=True):
            _gen_result("adapt", adapt_for_platforms, "template", "platform_adapt",
                        {"platform": pa_p}, pa_c, pa_p)

    elif tool == t("best_time"):
        pt1, pt2, pt3 = st.columns(3)
        with pt1: pt_n = st.text_input("n", placeholder="Tech", key="pt_n2", label_visibility="collapsed")
        with pt2: pt_a = st.text_input("a", placeholder="18-35", key="pt_a2", label_visibility="collapsed")
        with pt3: pt_p = st.selectbox("p", list(PLATFORMS.keys()), key="pt_p2", label_visibility="collapsed")
        if st.button(f"⏰ {t('best_time')}", type="primary", use_container_width=True):
            _gen_result("best_time", analyze_best_posting_time, "other", "posting_time",
                        {"platform": pt_p, "topic": pt_n[:20]}, pt_n, pt_a, pt_p)


# ── PRO TAB：無臉頻道工作坊
with pro_tab_faceless:
    st.caption(t("faceless_caption"))

    faceless_tool = st.radio(
        "faceless_tool",
        [t("niche_finder"), t("script_gen"), t("seo_package"), t("thumbnail_prompt"), t("storyboard")],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    def _faceless_result(label: str, result: str, fav_type: str = "other"):
        st.markdown(result)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇ 下載", result,
                file_name=f"{label}.txt", mime="text/plain",
                use_container_width=True, key=f"dl_f_{label}",
            )
        with c2:
            if st.button(t("save_btn"), key=f"sv_f_{label}_{len(result)}", use_container_width=True):
                add_favorite(fav_type, label, result)
                st.success(t("saved_msg"))

    # 利基市場發現器
    if faceless_tool == t("niche_finder"):
        st.markdown("### 🔍 利基市場發現器")
        st.caption("找出適合華語市場的高獲利無臉頻道主題")
        nc1, nc2 = st.columns([2, 1])
        with nc1:
            niche_cat = st.selectbox("類別偏好", NICHE_CATEGORIES, key="niche_cat")
        with nc2:
            niche_lang = st.selectbox("輸出語言", ["繁體中文", "简体中文"], key="niche_lang")
        if st.button("🔍 發現利基市場", type="primary", use_container_width=True):
            if not _need_key():
                track("find_niches", {"category": niche_cat})
                with st.spinner("AI 分析熱門無臉頻道利基中…約需 20 秒"):
                    r = find_niches(niche_cat, niche_lang)
                _faceless_result(f"利基市場_{niche_cat}", r, "other")

    # AI 腳本生成
    elif faceless_tool == t("script_gen"):
        st.markdown(f"### {t('script_gen')}")
        sc1 = st.text_input("topic", placeholder="例如：古埃及法老最神秘的詛咒", key="sc_topic", label_visibility="collapsed")
        sc2, sc3, sc4 = st.columns(3)
        with sc2:
            sc_length = st.selectbox("len", list(SCRIPT_LENGTHS.keys()), index=1, key="sc_len", label_visibility="collapsed")
        with sc3:
            sc_style = st.selectbox("style", SCRIPT_STYLES, key="sc_style", label_visibility="collapsed")
        with sc4:
            sc_lang = st.selectbox("lang", ["繁體中文", "简体中文", "English"], key="sc_lang", label_visibility="collapsed")
        if st.button(f"📝 {t('script_gen')}", type="primary", use_container_width=True):
            if not sc1:
                st.warning("⚠️")
            elif not _need_key():
                track("generate_script", {"topic": sc1[:30], "length": sc_length})
                with st.spinner(t("generating")):
                    r = generate_script(sc1, sc_length, sc_style, sc_lang)
                st.session_state["faceless_script"] = r
                st.session_state["faceless_topic"] = sc1
                _faceless_result(f"script_{sc1[:20]}", r, "template")
                st.info("💡 Script generated! Switch to SEO Package or AI Storyboard to continue.")

    # SEO 優化包
    elif faceless_tool == t("seo_package"):
        st.markdown(f"### {t('seo_package')}")
        seo_topic = st.text_input(
            "topic",
            value=st.session_state.get("faceless_topic", ""),
            placeholder="例如：古埃及法老最神秘的詛咒",
            key="seo_topic", label_visibility="collapsed",
        )
        seo_script = st.text_area(
            "script",
            value=st.session_state.get("faceless_script", "")[:300],
            height=80, key="seo_script", label_visibility="collapsed",
        )
        seo_lang = st.selectbox("lang", ["繁體中文", "简体中文"], key="seo_lang", label_visibility="collapsed")
        if st.button(f"🔑 {t('seo_package')}", type="primary", use_container_width=True):
            if not seo_topic:
                st.warning("⚠️")
            elif not _need_key():
                track("seo_package", {"topic": seo_topic[:30]})
                with st.spinner(t("generating")):
                    r = generate_seo_package(seo_topic, seo_script, seo_lang)
                _faceless_result(f"SEO_{seo_topic[:20]}", r, "other")

    # 縮圖 Prompt
    elif faceless_tool == t("thumbnail_prompt"):
        st.markdown(f"### {t('thumbnail_prompt')}")
        st.caption("Midjourney / DALL-E / Stable Diffusion")
        th1, th2 = st.columns([3, 1])
        with th1:
            th_topic = st.text_input(
                "topic",
                value=st.session_state.get("faceless_topic", ""),
                placeholder="例如：古埃及法老最神秘的詛咒",
                key="th_topic", label_visibility="collapsed",
            )
        with th2:
            th_style = st.selectbox("style", THUMBNAIL_STYLES, key="th_style", label_visibility="collapsed")
        if st.button(f"🖼 {t('thumbnail_prompt')}", type="primary", use_container_width=True):
            if not th_topic:
                st.warning("⚠️")
            elif not _need_key():
                track("thumbnail_prompt", {"topic": th_topic[:30], "style": th_style})
                with st.spinner(t("generating")):
                    r = generate_thumbnail_prompts(th_topic, th_style)
                _faceless_result(f"thumbnail_{th_topic[:20]}", r, "other")

    # AI 分鏡腳本
    elif faceless_tool == t("storyboard"):
        st.markdown(f"### {t('storyboard')}")
        st.caption("Kling / Sora / Runway AI Video Prompt")
        sb_script = st.text_area(
            "貼上你的影片腳本",
            value=st.session_state.get("faceless_script", ""),
            height=200,
            placeholder="貼上用「AI 腳本生成」產生的腳本，或自己撰寫的腳本",
            key="sb_script",
        )
        sb_style = st.selectbox(
            "視覺風格",
            ["AI 動畫風格", "電影紀錄片風格", "真實感攝影風格", "暗黑奇幻風", "科幻未來風", "古典歷史風"],
            key="sb_style",
        )
        if st.button(f"🎬 {t('storyboard')}", type="primary", use_container_width=True):
            if not sb_script.strip():
                st.warning("⚠️")
            elif not _need_key():
                track("storyboard", {"style": sb_style})
                with st.spinner(t("generating")):
                    r = generate_storyboard(sb_script, sb_style)
                _faceless_result("storyboard", r, "template")
                st.info("💡 Copy each scene's AI Prompt → paste into Kling AI / Runway Gen-3 / Sora")


# ── PRO TAB 4：收藏
with pro_tab4:
    favs = get_favorites()
    if not favs:
        st.info(t("no_favorites"))
    else:
        st.caption(t("fav_count", n=len(favs)))
        for i, fav in enumerate(favs):
            type_label = FAVORITE_TYPES.get(fav["type"], "📌")
            with st.expander(f"{type_label} {fav['title']} — {fav['saved_at']}"):
                st.markdown(fav["content"][:600] + ("…" if len(fav["content"]) > 600 else ""))
                fc1, fc2 = st.columns(2)
                with fc1:
                    st.download_button(
                        t("download_btn"), fav["content"],
                        file_name=f"{fav['title'][:30]}.txt", mime="text/plain",
                        key=f"dl_fav_{i}", use_container_width=True,
                    )
                with fc2:
                    if st.button(t("delete_btn"), key=f"del_fav_{i}", use_container_width=True):
                        remove_favorite(i)
                        st.rerun()
        if st.button(t("clear_favorites"), use_container_width=True):
            from storage import clear_favorites
            clear_favorites()
            st.rerun()


# ── PRO TAB 5：歷史
with pro_tab5:
    history = get_history()
    if not history:
        st.info(t("no_history"))
    else:
        st.caption(t("history_count", n=len(history)))
        for item in history:
            with st.container(border=True):
                hc1, hc2 = st.columns([1, 4])
                with hc1:
                    if item.get("thumbnail"):
                        st.image(item["thumbnail"], use_container_width=True)
                with hc2:
                    st.markdown(f"**{item['title'][:50]}**")
                    st.caption(
                        f"👁 {format_count(item['view_count'])} · "
                        f"{item['platform']} · {item['analyzed_at']}"
                    )
                    if st.button(
                        t("reanalyze_btn"),
                        key=f"re_{item['url'][:30]}",
                        use_container_width=True,
                    ):
                        st.session_state["current_url"] = item["url"]
                        st.rerun()
        if st.button(t("clear_history"), use_container_width=True):
            clear_history()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 頁面底部：用戶體驗問卷
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
with st.expander(t("survey_expander"), expanded=False):
    render_survey()
