import os
import time
import re
import bcrypt
import secrets

USER_DATA_FILE = "users.txt"
SESSION_STORE = "sessions.txt"
ATTEMPT_LOG = "failed_attempts.txt"

MAX_ATTEMPTS = 3
LOCK_PERIOD = 5 * 60


def hash_password(plain_text_password):
    raw = plain_text_password.encode("utf-8")
    salt_val = bcrypt.gensalt()
    hashed_val = bcrypt.hashpw(raw, salt_val)
    return hashed_val.decode("utf-8")

def verify_password(plain_text_password, hashed_password):
    incoming = plain_text_password.encode("utf-8")
    stored = hashed_password.encode("utf-8")
    return bcrypt.checkpw(incoming, stored)

def create_session(username):
    session_key = secrets.token_hex(16)
    created_at = time.time()
    with open(SESSION_STORE, "a") as f:
        f.write(f"{username},{session_key},{created_at}\n")
    return session_key

def register_user(username, password, role="user"):
    if not os.path.exists(USER_DATA_FILE):
        open(USER_DATA_FILE, "w").close()

    with open(USER_DATA_FILE, "r") as f:
        for entry in f:
            existing = entry.strip().split(",")[0]
            if existing == username:
                return False

    secured = hash_password(password)

    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{secured},{role}\n")

    return True


def load_failed_attempts():
    data = {}
    if os.path.exists(ATTEMPT_LOG):
        with open(ATTEMPT_LOG, "r") as f:
            for rec in f:
                u, c, ts = rec.strip().split(",")
                data[u] = (int(c), float(ts))
    return data


def save_failed_attempts(attempt_dict):
    with open(ATTEMPT_LOG, "w") as f:
        for u, pair in attempt_dict.items():
            f.write(f"{u},{pair[0]},{pair[1]}\n")


def login_user(username, password):
    logs = load_failed_attempts()

    if username in logs:
        hit_count, last_try = logs[username]
        gap = time.time() - last_try

        if hit_count >= MAX_ATTEMPTS and gap < LOCK_PERIOD:
            remaining = int((LOCK_PERIOD - gap) // 60)
            print(f"Account locked. Try again in {remaining} min")
            return False

        if gap >= LOCK_PERIOD:
            logs[username] = (0, 0)
            save_failed_attempts(logs)

    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r") as f:
        for rec in f:
            user_rec, hashed_pw, *_ = rec.strip().split(",", 2)

            if user_rec == username:
                if verify_password(password, hashed_pw):
                    logs[username] = (0, 0)
                    save_failed_attempts(logs)
                    return True
                else:
                    prev_count = logs.get(username, (0, 0))[0]
                    logs[username] = (prev_count + 1, time.time())
                    save_failed_attempts(logs)
                    print(f"Incorrect password. Attempt {logs[username][0]}/{MAX_ATTEMPTS}")
                    return False

    return False



