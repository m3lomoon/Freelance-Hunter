"""Add one recorded batch to the voice library.

    python3 tools/voice_lib.py melo b01 take.mp3

cuts the take (one batch from tools/voice_batches.json, read in order with a blank line
between lines) into assets/v/<voice>/<hash>.mp3 and rewrites assets/v/index.json, which
the app loads to know which lines each voice can say. Refuses a take whose clips look
wrong (fewer pauses than lines, or a clip under 0.35 s or over 12 s) so a bad cut never
reaches the app.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

from split_tts import cut

HERE = Path(__file__).resolve().parent
LIB = HERE.parent / "assets" / "v"


def reindex():
    index = {d.name: sorted(f.stem for f in d.glob("*.mp3")) for d in sorted(LIB.iterdir()) if d.is_dir()}
    (LIB / "index.json").write_text(json.dumps(index, separators=(",", ":")))
    return {k: len(v) for k, v in index.items()}


def main(voice, batch_id, take):
    batches = {b["id"]: b for b in json.loads((HERE / "voice_batches.json").read_text())}
    lines = batches[batch_id]["lines"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp_files = [Path(tmp) / f"{l['h']}.mp3" for l in lines]
        lengths = cut(take, tmp_files)
        bad = [(l["t"], round(s, 2)) for l, s in zip(lines, lengths) if not 0.35 <= s <= 12]
        if bad:
            sys.exit(f"{batch_id}: clips out of range, nothing added: {bad}")
        (LIB / voice).mkdir(parents=True, exist_ok=True)
        for f in tmp_files:
            shutil.move(str(f), LIB / voice / f.name)
    print(f"{voice} {batch_id}: {len(lines)} lines added; library now {reindex()}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
