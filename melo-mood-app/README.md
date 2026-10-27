# Melo Mood

用你自己的聲音，對潛意識說話。AI 個人化冥想引導 · 聲音複製 · 睡前放鬆導引 · 心情與感恩日記。

> 命名刻意避開「顯化」二字（錫蘭事件後的負面聯想），對外一律用「冥想 / 自我肯定 / 神經可塑性」。

## 視覺

單一深色版本（near-black `#0D0D10` 底），每個分類都有自己的 mesh 漸層方塊，**介面裡沒有任何 emoji**：
情境、目標、語氣、呼吸節奏、環境音全部用漸層色塊當識別，數字用 Syne 粗體大字，標記用酸黃三角。
`.mesh` + `.g-*`（方塊）與 `.gw-*`（寬版 hero）兩組漸層，共 12 個色系。

## 誰來唸給你聽

每個聆聽畫面（情境冥想、每日練習、睡前導引）頂部都有聲音 chip，點開是一張張帶人物介紹的卡片：
**Melo 的聲音**（創辦人複製聲）· **溫柔男聲**（Evan）· **Melo 品牌聲** · **你自己的聲音** · **系統聲音**。
每個聲音有角色、介紹與目前可用狀態（即時合成／只有預錄的幾段／還沒錄音），選了之後所有引導都跟著換。
有 ElevenLabs 金鑰時，「我 → 選擇播放聲音」還能挑帳號裡的任何聲音。

## 用自己的聲音，不用金鑰

沒有 ElevenLabs 帳號一樣可以用自己的聲音聽引導。「我 → 聲音錄音室」把每日練習與睡前導引的固定句子（共 44 句）一句一句錄一遍，
照著唸就好，不用背；每句錄好自動存進瀏覽器的 IndexedDB（不會上傳），中途離開也不會不見，之後回來從沒錄的那句繼續。
錄完一段（每日練習或睡前導引）的全部句子後，選「你自己的聲音」那段就會播放你錄的音檔，逐句接著播，呼吸與停頓照舊。
文字裡的「Melody」會自動換成你自己的名字，唸的時候不會叫錯人。
想要任何情境冥想都用自己的聲音、句子還能無限生成，才需要錄 30 秒交給 ElevenLabs 複製聲音（見上一節）。

## 方案：Free / Glow / Muse

| 方案 | 內容 | 怎麼做到的 |
|---|---|---|
| **Free** | 日記、呼吸、森林、4 種助眠音、4 種急救情境（焦慮/開會/約會/專注）、每天 1 段每日練習、系統聲音 | 全部在手機上 |
| **Glow** | Free 全部 + 其餘 9 種情境、主題廣場、自訂情境、每日練習不限次數、睡前導引、12 種助眠音、錄音室、30 天心情 + **Melo / Evan 真人聲音唸每一段** | Edge Function `voice`（我們的 ElevenLabs 帳號，句子層級快取） |
| **Muse** | Glow 全部 + **AI 複製你的聲音**、**AI 讀日記重寫引導詞**、**每週 AI 回顧 + 目標調頻**、Mumu Soul Care 茶飲 85 折 | Edge Functions `voice`（clone）與 `ai`（Claude） |

- 方案以伺服器為準：`subscriptions` 表 + 選用的 `BETA_TIER` 開關，前端只是照著顯示。
- 每月額度：Glow 6 萬字真人聲音；Muse 15 萬字 + 60 次 AI。聽過的句子會快取，重聽不扣額度。
- 日記只在 AI 生成的那一次送出，不存在伺服器；AI 聲音可以在「我 → 方案」刪除，連同合成過的音檔。
- 前端的鎖（`?paywall=1` 或正式開啟 `PAYWALL`）在試營運期間預設關閉；伺服器功能永遠照方案走。

**要上線，在 Supabase → Edge Functions → Secrets 設定：**
`ELEVENLABS_API_KEY`、`ANTHROPIC_API_KEY`；想讓試用者先體驗，可加 `BETA_TIER=glow` 或 `muse`（所有登入帳號都算這個方案，額度照算）。
Mumu 折扣碼填在 `index.html` 的 `MUMU={code,url}`，空的時候會員卡片不顯示這一項。

