import base64
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


def _get_header(headers: list[dict], name: str) -> str:
    """Return a Gmail header value by name."""
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def _decode_body_data(data: str) -> str:
    """Decode Gmail's base64url body data safely."""
    if not data:
        return ""

    try:
        padded_data = data + "=" * (-len(data) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded_data)
        return decoded_bytes.decode("utf-8", errors="replace").strip()
    except Exception:
        return ""


def _extract_plain_text_from_payload(payload: dict) -> str:
    """Walk a Gmail payload and prefer text/plain body content."""
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data", "")

    if mime_type == "text/plain" and body_data:
        return _decode_body_data(body_data)

    for part in payload.get("parts", []):
        text = _extract_plain_text_from_payload(part)
        if text:
            return text

    if body_data:
        return _decode_body_data(body_data)

    return ""


def parse_gmail_message(raw_message: dict) -> dict:
    """Normalize a raw Gmail API message into one dataframe-ready row."""
    payload = raw_message.get("payload", {})
    headers = payload.get("headers", [])
    snippet = raw_message.get("snippet", "")
    body = _extract_plain_text_from_payload(payload) or snippet
    message_id = raw_message.get("id", "")

    return {
        "id": message_id,
        "message_id": message_id,
        "thread_id": raw_message.get("threadId", ""),
        "from_email": _get_header(headers, "From"),
        "subject": _get_header(headers, "Subject"),
        "date": _get_header(headers, "Date"),
        "snippet": snippet,
        "body": body,
        "labels": ", ".join(raw_message.get("labelIds", [])),
    }


def parse_gmail_messages(raw_messages: list[dict]) -> pd.DataFrame:
    """Parse raw Gmail messages and add clean text for clustering."""
    emails = pd.DataFrame([parse_gmail_message(message) for message in raw_messages])

    if emails.empty:
        return pd.DataFrame(
            columns=[
                "id",
                "message_id",
                "thread_id",
                "from_email",
                "subject",
                "date",
                "snippet",
                "body",
                "labels",
                "clean_text",
            ]
        )

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
