import os
import re
import time
import streamlit as st

_MAX_ATTEMPTS = 5
_COOLDOWN_SECONDS = 300  # 5分鐘冷卻

# 內建 codes 留空 — 所有 code 必須透過 ACCESS_CODES env var 設定
_BUILTIN_CODES: set[str] = set()

# Gumroad 授權碼格式：XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX
_GUMROAD_KEY_RE = re.compile(
    r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{8}$'
)


def _load_valid_codes() -> set[str]:
    raw = os.environ.get("ACCESS_CODES", "")
    env_codes = {c.strip().upper() for c in raw.split(",") if c.strip()}
    return env_codes | _BUILTIN_CODES


_VERIFY_CACHE_TTL = 3600  # 每小時重驗一次訂閱狀態


def _verify_gumroad(license_key: str) -> dict:
    """
    透過 Gumroad API 驗證月費訂閱狀態。
    回傳 dict:
      valid  : True = 有效, False = 無效/過期, None = 網路錯誤（維持現狀）
      status : "active" | "cancelled" | "payment_failed" | "ended" |
               "not_found" | "network_error" | "invalid_format"
    """
    permalink = os.environ.get("GUMROAD_PRODUCT_PERMALINK", "")
    if not permalink or not _GUMROAD_KEY_RE.match(license_key):
        return {"valid": False, "status": "invalid_format"}
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
            if not data.get("success"):
                return {"valid": False, "status": "not_found"}

            purchase = data.get("purchase", {})
            ended_at     = purchase.get("subscription_ended_at")
            failed_at    = purchase.get("subscription_failed_at")
            cancelled_at = purchase.get("subscription_cancelled_at")

            # 訂閱已結束（取消且超過寬限期）
            if ended_at:
                return {"valid": False, "status": "ended"}

            # 付款失敗
            if failed_at:
                return {"valid": False, "status": "payment_failed", "failed_at": failed_at}

            # 已取消但仍在有效期內 / 正常訂閱中
            status = "cancelled" if cancelled_at else "active"
            return {
                "valid": True,
                "status": status,
                "cancelled_at": cancelled_at,
                "recurrence": purchase.get("recurrence", "monthly"),
                "charge_count": purchase.get("charge_occurrence_count", 0),
            }
    except Exception:
        # 網路錯誤：不強制登出，維持現有狀態
        return {"valid": None, "status": "network_error"}

    return {"valid": False, "status": "api_error"}


def is_unlocked() -> bool:
    # 環境變數開全功能（課程版 / 內部展示用）
    if os.environ.get("UNLOCK_ALL", "").lower() in ("1", "true", "yes"):
        return True

    if not st.session_state.get("pro_unlocked"):
        return False

    # ── 月費訂閱：每小時重驗 Gumroad key ──────────────────────────────────
    license_key = st.session_state.get("_license_key", "")
    if license_key and _GUMROAD_KEY_RE.match(license_key):
        last_ts = st.session_state.get("_verify_ts", 0)
        if time.time() - last_ts > _VERIFY_CACHE_TTL:
            result = _verify_gumroad(license_key)
            if result["valid"] is False:  # 明確失效（非網路錯誤）
                st.session_state["pro_unlocked"] = False
                st.session_state["_sub_status"] = result["status"]
                return False
            if result["valid"] is True:
                st.session_state["_sub_status"] = result.get("status", "active")
            # valid is None（網路錯誤）→ 維持解鎖，不更新 ts（下次還會重試）
            if result["valid"] is not None:
                st.session_state["_verify_ts"] = time.time()

    return True


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

    # 先嘗試 Gumroad 授權碼（UUID 格式）——月費訂閱驗證
    if _GUMROAD_KEY_RE.match(code):
        result = _verify_gumroad(code)
        if result["valid"] is True:
            st.session_state["pro_unlocked"] = True
            st.session_state["_license_key"] = code   # 儲存供每小時重驗
            st.session_state["_unlock_id"] = code      # 點數帳號身分
            st.session_state["_verify_ts"] = time.time()
            st.session_state["_sub_status"] = result.get("status", "active")
            st.session_state["unlock_attempts"] = 0
            return True
        if result["valid"] is None:
            # 網路錯誤，提示稍後再試，不計入失敗次數
            raise ValueError("無法連線驗證，請稍後再試")
        # 驗證失敗計入次數
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
        st.session_state["_unlock_id"] = code.upper()   # 點數帳號身分
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
        "🔒 💬 留言挖掘 → 內容點子",
        "🔒 📢 AI 廣告投放顧問",
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
