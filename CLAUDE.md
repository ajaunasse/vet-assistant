# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NeuroVet is a veterinary neurological diagnostic assistant that uses AI to help veterinarians analyze neurological disorders in dogs. The system is built as a full-stack application with:
- **Backend**: FastAPI with clean architecture (Python 3.12+)
- **Frontend**: React with TypeScript
- **Database**: MySQL 8.0
- **AI**: OpenAI Assistants API with thread persistence

## Development Environment

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ with `uv` package manager
- Node.js for frontend development

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `OPENAI_API_KEY`: Required for AI functionality
- `OPENAI_ASSISTANT_ID`: Required - the system uses a custom OpenAI assistant
- `DATABASE_URL`: MySQL connection string (auto-configured in Docker)

## Common Commands

### Using Make (Recommended for Docker)
```bash
# Full stack development
make dev              # Start all services with logs
make up               # Start all services in background
make down             # Stop all services

# Individual services
make backend          # Start only backend + database
make frontend         # Start only frontend
make db               # Start only database

# Database management
make db-setup         # Complete database setup (start db + run migrations)
make db-init          # Initialize database tables
make db-check         # Check database status
make db-reset         # Reset database (destructive)
make migrate-auto     # Generate new migration from model changes
make migrate-up       # Apply pending migrations
make migrate-down     # Rollback last migration

# Development tasks
make logs             # View all service logs
make logs-backend     # Backend logs only
make shell            # Open shell in backend container
make test             # Run backend tests
make lint             # Run ruff linter
make format           # Format code with ruff
```

### Backend (uv)
```bash
cd backend
uv sync                           # Install dependencies
uv add package-name               # Add new dependency
uv run uvicorn src.main:app --reload  # Run development server
uv run pytest                     # Run tests
uv run ruff check .               # Lint
uv run ruff format .              # Format
```

### Frontend (npm)
```bash
cd frontend
npm install                       # Install dependencies
npm start                         # Start development server (port 3000)
npm run build                     # Build for production
npm test                          # Run tests
```

### Database Migrations (Alembic)
Located in `backend/alembic/`:
```bash
# Inside Docker container
docker-compose exec backend uv run alembic revision --autogenerate -m "description"
docker-compose exec backend uv run alembic upgrade head
docker-compose exec backend uv run alembic downgrade -1
```

## Architecture

### Backend Clean Architecture

The backend follows clean architecture with strict layer separation:

**Domain Layer** (`src/domain/`)
- Core business entities and logic
- No external dependencies
- Entities: `ChatSession`, `ChatMessage`, `VeterinaryAssessment`, `PatientData`, `DogBreed`, `ConsultationReason`
- Repository interfaces (abstractions)

**Application Layer** (`src/application/`)
- Use case handlers implementing business workflows
- Commands: `CreateSessionCommand`, `SendMessageCommand`
- Queries: `GetSessionQuery`, `GetSessionMessagesQuery`, `GetSessionBySlugQuery`
- Handlers orchestrate domain entities and repositories

**Infrastructure Layer** (`src/infrastructure/`)
- External service implementations
- `ai/ai_service.py`: OpenAI integration with thread persistence
- `repositories.py`: SQL repository implementations
- `database.py`: SQLAlchemy models and database connection

**Presentation Layer** (`src/presentation/`)
- FastAPI routes and API schemas
- `router.py`: All API endpoints
- `schemas.py`: Pydantic request/response models

### Key Architectural Patterns

**OpenAI Assistant Integration**:
- Uses persistent threads (one thread per chat session)
- Thread ID stored in `chat_sessions.openai_thread_id`
- Patient data injected as context with each message
- Expects JSON responses from the assistant with structured fields

**Session & Conversation Flow**:
1. Create session → generates unique slug for URL sharing
2. Patient data collection via pre-consultation form (optional)
3. Chat messages sent to AI with patient context
4. AI responses parsed as `VeterinaryAssessment` objects
5. Session state persisted with current assessment

**Patient Data Structure**:
- Collected via form or extracted by AI during conversation
- Stored as JSON in `chat_sessions.patient_data`
- Includes: basic info, symptoms, neurological exam results, other exams
- Formatted and injected into AI context for each message

### Frontend Architecture

**Component Structure**:
- `ChatInterface.tsx`: Main orchestrator component
- `PreConsultationForm.tsx`: Patient data collection
- `AssessmentDisplay.tsx`: Shows AI diagnostic assessment
- `PatientDataDisplay.tsx`: Shows collected patient information
- `ConversationSidebar.tsx`: Session history management

