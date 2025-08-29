export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface VeterinaryAssessment {
  assessment: string;
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

export interface SessionResponse {
  id: string;
  created_at: string;
  updated_at: string;
  current_assessment?: VeterinaryAssessment;
}