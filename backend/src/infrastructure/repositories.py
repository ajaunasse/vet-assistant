"""Repository implementations for domain entities."""
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import ChatSession, ChatMessage, VeterinaryAssessment, PatientData, DogBreed, ConsultationReason, User, RefreshToken
from src.domain.repositories import SessionRepository, MessageRepository, DogBreedRepository, ConsultationReasonRepository, UserRepository, RefreshTokenRepository

from .database import SessionModel, MessageModel, DogBreedModel, ConsultationReasonModel, UserModel, RefreshTokenModel


def _session_to_entity(model: SessionModel) -> ChatSession:
    """Convert session model to entity."""
    current_assessment = None
    if model.current_assessment:
        # Handle backward compatibility for field name changes
        assessment_data = dict(model.current_assessment)
        
        # Convert old 'questions' field to new 'question' field if exists
        if 'questions' in assessment_data:
            if isinstance(assessment_data['questions'], list) and assessment_data['questions']:
                assessment_data['question'] = assessment_data['questions'][0]  # Take first question
            else:
                assessment_data['question'] = ""
            del assessment_data['questions']
        
        # Ensure required fields have default values
        assessment_data.setdefault('question', "")
        assessment_data.setdefault('patient_data', [])
        
        current_assessment = VeterinaryAssessment(**assessment_data)
    
    patient_data = None
    if model.patient_data:
        patient_data = PatientData.from_dict(model.patient_data)

    return ChatSession(
        id=model.id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        slug=model.slug if hasattr(model, 'slug') else None,
        current_assessment=current_assessment,
        openai_thread_id=model.openai_thread_id,
        patient_data=patient_data,
        is_collecting_data=model.is_collecting_data if hasattr(model, 'is_collecting_data') else True,
        user_id=model.user_id if hasattr(model, 'user_id') else None,
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
            "question": entity.current_assessment.question,
            "patient_data": entity.current_assessment.patient_data,
            "confidence_level": entity.current_assessment.confidence_level,
        }

    patient_data_dict = None
    if entity.patient_data:
        patient_data_dict = entity.patient_data.to_dict()

    return SessionModel(
        id=entity.id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        slug=entity.slug,
        current_assessment=current_assessment_dict,
        openai_thread_id=entity.openai_thread_id,
        patient_data=patient_data_dict,
        is_collecting_data=entity.is_collecting_data,
        user_id=entity.user_id,
    )


def _message_to_entity(model: MessageModel) -> ChatMessage:
    """Convert message model to entity."""
    return ChatMessage(
        id=model.id,
        session_id=model.session_id,
        role=model.role,
        content=model.content,
        timestamp=model.timestamp,
        status=model.status if hasattr(model, 'status') else None,
        follow_up_question=model.follow_up_question if hasattr(model, 'follow_up_question') else None,
    )


