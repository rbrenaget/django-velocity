#!/bin/bash
# =============================================================================
# Database Backup Script
# Creates a compressed pg_dump backup in custom format.
# Non-blocking: users can continue working during backup.
#
# Usage: /scripts/backup.sh
# Output: /backups/velocity_YYYY-MM-DD_HHMMSS.dump
# =============================================================================

set -euo pipefail

BACKUP_DIR="/backups"
DB_NAME="${POSTGRES_DB:-velocity}"
DB_USER="${POSTGRES_USER:-postgres}"
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
FILENAME="${DB_NAME}_${TIMESTAMP}.dump"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

mkdir -p "${BACKUP_DIR}"

echo "🗄️  Starting backup of database '${DB_NAME}'..."
START_TIME=$(date +%s)

pg_dump \
    --username="${DB_USER}" \
    --dbname="${DB_NAME}" \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="${FILEPATH}" \
    2>&1

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
SIZE=$(du -h "${FILEPATH}" | cut -f1)

echo ""
echo "✅ Backup completed successfully!"
echo "   File:     ${FILENAME}"
echo "   Size:     ${SIZE}"
echo "   Duration: ${DURATION}s"
