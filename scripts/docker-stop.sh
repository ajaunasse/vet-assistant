#!/bin/bash

echo "🛑 Stopping NeuroVet Docker services..."
docker-compose down

echo "✅ All services stopped!"
echo "💡 To remove all data (including database), run: docker-compose down -v"