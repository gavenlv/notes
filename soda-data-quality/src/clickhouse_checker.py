#!/usr/bin/env python3
"""
Custom ClickHouse Data Quality Checker
Since Soda Core doesn't have a ClickHouse module, we'll create our own
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import clickhouse_connect
from dotenv import load_dotenv
from pathlib import Path
import sys

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, 'config', 'environment.env')
load_dotenv(env_path)

# Setup logging for clickhouse_checker
log_dir = Path(project_root) / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / 'clickhouse_checker.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class ClickHouseDataQualityChecker:
    """Custom ClickHouse data quality checker"""
    
    def __init__(self):
        """Initialize the ClickHouse checker"""
        # clickhouse_connect uses HTTP port (default 8123) instead of native protocol port (9000)
        # Check if CLICKHOUSE_HTTP_PORT is set, otherwise convert native port to HTTP port
        if os.getenv('CLICKHOUSE_HTTP_PORT'):
            ch_port = int(os.getenv('CLICKHOUSE_HTTP_PORT'))
        else:
            # If native protocol port is 9000, HTTP port is likely 8123
            native_port = int(os.getenv('CLICKHOUSE_PORT', 9000))
            ch_port = 8123 if native_port == 9000 else native_port
            
        logger.info(f"Connecting to ClickHouse HTTP port: {ch_port}")
        
        self.client = clickhouse_connect.get_client(
            host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
            port=ch_port,
            username=os.getenv('CLICKHOUSE_USERNAME', 'admin'),
            password=os.getenv('CLICKHOUSE_PASSWORD', 'admin'),
            database=os.getenv('CLICKHOUSE_DATABASE', 'default')
        )
        
        logger.info("ClickHouse Data Quality Checker initialized")
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            result = self.client.query(
                "SELECT count() FROM system.tables WHERE database = currentDatabase() AND name = %(table)s",
                parameters={'table': table_name}
            )
            return result.first_row[0] > 0
        except Exception as e:
            logger.error(f"Error checking if table {table_name} exists: {e}")
            return False
    
    def run_table_checks(self, table_name: str) -> List[Dict[str, Any]]:
        """Run data quality checks for a specific table"""
        checks = []
        
        if not self.check_table_exists(table_name):
            checks.append({
                'name': f'Table {table_name} exists',
                'result': 'FAIL',
                'details': f'Table {table_name} does not exist'
            })
            return checks
        
        # Row count check
        try:
            result = self.client.query(f"SELECT count() FROM {table_name}")
            row_count = result.first_row[0]
            checks.append({
                'name': f'{table_name} has data',
                'result': 'PASS' if row_count > 0 else 'FAIL',
                'details': f'Found {row_count} rows'
            })
        except Exception as e:
            checks.append({
                'name': f'{table_name} has data',
                'result': 'FAIL',
                'details': f'Error: {str(e)}'
            })
        
        # Column-specific checks based on table
        if table_name == 'events':
            checks.extend(self._check_events_table())
        elif table_name == 'metrics':
            checks.extend(self._check_metrics_table())
        
        return checks
    
    def _check_events_table(self) -> List[Dict[str, Any]]:
        """Check events table specific quality issues"""
        checks = []
        
        # Missing event_type
        try:
            result = self.client.query("SELECT count() FROM events WHERE event_name IS NULL OR event_name = ''")
            missing_count = result.first_row[0]
            checks.append({
                'name': 'No missing event types',
                'result': 'PASS' if missing_count == 0 else 'FAIL',
                'details': f'Found {missing_count} events with missing event_type'
            })
        except Exception as e:
            checks.append({
                'name': 'No missing event types',
                'result': 'FAIL',
                'details': f'Error: {str(e)}'
            })
        
        # Missing user_id
        try:
            result = self.client.query("SELECT count() FROM events WHERE user_id IS NULL OR user_id = 0")
            missing_count = result.first_row[0]
            checks.append({
                'name': 'No missing user IDs',
                'result': 'PASS' if missing_count == 0 else 'FAIL',
                'details': f'Found {missing_count} events with missing user_id'
            })
        except Exception as e:
            checks.append({
                'name': 'No missing user IDs',
                'result': 'FAIL',
                'details': f'Error: {str(e)}'
            })
        
        # Removed 'No duplicate event IDs' check as session_id is not a unique event identifier
        # try:
        #     result = self.client.execute("""
        #         SELECT count() FROM (
        #             SELECT session_id, count() as cnt 
        #             FROM events 
        #             GROUP BY session_id 
        #             HAVING cnt > 1
        #         )
        #     """)
        #     duplicate_count = result[0][0]
        #     checks.append({
        #         'name': 'No duplicate event IDs',
        #         'result': 'PASS' if duplicate_count == 0 else 'FAIL',
        #         'details': f'Found {duplicate_count} duplicate event_ids'
        #     })
        # except Exception as e:
        #     checks.append({
        #         'name': 'No duplicate event IDs',
        #         'result': 'FAIL',
        #         'details': f'Error: {str(e)}'
        #     })
        
        # Future timestamps
        try:
            result = self.client.query("SELECT count() FROM events WHERE event_time > now()")
            future_count = result.first_row[0]
            checks.append({
                'name': 'No future timestamps',
                'result': 'PASS' if future_count == 0 else 'FAIL',
                'details': f'Found {future_count} events with future timestamps'
            })
        except Exception as e:
            checks.append({
                'name': 'No future timestamps',
                'result': 'FAIL',
                'details': f'Error: {str(e)}'
            })
        
        # Valid event types
        try:
            result = self.client.query("""
                SELECT count() FROM events 
                WHERE event_name NOT IN ('page_view', 'click', 'purchase', 'login', 'signup', 'view')
            """)
            invalid_count = result.first_row[0]
            checks.append({
                'name': 'Valid event types',
                'result': 'PASS' if invalid_count == 0 else 'FAIL',
                'details': f'Found {invalid_count} events with invalid types'
            })
        except Exception as e:
            checks.append({
                'name': 'Valid event types',
                'result': 'FAIL',
                'details': f'Error: {str(e)}'
            })
        
        return checks
    
    def _check_metrics_table(self) -> List[Dict[str, Any]]:
        """Check metrics table specific quality issues"""
        checks = []
        # No metrics table exists, so no checks will be run for it.
        return checks
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all ClickHouse data quality checks"""
        logger.info("Starting ClickHouse data quality checks")
        
        all_checks = []
        
        # Check events table
        events_checks = self.run_table_checks('events')
        all_checks.extend(events_checks)
        
        # Removed metrics table checks as it does not exist
        # metrics_checks = self.run_table_checks('metrics')
        # all_checks.extend(metrics_checks)
        
        # Calculate summary
        passed = sum(1 for check in all_checks if check['result'] == 'PASS')
        failed = sum(1 for check in all_checks if check['result'] == 'FAIL')
        
        result = {
            'data_source': 'clickhouse',
            'timestamp': datetime.now().isoformat(),
            'checks_passed': passed,
            'checks_failed': failed,
            'checks_warned': 0,
            'checks': all_checks
        }
        
        logger.info(f"ClickHouse checks completed. Passed: {passed}, Failed: {failed}")
        return result

def main():
    """Main function for testing"""
    checker = ClickHouseDataQualityChecker()
    result = checker.run_all_checks()
    
    print("\n" + "="*60)
    print("CLICKHOUSE DATA QUALITY CHECK RESULTS")
    print("="*60)
    print(f"Timestamp: {result['timestamp']}")
    print(f"Total Checks: {len(result['checks'])}")
    print(f"Passed: {result['checks_passed']}")
    print(f"Failed: {result['checks_failed']}")
    print("-"*60)
    
    for i, check in enumerate(result['checks'], 1):
        status_icon = "✅" if check['result'] == 'PASS' else "❌"
        print(f"{i:2d}. {status_icon} {check['name']}")
        print(f"    Result: {check['result']}")
        print(f"    Details: {check['details']}")
        print()
    
    overall_status = "✅ HEALTHY" if result['checks_failed'] == 0 else "⚠️  ISSUES FOUND"
    print(f"Overall Status: {overall_status}")
    print("="*60)

if __name__ == "__main__":
    main()
