#!/usr/bin/env python3
"""
Auto Clipper CLI - 把一支長 podcast 影片自動剪成多支雙語字幕短片

用法：
    python -m auto_clipper.cli --input podcast.mp4 --num-clips 5
"""

import argparse
import os
import sys
from pathlib import Path

# 確保能 import 到 repo 根目錄的 config.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auto_clipper import settings
from auto_clipper.clipper import cut_clip_with_subtitles
from auto_clipper.highlighter import find_highlights
from auto_clipper.subtitles import SubLine, write_subtitles
from auto_clipper.transcriber import transcribe
from auto_clipper.translator import translate_segments

DEFAULT_TARGET_LANG = {"zh": "en", "en": "zh"}


def parse_args():
    parser = argparse.ArgumentParser(description="自動剪片 + 雙語字幕工具")
    parser.add_argument("--input", required=True, help="來源 podcast 影片路徑")
    parser.add_argument("--outdir", default="clips_output", help="輸出資料夾")
    parser.add_argument("--num-clips", type=int, default=settings.DEFAULT_NUM_CLIPS)
    parser.add_argument("--source-lang", default=None, help="來源語言代碼，留空自動偵測")
    parser.add_argument("--target-lang", default=None, help="翻譯目標語言代碼，留空依來源語言自動判斷")
    parser.add_argument("--whisper-model", default=settings.WHISPER_MODEL_SIZE)
    parser.add_argument(
        "--no-vertical", action="store_true", help="輸出原始比例，不裁成 9:16 直式"
    )
    return parser.parse_args()


def run(args) -> list[str]:
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"找不到輸入影片: {args.input}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"🎙️  轉錄語音中（模型: {args.whisper_model}）...")
    language, segments = transcribe(
        args.input, language=args.source_lang, model_size=args.whisper_model
    )
    print(f"   偵測語言: {language}，共 {len(segments)} 句")

    if not segments:
        print("⚠️  沒有偵測到任何語音內容，結束。")
        return []

    target_lang = args.target_lang or DEFAULT_TARGET_LANG.get(language, "en")
    print(f"🌐 雙語字幕：{language} → {target_lang}")

    print(f"✂️  挑選 {args.num_clips} 個精華片段中...")
    highlights = find_highlights(segments, num_clips=args.num_clips)
    if not highlights:
        print("⚠️  沒有找到符合長度的精華片段，請調整 CLIPPER_MIN_SEC / CLIPPER_MAX_SEC。")
        return []

    output_paths = []
    for idx, highlight in enumerate(highlights, start=1):
        print(
            f"\n[{idx}/{len(highlights)}] "
            f"{highlight.start:.1f}s - {highlight.end:.1f}s "
            f"(score={highlight.score:.1f})"
        )

        print("   翻譯字幕中...")
        translations = translate_segments(highlight.segments, target_lang)

        sub_lines = [
            SubLine(
                start=seg.start - highlight.start,
                end=seg.end - highlight.start,
                original=seg.text,
                translated=translation,
            )
            for seg, translation in zip(highlight.segments, translations)
        ]

        clip_prefix = outdir / f"clip_{idx:02d}"
        ass_path, srt_path = write_subtitles(sub_lines, str(clip_prefix))

        output_path = str(clip_prefix.with_suffix(".mp4"))
        print("   剪輯 + 燒錄字幕中...")
        cut_clip_with_subtitles(
            source_video=args.input,
            start=highlight.start,
            duration=highlight.duration,
            ass_path=ass_path,
            output_path=output_path,
            vertical=not args.no_vertical,
        )

        print(f"   ✅ 完成: {output_path}  (字幕: {srt_path})")
        output_paths.append(output_path)

    print(f"\n🎉 全部完成！共產出 {len(output_paths)} 支短片，在 {outdir}/")
    return output_paths


if __name__ == "__main__":
    run(parse_args())
