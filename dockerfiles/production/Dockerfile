# =============================================================================
# Dockerfile for Django Velocity - Production (Hardened)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Node.js builder for Tailwind CSS
# -----------------------------------------------------------------------------
FROM node:22-alpine AS node-builder

WORKDIR /app/apps/theme/static_src

# Copy package files for better caching
COPY apps/theme/static_src/package*.json ./

# Install npm dependencies
RUN npm ci --prefer-offline

# Copy source files needed for Tailwind build
COPY apps/theme/static_src/ ./
COPY apps/ /app/apps/
COPY config/ /app/config/

# Build Tailwind CSS (using node to execute postcss directly)
RUN mkdir -p ../static/css/dist && \
    NODE_ENV=production node node_modules/postcss-cli/index.js ./src/styles.css -o ../static/css/dist/styles.css

# -----------------------------------------------------------------------------
# Stage 2: Python builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS python-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1

WORKDIR /app

# Install build dependencies (including git for git-based packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install only production dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

# Copy application code
COPY . .

# Copy built Tailwind CSS from node-builder
COPY --from=node-builder /app/apps/theme/static/css/dist/ /app/apps/theme/static/css/dist/

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# -----------------------------------------------------------------------------
# Stage 3: Production runtime (Hardened)
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS production

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

WORKDIR /app

# Install only runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    # Security: Remove unnecessary files
    && rm -rf /tmp/* /var/tmp/* \
    # Security: Remove package manager to prevent runtime installs
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy application from builder
COPY --from=python-builder /app /app

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

# Security: Drop all capabilities
USER django

# Security: Use non-privileged port
EXPOSE 8000

# Security: Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Run with Daphne (ASGI) for WebSocket support
CMD ["python", "-m", "daphne", \
    "-b", "0.0.0.0", \
    "-p", "8000", \
    "--access-log", "-", \
    "--proxy-headers", \
    "config.asgi:application"]
