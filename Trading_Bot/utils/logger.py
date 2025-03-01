import os
import logging
import logging.handlers
from typing import Optional, Dict, Any
import sys
from pathlib import Path

from trading_bot.utils.config_manager import get_config_manager

# Get configuration for logging
config = get_config_manager()

# Default log levels
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_CONSOLE_LOG_LEVEL = logging.INFO

# Global dictionary to store loggers
_loggers: Dict[str, logging.Logger] = {}

def get_logs_directory() -> str:
    """
    Get the directory path for log files.
    
    Returns:
        str: Path to the logs directory
    """
    logs_dir = config.get('logging.directory', 'logs')
    
    # Ensure the logs directory exists
    os.makedirs(logs_dir, exist_ok=True)
    
    return logs_dir
    
def get_log_level(level_name: Optional[str] = None) -> int:
    """
    Convert a log level name to its corresponding integer value.
    
    Args:
        level_name: The name of the log level, e.g., 'INFO', 'DEBUG'
        
    Returns:
        int: The log level value
    """
    if level_name is None:
        return DEFAULT_LOG_LEVEL
        
    level_name = level_name.upper()
    
    if level_name == 'DEBUG':
        return logging.DEBUG
    elif level_name == 'INFO':
        return logging.INFO
    elif level_name == 'WARNING':
        return logging.WARNING
    elif level_name == 'ERROR':
        return logging.ERROR
    elif level_name == 'CRITICAL':
        return logging.CRITICAL
    else:
        return DEFAULT_LOG_LEVEL
        
def configure_logger(
    name: str,
    level: Optional[str] = None,
    console_level: Optional[str] = None,
    file_level: Optional[str] = None,
    format_str: Optional[str] = None,
    file_name: Optional[str] = None
) -> logging.Logger:
    """
    Configure a logger with file and console handlers.
    
    Args:
        name: Name of the logger
        level: Overall logger level
        console_level: Console handler log level
        file_level: File handler log level
        format_str: Format string for log messages
        file_name: Name of the log file
        
    Returns:
        logging.Logger: The configured logger
    """
    if name in _loggers:
        return _loggers[name]
        
    # Create logger
    logger = logging.getLogger(name)
    
    # Set the logger level
    logger_level = get_log_level(level) if level else get_log_level(config.get('logging.level', 'INFO'))
    logger.setLevel(logger_level)
    
    # Remove existing handlers (if any)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # Set format
    if format_str is None:
        format_str = config.get(
            'logging.format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    formatter = logging.Formatter(format_str)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler_level = get_log_level(console_level) if console_level else get_log_level(
        config.get('logging.console_level', 'INFO')
    )
    console_handler.setLevel(console_handler_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if file_name is None:
        file_name = f"{name.replace('.', '_')}.log"
    
    logs_dir = get_logs_directory()
    log_file_path = os.path.join(logs_dir, file_name)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=config.get('logging.max_bytes', 10 * 1024 * 1024),  # 10 MB by default
        backupCount=config.get('logging.backup_count', 5)
    )
    
    file_handler_level = get_log_level(file_level) if file_level else get_log_level(
        config.get('logging.file_level', 'DEBUG')
    )
    file_handler.setLevel(file_handler_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Store the logger
    _loggers[name] = logger
    
    return logger
    
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name. If it doesn't exist, it will be created.
    
    Args:
        name: Name of the logger
        
    Returns:
        logging.Logger: The logger
    """
    if name in _loggers:
        return _loggers[name]
    
    return configure_logger(name)
    
def get_trading_logger() -> logging.Logger:
    """
    Get the trading logger.
    
    Returns:
        logging.Logger: The trading logger
    """
    return get_logger('trading_bot.trading')
    
def get_error_logger() -> logging.Logger:
    """
    Get the error logger.
    
    Returns:
        logging.Logger: The error logger
    """
    return get_logger('trading_bot.error')
    
def get_debug_logger() -> logging.Logger:
    """
    Get the debug logger.
    
    Returns:
        logging.Logger: The debug logger
    """
    return get_logger('trading_bot.debug')
    
def get_strategy_logger(strategy_name: str) -> logging.Logger:
    """
    Get a logger for a specific strategy.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        logging.Logger: The strategy logger
    """
    return get_logger(f'trading_bot.strategies.{strategy_name.lower().replace(" ", "_")}')
    
def init_logging():
    """Initialize the logging system based on configuration."""
    # Configure root logger
    configure_logger('trading_bot')
    
    # Configure component-specific loggers
    configure_logger('trading_bot.trading', file_name='trading.log')
    configure_logger('trading_bot.error', level='ERROR', file_name='error.log')
    configure_logger('trading_bot.debug', level='DEBUG', file_name='debug.log')
    configure_logger('trading_bot.strategies', file_name='strategies.log')
    
    # Configure exchange-specific logger
    configure_logger('trading_bot.exchanges', file_name='exchanges.log')
    
    # Configure data-specific logger
    configure_logger('trading_bot.data', file_name='data.log')
    
    # Log initialization
    logger = get_logger('trading_bot')
    logger.info('Logging system initialized') 