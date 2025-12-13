import bcrypt
import secrets
import time
import re
from pathlib import Path

from db.db import connect_database
from db.users import (
    get_user_by_username,
    insert_user
)

# Files for simple brute-force protection
SESSION_STORE = "sessions.txt"
ATTEMPT_LOG = "failed_attempts.txt"

MAX_ATTEMPTS = 3
LOCK_PERIOD = 5 * 60  # seconds


# ============================================================
# PASSWORD HASHING
# ============================================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except:
        return False


# ============================================================
# FAILED ATTEMPTS STORAGE
# ============================================================
def load_failed_attempts():
    if not Path(ATTEMPT_LOG).exists():
        return {}

    data = {}
    with open(ATTEMPT_LOG, "r") as f:
        for line in f:
            user, count, ts = line.strip().split(",")
            data[user] = (int(count), float(ts))
    return data


def save_failed_attempts(attempt_data: dict):
    with open(ATTEMPT_LOG, "w") as f:
        for user, (count, ts) in attempt_data.items():
            f.write(f"{user},{count},{ts}\n")


# ============================================================
# USER AUTHENTICATION
# ============================================================
def register_user(username: str, password: str, role: str = "user") -> bool:
    """
    Register a new user in the DB.
    Returns True if successful, False if username exists.
    """
    conn = connect_database()

    # Check if username exists
    existing = get_user_by_username(username)
    if existing:
        conn.close()
        return False

    pw_hash = hash_password(password)
    insert_user(username, pw_hash, role)
    conn.close()
    return True


def login_user(username: str, password: str) -> bool:
    """
    Login user. Handles brute-force protection.
    Returns True on success, False otherwise.
    """
    logs = load_failed_attempts()
    now = time.time()

    # If user had failed attempts
    if username in logs:
        count, last_try = logs[username]
        diff = now - last_try

        # Locked out?
        if count >= MAX_ATTEMPTS and diff < LOCK_PERIOD:
            return False

        # Reset after lock period expired
        if diff > LOCK_PERIOD:
            logs[username] = (0, 0)
            save_failed_attempts(logs)

    user = get_user_by_username(username)
    if not user:
        return False

    stored_hash = user[2]  # password_hash column

    if verify_password(password, stored_hash):
        logs[username] = (0, 0)
        save_failed_attempts(logs)
        return True
    else:
        # Increase attempt counter
        prev = logs.get(username, (0, 0))[0]
        logs[username] = (prev + 1, now)
        save_failed_attempts(logs)
        return False


# ============================================================
# SESSION MANAGEMENT
# ============================================================
def create_session(username: str) -> str:
    """
    Create session token (for logging in)
    """
    token = secrets.token_hex(16)
    ts = time.time()

    with open(SESSION_STORE, "a") as f:
        f.write(f"{username},{token},{ts}\n")

    return token


# ============================================================
# INPUT VALIDATION
# ============================================================
def validate_username(username: str):
    if not username:
        return False, "Username cannot be empty."
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3–20 characters."
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False, "Only letters, numbers, and _ allowed."
    return True, ""


def validate_password(password: str):
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Must include uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Must include lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Must include number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Must include special character."
    return True, ""


def check_password_strength(pw: str) -> str:
    score = 0
    if len(pw) >= 8: score += 1
    if re.search(r"[A-Z]", pw): score += 1
    if re.search(r"[a-z]", pw): score += 1
    if re.search(r"[0-9]", pw): score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw): score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"
