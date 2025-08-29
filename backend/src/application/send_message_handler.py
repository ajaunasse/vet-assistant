"""Send message handler."""
from src.domain.entities import ChatMessage, VeterinaryAssessment
from src.domain.repositories import SessionRepository, MessageRepository
from src.infrastructure.ai.ai_service import AIService

from .send_message_command import SendMessageCommand


class SendMessageHandler:
    """Handler for sending messages and getting AI responses."""

    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
        ai_service: AIService,
    ):
        self.session_repository = session_repository
        self.message_repository = message_repository
        self.ai_service = ai_service

    async def handle(self, command: SendMessageCommand) -> VeterinaryAssessment:
        """Handle the send message command."""
        # Get the session
        session = await self.session_repository.get_by_id(command.session_id)
        if not session:
            raise ValueError(f"Session {command.session_id} not found")

        # Create and save user message
        user_message = ChatMessage.create_user_message(
            content=command.message,
            session_id=command.session_id
        )
        await self.message_repository.create(user_message)

        # Get message history for AI context
        messages = await self.message_repository.get_recent_messages(
            command.session_id, limit=20
        )

        # Process message using your OpenAI assistant
        assessment = await self.ai_service.process_message(messages, session)

        # Create and save assistant message
        assistant_message = ChatMessage.create_assistant_message(
            content=f"Assessment: {assessment.assessment}",
            session_id=command.session_id
        )
        await self.message_repository.create(assistant_message)

        # Update session with current assessment
        session.update_assessment(assessment)
        await self.session_repository.update(session)

        return assessment