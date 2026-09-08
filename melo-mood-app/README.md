# Melo Mood

用你自己的聲音，對潛意識說話。AI 個人化冥想引導 · 聲音複製 · 睡前放鬆導引 · 心情與感恩日記。

> 命名刻意避開「顯化」二字（錫蘭事件後的負面聯想），對外一律用「冥想 / 自我肯定 / 神經可塑性」。

## 立刻試用

```bash
# 任何靜態伺服器都行；麥克風權限需要 localhost 或 https
cd melo-mood-app && python3 -m http.server 8080
# 開 http://localhost:8080
```

單一 `index.html`，零建置、零依賴。所有資料存在瀏覽器 `localStorage`。

## 功能

| 分頁 | 內容 |
|---|---|
| **開始設定** | 4 步問卷：最近想改善什麼（睡不好／焦慮／缺自信…）→ 方向與每日時長 → 語氣 → 錄音。答案會寫進引導詞開頭與睡前導引 |
| **今日** | 依目標 × 日期產生的每日肯定語、正在改善的狀態、3 秒心情打卡、連續天數、快速入口 |
| **冥想** | 依目標／長度（3・7・12 分）／語氣（溫柔・堅定・Baddie）動態生成引導詞，會引用你最近的日記與狀態；呼吸球 + 逐句高亮播放 |
| **睡眠** | 睡前放鬆導引：身體掃描 → 10 到 1 倒數 → 目標暗示 → 入睡；棕噪音環境音；調暗螢幕 |
| **日記** | 心情 1–5、三件感謝、筆記、標籤；30 天心情圖；本週洞察 |
| **我** | 聲音樣本狀態、目標與語氣、方案、API 金鑰、匯出 JSON |

## 聲音（三層）

| 情況 | 播什麼 |
|---|---|
| 沒有金鑰 | `assets/demo-*.mp3`：兩段用 Melo 自己的 ElevenLabs 複製聲預先生成的示範（🎤×💅×3 分 與 睡前導引），逐句時間點已對好；其他組合用瀏覽器 zh-TW 語音 |
| 有 **ElevenLabs API key** | 每一句即時合成（`eleven_multilingual_v2`，句子快取），可在「我 → 選擇播放聲音」挑帳號裡任何聲音 |
| 金鑰 + 錄音 | 樣本上傳建立 Instant Voice Clone，之後全部用你的聲音 |

填入 **Claude API key** 後，「冥想」頁會多一顆「✦ AI 深度」，讓 Claude 讀你最近 5 篇日記重寫引導詞。

> Demo 為了零後端直接從瀏覽器呼叫 API。正式版請走 `backend/` 的 Edge Functions，金鑰不進手機。

## 專案結構

```
melo-mood-app/
├─ index.html                     # 整個 App
├─ assets/demo-*.mp3              # Melo 聲音的示範音檔（mono 48kbps）
├─ BUSINESS.md                    # SaaS 商業計畫
└─ backend/
   ├─ supabase/schema.sql         # 資料表 + RLS
   └─ edge-functions/
      ├─ generate-script.ts       # Claude 腳本生成
      └─ synthesize.ts            # ElevenLabs 複製聲音 + 合成 + 快取
```

## 下一步

1. `supabase init` → 套用 `schema.sql` → 部署兩支 Edge Function
2. 把 `index.html` 裡的 `generateWithClaude` / `playCloned` 改呼叫 Edge Function
3. PWA manifest + Capacitor 打包上 TestFlight
