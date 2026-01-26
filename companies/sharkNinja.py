from playwright.sync_api import sync_playwright
import html

def scrape_jobs():
    BASE_URL = "https://careers.sharkninja.com"
    RESULTS_ENDPOINT = BASE_URL + "/search-jobs/results"

    jobs = []
    page_num = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while True:
            params = {
                "ActiveFacetID": 0,
                "CurrentPage": page_num,
                "RecordsPerPage": 15,
                "TotalContentResults": "",
                "Distance": 50,
                "RadiusUnitType": 0,
                "Keywords": "",
                "Location": "",
                "ShowRadius": False,
                "IsPagination": False,
                "CustomFacetName": "",
                "FacetTerm": "",
                "FacetType": 0,
                "SearchResultsModuleName": "Search Results",
                "SearchFiltersModuleName": "Search Filters",
                "SortCriteria": 1,
                "SortDirection": 1,
                "SearchType": 5,
                "PostalCode": "",
                "ResultsType": 0,
                "fc": "",
                "fl": "",
                "fcf": "",
                "afc": "",
                "afl": "",
                "afcf": "",
                "TotalContentPages": "NaN",
            }

            response = page.request.get(RESULTS_ENDPOINT, params=params)
            data = response.json()

            if not data.get("hasJobs"):
                break

            html_fragment = html.unescape(data.get("results", ""))
            if not html_fragment.strip():
                break

            page.set_content(html_fragment)
            job_cards = page.locator(
                "a.brand-facet.brand-facet__shark-ninja, a.brand-facet.brand-facet__ninja"
            )
            count = job_cards.count()

            for i in range(count):
                card = job_cards.nth(i)
                jobs.append({
                    "title": card.locator("h2").inner_text(),
                    "link": BASE_URL + card.get_attribute("href"),
                    "location": card.locator(".job-location").inner_text(),
                    "categories": card.locator(".job-categories").inner_text(),
                    "date_posted": card.locator(".job-date-posted").inner_text(),
                    "company": "SharkNinja"
                })

            page_num += 1

        browser.close()

    return jobs
