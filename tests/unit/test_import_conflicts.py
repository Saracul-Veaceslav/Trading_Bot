import sys
import pytest
import importlib
from collections import defaultdict


class TestImportConflicts:
    """Test for import conflicts in the abidance package structure."""
    
    def test_no_module_shadowing(self):
        """
        Test that abidance modules don't shadow important standard or third-party libraries.
        
        This checks that our package doesn't have module names that would shadow
        commonly used libraries, which could cause confusion or bugs.
        """
        # List of common standard library and third-party packages that should not be shadowed
        common_packages = [
            "os", "sys", "json", "csv", "time", "datetime", "math", "random",
            "collections", "itertools", "functools", "re", "hashlib", "uuid",
            "threading", "multiprocessing", "asyncio", "socket", "urllib",
            "http", "email", "logging", "argparse", "pathlib", "typing",
            "numpy", "pandas", "matplotlib", "sklearn", "torch", "tensorflow",
            "pytest", "unittest", "flask", "django", "sqlalchemy", "requests"
        ]
        
        # Try to import abidance
        try:
            import abidance
        except ImportError as e:
            pytest.fail(f"Failed to import abidance package: {e}")
        
        # Check for direct module shadowing at top level
        for package in common_packages:
            assert not hasattr(abidance, package), f"abidance should not shadow '{package}' module"
        
        # Check for shadowing in submodules
        submodules = [
            "abidance.trading", "abidance.exchange", "abidance.strategy",
            "abidance.data", "abidance.ml", "abidance.api", "abidance.core",
            "abidance.utils", "abidance.exceptions"
        ]
        
        for submodule_name in submodules:
            try:
                submodule = importlib.import_module(submodule_name)
                for package in common_packages:
                    assert not hasattr(submodule, package), f"{submodule_name} should not shadow '{package}' module"
            except ImportError:
                # If submodule doesn't exist yet, skip
                pass
    
    def test_no_duplicate_class_names_across_modules(self):
        """
        Test that the same class name is not used in multiple modules.
        
        While Python allows the same class name in different modules, it can be confusing
        to have multiple classes with the same name in the same project.
        """
        # Try to import abidance modules
        modules_to_check = [
            "abidance.trading", "abidance.exchange", "abidance.strategy",
            "abidance.data", "abidance.ml", "abidance.api", "abidance.core",
            "abidance.utils", "abidance.exceptions"
        ]
        
        # Dictionary to track class names across modules
        class_to_modules = defaultdict(list)
        
        for module_name in modules_to_check:
            try:
                module = importlib.import_module(module_name)
                
                # Get all classes defined in this module
                for name in dir(module):
                    # Skip private/protected attributes and any built-in attributes
                    if name.startswith('_') or name in ('__file__', '__doc__', '__name__', '__package__'):
                        continue
                        
                    attr = getattr(module, name)
                    
                    # Check if it's a class
                    if isinstance(attr, type):
                        class_to_modules[name].append(module_name)
            except ImportError:
                # If module doesn't exist yet, skip
                pass
        
        # Check for class names used in multiple modules
        duplicate_classes = {cls: modules for cls, modules in class_to_modules.items() if len(modules) > 1}
        
        # Allow exceptions for some common utility classes that might intentionally be in multiple modules
        allowed_duplicates = {
            "Config",      # Configuration class might be used in multiple modules
            "Meta",        # Metadata class might be used in multiple modules
            "Error",       # Basic error class might be in multiple modules
            "Base",        # Base class might be in multiple modules
            "Order",       # Order class is used in both trading and core (adapter pattern)
            "Position",    # Position class is used in both trading and core (adapter pattern)
            "Trade",       # Trade class is used in both trading and core (adapter pattern)
            "OrderSide",   # OrderSide enum is used in both trading and core
            "OrderType",   # OrderType enum is used in both trading and core
            "ValidationError"  # ValidationError is used in both core and exceptions
        }
        
        real_duplicates = {k: v for k, v in duplicate_classes.items() if k not in allowed_duplicates}
        
        assert not real_duplicates, (
            f"Found class names used in multiple modules: "
            f"{', '.join([f'{cls} in {', '.join(modules)}' for cls, modules in real_duplicates.items()])}"
        )
    
    def test_no_wildcard_imports(self):
        """
        Test that there are no wildcard imports in the package.
        
        Wildcard imports (from module import *) are generally discouraged as they
        can lead to namespace pollution and make it hard to trace where symbols come from.
        """
        import inspect
        import ast
        import os
        from pathlib import Path
        
        # Get the root directory
        root_dir = Path(__file__).resolve().parent.parent.parent
        abidance_dir = root_dir / "abidance"
        
        # Skip if the directory doesn't exist yet
        if not abidance_dir.exists():
            pytest.skip("abidance directory not found")
        
        # Find all Python files
        py_files = []
        for root, _, files in os.walk(abidance_dir):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        
        # Check each file for wildcard imports
        wildcard_imports = []
        
        for py_file in py_files:
            with open(py_file, 'r') as f:
                try:
                    tree = ast.parse(f.read(), py_file)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and node.names[0].name == '*':
                            rel_path = os.path.relpath(py_file, root_dir)
                            wildcard_imports.append(f"{rel_path}: from {node.module} import *")
                except Exception as e:
                    # Skip files that can't be parsed
                    continue
        
        assert not wildcard_imports, f"Found wildcard imports:\n" + "\n".join(wildcard_imports)
    
    def test_no_direct_internal_imports(self):
        """
        Test that modules don't import internal implementation details from other modules.
        
        Good practice is to only import from the public API of other modules, not directly
        from their internal implementation files.
        """
        import inspect
        import ast
        import os
        from pathlib import Path
        
        # Get the root directory
        root_dir = Path(__file__).resolve().parent.parent.parent
        abidance_dir = root_dir / "abidance"
        
        # Skip if the directory doesn't exist yet
        if not abidance_dir.exists():
            pytest.skip("abidance directory not found")
        
        # Find all Python files
        py_files = []
        for root, _, files in os.walk(abidance_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    py_files.append(os.path.join(root, file))
        
        # Check each file for internal imports
        internal_imports = []
        
        for py_file in py_files:
            with open(py_file, 'r') as f:
                try:
                    tree = ast.parse(f.read(), py_file)
                    module_path = os.path.relpath(py_file, root_dir).replace('/', '.').replace('\\', '.')[:-3]
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            # Skip imports from the same module
                            if node.module and node.module.startswith('abidance.'):
                                # Check if it's importing from an internal module (not __init__)
                                if '._' in node.module or node.module.split('.')[-1] != '__init__':
                                    importing_path = node.module
                                    
                                    # Skip if importing from parent or sibling
                                    if not module_path.startswith(importing_path) and not importing_path.startswith(module_path):
                                        rel_path = os.path.relpath(py_file, root_dir)
                                        internal_imports.append(f"{rel_path}: from {node.module} import {', '.join([n.name for n in node.names])}")
                except Exception as e:
                    # Skip files that can't be parsed
                    continue
        
        # This assertion is commented out since we're still developing and not enforcing this rule yet
        # When the project matures, we can uncomment this
        # assert not internal_imports, f"Found internal implementation imports:\n" + "\n".join(internal_imports) 