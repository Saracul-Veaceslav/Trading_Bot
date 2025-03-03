"""
API module for the Abidance trading bot.

This module provides interfaces for interacting with the trading bot
through HTTP and WebSocket APIs.
"""

# Define classes to be exported
class APIServer:
    """
    HTTP API server for the trading bot.
    """
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.routes = {}

    def add_route(self, path, handler, methods=None):
        """
        Add a route to the API server.

        Args:
            path: URL path
            handler: Function to handle the request
            methods: HTTP methods to support (GET, POST, etc.)
        """
        if methods is None:
            methods = ["GET"]
        self.routes[path] = {"handler": handler, "methods": methods}

    def start(self):
        """
        Start the API server.
        """
        # Placeholder implementation
        pass

    def stop(self):
        """
        Stop the API server.
        """
        # Placeholder implementation
        pass


class WebSocketServer:
    """
    WebSocket server for real-time communication.
    """
    def __init__(self, host="0.0.0.0", port=5001):
        self.host = host
        self.port = port
        self.clients = set()

    def start(self):
        """
        Start the WebSocket server.
        """
        # Placeholder implementation
        pass

    def stop(self):
        """
        Stop the WebSocket server.
        """
        # Placeholder implementation
        pass

    def broadcast(self, message):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast
        """
        # Placeholder implementation
        pass


# Define what's available when doing "from abidance.api import *"

__all__ = [
    "APIServer",
    "WebSocketServer",
]
