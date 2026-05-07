import os

import anthropic

LANGUAGES = {
    "繁體中文": "Traditional Chinese (繁體中文)",
    "简体中文": "Simplified Chinese (简体中文)",
    "English": "English",
    "日本語": "Japanese (日本語)",
    "한국어": "Korean (한국어)",
    "Español": "Spanish (Español)",
    "Français": "French (Français)",
    "Deutsch": "German (Deutsch)",
    "ภาษาไทย": "Thai (ภาษาไทย)",
    "Tiếng Việt": "Vietnamese (Tiếng Việt)",
}

MAX_CHARS = 12_000  # 單次翻譯字符上限


def translate_text(text: str, target_lang: str = "繁體中文") -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("請在側邊欄輸入 Anthropic API Key")

    lang_name = LANGUAGES.get(target_lang, target_lang)
    client = anthropic.Anthropic(api_key=api_key)

    # 超過上限時截斷並告知
    truncated = len(text) > MAX_CHARS
    chunk = text[:MAX_CHARS]

    prompt = (
        f"Please translate the following text into {lang_name}.\n"
        "Preserve the original meaning, tone, and paragraph structure.\n"
        "Output only the translation — no explanations, no headers.\n\n"
        f"{chunk}"
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    result = message.content[0].text
    if truncated:
        result += "\n\n⚠️ 原文過長，僅翻譯前段內容。"
    return result
