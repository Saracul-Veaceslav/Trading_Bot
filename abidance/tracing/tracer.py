"""
Distributed tracing implementation for tracking operations across components.

This module provides the core tracing functionality, including the Span class
for representing individual operations and the Tracer class for managing spans.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class Span:
    """Represents a single operation span within a trace.

    A span represents a single operation or unit of work within a distributed system.
    Spans can be nested to represent parent-child relationships between operations.

    Attributes:
        trace_id: Unique identifier for the trace this span belongs to
        span_id: Unique identifier for this span
        parent_id: Identifier of the parent span, if any
        operation: Name of the operation being traced
        start_time: When the span started
        end_time: When the span ended (None if still active)
        metadata: Additional contextual information about the span
    """
    trace_id: str
    span_id: str
    parent_id: Optional[str]
    operation: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate the duration of this span in milliseconds.

        Returns:
            The duration in milliseconds, or None if the span hasn't ended.
        """
        if not self.end_time:
            return None

        delta = self.end_time - self.start_time
        return delta.total_seconds() * 1000


class Tracer:
    """Distributed tracing system for tracking operations across components.

    The Tracer class manages the creation and tracking of spans, allowing
    operations to be traced across different components of the system.
    """

    def __init__(self):
        """Initialize a new Tracer instance."""
        self._spans: Dict[str, Span] = {}
        self._active_span: Optional[Span] = None

    @contextmanager
    def start_span(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Start a new trace span.

        This creates a new span and sets it as the active span. If there's already
        an active span, the new span will be a child of the active span.

        Args:
            operation: Name of the operation being traced
            metadata: Additional contextual information about the span

        Yields:
            The newly created span
        """
        span_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4()) if not self._active_span else self._active_span.trace_id
        parent_id = self._active_span.span_id if self._active_span else None

        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            operation=operation,
            metadata=metadata or {}
        )

        previous_span = self._active_span
        self._active_span = span
        self._spans[span_id] = span

        try:
            yield span
        finally:
            span.end_time = datetime.now()
            self._active_span = previous_span

    def get_span(self, span_id: str) -> Optional[Span]:
        """Get a span by its ID.

        Args:
            span_id: The ID of the span to retrieve

        Returns:
            The span with the given ID, or None if not found
        """
        return self._spans.get(span_id)

    def get_active_span(self) -> Optional[Span]:
        """Get the currently active span.

        Returns:
            The currently active span, or None if there is no active span
        """
        return self._active_span

    def get_trace_spans(self, trace_id: str) -> List[Span]:
        """Get all spans belonging to a specific trace.

        Args:
            trace_id: The ID of the trace to retrieve spans for

        Returns:
            A list of spans belonging to the specified trace
        """
        return [span for span in self._spans.values() if span.trace_id == trace_id]
