from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma"

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://aihubmix.com/v1")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
OPENAI_MODEL_API_KEY = os.getenv("OPENAI_MODEL_API_KEY", "")

OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_EMBED_API_KEY = os.getenv("OPENAI_EMBED_API_KEY", "")