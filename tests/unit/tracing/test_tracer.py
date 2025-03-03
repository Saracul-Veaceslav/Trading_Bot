"""
Unit tests for the tracing module.

Tests the functionality of the Tracer and Span classes.
"""

import pytest
from datetime import datetime, timedelta
import time
from abidance.tracing import Tracer, Span


class TestSpan:
    """Tests for the Span class."""
    
    def test_span_creation(self):
        """Test that a span can be created with the correct attributes."""
        # Given: Span parameters
        trace_id = "trace-123"
        span_id = "span-456"
        parent_id = "parent-789"
        operation = "test-operation"
        metadata = {"key": "value"}
        
        # When: Creating a span
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            operation=operation,
            metadata=metadata
        )
        
        # Then: The span should have the correct attributes
        assert span.trace_id == trace_id
        assert span.span_id == span_id
        assert span.parent_id == parent_id
        assert span.operation == operation
        assert span.metadata == metadata
        assert span.start_time is not None
        assert span.end_time is None
    
    def test_span_duration(self):
        """Test that span duration is calculated correctly."""
        # Given: A span with start and end times
        span = Span(
            trace_id="trace-123",
            span_id="span-456",
            parent_id=None,
            operation="test-operation"
        )
        
        # When: Setting the end time to 100ms after the start time
        span.start_time = datetime.now()
        span.end_time = span.start_time + timedelta(milliseconds=100)
        
        # Then: The duration should be approximately 100ms
        assert 99 <= span.duration_ms <= 101
    
    def test_span_duration_none(self):
        """Test that duration is None for an active span."""
        # Given: A span without an end time
        span = Span(
            trace_id="trace-123",
            span_id="span-456",
            parent_id=None,
            operation="test-operation"
        )
        
        # Then: The duration should be None
        assert span.duration_ms is None


class TestTracer:
    """Tests for the Tracer class."""
    
    def test_span_creation(self):
        """Test that a tracer can create spans.
        
        Feature: Span Creation
        Given a tracer
        When I start a new span
        Then the span should be created with the correct attributes
        """
        # Given: A tracer
        tracer = Tracer()
        
        # When: Starting a span
        with tracer.start_span("test-operation") as span:
            # Then: The span should be created with the correct attributes
            assert span.operation == "test-operation"
            assert span.parent_id is None
            assert span.trace_id is not None
            assert span.span_id is not None
            assert span.start_time is not None
            assert span.end_time is None
            
            # And: The span should be the active span
            assert tracer.get_active_span() is span
            
            # And: The span should be retrievable by ID
            assert tracer.get_span(span.span_id) is span
    
    def test_nested_spans(self):
        """Test that spans can be nested.
        
        Feature: Nested Spans
        Given a tracer
        When I start a parent span and then a child span
        Then the child span should have the parent span's ID as its parent ID
        And the child span should have the same trace ID as the parent span
        """
        # Given: A tracer
        tracer = Tracer()
        
        # When: Starting a parent span and then a child span
        with tracer.start_span("parent-operation") as parent_span:
            parent_id = parent_span.span_id
            trace_id = parent_span.trace_id
            
            with tracer.start_span("child-operation") as child_span:
                # Then: The child span should have the parent span's ID as its parent ID
                assert child_span.parent_id == parent_id
                
                # And: The child span should have the same trace ID as the parent span
                assert child_span.trace_id == trace_id
                
                # And: The child span should be the active span
                assert tracer.get_active_span() is child_span
            
            # And: After the child span ends, the parent span should be the active span again
            assert tracer.get_active_span() is parent_span
    
    def test_span_timing(self):
        """Test that span timing is recorded correctly.
        
        Feature: Span Timing
        Given a tracer
        When I start a span and let it run for a short time
        Then the span's duration should be approximately the time it ran
        """
        # Given: A tracer
        tracer = Tracer()
        
        # When: Starting a span and letting it run for a short time
        with tracer.start_span("timed-operation") as span:
            time.sleep(0.01)  # Sleep for 10ms
        
        # Then: The span's end time should be set
        assert span.end_time is not None
        
        # And: The span's duration should be approximately 10ms
        assert 5 <= span.duration_ms <= 50  # Allow for some timing variation
    
    def test_metadata_handling(self):
        """Test that span metadata is handled correctly.
        
        Feature: Metadata Handling
        Given a tracer
        When I start a span with metadata
        Then the span should have the correct metadata
        """
        # Given: A tracer
        tracer = Tracer()
        
        # When: Starting a span with metadata
        metadata = {"key1": "value1", "key2": 123}
        with tracer.start_span("metadata-operation", metadata=metadata) as span:
            # Then: The span should have the correct metadata
            assert span.metadata == metadata
            
            # And: I can add more metadata during the span's lifetime
            span.metadata["key3"] = "value3"
            assert span.metadata["key3"] == "value3"
    
    def test_get_trace_spans(self):
        """Test that all spans in a trace can be retrieved.
        
        Feature: Trace Retrieval
        Given a tracer with multiple spans in the same trace
        When I retrieve all spans for that trace
        Then I should get all spans belonging to the trace
        """
        # Given: A tracer with multiple spans in the same trace
        tracer = Tracer()
        
        with tracer.start_span("parent-operation") as parent_span:
            trace_id = parent_span.trace_id
            
            with tracer.start_span("child-operation-1"):
                pass
                
            with tracer.start_span("child-operation-2"):
                pass
        
        # When: Retrieving all spans for that trace
        trace_spans = tracer.get_trace_spans(trace_id)
        
        # Then: I should get all spans belonging to the trace
        assert len(trace_spans) == 3
        operations = [span.operation for span in trace_spans]
        assert "parent-operation" in operations
        assert "child-operation-1" in operations
        assert "child-operation-2" in operations 