import os
import anthropic

PLATFORM_STYLES = {
    "TikTok": "short-form vertical video (15-60 seconds), fast cuts, trending audio",
    "YouTube Shorts": "short-form vertical video (under 60 seconds), punchy hooks",
    "YouTube": "long-form horizontal video (5-20 minutes), structured storytelling",
    "Instagram Reels": "short-form vertical video (15-90 seconds), aesthetic-focused",
    "Bilibili": "mid-to-long form video, anime/gaming/educational culture",
}


def analyze_and_generate_templates(
    title: str,
    transcript: str,
    view_count: int = 0,
    like_count: int = 0,
    channel: str = "",
    platform: str = "YouTube",
    user_niche: str = "",
) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("請先在左側欄輸入 Anthropic API Key")

    client = anthropic.Anthropic(api_key=api_key)
    platform_style = PLATFORM_STYLES.get(platform, "online video")

    niche_line = f"Creator's niche/topic: {user_niche}" if user_niche else ""

    transcript_excerpt = transcript[:3000] if transcript else "（無逐字稿）"

    prompt = f"""You are an expert viral content strategist. Analyze this viral video and produce a detailed creator toolkit in Traditional Chinese (繁體中文).

VIDEO DATA:
- Title: {title}
- Platform: {platform} ({platform_style})
- Views: {view_count:,}
- Likes: {like_count:,}
- Channel: {channel}
{niche_line}

TRANSCRIPT EXCERPT:
{transcript_excerpt}

---

Please output ALL of the following sections in Traditional Chinese. Be specific, practical, and actionable.

## 🔥 爆款原因分析
List 3-5 specific reasons why this video went viral. Reference actual elements from the title and transcript.

## 🪝 鉤子模板（5個變體）
Generate 5 powerful opening hooks (first 3-5 seconds) inspired by this video's style. Each hook should:
- Start with a pattern interrupt or bold statement
- Create curiosity or urgency
- Be under 20 words
Format: 【鉤子1】... 【鉤子2】... etc.

## 🎬 拍攝腳本模板
A reusable shooting template based on this video's structure. Include:
- **開場（0-5秒）**: Hook strategy
- **引入（5-15秒）**: Problem/context setup
- **主體內容**: Key sections with timing
- **高潮時刻**: The most engaging moment
- **結尾CTA**: Call to action

## 📐 節奏與剪輯建議
Specific editing rhythm tips based on this video (cut timing, pacing, transitions).

## 💡 可複製的標題公式
3 title formulas extracted from this video that can be reused for other topics. Show the formula + an example.

## 🎯 適合複製這個影片的主題
5 specific video topic ideas that could use this same template."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text

    sections = {
        "virality_reasons": _extract_section(raw, "爆款原因分析"),
        "hooks": _extract_section(raw, "鉤子模板"),
        "shooting_template": _extract_section(raw, "拍攝腳本模板"),
        "editing_tips": _extract_section(raw, "節奏與剪輯建議"),
        "title_formulas": _extract_section(raw, "標題公式"),
        "topic_ideas": _extract_section(raw, "適合複製"),
        "raw": raw,
    }
    return sections


def _extract_section(text: str, keyword: str) -> str:
    lines = text.split("\n")
    result = []
    inside = False

    for line in lines:
        if keyword in line and line.startswith("#"):
            inside = True
            continue
        if inside:
            if line.startswith("## ") and keyword not in line:
                break
            result.append(line)

    return "\n".join(result).strip()


def generate_custom_hook(topic: str, platform: str = "TikTok", style: str = "好奇心") -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("請先在左側欄輸入 Anthropic API Key")

    client = anthropic.Anthropic(api_key=api_key)

    styles = {
        "好奇心": "curiosity gap - make them need to know the answer",
        "震驚開場": "shocking statement or surprising fact",
        "痛點共鳴": "relatable pain point that the audience deeply feels",
        "反直覺": "counter-intuitive or controversial take",
        "數字衝擊": "specific numbers that are impressive or surprising",
    }
    style_desc = styles.get(style, style)

    prompt = f"""Generate 5 powerful video hooks in Traditional Chinese (繁體中文) for the following:

Topic: {topic}
Platform: {platform}
Hook style: {style} ({style_desc})

Rules:
- Each hook is the opening 3-5 seconds of a video
- Under 25 words each
- Must make the viewer STOP scrolling
- No generic phrases like "大家好" or "今天要介紹"

Output format:
【1】hook text
【2】hook text
【3】hook text
【4】hook text
【5】hook text"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
