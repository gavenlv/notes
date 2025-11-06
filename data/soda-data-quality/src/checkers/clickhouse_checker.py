"""
ClickHouse data quality checker following Strategy pattern
"""

from typing import Dict, List, Any
from ..core.interfaces import IDatabaseConnection, ILogger
from ..core.database_connections import ClickHouseConnection
from .base_checker import BaseDataQualityChecker


class ClickHouseDataQualityChecker(BaseDataQualityChecker):
    """ClickHouse-specific data quality checker"""
    
    def __init__(self, 
                 database_connection: ClickHouseConnection,
                 logger: ILogger):
        super().__init__(database_connection, logger, 'clickhouse')
        self._client = database_connection.get_client()
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all ClickHouse data quality checks"""
        self._logger.info("Starting ClickHouse data quality checks")
        
        scan_id = self._generate_scan_id()
        scan_timestamp = self._get_scan_timestamp()
        
        checks = []
        
        # Check 1: Table exists
        checks.extend(self._check_table_exists())
        
        # Check 2: Data freshness
        checks.extend(self._check_data_freshness())
        
        # Check 3: Data completeness
        checks.extend(self._check_data_completeness())
        
        # Create result
        result = self._create_scan_result(scan_id, checks, scan_timestamp)
        
        # Log summary
        self._log_scan_summary(result)
        
        return result
    
    def _check_table_exists(self) -> List[Dict[str, Any]]:
        """Check if required tables exist"""
        checks = []
        required_tables = ['users', 'orders', 'products']
        
        for table in required_tables:
            try:
                result = self._client.query(f"EXISTS TABLE {table}")
                exists = result.result_rows[0][0]
                
                checks.append({
                    'name': f'Table {table} exists',
                    'table_name': table,
                    'result': 'PASSED' if exists else 'FAILED',
                    'details': f'Table {table} {"exists" if exists else "does not exist"}'
                })
            except Exception as e:
                checks.append({
                    'name': f'Table {table} exists',
                    'table_name': table,
                    'result': 'FAILED',
                    'details': f'Error checking table existence: {str(e)}'
                })
        
        return checks
    
    def _check_data_freshness(self) -> List[Dict[str, Any]]:
        """Check data freshness (example: recent data exists)"""
        checks = []
        
        try:
            # Check if there's data from the last 7 days
            result = self._client.query("""
                SELECT COUNT(*) as recent_count
                FROM users 
                WHERE created_at >= now() - INTERVAL 7 DAY
            """)
            recent_count = result.result_rows[0][0]
            
            checks.append({
                'name': 'Recent data exists (last 7 days)',
                'table_name': 'users',
                'result': 'PASSED' if recent_count > 0 else 'WARNED',
                'details': f'Found {recent_count} records from last 7 days'
            })
        except Exception as e:
            checks.append({
                'name': 'Recent data exists (last 7 days)',
                'table_name': 'users',
                'result': 'FAILED',
                'details': f'Error checking data freshness: {str(e)}'
            })
        
        return checks
    
    def _check_data_completeness(self) -> List[Dict[str, Any]]:
        """Check data completeness"""
        checks = []
        
        try:
            # Check for null values in critical columns
            result = self._client.query("""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(name) as non_null_names,
                    COUNT(email) as non_null_emails
                FROM users
            """)
            
            row = result.result_rows[0]
            total_rows = row[0]
            non_null_names = row[1]
            non_null_emails = row[2]
            
            # Check name completeness
            name_completeness = (non_null_names / total_rows * 100) if total_rows > 0 else 0
            checks.append({
                'name': 'Name field completeness',
                'table_name': 'users',
                'result': 'PASSED' if name_completeness >= 95 else 'FAILED',
                'details': f'Name completeness: {name_completeness:.1f}%'
            })
            
            # Check email completeness
            email_completeness = (non_null_emails / total_rows * 100) if total_rows > 0 else 0
            checks.append({
                'name': 'Email field completeness',
                'table_name': 'users',
                'result': 'PASSED' if email_completeness >= 95 else 'FAILED',
                'details': f'Email completeness: {email_completeness:.1f}%'
            })
            
        except Exception as e:
            checks.append({
                'name': 'Data completeness check',
                'table_name': 'users',
                'result': 'FAILED',
                'details': f'Error checking data completeness: {str(e)}'
            })
        
        return checks
