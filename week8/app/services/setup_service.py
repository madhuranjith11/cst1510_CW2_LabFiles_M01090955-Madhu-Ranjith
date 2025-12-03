import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file
from app.data.db import DB_PATH

DB_FILE = Path("project_database.db")

def initialize_full_database():
    print("\nStep 1/4: Establishing connection to the database...")
    connection = connect_database()
    print("✅ Connection successful!")

    print("\nStep 2/4: Setting up tables in the database...")
    create_all_tables(connection)
    print("✅ Tables created successfully!")

    print("\nStep 3/4: Importing users from users.txt...")
    migrated_count = migrate_users_from_file()
    print(f"✅ {migrated_count} users imported successfully!")

    print("\nStep 4/4: Checking database contents...")
    cur = connection.cursor()
    table_list = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']

    print("\nDatabase Overview:")
    print(f"{'Table Name':<25} {'Number of Records':<15}")
    for tbl in table_list:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        num_rows = cur.fetchone()[0]
        print(f"{tbl:<25} {num_rows:<15}")

    connection.close()
    print(f"\nDatabase path: {DB_FILE.resolve()}")

initialize_full_database()
