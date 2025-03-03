"""Unit tests for the health checker module."""

import pytest
from unittest.mock import Mock, patch
import asyncio
from datetime import datetime

from abidance.health.checker import HealthStatus, HealthCheck


class TestHealthStatus:
    """Tests for the HealthStatus enum."""
    
    def test_health_status_values(self):
        """Test that the HealthStatus enum has the expected values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"


class TestHealthCheck:
    """Tests for the HealthCheck class."""
    
    @pytest.fixture
    def health_check(self):
        """Create a HealthCheck instance for testing."""
        return HealthCheck()
    
    @pytest.fixture
    def mock_check(self):
        """Create a mock health check function."""
        return Mock(return_value=HealthStatus.HEALTHY)
    
    def test_register_check(self, health_check, mock_check):
        """Test that a health check can be registered."""
        # Given a health check instance
        # When registering a check
        health_check.register_check("test_check", mock_check)
        
        # Then the check should be registered
        assert "test_check" in health_check._checks
        assert health_check._checks["test_check"] == mock_check
        
        # And the registered checks should be retrievable
        assert health_check.get_registered_checks() == ["test_check"]
    
    def test_unregister_check(self, health_check, mock_check):
        """Test that a health check can be unregistered."""
        # Given a health check instance with a registered check
        health_check.register_check("test_check", mock_check)
        assert "test_check" in health_check._checks
        
        # When unregistering the check
        health_check.unregister_check("test_check")
        
        # Then the check should be unregistered
        assert "test_check" not in health_check._checks
        assert health_check.get_registered_checks() == []
    
    def test_unregister_nonexistent_check(self, health_check):
        """Test that unregistering a nonexistent check doesn't raise an error."""
        # Given a health check instance
        # When unregistering a nonexistent check
        health_check.unregister_check("nonexistent_check")
        
        # Then no error should be raised
        assert health_check.get_registered_checks() == []
    
    @pytest.mark.asyncio
    async def test_run_checks_healthy(self, health_check, mock_check):
        """Test running checks when all checks are healthy."""
        # Given a health check instance with a registered check
        health_check.register_check("test_check", mock_check)
        
        # When running the checks
        results = await health_check.run_checks()
        
        # Then the results should contain the check status
        assert "test_check" in results
        assert results["test_check"]["status"] == HealthStatus.HEALTHY.value
        assert results["test_check"]["error"] is None
        assert isinstance(results["test_check"]["timestamp"], str)
        
        # And the check should have been called
        mock_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_checks_unhealthy(self, health_check):
        """Test running checks when a check is unhealthy."""
        # Given a health check instance with a check that returns UNHEALTHY
        unhealthy_check = Mock(return_value=HealthStatus.UNHEALTHY)
        health_check.register_check("unhealthy_check", unhealthy_check)
        
        # When running the checks
        results = await health_check.run_checks()
        
        # Then the results should contain the unhealthy status
        assert "unhealthy_check" in results
        assert results["unhealthy_check"]["status"] == HealthStatus.UNHEALTHY.value
        assert results["unhealthy_check"]["error"] is None
        
        # And the check should have been called
        unhealthy_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_checks_degraded(self, health_check):
        """Test running checks when a check is degraded."""
        # Given a health check instance with a check that returns DEGRADED
        degraded_check = Mock(return_value=HealthStatus.DEGRADED)
        health_check.register_check("degraded_check", degraded_check)
        
        # When running the checks
        results = await health_check.run_checks()
        
        # Then the results should contain the degraded status
        assert "degraded_check" in results
        assert results["degraded_check"]["status"] == HealthStatus.DEGRADED.value
        assert results["degraded_check"]["error"] is None
        
        # And the check should have been called
        degraded_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_checks_error(self, health_check):
        """Test running checks when a check raises an exception."""
        # Given a health check instance with a check that raises an exception
        error_message = "Test error"
        error_check = Mock(side_effect=Exception(error_message))
        health_check.register_check("error_check", error_check)
        
        # When running the checks
        results = await health_check.run_checks()
        
        # Then the results should contain the error
        assert "error_check" in results
        assert results["error_check"]["status"] == HealthStatus.UNHEALTHY.value
        assert results["error_check"]["error"] == error_message
        
        # And the check should have been called
        error_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_checks_multiple(self, health_check):
        """Test running multiple checks."""
        # Given a health check instance with multiple checks
        healthy_check = Mock(return_value=HealthStatus.HEALTHY)
        degraded_check = Mock(return_value=HealthStatus.DEGRADED)
        unhealthy_check = Mock(return_value=HealthStatus.UNHEALTHY)
        
        health_check.register_check("healthy_check", healthy_check)
        health_check.register_check("degraded_check", degraded_check)
        health_check.register_check("unhealthy_check", unhealthy_check)
        
        # When running the checks
        results = await health_check.run_checks()
        
        # Then the results should contain all checks
        assert len(results) == 3
        assert results["healthy_check"]["status"] == HealthStatus.HEALTHY.value
        assert results["degraded_check"]["status"] == HealthStatus.DEGRADED.value
        assert results["unhealthy_check"]["status"] == HealthStatus.UNHEALTHY.value
        
        # And all checks should have been called
        healthy_check.assert_called_once()
        degraded_check.assert_called_once()
        unhealthy_check.assert_called_once() 