"""
用 ffmpeg 把精華片段切出來、重新裁成直式 9:16（給 Shorts/Reels/TikTok），
並把雙語字幕燒錄進畫面。
"""

import shutil
import subprocess
from pathlib import Path

from . import settings


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "找不到 ffmpeg，請先安裝：\n"
            "  macOS:  brew install ffmpeg\n"
            "  Ubuntu: sudo apt install ffmpeg"
        )


def _escape_for_filter(path: str) -> str:
    # ffmpeg filtergraph 裡的路徑要跳脫 \ : ' 這幾個字元
    escaped = path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    return escaped


def cut_clip_with_subtitles(
    source_video: str,
    start: float,
    duration: float,
    ass_path: str,
    output_path: str,
    vertical: bool = settings.VERTICAL_OUTPUT,
) -> None:
    """
    從 source_video 切出一段 [start, start+duration) 的片段，
    燒錄 ass_path 的雙語字幕，輸出到 output_path。
    """
    check_ffmpeg()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    escaped_ass = _escape_for_filter(str(Path(ass_path).resolve()))

    if vertical:
        vf = (
            f"scale={settings.OUTPUT_WIDTH}:{settings.OUTPUT_HEIGHT}:"
            "force_original_aspect_ratio=increase,"
            f"crop={settings.OUTPUT_WIDTH}:{settings.OUTPUT_HEIGHT},"
            f"subtitles='{escaped_ass}'"
        )
    else:
        vf = f"subtitles='{escaped_ass}'"

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", source_video,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 剪輯失敗 ({output_path}):\n{result.stderr[-2000:]}"
        )
