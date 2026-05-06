#!/bin/bash
# Freelance Hunter 一鍵安裝腳本

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📦 安裝目錄: $SCRIPT_DIR"

# 建立 log 目錄
mkdir -p "$SCRIPT_DIR/logs"

# 安裝 Python 套件
echo ""
echo "📦 安裝 Python 套件..."
pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet

# 確認 config 是否已填寫
echo ""
echo "🔧 請確認你已填寫 config.py 中的以下設定："
echo "   - TELEGRAM_BOT_TOKEN"
echo "   - TELEGRAM_CHAT_ID"
echo "   - ANTHROPIC_API_KEY"
echo ""
read -p "已填寫完畢？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "請先編輯 config.py，然後重新執行 setup.sh"
    exit 1
fi

# 測試 Telegram 連線
echo "📱 測試 Telegram 通知..."
python3 "$SCRIPT_DIR/main.py" --test

# 安裝 launchd 排程（每天早上 8:00 自動執行）
PLIST_SRC="$SCRIPT_DIR/com.freelancehunter.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.freelancehunter.plist"

echo ""
echo "⏰ 設定每日排程（早上 8:00）..."
cp "$PLIST_SRC" "$PLIST_DEST"
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"

echo ""
echo "✅ 安裝完成！"
echo ""
echo "每天早上 8:00 會自動搜尋案件並推播到你的 Telegram。"
echo ""
echo "常用指令："
echo "  立即執行一次：python3 $SCRIPT_DIR/main.py"
echo "  查看執行記錄：tail -f $SCRIPT_DIR/logs/output.log"
echo "  查看錯誤記錄：tail -f $SCRIPT_DIR/logs/error.log"
echo "  停止排程：    launchctl unload $PLIST_DEST"
echo "  重新啟動排程：launchctl load $PLIST_DEST"
