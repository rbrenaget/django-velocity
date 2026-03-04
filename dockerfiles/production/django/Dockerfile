# =============================================================================
# Dockerfile for Django Velocity - Production (Hardened)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Node.js builder for Tailwind CSS
# -----------------------------------------------------------------------------
FROM node:22-alpine AS node-builder

ARG APP_HOME=/app

WORKDIR ${APP_HOME}/apps/theme/static_src

# Copy package files for better caching
COPY apps/theme/static_src/package*.json .

# Install npm dependencies
RUN npm ci --prefer-offline

# Copy source files needed for Tailwind build
COPY apps/theme/static_src/ .
COPY apps/ /app/apps/
COPY config/ /app/config/

# Build Tailwind CSS (using node to execute postcss directly)
RUN mkdir -p ../static/css/dist && \
    NODE_ENV=production node node_modules/postcss-cli/index.js ./src/styles.css -o ../static/css/dist/styles.css

# -----------------------------------------------------------------------------
# Stage 2: Python builder
# -----------------------------------------------------------------------------
FROM python:3.14-slim-bookworm AS python-build-stage

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1


ARG APP_HOME=/app

WORKDIR ${APP_HOME}

# Install build dependencies (including git for git-based packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Requirements are installed here to ensure they will be cached
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy application code
COPY . ${APP_HOME}

# Copy built Tailwind CSS from node-builder
COPY --from=node-builder /app/apps/theme/static/css/dist/ /app/apps/theme/static/css/dist/

# Install only production dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# -----------------------------------------------------------------------------
# Stage 3: Production runtime (Hardened)
# -----------------------------------------------------------------------------
FROM python:3.14-slim-bookworm AS python-run-stage

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

# Security: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    # Disable pip to prevent runtime package installation
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Application settings
    UV_SYSTEM_PYTHON=1 \
    # Disable uv cache to prevent permission issues
    UV_NO_CACHE=1

# Install only runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gettext \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/* \
    # Security: Remove unnecessary files
    && rm -rf /tmp/* /var/tmp/* \
    # Security: Remove package manager to prevent runtime installs
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy application from builder
COPY --from=python-builder ${APP_HOME} ${APP_HOME}

# Security: Create non-root user with specific UID/GID and home directory
RUN groupadd --gid 1000 django \
    && useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin django \
    # Security: Set proper ownership
    && chown -R django:django /app \
    # Security: Remove write permissions where not needed
    && chmod -R a-w /app \
    && chmod -R u+w /app/staticfiles 2>/dev/null || true

# Add virtual environment to PATH (use pre-installed packages, no uv run)
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv"

# Copy entrypoint and scripts
COPY --chown=django:django ./dockerfiles/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./dockerfiles/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=django:django ./dockerfiles/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=django:django ./dockerfiles/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY --chown=django:django ./dockerfiles/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

# Security: Drop all capabilities
USER django

RUN DATABASE_URL="" \
    DJANGO_SETTINGS_MODULE="config.settings.test" \
    uv run python manage.py compilemessages

# Security: Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Run with Daphne (ASGI) for WebSocket support
CMD ["/entrypoint"]
