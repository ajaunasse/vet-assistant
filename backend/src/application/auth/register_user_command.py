"""Register user command and handler."""
from dataclasses import dataclass
from typing import Optional

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.security import PasswordService
from src.infrastructure.email import EmailService


@dataclass
class RegisterUserCommand:
    """Command to register a new user."""
    email: str
    password: str
    first_name: str
    last_name: str
    clinic_name: Optional[str] = None
    order_number: Optional[str] = None
    specialty: Optional[str] = None
    is_student: bool = False
    school_name: Optional[str] = None


class RegisterUserHandler:
    """Handler for user registration."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.email_service = email_service

    async def handle(self, command: RegisterUserCommand) -> User:
        """
        Handle user registration.

        Args:
            command: Registration command with user data

        Returns:
            Created user entity

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(command.email)
        if existing_user:
            raise ValueError(f"User with email {command.email} already exists")

        # Hash password
        hashed_password = self.password_service.hash_password(command.password)

        # Create user entity
        user = User.create(
            email=command.email,
            hashed_password=hashed_password,
            first_name=command.first_name,
            last_name=command.last_name,
            clinic_name=command.clinic_name,
            order_number=command.order_number,
            specialty=command.specialty,
            is_student=command.is_student,
            school_name=command.school_name,
        )

        # Save to database
        user = await self.user_repository.create(user)

        # Send verification email
        if user.verification_token:
            await self.email_service.send_verification_email(
                email=user.email,
                verification_token=user.verification_token,
                first_name=user.first_name,
            )

        return user
