from playwright.sync_api import sync_playwright
from modules.headless_mode import get_headless_mode

BASE_URL = "https://usnh.wd5.myworkdayjobs.com"

def scrape_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=get_headless_mode())
        page = browser.new_page()

        page.goto(f"{BASE_URL}/Careers", timeout=20000)

        while True:
            page.wait_for_selector('[data-automation-id="jobTitle"]', timeout=10000)

            job_cards = page.locator('[data-automation-id="jobTitle"]')
            count = job_cards.count()

            for i in range(count):
                job = job_cards.nth(i)

                title = job.inner_text().strip()
                link = job.get_attribute("href")
                full_link = BASE_URL + link

                # Job ID lives in subtitle
                card = job.locator("xpath=ancestor::li")
                job_id = card.locator('[data-automation-id="subtitle"] li').first.inner_text()

                location = card.locator('[data-automation-id="locations"] dd').inner_text()

                jobs.append({
                    "id": job_id,
                    "title": title,
                    "link": full_link,
                    "company": "USNH",
                    "location": location,
                    "key": f"{job_id}||{full_link}||USNH"
                })

            # Try next page
            next_button = page.locator('button[data-uxi-element-id="next"]')

            if next_button.count() == 0 or next_button.is_disabled():
                break

            next_button.click()
            page.wait_for_timeout(1500)

        browser.close()

    return jobs

