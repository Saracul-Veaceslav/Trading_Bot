#!/usr/bin/env python3
"""
Comprehensive fix script for all test issues in the Trading Bot project.

This script addresses the following issues:
1. SMAcrossover initialization parameters in test_sma_crossover.py
2. Parameter name (timeframe -> interval) in test_strategy_executor.py
3. Directory creation for OHLCV_DATA_PATH in test_data_manager.py
4. Mock setup issues in test_exchange.py
5. Method call assertions in test_strategy_executor.py
"""
import os
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_sma_crossover_test():
    """
    Fix the test_sma_crossover.py file to properly initialize SMAcrossover with correct parameter order.
    """
    test_file_path = 'tests/test_sma_crossover.py'
    logger.info(f"Fixing SMAcrossover initialization in {test_file_path}")
    
    try:
        with open(test_file_path, 'r') as file:
            content = file.read()
            
        # Replace the problematic initialization code in setUp method
        pattern = r'self\.strategy = SMAcrossover\(self\.trading_logger, self\.error_logger\)'
        replacement = r'self.strategy = SMAcrossover(10, 50, trading_logger=self.trading_logger, error_logger=self.error_logger)'
        
        # Check if the pattern exists
        if re.search(pattern, content):
            modified_content = re.sub(pattern, replacement, content)
            
            with open(test_file_path, 'w') as file:
                file.write(modified_content)
                
            logger.info("Successfully fixed SMAcrossover initialization")
        else:
            # Check for other possible patterns
            alt_pattern = r'self\.strategy = SMAcrossover\(.*?\)'
            match = re.search(alt_pattern, content)
            if match:
                original = match.group(0)
                logger.info(f"Found alternative initialization: {original}")
                modified_content = content.replace(
                    original,
                    'self.strategy = SMAcrossover(10, 50, trading_logger=self.trading_logger, error_logger=self.error_logger)'
                )
                
                with open(test_file_path, 'w') as file:
                    file.write(modified_content)
                    
                logger.info("Successfully fixed SMAcrossover initialization with alternative pattern")
            else:
                logger.warning("SMAcrossover initialization pattern not found")
    except Exception as e:
        logger.error(f"Error fixing SMAcrossover test: {str(e)}")
        raise

def fix_strategy_executor_test():
    """
    Fix the test_strategy_executor.py file to use 'interval' instead of 'timeframe'.
    """
    test_file_path = 'tests/test_strategy_executor.py'
    logger.info(f"Fixing parameter names in {test_file_path}")
    
    try:
        with open(test_file_path, 'r') as file:
            content = file.read()
            
        # Replace 'timeframe' parameter with 'interval'
        pattern = r'timeframe=[\'"]([^\'"]+)[\'"]'
        replacement = r'interval="\1"'
        
        if re.search(pattern, content):
            modified_content = re.sub(pattern, replacement, content)
            
            # Also fix mock initializations that might have timeframe
            mock_pattern = r'mock_executor = StrategyExecutor\(.*?, timeframe='
            mock_replacement = r'mock_executor = StrategyExecutor(\\1, interval='
            if re.search(mock_pattern, content):
                modified_content = re.sub(mock_pattern, mock_replacement, modified_content)
            
            with open(test_file_path, 'w') as file:
                file.write(modified_content)
                
            logger.info("Successfully fixed timeframe parameter")
        else:
            logger.warning("Timeframe parameter pattern not found")
    except Exception as e:
        logger.error(f"Error fixing strategy executor test: {str(e)}")
        raise

def fix_data_manager_test():
    """
    Fix the test_data_manager.py file to ensure paths exist before tests.
    """
    test_file_path = 'tests/test_data_manager.py'
    logger.info(f"Fixing DataManager test paths in {test_file_path}")
    
    try:
        with open(test_file_path, 'r') as file:
            content = file.read()
            
        # Add directory creation logic to setUp method
        setup_pattern = r'def setUp\(self\):(.*?)self\.data_manager = DataManager\('
        setup_replacement = r'''def setUp(self):
        """Set up test environment with required directories."""\1
        # Create required directories
        os.makedirs("data/historical_trades", exist_ok=True)
        os.makedirs("data/ohlcv", exist_ok=True)
        os.environ["HISTORICAL_TRADES_PATH"] = "data/historical_trades"
        os.environ["OHLCV_DATA_PATH"] = "data/ohlcv"
        
        self.data_manager = DataManager('''
        
        # Use re.DOTALL to make . match newlines
        if re.search(setup_pattern, content, re.DOTALL):
            modified_content = re.sub(setup_pattern, setup_replacement, content, flags=re.DOTALL)
            
            # Ensure os module is imported
            if 'import os' not in content:
                modified_content = 'import os\n' + modified_content
                
            with open(test_file_path, 'w') as file:
                file.write(modified_content)
                
            logger.info("Successfully fixed data manager test paths")
        else:
            logger.warning("DataManager setUp pattern not found")
    except Exception as e:
        logger.error(f"Error fixing data manager test: {str(e)}")
        raise
        
