"""AI service for veterinary neurological diagnostics using OpenAI Assistant API."""
import asyncio
import json
import re
from typing import List, Union
import openai

from src.domain.entities import ChatMessage, VeterinaryAssessment, PatientData, CollectionResponse, ResponseType


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
                questions=["Veuillez reformuler votre question"],
                confidence_level="faible"
            )

    async def _use_assistant(
        self, messages: List[ChatMessage], session
    ) -> VeterinaryAssessment:
        """Use your OpenAI Assistant API with thread persistence."""
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

                # Extract and save patient data from the conversation
                await self._extract_and_save_patient_data(content, messages, session)

                # Try to parse as JSON first (if your assistant returns structured data)
                try:
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

    async def _extract_and_save_patient_data(self, content: str, messages: List[ChatMessage], session) -> None:
        """Extract patient data from conversation and save to session."""
        # Initialize patient data if not exists
        if not session.patient_data:
            session.patient_data = PatientData()

        # Get the latest user message to analyze
        latest_user_message = None
        for msg in reversed(messages):
            if msg.role == "user":
                latest_user_message = msg.content
                break

        if not latest_user_message:
            return

        # Extract data using pattern matching
        extracted_data = self._extract_data_patterns(latest_user_message.lower())
        
        # Update patient data with extracted information
        if extracted_data:
            await self._update_patient_data_fields(session.patient_data, extracted_data)
            # Mark the session as updated
            session.update_patient_data(session.patient_data)

    def _extract_data_patterns(self, text: str) -> dict:
        """Extract patient data using regex patterns."""
        extracted = {}
        
        # Age patterns
        age_patterns = [
            r'(\d+)\s*(?:an|année)s?',
            r'(\d+)\s*mois',
            r'(\d+)\s*(?:semaine|semaines)',
            r'âge\s*:?\s*(\d+)\s*(?:an|année|mois)s?',
            r'il a\s*(\d+)\s*(?:an|année|mois)s?',
            r'elle a\s*(\d+)\s*(?:an|année|mois)s?'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text)
            if match:
                age_value = match.group(1)
                if 'mois' in match.group(0):
                    extracted['age'] = f"{age_value} mois"
                elif 'semaine' in match.group(0):
                    extracted['age'] = f"{age_value} semaines"
                else:
                    extracted['age'] = f"{age_value} ans"
                break

        # Sex patterns - ordre d'importance
        sex_patterns = [
            # Patterns spécifiques avec statut reproducteur
            r'(?:mâle|male)\s+(?:entier|non\s+castré)',
            r'(?:mâle|male)\s+castré',
            r'(?:femelle|female)\s+(?:entière|non\s+stérilisée)',
            r'(?:femelle|female)\s+stérilisée',
            
            # Patterns avec contexte
            r'sexe\s*:?\s*(mâle|femelle)(?:\s+(entier|castré|entière|stérilisée))?',
            r'(?:c\'est\s+)?(?:un\s+)?(mâle)(?:\s+(entier|castré))?',
            r'(?:c\'est\s+)?(?:une\s+)?(femelle)(?:\s+(entière|stérilisée))?',
            
            # Patterns simples
            r'(?:^|\s)(mâle|femelle)(?:\s|$|,|\.)',
        ]
        
        for pattern in sex_patterns:
            match = re.search(pattern, text)
            if match:
                matched_text = match.group(0).lower()
                
                if 'mâle' in matched_text or 'male' in matched_text:
                    if 'castré' in matched_text:
                        extracted['sex'] = "mâle castré"
                    else:
                        extracted['sex'] = "mâle entier"
                elif 'femelle' in matched_text or 'female' in matched_text:
                    if 'stérilisée' in matched_text:
                        extracted['sex'] = "femelle stérilisée"
                    else:
                        extracted['sex'] = "femelle entière"
                break

        # Race patterns - ordre spécifique important
        common_races = [
            'malinois', 'berger belge malinois', 'labrador', 'golden retriever', 
            'berger allemand', 'berger belge', 'berger australien', 'husky sibérien', 'husky', 
            'bulldog français', 'bulldog anglais', 'bulldog', 'caniche', 'boxer', 
            'rottweiler', 'doberman', 'beagle', 'jack russell', 'jack russell terrier',
            'yorkshire terrier', 'yorkshire', 'chihuahua', 'border collie', 'setter anglais', 
            'setter irlandais', 'setter', 'pointer', 'épagneul breton', 'épagneul',
            'teckel', 'bichon frisé', 'bichon', 'shih tzu', 'cavalier king charles', 'cocker',
            'saint-bernard', 'terre-neuve', 'dogue allemand', 'mastiff', 'staff', 'pitbull',
            'akita', 'shiba inu', 'samoyède', 'spitz', 'berger des pyrénées'
        ]
        
        # Chercher d'abord les races communes (plus précis)
        for race in common_races:
            if race in text:
                extracted['race'] = race.title()
                break
        
        # Si pas trouvé, utiliser des patterns plus spécifiques
        if 'race' not in extracted:
            race_patterns = [
                r'race\s*:?\s*([a-zà-ÿ\s]{3,20})(?:\s*[,\.!\?]|\s+de\s|\s+qui\s|\s+âgé|\s*$)',
                r'(?:c\'est\s+)?(?:un|une)\s+([a-zà-ÿ\s]{3,20}?)(?:\s+de\s+\d+|\s+âgé|\s+qui|\s+mâle|\s+femelle)',
                r'chien\s+([a-zà-ÿ\s]{3,20}?)(?:\s+de\s+\d+|\s+âgé|\s+qui|\s+mâle|\s+femelle)'
            ]
            
            for pattern in race_patterns:
                match = re.search(pattern, text)
                if match:
                    race_candidate = match.group(1).strip().lower()
                    # Filtrer les mots communs qui ne sont pas des races
                    excluded_words = ['chien', 'animal', 'patient', 'examen', 'symptômes', 'problème', 
                                    'trouble', 'cas', 'histoire', 'situation', 'consultation']
                    
                    if (len(race_candidate) >= 3 and 
                        race_candidate not in excluded_words and
                        not any(word in race_candidate for word in excluded_words)):
                        extracted['race'] = race_candidate.title()
                        break

        # Symptom patterns - neurologiques spécifiques
        neurological_symptoms = {
            'convulsions': ['convulsion', 'convulsions', 'crise épileptique', 'épilepsie'],
            'tremblements': ['tremblement', 'tremblements', 'trembler'],
            'paralysie': ['paralysie', 'paralysé', 'paralyse'],
            'parésie': ['parésie', 'faiblesse musculaire', 'faiblesse'],
            'ataxie': ['ataxie', 'troubles de l\'équilibre', 'perte d\'équilibre', 'déséquilibre'],
            'boiterie': ['boiterie', 'boite', 'claudication'],
            'troubles neurologiques': ['trouble neurologique', 'symptômes neurologiques', 'signes neurologiques'],
            'nystagmus': ['nystagmus', 'mouvements oculaires'],
            'troubles comportementaux': ['tourner en rond', 'comportement anormal', 'désorienté'],
            'troubles posturaux': ['pencher la tête', 'port de tête', 'posture anormale'],
            'troubles moteurs': ['difficultés locomotrices', 'troubles de la marche', 'démarche anormale']
        }
        
        detected_symptoms = []
        for symptom_category, keywords in neurological_symptoms.items():
            for keyword in keywords:
                if keyword in text:
                    detected_symptoms.append(symptom_category)
                    break  # Une seule occurrence par catégorie
        
        if detected_symptoms:
            extracted['symptoms'] = detected_symptoms

        # Weight patterns
        weight_patterns = [
            r'poids\s*:?\s*(\d+(?:\.\d+)?)\s*kg',
            r'pèse\s*(\d+(?:\.\d+)?)\s*kg',
            r'(\d+(?:\.\d+)?)\s*kg'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text)
            if match:
                extracted['weight'] = f"{match.group(1)} kg"
                break

        # Log des extractions pour débogage
        if extracted:
            print(f"[DEBUG] Données extraites du texte '{text[:100]}...': {extracted}")
        
        return extracted

    async def _update_patient_data_fields(self, patient_data: PatientData, extracted_data: dict) -> None:
        """Update patient data fields with extracted information."""
        if 'age' in extracted_data:
            patient_data.set_basic_info(age=extracted_data['age'])
        
        if 'sex' in extracted_data:
            patient_data.set_basic_info(sex=extracted_data['sex'])
        
        if 'race' in extracted_data:
            patient_data.set_basic_info(race=extracted_data['race'])
        
        if 'weight' in extracted_data:
            patient_data.set_basic_info(weight=extracted_data['weight'])
        
        if 'symptoms' in extracted_data:
            for symptom in extracted_data['symptoms']:
                patient_data.add_symptom(symptom)