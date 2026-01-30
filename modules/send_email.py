import smtplib
import time
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.get_google_sheet import load_seen_jobs, append_seen_jobs


def send_email(all_jobs_df: pd.DataFrame):
    # --- Email config ---
    smtp_host = os.getenv("JOBSCRAPER_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("JOBSCRAPER_SMTP_PORT", 465))

    email_username = os.getenv("JOBSCRAPER_EMAIL_USERNAME")
    email_password = os.getenv("JOBSCRAPER_EMAIL_PASSWORD")
    email_receiver = os.getenv("JOBSCRAPER_EMAIL_RECEIVER", email_username)

    sheet_id = os.getenv("JOBSCRAPER_GSHEET_ID")

    if not email_username or not email_password:
        raise ValueError("Missing email environment variables")

    if not sheet_id:
        raise ValueError("Missing JOBSCRAPER_GSHEET_ID")

    if all_jobs_df.empty:
        print("No jobs collected — skipping email.")
        return

    if "key" not in all_jobs_df.columns:
        raise ValueError("Expected 'key' column missing from all_jobs_df")

    # --- Date ---
    email_date = time.strftime("%A, %b %d %Y", time.localtime())

    # --- Load seen jobs from Google Sheets ---
    seen_df = load_seen_jobs(sheet_id)

    if not seen_df.empty and "key" not in seen_df.columns:
        raise ValueError("'key' column missing in seen_jobs sheet")

    # --- Filter new jobs ---
    new_jobs_df = (
        all_jobs_df
        if seen_df.empty
        else all_jobs_df[~all_jobs_df["key"].isin(seen_df["key"])]
    )

    if new_jobs_df.empty:
        print("No new jobs to email.")
        return

    # --- Build email ---
    html_table = new_jobs_df.to_html(index=False, escape=False)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{email_date} New Job Listings ({len(new_jobs_df)})"
    msg["From"] = email_username
    msg["To"] = email_receiver

    msg.attach(MIMEText(f"""
    <html>
      <body>
        <h2>New Job Listings</h2>
        {html_table}
      </body>
    </html>
    """, "html"))

    # --- Send ---
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(email_username, email_password)
        server.sendmail(email_username, email_receiver, msg.as_string())

    print(f"Emailed {len(new_jobs_df)} new jobs!")

    # --- Persist seen jobs to Google Sheets ---
    append_seen_jobs(new_jobs_df, sheet_id)
