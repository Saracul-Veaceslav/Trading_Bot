"""
Event handlers module for the Abidance trading bot.

This module provides specialized event handlers and handler registration utilities
that work with the event system defined in the events module.
"""

import logging
from typing import Dict, List, Callable, Optional, Type, TypeVar, Generic, Any, Union
from dataclasses import dataclass, field

from abidance.core.events import Event, EventSystem, EventHandler, EventFilter, EventData

logger = logging.getLogger(__name__)

T = TypeVar('T')


class EventHandlerRegistry:
    """
    Registry for event handlers that provides a centralized way to register and manage handlers.
    
    This class works with the EventSystem to provide a more structured way to register
    and manage event handlers across the application.
    """
    
    def __init__(self, event_system: EventSystem):
        """
        Initialize the event handler registry.
        
        Args:
            event_system: The event system to register handlers with
        """
        self._event_system = event_system
        self._registered_handlers: Dict[str, List[EventHandler]] = {}
    
    def register(
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
        # Register with the event system
        self._event_system.register_handler(event_type, handler, event_filter)
        
        # Keep track of registered handlers
        if event_type not in self._registered_handlers:
            self._registered_handlers[event_type] = []
        self._registered_handlers[event_type].append(handler)
        
        logger.debug(f"Registered handler for event type: {event_type} in registry")
    
    def unregister(self, event_type: str, handler: EventHandler) -> None:
        """
        Unregister a handler for an event type.
        
        Args:
            event_type: Type of event
            handler: Handler to unregister
        """
        # Unregister from the event system
        self._event_system.unregister_handler(event_type, handler)
        
        # Remove from our tracking
        if event_type in self._registered_handlers:
            if handler in self._registered_handlers[event_type]:
                self._registered_handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for event type: {event_type} from registry")
    
    def unregister_all(self, event_type: Optional[str] = None) -> None:
        """
        Unregister all handlers, optionally for a specific event type.
        
        Args:
            event_type: Optional event type to unregister handlers for
        """
        if event_type is not None:
            # Unregister all handlers for the specified event type
            if event_type in self._registered_handlers:
                for handler in self._registered_handlers[event_type]:
                    self._event_system.unregister_handler(event_type, handler)
                self._registered_handlers[event_type] = []
                logger.debug(f"Unregistered all handlers for event type: {event_type} from registry")
        else:
            # Unregister all handlers for all event types
            for event_type, handlers in self._registered_handlers.items():
                for handler in handlers:
                    self._event_system.unregister_handler(event_type, handler)
            self._registered_handlers = {}
            logger.debug("Unregistered all handlers from registry")
    
    def get_registered_handlers(self) -> Dict[str, List[EventHandler]]:
        """
        Get all registered handlers.
        
        Returns:
            Dictionary mapping event types to lists of handlers
        """
        return self._registered_handlers


@dataclass
class EventSubscription:
    """
    Represents a subscription to an event.
    
    This class can be used to manage event subscriptions and easily unsubscribe.
    """
    
    event_type: str
    handler: EventHandler
    registry: EventHandlerRegistry
    
    def unsubscribe(self) -> None:
        """Unsubscribe from the event."""
        self.registry.unregister(self.event_type, self.handler)


class EventHandlerGroup:
    """
    A group of event handlers that can be registered and unregistered together.
    
    This class is useful for components that need to register multiple event handlers
    and want to manage them as a group.
    """
    
    def __init__(self, registry: EventHandlerRegistry):
        """
        Initialize the event handler group.
        
        Args:
            registry: The event handler registry to register handlers with
        """
        self._registry = registry
        self._subscriptions: List[EventSubscription] = []
    
    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        event_filter: Optional[EventFilter] = None
    ) -> EventSubscription:
        """
        Subscribe to an event.
        
        Args:
            event_type: Type of event to handle
            handler: Function to handle the event
            event_filter: Optional filter to apply to events before handling
            
        Returns:
            An EventSubscription object that can be used to unsubscribe
        """
        self._registry.register(event_type, handler, event_filter)
        subscription = EventSubscription(event_type, handler, self._registry)
        self._subscriptions.append(subscription)
        return subscription
    
    def unsubscribe_all(self) -> None:
        """Unsubscribe from all events."""
        for subscription in self._subscriptions:
            subscription.unsubscribe()
        self._subscriptions = []


# Decorator for registering event handlers
def event_handler(
    event_type: str,
    registry: EventHandlerRegistry,
    event_filter: Optional[EventFilter] = None
) -> Callable[[EventHandler], EventHandler]:
    """
    Decorator for registering event handlers.
    
    Args:
        event_type: Type of event to handle
        registry: Registry to register the handler with
        event_filter: Optional filter to apply to events before handling
        
    Returns:
        Decorator function
    """
    def decorator(handler: EventHandler) -> EventHandler:
        registry.register(event_type, handler, event_filter)
        return handler
    return decorator 