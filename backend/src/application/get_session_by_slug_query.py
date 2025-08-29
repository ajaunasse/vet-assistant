"""Get session by slug query."""
from dataclasses import dataclass


@dataclass
class GetSessionBySlugQuery:
    """Query to get a chat session by its slug."""
    slug: str