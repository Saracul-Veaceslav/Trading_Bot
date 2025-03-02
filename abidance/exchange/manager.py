"""
Exchange manager module for handling multiple exchange connections.
"""
import logging
from typing import Dict, List, Optional, Type

from ..exceptions import ExchangeError
from .base import Exchange


class ExchangeManager:
    """
    Manager for handling multiple exchange connections.
    
    This class manages the creation and access of exchange instances,
    providing a centralized interface for exchange interactions.
    """
    
    def __init__(self):
        """Initialize the exchange manager."""
        self.exchanges: Dict[str, Exchange] = {}
        self.default_exchange_id: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self._exchange_registry: Dict[str, Type[Exchange]] = {}
    
    def register_exchange_class(self, exchange_id: str, exchange_class: Type[Exchange]) -> None:
        """
        Register an exchange class for later instantiation.
        
        Args:
            exchange_id: Identifier for the exchange
            exchange_class: Exchange class to register
        """
        self._exchange_registry[exchange_id] = exchange_class
        self.logger.debug(f"Registered exchange class: {exchange_id}")
    
    def add_exchange(self, exchange: Exchange, is_default: bool = False) -> None:
        """
        Add an exchange instance to the manager.
        
        Args:
            exchange: Exchange instance
            is_default: Whether this exchange should be the default
        """
        exchange_id = exchange.exchange_id
        self.exchanges[exchange_id] = exchange
        
        if is_default or self.default_exchange_id is None:
            self.default_exchange_id = exchange_id
            
        self.logger.info(f"Added exchange: {exchange_id} (default: {is_default})")
    
    def create_exchange(self, exchange_id: str, api_key: Optional[str] = None, 
                        api_secret: Optional[str] = None, testnet: bool = False, 
                        is_default: bool = False, **kwargs) -> Exchange:
        """
        Create and add a new exchange instance.
        
        Args:
            exchange_id: Identifier for the exchange
            api_key: API key for authentication
            api_secret: API secret for authentication
            testnet: Whether to use testnet/sandbox
            is_default: Whether this exchange should be the default
            **kwargs: Additional exchange-specific parameters
            
        Returns:
            The created Exchange instance
            
        Raises:
            ExchangeError: If the exchange class is not registered
        """
        if exchange_id not in self._exchange_registry:
            raise ExchangeError(f"Unknown exchange: {exchange_id}")
        
        exchange_class = self._exchange_registry[exchange_id]
        exchange = exchange_class(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
            **kwargs
        )
        
        self.add_exchange(exchange, is_default)
        return exchange
    
    def get_exchange(self, exchange_id: Optional[str] = None) -> Exchange:
        """
        Get an exchange instance.
        
        Args:
            exchange_id: Identifier for the exchange, or None for default
            
        Returns:
            The Exchange instance
            
        Raises:
            ExchangeError: If no exchanges are available or the requested exchange is not found
        """
        if not self.exchanges:
            raise ExchangeError("No exchanges available")
        
        if exchange_id is None:
            if self.default_exchange_id is None:
                raise ExchangeError("No default exchange set")
            exchange_id = self.default_exchange_id
        
        if exchange_id not in self.exchanges:
            raise ExchangeError(f"Exchange not found: {exchange_id}")
        
        return self.exchanges[exchange_id]
    
    def remove_exchange(self, exchange_id: str) -> None:
        """
        Remove an exchange instance.
        
        Args:
            exchange_id: Identifier for the exchange to remove
            
        Raises:
            ExchangeError: If the exchange is not found
        """
        if exchange_id not in self.exchanges:
            raise ExchangeError(f"Exchange not found: {exchange_id}")
        
        # If removing the default exchange, set a new default if possible
        if exchange_id == self.default_exchange_id:
            self.default_exchange_id = next(iter(self.exchanges.keys())) if self.exchanges else None
            
        del self.exchanges[exchange_id]
        self.logger.info(f"Removed exchange: {exchange_id}")
    
    def get_all_exchanges(self) -> List[Exchange]:
        """
        Get all registered exchange instances.
        
        Returns:
            List of Exchange instances
        """
        return list(self.exchanges.values()) 