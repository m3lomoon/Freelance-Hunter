"""
中文簡繁轉換：不管是 whisper 聽打出來的中文、還是 Claude 翻譯出來的中文，
一律轉成繁體中文＋台灣用語（s2twp：簡體 → 繁體，含台灣慣用詞轉換）。
"""

from . import settings

_converter = None


def _get_converter():
    global _converter
    if _converter is None:
        try:
            from opencc import OpenCC
        except ImportError as e:
            raise RuntimeError(
                "缺少 opencc-python-reimplemented，"
                "請先執行: pip install opencc-python-reimplemented"
            ) from e
        _converter = OpenCC("s2twp")
    return _converter


def to_traditional(text: str) -> str:
    """把中文字串轉成繁體中文（台灣用語）。非中文字串原樣返回。"""
    if not text or not settings.FORCE_TRADITIONAL_CHINESE:
        return text
    return _get_converter().convert(text)
