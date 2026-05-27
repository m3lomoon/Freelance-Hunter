"""
使用分析追蹤模組 — 基於 session_state，無需資料庫
紀錄功能使用頻率、平台分佈、搜尋關鍵字等，供管理員參考
"""
from datetime import datetime
import streamlit as st


# ── 事件類型標籤（中文）
EVENT_LABELS = {
    "analyze_video": "分析影片",
    "get_transcript": "取得字幕逐字稿",
    "whisper_transcribe": "Whisper 語音辨識",
    "translate": "翻譯功能",
    "generate_template": "爆款分析+模板",
    "custom_hook": "自訂鉤子生成",
    "recreation_guide": "重現指南",
    "ab_titles": "A/B 標題測試",
    "thumbnail_copy": "縮圖文案",
    "content_calendar": "30天內容日曆",
    "platform_adapt": "平台適配",
    "posting_time": "最佳發布時段",
    "find_niches": "利基市場發現",
    "generate_script": "AI 腳本生成",
    "seo_package": "SEO 優化包",
    "thumbnail_prompt": "縮圖 Prompt",
    "storyboard": "AI 分鏡腳本",
    "search_video": "搜尋影片",
    "unlock_pro": "解鎖 PRO",
    "add_favorite": "加入收藏",
}

_MAX_EVENTS = 500  # 最多保留 500 筆事件


def track(event_type: str, details: dict | None = None):
    """記錄一個使用事件"""
    # 初始化
    if "usage_events" not in st.session_state:
        st.session_state["usage_events"] = []
    if "usage_counters" not in st.session_state:
        st.session_state["usage_counters"] = {}
    if "platform_counts" not in st.session_state:
        st.session_state["platform_counts"] = {}
    if "keyword_counts" not in st.session_state:
        st.session_state["keyword_counts"] = {}
    if "hourly_counts" not in st.session_state:
        st.session_state["hourly_counts"] = {}

    now = datetime.now()
    event = {
        "type": event_type,
        "details": details or {},
        "time": now.strftime("%Y-%m-%d %H:%M"),
    }

    # 追加事件（環形緩衝）
    events = st.session_state["usage_events"]
    if len(events) >= _MAX_EVENTS:
        events.pop(0)
    events.append(event)

    # 功能計數
    counters = st.session_state["usage_counters"]
    counters[event_type] = counters.get(event_type, 0) + 1

    # 平台計數
    if details:
        if "platform" in details:
            p = details["platform"]
            pc = st.session_state["platform_counts"]
            pc[p] = pc.get(p, 0) + 1

        # 關鍵字計數（搜尋功能）
        if "keyword" in details:
            kw = details["keyword"][:30]
            kc = st.session_state["keyword_counts"]
            kc[kw] = kc.get(kw, 0) + 1

    # 時段計數（哪個小時最多人用）
    hour_key = now.strftime("%H:00")
    hc = st.session_state["hourly_counts"]
    hc[hour_key] = hc.get(hour_key, 0) + 1


def get_events() -> list:
    return st.session_state.get("usage_events", [])


def get_counters() -> dict:
    return st.session_state.get("usage_counters", {})


def get_platform_counts() -> dict:
    return st.session_state.get("platform_counts", {})


def get_keyword_counts() -> dict:
    return st.session_state.get("keyword_counts", {})


def get_summary() -> dict:
    counters = get_counters()
    platform_counts = get_platform_counts()
    keyword_counts = get_keyword_counts()
    hourly = st.session_state.get("hourly_counts", {})
    total = sum(counters.values())

    top_features = sorted(counters.items(), key=lambda x: x[1], reverse=True)[:12]
    top_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_actions": total,
        "feature_usage": top_features,
        "platform_usage": top_platforms,
        "keyword_usage": top_keywords,
        "hourly_usage": top_hours,
    }


def render_analytics_dashboard():
    """管理員用的使用分析儀表板"""
    summary = get_summary()
    total = summary["total_actions"]

    if total == 0:
        st.info("本次 Session 還沒有使用紀錄")
        return

    # ── 總覽
    st.markdown(f"**🔢 本次 Session 總操作：{total} 次**")

    col1, col2 = st.columns(2)
    with col1:
        platforms = len(summary["platform_usage"])
        st.metric("分析平台數", platforms)
    with col2:
        features = len(summary["feature_usage"])
        st.metric("使用功能數", features)

    # ── 功能使用排行
    if summary["feature_usage"]:
        st.markdown("---")
        st.markdown("**📊 功能使用排行（本次 Session）**")
        max_count = summary["feature_usage"][0][1] if summary["feature_usage"] else 1
        for event_type, count in summary["feature_usage"]:
            label = EVENT_LABELS.get(event_type, event_type)
            pct = count / max_count
            bar_len = max(1, int(pct * 15))
            bar = "█" * bar_len + "░" * (15 - bar_len)
            st.markdown(f"`{label}` `{bar}` **{count}次**")

    # ── 平台分佈
    if summary["platform_usage"]:
        st.markdown("---")
        st.markdown("**🌐 分析平台分佈**")
        total_p = sum(v for _, v in summary["platform_usage"])
        for plat, count in summary["platform_usage"]:
            pct = count / total_p * 100 if total_p else 0
            st.markdown(f"- **{plat}**：{count} 次（{pct:.0f}%）")

    # ── 熱門搜尋關鍵字
    if summary["keyword_usage"]:
        st.markdown("---")
        st.markdown("**🔍 熱門搜尋關鍵字**")
        for kw, count in summary["keyword_usage"]:
            st.markdown(f"- `{kw}`：{count} 次")

    # ── 使用時段
    if summary["hourly_usage"]:
        st.markdown("---")
        st.markdown("**⏰ 使用高峰時段（Top 5）**")
        for hour, count in summary["hourly_usage"]:
            st.markdown(f"- {hour} — {count} 次操作")

    # ── 最近事件
    events = get_events()
    if events:
        st.markdown("---")
        st.markdown("**⏱ 最近 15 筆操作**")
        for e in reversed(events[-15:]):
            label = EVENT_LABELS.get(e["type"], e["type"])
            detail = ""
            if e["details"].get("platform"):
                detail += f" [{e['details']['platform']}]"
            if e["details"].get("topic"):
                detail += f" — {e['details']['topic'][:25]}"
            if e["details"].get("keyword"):
                detail += f" 「{e['details']['keyword'][:20]}」"
            st.caption(f"🕐 {e['time']} · {label}{detail}")
