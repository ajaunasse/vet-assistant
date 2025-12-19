"""Get session handler."""
from typing import List, Tuple

from src.domain.entities import ChatSession, ChatMessage
from src.domain.repositories import SessionRepository, MessageRepository

from .get_session_query import GetSessionQuery
from .get_session_by_slug_query import GetSessionBySlugQuery


class GetSessionHandler:
    """Handler for getting session details."""

    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
    ):
        self.session_repository = session_repository
        self.message_repository = message_repository

    async def handle(self, query: GetSessionQuery) -> Tuple[ChatSession, List[ChatMessage]]:
        """Handle the get session query."""
        session = await self.session_repository.get_by_id(query.session_id)
        if not session:
            raise ValueError(f"Session {query.session_id} not found")

        messages = await self.message_repository.get_by_session_id(query.session_id)
        return session, messages
    
    async def handle_by_slug(self, query: GetSessionBySlugQuery) -> Tuple[ChatSession, List[ChatMessage]]:
        """Handle the get session by slug query."""
        session = await self.session_repository.get_by_slug(query.slug)
        if not session:
            raise ValueError(f"Session with slug '{query.slug}' not found")

        messages = await self.message_repository.get_by_session_id(session.id)
        return session, messages