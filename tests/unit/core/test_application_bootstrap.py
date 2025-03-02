import pytest
from typing import Dict, Any, Protocol, runtime_checkable
import os
import tempfile
import yaml

@runtime_checkable
class TestComponent(Protocol):
    """Test protocol for application bootstrap tests."""
    
    def initialize(self) -> bool:
        """Initialize the component."""
        ...

class ConcreteTestComponent:
    """Concrete implementation of TestComponent for testing."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the component."""
        self.initialized = True
        return True

class TestApplicationBootstrap:
    """Tests for the ApplicationBootstrap class."""
    
    def test_application_bootstrap_creation(self):
        """Test that an ApplicationBootstrap can be created."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        assert bootstrap is not None
    
    def test_load_config_from_file(self):
        """Test loading configuration from a file."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            yaml.dump({
                'test_key': 'test_value',
                'nested': {
                    'key': 'value'
                }
            }, temp)
        
        try:
            bootstrap = ApplicationBootstrap()
            config = bootstrap.load_config(temp.name)
            
            assert config is not None
            assert config.get('test_key') == 'test_value'
            assert config.get('nested', {}).get('key') == 'value'
        finally:
            os.unlink(temp.name)
    
    def test_load_config_file_not_found(self):
        """Test loading configuration from a non-existent file."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        
        with pytest.raises(FileNotFoundError):
            bootstrap.load_config('non_existent_config.yaml')
    
    def test_load_config_invalid_yaml(self):
        """Test loading configuration from an invalid YAML file."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        # Create a temporary config file with invalid YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            temp.write('invalid: yaml: content:')
        
        try:
            bootstrap = ApplicationBootstrap()
            
            with pytest.raises(yaml.YAMLError):
                bootstrap.load_config(temp.name)
        finally:
            os.unlink(temp.name)
    
    def test_register_component(self):
        """Test registering a component."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        component = ConcreteTestComponent()
        
        bootstrap.register_component('test_component', component)
        
        assert bootstrap.has_component('test_component')
        assert bootstrap.get_component('test_component') is component
    
    def test_register_component_factory(self):
        """Test registering a component factory."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        
        def factory(config: Dict[str, Any]) -> ConcreteTestComponent:
            return ConcreteTestComponent(config)
        
        bootstrap.register_component_factory('test_component', factory)
        
        assert bootstrap.has_component_factory('test_component')
    
    def test_create_component_from_factory(self):
        """Test creating a component from a factory."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        config = {'key': 'value'}
        
        def factory(config: Dict[str, Any]) -> ConcreteTestComponent:
            return ConcreteTestComponent(config)
        
        bootstrap.register_component_factory('test_component', factory)
        component = bootstrap.create_component('test_component', config)
        
        assert isinstance(component, ConcreteTestComponent)
        assert component.config == config
    
    def test_create_component_factory_not_found(self):
        """Test creating a component with a non-existent factory."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        
        with pytest.raises(KeyError):
            bootstrap.create_component('non_existent_component', {})
    
    def test_initialize_components(self):
        """Test initializing all registered components."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        component1 = ConcreteTestComponent()
        component2 = ConcreteTestComponent()
        
        bootstrap.register_component('component1', component1)
        bootstrap.register_component('component2', component2)
        
        bootstrap.initialize_components()
        
        assert component1.initialized
        assert component2.initialized
    
    def test_initialize_application(self):
        """Test initializing the application with a configuration."""
        from abidance.core.bootstrap import ApplicationBootstrap
        
        bootstrap = ApplicationBootstrap()
        config = {
            'components': {
                'component1': {'key1': 'value1'},
                'component2': {'key2': 'value2'}
            }
        }
        
        # Register component factories
        def factory1(config: Dict[str, Any]) -> ConcreteTestComponent:
            return ConcreteTestComponent(config)
        
        def factory2(config: Dict[str, Any]) -> ConcreteTestComponent:
            return ConcreteTestComponent(config)
        
        bootstrap.register_component_factory('component1', factory1)
        bootstrap.register_component_factory('component2', factory2)
        
        # Initialize application
        bootstrap.initialize_application(config)
        
        # Check that components were created and initialized
        component1 = bootstrap.get_component('component1')
        component2 = bootstrap.get_component('component2')
        
        assert isinstance(component1, ConcreteTestComponent)
        assert isinstance(component2, ConcreteTestComponent)
        assert component1.initialized
        assert component2.initialized
        assert component1.config == {'key1': 'value1'}
        assert component2.config == {'key2': 'value2'} 