"""
Setup Check Utility

This script checks the Trading Bot setup to ensure all required components
are properly installed and configured.
"""
import importlib
import logging
import os
import sys
from pathlib import Path
import platform
import subprocess
import warnings

logger = logging.getLogger('trading_bot.utils.check_setup')

def check_python_version():
    """Check if the Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version >= required_version:
        logger.info(f"Python version check: OK (v{sys.version.split()[0]})")
        return True
    else:
        logger.error(f"Python version check: FAILED - "
                     f"Required: {'.'.join(map(str, required_version))}+, "
                     f"Current: {'.'.join(map(str, current_version[:3]))}")
        return False

def check_required_packages():
    """Check if all required packages are installed."""
    required_packages = [
        'pandas',
        'numpy',
        'ccxt',
        'pyyaml',
        'python-dotenv',
        'requests'
    ]
    
    optional_packages = [
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'tensorflow',
        'sqlalchemy',
        'fastapi',
        'ta-lib',
        'ta'
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"Required package check: {package} - OK")
        except ImportError:
            missing_required.append(package)
            logger.error(f"Required package check: {package} - MISSING")
    
    # Check optional packages
    for package in optional_packages:
        try:
            importlib.import_module(package)
            logger.info(f"Optional package check: {package} - OK")
        except ImportError:
            missing_optional.append(package)
            logger.warning(f"Optional package check: {package} - MISSING")
    
    # Special handling for TA-Lib which is particularly problematic
    if 'ta-lib' in missing_optional:
        talib_instructions = {
            'Darwin': "Install with: brew install ta-lib && pip install ta-lib",
            'Linux': "Install with your package manager, e.g., apt-get install ta-lib, then: pip install ta-lib",
            'Windows': "Download from http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip, extract, and install with pip"
        }
        
        os_name = platform.system()
        if os_name in talib_instructions:
            logger.warning(f"TA-Lib installation instructions for {os_name}: {talib_instructions[os_name]}")
        
        # Check if fallback is available
        if 'ta' not in missing_optional:
            logger.info("The 'ta' package is available as a fallback for TA-Lib functionality")
    
    # Report status
    if missing_required:
        logger.error(f"Missing required packages: {', '.join(missing_required)}")
        logger.error("Install them with: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        logger.warning(f"Missing optional packages: {', '.join(missing_optional)}")
        logger.warning("Install them with: pip install " + " ".join(missing_optional))
    
    if not missing_required:
        logger.info("All required packages are installed")
        return True

def check_directories():
    """Check if all required directories exist and are writable."""
    required_dirs = [
        'data',
        'data/historical',
        'data/live',
        'logs',
        'results'
    ]
    
    base_dir = Path.cwd()
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            except Exception as e:
                missing_dirs.append(dir_name)
                logger.error(f"Failed to create directory {dir_path}: {e}")
        elif not os.access(dir_path, os.W_OK):
            logger.error(f"Directory exists but is not writable: {dir_path}")
            missing_dirs.append(dir_name)
        else:
            logger.info(f"Directory check: {dir_name} - OK")
    
    if missing_dirs:
        logger.error(f"Issues with required directories: {', '.join(missing_dirs)}")
        return False
    
    logger.info("All required directories are available")
    return True

def check_config_file():
    """Check if the configuration file exists."""
    config_files = ['config.yaml', 'config.yml', 'config.json']
    base_dir = Path.cwd()
    
    for config_file in config_files:
        config_path = base_dir / config_file
        if config_path.exists():
            logger.info(f"Configuration file found: {config_path}")
            return True
    
    example_path = base_dir / 'config.yaml.example'
    if example_path.exists():
        logger.warning("Configuration file not found, but example exists.")
        logger.warning("Create a configuration file by copying the example:")
        logger.warning("cp config.yaml.example config.yaml")
    else:
        logger.error("Configuration file not found and no example exists")
        logger.error("Create config.yaml based on the documentation")
    
    return False

def check_exchange_connection(exchange_name='binance', test_mode=True):
    """Test connection to the exchange API."""
    try:
        import ccxt
        
        if exchange_name not in ccxt.exchanges:
            logger.error(f"Exchange {exchange_name} is not supported by CCXT")
            return False
        
        # Create exchange instance
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'} if test_mode else {},
        })
        
        if test_mode:
            exchange.set_sandbox_mode(True)
            logger.info(f"Testing connection to {exchange_name} testnet...")
        else:
            logger.info(f"Testing connection to {exchange_name}...")
        
        # Test connection by fetching ticker
        ticker = exchange.fetch_ticker('BTC/USDT')
        
        if ticker and 'last' in ticker:
            logger.info(f"Exchange connection test: OK - Current BTC price: {ticker['last']}")
            return True
        else:
            logger.error("Exchange connection test: FAILED - Unexpected response format")
            return False
            
    except ImportError:
        logger.error("CCXT library is not installed. Cannot check exchange connection.")
        return False
    except Exception as e:
        logger.error(f"Exchange connection test: FAILED - {str(e)}")
        return False

def check_system_resources():
    """Check system resources like available memory and disk space."""
    import psutil
    
    # Check memory
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024 ** 3)
    
    logger.info(f"System memory: {memory_gb:.2f} GB total, {memory.percent}% used")
    
    if memory_gb < 4:
        logger.warning("Low system memory (<4GB). May impact performance.")
    
    # Check disk space
    disk = psutil.disk_usage('.')
    disk_gb = disk.total / (1024 ** 3)
    
    logger.info(f"Disk space: {disk_gb:.2f} GB total, {disk.percent}% used")
    
    if disk.free < 5 * (1024 ** 3):  # 5 GB
        logger.warning("Low disk space (<5GB free). May impact data storage.")
    
    return True

def run_all_checks():
    """Run all setup checks and return overall status."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/setup_check.log', mode='w')
        ]
    )
    
    logger.info("Starting Trading Bot setup checks...")
    
    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore')
    
    # Run all checks
    checks = [
        ("Python version", check_python_version),
        ("Required packages", check_required_packages),
        ("Directories", check_directories),
        ("Configuration file", check_config_file)
    ]
    
    # Optional checks
    try:
        import psutil
        checks.append(("System resources", check_system_resources))
    except ImportError:
        logger.warning("psutil not installed - skipping system resource check")
    
    try:
        import ccxt
        checks.append(("Exchange connection", lambda: check_exchange_connection('binance', True)))
    except ImportError:
        logger.warning("CCXT not installed - skipping exchange connection test")
    
    # Run checks and collect results
    results = []
    for name, check_func in checks:
        logger.info(f"\n--- Checking {name} ---")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Error during {name} check: {str(e)}")
            results.append((name, False))
    
    # Report summary
    logger.info("\n\n=== Setup Check Summary ===")
    all_passed = True
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{name}: {status}")
        all_passed = all_passed and result
    
    if all_passed:
        logger.info("\nAll checks PASSED! The Trading Bot should be ready to use.")
    else:
        logger.warning("\nSome checks FAILED. Please address the issues above before running the bot.")
    
    return all_passed

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    success = run_all_checks()
    sys.exit(0 if success else 1) 