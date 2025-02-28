"""
Script to convert unittest tests to pytest format.

This script analyzes existing unittest test files and generates equivalent pytest test files.
"""
import os
import re
import argparse
from pathlib import Path

def parse_unittest_file(file_path):
    """Parse a unittest file and extract test classes and methods."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract imports
    import_pattern = r'^import.*$|^from.*import.*$'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    
    # Extract test classes
    class_pattern = r'class\s+(\w+)\s*\(.*\):\s*(?:\n\s+"""(.*?)""")?\s*'
    classes = re.findall(class_pattern, content, re.DOTALL)
    
    # Extract test methods for each class
    result = []
    for class_name, class_docstring in classes:
        method_pattern = r'def\s+(test_\w+)\s*\(self(?:,\s*\w+\s*=\s*\w+)*\):\s*(?:\n\s+"""(.*?)""")?\s*'
        methods = re.findall(method_pattern, content, re.DOTALL)
        result.append((class_name, class_docstring.strip(), methods))
    
    # Extract setUp and tearDown methods
    setup_pattern = r'def\s+setUp\s*\(self\):\s*(.*?)\s*(?=def\s+|$)'
    teardown_pattern = r'def\s+tearDown\s*\(self\):\s*(.*?)\s*(?=def\s+|$)'
    
    setup_match = re.search(setup_pattern, content, re.DOTALL)
    teardown_match = re.search(teardown_pattern, content, re.DOTALL)
    
    setup_code = setup_match.group(1).strip() if setup_match else None
    teardown_code = teardown_match.group(1).strip() if teardown_match else None
    
    return {
        'imports': imports,
        'classes': result,
        'setup': setup_code,
        'teardown': teardown_code
    }

def convert_assertions(code):
    """Convert unittest assertions to pytest assertions."""
    # Convert common assertions
    code = re.sub(r'self\.assertEqual\((.*?),\s*(.*?)\)', r'assert \1 == \2', code)
    code = re.sub(r'self\.assertNotEqual\((.*?),\s*(.*?)\)', r'assert \1 != \2', code)
    code = re.sub(r'self\.assertTrue\((.*?)\)', r'assert \1', code)
    code = re.sub(r'self\.assertFalse\((.*?)\)', r'assert not \1', code)
    code = re.sub(r'self\.assertIsNone\((.*?)\)', r'assert \1 is None', code)
    code = re.sub(r'self\.assertIsNotNone\((.*?)\)', r'assert \1 is not None', code)
    code = re.sub(r'self\.assertIn\((.*?),\s*(.*?)\)', r'assert \1 in \2', code)
    code = re.sub(r'self\.assertNotIn\((.*?),\s*(.*?)\)', r'assert \1 not in \2', code)
    
    # Handle more complex assertions
    code = re.sub(r'self\.assertRaises\((.*?),\s*(.*?)\)', r'with pytest.raises(\1):\n        \2', code)
    
    return code

def convert_to_pytest(parsed_data, file_name):
    """Convert parsed unittest data to pytest format."""
    output = []
    
    # Add pytest import
    output.append("import pytest")
    
    # Add original imports
    output.extend(parsed_data['imports'])
    output.append("")
    
    # Add fixtures for setup and teardown if they exist
    if parsed_data['setup']:
        setup_code = convert_assertions(parsed_data['setup'])
        output.append("@pytest.fixture")
        output.append("def setup_fixture():")
        for line in setup_code.split('\n'):
            # Replace self. references
            line = line.replace('self.', '')
            if line.strip():
                output.append(f"    {line}")
        output.append("    # Return any values needed by tests")
        output.append("    return {'setup_complete': True}")
        output.append("")
    
    # Process each test class
    for class_name, class_docstring, methods in parsed_data['classes']:
        # Add class docstring as a module-level docstring
        if class_docstring:
            output.append(f'"""{class_docstring}"""')
            output.append("")
        
        # Create test module or class comment
        output.append(f"# Tests from {class_name}")
        output.append("")
        
        # Process each test method
        for method_name, method_docstring in methods:
            # Extract the method body from the original file
            method_pattern = rf'def\s+{method_name}\s*\(self(?:,\s*\w+\s*=\s*\w+)*\):.*?(?=def\s+|$)'
            method_match = re.search(method_pattern, open(file_name, 'r').read(), re.DOTALL)
            
            if method_match:
                method_body = method_match.group(0)
                
                # Add docstring if it exists
                if method_docstring:
                    output.append(f"def {method_name}(setup_fixture):")
                    output.append(f'    """{method_docstring}"""')
                else:
                    output.append(f"def {method_name}(setup_fixture):")
                
                # Process the method body
                body_lines = method_body.split('\n')[1:]  # Skip the definition line
                indentation = 0
                
                for i, line in enumerate(body_lines):
                    if i == 0:
                        # Determine initial indentation
                        indentation = len(line) - len(line.lstrip())
                    
                    if line.strip():
                        # Remove original indentation and add new indentation
                        stripped_line = line[indentation:] if len(line) > indentation else line
                        
                        # Replace self. references
                        stripped_line = stripped_line.replace('self.', '')
                        
                        # Convert assertions
                        stripped_line = convert_assertions(stripped_line)
                        
                        output.append(f"    {stripped_line}")
                
                output.append("")
    
    return '\n'.join(output)

def convert_file(input_file, output_file=None):
    """Convert a unittest file to pytest format."""
    if output_file is None:
        # Generate output filename
        input_path = Path(input_file)
        output_file = input_path.parent / f"pytest_{input_path.name}"
    
    parsed_data = parse_unittest_file(input_file)
    pytest_content = convert_to_pytest(parsed_data, input_file)
    
    with open(output_file, 'w') as f:
        f.write(pytest_content)
    
    print(f"Converted {input_file} to {output_file}")

def convert_directory(input_dir, output_dir=None):
    """Convert all unittest files in a directory to pytest format."""
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'pytest')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file_name in os.listdir(input_dir):
        if file_name.startswith('test_') and file_name.endswith('.py'):
            input_file = os.path.join(input_dir, file_name)
            output_file = os.path.join(output_dir, file_name)
            convert_file(input_file, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert unittest tests to pytest format')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', help='Output file or directory (optional)')
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        convert_directory(args.input, args.output)
    else:
        convert_file(args.input, args.output) 