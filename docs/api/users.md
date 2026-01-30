# Users API

Endpoints for user profile management.

!!! note "Authentication Required"
    All endpoints in this section require a valid access token.

## Get Current User

Retrieve the authenticated user's profile.

```http
GET /api/v1/users/me/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2026-01-15T10:30:00Z",
    "is_active": true
}
```

---

## Update Profile

Update the authenticated user's profile information.

```http
PATCH /api/v1/users/me/
Authorization: Bearer <access_token>
```

### Request Body

All fields are optional:

```json
{
    "first_name": "Jane",
    "last_name": "Smith"
}
```

### Response (200 OK)

```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "date_joined": "2026-01-15T10:30:00Z",
    "is_active": true
}
```

---

## Error Responses

### 401 Unauthorized

Returned when the access token is invalid or expired:

```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid"
}
```

### 403 Forbidden

Returned when the user doesn't have permission:

```json
{
    "detail": "You do not have permission to perform this action."
}
```
