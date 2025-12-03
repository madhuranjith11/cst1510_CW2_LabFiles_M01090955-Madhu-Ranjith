import sqlite3
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[2]
STORE_PATH = ROOT_PATH / "DATA"
DB_FILE = STORE_PATH / "intelligence_platform.db"

def open_db():
    STORE_PATH.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_FILE.as_posix())
