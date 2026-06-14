from pathlib import Path


def credentials_file_exists(credentials_path: Path) -> bool:
    """Check whether a local Gmail credentials file is present."""
    return credentials_path.exists()


def authenticate_gmail() -> None:
    """Later, this will run the Gmail OAuth flow and create a local token file."""
    raise NotImplementedError("Gmail authentication is not implemented in the starter scaffold.")
