"""Password hashing and verification service."""
from passlib.context import CryptContext


class PasswordService:
    """Service for password hashing and verification using Argon2."""

    def __init__(self):
        """Initialize password context with Argon2."""
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__memory_cost=65536,  # 64 MB
            argon2__time_cost=3,  # 3 iterations
            argon2__parallelism=4,  # 4 parallel threads
        )

    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against

        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if a hashed password needs to be rehashed.

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if password needs rehashing, False otherwise
        """
        return self.pwd_context.needs_update(hashed_password)
