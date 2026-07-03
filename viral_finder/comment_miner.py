"""
留言挖掘 → 內容點子
把觀眾留言丟給 Claude，提煉出：觀眾真正想看什麼、痛點、疑問、可做的新影片點子。
"""
import os
import anthropic
from security import SYSTEM_GUARD

_MAX_COMMENTS_TO_AI = 120   # 送進 AI 的留言上限
_MAX_CHARS_PER_COMMENT = 300


def _claude(prompt: str, max_tokens: int = 3000) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("請先在左側欄輸入 Anthropic API Key")
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=SYSTEM_GUARD,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _format_comments(comments: list[dict]) -> str:
    """把留言整理成帶讚數的文字，讚數高的排前面（已在抓取時排序）"""
    lines = []
    for c in comments[:_MAX_COMMENTS_TO_AI]:
        text = c["text"][:_MAX_CHARS_PER_COMMENT].replace("\n", " ")
        likes = c.get("like_count", 0)
        lines.append(f"[👍{likes}] {text}")
    return "\n".join(lines)


def mine_comments(
    comments: list[dict],
    video_title: str = "",
    output_lang: str = "繁體中文",
) -> dict:
    """
    分析留言，回傳結構化 dict：
      raw            完整 markdown
      pain_points    觀眾痛點
      questions      觀眾疑問（可做成 FAQ / 影片）
      ideas          新影片點子
      sentiment      整體風向
    """
    if not comments:
        raise ValueError("沒有留言可供分析")

    formatted = _format_comments(comments)
    total = len(comments)

    prompt = f"""You are an audience research analyst for content creators.
Below are the TOP viewer comments (sorted by likes) from a video titled "{video_title or '（未提供標題）'}".
Total comments analyzed: {total}.

Analyze what the audience REALLY wants, and output EVERYTHING in {output_lang}.

COMMENTS:
{formatted}

Produce your analysis in this EXACT markdown structure:

## 🎯 觀眾風向總結
2-3 sentences: overall sentiment, what resonated most, what the audience feels.

## 😣 觀眾痛點 TOP 5
The pain points / frustrations viewers mention. For each:
- **痛點**：___
- 💬 佐證留言：quote a representative comment
- 🎬 可做影片：a video idea that solves this pain

## ❓ 觀眾最想問的問題 TOP 5
Questions viewers are actually asking (explicit or implied). Each can become an FAQ or a video:
1. 問題 → 可做成的影片標題

## 💡 高潛力新影片點子 TOP 8
Concrete NEXT video ideas derived from the comments. For each:
- 【點子】具體影片標題
- 🔥 需求證據：why the comments show demand for this
- 📊 預估潛力：★ to ★★★★★

## 🗣 觀眾常用的關鍵字/說法
Words and phrases the audience uses — useful for titles, hooks, and SEO.

## 🚀 一句話行動建議
The single most valuable next video to make, and why.

Be specific and evidence-based — every idea must trace back to actual comments. Do NOT invent demand that isn't in the comments."""

    raw = _claude(prompt, 3500)
    return {
        "raw": raw,
        "pain_points": _section(raw, "😣 觀眾痛點"),
        "questions": _section(raw, "❓ 觀眾最想問"),
        "ideas": _section(raw, "💡 高潛力新影片點子"),
        "sentiment": _section(raw, "🎯 觀眾風向總結"),
    }


def _section(text: str, header_keyword: str) -> str:
    """從 markdown 中抽出某個 ## 區塊的內容"""
    lines = text.splitlines()
    out, capturing = [], False
    for line in lines:
        if line.startswith("## "):
            if capturing:
                break
            capturing = header_keyword in line
            continue
        if capturing:
            out.append(line)
    return "\n".join(out).strip()
