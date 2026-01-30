# Getting Started

Get up and running with Django Velocity in minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [just](https://github.com/casey/just) (task runner)
- [Docker](https://www.docker.com/) & Docker Compose

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url> django-velocity
cd django-velocity
```

### 2. Start Docker Containers

```bash
just up
```

This builds and starts:

- **web** - Django application (port 8000)
- **db** - PostgreSQL database

### 3. Run Migrations

```bash
just migrate
```

### 4. Create Superuser

```bash
just createsuperuser
```

### 5. Access the Application

- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **API**: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

## Development Commands

| Command | Description |
|---------|-------------|
| `just up` | Start Docker containers |
| `just down` | Stop containers |
| `just logs` | View container logs |
| `just shell` | Open Django shell (IPython) |
| `just test` | Run pytest |
| `just test-cov` | Run tests with coverage |
| `just lint` | Run Ruff linter |
| `just fmt` | Format code with Ruff |
| `just manage <cmd>` | Run any manage.py command |

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://postgres:postgres@db:5432/velocity
```

## Next Steps

- [Architecture Guide](architecture.md) - Understand the service-oriented design
- [API Reference](api/index.md) - Explore available endpoints
