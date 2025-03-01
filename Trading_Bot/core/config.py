"""
Trading Bot Configuration Management

This module handles loading, validating, and accessing configuration settings
for the Trading Bot. It supports configuration from files, environment variables,
and command line arguments.
"""
import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

logger = logging.getLogger('trading_bot.core.config')

# Default configuration values
DEFAULT_CONFIG = {
    'exchange': 'binance',
    'symbols': ['BTC/USDT'],
    'update_interval': 60,  # seconds
    'log_level': 'INFO',
    'data_dir': 'data',
    'strategy': 'sma_crossover',
    'strategy_sma_crossover': {
        'short_window': 20,
        'long_window': 50
    },
    'risk': {
        'max_position_size': 0.1,  # 10% of portfolio
        'stop_loss': 0.02,         # 2% stop loss
        'take_profit': 0.05,       # 5% take profit
        'max_open_trades': 3
    },
    'paper_trading': {
        'initial_balance': 10000,
        'fee_rate': 0.001          # 0.1% fee
    },
    'database': {
        'type': 'sqlite',
        'path': 'data/trading_bot.db'
    },
    'web': {
        'enabled': False,
        'port': 5000,
        'host': '127.0.0.1'
    }
}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file and merge with defaults.
    
    Args:
        config_path: Path to the configuration file (JSON or YAML)
        
    Returns:
        Dict[str, Any]: Merged configuration dictionary
        
    Raises:
        FileNotFoundError: If the config file is not found
        ValueError: If the config file is invalid
    """
    config = DEFAULT_CONFIG.copy()
    
    # If no config path provided, look for default config file locations
    if not config_path:
        possible_paths = [
            'config.json',
            'config.yaml',
            'config.yml',
            os.path.expanduser('~/.trading_bot/config.json'),
            os.path.expanduser('~/.trading_bot/config.yaml'),
            os.path.expanduser('~/.trading_bot/config.yml'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
    
    # Load configuration from file if provided or found
    file_config = {}
    if config_path:
        try:
            file_config = _load_config_file(config_path)
            
            # Deep merge configurations
            _deep_merge(config, file_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            raise
    
    # Override with environment variables
    env_config = _load_from_env()
    _deep_merge(config, env_config)
    
    # Create a final copy to ensure we return a fresh dictionary
    final_config = {}
    for key, value in config.items():
        # Special handling for symbols to ensure it's always a list
        if key == 'symbols':
            if isinstance(value, str):
                final_config[key] = [value]
            else:
                final_config[key] = value
        else:
            final_config[key] = value
    
    return final_config

def _load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a file based on its extension.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
        
    Raises:
        FileNotFoundError: If the file is not found
        ValueError: If the file format is unsupported or invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config = {}
    with open(config_path, 'r') as f:
        # Determine file type based on extension
        if config_path.endswith('.json'):
            config = json.load(f)
        elif config_path.endswith(('.yaml', '.yml')):
            config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path}")
    
    # Ensure symbols is a list (if single string, convert to list)
    if 'symbols' in config and isinstance(config['symbols'], str):
        config['symbols'] = [config['symbols']]
        
    return config

def _load_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Environment variables should be prefixed with "TRADING_BOT_" and use double underscore
    as separator for nested keys. For example, TRADING_BOT_RISK__MAX_POSITION_SIZE=0.1
    
    Returns:
        Dict[str, Any]: Configuration dictionary from environment variables
    """
    config = {}
    prefix = "TRADING_BOT_"
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and split into parts
            key_path = key[len(prefix):].lower().split('__')
            
            # Convert value to appropriate type
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif _is_float(value):
                value = float(value)
            
            # Build nested dictionary
            current = config
            for part in key_path[:-1]:
                current = current.setdefault(part, {})
            
            # Set the value
            current[key_path[-1]] = value
    
    return config

def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, modifying the target in place.
    
    Args:
        target: Target dictionary to merge into
        source: Source dictionary to merge from
        
    Returns:
        Dict[str, Any]: Merged dictionary (same object as target)
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target

def _is_float(value: str) -> bool:
    """Check if a string can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to save the configuration to
        
    Raises:
        ValueError: If the file format is unsupported
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    # Determine file type based on extension
    if config_path.endswith('.json'):
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    elif config_path.endswith(('.yaml', '.yml')):
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
    else:
        raise ValueError(f"Unsupported configuration file format: {config_path}")
    
    logger.info(f"Saved configuration to {config_path}")

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration against expected structure and constraints.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigurationError: If the configuration is invalid
    """
    # Required fields
    required_fields = ['exchange', 'symbols']
    for field in required_fields:
        if field not in config:
            raise ConfigurationError(f"Missing required configuration field: {field}")
    
    # Validate exchange
    exchange = config.get('exchange', '')
    if isinstance(exchange, str):
        if not exchange.strip():
            raise ConfigurationError("Exchange cannot be empty")
    elif isinstance(exchange, dict):
        if 'name' not in exchange or not exchange.get('name', '').strip():
            raise ConfigurationError("Exchange name cannot be empty when using object format")
    
    # Validate that symbols is a list
    symbols = config.get('symbols', [])
    if not isinstance(symbols, list):
        raise ConfigurationError("Configuration field 'symbols' must be a list")
    
    # Validate that symbols list is not empty
    if len(symbols) == 0:
        raise ConfigurationError("Symbols list cannot be empty")
    
    # Validate risk parameters if present
    risk = config.get('risk', {})
    if risk:
        # Ensure risk parameters are within reasonable bounds
        if 'max_position_size' in risk and (risk['max_position_size'] <= 0 or risk['max_position_size'] > 1):
            raise ConfigurationError("Risk parameter 'max_position_size' must be between 0 and 1")
        
        if 'stop_loss' in risk and (risk['stop_loss'] <= 0 or risk['stop_loss'] > 0.5):
            raise ConfigurationError("Risk parameter 'stop_loss' must be between 0 and 0.5")
        
        if 'take_profit' in risk and (risk['take_profit'] <= 0 or risk['take_profit'] > 1):
            raise ConfigurationError("Risk parameter 'take_profit' must be between 0 and 1")
        
        if 'max_open_trades' in risk and risk['max_open_trades'] < 1:
            raise ConfigurationError("Risk parameter 'max_open_trades' must be greater than 0")
    
    # Validate paper trading parameters if present
    paper = config.get('paper_trading', {})
    if paper:
        if 'initial_balance' in paper and paper['initial_balance'] <= 0:
            raise ConfigurationError("Paper trading parameter 'initial_balance' must be greater than 0")
        
        if 'fee_rate' in paper and (paper['fee_rate'] < 0 or paper['fee_rate'] > 0.1):
            raise ConfigurationError("Paper trading parameter 'fee_rate' must be between 0 and 0.1")
    
    logger.debug("Configuration validated successfully") 