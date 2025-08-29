#!/bin/bash

# Start script for NeuroVet Frontend

echo "🖥️  Starting NeuroVet Frontend..."

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the React development server
echo "🚀 Starting React development server..."
npm start