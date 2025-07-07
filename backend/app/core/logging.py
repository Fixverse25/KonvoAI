"""
EVA-Dev Logging Configuration
Structured logging setup for the application
"""

import logging
import sys
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup structured logging for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


class EVALogger:
    """Custom logger for EVA-Dev with structured logging"""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with context"""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with context"""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with context"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with context"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with context"""
        self.logger.critical(message, **kwargs)
    
    def bind(self, **kwargs: Any) -> "EVALogger":
        """Bind context to logger"""
        bound_logger = self.logger.bind(**kwargs)
        new_logger = EVALogger(self.logger.name)
        new_logger.logger = bound_logger
        return new_logger


def get_logger(name: str) -> EVALogger:
    """Get a structured logger instance"""
    return EVALogger(name)