## 網頁版：掃 QR 就能用（募資期間的主要入口）

- **QR code**：`assets/qr.svg`（App 內「我 → 放在手機上 → 給朋友掃」與首頁「分享給朋友」會顯示）；印刷用的卡片在 `share/qr-card.png`。
  網址換了（例如綁自訂網域）：改 `index.html` 的 `PUBLIC_URL`，再跑 `python3 tools/make_qr.py`，會重做 `assets/qr.svg` 與 `share/qr-card.html`。
- **安裝到主畫面**：`manifest.webmanifest`；Android Chrome 會跳安裝提示，iPhone 用 Safari「分享 → 加入主畫面」，LINE / IG 內建瀏覽器會提示改用 Safari。
- **離線**：`sw.js`（頁面網路優先、圖片快取優先；語音檔、Supabase、ElevenLabs、Anthropic 不經過快取）。改版後想強制清舊快取，改 `sw.js` 的 `VERSION`。
- **法務**：`privacy.html`、`terms.html`（中英雙語）。**發布前要在兩個檔案裡把「客服信箱」填進去**，並請專業人士看過。
- **刪除帳號**：「我 → 方案 → 刪除帳號」→ Edge Function `delete-account`：先停綠界定期扣款（綠界沒回應就不刪）、刪 ElevenLabs 的 AI 聲音與音檔、最後刪登入帳號；方案、用量、聲音紀錄隨帳號一起消失。

> 原生 App（App Store / Google Play）刻意沒做：需要 Apple 內購取代綠界、原生殼與審核流程，等募資後交給工程師。
> 現在的網頁版已經把 Apple 會查的基本功（隱私條款、刪帳號、沒有假功能）補齊，之後可以直接接上。

## 坐上 Melo 雲（自拍分享卡）

冥想結束 →「坐上 Melo 雲拍一張」，或「我 → 分享卡」。前鏡頭即時去背（MediaPipe selfie segmenter，在手機上跑，照片不上傳），
把人放到 **MELO / MOOD 棉花雲字**上，疊上今天的冥想時間、前後分數、連續天數，3 秒倒數自拍，一鍵分享到 IG 限動（Web Share）。
沒有相機時可以「從相簿選一張」；去背載入失敗時改用圓框。
素材：`assets/cloud-sky.jpg`（天空）、`assets/cloud-letters.webp`（去背雲字，蓋在人前面）、`assets/selfie_segmenter.tflite`。

## 速度

引導詞預設是「慢」。播放器上的 ◷ 可以切 很慢／慢／一般，句子之間的留白與語速一起變。太快會讓人更緊張，所以預設偏慢。

## 名字

第一次開啟先問名字，之後所有引導詞、睡前導引、錄音稿都直接叫這個名字。
預錄音檔唸的是「Melody」，所以名字不同時會自動改用系統聲音或你的 ElevenLabs 聲音，不會叫錯人。
想看範例資料，onboarding 第一頁有「先看看範例（Melody 的帳號）」。

## 語言

繁體中文（原始）· 简体中文 · English。左側或「我 → 語言」切換，介面、引導詞與**語音都會跟著換**。
簡體用完整字元表加一份台灣／大陸詞彙對照（訊息→消息、螢幕→屏幕、金鑰→密钥、聲音複製→声音克隆…）。
英文是逐句翻譯的字典；翻不完整的句子會整句保留中文，不會出現半中半英。

## App icon 與安裝

`assets/icon-*.png` 是同一套 mesh 漸層加同心圓標記（與「冥想」分頁圖示同源）。
PWA manifest 在執行時產生，所以放在任何網址都能安裝：
**iOS Safari** 分享 → 加入主畫面；**Android Chrome** 選單 → 安裝應用程式。裝完就是全螢幕、有 icon 的 App。

## 怎麼給別人試用

