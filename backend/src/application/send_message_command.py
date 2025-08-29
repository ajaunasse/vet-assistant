"""Send message command."""
from dataclasses import dataclass


@dataclass
class SendMessageCommand:
    """Command to send a message in a chat session."""
    session_id: str
    message: str