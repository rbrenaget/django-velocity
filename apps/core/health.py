"""
Health check views for monitoring and container health.
"""

from django.db import connection
from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    """
    Health check endpoint for container orchestration and load balancers.

    Returns a 200 OK response when the service is healthy.
    Returns a 503 Service Unavailable if critical services are down.

    Note: Does not expose detailed service status for security reasons.
    """

    def get(self, request):
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            return JsonResponse({"status": "unhealthy"}, status=503)

        # Check Redis/cache (optional)
        try:
            from django.core.cache import cache

            cache.set("health_check", "ok", timeout=1)
            cache.get("health_check")
        except Exception:
            # Cache failure is not critical for liveness
            pass

        return JsonResponse({"status": "healthy"}, status=200)


def health_check_simple(request):
    """
    Simple health check for basic liveness probes.
    Only checks if the Django app is responding.
    """
    return JsonResponse({"status": "ok"}, status=200)
