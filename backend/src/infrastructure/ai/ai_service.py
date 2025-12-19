"""AI service for veterinary neurological diagnostics using OpenAI Prompts API."""
import json
from typing import List, Dict, Any
import openai

from src.domain.entities import ChatMessage, VeterinaryAssessment, PatientData


class AIService:
    """AI service for generating veterinary assessments using OpenAI Prompts API."""

    def __init__(
        self,
        api_key: str,
        prompt_id: str,
        prompt_version: str = "2",
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.prompt_id = prompt_id
        self.prompt_version = prompt_version
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def process_message(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Process message using OpenAI Prompts API."""
        try:
            return await self._use_prompt_api(messages, session)
        except Exception as e:
            print(f"[ERROR] AI Service error: {str(e)}")
            return VeterinaryAssessment(
                assessment=f"Erreur technique: {str(e)}",
                treatment="Consultation vétérinaire recommandée",
                prognosis="Indéterminé",
                question="Veuillez reformuler votre question",
                confidence_level="faible"
            )

    async def _use_prompt_api(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Use OpenAI Prompts API with Conversations to generate assessment."""
        # Get or create conversation for this session
        conversation_id = await self._get_or_create_conversation(session)

        # Get the latest user message
        latest_message = messages[-1] if messages else None
        if not latest_message or latest_message.role != "user":
            raise ValueError("No user message found")

        # Prepare the user input with patient data context if available
        user_input = latest_message.content
        if session.patient_data:
            patient_context = self._format_patient_data_for_ai(session.patient_data)
            user_input = f"{patient_context}\n\n{user_input}"

        # Call the Prompts API with Conversations
        try:
            response = await self.client.responses.create(
                model=self.model,
                conversation=conversation_id,
                prompt={
                    "id": self.prompt_id,
                    "version": self.prompt_version
                },
                input=[{"role": "user", "content": user_input}]
            )

            # Extract the response content
            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'output') and isinstance(response.output, list):
                content = response.output[0].get('content', str(response))
            else:
                content = str(response)

            # Try to parse as JSON
            try:
                assessment_data = json.loads(content)

                # Process patient_data from AI response and update session
                if 'patient_data' in assessment_data and assessment_data['patient_data']:
                    await self._process_ai_patient_data(assessment_data['patient_data'], session)

                return VeterinaryAssessment(**assessment_data)
            except json.JSONDecodeError:
                # If not JSON, create assessment from text
                return VeterinaryAssessment(
                    assessment=content,
                    treatment="Consultation avec votre vétérinaire",
                    prognosis="Nécessite examen clinique",
                    question="Pouvez-vous fournir plus de détails sur les symptômes?",
                    confidence_level="moyenne"
                )

        except Exception as e:
            print(f"[ERROR] Prompts API call failed: {str(e)}")
            raise

    async def _get_or_create_conversation(self, session) -> str:
        """Get existing conversation or create new one for session."""
        # Check if session already has a conversation_id (stored in openai_thread_id field)
        if session.openai_thread_id:
            return session.openai_thread_id

        # Create new conversation
        conversation = await self.client.conversations.create()
        conversation_id = conversation.id

        # Update session with the conversation_id (reusing the openai_thread_id field)
        session.set_openai_thread(conversation_id)

        return conversation_id


    async def _process_ai_patient_data(self, ai_patient_data: dict, session) -> None:
        """Process patient data from AI response and update session."""
        if not ai_patient_data:
            return

        # Initialize patient data if not exists
        if not session.patient_data:
            session.patient_data = PatientData()

        # Update basic info
        if ai_patient_data.get('race'):
            session.patient_data.race = ai_patient_data['race']
        if ai_patient_data.get('age'):
            session.patient_data.age = ai_patient_data['age']
        if ai_patient_data.get('sexe'):
            session.patient_data.sex = ai_patient_data['sexe']

        # Add symptoms (avoid duplicates)
        existing_symptoms = set(session.patient_data.symptoms)
        for symptom in ai_patient_data.get('symptomes', []):
            if symptom and symptom not in existing_symptoms:
                session.patient_data.add_symptom(symptom)

        # Add exam results (avoid duplicates)
        for exam in ai_patient_data.get('examens', []):
            if exam:
                session.patient_data.add_exam_result('ai_exam', exam)

        # Add history
        if ai_patient_data.get('historique'):
            session.patient_data.add_exam_result('historique', ai_patient_data['historique'])

        # Add current treatment
        if ai_patient_data.get('traitement_actuel'):
            session.patient_data.add_exam_result('traitement_actuel', ai_patient_data['traitement_actuel'])

        # Update session
        session.update_patient_data(session.patient_data)

        print(f"[DEBUG] Processed AI patient data: race={ai_patient_data.get('race')}, "
              f"symptoms_count={len(ai_patient_data.get('symptomes', []))}, "
              f"exams_count={len(ai_patient_data.get('examens', []))}")

    def _format_patient_data_for_ai(self, patient_data: PatientData) -> str:
        """Format patient data for AI context."""
        patient_dict = patient_data.to_dict()
        
        context_parts = ["[DONNÉES PATIENT DISPONIBLES]"]
        
        if patient_dict.get('age'):
            context_parts.append(f"Âge: {patient_dict['age']}")
        if patient_dict.get('sex'):
            context_parts.append(f"Sexe: {patient_dict['sex']}")
        if patient_dict.get('race'):
            context_parts.append(f"Race: {patient_dict['race']}")
        if patient_dict.get('weight'):
            context_parts.append(f"Poids: {patient_dict['weight']}")
        
        if patient_dict.get('symptoms'):
            context_parts.append(f"Symptômes: {', '.join(patient_dict['symptoms'])}")
        
        if patient_dict.get('neurological_exam'):
            neuro_exam = patient_dict['neurological_exam']
            context_parts.append("Examen neurologique:")
            for key, value in neuro_exam.items():
                if value:
                    context_parts.append(f"  - {key}: {value}")
        
        if patient_dict.get('other_exams'):
            other_exams = patient_dict['other_exams']
            context_parts.append("Autres examens:")
            for key, value in other_exams.items():
                if value:
                    context_parts.append(f"  - {key}: {value}")
        
        context_parts.append("[FIN DONNÉES PATIENT]")
        
        return "\n".join(context_parts)