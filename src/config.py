from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"
TOKEN_PATH = PROJECT_ROOT / "token.json"


def get_project_paths() -> dict[str, Path]:
    """Return important local paths used by the app."""
    return {
        "project_root": PROJECT_ROOT,
        "data_dir": DATA_DIR,
        "credentials_path": CREDENTIALS_PATH,
        "token_path": TOKEN_PATH,
    }
