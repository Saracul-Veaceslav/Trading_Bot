"""Unit tests for the health checks module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import aiohttp
from datetime import datetime

from abidance.health.checker import HealthStatus
from abidance.health.checks import (
    create_memory_check,
    create_cpu_check,
    create_disk_space_check,
    create_api_health_check,
    create_database_check,
)


class TestMemoryCheck:
    """Tests for the memory check."""
    
    @patch('psutil.virtual_memory')
    def test_memory_check_healthy(self, mock_virtual_memory):
        """Test that the memory check returns HEALTHY when memory is sufficient."""
        # Given a memory check with a threshold of 500MB
        threshold_mb = 500
        memory_check = create_memory_check(threshold_mb=threshold_mb)
        
        # And available memory is above the threshold
        mock_memory = Mock()
        mock_memory.available = (threshold_mb + 100) * 1024 * 1024  # 600MB in bytes
        mock_virtual_memory.return_value = mock_memory
        
        # When checking memory
        status = memory_check()
        
        # Then the status should be HEALTHY
        assert status == HealthStatus.HEALTHY
    
    @patch('psutil.virtual_memory')
    def test_memory_check_degraded(self, mock_virtual_memory):
        """Test that the memory check returns DEGRADED when memory is low."""
        # Given a memory check with a threshold of 500MB
        threshold_mb = 500
        memory_check = create_memory_check(threshold_mb=threshold_mb)
        
        # And available memory is below the threshold but above half the threshold
        mock_memory = Mock()
        mock_memory.available = (threshold_mb - 100) * 1024 * 1024  # 400MB in bytes
        mock_virtual_memory.return_value = mock_memory
        
        # When checking memory
        status = memory_check()
        
        # Then the status should be DEGRADED
        assert status == HealthStatus.DEGRADED
    
    @patch('psutil.virtual_memory')
    def test_memory_check_unhealthy(self, mock_virtual_memory):
        """Test that the memory check returns UNHEALTHY when memory is critically low."""
        # Given a memory check with a threshold of 500MB
        threshold_mb = 500
        memory_check = create_memory_check(threshold_mb=threshold_mb)
        
        # And available memory is below half the threshold
        mock_memory = Mock()
        mock_memory.available = (threshold_mb / 2 - 50) * 1024 * 1024  # 200MB in bytes
        mock_virtual_memory.return_value = mock_memory
        
        # When checking memory
        status = memory_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY


class TestCpuCheck:
    """Tests for the CPU check."""
    
    @patch('psutil.cpu_percent')
    def test_cpu_check_healthy(self, mock_cpu_percent):
        """Test that the CPU check returns HEALTHY when CPU usage is low."""
        # Given a CPU check with a threshold of 80%
        threshold_percent = 80.0
        cpu_check = create_cpu_check(threshold_percent=threshold_percent)
        
        # And CPU usage is below the threshold
        mock_cpu_percent.return_value = threshold_percent - 10  # 70%
        
        # When checking CPU
        status = cpu_check()
        
        # Then the status should be HEALTHY
        assert status == HealthStatus.HEALTHY
    
    @patch('psutil.cpu_percent')
    def test_cpu_check_degraded(self, mock_cpu_percent):
        """Test that the CPU check returns DEGRADED when CPU usage is high."""
        # Given a CPU check with a threshold of 80%
        threshold_percent = 80.0
        cpu_check = create_cpu_check(threshold_percent=threshold_percent)
        
        # And CPU usage is above the threshold but below the threshold + 10%
        mock_cpu_percent.return_value = threshold_percent + 5  # 85%
        
        # When checking CPU
        status = cpu_check()
        
        # Then the status should be DEGRADED
        assert status == HealthStatus.DEGRADED
    
    @patch('psutil.cpu_percent')
    def test_cpu_check_unhealthy(self, mock_cpu_percent):
        """Test that the CPU check returns UNHEALTHY when CPU usage is critically high."""
        # Given a CPU check with a threshold of 80%
        threshold_percent = 80.0
        cpu_check = create_cpu_check(threshold_percent=threshold_percent)
        
        # And CPU usage is above the threshold + 10%
        mock_cpu_percent.return_value = threshold_percent + 15  # 95%
        
        # When checking CPU
        status = cpu_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY


class TestDiskSpaceCheck:
    """Tests for the disk space check."""
    
    @patch('psutil.disk_usage')
    def test_disk_space_check_healthy(self, mock_disk_usage):
        """Test that the disk space check returns HEALTHY when disk space is sufficient."""
        # Given a disk space check with a threshold of 1GB
        threshold_gb = 1.0
        disk_check = create_disk_space_check(threshold_gb=threshold_gb)
        
        # And available disk space is above the threshold
        mock_usage = Mock()
        mock_usage.free = (threshold_gb + 1) * 1024 * 1024 * 1024  # 2GB in bytes
        mock_disk_usage.return_value = mock_usage
        
        # When checking disk space
        status = disk_check()
        
        # Then the status should be HEALTHY
        assert status == HealthStatus.HEALTHY
    
    @patch('psutil.disk_usage')
    def test_disk_space_check_degraded(self, mock_disk_usage):
        """Test that the disk space check returns DEGRADED when disk space is low."""
        # Given a disk space check with a threshold of 1GB
        threshold_gb = 1.0
        disk_check = create_disk_space_check(threshold_gb=threshold_gb)
        
        # And available disk space is below the threshold but above half the threshold
        mock_usage = Mock()
        mock_usage.free = (threshold_gb - 0.3) * 1024 * 1024 * 1024  # 0.7GB in bytes
        mock_disk_usage.return_value = mock_usage
        
        # When checking disk space
        status = disk_check()
        
        # Then the status should be DEGRADED
        assert status == HealthStatus.DEGRADED
    
    @patch('psutil.disk_usage')
    def test_disk_space_check_unhealthy(self, mock_disk_usage):
        """Test that the disk space check returns UNHEALTHY when disk space is critically low."""
        # Given a disk space check with a threshold of 1GB
        threshold_gb = 1.0
        disk_check = create_disk_space_check(threshold_gb=threshold_gb)
        
        # And available disk space is below half the threshold
        mock_usage = Mock()
        mock_usage.free = (threshold_gb / 2 - 0.1) * 1024 * 1024 * 1024  # 0.4GB in bytes
        mock_disk_usage.return_value = mock_usage
        
        # When checking disk space
        status = disk_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY


class TestApiHealthCheck:
    """Tests for the API health check."""
    
    @patch('asyncio.run')
    @patch('time.time')
    def test_api_health_check_healthy(self, mock_time, mock_asyncio_run):
        """Test that the API health check returns HEALTHY when the API is healthy."""
        # Given an API health check
        url = "https://example.com/health"
        api_check = create_api_health_check(url=url)
        
        # And the API returns a 200 status code
        mock_asyncio_run.return_value = 200  # Status code 200
        
        # And the response time is fast
        mock_time.side_effect = [0, 1]  # 1 second response time
        
        # When checking the API
        status = api_check()
        
        # Then the status should be HEALTHY
        assert status == HealthStatus.HEALTHY
    
    @patch('asyncio.run')
    @patch('time.time')
    def test_api_health_check_degraded_slow(self, mock_time, mock_asyncio_run):
        """Test that the API health check returns DEGRADED when the API is slow."""
        # Given an API health check with a timeout of 5 seconds
        url = "https://example.com/health"
        timeout = 5.0
        api_check = create_api_health_check(url=url, timeout=timeout)
        
        # And the API returns a 200 status code
        mock_asyncio_run.return_value = 200  # Status code 200
        
        # And the response time is slow (> 80% of timeout)
        mock_time.side_effect = [0, timeout * 0.9]  # 4.5 seconds response time
        
        # When checking the API
        status = api_check()
        
        # Then the status should be DEGRADED
        assert status == HealthStatus.DEGRADED
    
    @patch('asyncio.run')
    @patch('time.time')
    def test_api_health_check_degraded_status(self, mock_time, mock_asyncio_run):
        """Test that the API health check returns DEGRADED when the API returns a 4xx status code."""
        # Given an API health check
        url = "https://example.com/health"
        api_check = create_api_health_check(url=url)
        
        # And the API returns a 4xx status code
        mock_asyncio_run.return_value = 429  # Status code 429 (Too Many Requests)
        
        # And the response time is fast
        mock_time.side_effect = [0, 1]  # 1 second response time
        
        # When checking the API
        status = api_check()
        
        # Then the status should be DEGRADED
        assert status == HealthStatus.DEGRADED
    
    @patch('asyncio.run')
    @patch('time.time')
    def test_api_health_check_unhealthy(self, mock_time, mock_asyncio_run):
        """Test that the API health check returns UNHEALTHY when the API returns a 5xx status code."""
        # Given an API health check
        url = "https://example.com/health"
        api_check = create_api_health_check(url=url)
        
        # And the API returns a 5xx status code
        mock_asyncio_run.return_value = 500  # Status code 500 (Internal Server Error)
        
        # And the response time is fast
        mock_time.side_effect = [0, 1]  # 1 second response time
        
        # When checking the API
        status = api_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY
    
    @patch('asyncio.run')
    def test_api_health_check_exception(self, mock_asyncio_run):
        """Test that the API health check returns UNHEALTHY when an exception is raised."""
        # Given an API health check
        url = "https://example.com/health"
        api_check = create_api_health_check(url=url)
        
        # And the API raises an exception
        mock_asyncio_run.side_effect = Exception("Connection refused")
        
        # When checking the API
        status = api_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY
    
    @patch('asyncio.run')
    def test_api_health_check_timeout(self, mock_asyncio_run):
        """Test that the API health check returns UNHEALTHY when the API times out."""
        # Given an API health check
        url = "https://example.com/health"
        api_check = create_api_health_check(url=url)
        
        # And the API times out
        mock_asyncio_run.side_effect = asyncio.TimeoutError("Timeout")
        
        # When checking the API
        status = api_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY


class TestDatabaseCheck:
    """Tests for the database check."""
    
    def test_database_check_healthy(self):
        """Test that the database check returns HEALTHY when the database is healthy."""
        # Given a database check with a connection function that returns True
        check_connection = Mock(return_value=True)
        db_check = create_database_check(check_connection)
        
        # When checking the database
        status = db_check()
        
        # Then the status should be HEALTHY
        assert status == HealthStatus.HEALTHY
        
        # And the connection function should have been called
        check_connection.assert_called_once()
    
    def test_database_check_unhealthy(self):
        """Test that the database check returns UNHEALTHY when the database is unhealthy."""
        # Given a database check with a connection function that returns False
        check_connection = Mock(return_value=False)
        db_check = create_database_check(check_connection)
        
        # When checking the database
        status = db_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY
        
        # And the connection function should have been called
        check_connection.assert_called_once()
    
    def test_database_check_exception(self):
        """Test that the database check returns UNHEALTHY when an exception is raised."""
        # Given a database check with a connection function that raises an exception
        check_connection = Mock(side_effect=Exception("Database connection error"))
        db_check = create_database_check(check_connection)
        
        # When checking the database
        status = db_check()
        
        # Then the status should be UNHEALTHY
        assert status == HealthStatus.UNHEALTHY
        
        # And the connection function should have been called
        check_connection.assert_called_once() 