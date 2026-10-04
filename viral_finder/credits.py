"""
點數扣除系統 (Credit Metering)
防止付費用戶無限呼叫 AI 功能燒光 API 費用。

規則：
- 課程版 UNLOCK_ALL / 試玩版 DEMO_MODE → 不計費（無限用）
- 靠授權碼 / Access Code 解鎖的付費用戶 → 每次 AI 功能扣對應點數
- 點數綁「解鎖身分」（授權碼雜湊），存檔在伺服器端 JSON，
  重新整理不會刷回；每月 1 號自動重置為方案額度。

⚠️ MVP 版用 JSON 檔存點數，適合單機 / 小規模。
   規模化後建議換成資料庫（Supabase 等），介面不變。
"""
import os
import json
import hashlib
import threading
from datetime import datetime, timezone

import streamlit as st

# ── 每個功能消耗的點數 ────────────────────────────────────────────────────────
CREDIT_COSTS = {
    "template":         30,   # 爆款分析 + 模板
    "recreation":       35,   # 重現指南
    "comment_mining":   25,   # 留言挖掘
    "ad_strategy":      40,   # 廣告投放策略
    "custom_hook":      10,   # 自訂鉤子
    "ab_titles":         8,
    "thumbnail_copy":    8,
    "content_calendar": 20,
    "platform_adapt":   15,
    "posting_time":      8,
    "niche_finder":     15,   # 無臉頻道
    "script_gen":       30,
    "seo_package":      15,
    "thumbnail_prompt": 10,
    "storyboard":       30,
    "translate_claude":  5,   # Claude 翻譯（Google 免費不計）
}

# ── 各方案每月點數額度 ────────────────────────────────────────────────────────
PLAN_CREDITS = {
    "starter":     500,
    "creator":    3000,
    "enterprise": 15000,
}

# 付費用戶預設方案（授權碼目前無法區分方案，先給創作者額度；可用環境變數覆蓋）
_DEFAULT_PLAN = os.environ.get("DEFAULT_PLAN", "creator")

_DB_PATH = os.environ.get("CREDITS_DB_PATH", os.path.join(
    os.path.dirname(__file__), ".credits_ledger.json"))

_LOCK = threading.Lock()


# ── 內部：讀寫帳本 ────────────────────────────────────────────────────────────

def _load() -> dict:
    try:
        with open(_DB_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict):
    tmp = _DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, _DB_PATH)  # 原子寫入，避免併發寫壞檔


def _current_period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _uid() -> str:
    """以解鎖身分（授權碼 / Access Code）雜湊為帳號 ID"""
    raw = st.session_state.get("_unlock_id", "") or "anon"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _plan_allowance(plan: str) -> int:
    return PLAN_CREDITS.get(plan, PLAN_CREDITS["creator"])


# ── 對外 API ─────────────────────────────────────────────────────────────────

def is_metered() -> bool:
    """是否要計費：付費解鎖 + 非課程版 + 非試玩版"""
    if os.environ.get("UNLOCK_ALL", "").lower() in ("1", "true", "yes"):
        return False
    if os.environ.get("DEMO_MODE", "").lower() in ("1", "true", "yes"):
        return False
    return bool(st.session_state.get("pro_unlocked"))


def _ensure_account(ledger: dict, uid: str) -> dict:
    """確保帳號存在且點數為當月額度（跨月自動重置）"""
    acc = ledger.get(uid)
    period = _current_period()
    plan = st.session_state.get("_plan", _DEFAULT_PLAN)
    allowance = _plan_allowance(plan)

    if acc is None:
        acc = {"balance": allowance, "period": period, "plan": plan,
               "spent_total": 0, "created": period}
        ledger[uid] = acc
    elif acc.get("period") != period:
        # 跨月 → 重置為方案額度（訂閱制每月更新）
        acc["balance"] = allowance
        acc["period"] = period
    return acc


def balance() -> int:
    """目前點數餘額（未計費模式回傳 -1 代表無限）"""
    if not is_metered():
        return -1
    with _LOCK:
        ledger = _load()
        acc = _ensure_account(ledger, _uid())
        _save(ledger)
        return acc["balance"]


def can_afford(feature: str) -> tuple[bool, int, int]:
    """
    回傳 (是否付得起, 該功能花費, 目前餘額)。
    未計費模式一律 (True, 0, -1)。
    """
    cost = CREDIT_COSTS.get(feature, 10)
    if not is_metered():
        return True, cost, -1
    with _LOCK:
        ledger = _load()
        acc = _ensure_account(ledger, _uid())
        _save(ledger)
        return acc["balance"] >= cost, cost, acc["balance"]


def charge(feature: str) -> int:
    """
    扣除該功能點數（AI 成功產出後呼叫）。回傳剩餘點數。
    未計費模式不扣，回傳 -1。餘額不足會 raise InsufficientCredits。
    """
    if not is_metered():
        return -1
    cost = CREDIT_COSTS.get(feature, 10)
    with _LOCK:
        ledger = _load()
        acc = _ensure_account(ledger, _uid())
        if acc["balance"] < cost:
            _save(ledger)
            raise InsufficientCredits(cost, acc["balance"])
        acc["balance"] -= cost
        acc["spent_total"] = acc.get("spent_total", 0) + cost
        _save(ledger)
        return acc["balance"]


def add_credits(amount: int) -> int:
    """加值點數（購買加購包時呼叫）。回傳新餘額。"""
    if not is_metered():
        return -1
    with _LOCK:
        ledger = _load()
        acc = _ensure_account(ledger, _uid())
        acc["balance"] += int(amount)
        _save(ledger)
        return acc["balance"]


def usage_stats() -> dict:
    """後台用：所有帳號的用量統計"""
    with _LOCK:
        ledger = _load()
    total_users = len(ledger)
    total_spent = sum(a.get("spent_total", 0) for a in ledger.values())
    total_balance = sum(a.get("balance", 0) for a in ledger.values())
    return {
        "total_users": total_users,
        "total_spent": total_spent,
        "total_balance": total_balance,
        "accounts": ledger,
    }


class InsufficientCredits(Exception):
    def __init__(self, cost: int, balance: int):
        self.cost = cost
        self.balance = balance
        super().__init__(f"點數不足：需要 {cost} 點，目前剩 {balance} 點")
