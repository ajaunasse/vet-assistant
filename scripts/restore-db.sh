#!/bin/bash

# NeuroVet Database Restore Script
# Usage: ./restore-db.sh <backup_file.sql.gz>

if [ -z "$1" ]; then
    echo "❌ Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "📦 Available backups:"
    ls -lh "$HOME/backups"/neurovet_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_FILE="/tmp/neurovet_restore_$$.sql"

# Vérifier que le fichier existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will restore the database from backup."
echo "📁 Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

echo ""
echo "🔄 Restoring database..."

# Décompresser le backup
echo "📦 Decompressing backup..."
gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"

# Aller dans le dossier du projet
cd "$PROJECT_DIR"

# Restaurer dans la base de données
echo "💾 Restoring to database..."
docker-compose exec -T db mysql -u neurovet -pneurovet_pass neurovet_db < "$TEMP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully!"
    rm "$TEMP_FILE"
else
    echo "❌ Restore failed!"
    rm "$TEMP_FILE"
    exit 1
fi
