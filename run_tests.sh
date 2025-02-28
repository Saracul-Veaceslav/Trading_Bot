#!/bin/bash

# -----------------------------------------------------
# IMPORTANT: Make this script executable with:
#   chmod +x run_tests.sh
# -----------------------------------------------------

# Run tests script for Trading Bot
# This script can run both unittest and pytest tests

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}     Trading Bot Test Runner        ${NC}"
echo -e "${BLUE}=====================================${NC}"

# Create a usage function
usage() {
    echo -e "${YELLOW}Usage:${NC} $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -u, --unittest   Run unittest tests (default)"
    echo "  -p, --pytest     Run pytest tests"
    echo "  -a, --all        Run both unittest and pytest tests"
    echo "  -v, --verbose    Verbose output"
    echo "  -c, --coverage   Run with coverage"
    echo
}

# Initialize variables
TEST_FRAMEWORK="unittest"
VERBOSE=""
COVERAGE=""

# Parse command line arguments
while [ "$1" != "" ]; do
    case $1 in
        -h | --help )           usage
                                exit
                                ;;
        -u | --unittest )       TEST_FRAMEWORK="unittest"
                                ;;
        -p | --pytest )         TEST_FRAMEWORK="pytest"
                                ;;
        -a | --all )            TEST_FRAMEWORK="all"
                                ;;
        -v | --verbose )        VERBOSE="-v"
                                ;;
        -c | --coverage )       COVERAGE="coverage run --source=Trading_Bot -m"
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

# Run tests based on the selected framework
if [ "$TEST_FRAMEWORK" = "unittest" ] || [ "$TEST_FRAMEWORK" = "all" ]; then
    echo -e "${GREEN}Running unittest tests...${NC}"
    if [ "$COVERAGE" != "" ]; then
        $COVERAGE python -m unittest discover $VERBOSE tests
    else
        python -m unittest discover $VERBOSE tests
    fi
    UNITTEST_RESULT=$?
    echo
fi

if [ "$TEST_FRAMEWORK" = "pytest" ] || [ "$TEST_FRAMEWORK" = "all" ]; then
    echo -e "${GREEN}Running pytest tests...${NC}"
    if [ "$COVERAGE" != "" ]; then
        $COVERAGE pytest $VERBOSE tests/pytest_*.py
    else
        python -m pytest $VERBOSE tests/pytest_*.py
    fi
    PYTEST_RESULT=$?
    echo
fi

# Generate coverage report if coverage was enabled
if [ "$COVERAGE" != "" ]; then
    echo -e "${GREEN}Generating coverage report...${NC}"
    coverage report
    echo -e "${YELLOW}Use 'coverage html' to generate a detailed HTML report${NC}"
    echo
fi

# Print summary
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}              Summary               ${NC}"
echo -e "${BLUE}=====================================${NC}"

if [ "$TEST_FRAMEWORK" = "unittest" ] || [ "$TEST_FRAMEWORK" = "all" ]; then
    if [ $UNITTEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}Unittest: PASSED${NC}"
    else
        echo -e "${RED}Unittest: FAILED${NC}"
    fi
fi

if [ "$TEST_FRAMEWORK" = "pytest" ] || [ "$TEST_FRAMEWORK" = "all" ]; then
    if [ $PYTEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}Pytest: PASSED${NC}"
    else
        echo -e "${RED}Pytest: FAILED${NC}"
    fi
fi

# Set the exit code based on test results
if [ "$TEST_FRAMEWORK" = "all" ]; then
    if [ $UNITTEST_RESULT -eq 0 ] && [ $PYTEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}All tests PASSED${NC}"
        exit 0
    else
        echo -e "${RED}Some tests FAILED${NC}"
        exit 1
    fi
elif [ "$TEST_FRAMEWORK" = "unittest" ]; then
    exit $UNITTEST_RESULT
else
    exit $PYTEST_RESULT
fi 