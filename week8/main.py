from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import (
    insert_incident, get_all_incidents, update_incident_status,
    delete_incident, load_incidents_from_csv, get_incident_statistics
)
from app.data.datasets import load_datasets_from_csv, get_all_datasets
from app.data.tickets import load_tickets_from_csv, get_all_tickets


def setup_database():
    """Setup database with all tables and data."""
    print("\n" + "="*60)
    print("🗄️  WEEK 8: DATABASE SETUP")
    print("="*60)

    # Connect and create tables
    print("\n[1/4] Creating database tables...")
    conn = connect_database()
    create_all_tables(conn)
    conn.close()

    # Migrate users
    print("\n[2/4] Migrating users from users.txt...")
    migrate_users_from_file('DATA/users.txt')

    # Load CSV data
    print("\n[3/4] Loading CSV data...")
    load_incidents_from_csv('DATA/cyber_incidents.csv')
    load_datasets_from_csv('DATA/datasets_metadata.csv')
    load_tickets_from_csv('DATA/it_tickets.csv')

    # Verify
    print("\n[4/4] Verifying database...")
    conn = connect_database()
    cursor = conn.cursor()

    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n📊 Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")

    conn.close()

    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)


def test_authentication():
    """Test user authentication functions."""
    print("\n" + "="*60)
    print("🔐 TESTING AUTHENTICATION")
    print("="*60)

    # Test registration
    print("\n[TEST] Registering new user...")
    success, msg = register_user("test_analyst", "SecurePass123!", "analyst")
    print(f"  {'✅' if success else '❌'} {msg}")

    # Test login - wrong password
    print("\n[TEST] Login with wrong password...")
    success, msg = login_user("test_analyst", "WrongPassword")
    print(f"  {'✅' if not success else '❌'} {msg}")


def test_crud_operations():
    """Test CRUD operations on incidents."""
    print("\n" + "="*60)
    print("📝 TESTING CRUD OPERATIONS")
    print("="*60)

    # CREATE
    print("\n[CREATE] Inserting new incident...")
    incident_id = insert_incident(
        date="2024-12-12",
        incident_type="Phishing",
        severity="High",
        status="Open",
        description="Suspicious email detected in finance department",
        reported_by="test_analyst"
    )
    print(f"  ✅ Created incident #{incident_id}")

    # READ
    print("\n[READ] Fetching all incidents...")
    df = get_all_incidents()
    print(f"  ✅ Found {len(df)} total incidents")
    if len(df) > 0:
        print(f"\n  Latest 3 incidents:")
        print(df[['id', 'date', 'incident_type', 'severity', 'status']].head(3).to_string(index=False))

    # UPDATE
    print(f"\n[UPDATE] Updating incident #{incident_id} status...")
    rows_updated = update_incident_status(incident_id, "Investigating")
    print(f"  ✅ Updated {rows_updated} incident(s)")

    # DELETE
    print(f"\n[DELETE] Deleting incident #{incident_id}...")
    rows_deleted = delete_incident(incident_id)
    print(f"  ✅ Deleted {rows_deleted} incident(s)")


def show_statistics():
    """Display database statistics."""
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60)

    stats = get_incident_statistics()

    print("\n🔴 Incidents by Type:")
    if not stats['by_type'].empty:
        print(stats['by_type'].to_string(index=False))

    print("\n🟠 Incidents by Severity:")
    if not stats['by_severity'].empty:
        print(stats['by_severity'].to_string(index=False))

    print("\n🟢 Incidents by Status:")
    if not stats['by_status'].empty:
        print(stats['by_status'].to_string(index=False))


def main():
    """Main function to run all demonstrations."""
    # Step 1: Setup database
    setup_database()

    # Step 2: Test authentication
    test_authentication()

    # Step 3: Test CRUD operations
    test_crud_operations()

    # Step 4: Show statistics
    show_statistics()

    print("\n" + "="*60)
    print("🎉 ALL DEMONSTRATIONS COMPLETE!")
    print("="*60)
    print("\nYour database is ready for Week 9 (Streamlit)!")
    print(f"Database location: {Path('DATA/intelligence_platform.db').resolve()}")


if __name__ == "__main__":
    main()
