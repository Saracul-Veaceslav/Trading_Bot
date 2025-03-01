#!/usr/bin/env python3
"""
Script to update imports in test files to match the new structure.
"""

import os
import re
import sys
from pathlib import Path


def update_imports(file_path):
    """
    Update imports in test files to match the new structure.
    
    Args:
        file_path (str): Path to the file to update
    
    Returns:
        bool: True if file was updated, False otherwise
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the import patterns to replace
    patterns = [
        # Fix imports for moved files
        (r'from\s+trading_bot\.data_manager\s+import', r'from trading_bot.data.manager import'),
        (r'from\s+trading_bot\.strategy_executor\s+import', r'from trading_bot.core.strategy_executor import'),
        (r'from\s+trading_bot\.exchange\s+import', r'from trading_bot.exchanges.base import'),
        # Fix any remaining bot imports
        (r'from\s+bot\.', r'from trading_bot.'),
        (r'import\s+bot\.', r'import trading_bot.'),
        # Fix patch statements
        (r"patch\('bot\.", r"patch('trading_bot."),
    ]
    
    # Apply the replacements
    updated_content = content
    for pattern, replacement in patterns:
        updated_content = re.sub(pattern, replacement, updated_content)
    
    # Check if the content was updated
    if content != updated_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    
    return False


def main():
    """Find and update test files."""
    # Find all Python files in the tests directory
    test_files = list(Path('tests').glob('**/*.py'))
    
    # Update imports in each file
    updated_files = 0
    for file_path in test_files:
        if update_imports(str(file_path)):
            print(f"Updated imports in {file_path}")
            updated_files += 1
    
    print(f"Updated {updated_files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 