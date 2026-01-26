from playwright.sync_api import sync_playwright

BASE_URL = "https://careers.chewy.com"
SEARCH_URL = BASE_URL + "/us/en/search-results"

def scrape_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        offset = 0

        while True:
            url = f"{SEARCH_URL}?from={offset}&s=1"
            print(f"Scraping Chewy: {url}")

            page.goto(url, timeout=10000)

            # ✅ Wait for job cards, NOT network idle
            try:
                page.wait_for_selector(
                    'a[data-ph-at-id="job-link"]',
                    timeout=60000
                )
            except:
                print("No jobs found — stopping pagination")
                break

            job_cards = page.locator('a[data-ph-at-id="job-link"]')
            count = job_cards.count()
            print(f"Found {count} jobs")

            if count == 0:
                break

            for i in range(count):
                card = job_cards.nth(i)

                jobs.append({
                    "id": card.get_attribute("data-ph-at-job-id-text"),
                    "title": card.get_attribute("data-ph-at-job-title-text"),
                    "location": card.get_attribute("data-ph-at-job-location-text"),
                    "link": card.get_attribute("href"),
                    "date_posted": card.get_attribute("data-ph-at-job-post-date-text"),
                    "company": "Chewy"
                })

            offset += 10  # next page

        browser.close()

    return jobs
