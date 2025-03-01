#!/usr/bin/env python
"""
Script to update imports from Trading_Bot and bot to trading_bot in all Python files.
This script is part of the migration process to standardize the package structure.
"""

import os
import re
import argparse
from pathlib import Path
import sys
from typing import List, Tuple


def update_imports(file_path: str, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """
    Update imports in a file from Trading_Bot and bot to trading_bot.
    
    Args:
        file_path: Path to the Python file
        dry_run: If True, don't write changes to file, just report
    
    Returns:
        Tuple of (whether_changed, list_of_changes)
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path} (not a text file)")
        return False, []
    
    changes = []
    
    # Track original content to check if any changes were made
    original_content = content
    
    # Replace specific import patterns
    patterns = [
        # from trading_bot.x import y
        (r'from\s+Trading_Bot\.([a-zA-Z0-9_\.]+)\s+import', r'from trading_bot.\1 import'),
        # from trading_bot.x import y
        (r'from\s+bot\.([a-zA-Z0-9_\.]+)\s+import', r'from trading_bot.\1 import'),
        # import trading_bot
        (r'import\s+Trading_Bot\b(?!\s*as)', r'import trading_bot'),
        # import trading_bot
        (r'import\s+bot\b(?!\s*as)', r'import trading_bot'),
        # import trading_bot as X
        (r'import\s+Trading_Bot\s+as\s+([a-zA-Z0-9_]+)', r'import trading_bot as \1'),
        # import trading_bot as X
        (r'import\s+bot\s+as\s+([a-zA-Z0-9_]+)', r'import trading_bot as \1'),
    ]
    
    for pattern, replacement in patterns:
        # Find all matches
        matches = re.findall(pattern, content)
        for match in matches:
            # Store the original line
            original_line = re.findall(f"{pattern.replace('([a-zA-Z0-9_\.]+)', match)}", content)
            if original_line:
                # Create replacement line
                replaced_line = re.sub(pattern, replacement, original_line[0])
                changes.append(f"{original_line[0]} -> {replaced_line}")
        
        # Apply replacement
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        if not dry_run:
            try:
                with open(file_path, 'w') as file:
                    file.write(content)
                print(f"Updated imports in {file_path}")
            except Exception as e:
                print(f"Error writing to {file_path}: {e}")
                return False, changes
        return True, changes
    return False, []


def find_python_files(directory: str, exclude_dirs: List[str] = None) -> List[str]:
    """
    Find all Python files in a directory, excluding specified directories.
    
    Args:
        directory: Directory to search
        exclude_dirs: List of directories to exclude
    
    Returns:
        List of paths to Python files
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Convert to absolute paths for easier comparison
    exclude_dirs = [os.path.abspath(d) for d in exclude_dirs]
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        if any(os.path.abspath(root).startswith(d) for d in exclude_dirs):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def main():
    """Main function to parse arguments and run the import updater."""
    parser = argparse.ArgumentParser(
        description='Update imports from Trading_Bot and bot to trading_bot'
    )
    parser.add_argument(
        '--directory', '-d', 
        default='.',
        help='Directory to search for Python files (default: current directory)'
    )
    parser.add_argument(
        '--exclude', '-e',
        action='append',
        default=[],
        help='Directories to exclude (can be specified multiple times)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode: show changes without modifying files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose mode: show all changed lines'
    )
    
    args = parser.parse_args()
    
    # Find Python files
    print(f"Searching for Python files in {args.directory}...")
    python_files = find_python_files(args.directory, args.exclude)
    print(f"Found {len(python_files)} Python files")
    
    # Update imports
    changed_files = 0
    total_changes = 0
    all_changes = []
    
    for file_path in python_files:
        changed, changes = update_imports(file_path, args.dry_run)
        if changed:
            changed_files += 1
            total_changes += len(changes)
            if args.verbose:
                for change in changes:
                    print(f"  {file_path}: {change}")
            all_changes.extend([f"{file_path}: {change}" for change in changes])
    
    # Report results
    mode = "Dry run: " if args.dry_run else ""
    print(f"{mode}Updated {changed_files} files with {total_changes} import changes")
    
    # Write changes to log file
    if all_changes and args.dry_run:
        log_file = "import_changes.log"
        with open(log_file, 'w') as f:
            for change in all_changes:
                f.write(f"{change}\n")
        print(f"Detailed changes written to {log_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 