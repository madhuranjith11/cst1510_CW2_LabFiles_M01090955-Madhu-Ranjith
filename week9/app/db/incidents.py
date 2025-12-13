import pandas as pd
from app.db.db import connect_database


def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    """
    Insert a new cyber incident.

    Args:
        date: Incident date (YYYY-MM-DD)
        incident_type: Type of incident
        severity: Severity level
        status: Current status
        description: Incident description
        reported_by: Username of reporter (optional)

    Returns:
        int: ID of inserted incident
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cyber_incidents
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))

    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()

    return incident_id


def get_all_incidents():
    """
    Get all incidents as DataFrame.

    Returns:
        pandas.DataFrame: All incidents
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def get_incident_by_id(incident_id):
    """
    Get single incident by ID.

    Args:
        incident_id: ID of incident to retrieve

    Returns:
        pandas.DataFrame: Single incident or empty DataFrame
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE id = ?",
        conn,
        params=(incident_id,)
    )
    conn.close()
    return df


def update_incident_status(incident_id, new_status):
    """
    Update incident status.

    Args:
        incident_id: ID of incident to update
        new_status: New status value

    Returns:
        int: Number of rows updated
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?",
        (new_status, incident_id)
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()

    return rows_updated


def delete_incident(incident_id):
    """
    Delete incident from database.

    Args:
        incident_id: ID of incident to delete

    Returns:
        int: Number of rows deleted
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cyber_incidents WHERE id = ?",
        (incident_id,)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()

    return rows_deleted


def load_incidents_from_csv(csv_path):
    """
    Load incidents from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        int: Number of rows loaded
    """
    from pathlib import Path

    if not Path(csv_path).exists():
        print(f"⚠️  File not found: {csv_path}")
        return 0

    conn = connect_database()
    df = pd.read_csv(csv_path)

    rows_loaded = df.to_sql(
        'cyber_incidents',
        conn,
        if_exists='append',
        index=False
    )

    conn.close()
    print(f"✅ Loaded {len(df)} incidents from {Path(csv_path).name}")
    return len(df)


def get_incidents_by_severity(severity):
    """
    Get incidents filtered by severity.

    Args:
        severity: Severity level to filter by

    Returns:
        pandas.DataFrame: Filtered incidents
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE severity = ? ORDER BY date DESC",
        conn,
        params=(severity,)
    )
    conn.close()
    return df


def get_incidents_by_status(status):
    """
    Get incidents filtered by status.

    Args:
        status: Status to filter by

    Returns:
        pandas.DataFrame: Filtered incidents
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE status = ? ORDER BY date DESC",
        conn,
        params=(status,)
    )
    conn.close()
    return df


def get_incident_statistics():
    """
    Get incident statistics (count by type, severity, status).

    Returns:
        dict: Statistics dictionary
    """
    conn = connect_database()

    stats = {}

    # Count by type
    df_type = pd.read_sql_query("""
        SELECT incident_type, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
    """, conn)
    stats['by_type'] = df_type

    # Count by severity
    df_severity = pd.read_sql_query("""
        SELECT severity, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY severity
        ORDER BY
            CASE severity
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END
    """, conn)
    stats['by_severity'] = df_severity

    # Count by status
    df_status = pd.read_sql_query("""
        SELECT status, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY status
        ORDER BY count DESC
    """, conn)
    stats['by_status'] = df_status

    conn.close()
    return stats
