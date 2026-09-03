"""
產生雙語字幕（.ass 給燒錄用、.srt 給後製軟體匯入用）。
每句字幕上排是原文，下排是翻譯。
"""

from dataclasses import dataclass
from typing import List

from . import settings


@dataclass
class SubLine:
    start: float  # 相對於片段開頭的秒數
    end: float
    original: str
    translated: str


def _ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _srt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _escape_ass(text: str) -> str:
    return text.replace("\n", "\\N").replace("{", "(").replace("}", ")")


ASS_HEADER_TEMPLATE = """[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Original,{font},{size_primary},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,{margin_lr},{margin_lr},{margin_v_primary},1
Style: Translated,{font},{size_secondary},&H0000D7FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1,2,{margin_lr},{margin_lr},{margin_v_secondary},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_ass(lines: List[SubLine]) -> str:
    """組出雙語 .ass 字幕內容（原文在上、翻譯在下）。"""
    header = ASS_HEADER_TEMPLATE.format(
        width=settings.OUTPUT_WIDTH if settings.VERTICAL_OUTPUT else 1920,
        height=settings.OUTPUT_HEIGHT if settings.VERTICAL_OUTPUT else 1080,
        font=settings.SUB_FONT,
        size_primary=settings.SUB_FONT_SIZE_PRIMARY,
        size_secondary=settings.SUB_FONT_SIZE_SECONDARY,
        margin_lr=settings.SUB_MARGIN_LR,
        margin_v_primary=settings.SUB_MARGIN_V_PRIMARY,
        margin_v_secondary=settings.SUB_MARGIN_V_SECONDARY,
    )

    events = []
    for line in lines:
        start = _ass_time(line.start)
        end = _ass_time(line.end)
        if line.original:
            events.append(
                f"Dialogue: 0,{start},{end},Original,,0,0,0,,{_escape_ass(line.original)}"
            )
        if line.translated:
            events.append(
                f"Dialogue: 0,{start},{end},Translated,,0,0,0,,{_escape_ass(line.translated)}"
            )

    return header + "\n".join(events) + "\n"


def build_srt(lines: List[SubLine]) -> str:
    """組出雙語 .srt 字幕內容（同一句字幕內原文+翻譯各一行）。"""
    blocks = []
    for i, line in enumerate(lines, start=1):
        text = "\n".join(t for t in (line.original, line.translated) if t)
        blocks.append(
            f"{i}\n{_srt_time(line.start)} --> {_srt_time(line.end)}\n{text}\n"
        )
    return "\n".join(blocks)


def write_subtitles(lines: List[SubLine], out_prefix: str) -> tuple[str, str]:
    """寫出 {out_prefix}.ass 與 {out_prefix}.srt，回傳兩個檔案路徑。"""
    ass_path = f"{out_prefix}.ass"
    srt_path = f"{out_prefix}.srt"

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(build_ass(lines))
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(build_srt(lines))

    return ass_path, srt_path
