# Authentication API

Endpoints for user registration, login, and password management.

## Register

Create a new user account.

```http
POST /api/v1/auth/register/
```

### Request Body

```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Response (201 Created)

```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Login

Authenticate and receive JWT tokens.

```http
POST /api/v1/auth/login/
```

### Request Body

```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

### Response (200 OK)

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Refresh Token

Get a new access token using the refresh token.

```http
POST /api/v1/auth/token/refresh/
```

### Request Body

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Response (200 OK)

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Forgot Password

Request a password reset email.

```http
POST /api/v1/auth/forgot-password/
```

### Request Body

```json
{
    "email": "user@example.com"
}
```

### Response (200 OK)

```json
{
    "detail": "Password reset email sent"
}
```

---

## Reset Password

Reset password using the token from email.

```http
POST /api/v1/auth/reset-password/
```

### Request Body

```json
{
    "token": "reset-token-from-email",
    "password": "newpassword123"
}
```

### Response (200 OK)

```json
{
    "detail": "Password reset successful"
}
```

---

## Change Password

Change password for authenticated user.

!!! note "Authentication Required"
    This endpoint requires a valid access token.

```http
POST /api/v1/auth/change-password/
Authorization: Bearer <access_token>
```

### Request Body

```json
{
    "old_password": "currentpassword",
    "new_password": "newpassword123"
}
```

### Response (200 OK)

```json
{
    "detail": "Password changed successfully"
}
```
