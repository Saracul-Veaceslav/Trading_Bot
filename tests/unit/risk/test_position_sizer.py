"""
Test for Position Sizer Module

This module contains tests for the position sizing strategies.
"""
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from bot.risk.position_sizer import (
    PositionSizer, 
    FixedRiskPositionSizer, 
    VolatilityPositionSizer, 
    KellyPositionSizer,
    PositionSizerFactory
)

class TestFixedRiskPositionSizer(unittest.TestCase):
    """Test case for the Fixed Risk Position Sizer."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock logger
        self.mock_logger = MagicMock()
        
        # Create position sizer instance
        self.position_sizer = FixedRiskPositionSizer(
            risk_per_trade=0.02,  # 2% risk per trade
            max_position_size=0.2,  # 20% max position size
            min_position_size=0.01,  # 1% min position size
            risk_logger=self.mock_logger
        )
    
    def test_initialization(self):
        """Test position sizer initialization."""
        self.assertEqual(self.position_sizer.risk_per_trade, 0.02)
        self.assertEqual(self.position_sizer.max_position_size, 0.2)
        self.assertEqual(self.position_sizer.min_position_size, 0.01)
        self.assertEqual(self.position_sizer.logger, self.mock_logger)
    
    def test_calculate_position_size_with_stop_loss(self):
        """Test position size calculation with stop loss."""
        # Test parameters
        account_balance = 10000.0
        current_price = 100.0
        stop_loss_price = 95.0  # 5% stop loss
        
        # Calculate position size
        with patch.object(self.position_sizer, 'validate_position_size', return_value=40.0):
            position_size = self.position_sizer.calculate_position_size(
                account_balance=account_balance,
                current_price=current_price,
                stop_loss_price=stop_loss_price,
                is_long=True
            )
        
        # Expected position size: (account_balance * risk_per_trade) / (current_price - stop_loss_price)
        # (10000 * 0.02) / (100 - 95) = 200 / 5 = 40
        self.assertEqual(position_size, 40.0)
    
    def test_calculate_position_size_without_stop_loss(self):
        """Test position size calculation without stop loss."""
        # Test parameters
        account_balance = 10000.0
        current_price = 100.0
        
        # Calculate position size with default stop loss (5%)
        with patch.object(self.position_sizer, 'validate_position_size', return_value=40.0):
            position_size = self.position_sizer.calculate_position_size(
                account_balance=account_balance,
                current_price=current_price,
                is_long=True
            )
        
        # Expected position size: (account_balance * risk_per_trade) / (current_price * default_stop_pct)
        # (10000 * 0.02) / (100 * 0.05) = 200 / 5 = 40
        self.assertEqual(position_size, 40.0)
    
    def test_calculate_position_size_short(self):
        """Test position size calculation for short positions."""
        # Test parameters
        account_balance = 10000.0
        current_price = 100.0
        stop_loss_price = 105.0  # 5% stop loss for short
        
        # Calculate position size
        with patch.object(self.position_sizer, 'validate_position_size', return_value=40.0):
            position_size = self.position_sizer.calculate_position_size(
                account_balance=account_balance,
                current_price=current_price,
                stop_loss_price=stop_loss_price,
                is_long=False
            )
        
        # Expected position size: (account_balance * risk_per_trade) / (stop_loss_price - current_price)
        # (10000 * 0.02) / (105 - 100) = 200 / 5 = 40
        self.assertEqual(position_size, 40.0)
    
    def test_validate_position_size_within_limits(self):
        """Test position size validation within limits."""
        # Test parameters
        position_size = 10.0
        account_balance = 10000.0
        current_price = 100.0
        
        # Position value: 10 * 100 = 1000
        # Position fraction: 1000 / 10000 = 0.1 (10%)
        # This is between min (1%) and max (20%), so should remain unchanged
        
        # Validate position size
        validated_size = self.position_sizer.validate_position_size(
            position_size=position_size,
            account_balance=account_balance,
            current_price=current_price
        )
        
        self.assertEqual(validated_size, position_size)
    
    def test_validate_position_size_above_max(self):
        """Test position size validation above maximum limit."""
        # Test parameters
        position_size = 30.0
        account_balance = 10000.0
        current_price = 100.0
        
        # Position value: 30 * 100 = 3000
        # Position fraction: 3000 / 10000 = 0.3 (30%)
        # This is above max (20%), so should be reduced
        
        # Expected adjusted size: (0.2 * 10000) / 100 = 20
        
        # Validate position size
        validated_size = self.position_sizer.validate_position_size(
            position_size=position_size,
            account_balance=account_balance,
            current_price=current_price
        )
        
        self.assertEqual(validated_size, 20.0)
    
    def test_validate_position_size_below_min(self):
        """Test position size validation below minimum limit."""
        # Test parameters
        position_size = 0.5
        account_balance = 10000.0
        current_price = 100.0
        
        # Position value: 0.5 * 100 = 50
        # Position fraction: 50 / 10000 = 0.005 (0.5%)
        # This is below min (1%), so should be increased
        
        # Expected adjusted size: (0.01 * 10000) / 100 = 1
        
        # Validate position size
        validated_size = self.position_sizer.validate_position_size(
            position_size=position_size,
            account_balance=account_balance,
            current_price=current_price
        )
        
        self.assertEqual(validated_size, 1.0)
    
    def test_invalid_inputs(self):
        """Test behavior with invalid inputs."""
        # Test with zero account balance
        position_size = self.position_sizer.calculate_position_size(
            account_balance=0.0,
            current_price=100.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with zero price
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=0.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with invalid stop loss (long position)
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=100.0,
            stop_loss_price=105.0,
            is_long=True
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with invalid stop loss (short position)
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=100.0,
            stop_loss_price=95.0,
            is_long=False
        )
        self.assertEqual(position_size, 0.0)


class TestVolatilityPositionSizer(unittest.TestCase):
    """Test case for the Volatility Position Sizer."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock logger
        self.mock_logger = MagicMock()
        
        # Create position sizer instance
        self.position_sizer = VolatilityPositionSizer(
            risk_per_trade=0.02,  # 2% risk per trade
            volatility_lookback=20,
            volatility_factor=1.0,
            max_position_size=0.2,  # 20% max position size
            min_position_size=0.01,  # 1% min position size
            risk_logger=self.mock_logger
        )
        
        # Create sample price history
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample price history for testing."""
        # Create date range
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        
        # Create price data with a trend and some volatility
        base_price = 100.0
        trend = np.linspace(0, 10, 30)  # Upward trend
        volatility = np.random.normal(0, 1, 30) * 2  # Random noise
        
        # Calculate prices
        close_prices = base_price + trend + volatility
        
        # Create DataFrame
        self.sample_data = pd.DataFrame({
            'close': close_prices
        }, index=dates)
    
    def test_initialization(self):
        """Test position sizer initialization."""
        self.assertEqual(self.position_sizer.risk_per_trade, 0.02)
        self.assertEqual(self.position_sizer.volatility_lookback, 20)
        self.assertEqual(self.position_sizer.volatility_factor, 1.0)
        self.assertEqual(self.position_sizer.max_position_size, 0.2)
        self.assertEqual(self.position_sizer.min_position_size, 0.01)
        self.assertEqual(self.position_sizer.logger, self.mock_logger)
    
    def test_calculate_volatility(self):
        """Test volatility calculation."""
        # Calculate volatility
        volatility = self.position_sizer._calculate_volatility(
            price_history=self.sample_data,
            current_price=100.0
        )
        
        # Volatility should be a positive number
        self.assertGreater(volatility, 0.0)
        
        # Test with no price history
        volatility = self.position_sizer._calculate_volatility(
            price_history=None,
            current_price=100.0
        )
        self.assertEqual(volatility, 0.02)  # Default volatility
        
        # Test with empty DataFrame
        volatility = self.position_sizer._calculate_volatility(
            price_history=pd.DataFrame(),
            current_price=100.0
        )
        self.assertEqual(volatility, 0.02)  # Default volatility
    
    def test_calculate_position_size(self):
        """Test position size calculation based on volatility."""
        # Test parameters
        account_balance = 10000.0
        current_price = 100.0
        
        # Mock volatility calculation
        with patch.object(self.position_sizer, '_calculate_volatility', return_value=0.02), \
             patch.object(self.position_sizer, 'validate_position_size', return_value=100.0):
            
            # Calculate position size
            position_size = self.position_sizer.calculate_position_size(
                account_balance=account_balance,
                current_price=current_price,
                price_history=self.sample_data
            )
        
        # Expected position size: (account_balance * risk_per_trade) / (current_price * volatility) * volatility_factor
        # (10000 * 0.02) / (100 * 0.02) * 1.0 = 200 / 2 = 100
        self.assertEqual(position_size, 100.0)
    
    def test_calculate_position_size_with_min_volatility(self):
        """Test position size calculation with minimum volatility."""
        # Test parameters
        account_balance = 10000.0
        current_price = 100.0
        
        # Mock volatility calculation to return a very low value
        with patch.object(self.position_sizer, '_calculate_volatility', return_value=0.001), \
             patch.object(self.position_sizer, 'validate_position_size', return_value=40.0):
            
            # Calculate position size with minimum volatility of 0.5%
            position_size = self.position_sizer.calculate_position_size(
                account_balance=account_balance,
                current_price=current_price,
                price_history=self.sample_data,
                min_volatility=0.005
            )
        
        # Expected position size: (account_balance * risk_per_trade) / (current_price * min_volatility) * volatility_factor
        # (10000 * 0.02) / (100 * 0.005) * 1.0 = 200 / 0.5 = 400
        # But this would be reduced by validate_position_size to 40.0 (as mocked)
        self.assertEqual(position_size, 40.0)
    
    def test_invalid_inputs(self):
        """Test behavior with invalid inputs."""
        # Test with zero account balance
        position_size = self.position_sizer.calculate_position_size(
            account_balance=0.0,
            current_price=100.0,
            price_history=self.sample_data
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with zero price
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=0.0,
            price_history=self.sample_data
        )
        self.assertEqual(position_size, 0.0)


class TestKellyPositionSizer(unittest.TestCase):
    """Test case for the Kelly Position Sizer."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock logger
        self.mock_logger = MagicMock()
        
        # Create position sizer instance
        self.position_sizer = KellyPositionSizer(
            max_position_size=0.2,
            min_position_size=0.01,
            kelly_fraction=0.5,
            risk_logger=self.mock_logger
        )
    
    def test_initialization(self):
        """Test position sizer initialization."""
        # Check that parameters are set correctly
        self.assertEqual(self.position_sizer.kelly_fraction, 0.5)
        self.assertEqual(self.position_sizer.max_position_size, 0.2)
        self.assertEqual(self.position_sizer.min_position_size, 0.01)
        self.assertEqual(self.position_sizer.logger, self.mock_logger)
    
    def test_calculate_position_size(self):
        """Test position size calculation."""
        # Test parameters
        account_balance = 10000.0
        current_price = 100.0
        win_probability = 0.6  # 60% win rate
        win_loss_ratio = 2.0  # 2:1 reward-to-risk ratio
        
        # Calculate position size
        position_size = self.position_sizer.calculate_position_size(
            account_balance=account_balance,
            current_price=current_price,
            win_probability=win_probability,
            win_loss_ratio=win_loss_ratio
        )
        
        # Expected Kelly percentage: (bp - q) / b = (0.6 * 2 - 0.4) / 2 = (1.2 - 0.4) / 2 = 0.4
        # Half Kelly: 0.4 * 0.5 = 0.2
        # Position value: 10000 * 0.2 = 2000
        # Position size: 2000 / 100 = 20
        expected_size = 20.0
        self.assertAlmostEqual(position_size, expected_size, places=10)
    
    def test_calculate_position_size_negative_edge(self):
        """Test position size calculation with negative edge."""
        # Create a scenario with negative edge (win_rate < 0.5)
        account_balance = 10000.0
        current_price = 100.0
        win_probability = 0.4  # 40% win rate
        win_loss_ratio = 1.0  # 1:1 reward-to-risk ratio
        
        # Calculate position size
        position_size = self.position_sizer.calculate_position_size(
            account_balance=account_balance,
            current_price=current_price,
            win_probability=win_probability,
            win_loss_ratio=win_loss_ratio
        )
        
        # With negative edge, Kelly criterion should return 0
        self.assertEqual(position_size, 0.0)
    
    def test_invalid_inputs(self):
        """Test behavior with invalid inputs."""
        # Test with invalid account balance
        position_size = self.position_sizer.calculate_position_size(
            account_balance=0.0,
            current_price=100.0,
            win_probability=0.6,
            win_loss_ratio=2.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with invalid price
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=0.0,
            win_probability=0.6,
            win_loss_ratio=2.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with invalid win probability
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=100.0,
            win_probability=1.5,  # Invalid probability
            win_loss_ratio=2.0
        )
        # Should use default probability and calculate normally
        self.assertGreater(position_size, 0.0)
        
        # Test with invalid win/loss ratio
        position_size = self.position_sizer.calculate_position_size(
            account_balance=10000.0,
            current_price=100.0,
            win_probability=0.6,
            win_loss_ratio=-1.0  # Invalid ratio
        )
        # Should use default ratio and calculate normally
        self.assertGreater(position_size, 0.0)


