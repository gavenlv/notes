"""
Test script for MySQL reporter functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.configuration import EnvironmentConfigurationManager
from core.database_connections import DatabaseConnectionFactory
from core.logging import LoggerFactory
from reporters.mysql_reporter import MySQLDataQualityReporter


def test_mysql_reporter():
    """Test MySQL reporter functionality"""
    try:
        # Create configuration manager
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / 'config' / 'environment.env'
        config_manager = EnvironmentConfigurationManager(str(env_file))
        
        # Create MySQL connection
        mysql_connection = DatabaseConnectionFactory.create_mysql_connection(config_manager)
        
        # Test connection
        if mysql_connection.connect():
            print("✓ MySQL connection successful")
            
            # Get connection info
            conn_info = mysql_connection.get_connection_info()
            print(f"  Connection info: {conn_info}")
            
            # Create logger
            logger = LoggerFactory.create_module_logger('mysql_reporter_test')
            
            # Create reporter
            reporter = MySQLDataQualityReporter(mysql_connection, logger)
            print("✓ MySQL reporter created successfully")
            
            # Create test scan result
            test_result = {
                'scan_id': 'test-scan-123',
                'data_source': 'mysql',
                'start_time': '2023-01-01 10:00:00',
                'end_time': '2023-01-01 10:05:00',
                'status': 'completed',
                'total_checks': 3,
                'passed_checks': 2,
                'failed_checks': 1,
                'warning_checks': 0,
                'checks': [
                    {
                        'scan_id': 'test-scan-123',
                        'name': 'Table users exists',
                        'table_name': 'users',
                        'result': 'PASSED',
                        'details': 'Table users exists'
                    },
                    {
                        'scan_id': 'test-scan-123',
                        'name': 'Recent data exists (last 7 days)',
                        'table_name': 'users',
                        'result': 'PASSED',
                        'details': 'Found 150 records from last 7 days'
                    },
                    {
                        'scan_id': 'test-scan-123',
                        'name': 'Name field completeness',
                        'table_name': 'users',
                        'result': 'FAILED',
                        'details': 'Name completeness: 85.0%'
                    }
                ],
                'logs': [
                    {
                        'scan_id': 'test-scan-123',
                        'timestamp': '2023-01-01 10:00:00',
                        'level': 'INFO',
                        'message': 'Starting MySQL data quality checks',
                        'module': 'mysql_checker'
                    },
                    {
                        'scan_id': 'test-scan-123',
                        'timestamp': '2023-01-01 10:05:00',
                        'level': 'INFO',
                        'message': 'MySQL data quality checks completed',
                        'module': 'mysql_checker'
                    }
                ],
                'metrics': {
                    'scan_id': 'test-scan-123',
                    'total_records': 1000,
                    'completeness_rate': 95.5,
                    'unit': '%',
                    'timestamp': '2023-01-01 10:05:00'
                }
            }
            
            # Test storing results
            success = reporter.store_scan_results(test_result)
            if success:
                print("✓ MySQL reporter stored scan results successfully")
            else:
                print("✗ MySQL reporter failed to store scan results")
                return False
            
            # Check connection status
            if mysql_connection.is_connected():
                print("✓ MySQL connection is still active")
            else:
                print("✗ MySQL connection is not active")
                return False
            
            # Disconnect
            mysql_connection.disconnect()
            print("✓ MySQL connection closed")
            
            return True
        else:
            print("✗ MySQL connection failed")
            return False
            
    except Exception as e:
        print(f"✗ Error testing MySQL reporter: {str(e)}")
        return False


def main():
    """Main test function"""
    print("Testing MySQL reporter functionality...")
    
    success = test_mysql_reporter()
    
    if success:
        print("\n✓ All MySQL reporter tests passed!")
        return 0
    else:
        print("\n✗ MySQL reporter tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())