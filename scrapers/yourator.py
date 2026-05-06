"""
Yourator — 台灣遠端工作最豐富的平台
搜尋全遠端、符合技能的兼職工作
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.yourator.co"
SEARCH_TERMS = ["影片", "剪輯", "翻譯", "音樂", "字幕", "內容", "社群"]


def scrape():
    jobs = []
    seen = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9",
    }

    for keyword in SEARCH_TERMS:
        try:
            # Yourator 搜尋 + 遠端篩選
            params = {
                "term": keyword,
                "work_type[]": "remote",   # 全遠端
            }
            resp = requests.get(
                f"{BASE_URL}/jobs",
                headers=headers,
                params=params,
                timeout=15,
            )
            soup = BeautifulSoup(resp.text, "html.parser")

            # Yourator 職缺卡片
            cards = soup.select("a.job-list-item, a[href*='/companies/'][href*='/jobs/'], .JobCard a")
            if not cards:
                cards = soup.select("article a, .job-item a, a[class*='job']")

            for card in cards:
                href = card.get("href", "")
                link = href if href.startswith("http") else BASE_URL + href
                if link in seen or not href or href in ("/", BASE_URL):
                    continue
                seen.add(link)

                title_elem = card.select_one("h2, h3, .title, [class*='title'], [class*='name']")
                title = title_elem.get_text(strip=True) if title_elem else card.get_text(strip=True)[:50]
                if len(title) < 3:
                    continue

                salary_elem = card.select_one(".salary, [class*='salary'], [class*='pay']")
                salary = salary_elem.get_text(strip=True) if salary_elem else ""

                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": "Yourator遠端",
                    "date": "",
                    "description": f"薪資: {salary}" if salary else "遠端工作",
                    "job_type": "遠端兼職 💼",
                })
        except Exception as e:
            print(f"[Yourator/{keyword}] 爬取失敗: {e}")

    return jobs
