"""
Logging configuration for Kalshi AI Hedge Fund Framework
"""

import sys
from typing import Optional

try:
    from loguru import logger
except ImportError:
    # Fallback logging if loguru is not available
    import logging
    
    class LoggerWrapper:
        def __init__(self):
            self.logger = logging.getLogger("kalshi_hedge_fund")
            self.logger.setLevel(logging.INFO)
            
            if not self.logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        
        def info(self, message):
            self.logger.info(message)
        
        def error(self, message):
            self.logger.error(message)
        
        def warning(self, message):
            self.logger.warning(message)
        
        def debug(self, message):
            self.logger.debug(message)
        
        def remove(self):
            """Remove all handlers (no-op for basic logging)"""
            pass
        
        def add(self, sink, level=None, format=None, **kwargs):
            """Add handler (no-op for basic logging)"""
            pass
    
    logger = LoggerWrapper()


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration for the framework
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    try:
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stdout,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # Add file handler if specified
        if log_file:
            logger.add(
                log_file,
                level=level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="1 day",
                retention="30 days"
            )
        
        logger.info(f"Logging configured with level: {level}")
        
    except Exception as e:
        # Fallback to basic logging if loguru setup fails
        print(f"Failed to setup loguru logging: {e}")
        print("Using basic logging configuration")