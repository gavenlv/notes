#!/usr/bin/env python3
"""
Soda Core Data Quality Startup Application
Monitors PostgreSQL and ClickHouse databases for data quality issues
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from soda.scan import Scan
from clickhouse_checker import ClickHouseDataQualityChecker


class DataQualityApp:
    """Main application class for data quality monitoring"""
    
    def __init__(self):
        """Initialize the application"""
        # Get the project root directory (parent of src)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Load environment variables
        env_path = os.path.join(project_root, 'config', 'environment.env')
        load_dotenv(env_path)
        
        # Setup logging
        self.setup_logging(project_root)
        
        # Configuration
        self.config_path = Path(project_root) / 'config' / 'configuration.yml'
        self.checks_path = Path(project_root) / 'config' / 'checks'
        self.reports_path = Path(project_root) / 'reports'
        
        # Ensure reports directory exists
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Data Quality App initialized")
    
    def setup_logging(self, project_root):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path(project_root) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'data_quality.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def validate_environment(self) -> bool:
        """Validate that all required environment variables are set"""
        required_vars = [
            'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DATABASE',
            'POSTGRES_USERNAME', 'POSTGRES_PASSWORD',
            'CLICKHOUSE_HOST', 'CLICKHOUSE_PORT', 'CLICKHOUSE_DATABASE',
            'CLICKHOUSE_USERNAME', 'CLICKHOUSE_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        return True
    
    def run_data_source_scan(self, data_source: str, checks_file: Optional[str] = None) -> Dict:
        """Run data quality scan for a specific data source"""
        self.logger.info(f"Starting scan for data source: {data_source}")
        
        try:
            # Create scan object
            scan = Scan()
            
            # Set configuration
            scan.set_data_source_name(data_source)
            scan.add_configuration_yaml_file(str(self.config_path))
            
            # Add checks
            if checks_file:
                checks_path = os.path.join(self.checks_path, checks_file)
                if os.path.exists(checks_path):
                    scan.add_sodacl_yaml_file(checks_path)
                    self.logger.info(f"Added checks from: {checks_path}")
                else:
                    self.logger.warning(f"Checks file not found: {checks_path}")
            else:
                # Add all YAML files in checks directory
                checks_dir = self.checks_path
                for check_file in checks_dir.glob("*.yml"):
                    scan.add_sodacl_yaml_file(str(check_file))
                    self.logger.info(f"Added checks from: {check_file}")
            
            # Execute scan
            result = scan.execute()
            
            # Process results
            scan_results_dict = scan.get_scan_results()
            
            scan_result = {
                'data_source': data_source,
                'timestamp': datetime.now().isoformat(),
                'scan_result': result,
                'checks_passed': scan_results_dict.get('checks_passed', 0) if scan_results_dict else 0,
                'checks_failed': scan_results_dict.get('checks_failed', 0) if scan_results_dict else 0,
                'checks_warned': scan_results_dict.get('checks_warned', 0) if scan_results_dict else 0,
                'logs': scan.get_logs_text()
            }
            
            self.logger.info(f"Scan completed for {data_source}. "
                           f"Passed: {scan_result['checks_passed']}, "
                           f"Failed: {scan_result['checks_failed']}, "
                           f"Warned: {scan_result['checks_warned']}")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Error running scan for {data_source}: {str(e)}")
            return {
                'data_source': data_source,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'scan_result': 1  # Error code
            }
    
    def save_report(self, results: List[Dict], report_name: str = None):
        """Save scan results to a JSON report file"""
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"data_quality_report_{timestamp}.json"
        
        report_path = os.path.join(self.reports_path, report_name)
        
        try:
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Report saved to: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
    
    def run_all_checks(self) -> List[Dict]:
        """Run data quality checks for all configured data sources"""
        self.logger.info("Starting comprehensive data quality checks")
        
        if not self.validate_environment():
            self.logger.error("Environment validation failed")
            return []
        
        results = []
        
        # Check PostgreSQL
        postgres_result = self.run_data_source_scan('postgresql', 'postgresql_checks.yml')
        results.append(postgres_result)
        
        # Check ClickHouse using custom checker
        clickhouse_checker = ClickHouseDataQualityChecker()
        clickhouse_result = clickhouse_checker.run_all_checks()
        results.append(clickhouse_result)
        
        # Save combined report
        self.save_report(results)
        
        return results
    
    def print_summary(self, results: List[Dict]):
        """Print a summary of the scan results"""
        print("\n" + "="*60)
        print("DATA QUALITY SCAN SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        total_warned = 0
        
        for result in results:
            data_source = result.get('data_source', 'Unknown')
            passed = result.get('checks_passed', 0)
            failed = result.get('checks_failed', 0)
            warned = result.get('checks_warned', 0)
            
            total_passed += passed
            total_failed += failed
            total_warned += warned
            
            status = "✅ HEALTHY" if failed == 0 else "❌ ISSUES FOUND"
            
            print(f"\n{data_source.upper()}:")
            print(f"  Status: {status}")
            print(f"  Checks Passed: {passed}")
            print(f"  Checks Failed: {failed}")
            print(f"  Checks Warned: {warned}")
            
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Total Checks Passed: {total_passed}")
        print(f"  Total Checks Failed: {total_failed}")
        print(f"  Total Checks Warned: {total_warned}")
        
        overall_status = "✅ ALL SYSTEMS HEALTHY" if total_failed == 0 else "⚠️  ATTENTION REQUIRED"
        print(f"  Overall Status: {overall_status}")
        print("="*60)


def main():
    """Main entry point"""
    print("🚀 Starting Data Quality Monitoring App")
    print("Monitoring PostgreSQL and ClickHouse databases...")
    
    app = DataQualityApp()
    
    try:
        # Run all checks
        results = app.run_all_checks()
        
        # Print summary
        app.print_summary(results)
        
        # Exit with appropriate code
        total_failed = sum(r.get('checks_failed', 0) for r in results)
        exit_code = 0 if total_failed == 0 else 1
        
        print(f"\nExiting with code: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️  Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        logging.getLogger(__name__).exception("Unexpected error in main")
        sys.exit(1)


if __name__ == "__main__":
    main()
