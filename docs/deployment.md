# Deployment

Guide for deploying Django Velocity to production.

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

### Services

| Variable | Default | Description |
|----------|---------|-------------|
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Redis broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Redis results |

## Docker Production

### Build Production Image

```dockerfile
# Dockerfile target: production
docker build --target production -t django-velocity:prod .
```

### Docker Compose Production

```yaml
# docker-compose.prod.yml
services:
  web:
    image: django-velocity:prod
    environment:
      - DJANGO_SETTINGS_MODULE=config.django.production
    env_file:
      - .env.prod
    ports:
      - "80:8000"
    depends_on:
      - db
      - redis

  celery-worker:
    image: django-velocity:prod
    command: celery -A config worker -l info
    env_file:
      - .env.prod

  celery-beat:
    image: django-velocity:prod
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - .env.prod
```

## Security Settings

Production settings in `config/django/production.py`:

```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = "DENY"
```

## Static Files

Static files are served via **WhiteNoise**:

```bash
# Collect static files
python manage.py collectstatic --noinput
```

WhiteNoise is already configured in `MIDDLEWARE` and serves files from `staticfiles/`.

## Database Migrations

```bash
# Run migrations in production
python manage.py migrate --noinput
```

## Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set `CSRF_TRUSTED_ORIGINS`
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for Celery
- [ ] Run `collectstatic`
- [ ] Run database migrations
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring/logging
