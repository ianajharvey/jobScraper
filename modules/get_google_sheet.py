import os
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_gsheet_client():
    creds_json = os.getenv("JOBSCRAPER_GOOGLE_CRED_JSON")

    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds_path = os.getenv("JOBSCRAPER_GOOGLE_CRED_PATH")
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)

    return gspread.authorize(creds)


def load_seen_jobs(sheet_id: str, worksheet_name="seen_jobs") -> pd.DataFrame:
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id)
    ws = sheet.worksheet(worksheet_name)

    records = ws.get_all_records()
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def append_seen_jobs(df: pd.DataFrame, sheet_id: str, worksheet_name="seen_jobs"):
    if df.empty:
        return

    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id)
    ws = sheet.worksheet(worksheet_name)

    ws.append_rows(
        df.astype(str).values.tolist(),
        value_input_option="RAW"
    )
