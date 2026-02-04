# Deployment

Guide for deploying Django Velocity to production.

## Quick Start

```bash
# Build and run production environment
just prod-build
just prod-up

# Run migrations
just prod-migrate

# Or run full production test (build, up, health check)
just prod-test
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Generate with `just secret-key` |
| `DATABASE_URL` | PostgreSQL connection | `postgres://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `yourdomain.com,www.yourdomain.com` |
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.django.production` |

### Security

| Variable | Description |
|----------|-------------|
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com` |
| `CORS_ALLOWED_ORIGINS` | `https://yourdomain.com` |
| `SECURE_SSL_REDIRECT` | Set to `false` for local testing |

### Services

| Variable | Default | Description |
|----------|---------|-------------|
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Redis broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Redis results |

## Production Docker Architecture

The production Docker setup uses a **multi-stage build** for security and performance:

### Build Stages

```
┌─────────────────────────────────────────────────────────────────┐
│ Stage 1: node-builder                                           │
│ - Builds Tailwind CSS with PostCSS                              │
│ - Uses Node.js 22 Alpine                                        │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Stage 2: python-builder                                         │
│ - Installs production dependencies (UV_NO_DEV=1)                │
│ - Copies Tailwind CSS from node-builder                         │
│ - Runs collectstatic                                            │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Stage 3: production (Hardened)                                  │
│ - Minimal runtime dependencies                                  │
│ - Non-root user (django:1000)                                   │
│ - Uses venv directly (no uv run)                                │
│ - Health check enabled                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Build Commands

```bash
# Build production image
just prod-build
```

### Services Stack

| Service | Description |
|---------|-------------|
| `web` | Django app with Gunicorn (gthread workers) |
| `db` | PostgreSQL 16 Alpine |
| `redis` | Redis 7 Alpine for caching/Celery |
| `celery-worker` | Background task processor |
| `celery-beat` | Scheduled task scheduler |

## Gunicorn Configuration

The production image runs with optimized Gunicorn settings:

```bash
python -m gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm
```

## Security Features

### Container Hardening

- **Non-root user**: Runs as `django` (UID/GID 1000)
- **Read-only app directory**: Write permissions only where needed
- **Minimal dependencies**: Only runtime packages installed
- **No package managers**: pip/apt disabled in production

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')"
```

### Django Security Settings

Production settings in `config/django/production.py`:

```python
DEBUG = False
SECURE_SSL_REDIRECT = True  # Set via env var for local testing
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = "DENY"
```

## Static Files

Static files are handled through:

1. **Tailwind CSS**: Built in `node-builder` stage
2. **Collectstatic**: Run in `python-builder` stage
3. **WhiteNoise**: Serves files at runtime from `staticfiles/`

## Database Migrations

```bash
# Run migrations after deployment
just prod-migrate
```

## Just Commands Reference

| Command | Description |
|---------|-------------|
| `just prod-build` | Build production Docker images |
| `just prod-up` | Start production containers |
| `just prod-down` | Stop production containers |
| `just prod-logs` | View all production logs |
| `just prod-logs web` | View specific service logs |
| `just prod-migrate` | Run database migrations |
| `just prod-health` | Check application health |
| `just prod-test` | Full test (build, up, health check) |
| `just prod-clean` | Remove containers and volumes |

## Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set `CSRF_TRUSTED_ORIGINS`
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for Celery
- [ ] Configure HTTPS/SSL (or set `SECURE_SSL_REDIRECT=false` for testing)
- [ ] Set up monitoring/logging
- [ ] Configure reverse proxy (nginx/traefik) for SSL termination
