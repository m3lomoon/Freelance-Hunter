# ============================================================
# 設定檔 - 請填入你的 API 金鑰和關鍵字
# ============================================================

# Telegram 通知設定（免費）
# 設定步驟：找 @BotFather → /newbot → 取得 token
# 取得 chat_id：找 @userinfobot 傳訊息給它
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8680893862:AAEKpSZbnfKW8IDD-aqzK2z94TWkR6Vk7iw")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID",   "8609823536")
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY",  "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")

# Freelancer.com API（可選，有更好的結果）
# 申請：https://developers.freelancer.com/
FREELANCER_API_KEY = ""  # 留空則跳過

# ============================================================
# 你的專長描述（給 AI 用來判斷案件相關性）
# ============================================================
MY_PROFILE = """
我是一位自由接案者，專長如下：
- AI MV 製作：使用 Sora、Runway、Kling 等 AI 工具製作音樂影片
- AI 廣告影片：製作品牌宣傳、產品廣告的 AI 生成影片
- 翻譯：中英文互譯、文件翻譯、影片字幕翻譯、合約翻譯
- 影片剪輯與後製：剪輯、調色、字幕、特效合成
- 歌曲製作：詞曲創作、編曲、配樂、音效設計
- 案件文件翻譯：法律文件、商業合約、技術文件翻譯
"""

# ── 遠端兼職工作條件 ──────────────────────────────
REMOTE_JOB_MIN_SALARY = 40000  # NT$ 月薪最低門檻
REMOTE_JOB_PROFILE = """
我也在找全遠端兼職工作，條件：
- 全遠端（WFH），不接受需到場的工作
- 月薪 NT$40,000 以上（時薪換算亦可）
- 可接受：影片剪輯、翻譯、字幕、音樂、AI相關、內容創作、社群媒體
- 不接受：需到場、業務電銷、MLM、需繳保證金
"""

# 搜尋關鍵字（用於各平台搜尋）
SEARCH_KEYWORDS = [
    # 影片相關
    "AI影片", "AI MV", "MV製作", "music video", "AI video",
    "AI廣告", "廣告影片", "影片製作", "影片後製",
    "剪輯", "後製", "video editing", "video production",
    # 翻譯相關
    "翻譯", "translation", "字幕翻譯", "subtitle", "文件翻譯",
    "中英翻譯", "英文翻譯", "合約翻譯",
    # 音樂相關
    "歌曲", "音樂製作", "作曲", "配樂", "music production",
    "song", "jingle", "背景音樂",
    # 遠端兼職
    "遠端", "居家上班", "WFH", "兼職",
]

# 每天執行時間（24小時制）
SCHEDULE_HOUR = 8
SCHEDULE_MINUTE = 0
