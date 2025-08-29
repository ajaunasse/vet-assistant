#!/bin/bash

echo "🛠️  Setting up NeuroVet development environment..."

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your OpenAI API key"
fi

# Setup backend
echo "🐍 Setting up backend environment..."
cd backend

# Create virtual environment with uv
echo "📦 Installing dependencies with uv..."
uv sync

# Get the virtual environment path
VENV_PATH=$(uv run python -c "import sys; print(sys.executable)")
echo "✅ Virtual environment created at: $VENV_PATH"

# Go back to root
cd ..

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env with your OpenAI API key"
echo "2. Open your IDE in this directory"
echo "3. WebStorm: Should auto-detect Python at backend/.venv/bin/python"
echo "   Other IDEs: Select Python interpreter: backend/.venv/bin/python"
echo ""
echo "🐳 To run with Docker:"
echo "   ./scripts/docker-start.sh"
echo ""
echo "💻 To run locally:"
echo "   Backend: cd backend && uv run python run.py"
echo "   Frontend: cd frontend && npm start"