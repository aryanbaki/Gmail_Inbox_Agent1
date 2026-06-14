import pandas as pd


HIGH_PRIORITY_WORDS = [
    "urgent",
    "deadline",
    "due",
    "payment failed",
    "security alert",
    "action required",
    "account locked",
    "interview",
    "appointment",
]

LOW_PRIORITY_WORDS = [
    "sale",
    "discount",
    "unsubscribe",
    "newsletter",
    "promotion",
    "deal",
]


def assign_priority_from_text(text: str) -> str:
    """Assign a simple priority label using beginner-friendly keyword rules."""
    normalized_text = str(text).lower()

    if any(word in normalized_text for word in HIGH_PRIORITY_WORDS):
        return "high"
    if any(word in normalized_text for word in LOW_PRIORITY_WORDS):
        return "low"
    return "medium"


def add_priority_labels(emails: pd.DataFrame) -> pd.DataFrame:
    """Add high, medium, and low priority labels to a dataframe of emails."""
    scored_emails = emails.copy()
    scored_emails["priority"] = scored_emails["clean_text"].apply(assign_priority_from_text)
    return scored_emails
