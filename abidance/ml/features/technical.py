"""
Technical feature generators for financial time series data.

This module provides feature generators that create technical indicators
from financial time series data, particularly OHLCV (Open, High, Low, Close, Volume) data.
"""
from typing import List

import pandas as pd
from abidance.ml.features.base import FeatureGenerator


class TechnicalFeatureGenerator(FeatureGenerator):
    """
    Generator for technical analysis features.

    This class generates common technical indicators used in financial analysis,
    such as moving averages, volatility measures, momentum indicators, and price patterns.

    Attributes:
        windows: List of window sizes for rolling calculations
    """

    def __init__(self, windows: List[int] = None):
        """
        Initialize the technical feature generator.

        Args:
            windows: List of window sizes for rolling calculations.
                     Defaults to [5, 10, 20, 50] if None.
        """
        self.windows = windows if windows is not None else [5, 10, 20, 50]

    def generate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate technical indicators as features.

        Args:
            data: DataFrame containing OHLCV data with columns:
                 'open', 'high', 'low', 'close', 'volume'

        Returns:
            DataFrame containing generated technical features
        """
        features = pd.DataFrame(index=data.index)

        # Price-based features
        for window in self.windows:
            # Moving averages
            features[f'sma_{window}'] = data['close'].rolling(window).mean()
            features[f'ema_{window}'] = data['close'].ewm(span=window).mean()

            # Volatility
            features[f'std_{window}'] = data['close'].rolling(window).std()

            # Momentum - use fill_method=None to avoid FutureWarning
            features[f'roc_{window}'] = data['close'].pct_change(window, fill_method=None)

            # Volume features
            features[f'volume_sma_{window}'] = data['volume'].rolling(window).mean()

        # Price patterns
        features['upper_shadow'] = data['high'] - data[['open', 'close']].max(axis=1)
        features['lower_shadow'] = data[['open', 'close']].min(axis=1) - data['low']
        features['body_size'] = (data['close'] - data['open']).abs()

        # Fill NaN values with 0
        return features.fillna(0)

    @property
    def feature_names(self) -> List[str]:
        """
        Get list of generated feature names.

        Returns:
            List of feature names that this generator produces
        """
        names = []
        for window in self.windows:
            names.extend([
                f'sma_{window}',
                f'ema_{window}',
                f'std_{window}',
                f'roc_{window}',
                f'volume_sma_{window}'
            ])
        names.extend(['upper_shadow', 'lower_shadow', 'body_size'])
        return names
