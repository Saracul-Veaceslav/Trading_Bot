#!/usr/bin/env python
"""
Script to migrate files from the old Trading_Bot structure to the new trading_bot structure.

This script copies files from the old structure to the new one, maintaining the directory
hierarchy while adapting it to the new standardized structure.
"""

import os
import shutil
import argparse
from pathlib import Path
import sys
from typing import Dict, List, Set


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    os.makedirs(directory, exist_ok=True)


def get_module_mapping() -> Dict[str, str]:
    """
    Get mapping of old module paths to new module paths.
    
    Returns:
        Dictionary mapping old paths to new paths
    """
    return {
        # Core modules
        "Trading_Bot/strategy_executor.py": "trading_bot/core/strategy_executor.py",
        "Trading_Bot/main.py": "trading_bot/core/main.py",
        
        # Data modules
        "Trading_Bot/data_manager.py": "trading_bot/data/manager.py",
        "Trading_Bot/data": "trading_bot/data",
        
        # Exchange modules
        "Trading_Bot/exchange.py": "trading_bot/exchanges/base.py",
        "Trading_Bot/binance.py": "trading_bot/exchanges/binance.py",
        
        # Strategy modules
        "Trading_Bot/strategies": "trading_bot/strategies",
        "Trading_Bot/strategy.py": "trading_bot/strategies/base.py",
        
        # Risk modules
        "Trading_Bot/risk": "trading_bot/risk",
        
        # Config modules
        "Trading_Bot/config": "trading_bot/config",
        
        # Utility modules
        "Trading_Bot/logger.py": "trading_bot/utils/logger.py",
        "Trading_Bot/utils.py": "trading_bot/utils/helpers.py",
    }


def copy_file(source: str, destination: str, dry_run: bool = False) -> None:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        dry_run: If True, don't actually copy, just print what would be done
    """
    # Ensure the destination directory exists
    dest_dir = os.path.dirname(destination)
    if not dry_run:
        ensure_directory(dest_dir)
    
    if os.path.isfile(source):
        if dry_run:
            print(f"Would copy {source} -> {destination}")
        else:
            print(f"Copying {source} -> {destination}")
            shutil.copy2(source, destination)
    else:
        print(f"Warning: Source file not found: {source}")


def copy_directory(source: str, destination: str, exclude: Set[str] = None, dry_run: bool = False) -> None:
    """
    Copy a directory from source to destination.
    
    Args:
        source: Source directory path
        destination: Destination directory path
        exclude: Set of file/directory names to exclude
        dry_run: If True, don't actually copy, just print what would be done
    """
    if exclude is None:
        exclude = set()
    
    if not os.path.isdir(source):
        print(f"Warning: Source directory not found: {source}")
        return
    
    # Ensure the destination directory exists
    if not dry_run:
        ensure_directory(destination)
    
    for item in os.listdir(source):
        if item in exclude or item.startswith('.'):
            continue
        
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        
        if os.path.isdir(s):
            if dry_run:
                print(f"Would copy directory {s} -> {d}")
            else:
                copy_directory(s, d, exclude, dry_run)
        else:
            if dry_run:
                print(f"Would copy file {s} -> {d}")
            else:
                copy_file(s, d, dry_run)


def migrate_files(mapping: Dict[str, str], dry_run: bool = False) -> None:
    """
    Migrate files according to the provided mapping.
    
    Args:
        mapping: Dictionary mapping old paths to new paths
        dry_run: If True, don't actually copy, just print what would be done
    """
    for source, destination in mapping.items():
        if os.path.isdir(source):
            copy_directory(source, destination, dry_run=dry_run)
        else:
            copy_file(source, destination, dry_run=dry_run)


def main() -> int:
    """
    Main function to parse arguments and run the migration.
    
    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description='Migrate files from Trading_Bot to trading_bot'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode: show what would be done without making changes'
    )
    
    args = parser.parse_args()
    
    # Get module mapping
    mapping = get_module_mapping()
    
    # Migrate files
    print(f"{'Dry run: ' if args.dry_run else ''}Migrating files from Trading_Bot to trading_bot")
    migrate_files(mapping, args.dry_run)
    
    print(f"{'Dry run: ' if args.dry_run else ''}Migration complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())