"""Get session messages query."""
from dataclasses import dataclass


@dataclass
class GetSessionMessagesQuery:
    """Query to get all messages for a session."""
    session_id: str