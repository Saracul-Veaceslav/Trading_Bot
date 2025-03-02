import pytest
from typing import Protocol, runtime_checkable

@runtime_checkable
class TestService(Protocol):
    """Test protocol for service registry tests."""
    
    def do_something(self) -> str:
        """Test method."""
        ...

class ConcreteTestService:
    """Concrete implementation of TestService for testing."""
    
    def do_something(self) -> str:
        """Return a test string."""
        return "test_result"

class AnotherTestService:
    """Another implementation of TestService for testing."""
    
    def do_something(self) -> str:
        """Return a different test string."""
        return "another_result"

class TestServiceRegistry:
    """Tests for the ServiceRegistry class."""
    
    def test_service_registry_creation(self):
        """Test that a ServiceRegistry can be created."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        assert registry is not None
    
    def test_register_service(self):
        """Test registering a service."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        service = ConcreteTestService()
        
        registry.register(TestService, service)
        
        assert registry.has(TestService)
    
    def test_get_service(self):
        """Test getting a registered service."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        service = ConcreteTestService()
        
        registry.register(TestService, service)
        retrieved = registry.get(TestService)
        
        assert retrieved is service
        assert retrieved.do_something() == "test_result"
    
    def test_get_nonexistent_service(self):
        """Test getting a service that hasn't been registered."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        
        with pytest.raises(KeyError):
            registry.get(TestService)
    
    def test_register_service_by_name(self):
        """Test registering a service with a name."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        service = ConcreteTestService()
        
        registry.register("test_service", service)
        
        assert registry.has("test_service")
        retrieved = registry.get("test_service")
        assert retrieved is service
    
    def test_register_multiple_implementations(self):
        """Test registering multiple implementations of the same protocol."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        service1 = ConcreteTestService()
        service2 = AnotherTestService()
        
        registry.register(TestService, service1, name="service1")
        registry.register(TestService, service2, name="service2")
        
        assert registry.get(TestService, name="service1").do_something() == "test_result"
        assert registry.get(TestService, name="service2").do_something() == "another_result"
    
    def test_register_factory(self):
        """Test registering a factory function."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        
        def factory():
            return ConcreteTestService()
        
        registry.register_factory(TestService, factory)
        
        service = registry.get(TestService)
        assert isinstance(service, ConcreteTestService)
        assert service.do_something() == "test_result"
    
    def test_singleton_service(self):
        """Test that singleton services return the same instance."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        
        def factory():
            return ConcreteTestService()
        
        registry.register_factory(TestService, factory, singleton=True)
        
        service1 = registry.get(TestService)
        service2 = registry.get(TestService)
        
        assert service1 is service2
    
    def test_non_singleton_service(self):
        """Test that non-singleton services return different instances."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        
        def factory():
            return ConcreteTestService()
        
        registry.register_factory(TestService, factory, singleton=False)
        
        service1 = registry.get(TestService)
        service2 = registry.get(TestService)
        
        assert service1 is not service2
        assert service1.do_something() == service2.do_something()
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        from abidance.core.container import ServiceRegistry
        
        registry = ServiceRegistry()
        service = ConcreteTestService()
        
        registry.register(TestService, service)
        assert registry.has(TestService)
        
        registry.clear()
        assert not registry.has(TestService) 