#!/bin/bash

# NeuroVet Health Check Script
# Usage: ./health-check.sh [domain]

DOMAIN="${1:-localhost}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🏥 NeuroVet Health Check"
echo "========================"
echo "Domain: $DOMAIN"
echo ""

cd "$PROJECT_DIR"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher le statut
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# 1. Vérifier les conteneurs Docker
echo "🐳 Docker Containers:"
docker-compose ps
echo ""

# 2. Vérifier la connectivité réseau
echo "🌐 Network Connectivity:"

# Backend health endpoint
if [[ "$DOMAIN" == "localhost" ]]; then
    BACKEND_URL="http://localhost:8000/health"
    FRONTEND_URL="http://localhost:3000"
else
    BACKEND_URL="https://$DOMAIN/api/v1/health"
    FRONTEND_URL="https://$DOMAIN"
fi

curl -s -f "$BACKEND_URL" > /dev/null 2>&1
check_status $? "Backend API ($BACKEND_URL)"

curl -s -f "$FRONTEND_URL" > /dev/null 2>&1
check_status $? "Frontend ($FRONTEND_URL)"

echo ""

# 3. Vérifier la base de données
echo "💾 Database:"
docker-compose exec -T db mysqladmin ping -h localhost -u root -proot_password > /dev/null 2>&1
check_status $? "MySQL Connection"

echo ""

# 4. Vérifier l'espace disque
echo "💿 Disk Usage:"
df -h | grep -E "Filesystem|/$" | awk '{print $5 " used on " $6}'

echo ""

# 5. Vérifier la mémoire
echo "🧠 Memory Usage:"
free -h | grep -E "Mem:" | awk '{print $3 " used of " $2}'

echo ""

# 6. Afficher les logs récents d'erreur
echo "📝 Recent Errors (last 10):"
docker-compose logs --tail=100 backend 2>&1 | grep -i error | tail -10 || echo "No recent errors"

echo ""

# 7. Vérifier les variables d'environnement critiques
echo "🔐 Environment Check:"
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY is configured"
    else
        echo -e "${RED}✗${NC} OPENAI_API_KEY is missing or invalid"
    fi

    if grep -q "OPENAI_ASSISTANT_ID=asst_" .env; then
        echo -e "${GREEN}✓${NC} OPENAI_ASSISTANT_ID is configured"
    else
        echo -e "${RED}✗${NC} OPENAI_ASSISTANT_ID is missing or invalid"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
fi

echo ""
echo "========================"
echo "Health check complete!"
