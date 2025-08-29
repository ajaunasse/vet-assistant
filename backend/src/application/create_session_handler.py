"""Create session handler."""
from src.domain.entities import ChatSession
from src.domain.repositories import SessionRepository

from .create_session_command import CreateSessionCommand


class CreateSessionHandler:
    """Handler for creating chat sessions."""

    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    async def handle(self, command: CreateSessionCommand) -> ChatSession:
        """Handle the create session command."""
        session = ChatSession.create()
        return await self.session_repository.create(session)