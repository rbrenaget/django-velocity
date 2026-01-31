# =============================================================================
# Multi-stage Dockerfile for Django Velocity
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base image with uv
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    PYDEVD_DISABLE_FILE_VALIDATION=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# -----------------------------------------------------------------------------
# Stage 2: Development image
# -----------------------------------------------------------------------------
FROM base AS development

WORKDIR /app

# Install dependencies including dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --dev --locked

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run development server
EXPOSE 5678

# Run with debugpy for VS Code remote debugging
CMD ["uv", "run", "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "manage.py", "runserver", "0.0.0.0:8000"]

# -----------------------------------------------------------------------------
# Stage 3: Production image
# -----------------------------------------------------------------------------
FROM base AS production

# Disable development dependencies
ENV UV_NO_DEV=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install only production dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

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
CMD ["uv", "run", "python", "-m", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
