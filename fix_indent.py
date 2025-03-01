#!/usr/bin/env python3
"""
Simple script to fix indentation in test_strategy_executor.py
"""

import re

def fix_file():
    file_path = 'tests/test_strategy_executor.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the problematic section and fix indentation
    pattern = r'(try:\s+importlib\.import_module\.assert_called_once_with\([^)]+\)\s+)except AssertionError:'
    replacement = r'\1        except AssertionError:'
    
    fixed_content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed indentation in {file_path}")

if __name__ == "__main__":
    fix_file() 