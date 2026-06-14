import re
from pathlib import Path

import pandas as pd

from src.config import DATA_DIR


DEFAULT_MOCK_EMAILS_PATH = DATA_DIR / "mock_emails.csv"


def clean_text(value: str) -> str:
    """Make email text easier to search, score, and cluster."""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def combine_email_text(row: pd.Series) -> str:
    """Combine the most useful email fields into one clean text value."""
    return clean_text(f"{row['subject']} {row['snippet']} {row['body']}")


def load_mock_email_data(csv_path: Path = DEFAULT_MOCK_EMAILS_PATH) -> pd.DataFrame:
    """Load demo emails from CSV and add a clean text field for analysis."""
    emails = pd.read_csv(csv_path)
    emails["clean_text"] = emails.apply(combine_email_text, axis=1)
    return emails


def parse_email_message(raw_message: dict) -> dict:
    """Later, this will normalize raw Gmail message payloads into app-friendly rows."""
    return {
        "id": raw_message.get("id", ""),
        "from_email": raw_message.get("from_email", ""),
        "subject": raw_message.get("subject", ""),
        "date": raw_message.get("date", ""),
        "snippet": raw_message.get("snippet", ""),
        "body": raw_message.get("body", ""),
    }