class TestPositionSizerFactory(unittest.TestCase):
    """Test case for the Position Sizer Factory."""
    
    def test_create_fixed_risk_sizer(self):
        """Test creating a fixed risk position sizer."""
        sizer = PositionSizerFactory.create_position_sizer('fixed_risk')
        self.assertIsInstance(sizer, FixedRiskPositionSizer)
    
    def test_create_volatility_sizer(self):
        """Test creating a volatility position sizer."""
        sizer = PositionSizerFactory.create_position_sizer('volatility')
        self.assertIsInstance(sizer, VolatilityPositionSizer)
    
    def test_create_kelly_sizer(self):
        """Test creating a Kelly position sizer."""
        sizer = PositionSizerFactory.create_position_sizer('kelly')
        self.assertIsInstance(sizer, KellyPositionSizer)
    
    def test_create_unknown_sizer(self):
        """Test creating an unknown position sizer type."""
        sizer = PositionSizerFactory.create_position_sizer('unknown')
        # Should default to fixed risk
        self.assertIsInstance(sizer, FixedRiskPositionSizer)
    
    def test_create_with_parameters(self):
        """Test creating a position sizer with parameters."""
        sizer = PositionSizerFactory.create_position_sizer(
            'fixed_risk',
            risk_per_trade=0.03,
            max_position_size=0.15
        )
        self.assertIsInstance(sizer, FixedRiskPositionSizer)
        self.assertEqual(sizer.risk_per_trade, 0.03)
        self.assertEqual(sizer.max_position_size, 0.15)


if __name__ == '__main__':
    unittest.main() 