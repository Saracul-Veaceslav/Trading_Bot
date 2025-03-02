"""
Tests for the EventSystem class.

This module contains tests for the EventSystem class, which provides
event handling functionality for the Abidance trading bot.
"""

import pytest
from typing import Any, Dict, List, Callable, Optional
from unittest.mock import Mock, call

from abidance.core.events import EventSystem, Event, EventHandler, EventFilter


class TestEventSystem:
    """Tests for the EventSystem class."""

    def test_event_system_creation(self):
        """Test creating an EventSystem instance."""
        event_system = EventSystem()
        assert event_system is not None
        assert isinstance(event_system, EventSystem)
        assert len(event_system.get_handlers()) == 0

    def test_register_handler(self):
        """Test registering an event handler."""
        event_system = EventSystem()
        
        # Create a mock handler
        handler = Mock()
        
        # Register the handler for a specific event type
        event_system.register_handler("test_event", handler)
        
        # Verify the handler was registered
        handlers = event_system.get_handlers()
        assert "test_event" in handlers
        assert handler in handlers["test_event"]
        assert len(handlers["test_event"]) == 1

    def test_register_multiple_handlers(self):
        """Test registering multiple handlers for the same event type."""
        event_system = EventSystem()
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Register the handlers for the same event type
        event_system.register_handler("test_event", handler1)
        event_system.register_handler("test_event", handler2)
        
        # Verify both handlers were registered
        handlers = event_system.get_handlers()
        assert "test_event" in handlers
        assert handler1 in handlers["test_event"]
        assert handler2 in handlers["test_event"]
        assert len(handlers["test_event"]) == 2

    def test_register_handler_with_filter(self):
        """Test registering a handler with a filter."""
        event_system = EventSystem()
        
        # Create a mock handler and filter
        handler = Mock()
        event_filter = lambda event: event.data.get("value", 0) > 10
        
        # Register the handler with the filter
        event_system.register_handler("test_event", handler, event_filter)
        
        # Verify the handler and filter were registered
        handlers = event_system.get_handlers()
        assert "test_event" in handlers
        assert len(handlers["test_event"]) == 1
        
        # The handler should be wrapped with the filter
        registered_handler = handlers["test_event"][0]
        assert registered_handler != handler  # It should be wrapped
        
        # Create test events
        event1 = Event("test_event", {"value": 5})
        event2 = Event("test_event", {"value": 15})
        
        # Test the filter
        registered_handler(event1)
        handler.assert_not_called()  # Should not be called for value 5
        
        registered_handler(event2)
        handler.assert_called_once_with(event2)  # Should be called for value 15

    def test_emit_event(self):
        """Test emitting an event."""
        event_system = EventSystem()
        
        # Create a mock handler
        handler = Mock()
        
        # Register the handler
        event_system.register_handler("test_event", handler)
        
        # Emit an event
        event_data = {"key": "value"}
        event_system.emit("test_event", event_data)
        
        # Verify the handler was called with the event
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args.type == "test_event"
        assert call_args.data == event_data

    def test_emit_event_no_handlers(self):
        """Test emitting an event with no registered handlers."""
        event_system = EventSystem()
        
        # Emit an event with no handlers registered
        # This should not raise an exception
        event_system.emit("test_event", {"key": "value"})

    def test_emit_event_multiple_handlers(self):
        """Test emitting an event with multiple handlers."""
        event_system = EventSystem()
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Register the handlers
        event_system.register_handler("test_event", handler1)
        event_system.register_handler("test_event", handler2)
        
        # Emit an event
        event_data = {"key": "value"}
        event_system.emit("test_event", event_data)
        
        # Verify both handlers were called with the event
        handler1.assert_called_once()
        handler2.assert_called_once()
        
        call_args1 = handler1.call_args[0][0]
        call_args2 = handler2.call_args[0][0]
        
        assert call_args1.type == "test_event"
        assert call_args1.data == event_data
        assert call_args2.type == "test_event"
        assert call_args2.data == event_data

    def test_unregister_handler(self):
        """Test unregistering a handler."""
        event_system = EventSystem()
        
        # Create a mock handler
        handler = Mock()
        
        # Register the handler
        event_system.register_handler("test_event", handler)
        
        # Verify the handler was registered
        handlers = event_system.get_handlers()
        assert "test_event" in handlers
        assert len(handlers["test_event"]) == 1
        
        # Unregister the handler
        event_system.unregister_handler("test_event", handler)
        
        # Verify the handler was unregistered
        handlers = event_system.get_handlers()
        assert "test_event" in handlers
        assert len(handlers["test_event"]) == 0
        
        # Emit an event
        event_system.emit("test_event", {"key": "value"})
        
        # Verify the handler was not called
        handler.assert_not_called()

    def test_unregister_nonexistent_handler(self):
        """Test unregistering a handler that was not registered."""
        event_system = EventSystem()
        
        # Create a mock handler
        handler = Mock()
        
        # Unregister a handler that was not registered
        # This should not raise an exception
        event_system.unregister_handler("test_event", handler)

    def test_clear_handlers(self):
        """Test clearing all handlers for an event type."""
        event_system = EventSystem()
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Register the handlers for different event types
        event_system.register_handler("test_event1", handler1)
        event_system.register_handler("test_event2", handler2)
        
        # Verify the handlers were registered
        handlers = event_system.get_handlers()
        assert "test_event1" in handlers
        assert "test_event2" in handlers
        
        # Clear handlers for test_event1
        event_system.clear_handlers("test_event1")
        
        # Verify the handlers for test_event1 were cleared
        handlers = event_system.get_handlers()
        assert "test_event1" in handlers
        assert len(handlers["test_event1"]) == 0
        assert "test_event2" in handlers
        assert len(handlers["test_event2"]) == 1
        
        # Emit events
        event_system.emit("test_event1", {"key": "value"})
        event_system.emit("test_event2", {"key": "value"})
        
        # Verify handler1 was not called and handler2 was called
        handler1.assert_not_called()
        handler2.assert_called_once()

    def test_clear_all_handlers(self):
        """Test clearing all handlers for all event types."""
        event_system = EventSystem()
        
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Register the handlers for different event types
        event_system.register_handler("test_event1", handler1)
        event_system.register_handler("test_event2", handler2)
        
        # Verify the handlers were registered
        handlers = event_system.get_handlers()
        assert "test_event1" in handlers
        assert "test_event2" in handlers
        
        # Clear all handlers
        event_system.clear_all_handlers()
        
        # Verify all handlers were cleared
        handlers = event_system.get_handlers()
        assert len(handlers) == 0
        
        # Emit events
        event_system.emit("test_event1", {"key": "value"})
        event_system.emit("test_event2", {"key": "value"})
        
        # Verify no handlers were called
        handler1.assert_not_called()
        handler2.assert_not_called()

    def test_event_with_metadata(self):
        """Test events with metadata."""
        event_system = EventSystem()
        
        # Create a mock handler
        handler = Mock()
        
        # Register the handler
        event_system.register_handler("test_event", handler)
        
        # Create an event with metadata
        timestamp = 1234567890
        source = "test_source"
        event_data = {"key": "value"}
        
        # Emit the event with metadata
        event_system.emit("test_event", event_data, timestamp=timestamp, source=source)
        
        # Verify the handler was called with the event including metadata
        handler.assert_called_once()
        call_args = handler.call_args[0][0]
        assert call_args.type == "test_event"
        assert call_args.data == event_data
        assert call_args.timestamp == timestamp
        assert call_args.source == source

    def test_event_propagation(self):
        """Test event propagation to parent event types."""
        event_system = EventSystem()
        
        # Create mock handlers
        parent_handler = Mock()
        child_handler = Mock()
        
        # Register the handlers
        event_system.register_handler("parent", parent_handler)
        event_system.register_handler("parent.child", child_handler)
        
        # Emit a child event
        event_data = {"key": "value"}
        event_system.emit("parent.child", event_data, propagate=True)
        
        # Verify both handlers were called
        parent_handler.assert_called_once()
        child_handler.assert_called_once()
        
        # Reset the mocks
        parent_handler.reset_mock()
        child_handler.reset_mock()
        
        # Emit a child event without propagation
        event_system.emit("parent.child", event_data, propagate=False)
        
        # Verify only the child handler was called
        parent_handler.assert_not_called()
        child_handler.assert_called_once()

    def test_async_event_handling(self):
        """Test asynchronous event handling."""
        event_system = EventSystem()
        
        # Create a mock handler that simulates async behavior
        async_results = []
        
        def async_handler(event):
            # Simulate async behavior by appending to a list
            async_results.append(event.data["value"])
        
        # Register the handler
        event_system.register_handler("test_event", async_handler)
        
        # Emit multiple events
        for i in range(5):
            event_system.emit("test_event", {"value": i})
        
        # Verify the events were handled in order
        assert async_results == [0, 1, 2, 3, 4]

    def test_event_filtering(self):
        """Test filtering events based on their data."""
        event_system = EventSystem()
        
        # Create mock handlers
        even_handler = Mock()
        odd_handler = Mock()
        
        # Create filters
        even_filter = lambda event: event.data.get("value", 0) % 2 == 0
        odd_filter = lambda event: event.data.get("value", 0) % 2 == 1
        
        # Register the handlers with filters
        event_system.register_handler("test_event", even_handler, even_filter)
        event_system.register_handler("test_event", odd_handler, odd_filter)
        
        # Emit events with different values
        for i in range(10):
            event_system.emit("test_event", {"value": i})
        
        # Verify the handlers were called with the correct events
        assert even_handler.call_count == 5  # 0, 2, 4, 6, 8
        assert odd_handler.call_count == 5   # 1, 3, 5, 7, 9
        
        # Verify the specific events received by each handler
        even_values = []
        for call_args in even_handler.call_args_list:
            event = call_args[0][0]  # First argument of the call
            even_values.append(event.data["value"])
        
        odd_values = []
        for call_args in odd_handler.call_args_list:
            event = call_args[0][0]  # First argument of the call
            odd_values.append(event.data["value"])
        
        assert sorted(even_values) == [0, 2, 4, 6, 8]
        assert sorted(odd_values) == [1, 3, 5, 7, 9]

    def test_event_repr(self):
        """Test the __repr__ method of the Event class."""
        event = Event("test_event", {"key": "value"}, 123.45, "test_source")
        repr_str = repr(event)
        assert "Event(" in repr_str
        assert "type=test_event" in repr_str
        assert "data={'key': 'value'}" in repr_str
        assert "timestamp=123.45" in repr_str
        assert "source=test_source" in repr_str

    def test_event_handler_exception(self):
        """Test that exceptions in event handlers are caught and logged."""
        event_system = EventSystem()
        
        # Create a handler that raises an exception
        def failing_handler(event):
            raise ValueError("Test exception")
        
        # Register the handler
        event_system.register_handler("test_event", failing_handler)
        
        # Emit an event - this should not raise an exception
        event_system.emit("test_event", {"key": "value"})
        
        # The test passes if no exception is raised 