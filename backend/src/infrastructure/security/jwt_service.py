"""JWT token generation and verification service."""
import os
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any

from jose import jwt, JWTError


class JWTService:
    """Service for creating and verifying JWT tokens."""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30,
    ):
        """
        Initialize JWT service.

        Args:
            secret_key: Secret key for signing tokens (from env if not provided)
            algorithm: Algorithm to use for signing (default: HS256)
            access_token_expire_minutes: Access token expiration time in minutes
            refresh_token_expire_days: Refresh token expiration time in days
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY must be set in environment or provided")

        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create an access token.

        Args:
            data: Data to encode in the token (should include 'sub' for user ID)

        Returns:
            Encoded JWT access token
        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a refresh token.

        Args:
            data: Data to encode in the token (should include 'sub' for user ID)

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token data

        Raises:
            JWTError: If token is invalid or expired
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return its payload.

        Args:
            token: JWT token to verify
            token_type: Expected token type ('access' or 'refresh')

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = self.decode_token(token)

            # Verify token type
            if payload.get("type") != token_type:
                return None

            return payload
        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from a token.

        Args:
            token: JWT token

        Returns:
            User ID if token is valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None
