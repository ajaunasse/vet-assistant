"""Consultation reason entity."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ConsultationReason:
    """Consultation reason entity."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    def __str__(self) -> str:
        """String representation of the consultation reason."""
        return self.name