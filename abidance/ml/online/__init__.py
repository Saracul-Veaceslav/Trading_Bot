"""
Online learning module for continuous model updating.

This module provides functionality for online learning, allowing models
to adapt to changing market conditions over time.
"""
from .learner import OnlineLearner
from .buffer import DataBuffer

__all__ = ['OnlineLearner', 'DataBuffer']
