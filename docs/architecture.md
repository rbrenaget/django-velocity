# Architecture

Django Velocity follows the **Service-Oriented Architecture** pattern from the [HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

## Overview

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

## Key Principles

### 1. Thin Views

Views handle only:

- Request validation
- Calling the appropriate service or selector
- Formatting the response

```python title="apps/authentication/views.py"
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Delegate to service - view is thin!
        result = services.register_user(**serializer.validated_data)

        return Response(RegisterOutputSerializer(result).data, status=201)
```

### 2. Services (Write Operations)

Services contain business logic for operations that modify state:

```python title="apps/authentication/services.py"
from apps.core.services import service
from apps.core.exceptions import ValidationError

@service
def register_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = ""
) -> dict:
    """Register a new user and return JWT tokens."""
    if user_get_by_email(email=email):
        raise ValidationError("Email already registered")

    user = User.objects.create_user(email=email, password=password)
    tokens = generate_tokens_for_user(user)
    return {"user": user, **tokens}
```

!!! tip "Service Decorator"
    The `@service` decorator wraps the function in a database transaction and provides consistent error handling.

### 3. Selectors (Read Operations)

Selectors handle all read operations without side effects:

```python title="apps/users/selectors.py"
def user_get_by_email(*, email: str) -> User | None:
    """Fetch user by email - read only, no side effects."""
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None

def user_list(*, is_active: bool = True) -> QuerySet[User]:
    """List users with optional filters."""
    return User.objects.filter(is_active=is_active)
```

### 4. Anemic Models

Models define schema only - no business logic:

```python title="apps/users/models.py"
class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]
```

## Why This Architecture?

| Traditional Django | Service-Oriented |
|-------------------|------------------|
| Fat models with logic | Anemic models (schema only) |
| Logic scattered in views | Business logic in dedicated services |
| Hard to test | Unit tests for services/selectors |
| Difficult to maintain | Clear separation of concerns |

## Project Structure

```
apps/
├── core/                   # Shared utilities
│   ├── exceptions.py       # Business exception hierarchy
│   ├── models.py           # BaseModel with timestamps
│   ├── services.py         # @service decorator
│   └── api.py              # Django Ninja setup
│
├── authentication/         # Authentication domain
│   ├── models.py           # Auth-related models
│   ├── services.py         # register_user, login_user...
│   ├── selectors.py        # Auth queries
│   ├── serializers.py      # Request/Response serializers
│   └── views.py            # API endpoints
│
└── users/                  # User domain
    ├── models.py           # Custom User model
    ├── services.py         # user_update, user_change_password...
    ├── selectors.py        # user_get_by_email, user_list...
    └── views.py            # User profile endpoints
```
