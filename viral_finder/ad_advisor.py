"""
AI 廣告投放顧問 (Ad Strategy Advisor)
針對一支影片 / 內容，產出可直接執行的付費廣告投放策略：
平台選擇、預算分配、受眾鎖定、廣告文案、出價策略、預期成效與優化建議。
主打「拿了就能開廣告帳戶投放」的實戰等級。
"""
import os
import anthropic
from security import SYSTEM_GUARD

_MAX_INPUT = 2500


def _sanitize(text: str, max_len: int = _MAX_INPUT) -> str:
    return (text or "")[:max_len].strip()


def _claude(prompt: str, max_tokens: int = 3500) -> str:
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


# 目標對應的行銷語言
_GOALS = {
    "品牌曝光": "brand awareness / reach — maximize impressions and video views cheaply",
    "衝流量追蹤數": "traffic & followers — drive profile visits and new followers",
    "名單/導客": "lead generation — collect emails / LINE adds / sign-ups",
    "銷售轉換": "conversions / sales — drive purchases with measurable ROAS",
    "接案詢問": "inbound inquiries — get DMs / form fills for freelance or B2B service",
}

# 幣別 → 建議日預算區間提示
_CURRENCIES = {
    "TWD (NT$)": "New Taiwan Dollars. Use realistic Taiwan CPM/CPC benchmarks.",
    "USD ($)": "US Dollars. Use US market benchmarks.",
    "CNY (¥)": "Chinese Yuan. Use China / 小紅書 / 抖音 benchmarks.",
}


def generate_ad_strategy(
    title: str,
    transcript: str = "",
    description: str = "",
    platform: str = "YouTube",
    goal: str = "銷售轉換",
    monthly_budget: str = "10000",
    currency: str = "TWD (NT$)",
    product: str = "",
    target_market: str = "台灣",
    output_lang: str = "繁體中文",
) -> dict:
    """
    產出完整廣告投放策略，回傳結構化 dict（每個 key 對應一個 UI 分頁）。
    """
    # 試玩模式：回傳範例策略（不需 API Key）
    from demo import is_demo, DEMO_AD_STRATEGY
    if is_demo() and not os.environ.get("ANTHROPIC_API_KEY"):
        return dict(DEMO_AD_STRATEGY)

    title = _sanitize(title, 300)
    transcript = _sanitize(transcript, 1500)
    description = _sanitize(description, 500)
    product = _sanitize(product, 300)

    goal_desc = _GOALS.get(goal, goal)
    cur_desc = _CURRENCIES.get(currency, currency)

    prompt = f"""You are a senior paid-media strategist who has managed 8-figure ad budgets across Meta, TikTok, YouTube/Google, and 小紅書. Produce a COMPLETE, ready-to-execute paid advertising plan based on this organic video.

VIDEO / CONTENT:
- Title: {title}
- Platform it came from: {platform}
- Description: {description or "（無）"}
- Transcript excerpt: {transcript or "（無逐字稿）"}

CAMPAIGN BRIEF:
- Product / offer being promoted: {product or "（同影片主題，未特別指定產品）"}
- Primary goal: {goal} ({goal_desc})
- Target market / region: {target_market}
- Monthly budget: {monthly_budget} {currency} ({cur_desc})

Write EVERYTHING in {output_lang}. Be specific and numeric — real percentages, real {currency} amounts, real audience sizes. No vague advice. Use this EXACT markdown structure with these EXACT section headers:

## 📊 策略總覽
3-4 sentences: is this content ad-worthy? What's the single biggest opportunity and the main risk. State the recommended primary platform and why.

## 🎯 平台分配建議
A markdown table recommending how to split the {monthly_budget} {currency}/month budget across platforms:
| 平台 | 預算佔比 | 月預算 | 為什麼 | 適合的目標 |
Base the split on where THIS content and goal perform best. Include at least the top 2-3 platforms.

## 👥 受眾鎖定 (Audience Targeting)
For the PRIMARY platform, give 3 concrete audience sets ready to build in Ads Manager:
For each:
- **受眾名稱**
- 年齡 / 性別 / 地區
- 興趣 / 行為 / 關鍵字 (be specific — real interest names)
- 預估受眾規模
- 🎯 為什麼這群人會買

Include one 再行銷 (retargeting) audience and one 相似受眾 (lookalike) recommendation.

## ✍️ 廣告文案 (Ad Copy) ×3
3 distinct ad copy variations ready to paste. For each:
- 【主標 Primary Text】
- 【標題 Headline】(short)
- 【CTA 按鈕】
- 🧠 心理角度: which angle (痛點/好奇/社會認同/急迫/利益)

## 🎬 廣告素材建議 (Creative)
- How to cut this video into ad creative (hook in first 3s, length, aspect ratio per platform)
- 2-3 alternative creative angles to A/B test
- Thumbnail / first-frame guidance

## 💰 出價與預算策略
- Recommended bidding strategy & campaign objective per platform (real names: e.g. Meta 'Sales / Advantage+', TikTok 'Conversions')
- Suggested daily budget to start, and when/how to scale
- Testing budget vs scaling budget split (e.g. 20% test / 80% scale)

## 📈 預期成效與 KPI
A table of realistic benchmarks for {target_market} in {currency}:
| 指標 | 保守估計 | 目標值 | 說明 |
Include CPM, CPC, CTR, and a goal-specific metric (CPA/ROAS/每粉絲成本 depending on the goal).

## 🚦 30天投放路線圖
Week-by-week plan: Week 1 test, Week 2 read data, Week 3 kill losers & scale winners, Week 4 optimize. Concrete actions each week.

## ⚠️ 常見錯誤與避雷
4-5 specific mistakes people make advertising this type of content, and how to avoid each.

## ✅ 立即行動清單
A checklist of 5-7 concrete next steps to launch within 48 hours.

Ground every number in real ad-platform benchmarks. If budget is small, be honest about what's realistic and prioritize ruthlessly."""

    raw = _claude(prompt, 4000)
    return {
        "raw": raw,
        "overview": _section(raw, "📊 策略總覽"),
        "platform_split": _section(raw, "🎯 平台分配"),
        "targeting": _section(raw, "👥 受眾鎖定"),
        "ad_copy": _section(raw, "✍️ 廣告文案"),
        "creative": _section(raw, "🎬 廣告素材"),
        "bidding": _section(raw, "💰 出價與預算"),
        "kpi": _section(raw, "📈 預期成效"),
        "roadmap": _section(raw, "🚦 30天投放路線圖"),
        "mistakes": _section(raw, "⚠️ 常見錯誤"),
        "checklist": _section(raw, "✅ 立即行動清單"),
    }


def _section(text: str, header_keyword: str) -> str:
    """從 markdown 抽出某個 ## 區塊內容"""
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


GOAL_OPTIONS = list(_GOALS.keys())
CURRENCY_OPTIONS = list(_CURRENCIES.keys())
