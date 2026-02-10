#!/bin/bash
# =============================================================================
# Backup Cleanup Script
# Prunes old backups based on age and count limits.
#
# Usage: /scripts/cleanup.sh
# Env vars:
#   BACKUP_MAX_AGE_DAYS  (default: 30)
#   BACKUP_MAX_COUNT     (default: 50)
# =============================================================================

set -euo pipefail

BACKUP_DIR="/backups"
MAX_AGE_DAYS="${BACKUP_MAX_AGE_DAYS:-30}"
MAX_COUNT="${BACKUP_MAX_COUNT:-50}"

echo "🧹 Cleaning up backups..."
echo "   Max age:   ${MAX_AGE_DAYS} days"
echo "   Max count: ${MAX_COUNT}"
echo ""

DELETED=0

# Phase 1: Remove backups older than MAX_AGE_DAYS
if [ -d "${BACKUP_DIR}" ]; then
    while IFS= read -r file; do
        echo "   ⏰ Removing (too old): $(basename "${file}")"
        rm -f "${file}"
        DELETED=$((DELETED + 1))
    done < <(find "${BACKUP_DIR}" -name "*.dump" -type f -mtime "+${MAX_AGE_DAYS}" 2>/dev/null)
fi

# Phase 2: Keep only MAX_COUNT most recent backups
CURRENT_COUNT=$(find "${BACKUP_DIR}" -name "*.dump" -type f 2>/dev/null | wc -l)

if [ "${CURRENT_COUNT}" -gt "${MAX_COUNT}" ]; then
    EXCESS=$((CURRENT_COUNT - MAX_COUNT))
    # Sort oldest first, take the excess
    find "${BACKUP_DIR}" -name "*.dump" -type f -printf '%T+ %p\n' 2>/dev/null \
        | sort \
        | head -n "${EXCESS}" \
        | cut -d' ' -f2- \
        | while IFS= read -r file; do
            echo "   📦 Removing (over limit): $(basename "${file}")"
            rm -f "${file}"
            DELETED=$((DELETED + 1))
        done
fi

REMAINING=$(find "${BACKUP_DIR}" -name "*.dump" -type f 2>/dev/null | wc -l)
echo ""
echo "✅ Cleanup complete. Removed: ${DELETED}. Remaining: ${REMAINING}."
