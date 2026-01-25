# =============================================================================
# Multi-stage Dockerfile for Django Velocity
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base image with uv
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# -----------------------------------------------------------------------------
# Stage 2: Development image
# -----------------------------------------------------------------------------
FROM base AS development

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies including dev
RUN uv pip install -e ".[dev]"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# -----------------------------------------------------------------------------
# Stage 3: Production image
# -----------------------------------------------------------------------------
FROM base AS production

# Copy dependency files
COPY pyproject.toml ./

# Install only production dependencies
RUN uv pip install -e .

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system django && adduser --system --group django
USER django

# Expose port
EXPOSE 8000

# Run with gunicorn (add gunicorn to dependencies for production)
CMD ["python", "-m", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
