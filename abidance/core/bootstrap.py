"""
Application bootstrap module for the Abidance trading bot.

This module provides functionality for bootstrapping the application,
including loading configuration, registering components, and initializing
the application.
"""

from typing import Dict, Any, Callable, Optional, TypeVar, cast
import logging

import yaml


from .container import ServiceRegistry

T = TypeVar('T')
ComponentFactory = Callable[[Dict[str, Any]], T]

logger = logging.getLogger(__name__)

class ApplicationBootstrap:
    """
    Application bootstrap for the Abidance trading bot.

    This class provides functionality for bootstrapping the application,
    including loading configuration, registering components, and initializing
    the application.
    """

    def __init__(self):
        """Initialize the application bootstrap."""
        self._components: Dict[str, Any] = {}
        self._component_factories: Dict[str, ComponentFactory] = {}
        self._service_registry = ServiceRegistry()

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Loaded configuration

        Raises:
            FileNotFoundError: If the configuration file is not found
            yaml.YAMLError: If the configuration file contains invalid YAML
        """
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)

            if config is None:
                config = {}

            logger.info("Configuration loaded from %s", config_path)
            return config
        except FileNotFoundError:
            logger.error("Configuration file not found: %s", config_path)
            raise
        except yaml.YAMLError as e:
            logger.error("Invalid YAML in configuration file: %s", e)
            raise
        except Exception as e:
            logger.error("Error loading configuration: %s", e)
            raise

    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component.

        Args:
            name: Name of the component
            component: Component instance
        """
        self._components[name] = component
        self._service_registry.register(name, component)
        logger.debug("Component registered: %s", name)

    def register_component_factory(self, name: str, factory: ComponentFactory) -> None:
        """
        Register a component factory.

        Args:
            name: Name of the component
            factory: Factory function for creating the component
        """
        self._component_factories[name] = factory
        logger.debug("Component factory registered: %s", name)

    def has_component(self, name: str) -> bool:
        """
        Check if a component is registered.

        Args:
            name: Name of the component

        Returns:
            True if the component is registered, False otherwise
        """
        return name in self._components

    def has_component_factory(self, name: str) -> bool:
        """
        Check if a component factory is registered.

        Args:
            name: Name of the component

        Returns:
            True if the component factory is registered, False otherwise
        """
        return name in self._component_factories

    def get_component(self, name: str) -> Any:
        """
        Get a registered component.

        Args:
            name: Name of the component

        Returns:
            Component instance

        Raises:
            KeyError: If the component is not registered
        """
        if not self.has_component(name):
            raise KeyError(f"Component not registered: {name}")

        return self._components[name]

    def create_component(self, name: str, config: Dict[str, Any]) -> Any:
        """
        Create a component using a registered factory.

        Args:
            name: Name of the component
            config: Configuration for the component

        Returns:
            Created component

        Raises:
            KeyError: If the component factory is not registered
        """
        if not self.has_component_factory(name):
            raise KeyError(f"Component factory not registered: {name}")

        factory = self._component_factories[name]
        component = factory(config)

        # Register the created component
        self.register_component(name, component)

        return component

    def initialize_components(self) -> None:
        """
        Initialize all registered components.

        This method calls the initialize method on all registered components
        that have such a method.
        """
        for name, component in self._components.items():
            if hasattr(component, 'initialize') and callable(getattr(component, 'initialize')):
                try:
                    logger.info("Initializing component: %s", name)
                    component.initialize()
                except Exception as e:
                    logger.error("Error initializing component %s: %s", name, e)
                    raise

    def initialize_application(self, config: Dict[str, Any]) -> None:
        """
        Initialize the application with the given configuration.

        This method creates components from registered factories based on the
        configuration, and then initializes all components.

        Args:
            config: Application configuration
        """
        # Create components from factories
        components_config = config.get('components', {})
        for name, component_config in components_config.items():
            if self.has_component_factory(name):
                try:
                    logger.info("Creating component: %s", name)
                    self.create_component(name, component_config)
                except Exception as e:
                    logger.error("Error creating component %s: %s", name, e)
                    raise

        # Initialize all components
        self.initialize_components()

    def get_service_registry(self) -> ServiceRegistry:
        """
        Get the service registry.

        Returns:
            Service registry
        """
        return self._service_registry
