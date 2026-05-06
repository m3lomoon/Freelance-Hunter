import requests
from datetime import date
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def _escape(text: str) -> str:
    """Escape HTML special characters in plain text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_message(text: str):
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if not resp.ok:
            print(f"[Telegram] 發送失敗: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"[Telegram] 發送失敗: {e}")


def notify(jobs: list):
    if not jobs:
        send_message(f"📭 <b>{date.today()} 接案日報</b>\n\n今天沒有找到相關案件，明天繼續加油！")
        return

    today = date.today().strftime("%Y/%m/%d")

    freelance = [j for j in jobs if j.get("job_type", "接案") == "接案"]
    remote    = [j for j in jobs if j.get("job_type", "") == "遠端兼職 💼"]

    header = (
        f"🎯 <b>{today} 每日機會日報</b>\n"
        f"接案 {len(freelance)} 筆 ｜ 遠端兼職 {len(remote)} 筆\n\n"
    )

    # 遠端兼職優先顯示，再接案，依平台分組
    ordered = []
    if remote:
        ordered.append(("💼 遠端兼職機會", remote))
    if freelance:
        ordered.append(("🎬 接案機會", freelance))

    # 依平台分組（在各大類內）
    by_platform = {}
    for job in jobs:
        key = f"{job.get('job_type','接案')}|{job['platform']}"
        if key not in by_platform:
            by_platform[key] = []
        by_platform[key].append(job)

    # 建立訊息區塊，超過 3800 字元就分批
    chunks = []
    current = header

    MAX_PER_PLATFORM = 8  # 每個平台最多顯示幾筆

    for key, platform_jobs in by_platform.items():
        _, platform = key.split("|", 1)
        shown = platform_jobs[:MAX_PER_PLATFORM]
        extra = len(platform_jobs) - len(shown)
        section = f"📌 <b>{_escape(platform)}</b> ({len(platform_jobs)} 筆)\n"
        for j in shown:
            title = _escape(j["title"][:55])
            link = j["link"]
            desc = _escape(j.get("description", "")[:70])
            line = f'• <a href="{link}">{title}</a>'
            if desc:
                line += f"\n  └ {desc}"
            line += "\n"
            section += line
        if extra > 0:
            section += f"  ＋ 另有 {extra} 筆，請直接上平台查看\n"
        section += "\n"

        if len(current) + len(section) > 3800:
            chunks.append(current)
            current = section
        else:
            current += section

    if current.strip():
        chunks.append(current)

    for msg in chunks:
        if msg.strip():
            send_message(msg)

    print(f"[Telegram] 已發送 {len(jobs)} 筆案件通知")


def test_connection():
    send_message("✅ Freelance Hunter 連線測試成功！每天早上我會自動幫你搜尋案件。")
