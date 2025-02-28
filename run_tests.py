"""
Advanced test runner script for debugging test failures.
Run this script to get more detailed information about failing tests.
"""
import unittest
import sys
import traceback as tb_module
from io import StringIO

def run_tests():
    """Run all discovered tests with detailed output."""
    # Create a proper stream that has the writeln method
    stream = StringIO()
    runner = unittest.TextTestRunner(stream, descriptions=True, verbosity=2)
    
    # Discover and load all tests
    test_suite = unittest.defaultTestLoader.discover('tests')
    
    # Run the tests
    print("\n======= RUNNING ALL TESTS =======\n")
    result = runner.run(test_suite)
    
    # Print detailed output
    output = stream.getvalue()
    print(output)
    
    # Print summary
    print("\n======= TEST SUMMARY =======")
    print(f"Ran {result.testsRun} tests")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    # Print detailed failures
    if result.failures:
        print("\n======= TEST FAILURES =======")
        for i, (test, traceback) in enumerate(result.failures):
            print(f"\n--- Failure {i+1}: {test} ---")
            print(traceback)
    
    # Print errors
    if result.errors:
        print("\n======= TEST ERRORS =======")
        for i, (test, traceback) in enumerate(result.errors):
            print(f"\n--- Error {i+1}: {test} ---")
            print(traceback)
    
    return len(result.failures) + len(result.errors) == 0

def run_specific_test(test_name):
    """Run a specific test case or test method."""
    try:
        # Create a proper stream that has the writeln method
        stream = StringIO()
        runner = unittest.TextTestRunner(stream, descriptions=True, verbosity=2)
        
        if '.' in test_name:
            # If test_name contains a dot, it's specifying a test method
            # Format: module.TestClass.test_method
            test_suite = unittest.defaultTestLoader.loadTestsFromName(test_name)
        else:
            # Otherwise, it's a test module or class
            test_suite = unittest.defaultTestLoader.loadTestsFromName(f"tests.{test_name}")
        
        # Run the tests
        result = runner.run(test_suite)
        
        # Print detailed output
        output = stream.getvalue()
        print(output)
        
        # Print summary
        print("\n======= TEST SUMMARY =======")
        print(f"Ran {result.testsRun} tests")
        print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"❌ Failed: {len(result.failures)}")
        print(f"⚠️ Errors: {len(result.errors)}")
        
        # Print detailed failures and errors
        if result.failures:
            print("\n======= TEST FAILURES =======")
            for test, traceback in result.failures:
                print(f"\n--- Failure: {test} ---")
                print(traceback)
        
        if result.errors:
            print("\n======= TEST ERRORS =======")
            for test, traceback in result.errors:
                print(f"\n--- Error: {test} ---")
                print(traceback)
                
    except Exception as e:
        print(f"Error running test '{test_name}': {e}")
        tb_module.print_exc()

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        # Run specific test
        run_specific_test(sys.argv[1])
    else:
        # Run all tests
        success = run_tests()
        sys.exit(0 if success else 1) 