#!/usr/bin/env python3
"""
Test Runner for Trading Bot

This script provides a convenient way to run tests for the Trading Bot project.
It supports running all tests or specific test categories.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_tests(test_path=None, verbose=False, coverage=False, pattern=None):
    """
    Run pytest with the specified options.
    
    Args:
        test_path (str): Path to the tests to run
        verbose (bool): Whether to run tests in verbose mode
        coverage (bool): Whether to generate coverage report
        pattern (str): Pattern to match test files
    
    Returns:
        int: Exit code from pytest
    """
    # Construct the pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add options
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=trading_bot", "--cov-report=term", "--cov-report=html"])
    
    # Add test path if specified
    if test_path:
        cmd.append(test_path)
    
    # Add pattern if specified
    if pattern:
        cmd.append(f"-k={pattern}")
    
    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    
    # Run the command
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run Trading Bot tests")
    
    # Add arguments
    parser.add_argument(
        "--unit", action="store_true", 
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", action="store_true", 
        help="Run only integration tests"
    )
    parser.add_argument(
        "--module", type=str, choices=["config", "core", "data", "exchanges", "risk", "strategies", "utils"],
        help="Run tests for a specific module"
    )
    parser.add_argument(
        "--file", type=str, 
        help="Run a specific test file"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", 
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage", action="store_true", 
        help="Generate coverage report"
    )
    parser.add_argument(
        "-k", "--pattern", type=str, 
        help="Only run tests matching the given pattern"
    )
    
    args = parser.parse_args()
    
    # Determine the test path
    base_test_path = "tests/"
    
    test_path = base_test_path
    
    if args.unit:
        test_path = f"{base_test_path}unit/"
    elif args.integration:
        test_path = f"{base_test_path}integration/"
    
    if args.module:
        module_path = f"{base_test_path}unit/{args.module}/"
        if os.path.exists(module_path):
            test_path = module_path
        else:
            # Try to find module tests in the flat structure
            print(f"Module directory {module_path} not found, searching for module tests in main test directory")
            test_path = base_test_path
    
    if args.file:
        test_path = args.file
        if not os.path.exists(test_path):
            # Try to find the file in the tests directory
            potential_paths = list(Path("tests").glob(f"**/{args.file}"))
            
            # Check if the file name was provided without extension
            if not args.file.endswith('.py'):
                potential_paths.extend(list(Path("tests").glob(f"**/{args.file}.py")))
            
            if potential_paths:
                test_path = str(potential_paths[0])
                print(f"Found test file at: {test_path}")
            else:
                print(f"Error: Test file '{args.file}' not found")
                return 1
    
    # Run the tests
    return run_tests(
        test_path=test_path,
        verbose=args.verbose,
        coverage=args.coverage,
        pattern=args.pattern
    )


if __name__ == "__main__":
    sys.exit(main()) 