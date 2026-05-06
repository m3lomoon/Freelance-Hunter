"""
518 人力銀行 - 兼職/接案搜尋
（替換原本的 Pro360，Pro360 是居家服務平台不適合數位接案）
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.518.com.tw"
SEARCH_TERMS = ["翻譯", "影片剪輯", "音樂", "AI影片", "MV"]


def scrape():
    jobs = []
    seen = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9",
    }

    for keyword in SEARCH_TERMS:
        try:
            params = {"q": keyword, "type": "part"}
            resp = requests.get(f"{BASE_URL}/jobs", headers=headers, params=params, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select(".job-item, .job-card, article, .job-list li")
            for card in cards:
                link_elem = card.select_one("a[href*='/job/'], a[href*='/work/']")
                if not link_elem:
                    link_elem = card.find("a")
                if not link_elem:
                    continue
                href = link_elem.get("href", "")
                link = href if href.startswith("http") else BASE_URL + href
                if link in seen or not href or href == "/":
                    continue
                seen.add(link)

                title_elem = card.select_one("h2, h3, .title, .job-title")
                title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)[:50]

                salary_elem = card.select_one(".salary, .pay, .wage")
                salary = salary_elem.get_text(strip=True) if salary_elem else ""

                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": "518人力銀行",
                    "date": "",
                    "description": f"薪資: {salary}" if salary else "",
                })
        except Exception as e:
            print(f"[518/{keyword}] 爬取失敗: {e}")

    return jobs
