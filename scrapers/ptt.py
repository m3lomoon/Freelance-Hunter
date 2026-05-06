import requests
from bs4 import BeautifulSoup

PTT_BOARDS = ["SOHO", "part-time", "Film-Produce"]
BASE_URL = "https://www.ptt.cc"


def scrape():
    jobs = []
    session = requests.Session()
    session.cookies.set("over18", "1")
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

    for board in PTT_BOARDS:
        try:
            url = f"{BASE_URL}/bbs/{board}/index.html"
            resp = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            for post in soup.select(".r-ent"):
                title_elem = post.select_one(".title a")
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                # 過濾掉刪除和公告
                if "[公告]" in title or "[版規]" in title:
                    continue
                link = BASE_URL + title_elem["href"]
                date_elem = post.select_one(".date")
                date = date_elem.text.strip() if date_elem else ""
                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": f"PTT/{board}",
                    "date": date,
                    "description": "",
                })
        except Exception as e:
            print(f"[PTT/{board}] 爬取失敗: {e}")

    return jobs
