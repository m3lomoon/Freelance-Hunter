# Auto Clipper 🎬

把一支長 podcast 影片，自動剪成好幾支**帶雙語字幕的短片**（適合 Reels / Shorts / TikTok）。

## 流程

```
長影片 → 語音辨識(faster-whisper) → 挑精華片段 → 翻譯(Claude) → 燒錄雙語字幕 → 直式短片
```

## 安裝

```bash
pip install -r requirements.txt
brew install ffmpeg   # macOS；Ubuntu 用 sudo apt install ffmpeg
```

翻譯功能沿用專案根目錄 `config.py` 裡的 `ANTHROPIC_API_KEY`。

## 使用方式

在 repo 根目錄執行：

```bash
python -m auto_clipper.cli --input podcast.mp4 --num-clips 5
```

輸出會放在 `clips_output/`：

- `clip_01.mp4`～`clip_05.mp4`：已裁成 9:16、燒錄雙語字幕的短片
- `clip_01.srt` / `.ass`：對應的雙語字幕檔（可另外匯入 CapCut 等軟體微調）

## 常用參數

| 參數 | 說明 | 預設 |
|---|---|---|
| `--input` | 來源影片路徑（必填） | — |
| `--num-clips` | 要剪幾支短片 | 5 |
| `--source-lang` | 來源語言代碼，留空自動偵測 | 自動 |
| `--target-lang` | 翻譯目標語言，留空依來源語言判斷（中↔英） | 自動 |
| `--whisper-model` | tiny/base/small/medium/large-v3，越大越準越慢 | medium |
| `--no-vertical` | 不裁成直式，保留原始比例 | 關閉 |

也可以用環境變數微調精華片段的長度、鉤子詞彙、字幕字體大小，細節看 `auto_clipper/settings.py`。

## 目前限制

- 精華片段挑選是關鍵字 + 語速的規則式評分，不是語意理解，效果好壞會跟你的鉤子詞彙表有關（可以在 `settings.py` 的 `HOOK_KEYWORDS` 依自己的節目風格調整）。
- 沒有自動加封面字卡/動態字幕動畫，字幕是靜態雙語兩行。
- 剪輯點目前只依語音斷句對齊，還沒接笑聲/掌聲/畫面偵測。
