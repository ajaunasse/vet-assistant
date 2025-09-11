"""AI service for veterinary neurological diagnostics using OpenAI Assistant API."""
import asyncio
import json
from typing import List
import openai

from src.domain.entities import ChatMessage, VeterinaryAssessment, PatientData


class AIService:
    """AI service for generating veterinary assessments using OpenAI Assistant API."""

    def __init__(
        self,
        api_key: str,
        assistant_id: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def process_message(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Process message using your OpenAI assistant."""
        try:
            return await self._use_assistant(messages, session)
        except Exception as e:
            return VeterinaryAssessment(
                assessment=f"Erreur technique: {str(e)}",
                treatment="Consultation vétérinaire recommandée",
                prognosis="Indéterminé",
                question="Veuillez reformuler votre question",
                confidence_level="faible"
            )

    async def _use_assistant(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Use your OpenAI Assistant API with thread persistence."""
        # Get or create thread for this session
        thread_id = await self._get_or_create_thread(session)

        # Add the latest user message to the thread with patient data context
        latest_message = messages[-1] if messages else None
        if latest_message and latest_message.role == "user":
            message_content = latest_message.content
            
            # Add patient data context if available
            if session.patient_data:
                patient_context = self._format_patient_data_for_ai(session.patient_data)
                message_content = f"{patient_context}\n\n{message_content}"
            
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_content
            )

        # Run your assistant with its configured instructions
        run = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)
            run = await self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        if run.status == "completed":
            # Get the assistant's response
            messages_response = await self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )

            if messages_response.data:
                content = messages_response.data[0].content[0].text.value

                # Try to parse as JSON first (if your assistant returns structured data)
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

        # If run failed or no response
        return VeterinaryAssessment(
            assessment="Erreur lors de l'exécution de l'assistant",
            treatment="Consultation vétérinaire recommandée",
            prognosis="Indéterminé",
            question="Veuillez reformuler votre question",
            confidence_level="faible"
        )

    async def _get_or_create_thread(self, session) -> str:
        """Get existing thread or create new one for session."""
        # Check if session already has a thread_id
        if session.openai_thread_id:
            return session.openai_thread_id
        
        # Create new thread
        thread = await self.client.beta.threads.create()
        thread_id = thread.id
        
        # Update session with the thread_id
        session.set_openai_thread(thread_id)
        
        return thread_id

    async def _process_ai_patient_data(self, ai_patient_data: List[str], session) -> None:
        """Process patient data from AI response and update session."""
        # Initialize patient data if not exists
        if not session.patient_data:
            session.patient_data = PatientData()
        
        # Simply store the AI patient data as text - the AI handles the structure
        # Update the session with this information
        session.update_patient_data(session.patient_data)
        
        print(f"[DEBUG] Processed AI patient data: {ai_patient_data}")

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