import smtplib
import time
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email():
    # --- Environment variables ---
    SMTP_HOST = os.getenv("JOBSCRAPER_SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("JOBSCRAPER_SMTP_PORT", 465))

    EMAIL_USERNAME = os.getenv("JOBSCRAPER_EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("JOBSCRAPER_EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.getenv("JOBSCRAPER_EMAIL_RECEIVER", EMAIL_USERNAME)

    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise ValueError("Missing EMAIL_USERNAME or EMAIL_PASSWORD environment variables")

    # --- Date ---
    now = time.localtime()
    email_date = time.strftime("%A, %b %d %Y", now)

    # --- Load scraped jobs ---
    jobs_df = pd.read_csv("../data/all_filtered_jobs.csv")

    # --- Load previously seen jobs ---
    seen_file = "../data/seen_jobs.csv"
    if os.path.exists(seen_file):
        seen_df = pd.read_csv(seen_file)
    else:
        seen_df = pd.DataFrame(columns=jobs_df.columns)

    # --- Filter new jobs ---
    new_jobs_df = jobs_df[~jobs_df["key"].isin(seen_df["key"])]

    if new_jobs_df.empty:
        print("No new jobs to email.")
        return

    # --- Build email ---
    html_table = new_jobs_df.to_html(index=False, escape=False)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{email_date} New Job Listings ({len(new_jobs_df)})"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = EMAIL_RECEIVER

    html_content = f"""
    <html>
      <body>
        <h2>New Job Listings</h2>
        {html_table}
      </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # --- Send email ---
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(
            EMAIL_USERNAME,
            EMAIL_RECEIVER,
            msg.as_string()
        )

    print(f"Emailed {len(new_jobs_df)} new jobs!")

    # --- Update seen jobs ---
    updated_seen = pd.concat([seen_df, new_jobs_df], ignore_index=True)
    updated_seen.to_csv(seen_file, index=False)
