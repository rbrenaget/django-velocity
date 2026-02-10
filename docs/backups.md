# Database Backups

Django Velocity includes a CLI-based PostgreSQL backup strategy using `pg_dump` and `pg_restore`, orchestrated through `just` commands.

## Quick Reference

```bash
just db-backup          # Create a backup (no downtime)
just db-backup-list     # List available backups
just db-restore <file>  # Restore from backup (causes downtime)
just db-backup-cleanup  # Remove old backups
```

## How It Works

### Backup (`just db-backup`)

Runs `pg_dump` in **custom format** with maximum compression inside the `db` container. The output is saved to a Docker volume mounted at `/backups/`.

- **Non-blocking** — PostgreSQL takes a consistent snapshot without locking tables
- **No downtime** — users can continue working normally
- **File naming** — `velocity_YYYY-MM-DD_HHMMSS.dump`

### Restore (`just db-restore <filename>`)

Restores from a `.dump` file. This is a **destructive operation**:

1. Waits 5 seconds (press `Ctrl+C` to cancel)
2. **Stops** `web`, `celery-worker`, and `celery-beat` services
3. Terminates active database connections
4. Drops and recreates the database
5. Runs `pg_restore`
6. **Restarts** all stopped services

> ⚠️ **Users will experience downtime** during a restore. The justfile recipe handles stopping and restarting services automatically.

### Cleanup (`just db-backup-cleanup`)

Prunes old backups based on two criteria:

| Setting | Env Variable | Default |
|---------|-------------|---------|
| Max age | `BACKUP_MAX_AGE_DAYS` | 30 days |
| Max count | `BACKUP_MAX_COUNT` | 50 backups |

Oldest backups exceeding either limit are deleted first.

## Storage

Backups are stored in a **Docker named volume** (`backup-data`) mounted at `/backups/` inside the `db` container. This volume persists across `docker compose down` but is **deleted** by `docker compose down -v` or `just rebuild`.

To inspect backups from the host:

```bash
# List backup files
just db-backup-list

# Or inspect the volume directly
docker volume inspect django-velocity_backup-data
```

## Scripts

The backup system consists of three bash scripts in `scripts/`:

| Script | Purpose |
|--------|---------|
| `scripts/backup.sh` | `pg_dump` with compression |
| `scripts/restore.sh` | Drop + recreate DB + `pg_restore` |
| `scripts/cleanup.sh` | Prune by age and count |

These scripts run inside the PostgreSQL container where `pg_dump`/`pg_restore` are natively available. They are mounted read-only via `./scripts:/scripts:ro` in Docker Compose.

## Configuration

Add these to your `.env` to customize retention (optional):

```bash
BACKUP_MAX_AGE_DAYS=30
BACKUP_MAX_COUNT=50
```
