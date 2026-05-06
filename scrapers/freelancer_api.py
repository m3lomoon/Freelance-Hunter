import requests
from config import FREELANCER_API_KEY

BASE_URL = "https://www.freelancer.com/api"

# 對應技能 ID（Freelancer.com 官方技能分類）
SKILL_IDS = {
    "video_production": 3,
    "video_editing": 156,
    "translation": 18,
    "music_production": 61,
    "audio_production": 180,
    "animation": 23,
}


def scrape():
    if not FREELANCER_API_KEY:
        print("[Freelancer] 未設定 API key，跳過")
        return []

    jobs = []
    headers = {
        "freelancer-oauth-v1": FREELANCER_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        params = {
            "limit": 50,
            "offset": 0,
            "job_details": True,
            "full_description": False,
            "jobs[]": list(SKILL_IDS.values()),
            "sort_field": "time_updated",
            "reverse_sort": True,
        }
        resp = requests.get(
            f"{BASE_URL}/projects/0.1/projects/active/",
            headers=headers,
            params=params,
            timeout=15,
        )
        data = resp.json()

        projects = data.get("result", {}).get("projects", [])
        for p in projects:
            pid = p.get("id", "")
            title = p.get("title", "")
            desc = p.get("preview_description", "")[:200]
            budget = p.get("budget", {})
            min_b = budget.get("minimum", 0)
            max_b = budget.get("maximum", 0)
            currency = p.get("currency", {}).get("sign", "$")
            seo_url = p.get("seo_url", "")
            link = f"https://www.freelancer.com/projects/{seo_url}" if seo_url else f"https://www.freelancer.com/projects/{pid}"

            jobs.append({
                "title": title,
                "link": link,
                "platform": "Freelancer.com",
                "date": "",
                "description": f"預算: {currency}{min_b}-{currency}{max_b} | {desc}",
            })
    except Exception as e:
        print(f"[Freelancer API] 爬取失敗: {e}")

    return jobs


def scrape_without_api():
    """不使用 API，直接搜尋頁面（備用方案）"""
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    search_terms = ["video editing", "translation Chinese", "music production", "AI video"]

    from bs4 import BeautifulSoup
    seen = set()

    for term in search_terms:
        try:
            url = f"https://www.freelancer.com/jobs/{requests.utils.quote(term.replace(' ', '-'))}/"
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            for item in soup.select(".JobSearchCard-item"):
                link_elem = item.select_one("a.JobSearchCard-primary-heading-link")
                if not link_elem:
                    continue
                href = link_elem.get("href", "")
                link = "https://www.freelancer.com" + href if href.startswith("/") else href
                if link in seen:
                    continue
                seen.add(link)

                title = link_elem.text.strip()
                desc_elem = item.select_one(".JobSearchCard-primary-description")
                desc = desc_elem.text.strip()[:200] if desc_elem else ""

                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": "Freelancer.com",
                    "date": "",
                    "description": desc,
                })
        except Exception as e:
            print(f"[Freelancer/{term}] 爬取失敗: {e}")

    return jobs
