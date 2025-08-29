#!/bin/bash

echo "🐳 Starting NeuroVet with Docker Compose..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your OpenAI API key before continuing."
    echo "Then run this script again."
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Please set your OPENAI_API_KEY in .env file"
    exit 1
fi

# Start services
echo "🚀 Starting all services..."
docker-compose up --build

echo "✅ NeuroVet is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"