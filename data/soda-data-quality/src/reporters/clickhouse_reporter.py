"""
ClickHouse reporter implementation following Observer pattern
"""

from typing import Dict, List, Any
from core.interfaces import IDatabaseConnection, ILogger
from core.database_connections import ClickHouseDQConnection
from .base_reporter import BaseDataQualityReporter


class ClickHouseDataQualityReporter(BaseDataQualityReporter):
    """ClickHouse-specific data quality reporter"""
    
    def __init__(self, 
                 database_connection: ClickHouseDQConnection,
                 logger: ILogger,
                 environment: str = 'production'):
        super().__init__(database_connection, logger, 'clickhouse')
        self._client = database_connection.get_client()
        self._environment = environment
    
    def store_scan_results(self, results: List[Dict[str, Any]]) -> None:
        """Store scan results in ClickHouse"""
        try:
            self._logger.info("Storing scan results in ClickHouse")
            
            for result in results:
                scan_id = result.get('scan_id', self._generate_id())
                scan_timestamp = result.get('scan_timestamp', self._get_current_timestamp())
                
                # Store main scan record
                self._store_scan(scan_id, result, scan_timestamp)
                
                # Store individual checks
                checks = result.get('checks', [])
                if checks:
                    self._store_checks(scan_id, result['data_source'], checks, scan_timestamp)
                
                # Store logs if available
                logs = result.get('logs', '')
                if logs:
                    self._store_logs(scan_id, result['data_source'], logs, scan_timestamp)
                
                # Calculate and store metrics
                self._store_metrics(scan_id, result, scan_timestamp)
            
            self._logger.info(f"Successfully stored scan results with ID: {scan_id}")
            
        except Exception as e:
            self._logger.error(f"Error storing scan results: {str(e)}")
            raise
    
    def _store_scan(self, scan_id: str, result: Dict[str, Any], scan_timestamp) -> None:
        """Store main scan result"""
        try:
            total_checks = len(result.get('checks', []))
            scan_data = {
                'scan_id': scan_id,
                'data_source': result['data_source'],
                'scan_timestamp': scan_timestamp,
                'total_checks': total_checks,
                'checks_passed': result.get('checks_passed', 0),
                'checks_failed': result.get('checks_failed', 0),
                'checks_warned': result.get('checks_warned', 0),
                'scan_result': result.get('scan_result', 0),
                'scan_duration_ms': 0,  # TODO: Add actual duration tracking
                'environment': self._environment
            }
            
            self._logger.info(f"Inserting scan data: {scan_data}")
            columns = [
                'scan_id', 'data_source', 'scan_timestamp',
                'total_checks', 'checks_passed', 'checks_failed', 'checks_warned',
                'scan_result', 'scan_duration_ms', 'environment'
            ]
            # Convert dict to list of values in column order
            scan_values = [scan_data[col] for col in columns]
            self._client.insert('data_quality_scans', [scan_values], column_names=columns)
            self._logger.debug(f"Stored scan data for source: {result['data_source']}")
            
        except Exception as e:
            self._logger.error(f"Error storing scan data: {str(e)}")
            raise
    
    def _store_checks(self, scan_id: str, data_source: str, checks: List[Dict[str, Any]], scan_timestamp) -> None:
        """Store individual check results"""
        try:
            check_records = []
            for check in checks:
                check_id = self._generate_id()
                check_record = {
                    'check_id': check_id,
                    'scan_id': scan_id,
                    'data_source': data_source,
                    'table_name': check.get('table_name', ''),
                    'check_name': check['name'],
                    'check_type': self._determine_check_type(check['name']),
                    'check_result': check['result'].upper(),
                    'check_value': self._extract_numeric_value(check.get('details', '')),
                    'expected_value': None,  # TODO: Extract from check configuration
                    'threshold_value': None,  # TODO: Extract from check configuration
                    'check_details': check.get('details', ''),
                    'check_category': 'general',
                    'severity': self._determine_severity(check['name']).upper(),
                    'scan_timestamp': scan_timestamp
                }
                check_records.append(check_record)
            
            if check_records:
                columns = [
                    'check_id', 'scan_id', 'data_source', 'table_name', 'check_name',
                    'check_type', 'check_result', 'check_value', 'expected_value',
                    'threshold_value', 'check_details', 'check_category', 'severity',
                    'scan_timestamp'
                ]
                # Convert list of dicts to list of lists
                check_values = [[record[col] for col in columns] for record in check_records]
                self._client.insert('data_quality_checks', check_values, column_names=columns)
                self._logger.debug(f"Stored {len(check_records)} check results")
                
        except Exception as e:
            self._logger.error(f"Error storing check results: {str(e)}")
            raise
    
    def _store_logs(self, scan_id: str, data_source: str, logs: str, scan_timestamp) -> None:
        """Store scan logs"""
        try:
            # Parse and store individual log entries
            log_entries = []
            for line in logs.split('\n'):
                if line.strip():
                    log_level = self._determine_log_level(line)
                    log_entries.append({
                        'log_id': self._generate_id(),
                        'scan_id': scan_id,
                        'data_source': data_source,
                        'log_level': log_level.upper(),
                        'log_message': line.strip(),
                        'log_details': '',
                        'scan_timestamp': scan_timestamp
                    })
            
            if log_entries:
                columns = [
                    'log_id', 'scan_id', 'data_source', 'log_level', 'log_message',
                    'log_details', 'scan_timestamp'
                ]
                # Convert list of dicts to list of lists
                log_values = [[entry[col] for col in columns] for entry in log_entries]
                self._client.insert('data_quality_logs', log_values, column_names=columns)
                self._logger.debug(f"Stored {len(log_entries)} log entries")
                
        except Exception as e:
            self._logger.error(f"Error storing logs: {str(e)}")
            raise
    
    def _store_metrics(self, scan_id: str, result: Dict[str, Any], scan_timestamp) -> None:
        """Calculate and store metrics from scan results"""
        try:
            metrics = []
            data_source = result['data_source']
            total_checks = len(result.get('checks', []))
            
            if total_checks > 0:
                # Calculate pass rate
                pass_rate = (result.get('checks_passed', 0) / total_checks) * 100
                metrics.append({
                    'metric_id': self._generate_id(),
                    'data_source': data_source,
                    'table_name': '',  # Overall metric
                    'metric_name': 'pass_rate',
                    'metric_value': pass_rate,
                    'metric_unit': 'percentage',
                    'metric_category': 'quality',
                    'scan_timestamp': scan_timestamp
                })
            
            # Store metrics
            if metrics:
                columns = [
                    'metric_id', 'data_source', 'table_name', 'metric_name',
                    'metric_value', 'metric_unit', 'metric_category', 'scan_timestamp'
                ]
                # Convert list of dicts to list of lists
                metric_values = [[metric[col] for col in columns] for metric in metrics]
                self._client.insert('data_quality_metrics', metric_values, column_names=columns)
                self._logger.debug(f"Stored {len(metrics)} metrics")
                
        except Exception as e:
            self._logger.error(f"Error storing metrics: {str(e)}")
            raise
