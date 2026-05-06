import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.tasker.com.tw"
PAGES = ["/cases", "/cases?page=2"]


def scrape():
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9",
    }
    seen = set()

    for path in PAGES:
        try:
            url = BASE_URL + path
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.select("a.li-case")
            for card in cards:
                href = card.get("href", "")
                link = BASE_URL + href if href.startswith("/") else href
                if link in seen or not href:
                    continue
                seen.add(link)

                title_elem = card.select_one("h2 span, h2, .li-title")
                title = title_elem.get_text(strip=True) if title_elem else "未知案件"

                budget_elem = card.select_one(".text-primary-500, .text-primary-400")
                budget = budget_elem.get_text(strip=True) if budget_elem else ""

                desc_elem = card.select_one(".case-content")
                desc = desc_elem.get_text(strip=True)[:100] if desc_elem else ""

                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": "出任務 Tasker",
                    "date": "",
                    "description": f"{budget} | {desc}" if budget else desc,
                })
        except Exception as e:
            print(f"[Tasker/{path}] 爬取失敗: {e}")

    return jobs
