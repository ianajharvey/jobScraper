from playwright.sync_api import sync_playwright
from modules.headless_mode import get_headless_mode

def scrape_jobs():
    BASE_URL = "https://jobs.fidelity.com"
    START_URL = BASE_URL + "/en/jobs/"

    job_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=get_headless_mode())
        page = browser.new_page()
        page_num = 1

        while True:

            url = f"{START_URL}?page={page_num}#results"
            page.goto(url, timeout=10000)

            try:
                page.wait_for_selector("a.stretched-link.js-view-job", timeout=10000)
            except:
                break  # No jobs found on this page

            jobs_locator = page.locator("a.stretched-link.js-view-job")
            jobs_count = jobs_locator.count()

            if jobs_count == 0:
                break

            for i in range(jobs_count):
                job = jobs_locator.nth(i)
                title = job.inner_text().strip()
                link = job.get_attribute("href")
                job_id = link.split("/")[3]  # numeric ID
                full_link = BASE_URL + link

                if job_id not in [j["id"] for j in job_list]:
                    job_list.append({
                        "id": job_id,
                        "title": title,
                        "link": full_link,
                        "company": "Fidelity"
                    })

            page_num += 1

        browser.close()

    return job_list
