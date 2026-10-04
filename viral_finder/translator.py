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

# Google Translate 語言代碼對應
_GOOGLE_LANG_CODES = {
    "繁體中文": "zh-TW",
    "简体中文": "zh-CN",
    "English": "en",
    "日本語": "ja",
    "한국어": "ko",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "ภาษาไทย": "th",
    "Tiếng Việt": "vi",
}

MAX_CHARS = 12_000
_GOOGLE_CHUNK = 4_000  # Google 翻譯單次上限


def translate_text(text: str, target_lang: str = "繁體中文") -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        return _translate_claude(text, target_lang, api_key)
    else:
        return _translate_google(text, target_lang)


def _translate_claude(text: str, target_lang: str, api_key: str) -> str:
    lang_name = LANGUAGES.get(target_lang, target_lang)
    client = anthropic.Anthropic(api_key=api_key)

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


def _translate_google(text: str, target_lang: str) -> str:
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise RuntimeError("請安裝 deep-translator：pip install deep-translator")

    lang_code = _GOOGLE_LANG_CODES.get(target_lang, "zh-TW")
    translator = GoogleTranslator(source="auto", target=lang_code)

    # 長文本分段翻譯
    if len(text) <= _GOOGLE_CHUNK:
        result = translator.translate(text)
        return (result or "") + "\n\n🆓 使用 Google 翻譯（免費版）· 輸入 API Key 可切換至 Claude 高品質翻譯"

    chunks = []
    for i in range(0, len(text), _GOOGLE_CHUNK):
        part = text[i:i + _GOOGLE_CHUNK]
        translated = translator.translate(part) or ""
        chunks.append(translated)

    return "\n".join(chunks) + "\n\n🆓 使用 Google 翻譯（免費版）· 輸入 API Key 可切換至 Claude 高品質翻譯"


def using_free_translation() -> bool:
    return not bool(os.environ.get("ANTHROPIC_API_KEY", ""))