**State Management**:
- React hooks for local state
- `SessionManager.ts`: Browser-based session persistence
- `conversationHistory.ts`: Conversation list management

**API Communication**:
- `services/api.ts`: Centralized API client
- Axios for HTTP requests
- Proxy configured to backend in development

### Database Schema

**chat_sessions**:
- `id` (UUID), `created_at`, `updated_at`, `slug` (unique URL identifier)
- `openai_thread_id`: OpenAI thread for conversation persistence
- `patient_data` (JSON): Collected patient information
- `current_assessment` (JSON): Latest AI assessment
- `is_collecting_data`: Flag for pre-consultation phase

**chat_messages**:
- `id`, `session_id` (FK), `role`, `content`, `timestamp`
- Simple message storage, actual conversation in OpenAI thread

**dog_breeds** & **consultation_reasons**:
- Reference data for form dropdowns

## Important Development Notes

### Working with the AI Service
- The system requires a configured OpenAI Assistant (set `OPENAI_ASSISTANT_ID`)
- **Assistant configuration files**:
  - `.claude/openai-assistant-prompt.txt`: Complete assistant instructions
  - `.claude/openai-assistant-schema.json`: JSON response schema
  - Copy these to your OpenAI Assistant configuration
- **Model settings**: Use gpt-4o, temperature: 0.3, top_p: default (1.0)
- Assistant returns structured JSON with these fields:
  - Required: `status`, `assessment`, `patient_data` (object)
  - Optional: `localization`, `differentials`, `diagnostics`, `treatment`, `prognosis`, `question`, `confidence_level`
- **Patient data flow**:
  1. Backend sends existing patient data as context prefix to each message
  2. AI extracts new information from conversation and returns complete `patient_data` object
  3. Backend parses and integrates the structured data into session
  4. Updated data is sent in next message context
- **patient_data structure** (from AI response):
  ```json
  {
    "race": "string",
    "age": "string",
    "sexe": "string",
    "symptomes": ["string"],
    "examens": ["string"],
    "historique": "string",
    "traitement_actuel": "string"
  }
  ```
- Thread persistence means the assistant maintains full conversation history

### Database Migrations
- Always use Alembic for schema changes, never modify SQLAlchemy models directly without migrations
- Models in `database.py` must match domain entities but are separate (infrastructure vs domain)
- Run `make migrate-auto` after changing models to generate migration

### Testing
- Backend tests use pytest with async support
- Integration test exists at root: `test_integration.py`
- No frontend tests currently configured (uses react-scripts test setup)

### API Endpoints
```
GET  /                                      # Root
GET  /api/v1/health                        # Health check
POST /api/v1/sessions                      # Create new session
POST /api/v1/sessions/{id}/messages        # Send message
GET  /api/v1/sessions/{id}                 # Get session with messages
GET  /api/v1/sessions/slug/{slug}          # Get session by slug
POST /api/v1/sessions/{id}/patient-data    # Save patient data
GET  /api/v1/sessions/{id}/patient-data    # Get patient data
DELETE /api/v1/sessions/{id}/patient-data  # Clear patient data
GET  /api/v1/dog-breeds                    # List dog breeds
GET  /api/v1/consultation-reasons          # List consultation reasons
```

## Common Tasks

### Adding a New Domain Entity
1. Create entity class in `src/domain/entities/`
2. Add repository interface in `src/domain/repositories.py`
3. Create SQLAlchemy model in `src/infrastructure/database.py`
4. Implement repository in `src/infrastructure/repositories.py`
5. Generate migration: `make migrate-auto`
6. Apply migration: `make migrate-up`

### Adding a New API Endpoint
1. Create command/query in `src/application/`
2. Create handler in `src/application/`
3. Add Pydantic schemas in `src/presentation/schemas.py`
4. Add route in `src/presentation/router.py`
5. Update frontend API client in `services/api.ts`

### Modifying AI Response Structure
1. Update `VeterinaryAssessment` entity in `src/domain/entities/veterinary_assessment.py`
2. Update Pydantic schema in `src/presentation/schemas.py`
3. Update OpenAI Assistant instructions to match new structure
4. Update frontend types in `src/types/api.ts`
5. Update display components as needed

## Language & Domain Context

This is a French-language veterinary application:
- All user-facing text is in French
- Medical terminology uses French veterinary conventions
- Patient data fields use French names (race, âge, sexe, etc.)
- AI assistant is configured for French veterinary neurology expertise
