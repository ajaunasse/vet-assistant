"""Patient data entity for veterinary diagnostics."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class PatientData:
    """Patient data collection entity."""
    # Basic information
    age: Optional[str] = None
    sex: Optional[str] = None
    race: Optional[str] = None
    weight: Optional[str] = None
    
    # Clinical information
    symptoms: List[str] = field(default_factory=list)
    symptom_duration: Optional[str] = None
    symptom_progression: Optional[str] = None
    
    # Examination results
    neurological_exam: Dict[str, Any] = field(default_factory=dict)
    other_exams: Dict[str, Any] = field(default_factory=dict)
    
    # Medical history
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    
    # Collection status
    collected_fields: List[str] = field(default_factory=list)
    is_complete: bool = False
    last_updated: Optional[datetime] = None
    
    def add_symptom(self, symptom: str) -> None:
        """Add a symptom to the list."""
        if symptom not in self.symptoms:
            self.symptoms.append(symptom)
            self._mark_field_collected("symptoms")
    
    def set_basic_info(self, age: str = None, sex: str = None, race: str = None, weight: str = None) -> None:
        """Set basic patient information."""
        if age:
            self.age = age
            self._mark_field_collected("age")
        if sex:
            self.sex = sex
            self._mark_field_collected("sex")
        if race:
            self.race = race
            self._mark_field_collected("race")
        if weight:
            self.weight = weight
            self._mark_field_collected("weight")
    
    def add_exam_result(self, exam_type: str, result: Any) -> None:
        """Add an examination result."""
        if exam_type.startswith("neuro"):
            self.neurological_exam[exam_type] = result
        else:
            self.other_exams[exam_type] = result
        self._mark_field_collected("exams")
    
    def add_medical_history(self, history_item: str) -> None:
        """Add medical history item."""
        if history_item not in self.medical_history:
            self.medical_history.append(history_item)
            self._mark_field_collected("medical_history")
    
    def add_medication(self, medication: str) -> None:
        """Add current medication."""
        if medication not in self.current_medications:
            self.current_medications.append(medication)
            self._mark_field_collected("medications")
    
    def _mark_field_collected(self, field_name: str) -> None:
        """Mark a field as collected."""
        if field_name not in self.collected_fields:
            self.collected_fields.append(field_name)
        self.last_updated = datetime.now()
        self._check_completeness()
    
    def _check_completeness(self) -> None:
        """Check if we have enough data for diagnosis."""
        required_fields = ["age", "sex", "race", "symptoms"]
        self.is_complete = all(field in self.collected_fields for field in required_fields)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        required_fields = ["age", "sex", "race", "symptoms"]
        return [field for field in required_fields if field not in self.collected_fields]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "age": self.age,
            "sex": self.sex,
            "race": self.race,
            "weight": self.weight,
            "symptoms": self.symptoms,
            "symptom_duration": self.symptom_duration,
            "symptom_progression": self.symptom_progression,
            "neurological_exam": self.neurological_exam,
            "other_exams": self.other_exams,
            "medical_history": self.medical_history,
            "current_medications": self.current_medications,
            "is_complete": self.is_complete,
            "collected_fields": self.collected_fields
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientData":
        """Create instance from dictionary."""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance