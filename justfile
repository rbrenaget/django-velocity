# Justfile for Django Velocity
# Task runner for common Docker/Django commands
# Usage: just <command> [args]

set dotenv-load := true

# Default: show available commands
default:
    @just --list

# =============================================================================
# Docker Commands
# =============================================================================

# Build and start all containers
up:
    docker compose up -d --build

# Stop all containers
down:
    docker compose down

# View logs (optionally for specific service)
logs service="":
    docker compose logs -f {{ service }}

# Rebuild containers from scratch
rebuild:
    docker compose down -v
    docker compose build --no-cache
    docker compose up -d

# =============================================================================
# Django Management Commands
# =============================================================================

# Run any manage.py command
manage *args:
    docker compose exec web uv run python manage.py {{ args }}

# Run migrations
migrate *args:
    docker compose exec web uv run python manage.py migrate {{ args }}

# Create new migrations
makemigrations *args:
    docker compose run --rm --user "$(id -u):$(id -g)" web uv run python manage.py makemigrations {{ args }}

# Create superuser
createsuperuser:
    docker compose exec web uv run python manage.py createsuperuser

# Open Django shell (IPython)
shell:
    docker compose exec web uv run python manage.py shell

# Collect static files
collectstatic:
    docker compose run --rm --user "$(id -u):$(id -g)" web uv run python manage.py collectstatic --noinput

# =============================================================================
# Testing & Quality
# =============================================================================

# Run tests with pytest
test *args:
    docker compose exec web uv run pytest {{ args }}

# Run tests with coverage
test-cov:
    docker compose exec web uv run pytest --cov=apps --cov-report=term-missing --cov-report=html

# Run linting with ruff
lint:
    docker compose exec web uv run ruff check .

# Run formatting with ruff
fmt:
    docker compose exec web uv run ruff format .

# Check formatting without changes
fmt-check:
    docker compose exec web uv run ruff format --check .

# Run all quality checks
check: lint fmt-check

# Fix all auto-fixable issues
fix:
    docker compose exec web ruff check --fix .
    docker compose exec web ruff format .

# =============================================================================
# Development Utilities
# =============================================================================

# Open bash shell in web container
bash:
    docker compose exec web bash

# Open psql shell in db container
dbshell:
    docker compose exec db psql -U postgres -d velocity

# Install dependencies (rebuild web container)
install:
    docker compose build web
    docker compose up -d web

# Generate new SECRET_KEY
secret-key:
    docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Fix ownership of all files in the current directory
fix-perms:
    sudo chown -R $USER:$USER .

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
# Tailwind
# =============================================================================

tailwind *args:
    uv run python manage.py tailwind {{ args }}

# =============================================================================
# Documentation
# =============================================================================

# Build documentation
docs:
    uv run zensical build

# Serve documentation with hot-reload
docs-serve:
    uv run zensical serve
