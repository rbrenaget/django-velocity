#!/bin/bash
# =============================================================================
# Database Restore Script
# Restores a pg_dump backup. DESTRUCTIVE: drops and recreates the database.
# App services must be stopped BEFORE running this script.
#
# Usage: /scripts/restore.sh <filename>
# Example: /scripts/restore.sh velocity_2026-02-10_095800.dump
# =============================================================================

set -euo pipefail

BACKUP_DIR="/backups"
DB_NAME="${POSTGRES_DB:-velocity}"
DB_USER="${POSTGRES_USER:-postgres}"

if [ $# -eq 0 ]; then
    echo "❌ Error: No backup filename provided."
    echo "Usage: $0 <filename>"
    echo ""
    echo "Available backups:"
    ls -1t "${BACKUP_DIR}"/*.dump 2>/dev/null | while read -r f; do
        SIZE=$(du -h "$f" | cut -f1)
        echo "  $(basename "$f")  (${SIZE})"
    done
    exit 1
fi

FILENAME="$1"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

if [ ! -f "${FILEPATH}" ]; then
    echo "❌ Error: Backup file not found: ${FILEPATH}"
    exit 1
fi

SIZE=$(du -h "${FILEPATH}" | cut -f1)
echo "⚠️  WARNING: This will DESTROY the current database '${DB_NAME}'!"
echo "   Restoring from: ${FILENAME} (${SIZE})"
echo ""

# Terminate active connections
echo "🔌 Terminating active connections..."
psql --username="${DB_USER}" --dbname=postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" \
    > /dev/null 2>&1 || true

# Drop and recreate database
echo "🗑️  Dropping database '${DB_NAME}'..."
dropdb --username="${DB_USER}" --if-exists "${DB_NAME}"

echo "🆕 Creating database '${DB_NAME}'..."
createdb --username="${DB_USER}" --owner="${DB_USER}" "${DB_NAME}"

# Restore
echo "📥 Restoring from backup..."
START_TIME=$(date +%s)

pg_restore \
    --username="${DB_USER}" \
    --dbname="${DB_NAME}" \
    --verbose \
    --no-owner \
    --no-privileges \
    "${FILEPATH}" \
    2>&1

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "✅ Restore completed successfully!"
echo "   Duration: ${DURATION}s"
