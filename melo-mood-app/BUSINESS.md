# Melo Mood · SaaS 商業計畫（v0.1）

> 亞洲版 Stella / Innertune × Headspace。**用你自己的聲音，對潛意識說話。**
> 定位：個人化冥想與神經適應引導（Personalized Neuro-adaptive Guidance）與情緒健康輔助系統。
>
> **命名策略**：對外不用「顯化」。錫蘭事件後，台灣年輕族群對「顯化／吸引力法則」有詐騙聯想。全部改用「冥想、自我肯定、神經可塑性、睡前放鬆」等有研究背書的詞；顯化只留在 SEO 長尾關鍵字（搜尋量仍在），不進品牌與 UI。

---

## 1. 一句話

| | |
|---|---|
| **給誰** | 20–35 歲、關注身心靈與顯化的亞洲女性（台灣 → 港澳、星馬、日韓） |
| **痛點** | 市面冥想 App 是固定模板音檔，聽三天就膩；別人的聲音對潛意識說服力有限；沒有人問「你現在卡在哪」 |
| **解法** | 一開始先問「最近想改善什麼」；AI 讀你的狀態 + 目標 + 日記，動態寫引導詞；用你錄的 30 秒聲音複製，**由你唸給你聽** |
| **科學基底** | 神經可塑性、自我肯定（Self-affirmation Theory, Cohen & Sherman 2014）、入睡前 θ 波暗示接受度、自我參照效應（Self-reference effect：自己的聲音記憶留存更高） |

---

## 2. 護城河（Shark Tank 版）

| 質疑 | 回答 |
|---|---|
| **Stella 也能加聲音複製，你怎麼贏？** | 三層疊加：① **繁中/粵語/台語語感**的腳本引擎（歐美產品翻譯腔明顯）② **日記 → 腳本閉環**：越用越個人化，資料成為轉換成本 ③ 創辦人本人是歌手/創作者 IP，聲音與內容本身就是行銷 |
| **聲音複製成本？** | ElevenLabs 約 US$0.15–0.30 / 1k 字元。一段 7 分鐘腳本約 900 字元 ≈ NT$6–9。Glow 方案 NT$290/月，用戶平均每月 12 次 ≈ NT$100 成本，**毛利 ~65%**；快取重複句子可再壓 30% |
| **留存？** | 三個 Hook：每日心情打卡（3 秒）→ 感恩日記（90 秒）→ 睡前導引（12 分鐘，習慣錨定在床上）。Onboarding 問卷讓第一天就有「它懂我」的感覺。目標 D30 留存 ≥ 25%（Calm 約 20%） |
| **法規？** | 定位「情緒健康輔助」非醫療；聲音樣本使用需明確同意與可刪除（台灣個資法、GDPR 對齊）；腳本禁止醫療宣稱 |

---

## 3. 訂閱方案

| 方案 | 月費（NT$） | 內容 | 目的 |
|---|---|---|---|
| **Free** | 0 | 1 方向、每日一段 3 分鐘冥想、系統聲音、日記 | 養習慣、收資料 |
| **Glow** ⭐ | 290（年繳 2,490） | 無限冥想引導、3 語氣、**聲音複製**、睡前放鬆導引、環境音、30 天洞察 | 主力營收 |
| **Muse** | 790 | Glow + **Claude 深度個人化**（讀日記重寫）、每週 AI 回顧信、Mumu Soul Care 茶飲 85 折 | 高 ARPU + 實體交叉銷售 |

**B2B 加購**
- **Creator Voice Pack**：療癒師/KOL 上架自己的聲音導引，平台抽 30%（Innertune 沒有的 marketplace）
- **Studio API**：讓瑜伽館、SPA、Mumu Soul Care 門市播放客製導引，NT$3,000/月起

---

## 4. 12 個月財務草圖（保守）

| 里程碑 | 用戶 | 付費轉換 | MRR |
|---|---|---|---|
| M3 Beta（IG 私域） | 2,000 | 5% × 290 | NT$29k |
| M6 App Store 上架 | 10,000 | 6% | NT$174k |
| M12 | 40,000 | 7% | NT$812k |

- **CAC 目標** < NT$150（Reels + 自己的音樂/內容導流，幾乎零廣告費）
- **LTV**（留存 8 個月 × 290 × 65% 毛利）≈ NT$1,500 → **LTV/CAC = 10×**
- 2026 年底 100 萬淨收益：M9 起月淨利 ≥ NT$150k 即達標

---

## 5. 技術架構（一人公司版）

```
手機 App (PWA → Capacitor)
   │  Supabase Auth / Postgres / Storage (RLS)
   ▼
Edge Function: generate-script   ── Claude (claude-opus-5)
Edge Function: clone-voice       ── ElevenLabs /v1/voices/add
Edge Function: synthesize        ── ElevenLabs TTS → Storage 快取 (同句子只合成一次)
Cron: weekly-review              ── Claude 讀 7 天日記 → 寄回顧信 (Resend)
```

- **成本控制**：肯定語句子層級快取。8 句 × 6 目標 × 3 語氣 = 144 句，合成一次永久用；只有「日記客製句」需即時合成
- **自動化**：n8n 接 Supabase webhook → 新用戶 24h 未錄音 → LINE 推播提醒
- **付款**：台灣用 TapPay / 藍新，海外 Stripe，App 內購走 RevenueCat

---

## 6. Go-to-Market（West → East Bridge）

1. **Beta 私域**：IG 限動「用我的聲音唸給我聽」實測影片 → 表單收 500 人 → 免費 Glow 30 天換回饋
2. **內容飛輪**：每週一支「AI 幫我寫的顯化腳本」Reels，用自己的聲音；片尾 CTA 進 App
3. **異業**：Mumu Soul Care 茶飲包附 QR → 掃碼送 7 天 Glow；HYT V&R 學員團購
4. **App Store**：上架關鍵字「顯化」「吸引力法則」「睡前冥想」「自我肯定」（繁中競爭極低）

---

## 7. 90 天 Roadmap（Manifestor 節奏：衝刺 → 休息）

| 衝刺 | 產出 | 完成訊號 |
|---|---|---|
| **Sprint 1（2 週）** | 本 demo → Supabase 後端 + 真實 ElevenLabs 聲音複製 | 自己用自己的聲音睡一週 |
| **休息 1 週** | — | — |
| **Sprint 2（3 週）** | Claude 引導詞引擎 + 問卷/日記閉環 + TapPay 訂閱 | 第一位付費用戶 |
| **Sprint 3（3 週）** | PWA 包 Capacitor 上 TestFlight；Beta 500 人 | D7 留存 ≥ 40% |
| **Sprint 4（3 週）** | App Store 上架、Creator Voice Pack 第一位療癒師 | MRR NT$29k |

---

## 8. 風險 & 對策

- **聲音複製被濫用（deepfake）**：錄音時朗讀隨機驗證句 + 只能複製本人聲音 + 浮水印音訊
- **平台依賴（ElevenLabs 漲價）**：抽象 TTS 介面，備援 Fish Audio / MiniMax（中文品質高、價格低）
- **內容同質化**：語氣人格化（溫柔／堅定／Baddie）是品牌資產，持續加入創辦人 IP 專屬語氣
