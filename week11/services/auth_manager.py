"""AuthManager service class."""

from typing import Optional
import hashlib
import re
from models.user import User
from services.database_manager import DatabaseManager

class SimpleHasher:
    """Simple hasher using SHA256."""

    @staticmethod
    def hash_password(plain: str) -> str:
        """Hash a plain password."""
        return hashlib.sha256(plain.encode("utf-8")).hexdigest()

    @staticmethod
    def check_password(plain: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return SimpleHasher.hash_password(plain) == hashed

class AuthManager:
    """Handles user registration and login."""

    def __init__(self, db: DatabaseManager):
        self._db = db
        self._hasher = SimpleHasher()

    def register_user(self, username: str, password: str, role: str = "user") -> bool:
        """Register a new user."""
        try:
            # Check if user exists
            if self.user_exists(username):
                return False

            password_hash = self._hasher.hash_password(password)
            self._db.execute_query(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False

    def login_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user and return User object if successful."""
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if row is None:
            return None

        username_db = row["username"]
        password_hash_db = row["password_hash"]
        role_db = row["role"]

        if self._hasher.check_password(password, password_hash_db):
            return User(username_db, password_hash_db, role_db)

        return None

    def user_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        row = self._db.fetch_one(
            "SELECT 1 FROM users WHERE username = ?",
            (username,),
        )
        return row is not None

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username format."""
        if not username:
            return False, "Username cannot be empty"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, "Valid username"

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password format."""
        if not password:
            return False, "Password cannot be empty"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, "Valid password"

    @staticmethod
    def check_password_strength(password: str) -> str:
        """Check password strength."""
        if len(password) < 6:
            return "Weak"

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        strength_score = sum([has_upper, has_lower, has_digit, has_special])

        if strength_score >= 4 and len(password) >= 10:
            return "Very Strong"
        elif strength_score >= 3 and len(password) >= 8:
            return "Strong"
        elif strength_score >= 2:
            return "Medium"
        else:
            return "Weak"
