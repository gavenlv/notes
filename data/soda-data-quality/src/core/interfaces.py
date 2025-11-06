"""
Core interfaces following SOLID principles
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class IDataQualityChecker(ABC):
    """Interface for data quality checkers"""
    
    @abstractmethod
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all data quality checks"""
        pass
    
    @abstractmethod
    def get_data_source_name(self) -> str:
        """Get the name of the data source"""
        pass


class IDataQualityReporter(ABC):
    """Interface for data quality reporters"""
    
    @abstractmethod
    def store_scan_results(self, results: List[Dict[str, Any]]) -> None:
        """Store scan results"""
        pass
    
    @abstractmethod
    def get_reporter_name(self) -> str:
        """Get the name of the reporter"""
        pass


class IDatabaseConnection(ABC):
    """Interface for database connections"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active"""
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        pass


class IConfigurationManager(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def load_config(self) -> None:
        """Load configuration from source"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate configuration"""
        pass


class ILogger(ABC):
    """Interface for logging"""
    
    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message"""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message"""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message"""
        pass
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """Log debug message"""
        pass


class IFileManager(ABC):
    """Interface for file operations"""
    
    @abstractmethod
    def save_report(self, data: Dict[str, Any], filename: str) -> str:
        """Save report to file"""
        pass
    
    @abstractmethod
    def load_config_file(self, filepath: str) -> str:
        """Load configuration file content"""
        pass
    
    @abstractmethod
    def ensure_directory_exists(self, directory: str) -> None:
        """Ensure directory exists"""
        pass


class IDataQualityScan(ABC):
    """Interface for data quality scans"""
    
    @abstractmethod
    def execute_scan(self) -> Dict[str, Any]:
        """Execute the scan"""
        pass
    
    @abstractmethod
    def get_scan_id(self) -> str:
        """Get unique scan ID"""
        pass
    
    @abstractmethod
    def get_scan_timestamp(self) -> datetime:
        """Get scan timestamp"""
        pass
