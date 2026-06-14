from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.config import CREDENTIALS_PATH, SCOPES, TOKEN_PATH


class GmailAuthError(RuntimeError):
    """Raised when Gmail authentication cannot be completed."""


def credentials_file_exists() -> bool:
    """Check whether a local Gmail credentials file is present."""
    return CREDENTIALS_PATH.exists()


def authenticate_gmail():
    """Authenticate with Gmail through local OAuth and return a Gmail service."""
    if not CREDENTIALS_PATH.exists():
        raise GmailAuthError(
            "Missing credentials.json. Place your Gmail OAuth credentials.json file "
            "in the project root before using Gmail Mode."
        )

    credentials = None

    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        credentials = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(credentials.to_json())
    return build("gmail", "v1", credentials=credentials)
