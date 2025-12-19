#!/bin/bash

# NeuroVet Update Script
# Usage: ./update-app.sh [branch_name]

BRANCH="${1:-main}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 NeuroVet Update Script"
echo "=========================="
echo "Branch: $BRANCH"
echo ""

cd "$PROJECT_DIR"

# Vérifier qu'on est dans un repo git
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Backup de la base de données avant mise à jour
echo "💾 Creating database backup before update..."
./scripts/backup-db.sh
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Backup failed, continuing anyway..."
fi

echo ""
echo "📥 Pulling latest changes from $BRANCH..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed!"
    exit 1
fi

echo ""
echo "🛑 Stopping services..."
docker-compose down

echo ""
echo "🔨 Building new images..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services!"
    exit 1
fi

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 15

echo ""
echo "🔄 Running database migrations..."
docker-compose exec backend uv run alembic upgrade head

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Migrations failed or no migrations to run"
fi

echo ""
echo "✅ Update complete!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔍 To view logs, run:"
echo "  docker-compose logs -f"
