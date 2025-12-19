#!/bin/bash

# NeuroVet Database Backup Script
# Usage: ./backup-db.sh

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="neurovet_backup_$DATE.sql"

# Créer le dossier de backups s'il n'existe pas
mkdir -p "$BACKUP_DIR"

echo "🔄 Creating database backup..."

# Aller dans le dossier du projet
cd "$PROJECT_DIR"

# Créer le backup
docker-compose exec -T db mysqldump -u neurovet -pneurovet_pass neurovet_db > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compresser
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    echo "✅ Backup created: $BACKUP_FILE.gz"

    # Garder seulement les 7 derniers backups
    echo "🧹 Cleaning old backups (keeping last 7)..."
    find "$BACKUP_DIR" -name "neurovet_backup_*.sql.gz" -mtime +7 -delete

    # Afficher les backups existants
    echo ""
    echo "📦 Available backups:"
    ls -lh "$BACKUP_DIR"/neurovet_backup_*.sql.gz
else
    echo "❌ Backup failed!"
    exit 1
fi
