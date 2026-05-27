import os
import sys
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from search import search_videos, format_count, format_duration, format_date, PLATFORMS
from analyzer import get_video_info, get_transcript, download_audio, transcribe_with_whisper
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
from security import sanitize_prompt_input
from survey import render_survey, render_admin_dashboard
from analytics import track, render_analytics_dashboard

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
    st.session_state["dark_mode"] = True  # 預設深色模式


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
        '<div class="hero-title" style="font-size:1.5rem; padding: 0.5rem 0;">🎯 爆款影片獵手</div>',
        unsafe_allow_html=True,
    )
    st.caption("為內容創作者打造的爆款分析工具")
    st.divider()

    # ── 深淺色切換
    mode_label = "🌙 深色模式" if st.session_state["dark_mode"] else "☀️ 淺色模式"
    if st.button(mode_label, use_container_width=True):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()

    st.divider()

    # ── 方案狀態
    if is_unlocked():
        st.success("✅ 進階版已解鎖", icon="🔓")
        if st.button("登出進階版", use_container_width=True):
            from paywall import lock
            lock()
            st.rerun()
    else:
        with st.expander("🔒 解鎖進階功能"):
            code_in = st.text_input("Access Code", placeholder="VH-XXXX-XXXX", key="sidebar_code")
            if st.button("🔓 解鎖", type="primary", use_container_width=True):
                from paywall import try_unlock
                if try_unlock(code_in):
                    track("unlock_pro")
                    st.success("✅ 解鎖成功！")
                    st.rerun()
                else:
                    st.error("Code 不正確或已達嘗試上限")

        st.markdown('<p class="section-header">免費功能</p>', unsafe_allow_html=True)
        for f in PLAN_FEATURES["free"]:
            st.markdown(f)
        st.markdown('<p class="section-header" style="margin-top:0.75rem;">進階功能 🔥</p>', unsafe_allow_html=True)
        for f in PLAN_FEATURES["pro"]:
            st.markdown(f)

    st.divider()
    st.markdown('<p class="section-header">⚙️ 設定</p>', unsafe_allow_html=True)

    _env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if _env_key:
        st.success("✅ AI 功能已啟用", icon="🤖")
    else:
        api_key = st.text_input(
            "Anthropic API Key（選填）",
            type="password",
            placeholder="sk-ant-...",
            help="有填 Key → Claude 翻譯；沒填 → Google 翻譯（免費）",
        )
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

    ig_session = st.text_input(
        "Instagram Session ID（選填）",
        type="password",
        placeholder="貼上 sessionid cookie 值",
        help="分析 Instagram Reels 需要",
        key="ig_session",
    )

    whisper_model = st.selectbox(
        "🎙 Whisper 模型",
        ["tiny", "base", "small", "medium"],
        index=1,
        help="模型越大越準確，但速度較慢",
    )

    st.divider()

    # ── 管理員工具
    _admin_key = os.environ.get("ADMIN_KEY", "")
    if _admin_key:
        with st.expander("🔧 管理員工具"):
            admin_input = st.text_input("管理員密碼", type="password", key="admin_pw")
            if admin_input == _admin_key:
                admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📊 使用分析", "💬 問卷", "🔑 Access Code"])

                with admin_tab1:
                    render_analytics_dashboard()

                with admin_tab2:
                    render_admin_dashboard()

                with admin_tab3:
                    import secrets, string
                    num_codes = st.number_input("產生幾組", min_value=1, max_value=50, value=5, step=1)
                    if st.button("產生 Access Code", use_container_width=True, type="primary"):
                        codes = []
                        for _ in range(int(num_codes)):
                            p1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                            p2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                            codes.append(f"VH-{p1}-{p2}")
                        st.code("\n".join(codes))
                        st.caption("複製後加入 Streamlit Secrets 的 ACCESS_CODES（逗號分隔）")

            elif admin_input:
                st.error("密碼錯誤")

# ══════════════════════════════════════════════════════════════════════════════
# 主標題區
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    '<h1 class="hero-title">🎯 爆款影片獵手</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:1.05rem; color: var(--text-color, #888); margin-top: 0.2rem; margin-bottom: 1.5rem;">'
    '找到爆款 → 理解為什麼爆 → 做出你的版本</p>',
    unsafe_allow_html=True,
)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1：輸入影片
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    '<span class="step-badge">STEP 1</span> **找到你的靈感影片**',
    unsafe_allow_html=True,
)

