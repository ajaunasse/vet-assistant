#!/bin/bash

# NeuroVet Native Update Script (Sans Docker)
# Usage: ./update-neurovet-native.sh [branch]

BRANCH="${1:-main}"
PROJECT_DIR="/var/www/neurovet"

echo "🚀 NeuroVet Native Update Script"
echo "================================"
echo "Branch: $BRANCH"
echo ""

cd "$PROJECT_DIR" || exit 1

# Vérifier qu'on est dans un repo git
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Backup optionnel
read -p "Create database backup before update? (y/N): " backup_choice
if [[ "$backup_choice" =~ ^[Yy]$ ]]; then
    echo ""
    /opt/scripts/backup-neurovet-native.sh
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: Backup failed, continuing anyway..."
    fi
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

# Backend
echo ""
echo "🔧 Backend: Installing dependencies..."
cd "$PROJECT_DIR/backend"
uv sync

if [ $? -ne 0 ]; then
    echo "❌ Backend dependencies installation failed!"
    exit 1
fi

echo ""
echo "🔄 Backend: Running migrations..."
uv run alembic upgrade head

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Migrations failed or no migrations to run"
fi

# Frontend
echo ""
echo "⚛️  Frontend: Building..."
cd "$PROJECT_DIR/frontend"
npm install

if [ $? -ne 0 ]; then
    echo "❌ Frontend npm install failed!"
    exit 1
fi

npm run build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

# Restart services
echo ""
echo "🔄 Restarting backend service..."
systemctl restart neurovet-backend

if [ $? -ne 0 ]; then
    echo "❌ Failed to restart backend!"
    exit 1
fi

echo ""
echo "🔄 Reloading Nginx..."
systemctl reload nginx

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Nginx reload failed"
fi

echo ""
echo "✅ Update complete!"
echo ""
echo "📊 Service Status:"
systemctl status neurovet-backend --no-pager -l

echo ""
echo "🔍 To view logs, run:"
echo "  journalctl -u neurovet-backend -f"
