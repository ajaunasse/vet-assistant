"""Resend verification email command and handler."""
from dataclasses import dataclass

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.email import EmailService


@dataclass
class ResendVerificationCommand:
    """Command to resend verification email."""
    email: str


class ResendVerificationHandler:
    """Handler for resending verification email."""

    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.email_service = email_service

    async def handle(self, command: ResendVerificationCommand) -> bool:
        """
        Handle resending verification email.

        Args:
            command: Resend verification command

        Returns:
            True if email was sent successfully

        Raises:
            ValueError: If user not found or already verified
        """
        # Get user by email
        user = await self.user_repository.get_by_email(command.email)
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Check if already verified
        if user.is_verified:
            raise ValueError("Email déjà vérifié")

        # Send verification email
        success = await self.email_service.send_verification_email(
            email=user.email,
            verification_token=user.verification_token,
            first_name=user.first_name,
        )

        if not success:
            raise ValueError("Échec de l'envoi de l'email")

        return True
