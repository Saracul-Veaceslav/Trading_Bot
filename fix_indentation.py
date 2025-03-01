#!/usr/bin/env python3
"""
Script to fix indentation issues in the test_strategy_executor.py file.
"""

import os

def fix_indentation():
    """Fix indentation issues in the test_strategy_executor.py file."""
    file_path = 'tests/test_strategy_executor.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the indentation in the try-except block
    fixed_content = content.replace("try:\n            importlib.import_module.assert_called_once_with('bot.strategies.sma_crossover')\n        except AssertionError:", 
                                   "try:\n            importlib.import_module.assert_called_once_with('bot.strategies.sma_crossover')\n        except AssertionError:")
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed indentation in {file_path}")

if __name__ == "__main__":
    fix_indentation() 