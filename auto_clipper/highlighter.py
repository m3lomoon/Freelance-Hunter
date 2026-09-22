"""
精華片段挑選：從逐句稿裡找出最適合剪成短片的片段。

演算法很單純（不需要額外的 ML 模型，跑起來快）：
1. 把連續的句子貼成長度落在 [CLIP_MIN_SEC, CLIP_MAX_SEC] 的候選片段。
2. 依「鉤子詞彙命中數」「贅字扣分」「語速是否自然」幫每個候選片段打分。
3. 取分數最高、彼此不重疊的前 N 段，再依照時間排序輸出。
"""

from dataclasses import dataclass
from typing import List

from . import settings
from .transcriber import Segment


@dataclass
class Highlight:
    start: float
    end: float
    text: str
    score: float
    segments: List[Segment]

    @property
    def duration(self) -> float:
        return self.end - self.start


def _score_text(text: str, duration: float, word_count: int) -> float:
    score = 0.0
    lower = text.lower()

    for kw in settings.HOOK_KEYWORDS:
        if kw.lower() in lower:
            score += 3.0

    for kw in settings.FILLER_KEYWORDS:
        if kw.lower() in lower:
            score -= 1.0

    score += text.count("？") + text.count("?")  # 提問通常是好片段
    score += 0.5 * (text.count("！") + text.count("!"))

    # 語速太快或太慢的片段通常不好聽，落在自然範圍內加分
    if duration > 0:
        pace = word_count / duration
        if 1.5 <= pace <= 4.5:
            score += 1.0

    return score


def _build_candidates(segments: List[Segment]) -> List[Highlight]:
    candidates = []
    n = len(segments)

    for i in range(n):
        window_segments = []
        word_count = 0
        for j in range(i, n):
            seg = segments[j]
            duration = seg.end - segments[i].start
            if duration > settings.CLIP_MAX_SEC:
                break

            window_segments.append(seg)
            word_count += len(seg.text)

            if duration >= settings.CLIP_MIN_SEC:
                text = " ".join(s.text for s in window_segments)
                candidates.append(
                    Highlight(
                        start=segments[i].start,
                        end=seg.end,
                        text=text,
                        score=_score_text(text, duration, word_count),
                        segments=list(window_segments),
                    )
                )

    return candidates


def _remove_overlaps(candidates: List[Highlight], num_clips: int) -> List[Highlight]:
    ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
    picked: List[Highlight] = []

    for cand in ranked:
        overlaps = any(
            cand.start < p.end and p.start < cand.end for p in picked
        )
        if not overlaps:
            picked.append(cand)
        if len(picked) >= num_clips:
            break

    return sorted(picked, key=lambda c: c.start)


def find_highlights(
    segments: List[Segment], num_clips: int = settings.DEFAULT_NUM_CLIPS
) -> List[Highlight]:
    """從逐句稿中挑出前 num_clips 個最適合的精華片段（依時間排序）。"""
    if not segments:
        return []

    candidates = _build_candidates(segments)
    if not candidates:
        return []

    return _remove_overlaps(candidates, num_clips)
