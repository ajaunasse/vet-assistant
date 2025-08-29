"""Get session messages handler."""
from typing import List

from src.domain.entities import ChatMessage
from src.domain.repositories import MessageRepository

from .get_session_messages_query import GetSessionMessagesQuery


class GetSessionMessagesHandler:
    """Handler for getting session messages."""

    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def handle(self, query: GetSessionMessagesQuery) -> List[ChatMessage]:
        """Handle the get session messages query."""
        return await self.message_repository.get_by_session_id(query.session_id)