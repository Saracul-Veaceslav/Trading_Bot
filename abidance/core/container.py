"""
Dependency injection container for the Abidance trading bot.

This module provides a simple dependency injection container that allows
for registering and retrieving services by type or name. It supports
both direct instance registration and factory functions, with optional
singleton behavior.
"""

from typing import Dict, Any, Type, TypeVar, Callable, Optional, Union, cast, get_type_hints, runtime_checkable

T = TypeVar('T')
ServiceKey = Union[Type[T], str]
ServiceFactory = Callable[[], T]


class ServiceRegistry:
    """
    Simple dependency injection container.
    
    This class provides a registry for services that can be retrieved
    by type or name. It supports registering instances directly or
    through factory functions, with optional singleton behavior.
    """
    
    def __init__(self):
        """Initialize an empty service registry."""
        self._services: Dict[Any, Dict[str, Any]] = {}
        self._factories: Dict[Any, Dict[str, tuple[ServiceFactory, bool]]] = {}
        self._singletons: Dict[Any, Dict[str, Any]] = {}
    
    def register(self, service_type: ServiceKey, instance: Any, name: str = "default") -> None:
        """
        Register a service instance.
        
        Args:
            service_type: The type or name of the service
            instance: The service instance
            name: Optional name for the service (default: "default")
        """
        if service_type not in self._services:
            self._services[service_type] = {}
        
        self._services[service_type][name] = instance
    
    def register_factory(self, service_type: ServiceKey, factory: ServiceFactory, 
                         singleton: bool = True, name: str = "default") -> None:
        """
        Register a factory function for creating service instances.
        
        Args:
            service_type: The type or name of the service
            factory: Factory function that creates the service
            singleton: Whether to cache and reuse the instance (default: True)
            name: Optional name for the service (default: "default")
        """
        if service_type not in self._factories:
            self._factories[service_type] = {}
        
        self._factories[service_type][name] = (factory, singleton)
    
    def has(self, service_type: ServiceKey, name: str = "default") -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_type: The type or name of the service
            name: Optional name for the service (default: "default")
            
        Returns:
            True if the service is registered, False otherwise
        """
        # Check direct registrations
        if service_type in self._services and name in self._services[service_type]:
            return True
        
        # Check factories
        if service_type in self._factories and name in self._factories[service_type]:
            return True
        
        # Check singletons
        if service_type in self._singletons and name in self._singletons[service_type]:
            return True
        
        return False
    
    def get(self, service_type: ServiceKey, name: str = "default") -> Any:
        """
        Get a service instance.
        
        Args:
            service_type: The type or name of the service
            name: Optional name for the service (default: "default")
            
        Returns:
            The service instance
            
        Raises:
            KeyError: If the service is not registered
        """
        # Check direct registrations
        if service_type in self._services and name in self._services[service_type]:
            return self._services[service_type][name]
        
        # Check singletons
        if service_type in self._singletons and name in self._singletons[service_type]:
            return self._singletons[service_type][name]
        
        # Check factories
        if service_type in self._factories and name in self._factories[service_type]:
            factory, is_singleton = self._factories[service_type][name]
            instance = factory()
            
            # Cache singleton instances
            if is_singleton:
                if service_type not in self._singletons:
                    self._singletons[service_type] = {}
                self._singletons[service_type][name] = instance
            
            return instance
        
        raise KeyError(f"Service {service_type} with name '{name}' not registered")
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear() 