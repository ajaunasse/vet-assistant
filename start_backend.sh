#!/bin/bash

# Start script for NeuroVet Backend using uv

echo "🧠 Starting NeuroVet Backend..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Navigate to backend directory
cd backend

# Sync dependencies and create virtual environment
echo "📦 Syncing dependencies with uv..."
uv sync

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure your OpenAI API key."
    echo "cp .env.example .env"
    echo "Then edit .env with your configuration."
    exit 1
fi

# Start the server using uv run
echo "🚀 Starting FastAPI server..."
uv run python run.py