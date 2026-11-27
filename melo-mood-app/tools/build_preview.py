"""Build the single-page preview published as a claude.ai artifact.

    python3 tools/build_preview.py OUT_DIR

writes OUT_DIR/melo-mood.html with the small assets inlined as data URIs (the preview
has no file server for them), and OUT_DIR/assets/v/{index.json,<voice>.json} with each
voice's clips bundled as base64, since the preview can hold only a few hundred files.
Publish melo-mood.html with the assets/v files alongside it.
"""
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
TYPES = {".mp3": "audio/mpeg", ".svg": "image/svg+xml", ".webp": "image/webp", ".tflite": "application/octet-stream"}


def data_uri(f):
    t = TYPES.get(f.suffix) or mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    return f"data:{t};base64," + base64.b64encode(f.read_bytes()).decode()


def main(out):
    out = Path(out)
    html = (APP / "index.html").read_text(encoding="utf-8")
    html = re.sub(r'<link rel="manifest"[^>]*>\n?', "", html)
    for f in sorted((APP / "assets").iterdir()):
        if f.is_file() and f.name not in ("og.jpg", "icon-1024.png"):
            html = html.replace(f"assets/{f.name}", data_uri(f))
    html = html.replace("<script>", "<script>window.VOICE_BUNDLED=true;</script>\n<script>", 1)
    (out / "assets" / "v").mkdir(parents=True, exist_ok=True)
    (out / "melo-mood.html").write_text(html, encoding="utf-8")
    lib = APP / "assets" / "v"
    if (lib / "index.json").exists():
        (out / "assets/v/index.json").write_text((lib / "index.json").read_text())
        for d in sorted(p for p in lib.iterdir() if p.is_dir()):
            clips = {f.stem: base64.b64encode(f.read_bytes()).decode() for f in sorted(d.glob("*.mp3"))}
            (out / f"assets/v/{d.name}.json").write_text(json.dumps(clips, separators=(",", ":")))
    for f in sorted(out.rglob("*")):
        if f.is_file():
            print(f"{f.relative_to(out)}: {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
