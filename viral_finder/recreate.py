import os
import anthropic
from security import SYSTEM_GUARD


def generate_recreation_guide(
    title: str,
    transcript: str,
    description: str,
    view_count: int,
    platform: str,
    thumbnail_url: str = "",
    user_tools: str = "",
) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("請先在左側欄輸入 Anthropic API Key")

    client = anthropic.Anthropic(api_key=api_key)

    tools_line = f"Creator's available tools/gear: {user_tools}" if user_tools else ""
    transcript_excerpt = transcript[:3000] if transcript else "（無逐字稿）"
    desc_excerpt = description[:800] if description else "（無描述）"

    prompt = f"""You are a professional video production analyst and director. Analyze this viral video and produce a complete step-by-step recreation guide in Traditional Chinese (繁體中文).

VIDEO DATA:
- Title: {title}
- Platform: {platform}
- Views: {view_count:,}
- Description: {desc_excerpt}
{tools_line}

TRANSCRIPT:
{transcript_excerpt}

---

Produce ALL sections below in Traditional Chinese. Be extremely specific and practical — a beginner should be able to follow this guide.

## 📱 拍攝設置
Describe the exact filming setup based on visual cues in the title/description/transcript:
- 鏡頭類型（手機/相機/空拍機）
- 拍攝角度（正面/側面/俯拍/仰拍）
- 鏡頭移動（固定/跟拍/推近/拉遠）
- 畫面比例（9:16 直式 / 16:9 橫式）

## 💡 燈光與場景
- 燈光來源（自然光/環形燈/柔光箱）
- 背景設置
- 道具與場景佈置

## 📝 腳本結構重現
Break down the video into exact segments with estimated timing. For each segment:
- 時間點
- 說了什麼（或字幕文字）
- 視覺呈現

## ✂️ 剪輯步驟
- 剪輯節奏（快切/慢切）
- 特效與濾鏡
- 字幕樣式
- 轉場方式

## 🎵 音樂與音效
- 音樂類型與節奏
- 音效使用時機
- 建議曲風關鍵字（用於尋找版權音樂）

## 📦 所需器材清單
List everything needed (budget-friendly alternatives included)

## 🤖 AI 影片生成 Prompt
Generate 2 ready-to-use prompts in English for AI video tools (Sora, Kling, Runway Gen-3):
**Prompt 1 (Kling/Runway):** [detailed cinematic prompt]
**Prompt 2 (Sora style):** [detailed scene description prompt]

## 🪜 完整重現步驟（10步）
A numbered step-by-step production checklist from pre-production to publish."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3500,
        system=SYSTEM_GUARD,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text

    sections = {
        "filming_setup": _extract(raw, "拍攝設置"),
        "lighting_scene": _extract(raw, "燈光與場景"),
        "script_breakdown": _extract(raw, "腳本結構重現"),
        "editing": _extract(raw, "剪輯步驟"),
        "music": _extract(raw, "音樂與音效"),
        "equipment": _extract(raw, "所需器材"),
        "ai_prompts": _extract(raw, "AI 影片生成"),
        "steps": _extract(raw, "完整重現步驟"),
        "raw": raw,
    }
    return sections


def _extract(text: str, keyword: str) -> str:
    lines = text.split("\n")
    result, inside = [], False
    for line in lines:
        if keyword in line and line.startswith("#"):
            inside = True
            continue
        if inside:
            if line.startswith("## ") and keyword not in line:
                break
            result.append(line)
    return "\n".join(result).strip()
