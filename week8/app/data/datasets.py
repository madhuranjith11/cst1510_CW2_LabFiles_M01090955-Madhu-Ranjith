import pandas as pd
from app.data.db import connect_database

def add_data_entry(db, name, cat, src, updated_at, records, size_mb):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO datasets_metadata (dataset_name, category, source, last_updated, record_count, file_size_mb) VALUES (?, ?, ?, ?, ?, ?)",
        (name, cat, src, updated_at, records, size_mb)
    )
    db.commit()
    return cur.lastrowid

def fetch_datasets(db):
    return pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", db)

def modify_dataset(db, ds_id, **fields):
    set_block = ", ".join(f"{key} = ?" for key in fields)
    vals = list(fields.values()) + [ds_id]
    cur = db.cursor()
    cur.execute(f"UPDATE datasets_metadata SET {set_block} WHERE id = ?", vals)
    db.commit()
    return cur.rowcount

def remove_dataset(db, ds_id):
    cur = db.cursor()
    cur.execute("DELETE FROM datasets_metadata WHERE id = ?", (ds_id,))
    db.commit()
    return cur.rowcount

def category_breakdown(db):
    q = "SELECT category, COUNT(*) AS total FROM datasets_metadata GROUP BY category ORDER BY total DESC"
    return pd.read_sql_query(q, db)
