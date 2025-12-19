"""Get user query and handler."""
from dataclasses import dataclass

from src.domain.entities import User
from src.domain.repositories import UserRepository


@dataclass
class GetUserQuery:
    """Query to get user by ID."""
    user_id: str


class GetUserHandler:
    """Handler for getting user."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, query: GetUserQuery) -> User:
        """
        Handle getting user.

        Args:
            query: Query with user ID

        Returns:
            User entity

        Raises:
            ValueError: If user not found
        """
        user = await self.user_repository.get_by_id(query.user_id)
        if not user:
            raise ValueError("User not found")

        return user
