"""Repository interfaces for domain entities."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import ChatSession, ChatMessage


class SessionRepository(ABC):
    """Repository interface for chat sessions."""

    @abstractmethod
    async def create(self, session: ChatSession) -> ChatSession:
        """Create a new chat session."""
        pass

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID."""
        pass

    @abstractmethod
    async def update(self, session: ChatSession) -> ChatSession:
        """Update an existing session."""
        pass


class MessageRepository(ABC):
    """Repository interface for chat messages."""

    @abstractmethod
    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new message."""
        pass

    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session."""
        pass

    @abstractmethod
    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages for a session."""
        pass