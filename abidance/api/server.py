"""
Server implementation for the Abidance trading bot API.

This module provides the APIServer class for serving the RESTful API.
"""

from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI

from abidance.api.app import app

class APIServer:
    """
    Server for the Abidance trading bot API.
    
    This class wraps the FastAPI application and provides methods for
    starting and stopping the server.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000, 
                 app: Optional[FastAPI] = None, **kwargs: Any):
        """
        Initialize the API server.
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            app: FastAPI application instance (uses default if None)
            **kwargs: Additional keyword arguments to pass to uvicorn
        """
        self.host = host
        self.port = port
        self.app = app or globals()['app']
        self.server_config = {
            "host": host,
            "port": port,
            **kwargs
        }
        self._server = None
    
    def start(self, block: bool = True) -> None:
        """
        Start the API server.
        
        Args:
            block: Whether to block the current thread
        """
        if block:
            uvicorn.run(self.app, **self.server_config)
        else:
            # For non-blocking operation, would need to use a separate thread
            # or process, which is not implemented here
            raise NotImplementedError(
                "Non-blocking server start is not implemented yet"
            )
    
    def stop(self) -> None:
        """Stop the API server."""
        # This would need to be implemented if using a separate thread or process
        pass
    
    @property
    def url(self) -> str:
        """Get the base URL of the server."""
        return f"http://{self.host}:{self.port}" 