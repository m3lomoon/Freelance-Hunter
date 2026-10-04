#!/usr/bin/env bash
# 爆款影片獵手啟動腳本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/viral_finder"

echo "🎯 爆款影片獵手 - 啟動中..."

# 安裝依賴
if ! python -c "import streamlit" &>/dev/null; then
    echo "📦 安裝依賴套件..."
    pip install -r "$APP_DIR/requirements.txt"
fi

# 提示 ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "⚠️  未偵測到 ffmpeg，音頻下載功能將無法使用"
    echo "   macOS:  brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
fi

echo "🚀 啟動應用程式... 請在瀏覽器開啟 http://localhost:8501"
streamlit run "$APP_DIR/app.py" \
    --server.port 8501 \
    --server.headless false \
    --theme.base dark
