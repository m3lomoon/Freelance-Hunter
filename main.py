#!/usr/bin/env python3
"""
Freelance Hunter - 自動接案搜尋機器人
每天自動搜尋各平台案件，用 AI 過濾後推播到 Telegram
"""

import json
import os
import sys
from datetime import date

# 確保可以 import 同目錄的模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers import ptt, job104, taker, pro360, waibao, freelancer_api, yourator
from filter import filter_jobs
from notifier import notify, test_connection

SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen_jobs.json")


def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                data = json.load(f)
                # 只保留最近 30 天的記錄，避免檔案無限增長
                today = str(date.today())
                cleaned = {k: v for k, v in data.items()
                           if abs((date.today() - date.fromisoformat(v)).days) <= 30}
                return set(cleaned.keys())
        except Exception:
            return set()
    return set()


def save_seen(seen: set, new_links: list):
    try:
        existing = {}
        if os.path.exists(SEEN_FILE):
            with open(SEEN_FILE, "r") as f:
                existing = json.load(f)
        today = str(date.today())
        for link in new_links:
            existing[link] = today
        # 清理 30 天以上的舊記錄
        existing = {k: v for k, v in existing.items()
                    if abs((date.today() - date.fromisoformat(v)).days) <= 30}
        with open(SEEN_FILE, "w") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[seen_jobs] 儲存失敗: {e}")


def run():
    print(f"\n{'='*50}")
    print(f"🔍 Freelance Hunter 啟動 — {date.today()}")
    print(f"{'='*50}")

    seen = load_seen()
    all_jobs = []

    # ── 各平台爬取 ──────────────────────────────
    scrapers = [
        ("PTT", ptt.scrape),
        ("104外包", job104.scrape),
        ("Taker", taker.scrape),
        ("518人力銀行", pro360.scrape),
        ("外包達人", waibao.scrape),
        ("Yourator遠端", yourator.scrape),
        ("Freelancer", freelancer_api.scrape
         if __import__("config").FREELANCER_API_KEY
         else freelancer_api.scrape_without_api),
    ]

    for name, scrape_fn in scrapers:
        try:
            print(f"\n[{name}] 爬取中...")
            jobs = scrape_fn()
            # 過濾已看過的案件
            new_jobs = [j for j in jobs if j["link"] not in seen]
            print(f"[{name}] 取得 {len(jobs)} 筆，其中 {len(new_jobs)} 筆為新案件")
            all_jobs.extend(new_jobs)
        except Exception as e:
            print(f"[{name}] 發生錯誤: {e}")

    print(f"\n📊 合計新案件: {len(all_jobs)} 筆")

    if not all_jobs:
        print("今天沒有新案件")
        notify([])
        return

    # ── AI 過濾 ─────────────────────────────────
    print("\n🤖 AI 過濾中...")
    relevant_jobs = filter_jobs(all_jobs)

    # ── 記錄已看過的連結 ─────────────────────────
    new_links = [j["link"] for j in all_jobs]
    save_seen(seen, new_links)

    # ── 發送 Telegram 通知 ───────────────────────
    print(f"\n📱 發送通知：{len(relevant_jobs)} 筆相關案件")
    notify(relevant_jobs)

    print(f"\n✅ 完成！")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("測試 Telegram 連線...")
        test_connection()
    else:
        run()
