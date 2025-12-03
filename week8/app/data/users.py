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
