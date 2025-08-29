"""Veterinary assessment entity."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VeterinaryAssessment:
    """Veterinary assessment entity with rich domain logic."""
    assessment: str
    localization: Optional[str] = None
    differentials: List[dict] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    treatment: str = ""
    prognosis: str = ""
    questions: List[str] = field(default_factory=list)
    confidence_level: str = "medium"

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

    def add_question(self, question: str) -> None:
        """Add a clarifying question."""
        if question not in self.questions:
            self.questions.append(question)