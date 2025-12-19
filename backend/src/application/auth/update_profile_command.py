"""Update user profile command and handler."""
from dataclasses import dataclass
from typing import Optional

from src.domain.entities import User
from src.domain.repositories import UserRepository


@dataclass
class UpdateProfileCommand:
    """Command to update user profile."""
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    clinic_name: Optional[str] = None
    order_number: Optional[str] = None
    specialty: Optional[str] = None
    is_student: Optional[bool] = None
    school_name: Optional[str] = None


class UpdateProfileHandler:
    """Handler for updating user profile."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: UpdateProfileCommand) -> User:
        """
        Handle profile update.

        Args:
            command: Update command with profile data

        Returns:
            Updated user entity

        Raises:
            ValueError: If user not found
        """
        # Get user
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise ValueError("User not found")

        # Update profile
        user.update_profile(
            first_name=command.first_name,
            last_name=command.last_name,
            clinic_name=command.clinic_name,
            order_number=command.order_number,
            specialty=command.specialty,
            is_student=command.is_student,
            school_name=command.school_name,
        )

        # Save to database
        user = await self.user_repository.update(user)

        return user
