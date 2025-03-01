#!/usr/bin/env python3
"""
Script to fix the test_strategy_executor.py file by correcting the parameter name
from 'timeframe' to 'interval' in the StrategyExecutor initialization.
"""

import os
import re

def fix_test_file():
    """Fix the test_strategy_executor.py file."""
    file_path = 'tests/test_strategy_executor.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all occurrences of timeframe parameter with interval
    pattern = r'timeframe=[\'"]([^\'"]+)[\'"]'
    replacement = r'interval="\1"'
    new_content = re.sub(pattern, replacement, content)
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_test_file() 