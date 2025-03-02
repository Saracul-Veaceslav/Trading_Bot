import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import yaml

# Update import path
from abidance.core.configuration import Configuration, ConfigurationError


class TestConfiguration:
    """Test the Configuration class."""

    def test_configuration_creation(self):
        """Test that a Configuration object can be created."""
        config = Configuration()
        assert isinstance(config, Configuration)
        assert config.data == {}

    def test_load_from_dict(self):
        """Test loading configuration from a dictionary."""
        config_data = {"key1": "value1", "key2": 2, "key3": {"nested": True}}
        config = Configuration()
        config.load_from_dict(config_data)
        assert config.data == config_data

    def test_get_value(self):
        """Test getting values from the configuration."""
        config_data = {"key1": "value1", "key2": 2, "key3": {"nested": True}}
        config = Configuration()
        config.load_from_dict(config_data)
        assert config.get("key1") == "value1"
        assert config.get("key2") == 2
        assert config.get("key3") == {"nested": True}
        assert config.get("key3.nested") is True
        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"

    def test_set_value(self):
        """Test setting values in the configuration."""
        config = Configuration()
        config.set("key1", "value1")
        assert config.get("key1") == "value1"
        config.set("key2.nested", True)
        assert config.get("key2.nested") is True
        assert config.get("key2") == {"nested": True}

    def test_load_from_yaml(self):
        """Test loading configuration from a YAML file."""
        config_data = {"key1": "value1", "key2": 2, "key3": {"nested": True}}
        yaml_content = yaml.dump(config_data)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write(yaml_content)
            temp_path = temp.name
        
        try:
            config = Configuration()
            config.load_from_yaml(temp_path)
            assert config.data == config_data
        finally:
            os.unlink(temp_path)

    def test_load_from_yaml_file_not_found(self):
        """Test that loading from a non-existent YAML file raises an error."""
        from abidance.core.configuration import Configuration, ConfigurationError
        
        config = Configuration()
        with pytest.raises(ConfigurationError) as excinfo:
            config.load_from_yaml("/nonexistent/path.yaml")
        assert "File not found" in str(excinfo.value)

    def test_load_from_yaml_invalid_yaml(self):
        """Test that loading invalid YAML raises an error."""
        from abidance.core.configuration import Configuration, ConfigurationError
        
        invalid_yaml = "key1: value1\nkey2: : invalid"
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write(invalid_yaml)
            temp_path = temp.name
        
        try:
            config = Configuration()
            with pytest.raises(ConfigurationError) as excinfo:
                config.load_from_yaml(temp_path)
            assert "Invalid YAML" in str(excinfo.value)
        finally:
            os.unlink(temp_path)

    def test_load_from_yaml_file(self):
        """Test loading configuration from a YAML file."""
        from abidance.core.configuration import Configuration
        
        # Create a temporary YAML file
        config_data = {
            "app": {
                "name": "Abidance",
                "version": "1.0.0"
            },
            "trading": {
                "default_exchange": "binance",
                "default_symbol": "BTC/USDT"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            yaml.dump(config_data, temp_file)
            temp_file_path = temp_file.name
        
        try:
            config = Configuration()
            config.load_from_yaml(temp_file_path)
            
            assert config.get("app.name") == "Abidance"
            assert config.get("app.version") == "1.0.0"
            assert config.get("trading.default_exchange") == "binance"
            assert config.get("trading.default_symbol") == "BTC/USDT"
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_get_with_default(self):
        """Test getting configuration with default value."""
        from abidance.core.configuration import Configuration
        
        config = Configuration()
        config.load_from_dict({
            "app": {
                "name": "Abidance",
                "version": "1.0.0",
                "details": {
                    "build": {
                        "number": 123
                    }
                }
            }
        })
        
        # Test getting existing values
        assert config.get("app.name") == "Abidance"
        
        # Test getting non-existent values with default
        assert config.get("app.description", "A trading bot") == "A trading bot"
        assert config.get("app.details.build.date", "2023-01-01") == "2023-01-01"

    def test_get_nested_keys(self):
        """Test getting nested configuration keys."""
        from abidance.core.configuration import Configuration
        
        config = Configuration()
        config.load_from_dict({
            "app": {
                "name": "Abidance",
                "details": {
                    "version": "1.0.0",
                    "build": {
                        "number": 123,
                        "date": "2023-01-01"
                    }
                }
            }
        })
        
        assert config.get("app.details.version") == "1.0.0"
        assert config.get("app.details.build.number") == 123
        assert config.get("app.details.build.date") == "2023-01-01"

    def test_load_from_env_variables(self):
        """Test loading configuration from environment variables."""
        from abidance.core.configuration import Configuration
        
        # Mock environment variables
        mock_env = {
            "ABIDANCE_APP_NAME": "Abidance",
            "ABIDANCE_APP_VERSION": "1.0.0",
            "ABIDANCE_TRADING_DEFAULT_EXCHANGE": "binance",
            "ABIDANCE_TRADING_RISK_PERCENTAGE": "1.5",
            "ABIDANCE_TRADING_ENABLED": "true",
            "ABIDANCE_TRADING_MAX_TRADES": "10"
        }
        
        with patch.dict(os.environ, mock_env):
            config = Configuration()
            config.load_from_env(prefix="ABIDANCE_")
            
            assert config.get("app.name") == "Abidance"
            assert config.get("app.version") == "1.0.0"
            assert config.get("trading.default_exchange") == "binance"
            assert config.get("trading.risk_percentage") == 1.5
            assert config.get("trading.enabled") is True
            assert config.get("trading.max_trades") == 10

    def test_load_from_env_with_type_conversion(self):
        """Test type conversion when loading from environment variables."""
        from abidance.core.configuration import Configuration
        
        with patch.dict(os.environ, {
            "ABIDANCE_APP_VERSION": "1.0.0",
            "ABIDANCE_TRADING_RISK_PERCENTAGE": "1.5",
            "ABIDANCE_TRADING_ENABLED": "true",
            "ABIDANCE_TRADING_MAX_TRADES": "10",
            "ABIDANCE_TRADING_SYMBOLS": '["BTC/USDT", "ETH/USDT"]'
        }):
            config = Configuration()
            config.load_from_env(prefix="ABIDANCE_")
            
            assert config.get("app.version") == "1.0.0"  # String
            assert config.get("trading.risk_percentage") == 1.5  # Float
            assert config.get("trading.enabled") is True  # Boolean
            assert config.get("trading.max_trades") == 10  # Integer
            assert config.get("trading.symbols") == ["BTC/USDT", "ETH/USDT"]  # List

    def test_merge_configurations(self):
        """Test merging multiple configurations."""
        from abidance.core.configuration import Configuration
        
        config1 = Configuration()
        config1.load_from_dict({
            "app": {
                "name": "Abidance",
                "version": "1.0.0"
            },
            "trading": {
                "default_exchange": "binance"
            }
        })
        
        config2 = Configuration()
        config2.load_from_dict({
            "app": {
                "version": "1.1.0"  # This should override
            },
            "trading": {
                "default_symbol": "BTC/USDT"  # This should be added
            }
        })
        
        # Merge config2 into config1
        config1.merge(config2)
        
        assert config1.get("app.name") == "Abidance"
        assert config1.get("app.version") == "1.1.0"  # Overridden
        assert config1.get("trading.default_exchange") == "binance"
        assert config1.get("trading.default_symbol") == "BTC/USDT"  # Added

    def test_validate_required_keys(self):
        """Test validation of required configuration keys."""
        from abidance.core.configuration import Configuration, ConfigurationError
        
        config = Configuration()
        config.load_from_dict({
            "app": {
                "name": "Abidance",
                "version": "1.0.0"
            },
            "trading": {
                "default_exchange": "binance"
            }
        })
        
        # Should not raise an error
        config.validate_required_keys(["app.name", "app.version", "trading.default_exchange"])
        
        # Should raise an error for missing key
        with pytest.raises(ConfigurationError) as excinfo:
            config.validate_required_keys(["app.name", "trading.default_symbol"])
        
        assert "Missing required configuration key" in str(excinfo.value)

    def test_to_dict(self):
        """Test converting configuration to a dictionary."""
        from abidance.core.configuration import Configuration
        
        config_data = {
            "app": {
                "name": "Abidance",
                "version": "1.0.0"
            },
            "trading": {
                "default_exchange": "binance",
                "default_symbol": "BTC/USDT"
            }
        }
        
        config = Configuration()
        config.load_from_dict(config_data)
        
        assert config.to_dict() == config_data

    def test_save_to_yaml(self):
        """Test saving configuration to a YAML file."""
        from abidance.core.configuration import Configuration
        
        config_data = {
            "app": {
                "name": "Abidance",
                "version": "1.0.0"
            },
            "trading": {
                "default_exchange": "binance",
                "default_symbol": "BTC/USDT"
            }
        }
        
        config = Configuration()
        config.load_from_dict(config_data)
        
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # Save configuration to the file
            config.save_to_yaml(temp_file_path)
            
            # Load the saved configuration and verify
            with open(temp_file_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data == config_data
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path) 