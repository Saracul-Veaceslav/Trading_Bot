"""
Event system module for the Abidance trading bot.

This module provides event handling functionality for the Abidance trading bot,
including event emission, event handling, and event filtering.
"""

import time
import logging
from typing import Any, Dict, List, Callable, Optional, Union, TypeVar, Generic

logger = logging.getLogger(__name__)

# Type definitions
EventData = Dict[str, Any]
EventHandler = Callable[['Event'], None]
EventFilter = Callable[['Event'], bool]

T = TypeVar('T')


class Event:
    """
    Event class representing an event in the system.
    
    An event has a type, data, and optional metadata such as timestamp and source.
    """
    
    def __init__(
        self,
        type: str,
        data: EventData,
        timestamp: Optional[float] = None,
        source: Optional[str] = None
    ):
        """
        Initialize an event.
        
        Args:
            type: Event type
            data: Event data
            timestamp: Event timestamp (defaults to current time)
            source: Event source
        """
        self.type = type
        self.data = data
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.source = source
    
    def __str__(self) -> str:
        """Return a string representation of the event."""
        return f"Event(type={self.type}, data={self.data}, timestamp={self.timestamp}, source={self.source})"
    
    def __repr__(self) -> str:
        """Return a string representation of the event."""
        return self.__str__()


class EventSystem:
    """
    Event system for the Abidance trading bot.
    
    The event system allows components to emit events and register handlers for events.
    Handlers can be filtered to only receive events that match certain criteria.
    Events can be propagated to parent event types.
    """
    
    def __init__(self):
        """Initialize the event system."""
        self._handlers: Dict[str, List[EventHandler]] = {}
    
    def register_handler(
        self,
        event_type: str,
        handler: EventHandler,
        event_filter: Optional[EventFilter] = None
    ) -> None:
        """
        Register a handler for an event type.
        
        Args:
            event_type: Type of event to handle
            handler: Function to handle the event
            event_filter: Optional filter to apply to events before handling
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # If a filter is provided, wrap the handler with the filter
        if event_filter is not None:
            original_handler = handler
            
            def filtered_handler(event: Event) -> None:
                if event_filter(event):
                    original_handler(event)
            
            handler = filtered_handler
        
        self._handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event type: {event_type}")
    
    def unregister_handler(self, event_type: str, handler: EventHandler) -> None:
        """
        Unregister a handler for an event type.
        
        Args:
            event_type: Type of event
            handler: Handler to unregister
        """
        if event_type in self._handlers:
            # Try to find the handler in the list
            # Note: This might not work for wrapped handlers with filters
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for event type: {event_type}")
    
    def clear_handlers(self, event_type: str) -> None:
        """
        Clear all handlers for an event type.
        
        Args:
            event_type: Type of event
        """
        if event_type in self._handlers:
            self._handlers[event_type] = []
            logger.debug(f"Cleared all handlers for event type: {event_type}")
    
    def clear_all_handlers(self) -> None:
        """Clear all handlers for all event types."""
        self._handlers = {}
        logger.debug("Cleared all handlers for all event types")
    
    def emit(
        self,
        event_type: str,
        event_data: EventData,
        timestamp: Optional[float] = None,
        source: Optional[str] = None,
        propagate: bool = False
    ) -> None:
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            event_data: Data for the event
            timestamp: Optional timestamp for the event
            source: Optional source of the event
            propagate: Whether to propagate the event to parent event types
        """
        event = Event(event_type, event_data, timestamp, source)
        logger.debug(f"Emitting event: {event}")
        
        # Call handlers for this event type
        self._call_handlers(event_type, event)
        
        # If propagation is enabled, call handlers for parent event types
        if propagate and '.' in event_type:
            parent_type = event_type.rsplit('.', 1)[0]
            self._call_handlers(parent_type, event)
    
    def _call_handlers(self, event_type: str, event: Event) -> None:
        """
        Call all handlers for an event type.
        
        Args:
            event_type: Type of event
            event: Event to handle
        """
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    def get_handlers(self) -> Dict[str, List[EventHandler]]:
        """
        Get all registered handlers.
        
        Returns:
            Dictionary mapping event types to lists of handlers
        """
        return self._handlers 