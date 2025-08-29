"""Pydantic schemas for request/response models."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union, Dict, Any

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Request schema for sending a message."""
    message: str = Field(..., min_length=1, max_length=5000)


class CollectionResponse(BaseModel):
    """Response schema for data collection phase."""
    message: str
    response_type: str = "collection"
    questions: List[str] = Field(default_factory=list)
    data_extracted: Dict[str, Any] = Field(default_factory=dict)
    ready_for_diagnosis: bool = False
    confidence_level: str = "medium"


class VeterinaryAssessmentResponse(BaseModel):
    """Response schema for veterinary assessment."""
    assessment: str
    status: str = "processed"  # "processed" or "completed"
    localization: Optional[str] = None
    differentials: List[dict] = Field(default_factory=list)
    diagnostics: List[str] = Field(default_factory=list)
    treatment: str = ""
    prognosis: str = ""
    questions: List[str] = Field(default_factory=list)
    confidence_level: str = "moyenne"


class PatientDataResponse(BaseModel):
    """Response schema for patient data."""
    age: Optional[str] = None
    sex: Optional[str] = None
    race: Optional[str] = None
    weight: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    symptom_duration: Optional[str] = None
    symptom_progression: Optional[str] = None
    neurological_exam: Dict[str, Any] = Field(default_factory=dict)
    other_exams: Dict[str, Any] = Field(default_factory=dict)
    medical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    is_complete: bool = False
    collected_fields: List[str] = Field(default_factory=list)


class ChatMessageResponse(BaseModel):
    """Response schema for chat messages."""
    id: str
    role: str
    content: str
    timestamp: datetime


class SessionResponse(BaseModel):
    """Response schema for chat sessions."""
    id: str
    created_at: datetime
    updated_at: datetime
    current_assessment: Optional[VeterinaryAssessmentResponse] = None
    patient_data: Optional[PatientDataResponse] = None
    is_collecting_data: bool = True


class SessionWithMessagesResponse(BaseModel):
    """Response schema for session with messages."""
    session: SessionResponse
    messages: List[ChatMessageResponse]


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    message: str