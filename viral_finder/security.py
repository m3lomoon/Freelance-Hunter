"""
安全工具：防止 Prompt Injection、輸入清理
"""
import re

# 常見 Prompt Injection 關鍵字
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior)\s+",
    r"forget\s+(everything|all)",
    r"you\s+are\s+now\s+(a|an|the)",
    r"act\s+as\s+(a|an|the)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"new\s+system\s+prompt",
    r"###\s*(instruction|system|prompt)",
    r"\[INST\]|\[SYS\]|<\|system\|>",
    r"jailbreak",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def sanitize_prompt_input(text: str, max_len: int = 500) -> str:
    """
    清理使用者輸入，移除 Prompt Injection 嘗試，限制長度。
    回傳清理後的文字。
    """
    if not text:
        return ""

    # 長度限制
    text = text[:max_len].strip()

    # 偵測並移除 injection 嘗試
    for pattern in _COMPILED:
        if pattern.search(text):
            # 移除符合的部分，不是整段拒絕（避免誤判）
            text = pattern.sub("[...]", text)

    return text


def sanitize_url_for_display(url: str) -> str:
    """移除 URL 中的 token、session 等敏感參數後顯示"""
    # 移除常見的 tracking/auth 參數
    url = re.sub(r'[?&](token|session|key|auth|access_token|mcp_token|fbclid)[^&]*', '', url)
    return url


def is_safe_filename(name: str) -> str:
    """把字串轉成安全的檔名"""
    safe = re.sub(r'[^\w\s\-.]', '', name)
    safe = re.sub(r'\s+', '_', safe)
    return safe[:60] or "file"
