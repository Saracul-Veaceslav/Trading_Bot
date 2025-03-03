#!/usr/bin/env python3
"""
Script to start the Abidance Trading Bot API server.
"""

import logging
import os
from abidance.api.server import APIServer

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("abidance.api")

def main():
    """Start the API server."""
    logger.info("Starting Abidance Trading Bot API server")
    
    # Create and start the API server
    server = APIServer(host="0.0.0.0", port=8000)
    
    try:
        logger.info(f"API server running at {server.url}")
        server.start()
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
    except Exception as e:
        logger.exception(f"Error starting API server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 