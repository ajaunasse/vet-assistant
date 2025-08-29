export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface VeterinaryAssessment {
  assessment: string;
  status: 'processed' | 'completed';
  localization?: string;
  differentials: Array<{
    condition: string;
    probability: 'haute' | 'moyenne' | 'faible';
    rationale: string;
  }>;
  diagnostics: string[];
  treatment: string;
  prognosis: string;
  questions: string[];
  confidence_level: 'haute' | 'moyenne' | 'faible';
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse extends VeterinaryAssessment {}

export interface PatientData {
  age?: string;
  sex?: string;
  race?: string;
  weight?: string;
  symptoms: string[];
  symptom_duration?: string;
  symptom_progression?: string;
  neurological_exam: Record<string, any>;
  other_exams: Record<string, any>;
  medical_history: string[];
  current_medications: string[];
  is_complete: boolean;
  collected_fields: string[];
}

export interface SessionResponse {
  id: string;
  created_at: string;
  updated_at: string;
  current_assessment?: VeterinaryAssessment;
  patient_data?: PatientData;
  is_collecting_data: boolean;
}