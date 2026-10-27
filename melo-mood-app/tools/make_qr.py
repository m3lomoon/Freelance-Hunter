#!/usr/bin/env python3
"""Regenerate the QR code the app shows ("我 → 放在手機上") and the printable card.
   python3 tools/make_qr.py [url]      default: the public address in index.html (PUBLIC_URL)
   writes assets/qr.svg (shown in the app) and share/qr-card.html (open it, screenshot or print to PDF).
   needs: pip install qrcode"""
import re, sys, pathlib
import qrcode, qrcode.image.svg

root = pathlib.Path(__file__).resolve().parent.parent
url = sys.argv[1] if len(sys.argv) > 1 else re.search(r"PUBLIC_URL\s*=\s*'([^']+)'", (root / "index.html").read_text()).group(1)

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=2, box_size=10)
qr.add_data(url); qr.make(fit=True)
svg = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage).to_string().decode()
svg = re.sub(r'<\?xml[^>]*\?>', '', svg).replace('<svg ', '<svg shape-rendering="crispEdges" role="img" aria-label="Melo Mood QR code" ', 1)
(root / "assets" / "qr.svg").write_text(svg)

card = f"""<!doctype html><meta charset="utf-8"><title>Melo Mood QR</title>
<style>
  html,body{{margin:0}} body{{width:1080px;height:1350px;background:#0D0D10;color:#F5F5F7;display:grid;place-items:center;
    font-family:"Noto Sans TC","PingFang TC","WenQuanYi Zen Hei",system-ui,sans-serif}}
  .c{{text-align:center}} h1{{font-size:96px;letter-spacing:.04em;margin:0 0 8px;font-weight:800}}
  h1 i{{color:#E4FF57;font-style:normal}} p{{margin:0;color:#9B9BA8;font-size:36px}}
  .qr{{width:620px;height:620px;background:#fff;border-radius:44px;padding:36px;margin:64px auto 56px;box-sizing:border-box;
    box-shadow:0 0 120px rgba(228,255,87,.25)}} .qr svg{{width:100%;height:100%;display:block}}
  b{{display:block;font-size:44px;color:#E4FF57;margin-bottom:14px}} small{{display:block;margin-top:40px;font-size:26px;color:#6B6B7A;font-family:monospace}}
</style>
<div class="c"><h1>MELO<i>.</i>MOOD</h1><p>用自己的聲音，對潛意識說話</p>
<div class="qr">{svg}</div><b>掃一下就能用</b><p>iPhone 用 Safari 開，加到主畫面</p><small>{url}</small></div>"""
(root / "share" / "qr-card.html").write_text(card)
print("ok", url)
