"""Common health checks for the Abidance trading bot."""

from typing import Callable, Dict, Any, Optional
import asyncio
import logging
import os
import time

import aiohttp
import psutil

from .checker import HealthStatus

logger = logging.getLogger(__name__)

def create_memory_check(threshold_mb: int = 500) -> Callable[[], HealthStatus]:
    """Create a health check that monitors available memory.

    Args:
        threshold_mb: The minimum amount of free memory in MB before the check
            returns DEGRADED or UNHEALTHY

    Returns:
        A callable health check function
    """
    def check() -> HealthStatus:
        """Check available memory."""
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # Convert to MB

        if available_memory < threshold_mb / 2:
            logger.warning(f"Available memory critically low: {available_memory:.2f}MB")
            return HealthStatus.UNHEALTHY
        if available_memory < threshold_mb:
            logger.info(f"Available memory low: {available_memory:.2f}MB")
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY

    return check

def create_cpu_check(threshold_percent: float = 80.0) -> Callable[[], HealthStatus]:
    """Create a health check that monitors CPU usage.

    Args:
        threshold_percent: The maximum CPU usage percentage before the check
            returns DEGRADED or UNHEALTHY

    Returns:
        A callable health check function
    """
    def check() -> HealthStatus:
        """Check CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=0.1)

        if cpu_percent > threshold_percent + 10:
            logger.warning(f"CPU usage critically high: {cpu_percent:.2f}%")
            return HealthStatus.UNHEALTHY
        if cpu_percent > threshold_percent:
            logger.info(f"CPU usage high: {cpu_percent:.2f}%")
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY

    return check

def create_disk_space_check(path: str = ".", threshold_gb: float = 1.0) -> Callable[[], HealthStatus]:
    """Create a health check that monitors available disk space.

    Args:
        path: The path to check disk space for
        threshold_gb: The minimum amount of free disk space in GB before the check
            returns DEGRADED or UNHEALTHY

    Returns:
        A callable health check function
    """
    def check() -> HealthStatus:
        """Check available disk space."""
        disk_usage = psutil.disk_usage(path)
        free_space_gb = disk_usage.free / (1024 * 1024 * 1024)  # Convert to GB

        if free_space_gb < threshold_gb / 2:
            logger.warning(f"Available disk space critically low: {free_space_gb:.2f}GB")
            return HealthStatus.UNHEALTHY
        if free_space_gb < threshold_gb:
            logger.info(f"Available disk space low: {free_space_gb:.2f}GB")
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY

    return check

def create_api_health_check(url: str, timeout: float = 5.0) -> Callable[[], HealthStatus]:
    """Create a health check that monitors the health of an API endpoint.

    Args:
        url: The URL to check
        timeout: The timeout in seconds before considering the API unhealthy

    Returns:
        A callable health check function
    """
    def check() -> HealthStatus:
        """Check API health."""
        try:
            start_time = time.time()

            # Create a session and make a request
            async def fetch():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=timeout) as response:
                        return response.status

            # Run the async function
            try:
                status_code = asyncio.run(fetch())
            except (asyncio.CancelledError, asyncio.TimeoutError):
                logger.warning("API endpoint %s timed out after %s seconds", url, timeout)
                return HealthStatus.UNHEALTHY

            response_time = time.time() - start_time

            # Check the status code and response time
            if status_code >= 500:
                logger.warning("API endpoint %s returned server error: %s", url, status_code)
                return HealthStatus.UNHEALTHY
            if status_code >= 400 or response_time > timeout * 0.8:
                logger.info(f"API endpoint {url} degraded: status={status_code}, time={response_time:.2f}s")
                return HealthStatus.DEGRADED
            
            return HealthStatus.HEALTHY
        except Exception as e:
            logger.error("API endpoint %s health check failed: %s", url, str(e))
            return HealthStatus.UNHEALTHY

    return check

def create_database_check(check_connection_func: Callable[[], bool]) -> Callable[[], HealthStatus]:
    """Create a health check that monitors database connectivity.

    Args:
        check_connection_func: A function that returns True if the database
            connection is healthy, False otherwise

    Returns:
        A callable health check function
    """
    def check() -> HealthStatus:
        """Check database connectivity."""
        try:
            if check_connection_func():
                return HealthStatus.HEALTHY
            
            logger.warning("Database connection check failed")
            return HealthStatus.UNHEALTHY
        except Exception as e:
            logger.error("Database health check failed: %s", str(e))
            return HealthStatus.UNHEALTHY

    return check