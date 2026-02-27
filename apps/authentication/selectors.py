"""
Authentication Selectors - Read operations for authentication domain.

Selectors are responsible for:
- Fetching data from the database
- Complex filtering and aggregations
- Returning QuerySets or single objects

IMPORTANT: Selectors should NEVER modify data.

Note: User lookups (user_get_by_email, etc.) live in apps.users.selectors
since they belong to the User domain. This module is for auth-specific
read operations (e.g., token lookups, email confirmation queries).
"""
