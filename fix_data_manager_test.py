#!/usr/bin/env python3
"""
Script to fix the test_data_manager.py file by ensuring proper initialization
of data paths and making temporary directories for testing.
"""

import os
import re
import tempfile
import shutil

def fix_test_file():
    """Fix the test_data_manager.py file."""
    file_path = 'tests/test_data_manager.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import for tempfile and shutil if not present
    imports_pattern = r'import unittest'
    imports_replacement = r'import unittest\nimport tempfile\nimport shutil\nimport os'
    
    new_content = re.sub(imports_pattern, imports_replacement, content)
    
    # Fix the setUp method to use temporary directories
    setup_pattern = r'def setUp\(self\):(.*?)(self\.data_manager = DataManager\()'
    setup_replacement = r'def setUp(self):\1# Create temporary directories for testing\n        self.test_dir = tempfile.mkdtemp()\n        self.ohlcv_dir = os.path.join(self.test_dir, "ohlcv")\n        self.trades_dir = os.path.join(self.test_dir, "trades")\n        os.makedirs(self.ohlcv_dir, exist_ok=True)\n        os.makedirs(self.trades_dir, exist_ok=True)\n        \n        # Mock the config settings for testing\n        self.original_ohlcv_path = config.settings["OHLCV_DATA_PATH"]\n        self.original_trades_path = config.settings["HISTORICAL_TRADES_PATH"]\n        config.settings["OHLCV_DATA_PATH"] = self.ohlcv_dir\n        config.settings["HISTORICAL_TRADES_PATH"] = self.trades_dir\n        \n        \2'
    
    new_content = re.sub(setup_pattern, setup_replacement, new_content, flags=re.DOTALL)
    
    # Fix the tearDown method to clean up temporary directories
    teardown_pattern = r'def tearDown\(self\):(.*?)(pass)'
    teardown_replacement = r'def tearDown(self):\1# Restore original settings\n        config.settings["OHLCV_DATA_PATH"] = self.original_ohlcv_path\n        config.settings["HISTORICAL_TRADES_PATH"] = self.original_trades_path\n        \n        # Clean up temporary directories\n        shutil.rmtree(self.test_dir)'
    
    new_content = re.sub(teardown_pattern, teardown_replacement, new_content, flags=re.DOTALL)
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_test_file() 