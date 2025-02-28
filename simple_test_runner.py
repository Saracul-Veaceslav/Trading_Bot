"""
Simplified test runner script for Python 3.13.
This script avoids the writeln issue in the more complex test runner.
"""
import unittest
import sys
import os

def run_tests():
    """Run all tests with standard unittest methods."""
    # Make sure current directory is in path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    # Create the test loader
    loader = unittest.TestLoader()
    
    # Discover all tests in the tests directory
    test_suite = loader.discover('tests')
    
    # Create a text test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    print("\n======= RUNNING ALL TESTS =======\n")
    result = runner.run(test_suite)
    
    # Print summary
    print("\n======= TEST SUMMARY =======")
    print(f"Ran {result.testsRun} tests")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return len(result.failures) + len(result.errors) == 0

def run_specific_test(test_name):
    """Run a specific test module."""
    # Make sure current directory is in path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    # Create the test loader
    loader = unittest.TestLoader()
    
    try:
        # Try to load the specified test
        if '.' in test_name:
            # It's a specific test method
            test_suite = loader.loadTestsFromName(test_name)
        else:
            # It's a test module
            test_suite = loader.loadTestsFromName(f"tests.{test_name}")
        
        # Run the test
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        # Print summary
        print(f"\nRan {result.testsRun} tests")
        print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Failed: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
    except Exception as e:
        print(f"Error loading test '{test_name}': {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        run_specific_test(sys.argv[1])
    else:
        # Run all tests
        success = run_tests()
        sys.exit(0 if success else 1) 