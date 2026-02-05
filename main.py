from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import importlib
import os
from modules.send_email import send_email

COMPANIES_FOLDER = "companies"

all_jobs = []

for file in os.listdir(COMPANIES_FOLDER):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]  # strip .py
        module_path = f"{COMPANIES_FOLDER}.{module_name}"

        module = importlib.import_module(module_path)

        if hasattr(module, "scrape_jobs"):
            print(f"Scraping jobs from {module_name}...")
            jobs = module.scrape_jobs()
            all_jobs.extend(jobs)
        else:
            print(f"Module {module_name} has no scrape_jobs() function, skipping.")

print(f"Total jobs collected: {len(all_jobs)}")

# Convert to DataFrame
df = pd.DataFrame(all_jobs)

# Optional: filter by keywords
keywords = ["analyst", "data", "intelligence", "business", "scientist"]
pattern = "|".join(keywords)
filtered_df = df[df['title'].str.contains(pattern, case=False, regex=True)].reset_index(drop=True)

filtered_df['key'] = filtered_df['title'] + '||' + filtered_df['link'] + '||' + filtered_df['company']

send_email(filtered_df)

print(filtered_df)
