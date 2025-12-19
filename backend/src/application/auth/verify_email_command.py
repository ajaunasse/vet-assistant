"""Verify email command and handler."""
from dataclasses import dataclass

from src.domain.entities import User
from src.domain.repositories import UserRepository


@dataclass
class VerifyEmailCommand:
    """Command to verify user email."""
    token: str


class VerifyEmailHandler:
    """Handler for email verification."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: VerifyEmailCommand) -> User:
        """
        Handle email verification.

        Args:
            command: Verification command with token

        Returns:
            Verified user entity

        Raises:
            ValueError: If token is invalid or expired
        """
        # Get user by verification token
        user = await self.user_repository.get_by_verification_token(command.token)
        if not user:
            raise ValueError("Invalid verification token")

        # Check if already verified
        if user.is_verified:
            return user

        # Check if token is still valid
        if not user.is_verification_token_valid():
            raise ValueError("Verification token has expired. Please request a new one.")

        # Verify email
        user.verify_email()

        # Update user in database
        user = await self.user_repository.update(user)

        return user
