import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Centralized configuration management for the trading bot.
    
    This class handles loading, validating, and accessing configuration
    settings from various sources (env vars, config files, etc.)
    """
    
    DEFAULT_CONFIG_PATH = "config/config.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or os.environ.get("CONFIG_PATH", self.DEFAULT_CONFIG_PATH)
        self.config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from the specified file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        self.config = yaml.safe_load(file) or {}
                    elif self.config_path.endswith('.json'):
                        self.config = json.load(file) or {}
                    else:
                        raise ValueError(f"Unsupported config file format: {self.config_path}")
                    
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found: {self.config_path}. Using default values.")
                self.config = {}
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The configuration key to look up
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        # First check environment variables (with TRADING_BOT_ prefix)
        env_key = f"TRADING_BOT_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # Then check the loaded config
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key to set
            value: The value to set
        """
        keys = key.split('.')
        config = self.config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save the current configuration to a file.
        
        Args:
            path: Path to save to (defaults to the loaded config path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        save_path = path or self.config_path
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as file:
                if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                    yaml.dump(self.config, file, default_flow_style=False)
                elif save_path.endswith('.json'):
                    json.dump(self.config, file, indent=2)
                else:
                    raise ValueError(f"Unsupported config file format: {save_path}")
                    
            logger.info(f"Saved configuration to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
            
    def get_all(self) -> Dict[str, Any]:
        """
        Get the complete configuration.
        
        Returns:
            Dict[str, Any]: The complete configuration
        """
        return self.config.copy()
        
    def merge(self, config_dict: Dict[str, Any]) -> None:
        """
        Merge a configuration dictionary with the current configuration.
        
        Args:
            config_dict: Dictionary to merge
        """
        self._merge_dicts(self.config, config_dict)
    
    def _merge_dicts(self, d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.
        
        Args:
            d1: First dictionary (modified in place)
            d2: Second dictionary
            
        Returns:
            Dict[str, Any]: Merged dictionary
        """
        for k, v in d2.items():
            if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                self._merge_dicts(d1[k], v)
            else:
                d1[k] = v
        return d1


# Create a singleton instance
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """
    Get the singleton ConfigManager instance.
    
    Returns:
        ConfigManager: The singleton instance
    """
    return config_manager 