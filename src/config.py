from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
CREDENTIALS_PATH = PROJECT_ROOT / CREDENTIALS_FILE
TOKEN_PATH = PROJECT_ROOT / TOKEN_FILE
MAX_EMAILS = 200
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_project_paths() -> dict[str, Path]:
    """Return important local paths used by the app."""
    return {
        "project_root": PROJECT_ROOT,
        "data_dir": DATA_DIR,
        "credentials_path": CREDENTIALS_PATH,
        "token_path": TOKEN_PATH,
    }