| 方式 | 做法 | 適合 |
|---|---|---|
| **Artifact 連結** | 我發佈的那個連結，右上角分享給任何人 | 最快，傳給朋友看一眼 |
| **GitHub Pages** | repo → Settings → Pages → 選 `claude/personalized-manifestation-app-x3a8j4` 分支、根目錄；網址是 `https://m3lomoon.github.io/Freelance-Hunter/melo-mood-app/` | Beta 名單、固定網址、可加到主畫面 |
| **Netlify Drop** | 把 `melo-mood-app/` 整個資料夾拖到 app.netlify.com/drop | 不想動 Git，30 秒有網址 |
| **本機** | 見下方 | 自己測麥克風與金鑰 |

麥克風錄音需要 https 或 localhost，所以 Pages / Netlify 都可以，直接開檔案不行。
每個人的資料各自存在自己的瀏覽器，互不干擾。

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
| **今日** | 每日肯定語、心情打卡、連續天數，加上 **內容牆**（為你挑的／現在最多人在做／回到你自己／也可以試試），以及送朋友 30 天的邀請 |
| **收藏** | 獨立清單頁：縮圖、♥、標題、類型 · 時長。冥想、呼吸、環境音、睡前導引都能收藏 |
| **冥想** | **情境冥想庫**：13 種場合（焦慮急救、開會前、約會前、上台前、發文前、情緒降溫、早晨開機、專注啟動、談錢前、經期照顧、一杯茶、創作前、轉場重設）＋ **自訂情境（選項式，可以完全不打字）**：選一個最接近的場合 → 名稱、時機、呼吸節奏自動帶入，句子用點選的（也能讓 AI 生成或自己加）。每段配好呼吸節奏與肯定語，開始前後各打一次分，App 會算出「這段對你降了幾分」。另有**每日練習**（依方向／長度／語氣動態生成，會引用日記） |
| **呼吸練習** | 6 種節奏（生理嘆息、方箱、4-7-8、共振 5-5、4-6 安撫、提振），視覺呼吸球帶節拍，**吸氣／吐氣有合成音效**（濾波噪音，吸氣上揚、吐氣下沉，可關），秒數與回合可自訂 |
| **睡眠** | 睡前放鬆導引：身體掃描 → 10 到 1 倒數 → 目標暗示 → 入睡；棕噪音環境音；調暗螢幕 |
| **日記** | 心情 1–5、三件感謝、筆記、標籤；30 天心情圖；本週洞察 |
| **我** | 聲音樣本、方向與狀態、**效果排行**（哪一段最有效）、每日提醒、IG 分享卡、方案、API 金鑰、匯出資料 |

### 環境音（即時合成，不用下載音檔）
白噪音 · 棕噪音 · 雨聲 · 海邊 · 山林裡 · 頌缽 — **可以疊**，音量獨立調，能跟語音引導同時播。

## 聲音（三層）

| 情況 | 播什麼 |
|---|---|
| 沒有金鑰 | `assets/*.mp3`：焦慮急救、開會前、約會前、專注啟動、每日練習、睡前導引共 6 段預錄（每日／睡前另有男聲版），逐句時間點已對好；其他組合用瀏覽器 zh-TW 語音 |
| 有 **ElevenLabs API key** | 每一句即時合成（`eleven_multilingual_v2`，句子快取），預設用 **Melo 品牌聲 `ZGNKRFGTTnfytxotHN56`**；該聲音尚未 fine-tune 完成時會自動回退到複製聲並提示。可在「我 → 選擇播放聲音」改成帳號裡任何聲音 |
| 金鑰 + 錄音 | 樣本上傳建立 Instant Voice Clone，之後全部用你的聲音 |

填入 **Claude API key** 後，「冥想」頁會多一顆「✦ AI 深度」，讓 Claude 讀你最近 5 篇日記重寫引導詞。

> Demo 為了零後端直接從瀏覽器呼叫 API。正式版請走 `backend/` 的 Edge Functions，金鑰不進手機。

## 專案結構

```
melo-mood-app/
├─ index.html                     # 整個 App
├─ assets/*.mp3                   # Melo 聲音的預錄音檔（mono 48kbps）
├─ assets/icon-*.png              # App icon（192 / 512 / 1024 / maskable）
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