input_mode = st.radio(
    "輸入方式",
    ["🔗 貼上連結", "🔍 關鍵字搜尋"],
    horizontal=True,
    label_visibility="collapsed",
)

video_url = None

if input_mode == "🔗 貼上連結":
    c1, c2 = st.columns([4, 1])
    with c1:
        url_input = st.text_input(
            "影片連結",
            value=st.session_state.get("analyze_url", ""),
            placeholder="貼上 YouTube / TikTok / Instagram / Bilibili 連結…",
            label_visibility="collapsed",
        )
    with c2:
        go_btn = st.button("分析 →", type="primary", use_container_width=True)

    if go_btn and url_input.strip():
        video_url = url_input.strip()
        st.session_state["current_url"] = video_url

else:
    sc1, sc2, sc3 = st.columns([3, 1.5, 1])
    with sc1:
        keyword = st.text_input(
            "關鍵字",
            placeholder="例如：AI副業、健身教學…",
            label_visibility="collapsed",
        )
    with sc2:
        platform = st.selectbox("平台", list(PLATFORMS.keys()), label_visibility="collapsed")
    with sc3:
        search_btn = st.button("🔍 搜尋", type="primary", use_container_width=True)

    if search_btn and keyword.strip():
        track("search_video", {"platform": platform, "keyword": keyword.strip()})
        with st.spinner(f"搜尋 {platform} 爆款中…"):
            videos = search_videos(keyword.strip(), platform, 9)

        if not videos:
            st.error("沒有找到影片，換個關鍵字試試")
        else:
            st.success(f"✅ 找到 **{len(videos)}** 部影片，點「選這部分析」繼續")
            cols_per_row = 3
            for row_start in range(0, len(videos), cols_per_row):
                row = videos[row_start: row_start + cols_per_row]
                cols = st.columns(cols_per_row)
                for col, video in zip(cols, row):
                    with col:
                        with st.container(border=True):
                            if video["thumbnail"]:
                                st.image(video["thumbnail"], use_container_width=True)
                            st.markdown(
                                f"**{video['title'][:45]}{'…' if len(video['title'])>45 else ''}**"
                            )
                            st.caption(f"📺 {video['channel']}")
                            m1, m2 = st.columns(2)
                            m1.metric("👁 觀看", format_count(video["view_count"]))
                            m2.metric("⏱", format_duration(video["duration"]))
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.link_button("▶ 看影片", video["url"], use_container_width=True)
                            with col_b:
                                if st.button(
                                    "✅ 選這部",
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
    '<span class="step-badge">STEP 2</span> **分析影片** <span class="free-badge">免費</span>',
    unsafe_allow_html=True,
)

_ig = st.session_state.get("ig_session", "")


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_info(url, ig):
    return get_video_info(url, ig)


with st.spinner("讀取影片資訊中…"):
    info = _fetch_info(video_url, _ig)

if "error" in info:
    st.error(f"❌ 無法讀取影片：{info['error']}")
    if "429" in info["error"] or "instagram" in video_url.lower():
        st.info("💡 Instagram 需要 Session ID，請在左側欄「設定」中填入")
    if st.button("← 換一部影片"):
        st.session_state.pop("current_url", None)
        st.rerun()
    st.stop()

# 記錄分析事件
track("analyze_video", {"platform": info.get("platform", "Unknown"), "title": info.get("title", "")[:30]})
add_history(video_url, info["title"], info["platform"], info["view_count"], info["thumbnail"])

# ── 影片資訊卡
col_img, col_meta = st.columns([1, 2])
with col_img:
    if info["thumbnail"]:
        st.image(info["thumbnail"], use_container_width=True)
    st.link_button("▶ 觀看原影片", info["webpage_url"], use_container_width=True)

with col_meta:
    st.markdown(f"## {info['title']}")
    ch = (
        f"[{info['channel']}]({info['channel_url']})"
        if info.get("channel_url")
        else info["channel"]
    )
    st.markdown(f"📺 {ch}")
    if info.get("channel_follower_count"):
        st.markdown(f"👥 訂閱數：**{format_count(info['channel_follower_count'])}**")
    if info.get("upload_date"):
        st.markdown(f"📅 {format_date(info['upload_date'])}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👁 觀看", format_count(info["view_count"]))
    m2.metric("👍 按讚", format_count(info["like_count"]))
    m3.metric("💬 留言", format_count(info["comment_count"]))
    m4.metric("⏱ 時長", format_duration(info["duration"]))

    if info.get("description"):
        with st.expander("📝 影片描述"):
            st.text(info["description"][:1000])

