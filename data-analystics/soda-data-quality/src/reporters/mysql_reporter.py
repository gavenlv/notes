"""
MySQL data quality reporter following Observer pattern
"""

from typing import Dict, List, Any
from ..core.interfaces import IDataQualityReporter, IDatabaseConnection, ILogger
from .base_reporter import BaseDataQualityReporter
from ..core.mysql_connection import MySQLConnection


class MySQLDataQualityReporter(BaseDataQualityReporter):
    """MySQL-specific data quality reporter"""
    
    def __init__(self, 
                 database_connection: MySQLConnection,
                 logger: ILogger):
        super().__init__(database_connection, logger, 'mysql')
        self._connection = database_connection.get_connection()
    
    def store_scan_results(self, scan_result: Dict[str, Any]) -> bool:
        """Store scan results to MySQL database"""
        try:
            self._logger.info("Storing MySQL scan results")
            
            # Store scan summary
            self._store_scan(scan_result)
            
            # Store individual checks
            self._store_checks(scan_result.get('checks', []))
            
            # Store logs
            self._store_logs(scan_result.get('logs', []))
            
            # Store metrics
            self._store_metrics(scan_result.get('metrics', {}))
            
            self._connection.commit()
            self._logger.info("Successfully stored MySQL scan results")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to store MySQL scan results: {str(e)}")
            self._connection.rollback()
            return False
    
    def _store_scan(self, scan_result: Dict[str, Any]) -> None:
        """Store scan summary information"""
        cursor = self._connection.cursor()
        try:
            query = """
            INSERT INTO data_quality_scans 
            (scan_id, data_source, start_time, end_time, status, total_checks, passed_checks, failed_checks, warning_checks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                scan_result.get('scan_id'),
                scan_result.get('data_source'),
                scan_result.get('start_time'),
                scan_result.get('end_time'),
                scan_result.get('status'),
                scan_result.get('total_checks', 0),
                scan_result.get('passed_checks', 0),
                scan_result.get('failed_checks', 0),
                scan_result.get('warning_checks', 0)
            )
            
            cursor.execute(query, values)
        finally:
            cursor.close()
    
    def _store_checks(self, checks: List[Dict[str, Any]]) -> None:
        """Store individual check results"""
        cursor = self._connection.cursor()
        try:
            query = """
            INSERT INTO data_quality_checks 
            (scan_id, check_name, table_name, result, details, severity, check_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for check in checks:
                values = (
                    check.get('scan_id'),
                    check.get('name'),
                    check.get('table_name'),
                    check.get('result'),
                    check.get('details'),
                    self._determine_severity(check.get('result')),
                    self._determine_check_type(check.get('name'))
                )
                cursor.execute(query, values)
        finally:
            cursor.close()
    
    def _store_logs(self, logs: List[Dict[str, Any]]) -> None:
        """Store log entries"""
        cursor = self._connection.cursor()
        try:
            query = """
            INSERT INTO data_quality_logs 
            (scan_id, timestamp, level, message, module)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for log in logs:
                values = (
                    log.get('scan_id'),
                    log.get('timestamp'),
                    log.get('level'),
                    log.get('message'),
                    log.get('module')
                )
                cursor.execute(query, values)
        finally:
            cursor.close()
    
    def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store metrics data"""
        cursor = self._connection.cursor()
        try:
            query = """
            INSERT INTO data_quality_metrics 
            (scan_id, metric_name, value, unit, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for metric_name, metric_value in metrics.items():
                values = (
                    metrics.get('scan_id'),
                    metric_name,
                    metric_value,
                    metrics.get('unit', ''),
                    metrics.get('timestamp')
                )
                cursor.execute(query, values)
        finally:
            cursor.close()