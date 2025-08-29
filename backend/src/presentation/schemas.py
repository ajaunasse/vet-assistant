"""Pydantic schemas for request/response models."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Request schema for sending a message."""
    message: str = Field(..., min_length=1, max_length=5000)


class VeterinaryAssessmentResponse(BaseModel):
    """Response schema for veterinary assessment."""
    assessment: str
    localization: Optional[str] = None
    differentials: List[dict] = Field(default_factory=list)
    diagnostics: List[str] = Field(default_factory=list)
    treatment: str
    prognosis: str
    questions: List[str] = Field(default_factory=list)
    confidence_level: str


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


class SessionWithMessagesResponse(BaseModel):
    """Response schema for session with messages."""
    session: SessionResponse
    messages: List[ChatMessageResponse]


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    message: str