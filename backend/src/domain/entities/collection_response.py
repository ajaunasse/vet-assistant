"""Collection response entity for data gathering phase."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ResponseType(Enum):
    """Type of response from the AI assistant."""
    COLLECTION = "collection"
    DIAGNOSTIC = "diagnostic"


@dataclass
class CollectionResponse:
    """Response from AI during data collection phase."""
    message: str
    response_type: ResponseType
    questions: List[str] = field(default_factory=list)
    data_extracted: Dict[str, Any] = field(default_factory=dict)
    ready_for_diagnosis: bool = False
    confidence_level: str = "medium"
    
    def add_question(self, question: str) -> None:
        """Add a question to ask the user."""
        if question not in self.questions:
            self.questions.append(question)
    
    def add_extracted_data(self, field: str, value: Any) -> None:
        """Add extracted data from user response."""
        self.data_extracted[field] = value
    
    def mark_ready_for_diagnosis(self) -> None:
        """Mark that we have enough data for diagnosis."""
        self.ready_for_diagnosis = True
        self.response_type = ResponseType.DIAGNOSTIC