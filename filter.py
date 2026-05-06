import anthropic
from config import ANTHROPIC_API_KEY, MY_PROFILE, REMOTE_JOB_PROFILE, REMOTE_JOB_MIN_SALARY


def filter_jobs(jobs: list) -> list:
    """用 Claude Haiku 過濾案件，同時標記「接案」與「遠端兼職」"""
    if not jobs:
        return []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    jobs_text = "\n".join([
        f"{i+1}. [{j['platform']}] {j['title']}"
        + (f" — {j['description'][:100]}" if j.get('description') else "")
        for i, j in enumerate(jobs)
    ])

    prompt = f"""你是接案與求職篩選助手。以下是今天各平台的機會列表。

【我的接案專長】
{MY_PROFILE}

【我的遠端兼職條件】
{REMOTE_JOB_PROFILE}
月薪門檻：NT${REMOTE_JOB_MIN_SALARY:,} 以上

機會列表：
{jobs_text}

請分兩類回傳，格式如下（只列編號，用逗號分隔）：
接案: 1,3,7
遠端兼職: 2,5,9

判斷標準：
- 接案：與我專長相關的案件（AI影片、MV、翻譯、音樂、剪輯等）
- 遠端兼職：全遠端工作機會，月薪達 NT${REMOTE_JOB_MIN_SALARY:,}，與我技能相關
- 若薪資明顯過低（低於 NT$25,000）或需到場，不列入遠端兼職
- 若不符合任何一類，該類留空

如果兩類都沒有，回傳：
接案: 無
遠端兼職: 無"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.content[0].text.strip()
        print(f"[AI 回應] {result}")

        freelance_jobs = []
        remote_jobs = []

        for line in result.splitlines():
            # 清除 markdown 粗體符號 ** 和多餘空白
            clean = line.strip().lstrip("*").rstrip("*").strip()
            if clean.startswith("接案:") or clean.startswith("接案："):
                indices = _parse_indices(clean.split(":", 1)[-1].split("：", 1)[-1], jobs)
                freelance_jobs = [jobs[i] for i in indices]
            elif clean.startswith("遠端兼職:") or clean.startswith("遠端兼職："):
                indices = _parse_indices(clean.split(":", 1)[-1].split("：", 1)[-1], jobs)
                remote_jobs = [jobs[i] for i in indices]

        # 標記類型
        for j in freelance_jobs:
            j["job_type"] = "接案"
        for j in remote_jobs:
            j["job_type"] = "遠端兼職 💼"

        # 合併，去除重複
        seen = set()
        combined = []
        for j in freelance_jobs + remote_jobs:
            if j["link"] not in seen:
                seen.add(j["link"])
                combined.append(j)

        print(f"[過濾] {len(jobs)} 筆 → 接案 {len(freelance_jobs)} 筆 / 遠端兼職 {len(remote_jobs)} 筆")
        return combined

    except Exception as e:
        print(f"[AI 過濾失敗] {e}，回傳全部")
        return jobs


def _parse_indices(text: str, jobs: list) -> list:
    indices = []
    for part in text.replace("，", ",").split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(jobs):
                indices.append(idx)
    return indices
