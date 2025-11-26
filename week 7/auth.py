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


