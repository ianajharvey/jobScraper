from pathlib import Path
import smtplib
import time
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


BASE_DIR = Path(__file__).resolve().parents[1]   # jobScraper/
DATA_DIR = BASE_DIR / "data"
SEEN_JOBS_FILE = DATA_DIR / "seen_jobs.csv"


def send_email(all_jobs_df: pd.DataFrame):
    # --- Email config ---
    SMTP_HOST = os.getenv("JOBSCRAPER_SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("JOBSCRAPER_SMTP_PORT", 465))

    EMAIL_USERNAME = os.getenv("JOBSCRAPER_EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("JOBSCRAPER_EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.getenv("JOBSCRAPER_EMAIL_RECEIVER", EMAIL_USERNAME)

    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise ValueError("Missing email environment variables")

    if all_jobs_df.empty:
        print("No jobs collected — skipping email.")
        return

    if "key" not in all_jobs_df.columns:
        raise ValueError("Expected 'key' column missing from all_jobs_df")

    # --- Date ---
    email_date = time.strftime("%A, %b %d %Y", time.localtime())

    # --- Load seen jobs ---
    if SEEN_JOBS_FILE.exists():
        seen_df = pd.read_csv(SEEN_JOBS_FILE)
    else:
        seen_df = pd.DataFrame(columns=all_jobs_df.columns)

    # --- Filter new jobs ---
    new_jobs_df = all_jobs_df[~all_jobs_df["key"].isin(seen_df["key"])]

    if new_jobs_df.empty:
        print("No new jobs to email.")
        return

    # --- Build email ---
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

    # --- Send ---
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, EMAIL_RECEIVER, msg.as_string())

    print(f"Emailed {len(new_jobs_df)} new jobs!")

    # --- Persist seen jobs ---
    updated_seen = pd.concat([seen_df, new_jobs_df], ignore_index=True)
    updated_seen.to_csv(SEEN_JOBS_FILE, index=False)
