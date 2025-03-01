#!/usr/bin/env python
"""Setup script for the trading_bot package."""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        # Metadata and dependencies are specified in pyproject.toml
        # This file exists for backward compatibility
        packages=find_packages(),
        package_data={"trading_bot": ["py.typed"]},
    ) 