"""AI service for veterinary neurological diagnostics using OpenAI Assistant API."""
import asyncio
from typing import List
import openai

from src.domain.entities import ChatMessage, VeterinaryAssessment


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

    async def generate_assessment(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Generate a veterinary assessment using OpenAI Assistant API."""
        try:
            return await self._use_assistant(messages, session)
        except Exception as e:
            return VeterinaryAssessment(
                assessment=f"Erreur technique: {str(e)}",
                treatment="Consultation vétérinaire recommandée",
                prognosis="Indéterminé",
                questions=["Veuillez reformuler votre question"],
                confidence_level="faible"
            )

    async def _use_assistant(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Use OpenAI Assistant API with thread persistence."""
        # Get or create thread for this session
        thread_id = await self._get_or_create_thread(session)

        # Add the latest user message to the thread
        latest_message = messages[-1] if messages else None
        if latest_message and latest_message.role == "user":
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=latest_message.content
            )

        # Run the assistant
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

                # Try to parse as JSON first
                try:
                    import json
                    assessment_data = json.loads(content)
                    return VeterinaryAssessment(**assessment_data)
                except json.JSONDecodeError:
                    # If not JSON, create assessment from text
                    return VeterinaryAssessment(
                        assessment=content,
                        treatment="Consultation avec votre vétérinaire",
                        prognosis="Nécessite examen clinique",
                        questions=["Pouvez-vous fournir plus de détails sur les symptômes?"],
                        confidence_level="moyenne"
                    )

        # If run failed or no response
        return VeterinaryAssessment(
            assessment="Erreur lors de l'exécution de l'assistant",
            treatment="Consultation vétérinaire recommandée",
            prognosis="Indéterminé",
            questions=["Veuillez reformuler votre question"],
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