# ── 逐字稿（免費）
st.markdown("#### 📜 逐字稿")
sub_col, whisper_col = st.columns(2)
with sub_col:
    get_sub = st.button("🗒 取得字幕逐字稿", use_container_width=True)
with whisper_col:
    get_whisper = st.button("🎙 Whisper 語音辨識", use_container_width=True, help="需要 ffmpeg")

transcript_text = ""

if get_sub:
    track("get_transcript", {"platform": info.get("platform", "")})
    with st.spinner("取得逐字稿中…"):
        entries, lang = get_transcript(video_url, ig_session=_ig)
    if not entries:
        st.warning("⚠️ 找不到字幕，試試 Whisper 語音辨識")
    else:
        transcript_text = " ".join(e["text"] for e in entries)
        st.success(f"✅ 語言：{lang}，共 {len(entries)} 段")
        st.text_area("逐字稿", transcript_text, height=250)
        st.session_state["transcript"] = transcript_text

if get_whisper:
    track("whisper_transcribe", {"platform": info.get("platform", "")})
    with st.spinner("下載音頻中…"):
        try:
            tmpdir = tempfile.mkdtemp()
            audio_path = download_audio(video_url, tmpdir)
        except Exception as e:
            st.error(f"❌ 音頻下載失敗：{e}")
            audio_path = None
    if audio_path:
        with st.spinner(f"Whisper 辨識中（{whisper_model}）…"):
            try:
                entries, lang = transcribe_with_whisper(audio_path, whisper_model)
                transcript_text = " ".join(e["text"] for e in entries)
                st.success(f"✅ 辨識語言：{lang}")
                st.text_area("Whisper 逐字稿", transcript_text, height=250)
                st.session_state["transcript"] = transcript_text
            except Exception as e:
                st.error(f"❌ Whisper 失敗：{e}")

# ── 翻譯
if st.session_state.get("transcript") or transcript_text:
    _txt = transcript_text or st.session_state.get("transcript", "")
    st.markdown("#### 🌐 翻譯逐字稿")
    if using_free_translation():
        st.caption("🆓 免費模式：使用 Google 翻譯 · 輸入 Anthropic API Key 切換 Claude 高品質翻譯")
    lang_choice = st.selectbox(
        "翻譯語言",
        list({
            "繁體中文": "", "简体中文": "", "English": "", "日本語": "",
            "한국어": "", "Español": "", "Français": "", "Deutsch": "",
            "ภาษาไทย": "", "Tiếng Việt": "",
        }),
        label_visibility="collapsed",
        key="trans_lang",
    )
    if st.button(f"🌐 翻譯為「{lang_choice}」", use_container_width=True):
        track("translate", {"lang": lang_choice})
        with st.spinner("翻譯中…"):
            try:
                result = translate_text(_txt, lang_choice)
                st.text_area("翻譯結果", result, height=250)
                st.download_button(
                    "⬇ 下載翻譯", result,
                    file_name="translation.txt", mime="text/plain",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ 翻譯失敗：{e}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3：進階工具（PRO）
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown(
    '<span class="step-badge">STEP 3</span> **生成你的版本** <span class="pro-badge">PRO</span>',
    unsafe_allow_html=True,
)

if not is_unlocked():
    render_unlock_prompt("創作工具")
    st.stop()

# ── PRO tabs
pro_tab1, pro_tab2, pro_tab3, pro_tab_faceless, pro_tab4, pro_tab5 = st.tabs([
    "🔥 爆款分析 + 模板",
    "🎥 重現指南",
    "✍️ 內容工具",
    "🤖 無臉頻道工作坊",
    "⭐ 我的收藏",
    "📋 分析歷史",
])

_transcript = st.session_state.get("transcript", "")


def _need_key() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("❌ 此功能需要 Anthropic API Key，請在左側欄填入")
        return True
    return False


# ── PRO TAB 1：爆款分析 + 模板
with pro_tab1:
    st.caption("AI 分析爆款原因，生成可複製的鉤子與拍攝模板")
    tmpl_platform = st.selectbox(
        "平台",
        ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "Bilibili"],
        key="tmpl_p",
    )
    tmpl_niche = st.text_input("你的創作主題（選填）", placeholder="例如：科技開箱、健身教學", key="tmpl_n")

    if st.button("🚀 生成爆款模板", type="primary", use_container_width=True):
        if not _need_key():
            track("generate_template", {"platform": tmpl_platform, "topic": tmpl_niche})
            with st.spinner("AI 分析中…約需 20 秒"):
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
                            "⬇ 下載完整模板", result["raw"],
                            file_name="template.md", mime="text/markdown",
                            use_container_width=True,
                        )
                    with col_fav:
                        if st.button("⭐ 收藏模板", use_container_width=True):
                            add_favorite("template", info["title"][:40], result["raw"])
                            track("add_favorite", {"type": "template"})
                            st.success("✅ 已收藏！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{e}")

    st.divider()
    st.markdown("#### 🪝 自訂鉤子生成器")
    hk1, hk2, hk3 = st.columns(3)
    with hk1:
        hk_topic = st.text_input("主題", placeholder="我用AI一個月賺10萬", key="hk_t")
    with hk2:
        hk_platform = st.selectbox("平台", ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube"], key="hk_p")
    with hk3:
        hk_style = st.selectbox("風格", ["好奇心", "震驚開場", "痛點共鳴", "反直覺", "數字衝擊"], key="hk_s")

    if st.button("✨ 生成鉤子", type="primary", use_container_width=True):
        if not _need_key():
            track("custom_hook", {"platform": hk_platform, "topic": hk_topic})
            with st.spinner("生成中…"):
                hooks = generate_custom_hook(hk_topic, hk_platform, hk_style)
            st.markdown(hooks)
            if st.button("⭐ 收藏這組鉤子", key="fav_hook"):
                add_favorite("hook", hk_topic[:40], hooks)
                st.success("✅ 已收藏！")


# ── PRO TAB 2：重現指南
with pro_tab2:
    st.caption("AI 告訴你怎麼拍出一樣效果，含 Sora / Kling AI 生成 Prompt")
    rc_platform = st.selectbox(
        "平台",
        ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "Bilibili"],
        key="rc_p",
    )
    rc_tools = st.text_input("你有哪些器材？", placeholder="iPhone 15、環形燈、剪映…", key="rc_t")

    if st.button("🎥 生成重現指南", type="primary", use_container_width=True):
        if not _need_key():
            track("recreation_guide", {"platform": rc_platform})
            with st.spinner("AI 生成中…約需 25 秒"):
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
                            "⬇ 下載指南", rc_result["raw"],
                            file_name="recreation.md", mime="text/markdown",
                            use_container_width=True,
                        )
                    with col_fav2:
                        if st.button("⭐ 收藏指南", use_container_width=True):
                            add_favorite("recreation", info["title"][:40], rc_result["raw"])
                            st.success("✅ 已收藏！")
                except Exception as e:
                    st.error(f"❌ 生成失敗：{e}")


