from playwright.sync_api import sync_playwright

BASE_URL = "https://www.104.com.tw"
SEARCH_TERMS = ["翻譯", "影片剪輯", "AI影片", "音樂製作", "MV製作", "字幕"]


def scrape():
    jobs = []
    seen = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )

            for keyword in SEARCH_TERMS:
                for job_type in ["4", "5"]:
                    job_list = []

                    def on_resp(resp):
                        if "/jobs/search/api/jobs" in resp.url:
                            try:
                                d = resp.json()
                                job_list.extend(d.get("data", []))
                            except:
                                pass

                    page.on("response", on_resp)
                    url = f"{BASE_URL}/jobs/search/?keyword={keyword}&jobType={job_type}&order=15"
                    page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    page.wait_for_timeout(3000)
                    page.remove_listener("response", on_resp)

                    for j in job_list:
                        job_link = j.get("link", {}).get("job", "")
                        if not job_link or job_link in seen:
                            continue
                        seen.add(job_link)

                        title = j.get("jobName", "")
                        company = j.get("custName", "")
                        salary_low = j.get("salaryLow", 0)
                        salary_high = j.get("salaryHigh", 0)
                        salary = f"${salary_low}~${salary_high}" if salary_low else ""

                        jobs.append({
                            "title": title,
                            "link": job_link,
                            "platform": "104兼職/接案",
                            "date": j.get("appearDate", ""),
                            "description": f"{company} | {salary}".strip(" |"),
                        })

            browser.close()
    except Exception as e:
        print(f"[104] 錯誤: {e}")

    return jobs
