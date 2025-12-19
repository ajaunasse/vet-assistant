"""Link session to user command and handler."""
from dataclasses import dataclass

from src.domain.entities import ChatSession
from src.domain.repositories import SessionRepository


@dataclass
class LinkSessionToUserCommand:
    """Command to link a session to a user."""
    session_id: str
    user_id: str


class LinkSessionToUserHandler:
    """Handler for linking sessions to users."""

    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    async def handle(self, command: LinkSessionToUserCommand) -> ChatSession:
        """
        Handle linking a session to a user.

        Args:
            command: Link command with session and user IDs

        Returns:
            Updated session entity

        Raises:
            ValueError: If session not found or already linked
        """
        # Get session
        session = await self.session_repository.get_by_id(command.session_id)
        if not session:
            raise ValueError("Session not found")

        # Check if already linked
        if session.user_id is not None:
            raise ValueError("Session is already linked to a user")

        # Link to user
        session.user_id = command.user_id
        session.touch()

        # Update in database
        session = await self.session_repository.update(session)

        return session
