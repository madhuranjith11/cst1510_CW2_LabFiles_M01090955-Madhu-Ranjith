import pandas as pd
from pathlib import Path
from app.data.db import connect_database, DB_PATH
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import (
    insert_incident,
    update_incident_status,
    delete_incident,
    get_all_incidents,
    get_incidents_by_type_count,
    get_high_severity_by_status
)
from app.data.datasets import (
    insert_dataset,
    get_all_datasets,
    update_dataset,
    delete_dataset,
    count_datasets_by_category
)
from app.data.tickets import (
    insert_ticket,
    get_all_tickets,
    update_ticket,
    delete_ticket,
    count_tickets_by_priority
)
from app.services.setup_service import setup_database_complete

if __name__ == "__main__":
    setup_database_complete()

    db_conn = connect_database()

    if len(get_all_incidents(db_conn)) == 0 and len(get_all_datasets(db_conn)) == 0 and len(get_all_tickets(db_conn)) == 0:
        success, msg = register_user("alice", "SecurePass123!", "analyst")
        print(f"User Registration: {msg}")

        success, msg = login_user("alice", "SecurePass123!")
        print(f"Login Attempt: {msg}")

    incidents_df = get_all_incidents(db_conn)
    print(f"\nTotal Cyber Incidents: {len(incidents_df)}")

    datasets_df = get_all_datasets(db_conn)
    print(f"Total Datasets: {len(datasets_df)}")

    tickets_df = get_all_tickets(db_conn)
    print(f"Total IT Tickets: {len(tickets_df)}")

    incidents_type_df = get_incidents_by_type_count(db_conn)
    print("\n--- Incidents Breakdown by Type ---")
    print(incidents_type_df)

    high_severity_df = get_high_severity_by_status(db_conn)
    print("\n--- High Severity Incidents by Status ---")
    print(high_severity_df)

    datasets_category_df = count_datasets_by_category(db_conn)
    print("\n--- Datasets Count by Category ---")
    print(datasets_category_df)

    tickets_priority_df = count_tickets_by_priority(db_conn)
    print("\n--- Tickets Count by Priority ---")
    print(tickets_priority_df)

    db_conn.close()
    print(f"\nDatabase closed. Location: {DB_PATH.resolve()}")

