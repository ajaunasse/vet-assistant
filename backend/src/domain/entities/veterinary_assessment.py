"""Veterinary assessment entity."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VeterinaryAssessment:
    """Veterinary assessment entity with rich domain logic."""
    assessment: str
    status: str = "processed"  # "processed" or "completed"
    localization: Optional[str] = None
    differentials: List[dict] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    treatment: str = ""
    prognosis: str = ""
    patient_data: List[str] = field(default_factory=list)
    question: str = ""
    confidence_level: str = "moyenne"

    def add_differential(self, condition: str, probability: str, rationale: str) -> None:
        """Add a differential diagnosis."""
        self.differentials.append({
            "condition": condition,
            "probability": probability,
            "rationale": rationale
        })

    def add_diagnostic_test(self, test: str) -> None:
        """Add a diagnostic test recommendation."""
        if test not in self.diagnostics:
            self.diagnostics.append(test)

    def set_question(self, question: str) -> None:
        """Set the single clarifying question."""
        self.question = question
    
    def add_patient_data(self, data: str) -> None:
        """Add patient data information."""
        if data not in self.patient_data:
            self.patient_data.append(data)