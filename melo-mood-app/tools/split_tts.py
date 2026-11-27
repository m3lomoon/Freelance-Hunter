"""Cut one ElevenLabs take that reads a whole theme list into one file per line.

    python3 tools/split_tts.py take.mp3 fightLow 12

writes assets/th/fightLow-0.mp3 … fightLow-11.mp3 (mono, 48 kbps, like the other
recordings). The take must read the lines in order with a paragraph break between
them; the cuts go in the middle of the N-1 longest pauses, so a comma inside a line
never splits it. Stops without writing anything if the take has fewer pauses than that.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "assets" / "th"
PAD = 0.12  # seconds of room kept before and after each line


def silences(src):
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=noise=-38dB:d=0.3", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(starts, ends))


def duration(src):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
        capture_output=True, text=True,
    ).stdout
    return float(out)


def main(src, key, n):
    total = duration(src)
    found = silences(src)
    gaps = [(s, e) for s, e in found if s > 0.05 and e < total - 0.05]
    head = next((e - PAD for s, e in found if s <= 0.05), 0.0)            # silence before the first word
    tail = next((s + PAD for s, e in found if e >= total - 0.05), total)  # and after the last
    if len(gaps) < n - 1:
        sys.exit(f"{src}: found {len(gaps)} pauses, need {n - 1}; nothing written")
    cuts = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[: n - 1])
    bounds = [max(0.0, head)]
    for s, e in cuts:
        bounds += [s + PAD, e - PAD]
    bounds.append(min(total, tail))
    OUT.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        a, b = bounds[2 * i], bounds[2 * i + 1]
        dst = OUT / f"{key}-{i}.mp3"
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
             "-ac", "1", "-b:a", "48k", str(dst)],
            check=True,
        )
        print(f"{dst.name}: {b - a:.2f}s")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
