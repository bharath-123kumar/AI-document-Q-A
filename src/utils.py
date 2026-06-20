import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_CHROMA_DIR = BASE_DIR / "chroma_db"

# Configuration getters
def get_data_dir() -> Path:
    path = os.getenv("DATA_PATH", str(DEFAULT_DATA_DIR))
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_chroma_dir() -> Path:
    path = os.getenv("CHROMA_DB_PATH", str(DEFAULT_CHROMA_DIR))
    return Path(path)

def get_gemini_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "")
    return key

def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def get_top_k() -> int:
    try:
        return int(os.getenv("TOP_K", "5"))
    except ValueError:
        return 5
