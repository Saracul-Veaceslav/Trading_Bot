"""
Script to list all test files in the tests directory.
"""
import os
import glob

def list_test_files():
    """List all Python files in the tests directory."""
    test_dir = 'tests'
    
    if not os.path.exists(test_dir):
        print(f"Directory '{test_dir}' does not exist.")
        return
    
    test_files = glob.glob(os.path.join(test_dir, '*.py'))
    
    if not test_files:
        print(f"No Python files found in '{test_dir}' directory.")
        return
    
    print(f"Found {len(test_files)} test files:")
    for file_path in sorted(test_files):
        print(f"  - {os.path.basename(file_path)}")
        
        # Print the first few lines to see what's being tested
        try:
            with open(file_path, 'r') as f:
                content = f.read().splitlines()
                
            # Print first 10 non-empty, non-comment lines
            count = 0
            for line in content:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('"""'):
                    print(f"    {line}")
                    count += 1
                    if count >= 5:
                        break
            print()
        except Exception as e:
            print(f"    Error reading file: {e}\n")

if __name__ == "__main__":
    list_test_files() 