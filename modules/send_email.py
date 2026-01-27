from pathlib import Path
import smtplib
import time
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


BASE_DIR = Path(__file__).resolve().parents[1]   # jobScraper/
DATA_DIR = BASE_DIR / "data"

ALL_JOBS_FILE = DATA_DIR / "all_filtered_jobs.csv"
SEEN_JOBS_FILE = DATA_DIR / "seen_jobs.csv"


def send_email():
    SMTP_HOST = os.getenv("JOBSCRAPER_SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("JOBSCRAPER_SMTP_PORT", 465))

    EMAIL_USERNAME = os.getenv("JOBSCRAPER_EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("JOBSCRAPER_EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.getenv("JOBSCRAPER_EMAIL_RECEIVER", EMAIL_USERNAME)

    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise ValueError("Missing email environment variables")

    if not ALL_JOBS_FILE.exists():
        print("No job file found — skipping email.")
        return

    now = time.localtime()
    email_date = time.strftime("%A, %b %d %Y", now)

    jobs_df = pd.read_csv(ALL_JOBS_FILE)

    if SEEN_JOBS_FILE.exists():
        seen_df = pd.read_csv(SEEN_JOBS_FILE)
    else:
        seen_df = pd.DataFrame(columns=jobs_df.columns)

    new_jobs_df = jobs_df[~jobs_df["key"].isin(seen_df["key"])]

    if new_jobs_df.empty:
        print("No new jobs to email.")
        return

    html_table = new_jobs_df.to_html(index=False, escape=False)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{email_date} New Job Listings ({len(new_jobs_df)})"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = EMAIL_RECEIVER

    msg.attach(MIMEText(f"""
    <html>
      <body>
        <h2>New Job Listings</h2>
        {html_table}
      </body>
    </html>
    """, "html"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, EMAIL_RECEIVER, msg.as_string())

    updated_seen = pd.concat([seen_df, new_jobs_df], ignore_index=True)
    updated_seen.to_csv(SEEN_JOBS_FILE, index=False)

    print(f"Emailed {len(new_jobs_df)} new jobs!")
