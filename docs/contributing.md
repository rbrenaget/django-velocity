# Contributing

Welcome! Here's how to contribute to Django Velocity.

## Development Setup

```bash
# Clone and setup
git clone <repo-url> django-velocity
cd django-velocity

# Start Docker environment
just up

# Run migrations
just migrate

# Run tests to verify setup
just test
```

## Code Style

We use **Ruff** for linting and formatting:

```bash
just lint    # Check for issues
just fmt     # Auto-format code
just fix     # Fix auto-fixable issues
```

### Python Guidelines

- Python 3.12+ with type hints
- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Maximum line length: 88 characters (Black-compatible)

## Architecture Patterns

Follow the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide):

### Services (Write Operations)

```python
from apps.core.services import service

@service
def user_create(*, email: str, password: str) -> User:
    """Business logic for writes - use keyword-only arguments."""
    ...
```

### Selectors (Read Operations)

```python
def user_get_by_email(*, email: str) -> User | None:
    """Read operations - no side effects."""
    ...
```

### Views (Thin Layer)

Views should only:

1. Validate input
2. Call service/selector
3. Return response

## Testing

```bash
just test              # Run all tests
just test-cov          # With coverage
just test path/to/test.py::TestClass::test_method  # Specific test
```

### Test Structure

```python
import pytest
from apps.users.services import user_create

class TestUserCreate:
    def test_creates_user_with_valid_data(self, db):
        user = user_create(email="test@example.com", password="secure123")
        assert user.email == "test@example.com"
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run `just check` (lint + format check)
4. Run `just test` to ensure tests pass
5. Open a PR with a clear description

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add password reset email functionality
fix: handle duplicate email registration
docs: update API reference for auth endpoints
```
