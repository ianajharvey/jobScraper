from playwright.sync_api import sync_playwright
from modules.headless_mode import get_headless_mode

BASE_URL = "https://www.dickssportinggoods.jobs"

def scrape_jobs():
    jobs = []
    page_num = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=get_headless_mode())
        page = browser.new_page()

        while True:
            url = f"{BASE_URL}/calc-results/?filter[brand]=Corporate&mypage={page_num}"
            print(f"Scraping Dicks: page {page_num}")

            page.goto(url, timeout=10000)
            page.wait_for_load_state("domcontentloaded")

            job_items = page.locator("li.Results__list__item")
            count = job_items.count()

            # ✅ End pagination cleanly
            if count == 0:
                print("No more jobs found — stopping pagination.")
                break

            for i in range(count):
                item = job_items.nth(i)
                link_el = item.locator("a").first
                href = link_el.get_attribute("href")

                if not href:
                    continue

                parts = href.strip("/").split("/")
                if len(parts) < 4:
                    continue

                _, title_slug, location_slug, job_id = parts[:4]

                jobs.append({
                    "id": f"dicks_{job_id}",
                    "title": title_slug.replace("-", " ").title(),
                    "location": location_slug.replace("-", " "),
                    "link": BASE_URL + href,
                    "company": "Dicks Sporting Goods"
                })

            page_num += 1

        browser.close()

    return jobs
