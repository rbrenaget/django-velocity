"""
WebSocket consumers for core app.

Consumers are simple interfaces—business logic should live in services.
"""

from typing import ClassVar

from channels.generic.websocket import JsonWebsocketConsumer


class EchoConsumer(JsonWebsocketConsumer):
    """
    Simple echo consumer for testing WebSocket connectivity.

    Echoes back any JSON message received with a type prefix.
    """

    groups: ClassVar[list[str]] = []

    def connect(self) -> None:
        """Accept WebSocket connection."""
        self.accept()

    def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnect."""
        pass

    def receive_json(self, content: dict) -> None:
        """Echo back received JSON with type prefix."""
        self.send_json(
            {
                "type": "echo",
                **content,
            }
        )
