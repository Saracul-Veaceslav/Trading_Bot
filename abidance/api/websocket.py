"""
WebSocket server implementation for the Abidance trading bot.

This module provides real-time communication capabilities for the trading bot.
"""

from typing import Dict, Set, Any, Optional, Callable, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from datetime import datetime
from ..core.events import EventSystem, Event

class WebSocketManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Handle new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            client_id: Unique identifier for the client
        """
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        
    async def disconnect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Handle WebSocket disconnection.
        
        Args:
            websocket: The WebSocket connection
            client_id: Unique identifier for the client
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
            
    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast message to all connected clients.
        
        Args:
            event_type: Type of event being broadcast
            data: Data to broadcast
        """
        message = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        disconnected = []
        
        for client_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    disconnected.append((connection, client_id))
        
        # Clean up disconnected clients
        for connection, client_id in disconnected:
            await self.disconnect(connection, client_id)

class WebSocketServer:
    """
    WebSocket server for the Abidance trading bot.
    
    This class provides real-time communication capabilities for the trading bot.
    """
    
    def __init__(self, app: FastAPI, use_event_system: bool = False):
        """
        Initialize the WebSocket server.
        
        Args:
            app: FastAPI application instance
            use_event_system: Whether to integrate with the event system
        """
        self.app = app
        self.manager = WebSocketManager()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.use_event_system = use_event_system
        
        # Initialize event system integration if requested
        if use_event_system:
            self.event_system = EventSystem()
            self._setup_event_handlers()
        
        # Register WebSocket endpoint
        @app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            try:
                await self.manager.connect(websocket, client_id)
                while True:
                    data = await websocket.receive_json()
                    await self._handle_message(data, client_id)
            except WebSocketDisconnect:
                await self.manager.disconnect(websocket, client_id)
    
    def _setup_event_handlers(self) -> None:
        """Set up handlers for events from the event system."""
        async def event_handler(event: Event) -> None:
            # Convert event to WebSocket message and broadcast
            await self.broadcast(event.type, event.data)
        
        # Register handler for common event types
        event_types = [
            "trade", "order", "position", "balance", "error", 
            "strategy", "market", "system", "test_event"
        ]
        for event_type in event_types:
            self.event_system.register_handler(event_type, event_handler)
    
    async def _handle_message(self, data: Dict[str, Any], client_id: str) -> None:
        """
        Handle incoming WebSocket message.
        
        Args:
            data: Message data
            client_id: Client identifier
        """
        event_type = data.get('type')
        if event_type and event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                await handler(data.get('data', {}), client_id)
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event is received
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            event_type: Type of event to broadcast
            data: Data to broadcast
        """
        await self.manager.broadcast(event_type, data) 