def _entity_to_message_model(entity: ChatMessage) -> MessageModel:
    """Convert message entity to model."""
    return MessageModel(
        id=entity.id,
        session_id=entity.session_id,
        role=entity.role,
        content=entity.content,
        timestamp=entity.timestamp,
        status=entity.status,
        follow_up_question=entity.follow_up_question,
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

    async def get_by_slug(self, slug: str) -> Optional[ChatSession]:
        """Get a session by slug."""
        stmt = select(SessionModel).where(SessionModel.slug == slug)
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
        model.slug = session_entity.slug
        model.openai_thread_id = session_entity.openai_thread_id
        model.is_collecting_data = session_entity.is_collecting_data
        model.user_id = session_entity.user_id
        
        if session_entity.current_assessment:
            model.current_assessment = {
                "assessment": session_entity.current_assessment.assessment,
                "status": session_entity.current_assessment.status,
                "localization": session_entity.current_assessment.localization,
                "differentials": session_entity.current_assessment.differentials,
                "diagnostics": session_entity.current_assessment.diagnostics,
                "treatment": session_entity.current_assessment.treatment,
                "prognosis": session_entity.current_assessment.prognosis,
                "question": session_entity.current_assessment.question,
                "patient_data": session_entity.current_assessment.patient_data,
                "confidence_level": session_entity.current_assessment.confidence_level,
            }
        
        if session_entity.patient_data:
            model.patient_data = session_entity.patient_data.to_dict()

        await self.session.flush()
        await self.session.refresh(model)
        return _session_to_entity(model)

    async def get_by_user_id(self, user_id: str) -> List[ChatSession]:
        """Get all sessions for a user."""
        stmt = (
            select(SessionModel)
            .where(SessionModel.user_id == user_id)
            .order_by(desc(SessionModel.updated_at))
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_session_to_entity(model) for model in models]


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


def _dog_breed_to_entity(model: DogBreedModel) -> DogBreed:
    """Convert dog breed model to entity."""
    return DogBreed(
        id=model.id,
        name=model.name,
        created_at=model.created_at,
    )


def _consultation_reason_to_entity(model: ConsultationReasonModel) -> ConsultationReason:
    """Convert consultation reason model to entity."""
    return ConsultationReason(
        id=model.id,
        name=model.name,
        description=model.description,
        created_at=model.created_at,
    )


class SQLDogBreedRepository(DogBreedRepository):
    """SQLAlchemy implementation of DogBreedRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[DogBreed]:
        """Get all dog breeds."""
        stmt = select(DogBreedModel).order_by(DogBreedModel.name)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_dog_breed_to_entity(model) for model in models]

    async def get_by_id(self, breed_id: int) -> Optional[DogBreed]:
        """Get a dog breed by ID."""
        stmt = select(DogBreedModel).where(DogBreedModel.id == breed_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _dog_breed_to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[DogBreed]:
        """Get a dog breed by name."""
        stmt = select(DogBreedModel).where(DogBreedModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _dog_breed_to_entity(model) if model else None


class SQLConsultationReasonRepository(ConsultationReasonRepository):
    """SQLAlchemy implementation of ConsultationReasonRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[ConsultationReason]:
        """Get all consultation reasons."""
        stmt = select(ConsultationReasonModel).order_by(ConsultationReasonModel.name)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [_consultation_reason_to_entity(model) for model in models]

    async def get_by_id(self, reason_id: int) -> Optional[ConsultationReason]:
        """Get a consultation reason by ID."""
        stmt = select(ConsultationReasonModel).where(ConsultationReasonModel.id == reason_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _consultation_reason_to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Optional[ConsultationReason]:
        """Get a consultation reason by name."""
        stmt = select(ConsultationReasonModel).where(ConsultationReasonModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _consultation_reason_to_entity(model) if model else None


def _user_to_entity(model: UserModel) -> User:
    """Convert user model to entity."""
    from datetime import UTC

    # MySQL returns naive datetimes, so we need to add UTC timezone
    verification_token_expires = None
    if model.verification_token_expires:
        verification_token_expires = model.verification_token_expires.replace(tzinfo=UTC)

    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        first_name=model.first_name,
        last_name=model.last_name,
        clinic_name=model.clinic_name,
        order_number=model.order_number,
        specialty=model.specialty,
        is_student=model.is_student,
        school_name=model.school_name,
        is_verified=model.is_verified,
        verification_token=model.verification_token,
        verification_token_expires=verification_token_expires,
        created_at=model.created_at.replace(tzinfo=UTC),
        updated_at=model.updated_at.replace(tzinfo=UTC),
    )


def _entity_to_user_model(entity: User) -> UserModel:
    """Convert user entity to model."""
    # Remove timezone info for MySQL storage (MySQL doesn't store timezone info)
    verification_token_expires = None
    if entity.verification_token_expires:
        verification_token_expires = entity.verification_token_expires.replace(tzinfo=None)

    return UserModel(
        id=entity.id,
        email=entity.email,
        hashed_password=entity.hashed_password,
        first_name=entity.first_name,
        last_name=entity.last_name,
        clinic_name=entity.clinic_name,
        order_number=entity.order_number,
        specialty=entity.specialty,
        is_student=entity.is_student,
        school_name=entity.school_name,
        is_verified=entity.is_verified,
        verification_token=entity.verification_token,
        verification_token_expires=verification_token_expires,
        created_at=entity.created_at.replace(tzinfo=None),
        updated_at=entity.updated_at.replace(tzinfo=None),
    )


def _refresh_token_to_entity(model: RefreshTokenModel) -> RefreshToken:
    """Convert refresh token model to entity."""
    from datetime import UTC

    # MySQL returns naive datetimes, so we need to add UTC timezone
    return RefreshToken(
        id=model.id,
        user_id=model.user_id,
        token=model.token,
        expires_at=model.expires_at.replace(tzinfo=UTC),
        created_at=model.created_at.replace(tzinfo=UTC),
        revoked=model.revoked,
    )


def _entity_to_refresh_token_model(entity: RefreshToken) -> RefreshTokenModel:
    """Convert refresh token entity to model."""
    # Remove timezone info for MySQL storage (MySQL doesn't store timezone info)
    return RefreshTokenModel(
        id=entity.id,
        user_id=entity.user_id,
        token=entity.token,
        expires_at=entity.expires_at.replace(tzinfo=None),
        created_at=entity.created_at.replace(tzinfo=None),
        revoked=entity.revoked,
    )


class SQLUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = _entity_to_user_model(user)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _user_to_entity(model)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _user_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _user_to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update an existing user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"User {user.id} not found")

        # Update fields
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.clinic_name = user.clinic_name
        model.order_number = user.order_number
        model.specialty = user.specialty
        model.is_student = user.is_student
        model.school_name = user.school_name
        model.is_verified = user.is_verified
        model.verification_token = user.verification_token
        model.verification_token_expires = user.verification_token_expires
        model.updated_at = user.updated_at

        await self.session.flush()
        await self.session.refresh(model)
        return _user_to_entity(model)

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get a user by verification token."""
        stmt = select(UserModel).where(UserModel.verification_token == token)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _user_to_entity(model) if model else None


class SQLRefreshTokenRepository(RefreshTokenRepository):
    """SQLAlchemy implementation of RefreshTokenRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Create a new refresh token."""
        model = _entity_to_refresh_token_model(refresh_token)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _refresh_token_to_entity(model)

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get a refresh token by token value."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _refresh_token_to_entity(model) if model else None

    async def revoke_user_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        for model in models:
            model.revoked = True

        await self.session.flush()

    async def delete_expired(self) -> None:
        """Delete all expired refresh tokens."""
        from datetime import datetime, UTC
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.expires_at < datetime.now(UTC))
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        for model in models:
            await self.session.delete(model)

        await self.session.flush()