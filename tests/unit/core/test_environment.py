"""
Tests for the Environment class.

This module contains tests for the Environment class, which is responsible
for loading and accessing environment variables.
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from abidance.core.environment import Environment
from abidance.exceptions import ConfigurationError


class TestEnvironment:
    """Tests for the Environment class."""
    
    def test_environment_creation(self):
        """Test creating an Environment instance."""
        env = Environment()
        assert env is not None
        assert env._loaded is False
    
    @patch('abidance.core.environment.load_dotenv')
    @patch('pathlib.Path.exists')
    def test_load_env_file(self, mock_exists, mock_load_dotenv):
        """Test loading environment variables from a file."""
        mock_exists.return_value = True
        mock_load_dotenv.return_value = True
        
        env = Environment()
        env.load('.env.test')
        
        mock_exists.assert_called_once_with()
        mock_load_dotenv.assert_called_once()
        assert env._loaded is True
    
    @patch('pathlib.Path.exists')
    def test_load_env_file_not_found(self, mock_exists):
        """Test loading environment variables from a non-existent file."""
        mock_exists.return_value = False
        
        env = Environment()
        with pytest.raises(ConfigurationError, match="Environment file not found"):
            env.load('.env.nonexistent')
    
    @patch('abidance.core.environment.load_dotenv')
    @patch('pathlib.Path.exists')
    def test_load_env_file_failure(self, mock_exists, mock_load_dotenv):
        """Test failure when loading environment variables."""
        mock_exists.return_value = True
        mock_load_dotenv.return_value = False
        
        env = Environment()
        with pytest.raises(ConfigurationError, match="Failed to load environment"):
            env.load('.env.test')
    
    @patch.dict(os.environ, {'TEST_VAR': 'test_value'})
    def test_get_value(self):
        """Test getting an environment variable."""
        env = Environment()
        assert env.get('TEST_VAR') == 'test_value'
        assert env.get('NONEXISTENT_VAR') is None
        assert env.get('NONEXISTENT_VAR', 'default') == 'default'
    
    @patch.dict(os.environ, {})
    def test_get_required_value_missing(self):
        """Test getting a required environment variable that is missing."""
        env = Environment()
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get('REQUIRED_VAR', required=True)
    
    @patch.dict(os.environ, {
        'BOOL_TRUE_1': 'true',
        'BOOL_TRUE_2': 'yes',
        'BOOL_TRUE_3': '1',
        'BOOL_TRUE_4': 'y',
        'BOOL_TRUE_5': 'on',
        'BOOL_FALSE_1': 'false',
        'BOOL_FALSE_2': 'no',
        'BOOL_FALSE_3': '0',
        'BOOL_FALSE_4': 'n',
        'BOOL_FALSE_5': 'off',
        'BOOL_INVALID': 'invalid'
    })
    def test_get_bool(self):
        """Test getting a boolean environment variable."""
        env = Environment()
        
        # Test true values
        assert env.get_bool('BOOL_TRUE_1') is True
        assert env.get_bool('BOOL_TRUE_2') is True
        assert env.get_bool('BOOL_TRUE_3') is True
        assert env.get_bool('BOOL_TRUE_4') is True
        assert env.get_bool('BOOL_TRUE_5') is True
        
        # Test false values
        assert env.get_bool('BOOL_FALSE_1') is False
        assert env.get_bool('BOOL_FALSE_2') is False
        assert env.get_bool('BOOL_FALSE_3') is False
        assert env.get_bool('BOOL_FALSE_4') is False
        assert env.get_bool('BOOL_FALSE_5') is False
        
        # Test invalid value
        with pytest.raises(ConfigurationError, match="Cannot convert environment variable"):
            env.get_bool('BOOL_INVALID')
        
        # Test missing value
        assert env.get_bool('BOOL_MISSING') is None
        assert env.get_bool('BOOL_MISSING', default=True) is True
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_bool('BOOL_MISSING', required=True)
    
    @patch.dict(os.environ, {
        'INT_VALID': '123',
        'INT_INVALID': 'not_an_int'
    })
    def test_get_int(self):
        """Test getting an integer environment variable."""
        env = Environment()
        
        # Test valid value
        assert env.get_int('INT_VALID') == 123
        
        # Test invalid value
        with pytest.raises(ConfigurationError, match="Cannot convert environment variable"):
            env.get_int('INT_INVALID')
        
        # Test missing value
        assert env.get_int('INT_MISSING') is None
        assert env.get_int('INT_MISSING', default=456) == 456
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_int('INT_MISSING', required=True)
    
    @patch.dict(os.environ, {
        'FLOAT_VALID': '123.45',
        'FLOAT_INVALID': 'not_a_float'
    })
    def test_get_float(self):
        """Test getting a float environment variable."""
        env = Environment()
        
        # Test valid value
        assert env.get_float('FLOAT_VALID') == 123.45
        
        # Test invalid value
        with pytest.raises(ConfigurationError, match="Cannot convert environment variable"):
            env.get_float('FLOAT_INVALID')
        
        # Test missing value
        assert env.get_float('FLOAT_MISSING') is None
        assert env.get_float('FLOAT_MISSING', default=456.78) == 456.78
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_float('FLOAT_MISSING', required=True)
    
    @patch.dict(os.environ, {
        'LIST_JSON': '["item1", "item2", "item3"]',
        'LIST_CSV': 'item1,item2,item3'
    })
    def test_get_list(self):
        """Test getting a list environment variable."""
        env = Environment()
        
        # Test JSON list
        assert env.get_list('LIST_JSON') == ['item1', 'item2', 'item3']
        
        # Test CSV list
        assert env.get_list('LIST_CSV') == ['item1', 'item2', 'item3']
        
        # Test missing value
        assert env.get_list('LIST_MISSING') is None
        assert env.get_list('LIST_MISSING', default=['default']) == ['default']
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_list('LIST_MISSING', required=True)
    
    @patch.dict(os.environ, {
        'DICT_VALID': '{"key1": "value1", "key2": 123}',
        'DICT_INVALID': 'not_a_dict'
    })
    def test_get_dict(self):
        """Test getting a dictionary environment variable."""
        env = Environment()
        
        # Test valid value
        assert env.get_dict('DICT_VALID') == {'key1': 'value1', 'key2': 123}
        
        # Test invalid value
        with pytest.raises(ConfigurationError, match="Cannot convert environment variable"):
            env.get_dict('DICT_INVALID')
        
        # Test missing value
        assert env.get_dict('DICT_MISSING') is None
        assert env.get_dict('DICT_MISSING', default={'default': 'value'}) == {'default': 'value'}
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_dict('DICT_MISSING', required=True)
    
    @patch.dict(os.environ, {
        'PATH_VALID': '/path/to/file'
    })
    def test_get_path(self):
        """Test getting a path environment variable."""
        env = Environment()
        
        # Test valid value
        assert env.get_path('PATH_VALID') == Path('/path/to/file')
        
        # Test missing value
        assert env.get_path('PATH_MISSING') is None
        assert env.get_path('PATH_MISSING', default=Path('/default/path')) == Path('/default/path')
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_path('PATH_MISSING', required=True)
    
    @patch.dict(os.environ, {
        'TYPED_VALID': 'value',
        'TYPED_INVALID': 'value'
    })
    def test_get_typed(self):
        """Test getting a typed environment variable."""
        env = Environment()
        
        # Test valid value
        assert env.get_typed('TYPED_VALID', str) == 'value'
        
        # Test invalid value
        class CustomType:
            def __init__(self, value):
                if value != 'special':
                    raise ValueError("Invalid value")
                self.value = value
        
        with pytest.raises(ConfigurationError, match="Cannot convert environment variable"):
            env.get_typed('TYPED_INVALID', CustomType)
        
        # Test missing value
        assert env.get_typed('TYPED_MISSING', str) is None
        assert env.get_typed('TYPED_MISSING', str, default='default') == 'default'
        
        # Test required value
        with pytest.raises(ConfigurationError, match="Required environment variable not set"):
            env.get_typed('TYPED_MISSING', str, required=True)
    
    @patch.dict(os.environ, {
        'PREFIX_1': 'value1',
        'PREFIX_2': 'value2',
        'OTHER_1': 'other1'
    })
    def test_get_all(self):
        """Test getting all environment variables with a prefix."""
        env = Environment()
        
        # Test with prefix
        result = env.get_all('PREFIX_')
        assert 'PREFIX_1' in result
        assert 'PREFIX_2' in result
        assert 'OTHER_1' not in result
        
        # Test without prefix
        result = env.get_all()
        assert 'PREFIX_1' in result
        assert 'PREFIX_2' in result
        assert 'OTHER_1' in result 