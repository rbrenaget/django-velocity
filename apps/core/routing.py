"""
WebSocket URL routing for core app.
"""

from django.urls import path

from apps.core.consumers import EchoConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
]
