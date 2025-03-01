# Trading Bot Test Suite

This directory contains the test suite for the Trading Bot project. The tests are organized by module and type to ensure comprehensive coverage of the codebase.

## Directory Structure

```
Tests/
├── integration/           # Integration tests that verify multiple components working together
├── unit/                  # Unit tests for individual components
│   ├── config/            # Tests for configuration management
│   ├── core/              # Tests for core bot functionality
│   ├── data/              # Tests for data management
│   ├── exchanges/         # Tests for exchange integrations
│   ├── risk/              # Tests for risk management
│   ├── strategies/        # Tests for trading strategies
│   └── utils/             # Tests for utility functions
└── test_utils/            # Shared test utilities and mocks
```

## Running Tests

### Running All Tests

To run all tests in the test suite:

```bash
python -m pytest Tests/
```

### Running Specific Test Categories

To run only unit tests:

```bash
python -m pytest Tests/unit/
```

To run tests for a specific module:

```bash
python -m pytest Tests/unit/strategies/
```

### Running Individual Tests

To run a specific test file:

```bash
python -m pytest Tests/unit/strategies/test_sma_crossover.py
```

To run a specific test case:

```bash
python -m pytest Tests/unit/strategies/test_sma_crossover.py::TestSMAcrossover::test_calculate_signal_buy
```

## Test Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`
- BVA (Boundary Value Analysis) tests should be named `test_*_bva.py`

## Writing New Tests

When writing new tests:

1. Place the test in the appropriate module directory
2. Follow the existing test structure and naming conventions
3. Include docstrings with Gherkin-style feature/scenario descriptions
4. Use the test utilities in `test_utils/` for common testing functionality
5. Ensure tests are isolated and don't depend on external resources

## Test Utilities

The `test_utils/` directory contains shared utilities for testing:

- `mock_strategy.py`: Mock implementation of the Strategy base class
- Additional mocks and fixtures for testing

## Continuous Integration

These tests are run automatically as part of the CI/CD pipeline to ensure code quality and prevent regressions. 