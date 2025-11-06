"""
Base reporter implementation following Observer pattern
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any
from abc import ABC

from ..core.interfaces import IDataQualityReporter, IDatabaseConnection, ILogger


class BaseDataQualityReporter(IDataQualityReporter, ABC):
    """Base implementation for data quality reporters"""
    
    def __init__(self, 
                 database_connection: IDatabaseConnection,
                 logger: ILogger,
                 reporter_name: str):
        self._db_connection = database_connection
        self._logger = logger
        self._reporter_name = reporter_name
    
    def get_reporter_name(self) -> str:
        """Get the name of the reporter"""
        return self._reporter_name
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> datetime:
        """Get current timestamp"""
        return datetime.now()
    
    def _determine_check_type(self, check_name: str) -> str:
        """Determine check type from check name"""
        check_name_lower = check_name.lower()
        if 'missing' in check_name_lower:
            return 'completeness'
        elif 'duplicate' in check_name_lower:
            return 'uniqueness'
        elif 'format' in check_name_lower or 'valid' in check_name_lower:
            return 'validity'
        elif 'reference' in check_name_lower:
            return 'referential_integrity'
        elif 'positive' in check_name_lower or 'negative' in check_name_lower:
            return 'range'
        elif 'fresh' in check_name_lower or 'recent' in check_name_lower:
            return 'freshness'
        else:
            return 'general'
    
    def _determine_severity(self, check_name: str) -> str:
        """Determine severity from check name"""
        check_name_lower = check_name.lower()
        if any(keyword in check_name_lower for keyword in ['critical', 'security', 'pii']):
            return 'critical'
        elif any(keyword in check_name_lower for keyword in ['duplicate', 'format', 'valid']):
            return 'high'
        elif any(keyword in check_name_lower for keyword in ['missing', 'fresh']):
            return 'medium'
        else:
            return 'low'
    
    def _extract_numeric_value(self, details: str) -> float:
        """Extract numeric value from check details"""
        try:
            # Look for patterns like "check_value: 123" or "value: 456"
            import re
            patterns = [
                r'check_value:\s*([+-]?\d*\.?\d+)',
                r'value:\s*([+-]?\d*\.?\d+)',
                r'count:\s*([+-]?\d*\.?\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, details)
                if match:
                    return float(match.group(1))
            
            return 0.0
        except:
            return 0.0
    
    def _determine_log_level(self, log_line: str) -> str:
        """Determine log level from log line"""
        log_line_lower = log_line.lower()
        if any(level in log_line_lower for level in ['error', 'failed', 'exception']):
            return 'error'
        elif any(level in log_line_lower for level in ['warning', 'warn']):
            return 'warning'
        elif any(level in log_line_lower for level in ['info', 'information']):
            return 'info'
        else:
            return 'debug'
