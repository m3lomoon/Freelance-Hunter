import os
import hashlib
import streamlit as st


def _load_valid_codes() -> set[str]:
    raw = os.environ.get("ACCESS_CODES", "")
    codes = {c.strip().upper() for c in raw.split(",") if c.strip()}
    return codes


def _hash(code: str) -> str:
    return hashlib.sha256(code.upper().encode()).hexdigest()


def is_unlocked() -> bool:
    return st.session_state.get("pro_unlocked", False)


def try_unlock(code: str) -> bool:
    valid = _load_valid_codes()
    if code.strip().upper() in valid:
        st.session_state["pro_unlocked"] = True
        return True
    return False


def lock():
    st.session_state["pro_unlocked"] = False


def render_unlock_prompt(feature_name: str = "進階功能"):
    """顯示付費牆提示，回傳 True 表示已解鎖"""
    if is_unlocked():
        return True

    st.divider()
    st.markdown(f"### 🔒 {feature_name} — 進階功能")
    st.info("此功能為付費解鎖。購買後你會收到一組 Access Code，輸入即可永久解鎖本次使用。")

    col1, col2 = st.columns([3, 1])
    with col1:
        code_input = st.text_input(
            "輸入 Access Code",
            placeholder="例如：VH-XXXX-XXXX",
            label_visibility="collapsed",
            key=f"code_input_{feature_name}",
        )
    with col2:
        if st.button("解鎖", type="primary", use_container_width=True, key=f"unlock_{feature_name}"):
            if try_unlock(code_input):
                st.success("✅ 解鎖成功！")
                st.rerun()
            else:
                st.error("Access Code 不正確")

    st.markdown("**購買方式：** 請聯絡我們取得 Access Code")
    return False


PLAN_FEATURES = {
    "free": [
        "✅ 搜尋爆款影片",
        "✅ 影片基本數據分析",
        "✅ 逐字稿取得",
        "✅ Google 翻譯（免費）",
    ],
    "pro": [
        "🔒 AI 爆款原因分析",
        "🔒 鉤子模板生成",
        "🔒 拍攝腳本模板",
        "🔒 影片重現指南",
        "🔒 AI 影片生成 Prompt",
        "🔒 A/B 標題測試",
        "🔒 縮圖文案生成",
        "🔒 30天內容日曆",
        "🔒 平台適配器",
        "🔒 最佳發布時間分析",
        "🔒 Claude 高品質翻譯",
    ],
}
