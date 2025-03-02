import pytest


class TestPackageAPI:
    """Test the public API of the abidance package."""
    
    def test_main_package_exports(self):
        """Test that the main package exports the expected objects."""
        try:
            import abidance
            # Check for version information
            assert hasattr(abidance, "__version__"), "Package should export __version__"
            assert isinstance(abidance.__version__, str), "__version__ should be a string"
            
            # Check for key modules
            assert hasattr(abidance, "trading"), "Package should export trading module"
            assert hasattr(abidance, "exchange"), "Package should export exchange module"
            assert hasattr(abidance, "strategy"), "Package should export strategy module"
            assert hasattr(abidance, "data"), "Package should export data module"
        except ImportError as e:
            pytest.fail(f"Failed to import abidance package: {e}")
    
    def test_trading_module_exports(self):
        """Test that the trading module exports expected classes and functions."""
        try:
            from abidance import trading
            
            # Key classes that should be exported
            expected_exports = [
                "Order", 
                "Trade", 
                "Position",
                "TradingEngine"
            ]
            
            for export in expected_exports:
                assert hasattr(trading, export), f"trading module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import trading module: {e}")
    
    def test_exchange_module_exports(self):
        """Test that the exchange module exports expected classes and functions."""
        try:
            from abidance import exchange
            
            # Key classes that should be exported
            expected_exports = [
                "Exchange",
                "ExchangeManager",
                "BinanceExchange"
            ]
            
            for export in expected_exports:
                assert hasattr(exchange, export), f"exchange module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import exchange module: {e}")
    
    def test_strategy_module_exports(self):
        """Test that the strategy module exports expected classes and functions."""
        try:
            from abidance import strategy
            
            # Key classes that should be exported
            expected_exports = [
                "Strategy",
                "StrategyRegistry",
                "SMAStrategy",
                "RSIStrategy"
            ]
            
            for export in expected_exports:
                assert hasattr(strategy, export), f"strategy module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import strategy module: {e}")
    
    def test_data_module_exports(self):
        """Test that the data module exports expected classes and functions."""
        try:
            from abidance import data
            
            # Key classes that should be exported
            expected_exports = [
                "DataManager",
                "OHLCVRepository",
                "TradeRepository",
                "StrategyRepository"
            ]
            
            for export in expected_exports:
                assert hasattr(data, export), f"data module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import data module: {e}")
    
    def test_exceptions_module_exports(self):
        """Test that the exceptions module exports expected exception classes."""
        try:
            from abidance import exceptions
            
            # Key exception classes that should be exported
            expected_exports = [
                "AbidanceError",
                "ExchangeError",
                "StrategyError",
                "DataError",
                "ConfigurationError"
            ]
            
            for export in expected_exports:
                assert hasattr(exceptions, export), f"exceptions module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import exceptions module: {e}")
    
    def test_core_module_exports(self):
        """Test that the core module exports expected classes and functions."""
        try:
            from abidance import core
            
            # Key classes that should be exported
            expected_exports = [
                "ConfigManager",
                "Logger",
                "EventSystem"
            ]
            
            for export in expected_exports:
                assert hasattr(core, export), f"core module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import core module: {e}")
    
    def test_utils_module_exports(self):
        """Test that the utils module exports expected utility functions."""
        try:
            from abidance import utils
            
            # Key utility functions that should be exported
            expected_exports = [
                "format_timestamp",
                "calculate_roi",
                "validate_dataframe"
            ]
            
            for export in expected_exports:
                assert hasattr(utils, export), f"utils module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import utils module: {e}")
            
    def test_ml_module_exports(self):
        """Test that the ml module exports expected classes and functions."""
        try:
            from abidance import ml
            
            # Key classes that should be exported
            expected_exports = [
                "FeatureEngineering",
                "ModelRegistry",
                "PredictionService"
            ]
            
            for export in expected_exports:
                assert hasattr(ml, export), f"ml module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import ml module: {e}")
            
    def test_api_module_exports(self):
        """Test that the api module exports expected classes and functions."""
        try:
            from abidance import api
            
            # Key classes that should be exported
            expected_exports = [
                "APIServer",
                "WebSocketServer"
            ]
            
            for export in expected_exports:
                assert hasattr(api, export), f"api module should export {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import api module: {e}") 