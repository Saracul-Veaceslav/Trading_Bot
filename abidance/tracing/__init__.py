"""
Distributed tracing system for tracking operations across components.

This module provides tools for creating and managing trace spans to track
the flow of operations through the system, making it easier to debug and
analyze performance.
"""

from abidance.tracing.tracer import Tracer, Span

__all__ = ["Tracer", "Span"] 