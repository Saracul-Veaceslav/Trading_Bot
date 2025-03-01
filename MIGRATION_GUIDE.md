# Trading Bot Migration Guide

This document outlines the process for migrating from the current code structure with symbolic links to a standardized package structure.

## Current Structure

Currently, the project uses two directory structures:
- `Trading_Bot/` - The main package directory containing the actual code
- `bot/` - A symbolic link to `Trading_Bot` for backward compatibility

This creates confusion with imports, as some files import from `Trading_Bot` while others import from `bot`.

## New Structure

We're standardizing on a single package name: `trading_bot` (lowercase, underscore separated) for all imports.

The directory structure will be:
```
trading_bot/
├── __init__.py  # Package version and metadata
├── core/        # Core functionality
├── data/        # Data management
├── exchanges/   # Exchange integrations
├── strategies/  # Trading strategies
├── risk/        # Risk management
└── utils/       # Utility functions
```

## Migration Steps

### 1. Create New Package Structure

```bash
# Create the new package directory
mkdir -p trading_bot/{core,data,exchanges,strategies,risk,utils}

# Create empty __init__.py files
touch trading_bot/__init__.py
touch trading_bot/{core,data,exchanges,strategies,risk,utils}/__init__.py
```

### 2. Copy Code from Trading_Bot to trading_bot

```bash
# Copy files while maintaining directory structure
cp -R Trading_Bot/core/* trading_bot/core/
cp -R Trading_Bot/data/* trading_bot/data/
cp -R Trading_Bot/exchanges/* trading_bot/exchanges/
cp -R Trading_Bot/strategies/* trading_bot/strategies/
cp -R Trading_Bot/risk/* trading_bot/risk/
cp -R Trading_Bot/utils/* trading_bot/utils/
cp Trading_Bot/*.py trading_bot/
```

### 3. Update Imports

Update all imports to use the new package name:

- Change `from Trading_Bot.module import X` to `from trading_bot.module import X`
- Change `from bot.module import X` to `from trading_bot.module import X`

### 4. Testing Strategy

1. Run the tests with the old structure to establish a baseline
2. Run the tests with the new structure to verify functionality
3. Fix any import errors that occur

### 5. Deployment

Once all tests pass:

1. Remove the `bot` symbolic link
2. Create a migration guide for users
3. Update documentation to reference the new package name

## Import Examples

### Before

```python
# Using Trading_Bot
from Trading_Bot.strategies.sma_crossover import SMAcrossover
from Trading_Bot.config.settings import SETTINGS

# Using bot
from bot.data_manager import DataManager
from bot.exchange import BinanceTestnet
```

### After

```python
# All imports use trading_bot
from trading_bot.strategies.sma_crossover import SMAcrossover
from trading_bot.config.settings import SETTINGS
from trading_bot.data.manager import DataManager
from trading_bot.exchanges.binance import BinanceTestnet
```

## Script to Find and Replace Imports

A Python script will be provided to automate the import changes:

```python
import os
import re

def update_imports(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace Trading_Bot imports
    updated_content = re.sub(
        r'from\s+Trading_Bot\.([a-zA-Z0-9_\.]+)\s+import', 
        r'from trading_bot.\1 import', 
        content
    )
    
    # Replace bot imports
    updated_content = re.sub(
        r'from\s+bot\.([a-zA-Z0-9_\.]+)\s+import', 
        r'from trading_bot.\1 import', 
        content
    )
    
    # Replace import Trading_Bot
    updated_content = re.sub(
        r'import\s+Trading_Bot', 
        r'import trading_bot', 
        updated_content
    )
    
    # Replace import bot
    updated_content = re.sub(
        r'import\s+bot', 
        r'import trading_bot', 
        updated_content
    )
    
    if content != updated_content:
        with open(file_path, 'w') as file:
            file.write(updated_content)
        return True
    return False

def find_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    python_files = find_python_files('.')
    changed_files = 0
    
    for file_path in python_files:
        if update_imports(file_path):
            print(f"Updated imports in {file_path}")
            changed_files += 1
    
    print(f"Updated {changed_files} files")

if __name__ == "__main__":
    main()
```

## Breaking Changes and Workarounds

This migration may cause breaking changes for code that relies on the old import structure. To mitigate this:

1. Consider adding compatibility imports in the old locations
2. Create a detailed changelog explaining the changes
3. Version bump to indicate a potentially breaking change

## Timeline

1. Create and test new package structure (1-2 days)
2. Update imports (1 day)
3. Test all functionality (1-2 days)
4. Deploy changes (1 day)
5. Monitor for issues (ongoing)

## Support

If you encounter any issues during migration, please:
1. Check the updated documentation
2. Refer to the examples in this guide
3. Create an issue in the repository with details of the problem 