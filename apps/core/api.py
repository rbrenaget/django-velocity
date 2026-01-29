"""
Django Ninja API Setup - Optional alternative to DRF.

This provides the Ninja API instance that can be used across the app.
Enable by adding routes in config/urls.py.

Usage:
    from apps.core.api import api

    @api.get("/health")
    def health_check(request):
        return {"status": "ok"}
"""

from ninja import NinjaAPI

from apps.core.exceptions import ApplicationError

api = NinjaAPI(
    title="Django Velocity API",
    version="1.0.0",
    description="Modern Django API with Service-Oriented Architecture",
    urls_namespace="ninja",
)


@api.exception_handler(ApplicationError)
def handle_application_error(request, exc: ApplicationError):
    """
    Global exception handler for ApplicationError in Ninja.
    """
    return api.create_response(
        request,
        {
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "extra": exc.extra,
            }
        },
        status=exc.status_code,
    )


# Health check endpoint
@api.get("/health", tags=["System"])
def health_check(request):
    """
    Health check endpoint for load balancers and monitoring.
    """
    return {"status": "healthy", "version": "1.0.0"}
