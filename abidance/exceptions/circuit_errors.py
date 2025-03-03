"""
Circuit breaker specific exceptions for the Abidance trading bot.

This module defines exceptions related to the circuit breaker pattern.
"""

from .base import AbidanceError



class CircuitOpenError(AbidanceError):
    """Exception raised when a circuit breaker is open."""
