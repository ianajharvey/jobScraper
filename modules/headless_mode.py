# utils/browser.py
import os

def get_headless_mode() -> bool:

    return os.getenv("JOBSCRAPER_HEADLESS", "true").lower() == "true"
