# API Reference

Django Velocity provides RESTful APIs built with Django REST Framework.

## Base URL

All API endpoints are prefixed with:

```
/api/v1/
```

## Authentication

Most endpoints require JWT authentication. Include the access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

## Available Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login, get JWT tokens |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |
| POST | `/api/v1/auth/forgot-password/` | Request password reset |
| POST | `/api/v1/auth/reset-password/` | Confirm password reset |
| POST | `/api/v1/auth/verify-email/` | Verify email address |
| POST | `/api/v1/auth/change-password/` | Change password (auth required) |

[Learn more →](authentication.md)

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me/` | Get current user |
| PATCH | `/api/v1/users/me/` | Update profile |

[Learn more →](users.md)

## Error Responses

All errors follow a consistent format:

```json
{
    "detail": "Error message here",
    "code": "error_code"
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Business rule violation |
