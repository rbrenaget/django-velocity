# Django Velocity

A modern, opinionated Django boilerplate implementing **Service-Oriented Architecture** following the [HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

## ✨ Features

- **Service-Oriented Architecture** - Business logic in Services & Selectors, not Views
- **Custom User Model** - Email-based authentication from day one
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **DRF + Django Ninja** - Choose your API framework (DRF primary, Ninja optional)
- **Modern Admin UI** - Beautiful admin interface with [django-unfold](https://unfoldadmin.com/)
- **Modern Python** - Python 3.12+, type hints, Ruff for linting
- **Docker Ready** - Docker Compose setup for development
- **Testing** - pytest + factory_boy with comprehensive examples
- **Task Runner** - `just` commands for common operations

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Views)                        │
│   Thin views - validation, call service/selector, respond   │
├──────────────────────────┬──────────────────────────────────┤
│      Services            │         Selectors                │
│   (Write Operations)     │      (Read Operations)           │
│   - Create, Update       │      - Get, List, Filter         │
│   - Business Logic       │      - Complex Queries           │
│   - Transactions         │      - DTOs/QuerySets            │
├──────────────────────────┴──────────────────────────────────┤
│                    Models (Data Layer)                      │
│              Anemic models - schema only                    │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

| Traditional Django         | Service-Oriented (This Boilerplate)         |
|---------------------------|---------------------------------------------|
| Fat models with logic     | Anemic models (schema only)                 |
| Logic scattered in views  | Business logic in dedicated services        |
| Hard to test              | Unit tests for services/selectors           |
| Difficult to maintain     | Clear separation of concerns                |

## 🚀 Quick Start

### Prerequisites

- [Python 3.12](https://www.python.org/downloads/)
- [uv](https://github.com/indygreg/uv) (Python manager)
- [just](https://github.com/casey/just) (task runner)
- Docker & Docker Compose

### Setup

```bash
# Clone the repository
git clone <repo-url> django-velocity
cd django-velocity

# Start Docker containers
just up

# Run migrations
just migrate

# Create superuser
just createsuperuser

# Open http://localhost:8000/admin/
```

### Development Commands

```bash
just              # Show all available commands
just up           # Start containers
just down         # Stop containers
just logs         # View logs
just shell        # Django shell (IPython)
just test         # Run tests
just test-cov     # Run tests with coverage
just lint         # Run Ruff linter
just fmt          # Format code with Ruff
just manage <cmd> # Run any manage.py command
```

## 📁 Project Structure

```
django-velocity/
├── config/                 # Django project configuration
│   ├── django/             # Django-specific settings
│   │   ├── base.py         # Base settings
│   │   ├── local.py        # Development settings
│   │   ├── production.py   # Production settings
│   │   └── test.py         # Test settings
│   ├── settings/           # Third-party integrations
│   │   ├── allauth.py      # django-allauth config
│   │   ├── email.py        # Email configuration
│   │   ├── jwt.py          # SimpleJWT settings
│   │   ├── rest_framework.py # DRF settings
│   │   └── unfold.py       # Django Unfold admin theme
│   ├── urls.py
│   └── wsgi.py
│
├── apps/                   # Domain applications
│   ├── core/               # Shared utilities
│   │   ├── exceptions.py   # Business exception hierarchy
│   │   ├── models.py       # BaseModel with timestamps
│   │   ├── services.py     # @service decorator
│   │   └── api.py          # Django Ninja setup
│   │
│   ├── authentication/     # Authentication domain
│   │   ├── models.py       # Auth-related models
│   │   ├── services.py     # register_user, login_user, password reset...
│   │   ├── serializers.py  # Auth serializers
│   │   ├── views.py        # Auth API views
│   │   └── tests/
│   │
│   └── users/              # User domain
│       ├── models.py       # Custom User model
│       ├── services.py     # user_update, user_change_password...
│       ├── selectors.py    # user_get_by_email, user_list...
│       ├── views.py        # User profile API views
│       └── tests/
│
└── tests/                  # Project-wide test utilities
    ├── conftest.py         # pytest fixtures
    └── factories.py        # FactoryBoy factories
```

## 📝 Code Examples

### Service (Business Logic)

```python
# apps/authentication/services.py
from apps.core.services import service
from apps.core.exceptions import ValidationError

@service
def register_user(*, email: str, password: str, first_name: str = "", last_name: str = "") -> dict:
    """Register a new user and return JWT tokens."""
    if user_get_by_email(email=email):
        raise ValidationError("Email already registered")

    user = User.objects.create_user(email=email, password=password)
    tokens = generate_tokens_for_user(user)
    return {"user": user, **tokens}
```

```python
# apps/users/services.py - Profile management
@service
def user_update(*, user: User, first_name: str | None = None, last_name: str | None = None) -> User:
    """Update user profile information."""
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    user.save(update_fields=["first_name", "last_name", "updated_at"])
    return user
```

### Selector (Read Operations)

```python
# apps/users/selectors.py
def user_get_by_email(*, email: str) -> User | None:
    """Fetch user by email - read only, no side effects."""
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None
```

### Thin View (API Layer)

```python
# apps/authentication/views.py
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Delegate to service - view is thin!
        result = services.register_user(**serializer.validated_data)

        return Response(RegisterOutputSerializer(result).data, status=201)
```

## 🔌 API Endpoints

### Authentication (`/api/v1/auth/`)

| Method | Endpoint                       | Description             |
|--------|--------------------------------|-------------------------|
| POST   | `/api/v1/auth/register/`       | Register new user       |
| POST   | `/api/v1/auth/login/`          | Login, get JWT tokens   |
| POST   | `/api/v1/auth/token/refresh/`  | Refresh access token    |
| POST   | `/api/v1/auth/forgot-password/`| Request password reset  |
| POST   | `/api/v1/auth/reset-password/` | Confirm password reset  |
| POST   | `/api/v1/auth/verify-email/`   | Verify email address    |
| POST   | `/api/v1/auth/change-password/`| Change password (auth)  |

### User Management (`/api/v1/users/`)

| Method | Endpoint                       | Description          |
|--------|--------------------------------|----------------------|
| GET    | `/api/v1/users/me/`            | Get current user     |
| PATCH  | `/api/v1/users/me/`            | Update profile       |

### Django Ninja (Optional)

| Method | Endpoint             | Description          |
|--------|----------------------|----------------------|
| GET    | `/api/ninja/health`  | Health check         |

## 🧪 Testing

```bash
# Run all tests
just test

# Run with coverage
just test-cov

# Run specific test file
just test apps/users/tests/test_services.py

# Run specific test
just test apps/users/tests/test_services.py::TestUserCreate::test_creates_user_successfully
```

### Test Strategy

1. **Unit Tests** (Primary) - Test services and selectors directly
2. **Integration Tests** - Test API endpoints through HTTP
3. **No View Logic Tests** - Views are thin, logic is in services

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://postgres:postgres@db:5432/velocity
```

### Using Django Ninja Instead of DRF

Django Ninja is included as an optional alternative. To use it:

1. Add your endpoints in `apps/<domain>/api_ninja.py`
2. Register routers in `apps/core/api.py`
3. Access at `/api/ninja/`

## 📦 Dependencies

| Package                      | Purpose                          |
|-----------------------------|----------------------------------|
| Django 6.0+                 | Web framework                    |
| djangorestframework         | REST API (primary)               |
| django-ninja                | REST API (optional alternative)  |
| djangorestframework-simplejwt| JWT authentication              |
| django-unfold               | Modern admin theme               |
| psycopg 3                   | PostgreSQL adapter               |
| django-environ              | Environment configuration        |
| whitenoise                  | Static file serving              |
| pytest-django               | Testing                          |
| factory-boy                 | Test data generation             |
| ruff                        | Linting & formatting             |

## 📚 Documentation

This project uses [Zensical](https://zensical.org/) for documentation generation.

```bash
# Build documentation
just docs

# Serve documentation locally with hot-reload
just docs-serve
# Then open http://localhost:8000
```

## 📄 License

MIT

---

Built following the [HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide)
