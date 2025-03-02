import importlib
import os
import sys
import pytest
from pathlib import Path


class TestPackageStructure:
    """Test the abidance package structure for proper organization and imports."""

    def test_package_directory_exists(self):
        """Test that the abidance package directory exists."""
        # Get the root directory of the project (where pyproject.toml is located)
        root_dir = Path(__file__).resolve().parent.parent.parent
        abidance_dir = root_dir / "abidance"
        
        assert abidance_dir.exists(), "Abidance package directory not found"
        assert abidance_dir.is_dir(), "Abidance path exists but is not a directory"

    def test_required_subdirectories_exist(self):
        """Test that all required subdirectories exist in the abidance package."""
        root_dir = Path(__file__).resolve().parent.parent.parent
        abidance_dir = root_dir / "abidance"
        
        required_subdirs = [
            "trading",
            "exchange",
            "strategy",
            "data",
            "ml",
            "api",
            "core",
            "utils",
            "exceptions",
        ]
        
        for subdir in required_subdirs:
            path = abidance_dir / subdir
            assert path.exists(), f"Required subdirectory '{subdir}' does not exist"
            assert path.is_dir(), f"'{subdir}' exists but is not a directory"
            
            # Check that each subdirectory has an __init__.py file
            init_file = path / "__init__.py"
            assert init_file.exists(), f"__init__.py file missing in {subdir} directory"

    def test_main_init_file_exists(self):
        """Test that the main __init__.py file exists in the abidance package."""
        root_dir = Path(__file__).resolve().parent.parent.parent
        init_file = root_dir / "abidance" / "__init__.py"
        
        assert init_file.exists(), "Main __init__.py file missing in abidance package"
        
        # The __init__.py file should contain version information
        with open(init_file, "r") as f:
            content = f.read()
            assert "__version__" in content, "Version information missing in __init__.py"

    @pytest.mark.parametrize("module_path", [
        "abidance",
        "abidance.trading",
        "abidance.exchange",
        "abidance.strategy",
        "abidance.data",
        "abidance.ml",
        "abidance.api",
        "abidance.core",
        "abidance.utils",
        "abidance.exceptions",
    ])
    def test_module_imports(self, module_path):
        """Test that modules can be imported without errors."""
        try:
            # Dynamically import the module
            importlib.import_module(module_path)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_path}: {e}")
        
    def test_no_circular_imports(self):
        """Basic test to check for circular imports in key modules."""
        # List of modules to check for circular imports
        modules_to_check = [
            "abidance.trading",
            "abidance.exchange",
            "abidance.strategy",
            "abidance.data",
            "abidance.ml",
            "abidance.api",
            "abidance.core",
            "abidance.utils",
            "abidance.exceptions",
        ]
        
        # Save original sys.modules
        original_modules = dict(sys.modules)
        
        for module_name in modules_to_check:
            # Remove the module if it was already imported
            if module_name in sys.modules:
                del sys.modules[module_name]
                
            # Try to import the module
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                # Reset sys.modules
                sys.modules.clear()
                sys.modules.update(original_modules)
                pytest.fail(f"Circular import detected in {module_name}: {e}")
        
        # Reset sys.modules
        sys.modules.clear()
        sys.modules.update(original_modules)

    def test_py_typed_file_exists(self):
        """Test that the py.typed marker file exists for type hinting support."""
        root_dir = Path(__file__).resolve().parent.parent.parent
        py_typed_file = root_dir / "abidance" / "py.typed"
        
        assert py_typed_file.exists(), "py.typed marker file missing"

    def test_no_duplicate_modules(self):
        """Test that there are no duplicate module names between trading_bot and abidance."""
        root_dir = Path(__file__).resolve().parent.parent.parent
        abidance_dir = root_dir / "abidance"
        trading_bot_dir = root_dir / "trading_bot"
        
        # Skip if trading_bot directory doesn't exist (may be renamed/removed during migration)
        if not trading_bot_dir.exists():
            pytest.skip("trading_bot directory not found")
        
        abidance_modules = set()
        for root, dirs, files in os.walk(abidance_dir):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), abidance_dir)
                    module_path = os.path.splitext(rel_path)[0].replace(os.sep, ".")
                    abidance_modules.add(module_path)
        
        trading_bot_modules = set()
        for root, dirs, files in os.walk(trading_bot_dir):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), trading_bot_dir)
                    module_path = os.path.splitext(rel_path)[0].replace(os.sep, ".")
                    trading_bot_modules.add(module_path)
        
        # Find duplicate module paths (excluding __init__ and __main__)
        duplicates = {m for m in abidance_modules.intersection(trading_bot_modules) 
                     if not (m.endswith("__init__") or m.endswith("__main__"))}
        
        assert not duplicates, f"Duplicate module paths found: {duplicates}" 