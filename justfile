# Justfile for Django Velocity
# Task runner for common Docker/Django commands
# Usage: just <command> [args]

set dotenv-load := true

# Compose command
compose := "docker compose -f docker-compose.yml"

# Default: show available commands
default:
    @just --list

# =============================================================================
# Docker Commands
# =============================================================================

# Build and start all containers
up:
    {{ compose }} up -d --build

# Stop all containers
down:
    {{ compose }} down

# View logs (optionally for specific service)
logs service="":
    {{ compose }} logs -f {{ service }}

# Rebuild containers from scratch
rebuild:
    {{ compose }} down -v
    {{ compose }} build --no-cache
    {{ compose }} up -d

# Build containers only
build:
    {{ compose }} build

# Show container status
ps:
    {{ compose }} ps

# =============================================================================
# Django Management Commands
# =============================================================================

# Run any manage.py command
manage *args:
    {{ compose }} exec web uv run python manage.py {{ args }}

# Run migrations
migrate *args:
    {{ compose }} exec web uv run python manage.py migrate {{ args }}

# Create new migrations
makemigrations *args:
    {{ compose }} run --rm --user "$(id -u):$(id -g)" web uv run python manage.py makemigrations {{ args }}

# Create superuser
createsuperuser:
    {{ compose }} exec web uv run python manage.py createsuperuser

# Open Django shell (IPython)
shell:
    {{ compose }} exec web uv run python manage.py shell

# Collect static files
collectstatic:
    {{ compose }} run --rm --user "$(id -u):$(id -g)" web uv run python manage.py collectstatic --noinput

# =============================================================================
# Testing & Quality
# =============================================================================

# Run tests with pytest
test *args:
    {{ compose }} exec web uv run pytest {{ args }}

# Run tests with coverage
test-cov:
    {{ compose }} exec web uv run pytest --cov=apps --cov-report=term-missing --cov-report=html

# Run linting with ruff
lint:
    {{ compose }} exec web uv run ruff check .

# Run formatting with ruff
fmt:
    {{ compose }} exec web uv run ruff format .

# Check formatting without changes
fmt-check:
    {{ compose }} exec web uv run ruff format --check .

# Run all quality checks
check: lint fmt-check

# Fix all auto-fixable issues
fix:
    {{ compose }} exec web ruff check --fix .
    {{ compose }} exec web ruff format .

# =============================================================================
# Development Utilities
# =============================================================================

# Open bash shell in web container
bash:
    {{ compose }} exec web bash

# Open psql shell in db container
dbshell:
    {{ compose }} exec db psql -U postgres -d velocity

# Install dependencies (rebuild web container)
install:
    {{ compose }} build web
    {{ compose }} up -d web

# Generate new SECRET_KEY
secret-key:
    {{ compose }} exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Fix ownership of all files in the current directory
fix-perms:
    sudo chown -R $USER:$USER .

# Check health endpoint
health:
    @curl -s http://localhost:8000/health/ | python -m json.tool || echo "Health check failed"

# =============================================================================
# Translations
# =============================================================================

# Extract translatable strings to .po files
makemessages *args:
    uv run python manage.py makemessages {{ args }}

# Compile .po files to .mo files
compilemessages:
    uv run python manage.py compilemessages

# =============================================================================
# Celery
# =============================================================================

# View Celery worker logs
celery-logs:
    {{ compose }} logs -f celery-worker

# View Celery beat logs
celery-beat-logs:
    {{ compose }} logs -f celery-beat

# =============================================================================
# Tailwind
# =============================================================================

tailwind *args:
    uv run python manage.py tailwind {{ args }}

# =============================================================================
# Production Shortcuts
# =============================================================================

# Build production images
prod-build:
    docker compose -f docker-compose.production.yml build

# Start production containers
prod-up:
    docker compose -f docker-compose.production.yml up -d

# Stop production containers
prod-down:
    docker compose -f docker-compose.production.yml down

# View production logs
prod-logs service="":
    docker compose -f docker-compose.production.yml logs -f {{ service }}

# Run production migrations
prod-migrate:
    docker compose -f docker-compose.production.yml exec web python manage.py migrate

# Check production health
prod-health:
    @curl -s http://localhost:8000/health/ | python3 -m json.tool || echo "Health check failed"

# Full production test (build, up, health check)
prod-test:
    @echo "🔨 Building production images..."
    docker compose -f docker-compose.production.yml build
    @echo "🚀 Starting production containers..."
    docker compose -f docker-compose.production.yml up -d
    @echo "⏳ Waiting for services to be ready..."
    sleep 10
    @echo "🏥 Running health check..."
    curl -sf http://localhost:8000/health/ && echo "✅ Health check passed" || echo "❌ Health check failed"
    @echo "📋 Container status:"
    docker compose -f docker-compose.production.yml ps

# Clean up production containers and volumes
prod-clean:
    docker compose -f docker-compose.production.yml down -v --rmi local

# =============================================================================
# Documentation
# =============================================================================

# Build documentation
docs:
    uv run zensical build

# Serve documentation with hot-reload
docs-serve:
    uv run zensical serve -a localhost:8001
