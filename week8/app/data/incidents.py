import pandas as pd
from app.data.db import connect_database

def add_incident(db, d, itype, level, state, detail, reporter=None):
    cur = db.cursor()
    cur.execute(
        """
            INSERT INTO cyber_incidents
            (date, incident_type, severity, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (d, itype, level, state, detail, reporter)
    )
    db.commit()
    return cur.lastrowid

def fetch_incidents(db):
    return pd.read_sql_query("SELECT * FROM cyber_incidents", db)

def change_incident_state(db, inc_id, state):
    cur = db.cursor()
    cur.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?", (state, inc_id))
    db.commit()
    return cur.rowcount

def drop_incident(db, inc_id):
    cur = db.cursor()
    cur.execute("DELETE FROM cyber_incidents WHERE id = ?", (inc_id,))
    db.commit()
    return cur.rowcount

def type_totals(db):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, db)

def high_severity_status_breakdown(db):
    q = """
        SELECT status, COUNT(*) AS total
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, db)
