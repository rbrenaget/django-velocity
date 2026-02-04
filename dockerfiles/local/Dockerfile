# =============================================================================
# Dockerfile for Django Velocity - Local Development
# =============================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    PYDEVD_DISABLE_FILE_VALIDATION=1

WORKDIR /app

# Install system dependencies including Node.js for Tailwind
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies including dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --dev --locked

# Copy application code
COPY . .

# Install npm dependencies for Tailwind (if package.json exists)
RUN if [ -f "apps/theme/static_src/package.json" ]; then \
    cd apps/theme/static_src && npm install; \
    fi

# Expose ports for Django and debugpy
EXPOSE 8000
EXPOSE 5678

# Run with Daphne (ASGI) for WebSocket support + debugpy for VS Code debugging
CMD ["uv", "run", "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
