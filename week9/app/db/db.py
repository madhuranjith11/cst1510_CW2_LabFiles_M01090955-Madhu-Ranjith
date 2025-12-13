"""
Database connection module.
Handles SQLite database connections.
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("DATA") / "intelligence_platform.db"


def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.

    Args:
        db_path: Path to the database file

    Returns:
        sqlite3.Connection: Database connection object
    """
    # Ensure DATA directory exists
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(str(db_path))


def close_database(conn):
    """
    Close database connection.

    Args:
        conn: Database connection to close
    """
    if conn:
        conn.close()
