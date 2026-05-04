#!/bin/bash
# script for backup on linux systems

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

if [ -f "$PROJECT_ROOT/.env" ]; then
	set -a
	source "$PROJECT_ROOT/.env"
	set +a
fi

# DB characteristics
DB_NAME="${DB_NAME:-fastfood24_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_PASSWORD="${DB_PASSWORD:-}"

BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date + "%Y%m%d_%H%M")
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"
LOG_FILE="$BACKUP_DIR/backup_log.txt"

mkdir -p "$BACKUP_DIR"

if [ -n "$DB_PASSWORD" ]; then
	export PGPASSWORD="$DB_PASSWORD"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] START OF BACKUPING..." | tee -a "$LOG_FILE"

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F p -f "$BACKUP_FILE" 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
	SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
	echo "[$(date '+%Y-%m-%d %H:%M:%S')] Success: $BACKUP_FILE ${SIZE}" | tee -a "$LOG_FILE"
else
	echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error in pg_dump! Check your access rules and connection settings. " | tee -a "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deleting older dumps..." | tee -a "$LOG_FILE"
find "$BACKUP_DIR" -name "backup_*.sql" -type f -mtime +30 -delete
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning finished. " | tee -a "$LOG_FILE"

unset PGPASSWORD
