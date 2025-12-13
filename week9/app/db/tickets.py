import pandas as pd
from app.db.db import connect_database



def insert_ticket(ticket_id, priority, status, category, subject, description,
                 created_date, resolved_date=None, assigned_to=None):
    """
    Insert new IT ticket.

    Args:
        ticket_id: Unique ticket identifier
        priority: Priority level
        status: Current status
        category: Ticket category
        subject: Ticket subject
        description: Detailed description
        created_date: Creation date
        resolved_date: Resolution date (optional)
        assigned_to: Assigned user (optional)

    Returns:
        int: ID of inserted ticket
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description,
         created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description,
          created_date, resolved_date, assigned_to))

    conn.commit()
    id_inserted = cursor.lastrowid
    conn.close()

    return id_inserted


def get_all_tickets():
    """
    Get all tickets as DataFrame.

    Returns:
        pandas.DataFrame: All tickets
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def get_ticket_by_id(ticket_id):
    """
    Get single ticket by ID.

    Args:
        ticket_id: ID of ticket to retrieve

    Returns:
        pandas.DataFrame: Single ticket or empty DataFrame
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE id = ?",
        conn,
        params=(ticket_id,)
    )
    conn.close()
    return df


def update_ticket_status(ticket_id, new_status, resolved_date=None):
    """
    Update ticket status.

    Args:
        ticket_id: ID of ticket to update
        new_status: New status value
        resolved_date: Resolution date (optional, for closed tickets)

    Returns:
        int: Number of rows updated
    """
    conn = connect_database()
    cursor = conn.cursor()

    if resolved_date:
        cursor.execute(
            "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE id = ?",
            (new_status, resolved_date, ticket_id)
        )
    else:
        cursor.execute(
            "UPDATE it_tickets SET status = ? WHERE id = ?",
            (new_status, ticket_id)
        )

    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()

    return rows_updated


def delete_ticket(ticket_id):
    """
    Delete ticket from database.

    Args:
        ticket_id: ID of ticket to delete

    Returns:
        int: Number of rows deleted
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM it_tickets WHERE id = ?",
        (ticket_id,)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()

    return rows_deleted


def load_tickets_from_csv(csv_path):
    """
    Load tickets from CSV file.

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
        'it_tickets',
        conn,
        if_exists='append',
        index=False
    )

    conn.close()
    print(f"✅ Loaded {len(df)} tickets from {Path(csv_path).name}")
    return len(df)


def get_tickets_by_priority(priority):
    """
    Get tickets filtered by priority.

    Args:
        priority: Priority level to filter by

    Returns:
        pandas.DataFrame: Filtered tickets
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE priority = ? ORDER BY created_date DESC",
        conn,
        params=(priority,)
    )
    conn.close()
    return df


def get_tickets_by_status(status):
    """
    Get tickets filtered by status.

    Args:
        status: Status to filter by

    Returns:
        pandas.DataFrame: Filtered tickets
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE status = ? ORDER BY created_date DESC",
        conn,
        params=(status,)
    )
    conn.close()
    return df


def get_open_tickets():
    """
    Get all open/unresolved tickets.

    Returns:
        pandas.DataFrame: Open tickets
    """
    conn = connect_database()
    df = pd.read_sql_query("""
        SELECT * FROM it_tickets
        WHERE status NOT IN ('Resolved', 'Closed')
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            created_date
    """, conn)
    conn.close()
    return df
