"""FastAPI router for the NeuroVet API."""
import os
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application import (
    CreateSessionCommand,
    SendMessageCommand,
    GetSessionQuery,
    GetSessionMessagesQuery,
    CreateSessionHandler,
    SendMessageHandler,
    GetSessionHandler,
    GetSessionMessagesHandler,
)
from src.domain.entities import VeterinaryAssessment, CollectionResponse as DomainCollectionResponse
from src.infrastructure.database import get_database_session
from src.infrastructure import SQLSessionRepository, SQLMessageRepository, SQLDogBreedRepository, SQLConsultationReasonRepository, AIService

from .schemas import (
    SendMessageRequest,
    VeterinaryAssessmentResponse,
    CollectionResponse,
    PatientDataResponse,
    PatientDataRequest,
    SessionResponse,
    SessionWithMessagesResponse,
    ChatMessageResponse,
    HealthResponse,
    DogBreedResponse,
    ConsultationReasonResponse,
)


router = APIRouter()


# Dependencies
def get_ai_service() -> AIService:
    """Get AI service instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "demo_key":
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        )

    prompt_id = os.getenv("OPENAI_PROMPT_ID")
    if not prompt_id or prompt_id == "pmpt_demo":
        raise HTTPException(
            status_code=500,
            detail="OpenAI Prompt ID not configured. Please set OPENAI_PROMPT_ID environment variable."
        )

    prompt_version = os.getenv("OPENAI_PROMPT_VERSION", "6")
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")
    temperature = float(os.getenv("TEMPERATURE", "0.3"))
    max_tokens = int(os.getenv("MAX_TOKENS", "2000"))

    try:
        return AIService(api_key, prompt_id, prompt_version, model, temperature, max_tokens)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize AI service: {str(e)}"
        )


def get_create_session_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> CreateSessionHandler:
    """Get create session handler."""
    session_repo = SQLSessionRepository(db_session)
    return CreateSessionHandler(session_repo)


def get_send_message_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
    ai_service: Annotated[AIService, Depends(get_ai_service)],
) -> SendMessageHandler:
    """Get send message handler."""
    session_repo = SQLSessionRepository(db_session)
    message_repo = SQLMessageRepository(db_session)
    return SendMessageHandler(session_repo, message_repo, ai_service)


def get_session_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GetSessionHandler:
    """Get session handler."""
    session_repo = SQLSessionRepository(db_session)
    message_repo = SQLMessageRepository(db_session)
    return GetSessionHandler(session_repo, message_repo)


def get_session_messages_handler(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> GetSessionMessagesHandler:
    """Get session messages handler."""
    message_repo = SQLMessageRepository(db_session)
    return GetSessionMessagesHandler(message_repo)


def get_dog_breed_repository(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> SQLDogBreedRepository:
    """Get dog breed repository."""
    return SQLDogBreedRepository(db_session)


def get_consultation_reason_repository(
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> SQLConsultationReasonRepository:
    """Get consultation reason repository."""
    return SQLConsultationReasonRepository(db_session)


# API Endpoints
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Veterinary Neurological Diagnostic Assistant API is running"
    )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    handler: Annotated[CreateSessionHandler, Depends(get_create_session_handler)],
) -> SessionResponse:
    """Create a new chat session."""
    command = CreateSessionCommand()
    session = await handler.handle(command)
    
    patient_data = None
    if session.patient_data:
        patient_data = PatientDataResponse(**session.patient_data.to_dict())
    
    return SessionResponse(
        id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        slug=session.slug,
        current_assessment=None,
        patient_data=patient_data,
        is_collecting_data=session.is_collecting_data,
    )


@router.post("/sessions/{session_id}/messages", response_model=VeterinaryAssessmentResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    handler: Annotated[SendMessageHandler, Depends(get_send_message_handler)],
) -> VeterinaryAssessmentResponse:
    """Send a message and get AI assessment."""
    try:
        command = SendMessageCommand(session_id=session_id, message=request.message)
        assessment = await handler.handle(command)

        # Convert patient_data: if it's a list or empty, set to None
        # The schema expects a dict (PatientDataAI) or None
        patient_data_response = None
        if assessment.patient_data and isinstance(assessment.patient_data, dict):
            patient_data_response = assessment.patient_data

        return VeterinaryAssessmentResponse(
            assessment=assessment.assessment,
            status=assessment.status,
            localization=assessment.localization,
            differentials=assessment.differentials,
            diagnostics=assessment.diagnostics,
            treatment=assessment.treatment,
            prognosis=assessment.prognosis,
            patient_data=patient_data_response,
            question=assessment.question,
            confidence_level=assessment.confidence_level,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionWithMessagesResponse)
async def get_session(
    session_id: str,
    handler: Annotated[GetSessionHandler, Depends(get_session_handler)],
) -> SessionWithMessagesResponse:
    """Get session details with messages."""
    try:
        session, messages = await handler.handle(GetSessionQuery(session_id=session_id))
        
        # Convert assessment if present
        current_assessment = None
        if session.current_assessment:
            # Convert patient_data: if it's a list or empty, set to None
            patient_data_value = getattr(session.current_assessment, 'patient_data', None)
            patient_data_response = None
            if patient_data_value and isinstance(patient_data_value, dict):
                patient_data_response = patient_data_value

            current_assessment = VeterinaryAssessmentResponse(
                assessment=session.current_assessment.assessment,
                status=session.current_assessment.status,
                localization=session.current_assessment.localization,
                differentials=session.current_assessment.differentials,
                diagnostics=session.current_assessment.diagnostics,
                treatment=session.current_assessment.treatment,
                prognosis=session.current_assessment.prognosis,
                patient_data=patient_data_response,
                question=getattr(session.current_assessment, 'question', ''),
                confidence_level=session.current_assessment.confidence_level,
            )

        patient_data = None
        if session.patient_data:
            patient_data = PatientDataResponse(**session.patient_data.to_dict())

        return SessionWithMessagesResponse(
            session=SessionResponse(
                id=session.id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                slug=session.slug,
                current_assessment=current_assessment,
                patient_data=patient_data,
                is_collecting_data=session.is_collecting_data,
            ),
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    status=msg.status,
                    follow_up_question=msg.follow_up_question,
                )
                for msg in messages
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions/{session_id}/patient-data", response_model=PatientDataResponse)
async def get_patient_data(
    session_id: str,
    handler: Annotated[GetSessionHandler, Depends(get_session_handler)],
) -> PatientDataResponse:
    """Get collected patient data for a session."""
    try:
        session, _ = await handler.handle(GetSessionQuery(session_id=session_id))
        
        if session.patient_data:
            return PatientDataResponse(**session.patient_data.to_dict())
        else:
            return PatientDataResponse()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/patient-data", response_model=PatientDataResponse)
async def save_patient_data(
    session_id: str,
    request: PatientDataRequest,
    db_session: Annotated[AsyncSession, Depends(get_database_session)],
) -> PatientDataResponse:
    """Save patient data from pre-consultation form."""
    try:
        session_repo = SQLSessionRepository(db_session)
        session = await session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session with id '{session_id}' not found")
        
        # Initialize patient data if not exists
        if not session.patient_data:
            from src.domain.entities import PatientData
            session.patient_data = PatientData()
        
        # Convert form data to patient data structure
        sex_str = f"{request.sexe.lower()} {'castré' if request.castre and request.sexe.lower() == 'mâle' else 'stérilisé' if request.castre and request.sexe.lower() == 'femelle' else 'entier' if not request.castre else ''}"
        
        session.patient_data.set_basic_info(
            race=request.race,
            age=request.age,
            sex=sex_str
        )
        
        # Add symptoms and examination data
        if request.premiers_symptomes:
            session.patient_data.add_symptom(f"Premiers symptômes: {request.premiers_symptomes}")
        
        if request.examens_realises:
            session.patient_data.add_exam_result("examens_realises", request.examens_realises)
        
        # Add neurological exam data
        session.patient_data.add_exam_result("neuro_etat_conscience", request.etat_conscience)
        session.patient_data.add_exam_result("neuro_comportement", request.comportement)
        session.patient_data.add_exam_result("neuro_convulsions", request.convulsions)
        session.patient_data.add_exam_result("motif_consultation", request.motif_consultation)
        
        # Mark session as updated
        session.update_patient_data(session.patient_data)
        
        # Save to database
        await session_repo.update(session)
        
        return PatientDataResponse(**session.patient_data.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/sessions/{session_id}/patient-data")
async def clear_patient_data(
    session_id: str,
    handler: Annotated[GetSessionHandler, Depends(get_session_handler)],
) -> dict:
    """Clear collected patient data for a session."""
    try:
        session, _ = await handler.handle(GetSessionQuery(session_id=session_id))
        
        # Clear patient data
        from src.domain.entities import PatientData
        session.patient_data = PatientData()
        
        # Save changes
        session_repo = SQLSessionRepository(get_database_session().__anext__().__await__().__next__())
        await session_repo.update(session)
        
        return {"message": "Patient data cleared successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/dog-breeds", response_model=List[DogBreedResponse])
async def get_dog_breeds(
    dog_breed_repo: Annotated[SQLDogBreedRepository, Depends(get_dog_breed_repository)],
) -> List[DogBreedResponse]:
    """Get all dog breeds."""
    try:
        breeds = await dog_breed_repo.get_all()
        return [
            DogBreedResponse(
                id=breed.id,
                name=breed.name,
                created_at=breed.created_at,
            )
            for breed in breeds
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/consultation-reasons", response_model=List[ConsultationReasonResponse])
async def get_consultation_reasons(
    consultation_reason_repo: Annotated[SQLConsultationReasonRepository, Depends(get_consultation_reason_repository)],
) -> List[ConsultationReasonResponse]:
    """Get all consultation reasons."""
    try:
        reasons = await consultation_reason_repo.get_all()
        return [
            ConsultationReasonResponse(
                id=reason.id,
                name=reason.name,
                description=reason.description,
                created_at=reason.created_at,
            )
            for reason in reasons
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sessions/slug/{slug}", response_model=SessionWithMessagesResponse)
async def get_session_by_slug(
    slug: str,
    handler: Annotated[GetSessionHandler, Depends(get_session_handler)],
) -> SessionWithMessagesResponse:
    """Get session details by slug with messages."""
    try:
        from src.application import GetSessionBySlugQuery
        session, messages = await handler.handle_by_slug(GetSessionBySlugQuery(slug=slug))
        
        # Convert assessment if present
        current_assessment = None
        if session.current_assessment:
            # Convert patient_data: if it's a list or empty, set to None
            patient_data_value = getattr(session.current_assessment, 'patient_data', None)
            patient_data_response = None
            if patient_data_value and isinstance(patient_data_value, dict):
                patient_data_response = patient_data_value

            current_assessment = VeterinaryAssessmentResponse(
                assessment=session.current_assessment.assessment,
                status=session.current_assessment.status,
                localization=session.current_assessment.localization,
                differentials=session.current_assessment.differentials,
                diagnostics=session.current_assessment.diagnostics,
                treatment=session.current_assessment.treatment,
                prognosis=session.current_assessment.prognosis,
                patient_data=patient_data_response,
                question=getattr(session.current_assessment, 'question', ''),
                confidence_level=session.current_assessment.confidence_level,
            )

        patient_data = None
        if session.patient_data:
            patient_data = PatientDataResponse(**session.patient_data.to_dict())

        return SessionWithMessagesResponse(
            session=SessionResponse(
                id=session.id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                slug=session.slug,
                current_assessment=current_assessment,
                patient_data=patient_data,
                is_collecting_data=session.is_collecting_data,
            ),
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    status=msg.status,
                    follow_up_question=msg.follow_up_question,
                )
                for msg in messages
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))