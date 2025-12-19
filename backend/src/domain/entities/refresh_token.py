"""Refresh token entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
import uuid
import secrets


def generate_id() -> str:
    """Generate a new UUID as string."""
    return str(uuid.uuid4())


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


@dataclass
class RefreshToken:
    """Refresh token entity with behavior."""
    id: str
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime
    revoked: bool = False

    @classmethod
    def create(cls, user_id: str, expires_days: int = 30) -> RefreshToken:
        """Create a new refresh token."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=expires_days)

        return cls(
            id=generate_id(),
            user_id=user_id,
            token=generate_token(),
            expires_at=expires_at,
            created_at=now,
            revoked=False,
        )

    def is_valid(self) -> bool:
        """Check if token is still valid."""
        if self.revoked:
            return False
        return datetime.now(UTC) < self.expires_at

    def revoke(self) -> None:
        """Revoke the token."""
        self.revoked = True

    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now(UTC) >= self.expires_at
