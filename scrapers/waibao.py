import requests
from bs4 import BeautifulSoup

# 外包達人 (freelancerclub.net / waibao.cc)
PLATFORMS = [
    ("外包達人", "https://www.freelancerclub.net/cases", "a[href*='/case/']"),
    ("外包網", "https://www.waibao.cc/cases", "a[href*='/case/']"),
]
SEARCH_TERMS = ["影片", "翻譯", "音樂", "剪輯"]


def _scrape_site(name, base_url, link_selector):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    seen = set()

    for keyword in SEARCH_TERMS:
        try:
            url = f"{base_url}?keyword={requests.utils.quote(keyword)}"
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select(link_selector)

            for link_elem in links:
                href = link_elem.get("href", "")
                link = href if href.startswith("http") else base_url.rsplit("/", 1)[0] + href
                if link in seen or not href:
                    continue
                seen.add(link)

                title = link_elem.get_text(strip=True)
                if len(title) < 3:
                    continue

                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": name,
                    "date": "",
                    "description": "",
                })
        except Exception as e:
            print(f"[{name}/{keyword}] 爬取失敗: {e}")

    return jobs


def scrape():
    jobs = []
    for name, url, selector in PLATFORMS:
        jobs.extend(_scrape_site(name, url, selector))
    return jobs
