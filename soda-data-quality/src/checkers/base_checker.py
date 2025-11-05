"""
Base checker implementation following Strategy pattern
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any
from abc import ABC

from ..core.interfaces import IDataQualityChecker, IDatabaseConnection, ILogger


class BaseDataQualityChecker(IDataQualityChecker, ABC):
    """Base implementation for data quality checkers"""
    
    def __init__(self, 
                 database_connection: IDatabaseConnection,
                 logger: ILogger,
                 data_source_name: str):
        self._db_connection = database_connection
        self._logger = logger
        self._data_source_name = data_source_name
    
    def get_data_source_name(self) -> str:
        """Get the name of the data source"""
        return self._data_source_name
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID"""
        return str(uuid.uuid4())
    
    def _get_scan_timestamp(self) -> datetime:
        """Get current timestamp"""
        return datetime.now()
    
    def _create_scan_result(self, 
                           scan_id: str, 
                           checks: List[Dict[str, Any]], 
                           scan_timestamp: datetime) -> Dict[str, Any]:
        """Create standardized scan result"""
        total_checks = len(checks)
        checks_passed = sum(1 for check in checks if check.get('result', '').upper() == 'PASSED')
        checks_failed = sum(1 for check in checks if check.get('result', '').upper() == 'FAILED')
        checks_warned = sum(1 for check in checks if check.get('result', '').upper() == 'WARNED')
        
        # Determine overall scan result
        if checks_failed > 0:
            scan_result = 0  # Failed
        elif checks_warned > 0:
            scan_result = 1  # Warning
        else:
            scan_result = 2  # Passed
        
        return {
            'scan_id': scan_id,
            'data_source': self._data_source_name,
            'scan_timestamp': scan_timestamp,
            'total_checks': total_checks,
            'checks_passed': checks_passed,
            'checks_failed': checks_failed,
            'checks_warned': checks_warned,
            'scan_result': scan_result,
            'checks': checks
        }
    
    def _log_scan_summary(self, result: Dict[str, Any]) -> None:
        """Log scan summary"""
        self._logger.info(f"Scan completed for {self._data_source_name}")
        self._logger.info(f"  Total checks: {result['total_checks']}")
        self._logger.info(f"  Passed: {result['checks_passed']}")
        self._logger.info(f"  Failed: {result['checks_failed']}")
        self._logger.info(f"  Warned: {result['checks_warned']}")
        
        if result['checks_failed'] > 0:
            self._logger.warning(f"  Status: ❌ ISSUES FOUND")
        elif result['checks_warned'] > 0:
            self._logger.warning(f"  Status: ⚠️  WARNINGS")
        else:
            self._logger.info(f"  Status: ✅ HEALTHY")
