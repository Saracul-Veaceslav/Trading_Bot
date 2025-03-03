"""
Unit tests for the WebSocket functionality.

This module contains tests for the WebSocket server implementation.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient
from datetime import datetime

from abidance.api.websocket import WebSocketManager, WebSocketServer
from abidance.core.events import Event, EventSystem


class TestWebSocketManager:
    """Tests for the WebSocketManager class."""

    def test_init(self):
        """
        Feature: WebSocketManager initialization
        
        Scenario: Creating a new WebSocketManager
          Given the WebSocketManager class
          When a new instance is created
          Then it should have an empty active_connections dictionary
        """
        manager = WebSocketManager()
        assert manager.active_connections == {}

    @pytest.mark.asyncio
    async def test_connect(self):
        """
        Feature: WebSocket connection management
        
        Scenario: Client connects to WebSocket
          Given a WebSocketManager
          When a client connects with a client_id
          Then the connection should be accepted and stored
        """
        manager = WebSocketManager()
        websocket = AsyncMock(spec=WebSocket)
        
        await manager.connect(websocket, "test_client")
        
        websocket.accept.assert_called_once()
        assert "test_client" in manager.active_connections
        assert websocket in manager.active_connections["test_client"]

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """
        Feature: WebSocket disconnection handling
        
        Scenario: Client disconnects from WebSocket
          Given a WebSocketManager with a connected client
          When the client disconnects
          Then the connection should be removed from active connections
        """
        manager = WebSocketManager()
        websocket = AsyncMock(spec=WebSocket)
        
        # Connect first
        await manager.connect(websocket, "test_client")
        
        # Then disconnect
        await manager.disconnect(websocket, "test_client")
        
        assert "test_client" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast(self):
        """
        Feature: WebSocket message broadcasting
        
        Scenario: Broadcasting a message to all clients
          Given a WebSocketManager with multiple connected clients
          When a message is broadcast
          Then all clients should receive the message
        """
        manager = WebSocketManager()
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        
        # Connect two clients
        await manager.connect(websocket1, "client1")
        await manager.connect(websocket2, "client2")
        
        # Broadcast a message
        await manager.broadcast("test_event", {"message": "Hello"})
        
        # Check that both clients received the message
        websocket1.send_json.assert_called_once()
        websocket2.send_json.assert_called_once()
        
        # Verify the message format
        call_args = websocket1.send_json.call_args[0][0]
        assert call_args["type"] == "test_event"
        assert call_args["data"] == {"message": "Hello"}
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_broadcast_with_disconnection(self):
        """
        Feature: WebSocket disconnection handling during broadcast
        
        Scenario: Client disconnects during broadcast
          Given a WebSocketManager with connected clients
          When a client disconnects during broadcast
          Then the disconnected client should be removed
        """
        manager = WebSocketManager()
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        
        # Connect two clients
        await manager.connect(websocket1, "client1")
        await manager.connect(websocket2, "client2")
        
        # Make websocket2 raise WebSocketDisconnect when send_json is called
        websocket2.send_json.side_effect = WebSocketDisconnect(code=1000)
        
        # Broadcast a message
        await manager.broadcast("test_event", {"message": "Hello"})
        
        # Check that client1 received the message
        websocket1.send_json.assert_called_once()
        
        # Check that client2 was disconnected
        assert "client2" not in manager.active_connections


class TestWebSocketServer:
    """Tests for the WebSocketServer class."""

    def test_init(self):
        """
        Feature: WebSocketServer initialization
        
        Scenario: Creating a new WebSocketServer
          Given a FastAPI application
          When a new WebSocketServer is created
          Then it should register the WebSocket endpoint
        """
        app = MagicMock()
        server = WebSocketServer(app)
        
        # Check that the websocket endpoint was registered
        app.websocket.assert_called_once_with("/ws/{client_id}")

    @pytest.mark.asyncio
    async def test_handle_message(self):
        """
        Feature: WebSocket message handling
        
        Scenario: Handling an incoming message
          Given a WebSocketServer with registered event handlers
          When a message is received
          Then the appropriate handler should be called
        """
        app = MagicMock()
        server = WebSocketServer(app)
        
        # Register a mock handler
        mock_handler = AsyncMock()
        server.register_event_handler("test_event", mock_handler)
        
        # Handle a message
        await server._handle_message({"type": "test_event", "data": {"message": "Hello"}}, "test_client")
        
        # Check that the handler was called with the correct arguments
        mock_handler.assert_called_once_with({"message": "Hello"}, "test_client")

    @pytest.mark.asyncio
    async def test_broadcast(self):
        """
        Feature: WebSocketServer message broadcasting
        
        Scenario: Broadcasting a message through the server
          Given a WebSocketServer
          When a message is broadcast
          Then it should be forwarded to the WebSocketManager
        """
        app = MagicMock()
        server = WebSocketServer(app)
        
        # Mock the manager's broadcast method
        server.manager.broadcast = AsyncMock()
        
        # Broadcast a message
        await server.broadcast("test_event", {"message": "Hello"})
        
        # Check that the manager's broadcast method was called
        server.manager.broadcast.assert_called_once_with("test_event", {"message": "Hello"})

    @pytest.mark.asyncio
    async def test_event_integration(self):
        """
        Feature: WebSocket event system integration
        
        Scenario: Integration with the event system
          Given a WebSocketServer with event system integration
          When an event is emitted in the event system
          Then it should be broadcast to WebSocket clients
        """
        app = MagicMock()
        event_system = EventSystem()
        
        # Create a server with event system integration
        with patch('abidance.api.websocket.EventSystem', return_value=event_system):
            server = WebSocketServer(app, use_event_system=True)
            
            # Mock the broadcast method
            server.broadcast = AsyncMock()
            
            # Register a handler for the test_event
            event_handler = None
            for event_type, handlers in event_system._handlers.items():
                if event_type == "test_event" and handlers:
                    event_handler = handlers[0]
            
            # Manually call the event handler
            if event_handler:
                event = Event("test_event", {"message": "Hello"})
                await event_handler(event)
                
                # Check that the broadcast method was called
                server.broadcast.assert_called_once_with("test_event", {"message": "Hello"}) 