"""
Tests for the Configuration Module.

These tests ensure that the configuration loading, merging, and validation
functions work correctly under various conditions.
"""
import pytest
import os
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

from Trading_Bot.core.config import (
    load_config, 
    save_config, 
    validate_config, 
    ConfigurationError,
    DEFAULT_CONFIG
)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def json_config_file(temp_config_dir):
    """Create a temporary JSON configuration file."""
    config = {
        'exchange': 'binance_test',
        'symbols': ['ETH/USDT', 'BTC/USDT'],
        'risk': {
            'max_position_size': 0.2,
            'stop_loss': 0.05
        }
    }
    
    config_path = os.path.join(temp_config_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    return config_path


@pytest.fixture
def yaml_config_file(temp_config_dir):
    """Create a temporary YAML configuration file."""
    config = {
        'exchange': 'ftx',
        'symbols': ['SOL/USDT', 'ADA/USDT'],
        'risk': {
            'max_position_size': 0.15,
            'stop_loss': 0.03
        }
    }
    
    config_path = os.path.join(temp_config_dir, 'config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    return config_path


def test_load_config_default():
    """
    Feature: Configuration Loading - Defaults
    
    Scenario: Load default configuration
        Given no configuration file is provided
        And no matching config file is found in default locations
        When load_config is called
        Then it should return the default configuration
    """
    # Mock to ensure no default config files are found
    with patch('os.path.exists', return_value=False):
        config = load_config()
        
        # Verify that default values are used
        assert config['exchange'] == DEFAULT_CONFIG['exchange']
        assert config['symbols'] == DEFAULT_CONFIG['symbols']
        assert config['strategy'] == DEFAULT_CONFIG['strategy']


def test_load_config_json(json_config_file):
    """
    Feature: Configuration Loading - JSON
    
    Scenario: Load configuration from JSON file
        Given a JSON configuration file
        When load_config is called with the file path
        Then it should load and merge the configuration correctly
    """
    config = load_config(json_config_file)
    
    # Verify loaded values
    assert config['exchange'] == 'binance_test'
    assert config['symbols'] == ['ETH/USDT', 'BTC/USDT']
    assert config['risk']['max_position_size'] == 0.2
    assert config['risk']['stop_loss'] == 0.05
    
    # Verify default values are preserved for fields not in the JSON
    assert 'update_interval' in config
    assert config['update_interval'] == DEFAULT_CONFIG['update_interval']


def test_load_config_yaml(yaml_config_file):
    """
    Feature: Configuration Loading - YAML
    
    Scenario: Load configuration from YAML file
        Given a YAML configuration file
        When load_config is called with the file path
        Then it should load and merge the configuration correctly
    """
    config = load_config(yaml_config_file)
    
    # Verify loaded values
    assert config['exchange'] == 'ftx'
    assert config['symbols'] == ['SOL/USDT', 'ADA/USDT']
    assert config['risk']['max_position_size'] == 0.15
    assert config['risk']['stop_loss'] == 0.03
    
    # Verify default values are preserved for fields not in the YAML
    assert 'update_interval' in config
    assert config['update_interval'] == DEFAULT_CONFIG['update_interval']


def test_load_config_file_not_found():
    """
    Feature: Configuration Loading - File Not Found
    
    Scenario: Handle file not found error
        Given a non-existent configuration file path
        When load_config is called with the file path
        Then it should raise a FileNotFoundError
    """
    non_existent_file = '/path/to/non_existent_config.json'
    
    with pytest.raises(FileNotFoundError):
        load_config(non_existent_file)


def test_load_config_invalid_format():
    """
    Feature: Configuration Loading - Invalid Format
    
    Scenario: Handle invalid file format
        Given a configuration file with an unsupported extension
        When load_config is called with the file path
        Then it should raise a ValueError
    """
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        tmp.write(b'invalid config format')
        tmp.flush()
        
        with pytest.raises(ValueError):
            load_config(tmp.name)


def test_load_config_environment_variables():
    """
    Feature: Configuration Loading - Environment Variables
    
    Scenario: Override configuration with environment variables
        Given environment variables with TRADING_BOT_ prefix
        When load_config is called
        Then it should incorporate the environment variables into the configuration
    """
    env_vars = {
        'TRADING_BOT_EXCHANGE': 'kraken',
        'TRADING_BOT_RISK__MAX_POSITION_SIZE': '0.3',
        'TRADING_BOT_LOG_LEVEL': 'DEBUG',
        'TRADING_BOT_WEB__ENABLED': 'true'
    }
    
    with patch.dict(os.environ, env_vars):
        config = load_config()
        
        # Verify environment variables were used
        assert config['exchange'] == 'kraken'
        assert config['risk']['max_position_size'] == 0.3
        assert config['log_level'] == 'DEBUG'
        assert config['web']['enabled'] is True


def test_save_config_json(temp_config_dir):
    """
    Feature: Configuration Saving - JSON
    
    Scenario: Save configuration to JSON file
        Given a configuration dictionary
        When save_config is called with a JSON file path
        Then it should save the configuration to the file in JSON format
    """
    config = {
        'exchange': 'kucoin',
        'symbols': ['DOT/USDT'],
        'test_value': True
    }
    
    config_path = os.path.join(temp_config_dir, 'saved_config.json')
    save_config(config, config_path)
    
    # Verify file was created
    assert os.path.exists(config_path)
    
    # Verify content
    with open(config_path, 'r') as f:
        loaded_config = json.load(f)
        assert loaded_config['exchange'] == 'kucoin'
        assert loaded_config['symbols'] == ['DOT/USDT']
        assert loaded_config['test_value'] is True


def test_save_config_yaml(temp_config_dir):
    """
    Feature: Configuration Saving - YAML
    
    Scenario: Save configuration to YAML file
        Given a configuration dictionary
        When save_config is called with a YAML file path
        Then it should save the configuration to the file in YAML format
    """
    config = {
        'exchange': 'bitfinex',
        'symbols': ['XRP/USDT'],
        'nested': {
            'value': 42
        }
    }
    
    config_path = os.path.join(temp_config_dir, 'saved_config.yaml')
    save_config(config, config_path)
    
    # Verify file was created
    assert os.path.exists(config_path)
    
    # Verify content
    with open(config_path, 'r') as f:
        loaded_config = yaml.safe_load(f)
        assert loaded_config['exchange'] == 'bitfinex'
        assert loaded_config['symbols'] == ['XRP/USDT']
        assert loaded_config['nested']['value'] == 42


def test_validate_config_valid():
    """
    Feature: Configuration Validation - Valid Config
    
    Scenario: Validate a valid configuration
        Given a valid configuration dictionary
        When validate_config is called
        Then it should not raise any exceptions
    """
    config = {
        'exchange': 'binance',
        'symbols': ['BTC/USDT', 'ETH/USDT'],
        'risk': {
            'max_position_size': 0.1,
            'stop_loss': 0.05,
            'take_profit': 0.1,
            'max_open_trades': 3
        }
    }
    
    # Should not raise any exceptions
    validate_config(config)


def test_validate_config_missing_required():
    """
    Feature: Configuration Validation - Missing Required Fields
    
    Scenario: Validate a configuration with missing required fields
        Given a configuration dictionary missing required fields
        When validate_config is called
        Then it should raise a ConfigurationError
    """
    # Missing 'symbols' field
    config = {
        'exchange': 'binance',
        # No symbols
    }
    
    with pytest.raises(ConfigurationError) as excinfo:
        validate_config(config)
    
    assert 'symbols' in str(excinfo.value)


def test_validate_config_invalid_symbols():
    """
    Feature: Configuration Validation - Invalid Symbols
    
    Scenario: Validate a configuration with invalid symbols format
        Given a configuration dictionary with symbols not as a list
        When validate_config is called
        Then it should raise a ConfigurationError
    """
    # Symbols is not a list
    config = {
        'exchange': 'binance',
        'symbols': 'BTC/USDT'  # Should be a list
    }
    
    with pytest.raises(ConfigurationError) as excinfo:
        validate_config(config)
    
    assert 'symbols' in str(excinfo.value)


def test_validate_config_invalid_risk_params():
    """
    Feature: Configuration Validation - Invalid Risk Parameters
    
    Scenario: Validate a configuration with invalid risk parameters
        Given a configuration dictionary with invalid risk parameters
        When validate_config is called
        Then it should raise a ConfigurationError
    """
    # Invalid risk parameters
    config = {
        'exchange': 'binance',
        'symbols': ['BTC/USDT'],
        'risk': {
            'max_position_size': 1.5,  # Should be <= 1
            'stop_loss': 0.6,          # Should be <= 0.5
            'max_open_trades': 0       # Should be >= 1
        }
    }
    
    # Test each invalid parameter
    with pytest.raises(ConfigurationError) as excinfo:
        validate_config(config)
    
    assert 'max_position_size' in str(excinfo.value)
    
    # Fix max_position_size and test stop_loss
    config['risk']['max_position_size'] = 0.5
    with pytest.raises(ConfigurationError) as excinfo:
        validate_config(config)
    
    assert 'stop_loss' in str(excinfo.value)
    
    # Fix stop_loss and test max_open_trades
    config['risk']['stop_loss'] = 0.1
    with pytest.raises(ConfigurationError) as excinfo:
        validate_config(config)
    
    assert 'max_open_trades' in str(excinfo.value) 