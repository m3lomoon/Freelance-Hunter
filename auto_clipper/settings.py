"""
Auto Clipper 設定檔
所有數值皆可用環境變數覆蓋，方便在不同影片上快速調整。
"""

import os

# ── 語音辨識 ────────────────────────────────────────────
# faster-whisper 模型大小：tiny / base / small / medium / large-v3
# 模型越大越準，但速度越慢。中文 podcast 建議至少 small。
WHISPER_MODEL_SIZE = os.environ.get("CLIPPER_WHISPER_MODEL", "medium")
WHISPER_DEVICE = os.environ.get("CLIPPER_WHISPER_DEVICE", "cpu")  # cpu / cuda
WHISPER_COMPUTE_TYPE = os.environ.get("CLIPPER_WHISPER_COMPUTE", "int8")

# ── 翻譯（雙語字幕）────────────────────────────────────
# 用 Anthropic API 做翻譯，沿用 config.py 裡的 ANTHROPIC_API_KEY
TRANSLATE_MODEL = os.environ.get("CLIPPER_TRANSLATE_MODEL", "claude-sonnet-5")

# ── 精華片段挑選 ────────────────────────────────────────
CLIP_MIN_SEC = float(os.environ.get("CLIPPER_MIN_SEC", 25))
CLIP_MAX_SEC = float(os.environ.get("CLIPPER_MAX_SEC", 75))
DEFAULT_NUM_CLIPS = int(os.environ.get("CLIPPER_NUM_CLIPS", 5))

# 會加分的「鉤子」詞彙／語氣（口語 podcast 常見的重點提示）
HOOK_KEYWORDS = [
    "重點是", "其實", "祕密", "秘密", "沒有人告訴你", "老實說", "說真的",
    "關鍵", "最重要", "血淚", "教訓", "後悔", "崩潰", "翻轉", "真相",
    "你知道嗎", "為什麼", "怎麼辦", "第一", "第二", "第三", "总结", "總結",
    "the secret", "honestly", "the key", "why", "how to", "the truth",
    "biggest mistake", "number one", "the reason",
]

# 出現這些字會扣分（贅字、開場閒聊、廣告置入常見用語）
FILLER_KEYWORDS = [
    "嗯", "呃", "那個", "就是說", "然後呢", "廣告時間", "業配",
    "um", "uh", "you know", "like i said", "sponsor",
]

# ── 輸出影片 ────────────────────────────────────────────
VERTICAL_OUTPUT = os.environ.get("CLIPPER_VERTICAL", "1") != "0"
OUTPUT_WIDTH = int(os.environ.get("CLIPPER_OUTPUT_WIDTH", 1080))
OUTPUT_HEIGHT = int(os.environ.get("CLIPPER_OUTPUT_HEIGHT", 1920))

# ── 雙語字幕樣式 ────────────────────────────────────────
SUB_FONT = os.environ.get("CLIPPER_SUB_FONT", "Noto Sans TC")
SUB_FONT_SIZE_PRIMARY = int(os.environ.get("CLIPPER_SUB_SIZE_PRIMARY", 64))
SUB_FONT_SIZE_SECONDARY = int(os.environ.get("CLIPPER_SUB_SIZE_SECONDARY", 46))
