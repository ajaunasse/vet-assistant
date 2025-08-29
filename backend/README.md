# NeuroVet Backend

FastAPI backend with clean architecture for the veterinary neurological diagnostic assistant.

## 🚀 Quick Start with uv

### Prerequisites
- Python 3.9+
- [uv package manager](https://github.com/astral-sh/uv)

### Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup and Run
1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Start the server:**
   ```bash
   cd src
   uv run python main.py
   ```

Or use the convenience script:
```bash
./start_backend.sh
```

## 🔧 Development Commands

### Install dependencies
```bash
uv sync
```

### Add new dependencies
```bash
uv add package-name
```

### Add development dependencies
```bash
uv add --dev package-name
```

### Run tests
```bash
uv run pytest
```

### Format code
```bash
uv run black src/
```

### Lint code
```bash
uv run ruff check src/
```

## 🏗️ Project Structure

```
backend/
├── src/
│   ├── domain/              # Business logic layer
│   │   ├── entities/        # Domain entities
│   │   ├── interfaces/      # Abstract interfaces
│   │   └── services/        # Domain services
│   ├── infrastructure/      # External services
│   │   └── ai/             # AI service implementations
│   ├── presentation/        # API layer
│   │   └── api/            # FastAPI routes and models
│   └── main.py             # Application entry point
├── tests/                  # Test files
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Locked dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=asst_CeppEgcYMIPQWfTAQUH2xyFp
OPENAI_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.3
MAX_TOKENS=2000
```

**Important:** If `OPENAI_ASSISTANT_ID` is provided, the system will use the OpenAI Assistants API with your custom assistant. If not provided, it will fall back to the standard Chat Completions API.

## 📡 API Endpoints

- `GET /health` - Health check
- `POST /api/v1/sessions` - Create new chat session
- `POST /api/v1/sessions/{session_id}/chat` - Send message to AI
- `GET /api/v1/sessions/{session_id}` - Get session history

## 🧠 AI Agent Configuration

The specialized veterinary AI agent is configured with:
- Expert knowledge in canine neuroanatomy
- Neurological diagnostic methodology  
- Evidence-based treatment recommendations
- Structured JSON response format