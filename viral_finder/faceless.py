import os
import anthropic


def _claude(prompt: str, max_tokens: int = 3000) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("請先在左側欄輸入 Anthropic API Key")
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── 1. 利基市場發現器 ────────────────────────────────────────────────────────

NICHE_CATEGORIES = [
    "全部熱門",
    "歷史與神秘",
    "科學與宇宙",
    "恐怖與靈異",
    "財經與理財",
    "心理與哲學",
    "動物與自然",
    "犯罪與真實案件",
    "AI 與科技",
    "勵志與成功學",
    "奇聞異事",
    "地理與文化",
]


def find_niches(category: str = "全部熱門", language: str = "繁體中文") -> str:
    return _claude(f"""你是一位專精 YouTube 無臉頻道（Faceless Channel）的市場分析師。

請用{language}列出 10 個目前最適合華語市場的「高獲利、低競爭」無臉頻道利基市場。
類別偏好：{category}

每個利基市場請提供：

【利基名稱】
📊 市場潛力：★★★★☆（1-5星）
💰 獲利潛力：（CPM 估算區間）
🏆 競爭程度：低 / 中 / 高
🎯 目標受眾：
📹 內容形式：（AI 生成畫面 / 圖片輪播 / 文字動畫）
✅ 為什麼適合無臉頻道：
💡 前5支影片建議題目：
  1.
  2.
  3.
  4.
  5.
⚠️ 注意事項：

---

最後加上「本週最推薦」選出前3名並說明原因。""", 4000)


# ── 2. AI 腳本生成器 ─────────────────────────────────────────────────────────

SCRIPT_STYLES = ["紀錄片旁白", "懸疑故事", "教育解說", "第一人稱故事", "新聞播報"]
SCRIPT_LENGTHS = {
    "短片 Shorts（60秒）": 150,
    "短影片（3分鐘）": 450,
    "中等長度（8分鐘）": 1200,
    "長影片（15分鐘）": 2200,
}


def generate_script(
    topic: str,
    length_label: str = "短影片（3分鐘）",
    style: str = "紀錄片旁白",
    language: str = "繁體中文",
) -> str:
    word_count = SCRIPT_LENGTHS.get(length_label, 450)

    return _claude(f"""你是一位頂尖的 YouTube 腳本作家，專門為無臉頻道撰寫高留存率的影片腳本。

主題：{topic}
風格：{style}
語言：{language}
目標字數：約 {word_count} 字

請撰寫一個完整的影片腳本，格式如下：

# 🎬 影片腳本：{topic}

## ⏱ 建議時長：{length_label}

---

## 🪝 開場鉤子（前10秒）
[這是最重要的部分，必須讓觀眾停止滑動]

---

## 📖 正文腳本

[用段落格式撰寫完整腳本，每段前面標注時間點]
[00:10] ...
[00:45] ...
以此類推

---

## 🎯 結尾 CTA
[訂閱提醒 + 下一支影片預告]

---

## 🎵 配樂建議
建議的背景音樂情緒與風格

## 📸 畫面風格建議
整體視覺風格描述（給 AI 影片生成工具參考）

---
腳本必須：
- 開場前10秒就要有強烈鉤子
- 每30秒有一個小高潮維持留存率
- 語氣自然，像真人在說話
- 避免過度正式的書面語""", 4000)


# ── 3. SEO 優化包 ────────────────────────────────────────────────────────────

def generate_seo_package(topic: str, script_excerpt: str = "", language: str = "繁體中文") -> str:
    script_part = f"\n腳本摘要：\n{script_excerpt[:500]}" if script_excerpt else ""

    return _claude(f"""你是 YouTube SEO 專家。請為以下影片生成完整的 SEO 優化包，用{language}輸出。

影片主題：{topic}{script_part}

請生成：

## 🏆 影片標題（5個選項，由強到弱排序）
[格式：每個標題控制在 60 字元以內，含關鍵字]

## 📝 影片說明欄（完整版）
[第一段：150字摘要（含主要關鍵字）]
[第二段：影片章節時間戳]
[第三段：相關資源連結預留位置]
[第四段：訂閱 CTA]
[第五段：免責聲明預留位置]

## 🏷️ 標籤（30個）
[混合：精確關鍵字 + 長尾關鍵字 + 廣泛關鍵字]

## 📌 關鍵字策略
主要關鍵字：
次要關鍵字：
長尾關鍵字：

## 📊 預估搜尋流量
（根據主題分析可能的月搜尋量區間）

## 💡 發布時機建議
最佳發布星期與時間""", 3000)


# ── 4. 縮圖生成 Prompt ───────────────────────────────────────────────────────

THUMBNAIL_STYLES = [
    "震驚表情 + 大字標題",
    "神秘暗黑風",
    "科幻未來感",
    "紀錄片風格",
    "懸疑驚悚",
    "教育資訊圖",
    "極簡現代",
]


def generate_thumbnail_prompts(topic: str, style: str = "震驚表情 + 大字標題") -> str:
    return _claude(f"""你是 YouTube 縮圖設計師，專門優化點擊率（CTR）。

影片主題：{topic}
設計風格：{style}

請生成：

## 🖼️ 縮圖設計方案（3個）

### 方案一
**視覺概念：**
**主要元素：**
**色彩搭配：**（背景色 / 文字色 / 強調色）
**文字：**（縮圖上的大字，最多8個字）

**Midjourney Prompt（英文）：**
```
[詳細的英文 Midjourney/DALL-E prompt]
```

**Stable Diffusion Prompt（英文）：**
```
[詳細的英文 SD prompt]
```

### 方案二
[同上格式]

### 方案三
[同上格式]

---

## 📐 技術規格建議
- 尺寸：1280 × 720px（16:9）
- 字體建議：
- 安全區域提醒：

## ✅ 高 CTR 縮圖原則
（針對此主題的3條最重要建議）""", 3000)


# ── 5. AI 分鏡腳本 ──────────────────────────────────────────────────────────

def generate_storyboard(script: str, video_style: str = "AI 動畫風格") -> str:
    script_excerpt = script[:2000]

    return _claude(f"""你是一位 AI 影片導演，專門為無臉 YouTube 頻道製作分鏡腳本。

影片腳本（摘要）：
{script_excerpt}

視覺風格：{video_style}

請生成逐場景的分鏡腳本，每個場景包含：
- 時間點
- 旁白文字（直接對應腳本）
- 畫面描述
- Kling/Sora/Runway 可用的 AI 影片生成 Prompt（英文）
- 轉場方式
- 音效建議

格式：

# 🎬 AI 分鏡腳本

---

## 場景 1｜[00:00 - 00:10]
**旁白：** [腳本文字]

**畫面描述：** [用中文描述畫面]

**🤖 AI 影片 Prompt（貼入 Kling/Sora/Runway）：**
```
[英文 prompt，詳細描述鏡頭、動作、光線、風格]
```

**轉場：** [淡入 / 切換 / 縮放]
**音效：** [描述]

---

## 場景 2｜[00:10 - 00:30]
[同上格式]

---

[繼續直到影片結束]

---

## 🎵 全片配樂建議
背景音樂：[情緒 + 風格描述]
音效庫推薦：Pixabay / Freesound / Epidemic Sound

## ⚙️ 製作工具推薦
AI 影片生成：Kling AI / Runway Gen-3 / Sora
配音：ElevenLabs / FishAudio
剪輯：剪映 / CapCut
字幕：Whisper / 剪映自動字幕""", 4000)
