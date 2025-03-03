from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import asyncio
from enum import Enum

class HealthStatus(Enum):
    """Enum representing the health status of a component."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """System health checking framework.

    This class provides a framework for registering and running health checks
    for various system components. Health checks are functions that return
    a HealthStatus indicating the health of a component.
    """

    def __init__(self):
        """Initialize the health checker with an empty dictionary of checks."""
        self._checks: Dict[str, Callable[[], HealthStatus]] = {}

    def register_check(self, name: str, check: Callable[[], HealthStatus]) -> None:
        """Register a health check.

        Args:
            name: A unique name for the health check
            check: A callable that returns a HealthStatus
        """
        self._checks[name] = check

    def unregister_check(self, name: str) -> None:
        """Unregister a health check.

        Args:
            name: The name of the health check to unregister
        """
        if name in self._checks:
            del self._checks[name]

    def get_registered_checks(self) -> List[str]:
        """Get a list of all registered health check names.

        Returns:
            A list of registered health check names
        """
        return list(self._checks.keys())

    async def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all registered health checks.

        Returns:
            A dictionary mapping check names to their results
        """
        results = {}
        for name, check in self._checks.items():
            try:
                status = check()
                results[name] = {
                    'status': status.value,
                    'timestamp': datetime.now().isoformat(),
                    'error': None
                }
            except Exception as e:
                results[name] = {
                    'status': HealthStatus.UNHEALTHY.value,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
        return results