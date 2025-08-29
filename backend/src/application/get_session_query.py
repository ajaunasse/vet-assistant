"""Get session query."""
from dataclasses import dataclass


@dataclass
class GetSessionQuery:
    """Query to get a chat session with its messages."""
    session_id: str