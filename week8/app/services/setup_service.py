from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.incidents import load_incidents_from_csv
from app.data.datasets import load_datasets_from_csv
from app.data.tickets import load_tickets_from_csv
from app.services.user_service import migrate_users_from_file


def initialize_database():
    """
    Initialize the database with all tables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("\\n🔧 Initializing database...")
        conn = connect_database()
        create_all_tables(conn)
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def load_all_data():
    """
    Load all data from CSV files and migrate users.
    
    Returns:
        dict: Summary of loaded data
    """
    data_dir = Path("DATA")
    summary = {
        'users': 0,
        'incidents': 0,
        'datasets': 0,
        'tickets': 0,
        'errors': []
    }
    
    print("\\n📥 Loading data from files...")
    
    # Migrate users from users.txt
    try:
        users_file = data_dir / "users.txt"
        if users_file.exists():
            summary['users'] = migrate_users_from_file(str(users_file))
        else:
            summary['errors'].append(f"users.txt not found in {data_dir}")
    except Exception as e:
        summary['errors'].append(f"Error loading users: {e}")
    
    # Load cyber incidents
    try:
        incidents_file = data_dir / "cyber_incidents.csv"
        if incidents_file.exists():
            summary['incidents'] = load_incidents_from_csv(str(incidents_file))
        else:
            summary['errors'].append(f"cyber_incidents.csv not found in {data_dir}")
    except Exception as e:
        summary['errors'].append(f"Error loading incidents: {e}")
    
    # Load datasets metadata
    try:
        datasets_file = data_dir / "datasets_metadata.csv"
        if datasets_file.exists():
            summary['datasets'] = load_datasets_from_csv(str(datasets_file))
        else:
            summary['errors'].append(f"datasets_metadata.csv not found in {data_dir}")
    except Exception as e:
        summary['errors'].append(f"Error loading datasets: {e}")
    
    # Load IT tickets
    try:
        tickets_file = data_dir / "it_tickets.csv"
        if tickets_file.exists():
            summary['tickets'] = load_tickets_from_csv(str(tickets_file))
        else:
            summary['errors'].append(f"it_tickets.csv not found in {data_dir}")
    except Exception as e:
        summary['errors'].append(f"Error loading tickets: {e}")
    
    return summary


def verify_database():
    """
    Verify database setup and return statistics.
    
    Returns:
        dict: Database statistics
    """
    print("\\n🔍 Verifying database...")
    conn = connect_database()
    cursor = conn.cursor()
    
    stats = {}
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count
        except Exception as e:
            stats[table] = f"Error: {e}"
    
    conn.close()
    return stats


def complete_setup():
    """
    Run complete database setup: initialize, load data, and verify.
    
    Returns:
        bool: True if setup was successful
    """
    print("\\n" + "="*70)
    print("🚀 STARTING COMPLETE DATABASE SETUP")
    print("="*70)
    
    # Step 1: Initialize database
    if not initialize_database():
        print("\\n❌ Setup failed at initialization step")
        return False
    
    # Step 2: Load all data
    print("\\n" + "-"*70)
    summary = load_all_data()
    
    # Step 3: Verify
    print("\\n" + "-"*70)
    stats = verify_database()
    
    # Display results
    print("\\n" + "="*70)
    print("📊 SETUP SUMMARY")
    print("="*70)
    
    print("\\n✅ Data Loaded:")
    print(f"  • Users:              {summary['users']}")
    print(f"  • Cyber Incidents:    {summary['incidents']}")
    print(f"  • Datasets:           {summary['datasets']}")
    print(f"  • IT Tickets:         {summary['tickets']}")
    
    if summary['errors']:
        print("\\n⚠️  Warnings/Errors:")
        for error in summary['errors']:
            print(f"  • {error}")
    
    print("\\n📈 Database Statistics:")
    for table, count in stats.items():
        print(f"  • {table:<25} {count}")
    
    print("\\n" + "="*70)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*70)
    print(f"\\n💾 Database location: {Path('DATA/intelligence_platform.db').resolve()}")
    
    return True


def reset_database():
    """
    Reset database by deleting the file and recreating everything.
    WARNING: This will delete all data!
    
    Returns:
        bool: True if reset was successful
    """
    db_path = Path("DATA") / "intelligence_platform.db"
    
    if db_path.exists():
        response = input("\\n⚠️  WARNING: This will delete all database data. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Reset cancelled.")
            return False
        
        try:
            db_path.unlink()
            print(f"\\n🗑️  Deleted {db_path}")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            return False
    
    # Run complete setup
    return complete_setup()
