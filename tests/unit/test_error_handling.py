"""
Tests for the error handling utilities in the Abidance exceptions module.
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from abidance.exceptions import (
    AbidanceError, DataError, 
    ErrorContext, error_boundary, retry, fallback, CircuitBreaker, CircuitOpenError
)


class TestErrorContext:
    """Tests for the ErrorContext class."""
    
    def test_error_context_initialization(self):
        """Test initializing an ErrorContext with various parameters."""
        # Test default initialization
        ctx = ErrorContext()
        assert ctx.context == {}
        assert ctx.source is None
        assert ctx.operation is None
        
        # Test initialization with parameters
        ctx = ErrorContext(
            context={"param": "value"}, 
            source="test_source",
            operation="test_operation"
        )
        assert ctx.context == {"param": "value"}
        assert ctx.source == "test_source"
        assert ctx.operation == "test_operation"
    
    def test_context_modification(self):
        """Test adding and updating context information."""
        ctx = ErrorContext()
        
        # Test add_context
        ctx.add_context("key1", "value1")
        assert ctx.context == {"key1": "value1"}
        
        # Test method chaining
        ctx.add_context("key2", "value2").add_context("key3", "value3")
        assert ctx.context == {"key1": "value1", "key2": "value2", "key3": "value3"}
        
        # Test update_context
        ctx.update_context({"key4": "value4", "key5": "value5"})
        assert ctx.context == {
            "key1": "value1", 
            "key2": "value2", 
            "key3": "value3",
            "key4": "value4",
            "key5": "value5"
        }
    
    def test_source_and_operation(self):
        """Test setting source and operation."""
        ctx = ErrorContext()
        
        # Test set_source
        ctx.set_source("test_source")
        assert ctx.source == "test_source"
        
        # Test set_operation
        ctx.set_operation("test_operation")
        assert ctx.operation == "test_operation"
        
        # Test method chaining
        ctx = ErrorContext()
        ctx.set_source("source").set_operation("operation")
        assert ctx.source == "source"
        assert ctx.operation == "operation"
    
    def test_enriching_exception(self):
        """Test enriching an exception with context information."""
        ctx = ErrorContext(
            context={"param": "value"},
            source="test_source",
            operation="test_operation"
        )
        
        error = AbidanceError("Test error")
        enriched = ctx.enrich_exception(error)
        
        # Check if the exception was enriched with context information
        assert hasattr(enriched, 'context')
        assert enriched.context == {"param": "value"}
        assert hasattr(enriched, 'source')
        assert enriched.source == "test_source"
        assert hasattr(enriched, 'operation')
        assert enriched.operation == "test_operation"


class TestErrorBoundary:
    """Tests for the error_boundary context manager."""
    
    def test_no_error(self):
        """Test the context manager when no error is raised."""
        with error_boundary() as ctx:
            ctx.add_context("test", "value")
            result = 1 + 1
        
        assert result == 2
    
    def test_with_error(self):
        """Test the context manager when an error is raised."""
        with pytest.raises(AbidanceError) as excinfo:
            with error_boundary(source="test_source", operation="test_operation") as ctx:
                ctx.add_context("test", "value")
                raise ValueError("Test error")
        
        error = excinfo.value
        assert isinstance(error, AbidanceError)
        assert hasattr(error, 'context')
        assert error.context == {"test": "value"}
        assert hasattr(error, 'source')
        assert error.source == "test_source"
        assert hasattr(error, 'operation')
        assert error.operation == "test_operation"
    
    def test_with_specific_error_type(self):
        """Test the context manager with specific error types."""
        # This should be caught and wrapped
        with pytest.raises(AbidanceError):
            with error_boundary(error_types=ValueError):
                raise ValueError("Test error")
        
        # This should not be caught
        with pytest.raises(KeyError):
            with error_boundary(error_types=ValueError):
                raise KeyError("Test error")
    
    def test_transform_exception(self):
        """Test transforming exceptions with the context manager."""
        def transform(exc, ctx):
            return DataError(f"Transformed: {str(exc)}")
        
        with pytest.raises(DataError) as excinfo:
            with error_boundary(transform_exception=transform):
                raise ValueError("Original error")
        
        assert "Transformed: " in str(excinfo.value)
    
    def test_no_reraise(self):
        """Test the context manager with reraise=False."""
        result = None
        with error_boundary(reraise=False):
            result = 1 + 1
        assert result == 2
        
        with error_boundary(reraise=False):
            raise ValueError("This error should be suppressed")
        # If we get here, the error was suppressed


class TestRetryDecorator:
    """Tests for the retry decorator."""
    
    def test_successful_execution(self):
        """Test successful execution without retries."""
        mock_func = MagicMock(return_value="success")
        decorated = retry()(mock_func)
        
        result = decorated("arg1", key="value")
        assert result == "success"
        mock_func.assert_called_once_with("arg1", key="value")
    
    def test_retry_on_error(self):
        """Test retrying on error."""
        mock_func = MagicMock(side_effect=[ValueError(), ValueError(), "success"])
        decorated = retry(max_attempts=3, delay=0.01)(mock_func)
        
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        decorated = retry(max_attempts=3, delay=0.01)(mock_func)
        
        with pytest.raises(ValueError):
            decorated()
        
        assert mock_func.call_count == 3
    
    def test_selective_retry(self):
        """Test that only specified error types trigger retries."""
        mock_func = MagicMock(side_effect=[ValueError(), KeyError(), "success"])
        decorated = retry(max_attempts=3, delay=0.01, error_types=ValueError)(mock_func)
        
        # Should retry on ValueError but raise on KeyError
        with pytest.raises(KeyError):
            decorated()
        
        assert mock_func.call_count == 2
    
    def test_backoff(self):
        """Test that backoff increases delay between retries."""
        mock_sleep = MagicMock()
        mock_func = MagicMock(side_effect=[ValueError(), ValueError(), ValueError(), "success"])
        
        with patch('time.sleep', mock_sleep):
            decorated = retry(max_attempts=4, delay=1.0, backoff_factor=2.0)(mock_func)
            try:
                decorated()
            except ValueError:
                pass
        
        # Check that sleep was called with increasing delays
        assert mock_sleep.call_count >= 2
        calls = mock_sleep.call_args_list
        assert calls[0][0][0] == 1.0
        assert calls[1][0][0] == 2.0  # Second delay should be 2x the first
    
    def test_should_retry_function(self):
        """Test the should_retry callback function."""
        should_retry = MagicMock(side_effect=[True, False])
        mock_func = MagicMock(side_effect=[ValueError(), ValueError(), "success"])
        
        decorated = retry(
            max_attempts=3, 
            delay=0.01, 
            should_retry=should_retry
        )(mock_func)
        
        with pytest.raises(ValueError):
            decorated()
        
        # Function should be called twice (original + 1 retry)
        assert mock_func.call_count == 2
        assert should_retry.call_count == 2


class TestFallbackDecorator:
    """Tests for the fallback decorator."""
    
    def test_successful_execution(self):
        """Test successful execution without fallback."""
        mock_func = MagicMock(return_value="success")
        decorated = fallback(default_value="default")(mock_func)
        
        result = decorated("arg1", key="value")
        assert result == "success"
        mock_func.assert_called_once_with("arg1", key="value")
    
    def test_fallback_to_default(self):
        """Test falling back to default value on error."""
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        decorated = fallback(default_value="default")(mock_func)
        
        result = decorated()
        assert result == "default"
        mock_func.assert_called_once()
    
    def test_fallback_function(self):
        """Test falling back to an alternative function on error."""
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        mock_fallback = MagicMock(return_value="fallback result")
        
        decorated = fallback(fallback_function=mock_fallback)(mock_func)
        
        result = decorated("arg1", key="value")
        assert result == "fallback result"
        mock_func.assert_called_once_with("arg1", key="value")
        mock_fallback.assert_called_once_with("arg1", key="value")
    
    def test_selective_fallback(self):
        """Test that only specified error types trigger fallback."""
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        
        # Should fall back on ValueError
        decorated1 = fallback(
            default_value="default", 
            error_types=ValueError
        )(mock_func)
        result1 = decorated1()
        assert result1 == "default"
        
        mock_func.reset_mock()
        
        # Should not fall back on ValueError if error_types is KeyError
        decorated2 = fallback(
            default_value="default", 
            error_types=KeyError
        )(mock_func)
        
        with pytest.raises(ValueError):
            decorated2()
    
    @patch('logging.Logger.log')
    def test_error_logging(self, mock_log):
        """Test that errors are logged."""
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        decorated = fallback(
            default_value="default", 
            log_error=True
        )(mock_func)
        
        result = decorated()
        assert result == "default"
        assert mock_log.called


class TestCircuitBreaker:
    """Tests for the CircuitBreaker class."""
    
    def test_successful_execution(self):
        """Test successful execution with circuit closed."""
        circuit = CircuitBreaker(failure_threshold=3)
        mock_func = MagicMock(return_value="success")
        
        result = circuit.execute(mock_func, "arg1", key="value")
        assert result == "success"
        mock_func.assert_called_once_with("arg1", key="value")
    
    def test_decorator_syntax(self):
        """Test using CircuitBreaker as a decorator."""
        circuit = CircuitBreaker(failure_threshold=3)
        
        @circuit
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
    
    def test_circuit_opens_after_failures(self):
        """Test that circuit opens after reaching the failure threshold."""
        with patch('time.time', return_value=100):
            circuit = CircuitBreaker(
                failure_threshold=3,
                recovery_timeout=60,
                fallback_value="fallback"
            )
            
            mock_func = MagicMock(side_effect=ValueError("Test error"))
            
            # First two failures
            for _ in range(2):
                with pytest.raises(ValueError):
                    circuit.execute(mock_func)
            
            assert circuit.state == CircuitBreaker.CLOSED
            assert circuit.failure_count == 2
            
            # Third failure should open the circuit
            result = circuit.execute(mock_func)
            assert circuit.state == CircuitBreaker.OPEN
            assert result == "fallback"
            
            # Subsequent calls with circuit open should return fallback without calling the function
            mock_func.reset_mock()
            result = circuit.execute(mock_func)
            assert result == "fallback"
            mock_func.assert_not_called()
    
    def test_circuit_transitions_to_half_open(self):
        """Test that circuit transitions to half-open after recovery timeout."""
        circuit = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1,  # Short timeout for testing
            fallback_value="fallback"
        )
        
        mock_func = MagicMock(side_effect=[ValueError("Test error"), "success"])
        
        # Fail once to open the circuit
        result = circuit.execute(mock_func)
        assert circuit.state == CircuitBreaker.OPEN
        assert result == "fallback"
        
        # Wait for the recovery timeout
        time.sleep(0.2)
        
        # Next call should transition to half-open and try the function again
        result = circuit.execute(mock_func)
        assert result == "success"
        assert circuit.state == CircuitBreaker.CLOSED  # Success in half-open state closes the circuit
    
    def test_fallback_function(self):
        """Test using a fallback function with circuit breaker."""
        circuit = CircuitBreaker(
            failure_threshold=1,
            fallback_function=lambda *args, **kwargs: f"fallback: {args[0]}"
        )
        
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        
        # Fail to open the circuit
        result = circuit.execute(mock_func, "test_arg")
        assert result == "fallback: test_arg"
    
    def test_callbacks(self):
        """Test that callbacks are called when circuit opens and closes."""
        on_open = MagicMock()
        on_close = MagicMock()
        
        circuit = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1,
            fallback_value="fallback",
            on_open=on_open,
            on_close=on_close
        )
        
        mock_func = MagicMock(side_effect=[ValueError("Test error"), "success"])
        
        # Fail to open the circuit
        circuit.execute(mock_func)
        on_open.assert_called_once()
        on_close.assert_not_called()
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Succeed to close the circuit
        circuit.execute(mock_func)
        on_close.assert_called_once()
    
    def test_circuit_open_error(self):
        """Test that CircuitOpenError is raised when no fallback is provided."""
        circuit = CircuitBreaker(failure_threshold=1)
        
        mock_func = MagicMock(side_effect=ValueError("Test error"))
        
        # Fail to open the circuit
        with pytest.raises(CircuitOpenError):
            circuit.execute(mock_func)
            circuit.execute(mock_func)  # This should raise CircuitOpenError 