# ── PRO TAB 3：內容工具
with pro_tab3:
    tool = st.radio(
        "工具",
        ["🔤 A/B 標題", "🖼 縮圖文案", "📅 30天日曆", "🔄 平台適配", "⏰ 最佳時段"],
        horizontal=True,
    )
    st.divider()

    def _gen_result(label: str, fn, fav_type: str, event_type: str, details: dict, *args, **kwargs):
        if _need_key():
            return
        track(event_type, details)
        with st.spinner("生成中…"):
            r = fn(*args, **kwargs)
        st.markdown(r)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇ 下載", r,
                file_name=f"{label}.txt", mime="text/plain",
                use_container_width=True, key=f"dl_{label}",
            )
        with c2:
            if st.button("⭐ 收藏", key=f"sv_{label}_{len(r)}", use_container_width=True):
                add_favorite(fav_type, label, r)
                st.success("✅ 已收藏！")

    if tool == "🔤 A/B 標題":
        ab_t = st.text_input("影片主題", value=info["title"], key="ab_t2")
        ab_p = st.selectbox("平台", list(PLATFORMS.keys()), key="ab_p2")
        if st.button("✨ 生成標題變體", type="primary", use_container_width=True):
            _gen_result("AB標題", generate_ab_titles, "title", "ab_titles",
                        {"platform": ab_p, "topic": ab_t[:20]}, ab_t, ab_p)

    elif tool == "🖼 縮圖文案":
        tc_t = st.text_input("影片主題", value=info["title"], key="tc_t2")
        tc_s = st.selectbox("風格", ["震驚", "好奇", "情緒", "數字", "對比"], key="tc_s2")
        if st.button("✨ 生成縮圖文案", type="primary", use_container_width=True):
            _gen_result("縮圖文案", generate_thumbnail_copy, "other", "thumbnail_copy",
                        {"topic": tc_t[:20]}, tc_t, tc_s)

    elif tool == "📅 30天日曆":
        cal_n = st.text_input("你的創作主題", placeholder="個人理財、健身…", key="cal_n2")
        cal_p = st.selectbox("平台", list(PLATFORMS.keys()), key="cal_p2")
        if st.button("📅 生成30天日曆", type="primary", use_container_width=True):
            _gen_result("30天日曆", generate_content_calendar, "calendar", "content_calendar",
                        {"platform": cal_p, "topic": cal_n[:20]}, cal_n, cal_p)

    elif tool == "🔄 平台適配":
        pa_c = st.text_area(
            "腳本或主題描述",
            value=_transcript[:500] if _transcript else "",
            height=120, key="pa_c2",
        )
        pa_p = st.selectbox("原始平台", list(PLATFORMS.keys()), key="pa_p2")
        if st.button("🔄 轉換各平台版本", type="primary", use_container_width=True):
            _gen_result("平台適配", adapt_for_platforms, "template", "platform_adapt",
                        {"platform": pa_p}, pa_c, pa_p)

    elif tool == "⏰ 最佳時段":
        pt1, pt2, pt3 = st.columns(3)
        with pt1: pt_n = st.text_input("主題", placeholder="科技開箱", key="pt_n2")
        with pt2: pt_a = st.text_input("目標受眾", placeholder="18-35歲台灣男性", key="pt_a2")
        with pt3: pt_p = st.selectbox("平台", list(PLATFORMS.keys()), key="pt_p2")
        if st.button("⏰ 分析最佳時段", type="primary", use_container_width=True):
            _gen_result("最佳時段", analyze_best_posting_time, "other", "posting_time",
                        {"platform": pt_p, "topic": pt_n[:20]}, pt_n, pt_a, pt_p)


