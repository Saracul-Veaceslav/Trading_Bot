#!/bin/bash
# Migration script for Trading Bot package reorganization
# This script runs the complete migration process in one step

set -e  # Exit on error

# Check if running in dry-run mode
DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo "Running in dry-run mode (no changes will be made)"
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Trading Bot package migration process...${NC}"

# Step 1: Create new package structure
echo -e "${YELLOW}Step 1: Creating new package structure...${NC}"
if [ "$DRY_RUN" == false ]; then
    mkdir -p trading_bot/{core,data,exchanges,strategies,risk,utils,config}
    touch trading_bot/__init__.py trading_bot/{core,data,exchanges,strategies,risk,utils,config}/__init__.py
    touch trading_bot/py.typed
else
    echo "Would create directory structure: trading_bot/{core,data,exchanges,strategies,risk,utils,config}"
    echo "Would create __init__.py files in each directory"
    echo "Would create py.typed file for type checking support"
fi

# Step 2: Copy files from old structure to new structure
echo -e "${YELLOW}Step 2: Copying files from old structure to new structure...${NC}"
MIGRATE_CMD="python migrate_files.py"
if [ "$DRY_RUN" == true ]; then
    MIGRATE_CMD="$MIGRATE_CMD --dry-run"
fi
eval $MIGRATE_CMD

# Step 3: Update imports in all Python files
echo -e "${YELLOW}Step 3: Updating imports in Python files...${NC}"
UPDATE_CMD="python update_imports.py"
if [ "$DRY_RUN" == true ]; then
    UPDATE_CMD="$UPDATE_CMD --dry-run"
fi
eval $UPDATE_CMD

# Step 4: Run tests to verify functionality
if [ "$DRY_RUN" == false ]; then
    echo -e "${YELLOW}Step 4: Running tests to verify functionality...${NC}"
    
    echo "Running old tests for comparison baseline:"
    python run_tests.py --module strategies || true
    
    echo "Running tests with new structure:"
    PYTHONPATH="." python run_tests.py --module strategies || true
else
    echo -e "${YELLOW}Step 4: Would run tests to verify functionality${NC}"
fi

# Step 5: Final steps and cleanup
echo -e "${YELLOW}Step 5: Final steps and cleanup...${NC}"
if [ "$DRY_RUN" == false ]; then
    # Create a backup of the old structure if it doesn't exist
    if [ ! -d "Trading_Bot_backup" ]; then
        echo "Creating backup of old Trading_Bot directory..."
        cp -R Trading_Bot Trading_Bot_backup
    fi
    
    # Remove the symbolic link to avoid confusion
    if [ -L "bot" ]; then
        echo "Removing 'bot' symbolic link..."
        rm bot
    fi
else
    echo "Would create backup of Trading_Bot directory"
    echo "Would remove 'bot' symbolic link"
fi

echo -e "${GREEN}Migration complete!${NC}"

if [ "$DRY_RUN" == false ]; then
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review the new structure in the 'trading_bot' directory"
    echo "2. Verify that all tests pass with the new structure"
    echo "3. Update any external scripts or documentation that reference the old structure"
else
    echo -e "${YELLOW}Run without --dry-run to perform the actual migration${NC}"
fi 