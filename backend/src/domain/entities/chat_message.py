"""Chat message entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
import uuid


def generate_id() -> str:
    """Generate a new UUID as string."""
    return str(uuid.uuid4())


@dataclass
class ChatMessage:
    """Chat message entity."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    session_id: str
    status: str | None = None  # "processed" or "completed" for assistant messages
    follow_up_question: str | None = None  # Question de suivi for assistant messages

    @classmethod
    def create_user_message(cls, content: str, session_id: str) -> ChatMessage:
        """Create a new user message."""
        return cls(
            id=generate_id(),
            role="user",
            content=content,
            timestamp=datetime.now(UTC),
            session_id=session_id
        )

    @classmethod
    def create_assistant_message(
        cls,
        content: str,
        session_id: str,
        status: str | None = None,
        follow_up_question: str | None = None
    ) -> ChatMessage:
        """Create a new assistant message."""
        return cls(
            id=generate_id(),
            role="assistant",
            content=content,
            timestamp=datetime.now(UTC),
            session_id=session_id,
            status=status,
            follow_up_question=follow_up_question
        )