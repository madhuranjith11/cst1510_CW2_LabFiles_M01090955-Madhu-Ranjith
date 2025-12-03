import pandas as pd
from app.data.db import connect_database

def add_ticket(db, t_id, pr, st, cat, title, desc, c_date, r_date=None, assigned=None):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO it_tickets (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (t_id, pr, st, cat, title, desc, c_date, r_date, assigned)
    )
    db.commit()
    return cur.lastrowid

def fetch_tickets(db):
    return pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", db)

def edit_ticket(db, t_id, **fields):
    update_block = ", ".join(f"{k} = ?" for k in fields)
    vals = list(fields.values()) + [t_id]
    cur = db.cursor()
    cur.execute(f"UPDATE it_tickets SET {update_block} WHERE ticket_id = ?", vals)
    db.commit()
    return cur.rowcount

def drop_ticket(db, t_id):
    cur = db.cursor()
    cur.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (t_id,))
    db.commit()
    return cur.rowcount

def priority_overview(db):
    q = "SELECT priority, COUNT(*) AS total FROM it_tickets GROUP BY priority ORDER BY total DESC"
    return pd.read_sql_query(q, db)
users 
from app.data.db import connect_database

def fetch_user(uname):
    db = connect_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (uname,))
    result = cur.fetchone()
    db.close()
    return result

def add_user(uname, pwd_hash, role_type='user'):
    db = connect_database()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (uname, pwd_hash, role_type)
    )
    db.commit()
    db.close()
