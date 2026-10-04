import streamlit as st
from datetime import datetime


# ── 初始化 session state ────────────────────────────────────────────────────

def _init():
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    if "history" not in st.session_state:
        st.session_state.history = []


# ── 歷史紀錄 ───────────────────────────────────────────────────────────────

def add_history(url: str, title: str, platform: str, view_count: int, thumbnail: str = ""):
    _init()
    existing = [h["url"] for h in st.session_state.history]
    if url in existing:
        return
    st.session_state.history.insert(0, {
        "url": url,
        "title": title,
        "platform": platform,
        "view_count": view_count,
        "thumbnail": thumbnail,
        "analyzed_at": datetime.now().strftime("%m/%d %H:%M"),
    })
    if len(st.session_state.history) > 50:
        st.session_state.history = st.session_state.history[:50]


def get_history() -> list[dict]:
    _init()
    return st.session_state.history


def clear_history():
    st.session_state.history = []


# ── 收藏夾 ─────────────────────────────────────────────────────────────────

def add_favorite(item_type: str, title: str, content: str, tags: list[str] | None = None):
    _init()
    st.session_state.favorites.insert(0, {
        "type": item_type,
        "title": title,
        "content": content,
        "tags": tags or [],
        "saved_at": datetime.now().strftime("%m/%d %H:%M"),
    })


def get_favorites(item_type: str | None = None) -> list[dict]:
    _init()
    if item_type:
        return [f for f in st.session_state.favorites if f["type"] == item_type]
    return st.session_state.favorites


def remove_favorite(index: int):
    _init()
    if 0 <= index < len(st.session_state.favorites):
        st.session_state.favorites.pop(index)


def clear_favorites():
    st.session_state.favorites = []


FAVORITE_TYPES = {
    "hook": "🪝 鉤子",
    "template": "🎬 模板",
    "title": "📐 標題",
    "calendar": "📅 日曆",
    "recreation": "🎥 重現指南",
    "other": "📌 其他",
}
