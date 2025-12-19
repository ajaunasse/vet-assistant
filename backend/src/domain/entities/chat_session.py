"""Chat session entity."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional, TYPE_CHECKING
import uuid
import re
import random

if TYPE_CHECKING:
    from .veterinary_assessment import VeterinaryAssessment
    from .patient_data import PatientData


def generate_id() -> str:
    """Generate a new UUID as string."""
    return str(uuid.uuid4())


def generate_slug_from_text(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    # Remove special characters and normalize
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    # Limit length and clean edges
    slug = text[:50].strip('-')
    
    # If slug is too short or empty, generate a random one
    if len(slug) < 3:
        slug = f"consultation-{random.randint(1000, 9999)}"
    
    # Add random suffix to ensure uniqueness
    suffix = random.randint(100, 999)
    return f"{slug}-{suffix}"


@dataclass
class ChatSession:
    """Chat session entity with behavior."""
    id: str
    created_at: datetime
    updated_at: datetime
    slug: Optional[str] = None
    current_assessment: Optional["VeterinaryAssessment"] = None
    openai_thread_id: Optional[str] = None
    patient_data: Optional["PatientData"] = None
    is_collecting_data: bool = True
    user_id: Optional[str] = None

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
    
    def update_patient_data(self, patient_data: "PatientData") -> None:
        """Update patient data."""
        self.patient_data = patient_data
        self.updated_at = datetime.now(UTC)
        
        # Switch to diagnostic phase if data is complete
        if patient_data and patient_data.is_complete:
            self.is_collecting_data = False
    
    def start_diagnosis_phase(self) -> None:
        """Start the diagnosis phase."""
        self.is_collecting_data = False
        self.updated_at = datetime.now(UTC)
    
    def generate_slug_from_message(self, message: str) -> None:
        """Generate and set slug from first user message."""
        if not self.slug:  # Only generate if not already set
            self.slug = generate_slug_from_text(message)
            self.updated_at = datetime.now(UTC)