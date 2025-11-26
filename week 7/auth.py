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

def validate_username(name):
    if not name:
        return False, "Username cannot be empty"
    if len(name) < 3 or len(name) > 20:
        return False, "Username must be 3-20 characters"
    if " " in name:
        return False, "Username cannot contain spaces"
    if not re.match("^[A-Za-z0-9_]+$", name):
        return False, "Only letters, numbers, underscores allowed"
    return True, ""


def validate_password(pw):
    if len(pw) < 6 or len(pw) > 50:
        return False, "Password must be 6-50 characters"
    if not re.search(r"[A-Z]", pw):
        return False, "Missing uppercase letter"
    if not re.search(r"[a-z]", pw):
        return False, "Missing lowercase letter"
    if not re.search(r"[0-9]", pw):
        return False, "Missing number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw):
        return False, "Missing special char"
    return True, ""


def check_password_strength(pw):
    s = 0
    if len(pw) >= 8: s += 1
    if re.search(r"[A-Z]", pw): s += 1
    if re.search(r"[a-z]", pw): s += 1
    if re.search(r"[0-9]", pw): s += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw): s += 1

    return "Weak" if s <= 2 else "Medium" if s <= 4 else "Strong"


def display_menu():
    print("\n" + "=" * 50)
    print("   MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("              Authentication")
    print("=" * 50)
    print("[1] Register")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)

def main():
    print("\nWelcome to the Week 7 Authentication System!")

    run = True
    while run:
        display_menu()
        choice = input("\nSelect option: ").strip()

        if choice == "1":
            print("\n--- NEW USER ---")
            uname = input("Username: ").strip()
            ok, msg = validate_username(uname)
            if not ok:
                print("Error:", msg)
                continue

            pw = input("Password: ").strip()
            ok, msg = validate_password(pw)
            if not ok:
                print("Error:", msg)
                continue

            print("Password Strength:", check_password_strength(pw))

            confirm = input("Confirm password: ").strip()
            if pw != confirm:
                print("Passwords do not match.")
                continue

            role = input("Role (user/admin/analyst): ").strip().lower()
            if role not in ["user", "admin", "analyst"]:
                role = "user"

            register_user(uname, pw, role)
            print("User registered successfully.")

        elif choice == "2":
            print("\n--- LOGIN ---")
            uname = input("Username: ").strip()
            pw = input("Password: ").strip()

            if login_user(uname, pw):
                sess = create_session(uname)
                print("Login successful.")
                print("Session token:", sess)
                input("Press Enter to continue...")
            else:
                print("Invalid login.")
                input("Press Enter to continue...")

        elif choice == "3":
            print("\nExiting system...")
            run = False

        else:
            print("Invalid option.")
            
main()

