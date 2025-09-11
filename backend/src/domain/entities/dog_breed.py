"""Dog breed entity."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DogBreed:
    """Dog breed entity."""
    id: int
    name: str
    created_at: datetime

    def __str__(self) -> str:
        """String representation of the dog breed."""
        return self.name