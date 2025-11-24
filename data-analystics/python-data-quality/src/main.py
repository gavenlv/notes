"""
Main Application Entry Point for Data Quality Framework
Orchestrates the entire framework with CLI interface.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from database_adapter import DatabaseAdapter, DatabaseConnectionPool
from rule_engine import RuleEngine
from report_generator import ReportManager


class DataQualityFramework:
    """Main framework class that orchestrates data quality checks."""
    
    def __init__(self, config_dir: str = "config", rules_file: str = "rules.yml"):
        """Initialize the data quality framework.
        
        Args:
            config_dir: Configuration directory
            rules_file: Rules configuration file
        """
        self.config_dir = Path(config_dir)
        self.rules_file = self.config_dir / rules_file
        
        # Initialize components
        self.config_manager = ConfigManager(
            env_file=self.config_dir / "environment.env",
            config_file=self.rules_file
        )
        
        self.rule_engine = RuleEngine(self.rules_file)
        self.report_manager = ReportManager()
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config_manager.get_framework_config().get('log_level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('data_quality.log')
            ]
        )
    
    def validate_configuration(self) -> bool:
        """Validate framework configuration.
        
        Returns:
            True if configuration is valid
        """
        # Validate environment configuration
        if not self.config_manager.validate_config():
            self.logger.error("Environment configuration validation failed")
            return False
        
        # Validate rules
        invalid_rules = self.rule_engine.validate_all_rules()
        if invalid_rules:
            self.logger.warning(f"Found {len(invalid_rules)} invalid rules: {invalid_rules}")
        
        self.logger.info("Configuration validation completed")
        return True
    
    def run_checks(self, rule_names: Optional[List[str]] = None, 
                   parallel: bool = True, check_type: str = 'all') -> List[dict]:
        """Execute data quality checks.
        
        Args:
            rule_names: Specific rules to execute (None for all)
            parallel: Whether to use parallel execution
            check_type: Specific type of checks to run
            
        Returns:
            List of check results
        """
        self.logger.info("Starting data quality checks")
        
        # Get database configuration
        db_config = self.config_manager.get_database_config()
        
        # Execute checks
        if parallel:
            results = self._run_checks_parallel(db_config, rule_names, check_type)
        else:
            results = self._run_checks_sequential(db_config, rule_names, check_type)
        
        self.logger.info(f"Completed {len(results)} data quality checks")
        return results
    
    def _run_checks_sequential(self, db_config: dict, rule_names: Optional[List[str]] = None) -> List[dict]:
        """Execute checks sequentially.
        
        Args:
            db_config: Database configuration
            rule_names: Specific rules to execute
            
        Returns:
            List of check results
        """
        results = []
        
        with DatabaseAdapter(db_config) as database:
            if database.connect():
                results = self.rule_engine.execute_rules(database, rule_names)
            else:
                self.logger.error("Failed to establish database connection")
        
        return results
    
    def _run_checks_parallel(self, db_config: dict, rule_names: Optional[List[str]] = None) -> List[dict]:
        """Execute checks in parallel using connection pool.
        
        Args:
            db_config: Database configuration
            rule_names: Specific rules to execute
            
        Returns:
            List of check results
        """
        # For now, use sequential execution
        # Parallel execution would require more complex implementation
        # with threading/multiprocessing
        return self._run_checks_sequential(db_config, rule_names)
    
    def generate_reports(self, results: List[dict], formats: List[str] = None) -> dict:
        """Generate reports from check results.
        
        Args:
            results: Check results
            formats: Report formats to generate
            
        Returns:
            Dictionary of generated report paths
        """
        if formats is None:
            formats = ['html', 'json']
        
        self.logger.info(f"Generating reports in formats: {formats}")
        
        report_paths = self.report_manager.generate_reports(results, formats)
        
        for fmt, path in report_paths.items():
            self.logger.info(f"Generated {fmt} report: {path}")
        
        return report_paths
    
    def run_full_pipeline(self, rule_names: Optional[List[str]] = None, 
                         check_type: str = 'all', generate_report_only: bool = False) -> dict:
        """Run the complete data quality pipeline.
        
        Args:
            rule_names: Specific rules to execute
            check_type: Specific type of checks to run
            generate_report_only: Whether to skip actual checks and only generate reports
            
        Returns:
            Pipeline execution results
        """
        self.logger.info("Starting full data quality pipeline")
        
        # Step 1: Validate configuration
        if not self.validate_configuration():
            return {'success': False, 'error': 'Configuration validation failed'}
        
        # Step 2: Execute checks (unless in report-only mode)
        if generate_report_only:
            self.logger.info("Generate report only mode - skipping actual checks")
            results = []
        else:
            try:
                results = self.run_checks(rule_names, check_type=check_type)
            except Exception as e:
                self.logger.error(f"Error during checks execution: {e}")
                return {'success': False, 'error': str(e)}
        
        # Step 3: Generate reports
        try:
            report_paths = self.generate_reports(results)
        except Exception as e:
            self.logger.error(f"Error during report generation: {e}")
            return {'success': False, 'error': str(e), 'results': results}
        
        # Step 4: Calculate summary
        passed = len([r for r in results if r.get('success', False) and not r.get('skipped', False)])
        failed = len([r for r in results if not r.get('success', False) and not r.get('skipped', False)])
        skipped = len([r for r in results if r.get('skipped', False)])
        
        summary = {
            'total_rules': len(results),
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'success_rate': (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 100
        }
        
        self.logger.info(f"Pipeline completed: {summary}")
        
        return {
            'success': True,
            'summary': summary,
            'results': results,
            'reports': report_paths
        }


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description='Python Data Quality Framework')
    parser.add_argument('--config-dir', default='config', help='Configuration directory')
    parser.add_argument('--rules-file', default='rules.yml', help='Rules configuration file')
    parser.add_argument('--rules', nargs='+', help='Specific rules to execute')
    parser.add_argument('--format', choices=['html', 'json', 'both'], default='both', 
                       help='Report format')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate configuration without executing checks')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--check-type', type=str, default='all', 
                       choices=['all', 'completeness', 'accuracy', 'custom_sql', 'generic', 'advanced'], 
                       help='Specific type of checks to run')
    parser.add_argument('--all-checks', action='store_true', 
                       help='Run all available checks')
    parser.add_argument('--generate-report', action='store_true', 
                       help='Generate report only (skip actual checks)')
    
    args = parser.parse_args()
    
    # Initialize framework
    framework = DataQualityFramework(args.config_dir, args.rules_file)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.validate_only:
        # Only validate configuration
        success = framework.validate_configuration()
        sys.exit(0 if success else 1)
    
    # Determine check type
    check_type = 'all' if args.all_checks else args.check_type
    
    # Run full pipeline
    result = framework.run_full_pipeline(args.rules, check_type, args.generate_report)
    
    if result['success']:
        print(f"\nData Quality Pipeline Completed Successfully!")
        print(f"Rules Executed: {result['summary']['total_rules']}")
        print(f"Passed: {result['summary']['passed']}")
        print(f"Failed: {result['summary']['failed']}")
        print(f"Skipped: {result['summary']['skipped']}")
        print(f"Success Rate: {result['summary']['success_rate']:.2f}%")
        
        if 'reports' in result:
            print(f"\nGenerated Reports:")
            for fmt, path in result['reports'].items():
                print(f"  {fmt.upper()}: {path}")
        
        # Exit with error code if any checks failed
        sys.exit(0 if result['summary']['failed'] == 0 else 1)
    else:
        print(f"\nPipeline Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()