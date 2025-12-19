#!/bin/bash

# NeuroVet Native Health Check Script (Sans Docker)
# Usage: ./health-check-native.sh [domain]

DOMAIN="${1:-localhost}"

echo "🏥 NeuroVet Native Health Check"
echo "==============================="
echo "Domain: $DOMAIN"
echo ""

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

# 1. Vérifier les services systemd
echo "🔧 System Services:"
systemctl is-active --quiet neurovet-backend
check_status $? "Backend Service (neurovet-backend)"

systemctl is-active --quiet mysql
check_status $? "MySQL Service"

systemctl is-active --quiet nginx
check_status $? "Nginx Service"

echo ""

# 2. Vérifier la connectivité réseau
echo "🌐 Network Connectivity:"

# Backend health endpoint
if [[ "$DOMAIN" == "localhost" ]]; then
    BACKEND_URL="http://localhost:8000/health"
    FRONTEND_URL="http://localhost"
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
mysqladmin ping -h localhost > /dev/null 2>&1
check_status $? "MySQL Connection"

# Vérifier les tables
mysql -u neurovet -pNSP neurovet_db -e "SHOW TABLES;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    TABLE_COUNT=$(mysql -u neurovet -pNSP neurovet_db -e "SHOW TABLES;" 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} Database Tables: $((TABLE_COUNT - 1)) tables found"
else
    echo -e "${YELLOW}⚠${NC} Database Tables: Could not verify (check credentials)"
fi

echo ""

# 4. Vérifier l'espace disque
echo "💿 Disk Usage:"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo -e "${RED}✗${NC} Disk: ${DISK_USAGE}% used (⚠️  Warning: High usage!)"
elif [ $DISK_USAGE -gt 80 ]; then
    echo -e "${YELLOW}⚠${NC} Disk: ${DISK_USAGE}% used"
else
    echo -e "${GREEN}✓${NC} Disk: ${DISK_USAGE}% used"
fi

echo ""

# 5. Vérifier la mémoire
echo "🧠 Memory Usage:"
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ $MEM_USAGE -gt 90 ]; then
    echo -e "${RED}✗${NC} Memory: ${MEM_USAGE}% used (⚠️  Warning: High usage!)"
elif [ $MEM_USAGE -gt 80 ]; then
    echo -e "${YELLOW}⚠${NC} Memory: ${MEM_USAGE}% used"
else
    echo -e "${GREEN}✓${NC} Memory: ${MEM_USAGE}% used"
fi

echo ""

# 6. Processus en cours
echo "📊 Running Processes:"
GUNICORN_COUNT=$(pgrep -f gunicorn | wc -l)
echo "  - Gunicorn workers: $GUNICORN_COUNT"
echo "  - MySQL: $(pgrep mysql | wc -l) process(es)"
echo "  - Nginx: $(pgrep nginx | wc -l) process(es)"

echo ""

# 7. Logs récents d'erreur
echo "📝 Recent Errors (last 5):"
ERROR_COUNT=$(journalctl -u neurovet-backend --since "1 hour ago" | grep -i error | wc -l)
if [ $ERROR_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Found $ERROR_COUNT error(s) in backend logs (last hour)"
    journalctl -u neurovet-backend --since "1 hour ago" | grep -i error | tail -5
else
    echo -e "${GREEN}✓${NC} No recent errors in backend logs"
fi

echo ""

# 8. Vérifier les variables d'environnement critiques
echo "🔐 Environment Check:"
if [ -f "/opt/apps/neurolocalizer-v2/.env" ]; then
    if grep -q "OPENAI_API_KEY=sk-" /opt/apps/neurolocalizer-v2/.env; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY is configured"
    else
        echo -e "${RED}✗${NC} OPENAI_API_KEY is missing or invalid"
    fi

    if grep -q "OPENAI_ASSISTANT_ID=asst_" /opt/apps/neurolocalizer-v2/.env; then
        echo -e "${GREEN}✓${NC} OPENAI_ASSISTANT_ID is configured"
    else
        echo -e "${RED}✗${NC} OPENAI_ASSISTANT_ID is missing or invalid"
    fi
else
    echo -e "${RED}✗${NC} .env file not found at /opt/apps/neurolocalizer-v2/.env"
fi

echo ""

# 9. SSL Certificate (si domaine spécifié)
if [[ "$DOMAIN" != "localhost" ]]; then
    echo "🔒 SSL Certificate:"
    if command -v certbot &> /dev/null; then
        CERT_INFO=$(certbot certificates 2>/dev/null | grep -A 2 "$DOMAIN")
        if [ -n "$CERT_INFO" ]; then
            EXPIRY=$(echo "$CERT_INFO" | grep "Expiry Date" | awk '{print $3, $4}')
            echo -e "${GREEN}✓${NC} SSL Certificate found (Expires: $EXPIRY)"
        else
            echo -e "${YELLOW}⚠${NC} SSL Certificate not found for $DOMAIN"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Certbot not installed, cannot check SSL"
    fi
    echo ""
fi

echo "=============================="
echo "Health check complete!"
