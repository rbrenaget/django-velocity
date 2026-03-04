# =============================================================================
# Dockerfile for Django Velocity - Local Development
# =============================================================================
FROM python:3.14-slim-bookworm AS python

FROM python AS python-build-stage

ARG APP_HOME=/app

WORKDIR ${APP_HOME}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYDEVD_DISABLE_FILE_VALIDATION=1

# Move the virtualenv outside of the $APP_HOME directory because it will be overriden by the docker compose mount
ENV UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

# Install system dependencies including Node.js for Tailwind
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    wait-for-it \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Requirements are installed here to ensure they will be cached
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project

# Copy application code
COPY . ${APP_HOME}

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync

# Install npm dependencies for Tailwind (if package.json exists)
RUN if [ -f "${APP_HOME}/apps/theme/static_src/package.json" ]; then \
    cd ${APP_HOME}/apps/theme/static_src && npm install; \
    fi

# Install devcontainer dependencies and utils
RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo bash-completion nano ssh

# Create devcontainer user and add it to sudoers
RUN groupadd --gid 1000 dev-user \
    && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
    && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
    && chmod 0440 /etc/sudoers.d/dev-user

# Add venv to PATH
ENV PATH="/${APP_HOME}/.venv/bin:$PATH"
ENV PYTHONPATH="${APP_HOME}/.venv/lib/python3.14/site-packages:$PYTHONPATH"

# Copy entrypoint and start scripts
COPY ./dockerfiles/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./dockerfiles/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./dockerfiles/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./dockerfiles/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./dockerfiles/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

# Run entrypoint
CMD ["/entrypoint"]
