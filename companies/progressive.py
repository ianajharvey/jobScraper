from playwright.sync_api import sync_playwright
from modules.headless_mode import get_headless_mode

BASE_URL = "https://careers.progressive.com/search/jobs"

# NOTE:
# Progressive triggers human verification on pagination.
# We intentionally scrape ONLY page 1 to avoid bot detection.
# Since page 1 contains newest jobs and we run daily, this is sufficient.


def scrape_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=get_headless_mode())
        page = browser.new_page()

        page_num = 1


        url = f"{BASE_URL}/in/?page={page_num}"
        print(f"Scraping Progressive: page {page_num}")

        page.goto(url, timeout=20000)


        job_cards = page.locator("li.jobs-section__item")
        count = job_cards.count()


        for i in range(count):
            card = job_cards.nth(i)

            title_el = card.locator("h3.heading-4 a")
            title = title_el.inner_text().strip()
            link = title_el.get_attribute("href")

            location = card.locator("div.columns.xlarge-4").inner_text().strip()

            posted_time = card.locator("time")
            posted_date = posted_time.get_attribute("datetime")

            # Progressive job ID lives in the URL
            job_id = link.rstrip("/").split("/")[-1]

            jobs.append({
                "id": job_id,
                "title": title,
                "link": link,
                "company": "Progressive",
                "location": location,
                "posted_date": posted_date,
                "key": f"{job_id}||{link}||Progressive"
            })

        browser.close()

    return jobs

