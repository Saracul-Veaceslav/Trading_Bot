"""
Script to test if all imports are working correctly.
Run this script to check if your project structure is set up correctly.
"""
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("PYTHONPATH:", sys.path)

# Add current directory to path if not already there
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())
    print("Added current directory to PYTHONPATH")

try:
    # Try importing from bot directory (symbolic link)
    print("\nTrying imports from 'bot' namespace:")
    import trading_bot
    print("✅ Successfully imported 'bot' package")
except ImportError as e:
    print(f"❌ Failed to import 'bot' package: {e}")

try:
    # Try importing from Trading_Bot directory (actual directory)
    print("\nTrying imports from 'Trading_Bot' namespace:")
    import trading_bot
    print("✅ Successfully imported 'Trading_Bot' package")
except ImportError as e:
    print(f"❌ Failed to import 'Trading_Bot' package: {e}")

try:
    # Try importing specific classes from the actual directory path
    print("\nTrying to import specific classes from actual directory:")
    from trading_bot.strategies.sma_crossover import SMAcrossover
    print("✅ Successfully imported 'SMAcrossover' class")
    from trading_bot.exchange import BinanceTestnet
    print("✅ Successfully imported 'BinanceTestnet' class")
    from trading_bot.data_manager import DataManager
    print("✅ Successfully imported 'DataManager' class")
    from trading_bot.strategy_executor import StrategyExecutor
    print("✅ Successfully imported 'StrategyExecutor' class")
    from trading_bot.config.settings import SETTINGS
    print("✅ Successfully imported 'SETTINGS'")
except ImportError as e:
    print(f"❌ Failed to import classes: {e}")

print("\nIf you see any import errors above, you need to fix your project structure.")
print("If all imports succeeded, you should be able to run the tests.")
print("\nTo run the tests, use:")
print("python -m unittest discover -v tests") 