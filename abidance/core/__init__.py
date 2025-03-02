"""
Core module for the Abidance trading bot.

This module provides core functionality used throughout the application,
including configuration management, logging, and event handling.
"""

# Define classes to be exported
class ConfigManager:
    """
    Manager for configuration settings.
    """
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.config = {}
    
    def load_config(self, config_path=None):
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Loaded configuration
        """
        # Placeholder implementation
        return self.config
    
    def save_config(self, config_path=None):
        """
        Save configuration to a file.
        
        Args:
            config_path: Path to save the configuration to
            
        Returns:
            True if successful, False otherwise
        """
        # Placeholder implementation
        return True
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value


class Logger:
    """
    Logger for the application.
    """
    def __init__(self, name=None, level="INFO"):
        self.name = name
        self.level = level
    
    def debug(self, message):
        """
        Log a debug message.
        
        Args:
            message: Message to log
        """
        # Placeholder implementation
        pass
    
    def info(self, message):
        """
        Log an info message.
        
        Args:
            message: Message to log
        """
        # Placeholder implementation
        pass
    
    def warning(self, message):
        """
        Log a warning message.
        
        Args:
            message: Message to log
        """
        # Placeholder implementation
        pass
    
    def error(self, message):
        """
        Log an error message.
        
        Args:
            message: Message to log
        """
        # Placeholder implementation
        pass


class EventSystem:
    """
    Event system for the application.
    """
    def __init__(self):
        self.handlers = {}
    
    def register_handler(self, event_type, handler):
        """
        Register a handler for an event type.
        
        Args:
            event_type: Type of event
            handler: Function to handle the event
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def emit(self, event_type, event_data=None):
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            event_data: Data for the event
        """
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(event_data)


# Define what's available when doing "from abidance.core import *"
__all__ = [
    "ConfigManager",
    "Logger",
    "EventSystem",
] 