# ── PRO TAB：無臉頻道工作坊
with pro_tab_faceless:
    st.caption("從找利基、寫腳本、SEO 到分鏡，一站式無臉頻道製作流程")

    faceless_tool = st.radio(
        "選擇工具",
        ["🔍 利基市場發現器", "📝 AI 腳本生成", "🔑 SEO 優化包", "🖼 縮圖 Prompt", "🎬 AI 分鏡腳本"],
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
            if st.button("⭐ 收藏", key=f"sv_f_{label}_{len(result)}", use_container_width=True):
                add_favorite(fav_type, label, result)
                st.success("✅ 已收藏！")

    # 利基市場發現器
    if faceless_tool == "🔍 利基市場發現器":
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
    elif faceless_tool == "📝 AI 腳本生成":
        st.markdown("### 📝 AI 腳本生成器")
        sc1 = st.text_input("影片主題或點子", placeholder="例如：古埃及法老最神秘的詛咒", key="sc_topic")
        sc2, sc3, sc4 = st.columns(3)
        with sc2:
            sc_length = st.selectbox("影片長度", list(SCRIPT_LENGTHS.keys()), index=1, key="sc_len")
        with sc3:
            sc_style = st.selectbox("腳本風格", SCRIPT_STYLES, key="sc_style")
        with sc4:
            sc_lang = st.selectbox("語言", ["繁體中文", "简体中文", "English"], key="sc_lang")
        if st.button("📝 生成完整腳本", type="primary", use_container_width=True):
            if not sc1:
                st.warning("⚠️ 請輸入影片主題")
            elif not _need_key():
                track("generate_script", {"topic": sc1[:30], "length": sc_length})
                with st.spinner("AI 撰寫腳本中…約需 25 秒"):
                    r = generate_script(sc1, sc_length, sc_style, sc_lang)
                st.session_state["faceless_script"] = r
                st.session_state["faceless_topic"] = sc1
                _faceless_result(f"腳本_{sc1[:20]}", r, "template")
                st.info("💡 腳本已生成！可直接切換到「SEO 優化包」或「AI 分鏡腳本」繼續製作")

    # SEO 優化包
    elif faceless_tool == "🔑 SEO 優化包":
        st.markdown("### 🔑 SEO 優化包")
        seo_topic = st.text_input(
            "影片主題",
            value=st.session_state.get("faceless_topic", ""),
            placeholder="例如：古埃及法老最神秘的詛咒",
            key="seo_topic",
        )
        seo_script = st.text_area(
            "腳本內容（選填，有了更準確）",
            value=st.session_state.get("faceless_script", "")[:300],
            height=80, key="seo_script",
        )
        seo_lang = st.selectbox("輸出語言", ["繁體中文", "简体中文"], key="seo_lang")
        if st.button("🔑 生成 SEO 優化包", type="primary", use_container_width=True):
            if not seo_topic:
                st.warning("⚠️ 請輸入影片主題")
            elif not _need_key():
                track("seo_package", {"topic": seo_topic[:30]})
                with st.spinner("AI 生成 SEO 優化包中…"):
                    r = generate_seo_package(seo_topic, seo_script, seo_lang)
                _faceless_result(f"SEO_{seo_topic[:20]}", r, "other")

    # 縮圖 Prompt
    elif faceless_tool == "🖼 縮圖 Prompt":
        st.markdown("### 🖼 縮圖生成 Prompt")
        st.caption("生成可貼入 Midjourney / DALL-E / Stable Diffusion 的縮圖提示詞")
        th1, th2 = st.columns([3, 1])
        with th1:
            th_topic = st.text_input(
                "影片主題",
                value=st.session_state.get("faceless_topic", ""),
                placeholder="例如：古埃及法老最神秘的詛咒",
                key="th_topic",
            )
        with th2:
            th_style = st.selectbox("縮圖風格", THUMBNAIL_STYLES, key="th_style")
        if st.button("🖼 生成縮圖 Prompt", type="primary", use_container_width=True):
            if not th_topic:
                st.warning("⚠️ 請輸入影片主題")
            elif not _need_key():
                track("thumbnail_prompt", {"topic": th_topic[:30], "style": th_style})
                with st.spinner("AI 設計縮圖方案中…"):
                    r = generate_thumbnail_prompts(th_topic, th_style)
                _faceless_result(f"縮圖_{th_topic[:20]}", r, "other")

    # AI 分鏡腳本
    elif faceless_tool == "🎬 AI 分鏡腳本":
        st.markdown("### 🎬 AI 分鏡腳本")
        st.caption("將腳本拆解成逐場景分鏡，每場景附 Kling / Sora / Runway 可用的 AI 影片 Prompt")
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
        if st.button("🎬 生成 AI 分鏡腳本", type="primary", use_container_width=True):
            if not sb_script.strip():
                st.warning("⚠️ 請貼上腳本內容")
            elif not _need_key():
                track("storyboard", {"style": sb_style})
                with st.spinner("AI 生成分鏡腳本中…約需 30 秒"):
                    r = generate_storyboard(sb_script, sb_style)
                _faceless_result("AI分鏡腳本", r, "template")
                st.info("💡 複製每個場景的 AI Prompt，貼入 Kling AI / Runway Gen-3 / Sora 即可生成影片片段")


# ── PRO TAB 4：收藏
with pro_tab4:
    favs = get_favorites()
    if not favs:
        st.info("💡 還沒有收藏，在各工具頁點「⭐ 收藏」即可")
    else:
        st.caption(f"共 {len(favs)} 個收藏")
        for i, fav in enumerate(favs):
            type_label = FAVORITE_TYPES.get(fav["type"], "📌")
            with st.expander(f"{type_label} {fav['title']} — {fav['saved_at']}"):
                st.markdown(fav["content"][:600] + ("…" if len(fav["content"]) > 600 else ""))
                fc1, fc2 = st.columns(2)
                with fc1:
                    st.download_button(
                        "⬇ 下載", fav["content"],
                        file_name=f"{fav['title'][:30]}.txt", mime="text/plain",
                        key=f"dl_fav_{i}", use_container_width=True,
                    )
                with fc2:
                    if st.button("🗑 刪除", key=f"del_fav_{i}", use_container_width=True):
                        remove_favorite(i)
                        st.rerun()
        if st.button("🗑 清空所有收藏", use_container_width=True):
            from storage import clear_favorites
            clear_favorites()
            st.rerun()


# ── PRO TAB 5：歷史
with pro_tab5:
    history = get_history()
    if not history:
        st.info("💡 還沒有分析過任何影片")
    else:
        st.caption(f"最近分析了 {len(history)} 部影片（最多保留 50 筆）")
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
                        "🔄 重新分析",
                        key=f"re_{item['url'][:30]}",
                        use_container_width=True,
                    ):
                        st.session_state["current_url"] = item["url"]
                        st.rerun()
        if st.button("🗑 清空歷史", use_container_width=True):
            clear_history()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 頁面底部：用戶體驗問卷
# ══════════════════════════════════════════════════════════════════════════════

st.divider()
with st.expander("💬 分享你的使用體驗（只需 1 分鐘）", expanded=False):
    render_survey()
