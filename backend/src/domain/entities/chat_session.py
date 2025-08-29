"""Chat session entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .veterinary_assessment import VeterinaryAssessment


def generate_id() -> str:
    """Generate a new UUID as string."""
    return str(uuid.uuid4())


@dataclass
class ChatSession:
    """Chat session entity with behavior."""
    id: str
    created_at: datetime
    updated_at: datetime
    current_assessment: Optional["VeterinaryAssessment"] = None
    openai_thread_id: Optional[str] = None

    @classmethod
    def create(cls) -> ChatSession:
        """Create a new chat session."""
        now = datetime.now(UTC)
        return cls(
            id=generate_id(),
            created_at=now,
            updated_at=now
        )

    def update_assessment(self, assessment: "VeterinaryAssessment") -> None:
        """Update the current assessment."""
        self.current_assessment = assessment
        self.updated_at = datetime.now(UTC)

    def touch(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now(UTC)

    def set_openai_thread(self, thread_id: str) -> None:
        """Set the OpenAI thread ID for this session."""
        self.openai_thread_id = thread_id
        self.updated_at = datetime.now(UTC)