# Security & Compliance

Django Velocity includes enterprise-grade security features for production environments.

## Features

| Feature | Description |
|---------|-------------|
| Session Management | Track and revoke active sessions remotely |
| IP Allowlisting | Restrict admin access by IP address |
| Security Headers | CSP, HSTS, X-Frame-Options, Referrer-Policy |
| Password Policies | Strength validation + breach checking (HIBP) |
| GDPR Compliance | Data export and account deletion |
| CORS | Cross-Origin Resource Sharing |

---

## Session Management

Users can view and manage their active sessions.

### API Endpoints

```
GET    /api/v1/security/sessions/           # List active sessions
DELETE /api/v1/security/sessions/<key>/     # Revoke specific session
POST   /api/v1/security/sessions/revoke-all/ # Revoke all other sessions
```

### Example Response

```json
[
  {
    "session_key": "abc123...",
    "device_info": "Chrome on Windows",
    "ip_address": "192.168.1.1",
    "last_activity": "2024-01-15T10:30:00Z",
    "is_current": true
  }
]
```

---

## IP Allowlisting

Restrict admin panel access to trusted IP addresses.

### How It Works

1. If **no active entries** exist → all IPs allowed (open access)
2. If **active entries exist** → only listed IPs can access `/admin/`

### API Endpoints (Admin Only)

```
GET  /api/v1/security/ip-allowlist/         # List all entries
POST /api/v1/security/ip-allowlist/         # Add IP
DELETE /api/v1/security/ip-allowlist/<ip>/  # Remove IP
```

### Configuration

```bash
# Disable IP restriction entirely
ADMIN_IP_RESTRICTION_ENABLED=false
```

---

## Security Headers Middleware

Automatically adds security headers to all responses.

### Headers Added

| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Restricts sensitive APIs |
| `Content-Security-Policy` | Configurable |
| `Strict-Transport-Security` | HTTPS only (prod) |

### Configuration

```bash
# Disable headers
SECURITY_HEADERS_ENABLED=false

# Custom CSP
SECURITY_CSP_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline'"

# HSTS duration (seconds)
SECURITY_HSTS_SECONDS=31536000  # 1 year
```

---

## Password Policies

Two custom validators enhance password security.

### PasswordStrengthValidator

Requires passwords to contain:
- Minimum 12 characters
- Uppercase letter
- Lowercase letter
- Digit
- Special character
- Minimum entropy (30 bits)

### BreachCheckValidator

Checks passwords against [Have I Been Pwned](https://haveibeenpwned.com/) using k-anonymity (only first 5 chars of hash sent).

### Configuration

```bash
# Disable breach checking
PASSWORD_BREACH_CHECK_ENABLED=false

# Minimum breach count to reject (default: 1)
PASSWORD_BREACH_THRESHOLD=5
```

---

## GDPR Compliance

Services and endpoints for data privacy compliance.

### Data Export

```
POST /api/v1/security/gdpr/export/
```

Returns all user data as JSON:
- Profile information
- Session history
- Group memberships
- Permissions

### Account Deletion

```
POST /api/v1/security/gdpr/delete-account/
Content-Type: application/json

{
  "confirmation": "user@example.com",
  "password": "current_password"
}
```

**Warning:** This permanently deletes the account and all associated data.

---

## CORS Configuration

Cross-Origin Resource Sharing for frontend applications.

### Configuration

```bash
# Production - specify allowed origins
CORS_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com

# Development - allow all origins
CORS_ALLOW_ALL_ORIGINS=true

# Allow credentials (cookies, auth headers)
CORS_ALLOW_CREDENTIALS=true
```

---

## Middleware Order

Security middleware is positioned for optimal protection:

```python
MIDDLEWARE = [
    "apps.security.middleware.SecurityHeadersMiddleware",  # First - add headers
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",               # After session
    # ... other middleware ...
    "apps.security.middleware.SessionTrackingMiddleware",  # After auth
    "apps.security.middleware.AdminIPRestrictionMiddleware",
]
```

---

## Celery Tasks

### Session Cleanup

Automatically clean up inactive sessions:

```python
from apps.security.tasks import cleanup_expired_sessions

# Run manually
cleanup_expired_sessions.delay()

# Configure timeout (default: 7 days)
SESSION_INACTIVITY_TIMEOUT=604800
```

Schedule in Celery Beat for automatic cleanup.
