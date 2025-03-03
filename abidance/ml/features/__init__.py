"""
Feature engineering module for machine learning models.

This package provides tools for generating features from raw data
for use in machine learning models, particularly for financial time series.
"""

from abidance.ml.features.base import FeatureGenerator
from abidance.ml.features.technical import TechnicalFeatureGenerator

__all__ = [
    'FeatureGenerator',
    'TechnicalFeatureGenerator',
]
