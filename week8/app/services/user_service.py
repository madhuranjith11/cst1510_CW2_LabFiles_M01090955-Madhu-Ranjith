import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_users_table

ROOT_DIR = Path(__file__).resolve().parents[2]
USERS_PATH = ROOT_DIR / "DATA" / "users.txt"

def signup(username, pwd, role_type='user'):
    db = connect_database()
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        db.close()
        return False, f"Username '{username}' is already taken."

    pwd_bytes = pwd.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_pwd, role_type)
    )
    db.commit()
    db.close()

    return True, f"User '{username}' created successfully!"

def signin(username, pwd):
    db = connect_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = cur.fetchone()
    db.close()

    if not user_data:
        return False, "User not found."

    stored_hash = user_data[2]
    if bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f"Hello, {username}!"
    return False, "Wrong password."

def import_users(file_path=USERS_PATH):
    if not file_path.exists():
        return False, f"No user file at {file_path}"

    db = connect_database()
    create_users_table(db)
    cur = db.cursor()

    added = 0
    ignored = 0

    with file_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            uname, pwd_hash, role = map(str.strip, parts)
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (uname, pwd_hash, role)
                )
                if cur.rowcount > 0:
                    added += 1
                else:
                    ignored += 1
            except Exception as err:
                print(f"Skipping {uname}: {err}")

    db.commit()
    db.close()
    return True, f"Imported {added} users, skipped {ignored} existing users."