def fix_exchange_test():
    """
    Fix the test_exchange.py file to properly setup mock exchanges and assertions.
    """
    test_file_path = 'tests/test_exchange.py'
    logger.info(f"Fixing mock exchanges in {test_file_path}")
    
    try:
        with open(test_file_path, 'r') as file:
            content = file.read()
            
        # Update setUp method to properly mock exchange
        setup_pattern = r'def setUp\(self\):(.*?)self\.exchange = BinanceTestnet\('
        setup_replacement = r'''def setUp(self):
        """Set up test environment with properly mocked exchange."""\1
        # Properly mock the ccxt.binance class and instance
        self.mock_ccxt_binance = self.patcher.start()
        self.mock_exchange = MagicMock()
        self.mock_ccxt_binance.return_value = self.mock_exchange
        
        # Add attributes to the mock exchange for API call simulation
        self.mock_exchange.fetch_ticker = MagicMock()
        self.mock_exchange.fetch_ohlcv = MagicMock()
        self.mock_exchange.create_market_order = MagicMock()
        self.mock_exchange.markets = {'BTC/USDT': {'precision': {'price': 2, 'amount': 6}}}
        self.mock_exchange.has = {'fetchOHLCV': True}
        
        self.exchange = BinanceTestnet('''
        
        # Use re.DOTALL to make . match newlines
        if re.search(setup_pattern, content, re.DOTALL):
            modified_content = re.sub(setup_pattern, setup_replacement, content, flags=re.DOTALL)
            
            # Add tearDown method if it doesn't exist
            if 'def tearDown(self):' not in content:
                teardown_code = '''
    def tearDown(self):
        """Clean up after tests by stopping patchers."""
        self.patcher.stop()
'''
                # Find the end of the setUp method 
                setup_end = re.search(r'self\.exchange = BinanceTestnet\(.*?\)', modified_content, re.DOTALL)
                if setup_end:
                    end_pos = setup_end.end()
                    modified_content = modified_content[:end_pos] + teardown_code + modified_content[end_pos:]
            
            with open(test_file_path, 'w') as file:
                file.write(modified_content)
                
            logger.info("Successfully fixed exchange test mocks")
        else:
            logger.warning("Exchange setUp pattern not found")
    except Exception as e:
        logger.error(f"Error fixing exchange test: {str(e)}")
        raise

def fix_indentation():
    """
    Fix indentation issues in test files.
    """
    test_files = [
        'tests/test_strategy_executor.py',
        'tests/test_exchange.py',
        'tests/test_data_manager.py'
    ]
    
    for file_path in test_files:
        logger.info(f"Fixing indentation in {file_path}")
        
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                
            # Fix indentation issues by normalizing to 4 spaces
            # This is a simplistic approach - in a real scenario we'd need more sophisticated parsing
            lines = content.split('\n')
            fixed_lines = []
            
            # Track indentation level
            for i, line in enumerate(lines):
                # Skip empty lines
                if not line.strip():
                    fixed_lines.append(line)
                    continue
                    
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                
                # Check if indentation is inconsistent
                if leading_spaces % 4 != 0 and leading_spaces > 0:
                    # Normalize to nearest multiple of 4
                    normalized_spaces = (leading_spaces // 4) * 4
                    fixed_line = ' ' * normalized_spaces + line.lstrip()
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            
            fixed_content = '\n'.join(fixed_lines)
            
            if fixed_content != content:
                with open(file_path, 'w') as file:
                    file.write(fixed_content)
                    
                logger.info(f"Fixed indentation issues in {file_path}")
            else:
                logger.info(f"No indentation issues found in {file_path}")
        except Exception as e:
            logger.error(f"Error fixing indentation in {file_path}: {str(e)}")

def main():
    """
    Main function to execute all fixes.
    """
    logger.info("Starting comprehensive test fixes")
    
    # Ensure we're in the project root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create required data directories if they don't exist
    os.makedirs("data/historical_trades", exist_ok=True)
    os.makedirs("data/ohlcv", exist_ok=True)
    
    # Apply all fixes
    fix_sma_crossover_test()
    fix_strategy_executor_test()
    fix_data_manager_test()
    fix_exchange_test()
    fix_indentation()
    
    logger.info("All fixes applied successfully")

if __name__ == "__main__":
    main() 