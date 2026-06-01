import os
import re
import time
import streamlit as st

_MAX_ATTEMPTS = 5
_COOLDOWN_SECONDS = 300  # 5分鐘冷卻

# 內建的 Beta 測試碼（不需要 env var 也能使用）
_BUILTIN_CODES: set[str] = {
    "MELOMOONJUSTFORYOU",
}

# Gumroad 授權碼格式：XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX
_GUMROAD_KEY_RE = re.compile(
    r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{8}$'
)


def _load_valid_codes() -> set[str]:
    raw = os.environ.get("ACCESS_CODES", "")
    env_codes = {c.strip().upper() for c in raw.split(",") if c.strip()}
    return env_codes | _BUILTIN_CODES


def _verify_gumroad(license_key: str) -> bool:
    """透過 Gumroad API 驗證授權碼，需要設定 GUMROAD_PRODUCT_PERMALINK env var"""
    permalink = os.environ.get("GUMROAD_PRODUCT_PERMALINK", "")
    if not permalink or not _GUMROAD_KEY_RE.match(license_key):
        return False
    try:
        import requests
        resp = requests.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={
                "product_permalink": permalink,
                "license_key": license_key,
                "increment_uses_count": "false",
            },
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json()
            return bool(data.get("success"))
    except Exception:
        pass
    return False


def is_unlocked() -> bool:
    # 環境變數開全功能（課程版 / 內部展示用）
    if os.environ.get("UNLOCK_ALL", "").lower() in ("1", "true", "yes"):
        return True
    return st.session_state.get("pro_unlocked", False)


def _is_rate_limited() -> tuple[bool, int]:
    attempts = st.session_state.get("unlock_attempts", 0)
    last_fail = st.session_state.get("unlock_last_fail", 0)

    if attempts >= _MAX_ATTEMPTS:
        elapsed = time.time() - last_fail
        if elapsed < _COOLDOWN_SECONDS:
            remaining = int(_COOLDOWN_SECONDS - elapsed)
            return True, remaining
        else:
            # 冷卻結束，重置計數
            st.session_state["unlock_attempts"] = 0

    return False, 0


def try_unlock(code: str) -> bool:
    """驗證 Access Code 或 Gumroad 授權碼，成功回傳 True"""
    limited, remaining = _is_rate_limited()
    if limited:
        raise ValueError(f"嘗試次數過多，請等待 {remaining} 秒後再試")

    code = code.strip()

    # 先嘗試 Gumroad 授權碼（UUID 格式）
    if _GUMROAD_KEY_RE.match(code):
        if _verify_gumroad(code):
            st.session_state["pro_unlocked"] = True
            st.session_state["unlock_attempts"] = 0
            return True
        # Gumroad 驗證失敗仍計入嘗試次數
        st.session_state["unlock_attempts"] = st.session_state.get("unlock_attempts", 0) + 1
        st.session_state["unlock_last_fail"] = time.time()
        return False

    # 一般 Access Code：只允許字母、數字、連字號
    if not re.match(r'^[A-Za-z0-9\-]{4,50}$', code):
        st.session_state["unlock_attempts"] = st.session_state.get("unlock_attempts", 0) + 1
        st.session_state["unlock_last_fail"] = time.time()
        return False

    valid = _load_valid_codes()
    if code.upper() in valid:
        st.session_state["pro_unlocked"] = True
        st.session_state["unlock_attempts"] = 0
        return True

    st.session_state["unlock_attempts"] = st.session_state.get("unlock_attempts", 0) + 1
    st.session_state["unlock_last_fail"] = time.time()
    return False


def lock():
    st.session_state["pro_unlocked"] = False


def render_unlock_prompt(feature_name: str = "進階功能"):
    if is_unlocked():
        return True

    limited, remaining = _is_rate_limited()

    st.divider()
    st.markdown(f"### 🔒 {feature_name} — 進階功能")
    st.info("此功能為付費解鎖。購買後你會收到一組 Access Code，輸入即可解鎖。")

    if limited:
        st.error(f"⛔ 嘗試次數過多，請等待 {remaining} 秒後再試")
        return False

    attempts = st.session_state.get("unlock_attempts", 0)
    if attempts > 0:
        st.warning(f"已嘗試 {attempts}/{_MAX_ATTEMPTS} 次")

    col1, col2 = st.columns([3, 1])
    with col1:
        code_input = st.text_input(
            "輸入 Access Code",
            placeholder="例如：VH-XXXX-XXXX",
            label_visibility="collapsed",
            key=f"code_input_{feature_name}",
            max_chars=32,
        )
    with col2:
        if st.button("解鎖", type="primary", use_container_width=True, key=f"unlock_{feature_name}"):
            try:
                if try_unlock(code_input):
                    st.success("✅ 解鎖成功！")
                    st.rerun()
                else:
                    st.error("Access Code 不正確")
            except ValueError as e:
                st.error(str(e))

    # Gumroad 購買按鈕（若設定了 URL）
    gumroad_url = os.environ.get("GUMROAD_URL", "")
    if gumroad_url:
        st.link_button("🛒 購買 PRO 進階版", gumroad_url, use_container_width=True)
        st.caption("購買後你會收到授權碼，輸入上方欄位即可解鎖")
    else:
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
        "🔒 無臉頻道工作坊",
    ],
}
