"""
Custom log handlers for Abidance.

This module provides custom handlers for logging to different destinations,
such as rotating files, syslog, and more.
"""

from typing import Optional, Dict, Any
import logging
import logging.handlers
import os
import socket
import threading
import time

import atexit
import queue



class AsyncRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Asynchronous rotating file handler.

    This handler writes log records to a file asynchronously, which can
    improve performance by not blocking the main thread during I/O operations.
    """

    def __init__(self, filename: str, mode: str = 'a', maxBytes: int = 0,
                 backupCount: int = 0, encoding: Optional[str] = None,
                 delay: bool = False, queue_size: int = 1000):
        """
        Initialize the async rotating file handler.

        Args:
            filename: Path to the log file
            mode: File open mode
            maxBytes: Maximum file size before rotation
            backupCount: Number of backup files to keep
            encoding: File encoding
            delay: Whether to delay file opening until first log
            queue_size: Size of the queue for async logging
        """
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)

        # Create a queue and worker thread
        self.queue = queue.Queue(queue_size)
        self._stop_event = threading.Event()
        self.worker = threading.Thread(target=self._process_queue)
        self.worker.daemon = True
        self.worker.start()

        # Register cleanup function to flush queue on exit
        atexit.register(self._cleanup)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record by putting it in the queue.

        Args:
            record: The log record to emit
        """
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            # If queue is full, log to stderr
            sys_stderr = logging.StreamHandler()
            sys_stderr.setFormatter(logging.Formatter('%(asctime)s - QUEUE FULL - %(message)s'))
            sys_stderr.emit(record)

    def _process_queue(self) -> None:
        """Process records from the queue."""
        while not self._stop_event.is_set():
            try:
                # Get a record from the queue with a timeout
                try:
                    record = self.queue.get(block=True, timeout=0.1)
                except queue.Empty:
                    continue

                # Call the parent class's emit method to actually write the record
                super().emit(record)
                self.queue.task_done()
            except Exception:
                # Log any errors to stderr
                import traceback
                traceback.print_exc()

    def _cleanup(self) -> None:
        """Flush the queue and close the handler on exit."""
        # Signal the worker thread to stop
        self._stop_event.set()

        # Wait for the worker thread to finish with a timeout
        if self.worker.is_alive():
            self.worker.join(timeout=1.0)

        # Process any remaining items in the queue
        try:
            while not self.queue.empty():
                record = self.queue.get_nowait()
                super().emit(record)
                self.queue.task_done()
        except Exception:
            pass  # Silently ignore exceptions during flush

        # Wait for queue to empty with a timeout
        try:
            self.queue.join()
        except (KeyboardInterrupt, SystemExit):
            # Don't block exit if interrupted
            pass

        # Close the file
        self.close()

    def close(self) -> None:
        """Close the handler and clean up resources."""
        # Signal the worker thread to stop
        self._stop_event.set()

        # Wait for the worker thread to finish with a timeout
        if hasattr(self, 'worker') and self.worker.is_alive():
            self.worker.join(timeout=1.0)

        # Call the parent's close method
        super().close()


class JsonFileHandler(logging.FileHandler):
    """
    File handler that writes logs in JSON format.

    This handler ensures that each log record is written as a separate
    JSON object on a new line, making it easy to parse the log file.
    """

    def __init__(self, filename: str, mode: str = 'a', encoding: Optional[str] = None,
                 delay: bool = False):
        """
        Initialize the JSON file handler.

        Args:
            filename: Path to the log file
            mode: File open mode
            encoding: File encoding
            delay: Whether to delay file opening until first log
        """
        super().__init__(filename, mode, encoding, delay)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Args:
            record: The log record to emit
        """
        # Ensure each JSON object is on a new line
        if self.formatter:
            msg = self.formatter.format(record)
            if not msg.endswith('\n'):
                msg += '\n'
            self.stream.write(msg)
            self.flush()


class ContextAwareHandler(logging.Handler):
    """
    Handler that adds context information to log records.

    This handler adds additional context information to log records,
    such as hostname, process ID, and thread ID.
    """

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the context-aware handler.

        Args:
            context: Additional context to add to log records
        """
        super().__init__()
        self.context = context or {}
        self.handler = None

        # Add some default context
        if 'hostname' not in self.context:
            self.context['hostname'] = socket.gethostname()
        if 'pid' not in self.context:
            self.context['pid'] = os.getpid()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record with added context.

        Args:
            record: The log record to emit
        """
        # Add context to the record
        for key, value in self.context.items():
            setattr(record, key, value)

        # Pass to the next handler in the chain
        if self.handler:
            self.handler.emit(record)

    def set_handler(self, handler: logging.Handler) -> None:
        """
        Set the next handler in the chain.

        Args:
            handler: The handler to receive contextualized records
        """
        self.handler = handler
