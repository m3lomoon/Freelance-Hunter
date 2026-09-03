"""
語音辨識：把 podcast 影片轉成帶時間戳的逐句稿。
使用 faster-whisper（CPU 也能跑，準確度接近 OpenAI Whisper large）。
"""

from dataclasses import dataclass
from typing import List, Optional

from . import settings
from .zhconvert import to_traditional


@dataclass
class Segment:
    start: float  # 秒
    end: float
    text: str


def transcribe(
    video_path: str,
    language: Optional[str] = None,
    model_size: str = settings.WHISPER_MODEL_SIZE,
) -> tuple[str, List[Segment]]:
    """
    轉錄影片語音。

    Args:
        video_path: 影片或音檔路徑。
        language: 指定語言代碼（如 "zh"、"en"），留空則自動偵測。
        model_size: whisper 模型大小。

    Returns:
        (偵測到的語言代碼, 逐句 Segment 列表)
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError(
            "缺少 faster-whisper，請先執行: pip install faster-whisper"
        ) from e

    model = WhisperModel(
        model_size,
        device=settings.WHISPER_DEVICE,
        compute_type=settings.WHISPER_COMPUTE_TYPE,
    )

    segments_iter, info = model.transcribe(
        video_path,
        language=language,
        vad_filter=True,  # 用 VAD 自動跳過靜音，斷句更乾淨
        vad_parameters={"min_silence_duration_ms": 400},
    )

    is_chinese = (language or info.language).startswith("zh")
    segments = []
    for s in segments_iter:
        text = s.text.strip()
        if not text:
            continue
        if is_chinese:
            text = to_traditional(text)
        segments.append(Segment(start=s.start, end=s.end, text=text))

    return info.language, segments
