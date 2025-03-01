#!/usr/bin/env python3
"""
Script to fix the test_sma_crossover.py file by correctly initializing
the SMAcrossover class with short_window and long_window parameters.
"""

import os
import re

def fix_test_file():
    """Fix the test_sma_crossover.py file."""
    file_path = 'tests/test_sma_crossover.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the setUp method
    setup_pattern = r'def setUp\(self\):(.*?)self\.strategy = SMAcrossover\(self\.trading_logger, self\.error_logger\)'
    setup_replacement = r'def setUp(self):\1# Initialize with correct parameter order: short_window, long_window, then loggers\n        self.strategy = SMAcrossover(10, 50, trading_logger=self.trading_logger, error_logger=self.error_logger)'
    
    new_content = re.sub(setup_pattern, setup_replacement, content, flags=re.DOTALL)
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    # Now check pytest_test_sma_crossover.py if it exists
    pytest_file_path = 'tests/pytest_test_sma_crossover.py'
    if os.path.exists(pytest_file_path):
        with open(pytest_file_path, 'r') as f:
            content = f.read()
        
        # Fix the initialization pattern for pytest style tests too
        init_pattern = r'SMAcrossover\([^,)]*,[^,)]*\)'
        init_replacement = r'SMAcrossover(10, 50, trading_logger=mock_trading_logger, error_logger=mock_error_logger)'
        
        new_content = re.sub(init_pattern, init_replacement, content)
        
        with open(pytest_file_path, 'w') as f:
            f.write(new_content)
        
        print(f"Fixed {pytest_file_path}")
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_test_file() 