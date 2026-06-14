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
    "final notice",
    "verify",
    "suspicious",
]

MEDIUM_PRIORITY_WORDS = [
    "approval",
    "reminder",
    "meeting",
    "project",
    "invoice",
    "verification",
    "review",
]

LOW_PRIORITY_WORDS = [
    "sale",
    "discount",
    "unsubscribe",
    "newsletter",
    "promotion",
    "deal",
    "offer",
    "coupon",
]


def _matching_words(text: str, words: list[str]) -> list[str]:
    """Return keywords found in the email text."""
    return [word for word in words if word in text]


def assign_priority_with_reason(text: str) -> tuple[str, str]:
    """Assign a priority label and explain the reason."""
    normalized_text = str(text).lower()

    high_matches = _matching_words(normalized_text, HIGH_PRIORITY_WORDS)
    if high_matches:
        return (
            "high",
            f"High priority because the email mentions {', '.join(high_matches[:3])}.",
        )

    low_matches = _matching_words(normalized_text, LOW_PRIORITY_WORDS)
    if low_matches:
        return (
            "low",
            f"Low priority because the email looks promotional or informational: {', '.join(low_matches[:3])}.",
        )

    medium_matches = _matching_words(normalized_text, MEDIUM_PRIORITY_WORDS)
    if medium_matches:
        return (
            "medium",
            f"Medium priority because the email mentions {', '.join(medium_matches[:3])}.",
        )

    return "medium", "Medium priority because no high or low priority keywords were found."


def assign_priority_from_text(text: str) -> str:
    """Assign a simple priority label using keyword rules."""
    priority, _ = assign_priority_with_reason(text)
    return priority


def add_priority_labels(emails: pd.DataFrame) -> pd.DataFrame:
    """Add priority labels and readable reasons to a dataframe of emails."""
    scored_emails = emails.copy()

    if scored_emails.empty:
        scored_emails["priority"] = []
        scored_emails["priority_reason"] = []
        return scored_emails

    priority_results = scored_emails["clean_text"].apply(assign_priority_with_reason)
    scored_emails["priority"] = priority_results.apply(lambda result: result[0])
    scored_emails["priority_reason"] = priority_results.apply(lambda result: result[1])
    return scored_emails
