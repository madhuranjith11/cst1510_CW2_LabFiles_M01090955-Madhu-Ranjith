"""Check actual column names in database tables."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "intelligence_platform.db"

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

tables = ['cyber_incidents', 'datasets_metadata', 'it_tickets']

for table in tables:
    print(f"\n{'='*60}")
    print(f"Table: {table}")
    print('='*60)

    # Get columns
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()

    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]:20s} ({col[2]})")

    # Get sample row
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    row = cursor.fetchone()
    if row:
        print("\nSample data:")
        for i, val in enumerate(row):
            print(f"  {columns[i][1]:20s} = {val}")

conn.close()
