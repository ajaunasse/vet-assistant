"""Repository interfaces for domain entities."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import ChatSession, ChatMessage, DogBreed, ConsultationReason, User, RefreshToken


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

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[ChatSession]:
        """Get all sessions for a user."""
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


class UserRepository(ABC):
    """Repository interface for users."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass

    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get a user by verification token."""
        pass


class RefreshTokenRepository(ABC):
    """Repository interface for refresh tokens."""

    @abstractmethod
    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Create a new refresh token."""
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get a refresh token by token value."""
        pass

    @abstractmethod
    async def revoke_user_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        pass

    @abstractmethod
    async def delete_expired(self) -> None:
        """Delete all expired refresh tokens."""
        pass