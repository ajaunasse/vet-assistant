"""Repository implementations for domain entities."""
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import ChatSession, ChatMessage, VeterinaryAssessment, PatientData
from src.domain.repositories import SessionRepository, MessageRepository

from .database import SessionModel, MessageModel


def _session_to_entity(model: SessionModel) -> ChatSession:
    """Convert session model to entity."""
    current_assessment = None
    if model.current_assessment:
        current_assessment = VeterinaryAssessment(**model.current_assessment)
    
    patient_data = None
    if model.patient_data:
        patient_data = PatientData.from_dict(model.patient_data)

    return ChatSession(
        id=model.id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        current_assessment=current_assessment,
        openai_thread_id=model.openai_thread_id,
        patient_data=patient_data,
        is_collecting_data=model.is_collecting_data if hasattr(model, 'is_collecting_data') else True,
    )


def _entity_to_session_model(entity: ChatSession) -> SessionModel:
    """Convert session entity to model."""
    current_assessment_dict = None
    if entity.current_assessment:
        current_assessment_dict = {
            "assessment": entity.current_assessment.assessment,
            "status": entity.current_assessment.status,
            "localization": entity.current_assessment.localization,
            "differentials": entity.current_assessment.differentials,
            "diagnostics": entity.current_assessment.diagnostics,
            "treatment": entity.current_assessment.treatment,
            "prognosis": entity.current_assessment.prognosis,
            "questions": entity.current_assessment.questions,
            "confidence_level": entity.current_assessment.confidence_level,
        }

    patient_data_dict = None
    if entity.patient_data:
        patient_data_dict = entity.patient_data.to_dict()

    return SessionModel(
        id=entity.id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        current_assessment=current_assessment_dict,
        openai_thread_id=entity.openai_thread_id,
        patient_data=patient_data_dict,
        is_collecting_data=entity.is_collecting_data,
    )


def _message_to_entity(model: MessageModel) -> ChatMessage:
    """Convert message model to entity."""
    return ChatMessage(
        id=model.id,
        session_id=model.session_id,
        role=model.role,
        content=model.content,
        timestamp=model.timestamp,
    )


def _entity_to_message_model(entity: ChatMessage) -> MessageModel:
    """Convert message entity to model."""
    return MessageModel(
        id=entity.id,
        session_id=entity.session_id,
        role=entity.role,
        content=entity.content,
        timestamp=entity.timestamp,
    )


class SQLSessionRepository(SessionRepository):
    """SQLAlchemy implementation of SessionRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, session_entity: ChatSession) -> ChatSession:
        """Create a new chat session."""
        model = _entity_to_session_model(session_entity)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _session_to_entity(model)

    async def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID."""
        stmt = select(SessionModel).where(SessionModel.id == session_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _session_to_entity(model) if model else None

    async def update(self, session_entity: ChatSession) -> ChatSession:
        """Update an existing session."""
        stmt = select(SessionModel).where(SessionModel.id == session_entity.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Session {session_entity.id} not found")

        # Update fields
        model.updated_at = session_entity.updated_at
        model.openai_thread_id = session_entity.openai_thread_id
        model.is_collecting_data = session_entity.is_collecting_data
        
        if session_entity.current_assessment:
            model.current_assessment = {
                "assessment": session_entity.current_assessment.assessment,
                "status": session_entity.current_assessment.status,
                "localization": session_entity.current_assessment.localization,
                "differentials": session_entity.current_assessment.differentials,
                "diagnostics": session_entity.current_assessment.diagnostics,
                "treatment": session_entity.current_assessment.treatment,
                "prognosis": session_entity.current_assessment.prognosis,
                "questions": session_entity.current_assessment.questions,
                "confidence_level": session_entity.current_assessment.confidence_level,
            }
        
        if session_entity.patient_data:
            model.patient_data = session_entity.patient_data.to_dict()

        await self.session.flush()
        await self.session.refresh(model)
        return _session_to_entity(model)


class SQLMessageRepository(MessageRepository):
    """SQLAlchemy implementation of MessageRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: ChatMessage) -> ChatMessage:
        """Create a new message."""
        model = _entity_to_message_model(message)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _message_to_entity(model)

    async def get_by_session_id(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session."""
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.timestamp)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_message_to_entity(model) for model in models]

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages for a session."""
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(desc(MessageModel.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        # Reverse to get chronological order
        return [_message_to_entity(model) for model in reversed(models)]