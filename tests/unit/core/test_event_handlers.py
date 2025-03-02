"""
Tests for the event_handlers module.

This module contains tests for the event handlers functionality provided
by the event_handlers module.
"""

import pytest
from typing import Dict, List, Any
from unittest.mock import Mock, call

from abidance.core.events import EventSystem, Event
from abidance.core.event_handlers import (
    EventHandlerRegistry, EventSubscription, EventHandlerGroup, event_handler
)


class TestEventHandlerRegistry:
    """Tests for the EventHandlerRegistry class."""

    def test_registry_creation(self):
        """Test creating an EventHandlerRegistry instance."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        assert registry is not None
        assert isinstance(registry, EventHandlerRegistry)
        assert registry.get_registered_handlers() == {}

    def test_register_handler(self):
        """Test registering a handler with the registry."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        # Create a mock handler
        handler = Mock()
        
        # Register the handler
        registry.register("test_event", handler)
        
        # Verify the handler was registered in the registry
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert handler in registered_handlers["test_event"]
        
        # Verify the handler was registered in the event system
        event_system_handlers = event_system.get_handlers()
        assert "test_event" in event_system_handlers
        assert handler in event_system_handlers["test_event"]

    def test_unregister_handler(self):
        """Test unregistering a handler from the registry."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        # Create a mock handler
        handler = Mock()
        
        # Register the handler
        registry.register("test_event", handler)
        
        # Unregister the handler
        registry.unregister("test_event", handler)
        
        # Verify the handler was unregistered from the registry
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert handler not in registered_handlers["test_event"]
        
        # Verify the handler was unregistered from the event system
        event_system_handlers = event_system.get_handlers()
        assert "test_event" in event_system_handlers
        assert handler not in event_system_handlers["test_event"]

    def test_unregister_all_for_event_type(self):
        """Test unregistering all handlers for a specific event type."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Register the handlers
        registry.register("test_event", handler1)
        registry.register("test_event", handler2)
        registry.register("other_event", Mock())
        
        # Unregister all handlers for test_event
        registry.unregister_all("test_event")
        
        # Verify the handlers were unregistered from the registry
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert len(registered_handlers["test_event"]) == 0
        assert "other_event" in registered_handlers
        assert len(registered_handlers["other_event"]) == 1
        
        # Verify the handlers were unregistered from the event system
        event_system_handlers = event_system.get_handlers()
        assert "test_event" in event_system_handlers
        assert len(event_system_handlers["test_event"]) == 0
        assert "other_event" in event_system_handlers
        assert len(event_system_handlers["other_event"]) == 1

    def test_unregister_all(self):
        """Test unregistering all handlers for all event types."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Register the handlers
        registry.register("test_event", handler1)
        registry.register("other_event", handler2)
        
        # Unregister all handlers
        registry.unregister_all()
        
        # Verify all handlers were unregistered from the registry
        registered_handlers = registry.get_registered_handlers()
        assert registered_handlers == {}
        
        # Verify all handlers were unregistered from the event system
        event_system_handlers = event_system.get_handlers()
        assert "test_event" in event_system_handlers
        assert len(event_system_handlers["test_event"]) == 0
        assert "other_event" in event_system_handlers
        assert len(event_system_handlers["other_event"]) == 0


class TestEventSubscription:
    """Tests for the EventSubscription class."""

    def test_subscription_creation(self):
        """Test creating an EventSubscription instance."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        handler = Mock()
        
        subscription = EventSubscription("test_event", handler, registry)
        
        assert subscription is not None
        assert isinstance(subscription, EventSubscription)
        assert subscription.event_type == "test_event"
        assert subscription.handler == handler
        assert subscription.registry == registry

    def test_unsubscribe(self):
        """Test unsubscribing from an event."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        handler = Mock()
        
        # Register the handler
        registry.register("test_event", handler)
        
        # Create a subscription
        subscription = EventSubscription("test_event", handler, registry)
        
        # Unsubscribe
        subscription.unsubscribe()
        
        # Verify the handler was unregistered
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert handler not in registered_handlers["test_event"]


class TestEventHandlerGroup:
    """Tests for the EventHandlerGroup class."""

    def test_group_creation(self):
        """Test creating an EventHandlerGroup instance."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        group = EventHandlerGroup(registry)
        
        assert group is not None
        assert isinstance(group, EventHandlerGroup)

    def test_subscribe(self):
        """Test subscribing to an event with a group."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        group = EventHandlerGroup(registry)
        
        # Create a mock handler
        handler = Mock()
        
        # Subscribe to an event
        subscription = group.subscribe("test_event", handler)
        
        # Verify the subscription was created
        assert subscription is not None
        assert isinstance(subscription, EventSubscription)
        assert subscription.event_type == "test_event"
        assert subscription.handler == handler
        
        # Verify the handler was registered
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert handler in registered_handlers["test_event"]

    def test_unsubscribe_all(self):
        """Test unsubscribing from all events in a group."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        group = EventHandlerGroup(registry)
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Subscribe to events
        group.subscribe("test_event", handler1)
        group.subscribe("other_event", handler2)
        
        # Unsubscribe from all events
        group.unsubscribe_all()
        
        # Verify the handlers were unregistered
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert handler1 not in registered_handlers["test_event"]
        assert "other_event" in registered_handlers
        assert handler2 not in registered_handlers["other_event"]


class TestEventHandlerDecorator:
    """Tests for the event_handler decorator."""

    def test_event_handler_decorator(self):
        """Test using the event_handler decorator."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        # Define a handler function with the decorator
        @event_handler("test_event", registry)
        def test_handler(event):
            pass
        
        # Verify the handler was registered
        registered_handlers = registry.get_registered_handlers()
        assert "test_event" in registered_handlers
        assert test_handler in registered_handlers["test_event"]

    def test_event_handler_with_filter(self):
        """Test using the event_handler decorator with a filter."""
        event_system = EventSystem()
        registry = EventHandlerRegistry(event_system)
        
        # Create a mock handler
        mock_handler = Mock()
        
        # Define a filter function
        def test_filter(event):
            return event.data.get("value", 0) > 10
        
        # Register the handler with the filter directly
        registry.register("test_event", mock_handler, test_filter)
        
        # Emit events
        event_system.emit("test_event", {"value": 5})
        event_system.emit("test_event", {"value": 15})
        
        # Verify the handler was called only for the event that passed the filter
        assert mock_handler.call_count == 1
        
        # Verify the handler was called with the correct event
        called_event = mock_handler.call_args[0][0]
        assert called_event.data.get("value") == 15 