"""DatabaseManager service class."""

import sqlite3
from typing import Any, Iterable, Optional, List
import pandas as pd

class DatabaseManager:
    """Handles SQLite database connections and queries."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Establish database connection."""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
                self._connection.row_factory = sqlite3.Row
                # Test the connection
                self._connection.execute("SELECT 1")
            except Exception as e:
                print(f"Database connection error: {e}")
                raise

    def close(self) -> None:
        """Close database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        if self._connection is None:
            self.connect()
        try:
            cur = self._connection.cursor()
            cur.execute(sql, tuple(params))
            self._connection.commit()
            return cur
        except Exception as e:
            print(f"Execute query error: {e}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            raise

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        """Fetch a single row."""
        if self._connection is None:
            self.connect()
        try:
            cur = self._connection.cursor()
            cur.execute(sql, tuple(params))
            return cur.fetchone()
        except Exception as e:
            print(f"Fetch one error: {e}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            raise

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> List[sqlite3.Row]:
        """Fetch all rows."""
        if self._connection is None:
            self.connect()
        try:
            cur = self._connection.cursor()
            cur.execute(sql, tuple(params))
            return cur.fetchall()
        except Exception as e:
            print(f"Fetch all error: {e}")
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            raise

    def fetch_df(self, sql: str, params: Iterable[Any] = ()) -> pd.DataFrame:
        """Fetch results as a pandas DataFrame."""
        if self._connection is None:
            self.connect()
        try:
            return pd.read_sql_query(sql, self._connection, params=list(params))
        except Exception as e:
            print(f"Fetch dataframe error: {e}")
            print(f"SQL: {sql}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
