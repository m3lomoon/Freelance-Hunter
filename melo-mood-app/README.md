# Melo Mood

用你自己的聲音，對潛意識說話。AI 顯化腳本 · 聲音複製 · 睡前催眠導引 · 心情與感恩日記。

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
| **今日** | 依目標 × 日期產生的每日肯定語、3 秒心情打卡、連續天數、快速入口 |
| **顯化** | 依目標／長度（3・7・12 分）／語氣（溫柔・堅定・Baddie）動態生成腳本，會引用你最近的日記；呼吸球 + 逐句高亮播放 |
| **睡眠** | 12 分鐘睡前催眠：身體掃描 → 10 到 1 倒數 → 目標暗示 → 入睡；棕噪音環境音；調暗螢幕 |
| **日記** | 心情 1–5、三件感謝、筆記、標籤；30 天心情圖；本週洞察 |
| **我** | 聲音樣本狀態、目標與語氣、方案、API 金鑰、匯出 JSON |

## 聲音

- 預設用瀏覽器內建 zh-TW 語音（Web Speech API）。
- 在「我」填入 **ElevenLabs API key** 後重錄聲音，樣本會上傳建立 Instant Voice Clone，之後所有腳本都用你的聲音合成。
- 填入 **Claude API key** 後，「顯化」頁會多一顆「✦ AI 深度」，讓 Claude 讀你最近 5 篇日記重寫腳本。

> Demo 為了零後端直接從瀏覽器呼叫 API。正式版請走 `backend/` 的 Edge Functions，金鑰不進手機。

## 專案結構

```
melo-mood-app/
├─ index.html                     # 整個 App
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
