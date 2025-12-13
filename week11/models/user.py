"""User entity class."""

class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""

    def __init__(self, username: str, password_hash: str, role: str = "user"):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    def get_username(self) -> str:
        """Get the username."""
        return self.__username

    def get_role(self) -> str:
        """Get the user role."""
        return self.__role

    def get_password_hash(self) -> str:
        """Get the password hash."""
        return self.__password_hash

    def verify_password(self, plain_password: str, hasher) -> bool:
        """Check if a plain-text password matches this user's hash."""
        return hasher.check_password(plain_password, self.__password_hash)

    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"

    def __repr__(self) -> str:
        return self.__str__()
