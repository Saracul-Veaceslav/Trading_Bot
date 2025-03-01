#!/usr/bin/env python3
"""
Script to fix the test_data_manager.py file by ensuring the directory 
for the HISTORICAL_TRADES_PATH exists before running tests.
"""

import os
import re
import tempfile

def fix_test_file():
    """Fix the test_data_manager.py file."""
    file_path = 'tests/test_data_manager.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add temporary directory creation to setUp method
    setup_pattern = r'def setUp\(self\):(.*?)self\.data_manager = DataManager\('
    setup_replacement = r'def setUp(self):\1# Create temp directories for test files\n        os.makedirs(os.path.dirname(SETTINGS["HISTORICAL_TRADES_PATH"]), exist_ok=True)\n        os.makedirs(os.path.dirname(SETTINGS["OHLCV_DATA_PATH"]), exist_ok=True)\n        \n        self.data_manager = DataManager('
    
    # Use re.DOTALL to make . match newlines
    new_content = re.sub(setup_pattern, setup_replacement, content, flags=re.DOTALL)
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_test_file() 