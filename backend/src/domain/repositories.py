"""Repository interfaces for domain entities."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import ChatSession, ChatMessage, DogBreed, ConsultationReason


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

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[ChatSession]:
        """Get a session by slug."""
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


class DogBreedRepository(ABC):
    """Repository interface for dog breeds."""

    @abstractmethod
    async def get_all(self) -> List[DogBreed]:
        """Get all dog breeds."""
        pass

    @abstractmethod
    async def get_by_id(self, breed_id: int) -> Optional[DogBreed]:
        """Get a dog breed by ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[DogBreed]:
        """Get a dog breed by name."""
        pass


class ConsultationReasonRepository(ABC):
    """Repository interface for consultation reasons."""

    @abstractmethod
    async def get_all(self) -> List[ConsultationReason]:
        """Get all consultation reasons."""
        pass

    @abstractmethod
    async def get_by_id(self, reason_id: int) -> Optional[ConsultationReason]:
        """Get a consultation reason by ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ConsultationReason]:
        """Get a consultation reason by name."""
        pass