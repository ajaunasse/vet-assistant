"""User entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from typing import Optional
import uuid
import secrets


def generate_id() -> str:
    """Generate a new UUID as string."""
    return str(uuid.uuid4())


def generate_verification_token() -> str:
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)


@dataclass
class User:
    """User entity with behavior."""
    id: str
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    clinic_name: Optional[str] = None
    order_number: Optional[str] = None
    specialty: Optional[str] = None
    is_student: bool = False
    school_name: Optional[str] = None
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        clinic_name: Optional[str] = None,
        order_number: Optional[str] = None,
        specialty: Optional[str] = None,
        is_student: bool = False,
        school_name: Optional[str] = None,
    ) -> User:
        """Create a new user with verification token."""
        now = datetime.now(UTC)
        verification_token = generate_verification_token()
        verification_expires = now + timedelta(days=7)  # Token valid for 7 days

        return cls(
            id=generate_id(),
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            clinic_name=clinic_name,
            order_number=order_number,
            specialty=specialty,
            is_student=is_student,
            school_name=school_name,
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires=verification_expires,
            created_at=now,
            updated_at=now,
        )

    def verify_email(self) -> None:
        """Mark email as verified and clear verification token."""
        self.is_verified = True
        self.verification_token = None
        self.verification_token_expires = None
        self.updated_at = datetime.now(UTC)

    def generate_new_verification_token(self) -> str:
        """Generate a new verification token."""
        self.verification_token = generate_verification_token()
        self.verification_token_expires = datetime.now(UTC) + timedelta(days=7)
        self.updated_at = datetime.now(UTC)
        return self.verification_token

    def is_verification_token_valid(self) -> bool:
        """Check if verification token is still valid."""
        if not self.verification_token or not self.verification_token_expires:
            return False
        return datetime.now(UTC) < self.verification_token_expires

    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        clinic_name: Optional[str] = None,
        order_number: Optional[str] = None,
        specialty: Optional[str] = None,
        is_student: Optional[bool] = None,
        school_name: Optional[str] = None,
    ) -> None:
        """Update user profile information."""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if clinic_name is not None:
            self.clinic_name = clinic_name
        if order_number is not None:
            self.order_number = order_number
        if specialty is not None:
            self.specialty = specialty
        if is_student is not None:
            self.is_student = is_student
        if school_name is not None:
            self.school_name = school_name

        self.updated_at = datetime.now(UTC)
