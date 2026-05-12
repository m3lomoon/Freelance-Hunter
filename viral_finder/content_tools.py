import os
import anthropic


def _claude(prompt: str, max_tokens: int = 2000) -> str:
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


# ── A/B 標題測試 ────────────────────────────────────────────────────────────

def generate_ab_titles(topic: str, platform: str = "YouTube", count: int = 5) -> str:
    return _claude(f"""Generate {count} completely different title variations in Traditional Chinese (繁體中文) for this video topic:

Topic: {topic}
Platform: {platform}

Each title must use a DIFFERENT psychological angle:
1. 好奇心缺口（Curiosity gap）
2. 數字衝擊（Specific numbers）
3. 痛點直擊（Pain point）
4. 反直覺（Counter-intuitive）
5. 身份認同（Identity/Aspiration）

Format each as:
【角度名稱】標題文字
✅ 為什麼有效：一句話解釋

Keep titles under 30 characters for short-form, 50 for long-form.""", 1500)


# ── 縮圖文案生成器 ──────────────────────────────────────────────────────────

def generate_thumbnail_copy(topic: str, style: str = "震驚") -> str:
    styles = {
        "震驚": "shocking, bold, creates disbelief",
        "好奇": "teases information, creates curiosity gap",
        "情緒": "emotional, relatable, personal",
        "數字": "specific numbers, measurable results",
        "對比": "before/after, vs, comparison",
    }
    style_desc = styles.get(style, style)
    return _claude(f"""Generate thumbnail text copy in Traditional Chinese for:

Topic: {topic}
Style: {style} ({style_desc})

Thumbnails need MAXIMUM 5-8 characters per text element (Chinese characters).
Generate 5 thumbnail text combinations, each with:
- 主標題（3-6字）: The big bold text
- 副標題（4-8字）: Supporting text (optional)
- 數字/強調詞: A number or power word if applicable

Format:
【方案1】
主標題：___
副標題：___
強調：___
效果說明：一句話

Use ALL CAPS feel, power words, and emotional triggers.""", 1200)


# ── 30天內容日曆 ───────────────────────────────────────────────────────────

def generate_content_calendar(niche: str, platform: str = "YouTube", days: int = 30) -> str:
    return _claude(f"""Create a {days}-day viral content calendar in Traditional Chinese (繁體中文) for:

Niche/Topic: {niche}
Platform: {platform}

Structure the calendar with:
- Week 1-4 themes (overall strategy per week)
- Daily video ideas with titles
- Mix of content types: 教學/娛樂/故事/爭議/趨勢借勢
- Mark "爆款潛力" (★★★) for highest-potential videos
- Include 2-3 "系列影片" that connect across multiple days

Format as a clean table:
| 日期 | 類型 | 標題 | 潛力 |
|------|------|------|------|

After the table, add:
## 本月策略說明
## 3個必做系列

Be specific with actual video ideas, not generic placeholders.""", 3000)


# ── 平台適配器 ─────────────────────────────────────────────────────────────

def adapt_for_platforms(content: str, original_platform: str = "YouTube") -> str:
    return _claude(f"""Adapt this video concept/script for multiple platforms in Traditional Chinese (繁體中文):

Original content ({original_platform}):
{content[:2000]}

Create platform-specific versions for each:

## 📱 TikTok 版本（15-60秒）
- 開場鉤子（前3秒）
- 核心內容精簡版
- 結尾CTA
- 建議音樂類型
- 適合的hashtag（5個）

## 📸 Instagram Reels 版本（15-90秒）
- 美學重點
- 字幕風格建議
- 開場鉤子
- 結尾互動設計

## ▶️ YouTube Shorts 版本（<60秒）
- 標題優化
- 開場前3秒
- 縮圖文案建議

## ▶️ YouTube 長影片版本（8-15分鐘）
- 完整標題
- 開場Hook（前30秒腳本）
- 影片章節結構
- 結尾訂閱CTA""", 2500)


# ── 最佳發布時間分析 ───────────────────────────────────────────────────────

def analyze_best_posting_time(niche: str, target_audience: str, platform: str = "YouTube") -> str:
    return _claude(f"""Analyze and recommend the best posting times in Traditional Chinese (繁體中文) for:

Niche: {niche}
Target audience: {target_audience}
Platform: {platform}

Provide:

## ⏰ 最佳發布時間（台灣/東八區）
List top 3 time slots with reasoning based on audience behavior patterns.
Format: 星期X 晚上X點 — 原因

## 📅 每週發布頻率建議
How many times per week, which days, and why.

## 🌍 如果受眾在美國/歐洲
Adjusted times for Western audiences.

## ⚡ 快速測試方法
A simple A/B testing schedule to find YOUR personal best time in 4 weeks.

## ❌ 避免的時段
Times to avoid and why.

Base recommendations on platform algorithm behavior, audience psychology, and competition patterns.""", 1500)


# ── 競爭對手分析 ───────────────────────────────────────────────────────────

def analyze_competitor(channel_url: str, your_niche: str) -> str:
    return _claude(f"""Act as a competitive intelligence analyst. Analyze this competitor channel for content strategy gaps:

Competitor channel: {channel_url}
My niche: {your_niche}

Provide a strategic competitive analysis in Traditional Chinese (繁體中文):

## 🔍 頻道策略推斷
Based on the channel URL/name, infer their likely content strategy.

## 💡 內容缺口機會
5 specific video topics they're likely NOT covering that you could own.

## 🪝 他們常用的鉤子類型
Infer 3 hook patterns they likely use based on their niche.

## 📈 如何差異化
3 specific ways to position yourself differently.

## 🎯 可以借勢的方向
How to ride on their audience's interests without copying.

Note: Since I cannot access the actual channel, base this on the niche and channel name analysis.""", 1500)
