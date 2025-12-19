"""Get user sessions query and handler."""
from dataclasses import dataclass
from typing import List

from src.domain.entities import ChatSession
from src.domain.repositories import SessionRepository


@dataclass
class GetUserSessionsQuery:
    """Query to get all sessions for a user."""
    user_id: str


class GetUserSessionsHandler:
    """Handler for getting user sessions."""

    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    async def handle(self, query: GetUserSessionsQuery) -> List[ChatSession]:
        """
        Handle getting user sessions.

        Args:
            query: Query with user ID

        Returns:
            List of session entities for the user
        """
        sessions = await self.session_repository.get_by_user_id(query.user_id)
        return sessions
