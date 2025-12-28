"""
Unified logging utility for the MetaGPT + E2B system
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from app.core.config import settings


class SystemLogger:
    """Centralized logging utility with consistent formatting"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    
    @classmethod
    def configure(cls):
        """Configure logging system"""
        if cls._configured:
            return
            
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (production only)
        if settings.is_production():
            file_handler = logging.FileHandler(log_dir / "app.log")
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger for the given name"""
        if not cls._configured:
            cls.configure()
            
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def info(cls, name: str, message: str, **kwargs):
        """Log info message with context"""
        logger = cls.get_logger(name)
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        logger.info(message)
    
    @classmethod
    def error(cls, name: str, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with context"""
        logger = cls.get_logger(name)
        if error:
            message = f"{message} | Error: {str(error)}"
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        logger.error(message)
    
    @classmethod
    def warning(cls, name: str, message: str, **kwargs):
        """Log warning message with context"""
        logger = cls.get_logger(name)
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        logger.warning(message)
    
    @classmethod
    def debug(cls, name: str, message: str, **kwargs):
        """Log debug message with context"""
        logger = cls.get_logger(name)
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        logger.debug(message)


# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get logger for module"""
    return SystemLogger.get_logger(name)


def log_info(name: str, message: str, **kwargs):
    """Log info message"""
    SystemLogger.info(name, message, **kwargs)


def log_error(name: str, message: str, error: Optional[Exception] = None, **kwargs):
    """Log error message"""
    SystemLogger.error(name, message, error, **kwargs)


def log_warning(name: str, message: str, **kwargs):
    """Log warning message"""
    SystemLogger.warning(name, message, **kwargs)


def log_debug(name: str, message: str, **kwargs):
    """Log debug message"""
    SystemLogger.debug(name, message, **kwargs)