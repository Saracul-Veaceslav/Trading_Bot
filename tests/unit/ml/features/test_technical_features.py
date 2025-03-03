import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal, assert_series_equal

# Import the modules to be tested
# These imports will fail until we create the actual modules
from abidance.ml.features.base import FeatureGenerator
from abidance.ml.features.technical import TechnicalFeatureGenerator


class TestTechnicalFeatureGenerator:
    """Test suite for TechnicalFeatureGenerator."""

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data for testing."""
        # Create a DataFrame with 100 rows of sample data
        np.random.seed(42)  # For reproducibility
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        
        # Generate random but somewhat realistic OHLCV data
        close_values = 100 + np.cumsum(np.random.normal(0, 1, 100))
        close = pd.Series(close_values, index=dates)
        
        data = pd.DataFrame({
            'open': close.shift(1).fillna(100) + np.random.normal(0, 0.5, 100),
            'high': close + np.abs(np.random.normal(0, 1, 100)),
            'low': close - np.abs(np.random.normal(0, 1, 100)),
            'close': close,
            'volume': np.abs(np.random.normal(1000, 200, 100))
        }, index=dates)
        
        # Ensure high is always >= open, close, low and low is always <= open, close
        data['high'] = data[['high', 'open', 'close']].max(axis=1)
        data['low'] = data[['low', 'open', 'close']].min(axis=1)
        
        return data

    def test_feature_generator_is_abstract(self):
        """Test that FeatureGenerator is an abstract base class."""
        with pytest.raises(TypeError):
            FeatureGenerator()

    def test_technical_feature_generator_initialization(self):
        """Test initialization of TechnicalFeatureGenerator."""
        # Test with default windows
        generator = TechnicalFeatureGenerator()
        assert generator.windows == [5, 10, 20, 50]
        
        # Test with custom windows
        custom_windows = [3, 7, 14]
        generator = TechnicalFeatureGenerator(windows=custom_windows)
        assert generator.windows == custom_windows

    def test_feature_names_consistency(self, sample_ohlcv_data):
        """Test that feature names match the generated features."""
        generator = TechnicalFeatureGenerator(windows=[5, 10])
        features = generator.generate(sample_ohlcv_data)
        
        # Check that all expected feature names are in the generated DataFrame
        for name in generator.feature_names:
            assert name in features.columns
        
        # Check that the number of features matches the expected count
        expected_count = len(generator.windows) * 5 + 3  # 5 features per window + 3 price pattern features
        assert len(features.columns) == expected_count

    def test_feature_generation(self, sample_ohlcv_data):
        """Test that features are correctly generated."""
        generator = TechnicalFeatureGenerator(windows=[5])
        features = generator.generate(sample_ohlcv_data)
        
        # Test SMA calculation
        expected_sma = sample_ohlcv_data['close'].rolling(5).mean()
        assert_series_equal(features['sma_5'], expected_sma.fillna(0), check_names=False)
        
        # Test EMA calculation
        expected_ema = sample_ohlcv_data['close'].ewm(span=5).mean()
        assert_series_equal(features['ema_5'], expected_ema.fillna(0), check_names=False)
        
        # Test STD calculation
        expected_std = sample_ohlcv_data['close'].rolling(5).std()
        assert_series_equal(features['std_5'], expected_std.fillna(0), check_names=False)
        
        # Test ROC calculation
        expected_roc = sample_ohlcv_data['close'].pct_change(5)
        assert_series_equal(features['roc_5'], expected_roc.fillna(0), check_names=False)
        
        # Test Volume SMA calculation
        expected_vol_sma = sample_ohlcv_data['volume'].rolling(5).mean()
        assert_series_equal(features['volume_sma_5'], expected_vol_sma.fillna(0), check_names=False)
        
        # Test price pattern features
        expected_upper_shadow = sample_ohlcv_data['high'] - sample_ohlcv_data[['open', 'close']].max(axis=1)
        assert_series_equal(features['upper_shadow'], expected_upper_shadow, check_names=False)
        
        expected_lower_shadow = sample_ohlcv_data[['open', 'close']].min(axis=1) - sample_ohlcv_data['low']
        assert_series_equal(features['lower_shadow'], expected_lower_shadow, check_names=False)
        
        expected_body_size = (sample_ohlcv_data['close'] - sample_ohlcv_data['open']).abs()
        assert_series_equal(features['body_size'], expected_body_size, check_names=False)

    def test_handling_missing_data(self):
        """Test handling of missing data in feature generation."""
        # Create data with missing values
        data = pd.DataFrame({
            'open': [100, 101, np.nan, 103, 104],
            'high': [105, 106, np.nan, 108, 109],
            'low': [95, 96, np.nan, 98, 99],
            'close': [102, 103, np.nan, 105, 106],
            'volume': [1000, 1100, np.nan, 1300, 1400]
        })
        
        generator = TechnicalFeatureGenerator(windows=[2])
        features = generator.generate(data)
        
        # Check that NaN values are filled with 0
        assert not features.isna().any().any()
        
        # Check specific handling of NaN in calculations
        # For example, SMA with window=2 at index 3 should only consider index 2 (which is NaN) and 3
        # Since one value is NaN, the result before fillna would be NaN
        assert features.loc[3, 'sma_2'] == 0

    def test_feature_value_ranges(self, sample_ohlcv_data):
        """Test that feature values are within expected ranges."""
        generator = TechnicalFeatureGenerator()
        features = generator.generate(sample_ohlcv_data)
        
        # STD should be non-negative
        for window in generator.windows:
            assert (features[f'std_{window}'] >= 0).all()
        
        # Body size should be non-negative
        assert (features['body_size'] >= 0).all()
        
        # Upper and lower shadows should be non-negative
        assert (features['upper_shadow'] >= 0).all()
        assert (features['lower_shadow'] >= 0).all()

    def test_different_window_sizes(self, sample_ohlcv_data):
        """Test feature generation with different window sizes."""
        # Test with small windows
        small_windows = [2, 3]
        generator = TechnicalFeatureGenerator(windows=small_windows)
        features = generator.generate(sample_ohlcv_data)
        
        for window in small_windows:
            assert f'sma_{window}' in features.columns
            assert f'ema_{window}' in features.columns
            assert f'std_{window}' in features.columns
            assert f'roc_{window}' in features.columns
            assert f'volume_sma_{window}' in features.columns
        
        # Test with large windows
        large_windows = [50, 100]
        generator = TechnicalFeatureGenerator(windows=large_windows)
        features = generator.generate(sample_ohlcv_data)
        
        for window in large_windows:
            assert f'sma_{window}' in features.columns
            assert f'ema_{window}' in features.columns
            assert f'std_{window}' in features.columns
            assert f'roc_{window}' in features.columns
            assert f'volume_sma_{window}' in features.columns 