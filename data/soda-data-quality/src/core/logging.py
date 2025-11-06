"""
Logging management following Single Responsibility Principle
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .interfaces import ILogger


class StandardLogger(ILogger):
    """Standard logging implementation"""
    
    def __init__(self, name: str, log_level: int = logging.INFO, log_file: Optional[str] = None):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(log_level)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            self._logger.addHandler(file_handler)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        if log_file:
            file_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self._logger.info(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self._logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self._logger.warning(message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self._logger.debug(message)


class LoggerFactory:
    """Factory for creating loggers"""
    
    @staticmethod
    def create_application_logger(project_root: str, log_level: int = logging.INFO) -> ILogger:
        """Create application logger with file output"""
        log_file = Path(project_root) / 'logs' / 'data_quality.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        return StandardLogger(
            name='data_quality_app',
            log_level=log_level,
            log_file=str(log_file)
        )
    
    @staticmethod
    def create_module_logger(module_name: str, log_level: int = logging.INFO) -> ILogger:
        """Create module-specific logger"""
        return StandardLogger(
            name=module_name,
            log_level=log_level
        )
