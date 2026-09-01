"""
雙語字幕翻譯：用 Anthropic API 把逐句稿翻成目標語言，
一次把整段的所有句子送進去翻，維持上下文與用詞一致。
"""

import re
from typing import List

from . import settings
from .transcriber import Segment

LANG_NAMES = {
    "zh": "繁體中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
}


def _build_prompt(lines: List[str], target_lang: str) -> str:
    target_name = LANG_NAMES.get(target_lang, target_lang)
    numbered = "\n".join(f"{i + 1}. {line}" for i, line in enumerate(lines))
    return (
        f"你是專業的影片字幕翻譯。請把以下每一行口語逐字稿翻譯成{target_name}，"
        "維持口語、簡短、適合放在短影音字幕上（不要超譯、不要加解釋）。\n"
        "務必逐行對應輸出，保留原本的編號，不要合併或拆開行數。\n\n"
        f"{numbered}"
    )


def _parse_numbered_response(response_text: str, expected: int) -> List[str]:
    lines = {}
    for raw_line in response_text.strip().splitlines():
        match = re.match(r"\s*(\d+)[.、)]\s*(.*)", raw_line)
        if match:
            idx = int(match.group(1))
            lines[idx] = match.group(2).strip()

    return [lines.get(i + 1, "") for i in range(expected)]


def translate_segments(
    segments: List[Segment], target_lang: str
) -> List[str]:
    """
    翻譯逐句稿，回傳與 segments 等長、順序相同的翻譯文字列表。
    """
    if not segments:
        return []

    try:
        import config as project_config
        api_key = project_config.ANTHROPIC_API_KEY
    except ImportError as e:
        raise RuntimeError(
            "找不到專案根目錄的 config.py，請在 repo 根目錄下執行本工具"
        ) from e

    if not api_key:
        raise RuntimeError("config.py 中的 ANTHROPIC_API_KEY 未設定")

    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError("缺少 anthropic 套件，請先執行: pip install anthropic") from e

    client = anthropic.Anthropic(api_key=api_key)
    lines = [seg.text for seg in segments]

    # 一批最多翻 40 句，避免單次請求過長
    batch_size = 40
    translated: List[str] = []

    for start in range(0, len(lines), batch_size):
        batch = lines[start:start + batch_size]
        prompt = _build_prompt(batch, target_lang)

        response = client.messages.create(
            model=settings.TRANSLATE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        translated.extend(_parse_numbered_response(response_text, len(batch)))

    return translated
