#!/bin/bash

# NeuroVet Native Database Backup Script (Sans Docker)
# Usage: ./backup-neurovet-native.sh

# Configuration
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="neurovet_backup_$DATE.sql"
DB_USER="neurovet"
DB_NAME="neurovet_db"

# Créer le dossier de backups s'il n'existe pas
mkdir -p "$BACKUP_DIR"

echo "🔄 Creating database backup..."

# Demander le mot de passe MySQL de manière sécurisée
read -sp "Enter MySQL password for user '$DB_USER': " DB_PASSWORD
echo ""

# Créer le backup
mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_DIR/$BACKUP_FILE"

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
