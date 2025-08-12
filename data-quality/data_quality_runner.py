#!/usr/bin/env python3
"""
Data Quality Check Runner
Supports multi-scenario, multi-database data quality checks
"""

import sys
import argparse
import logging
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

from core.engine import DataQualityEngine
from core.config_manager import ConfigManager
from core.database_adapters import DatabaseAdapterFactory


def setup_logging(level: str = "INFO"):
    """Setup logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data_quality.log')
        ]
    )


def list_scenarios(config_manager: ConfigManager):
    """List available scenarios"""
    scenarios = config_manager.get_available_scenarios()
    print("Available data quality test scenarios:")
    print("=" * 50)
    
    for scenario in scenarios:
        scenario_config = config_manager.get_scenario_config(scenario)
        description = scenario_config.get('description', 'No description')
        enabled = scenario_config.get('enabled', True)
        status = "✓" if enabled else "✗"
        print(f"  {status} {scenario:<20} - {description}")
    
    print(f"\nTotal {len(scenarios)} scenarios")


def list_databases():
    """List supported database types"""
    databases = DatabaseAdapterFactory.get_supported_types()
    print("Supported database types:")
    print("=" * 30)
    
    for db_type in databases:
        requirements = DatabaseAdapterFactory.get_adapter_requirements(db_type)
        req_str = ", ".join(requirements) if requirements else "No additional dependencies"
        print(f"  • {db_type:<15} ({req_str})")
    
    print(f"\nTotal support for {len(databases)} database types")


def test_database_connection(config_manager: ConfigManager, database_name: str = None):
    """Test database connection"""
    db_config = config_manager.get_database_config(database_name)
    db_type = db_config.get('type', 'clickhouse')
    
    print(f"Testing {db_type} database connection...")
    print(f"Host: {db_config.get('host', 'unknown')}")
    print(f"Port: {db_config.get('port', 'unknown')}")
    print(f"Database: {db_config.get('database', 'unknown')}")
    
    try:
        from core.database_adapters import test_database_connection
        success = test_database_connection(db_type, db_config)
        
        if success:
            print("✓ Database connection successful")
            return True
        else:
            print("✗ Database connection failed")
            return False
            
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        return False


def run_scenario(engine: DataQualityEngine, scenario_name: str, database_config: dict = None):
    """Run specified scenario"""
    print(f"Starting data quality scenario: {scenario_name}")
    print("=" * 50)
    
    try:
        summary = engine.run_scenario(scenario_name, database_config)
        
        print("\nExecution completed!")
        print("=" * 50)
        
        # Print summary
        print("Execution summary:")
        print(f"  Scenario: {summary.get('scenario', 'unknown')}")
        print(f"  Environment: {summary.get('environment', 'unknown')}")
        print(f"  Status: {summary.get('status', 'unknown')}")
        print(f"  Duration: {summary.get('duration', 0):.2f} seconds")
        
        stats = summary.get('summary', {})
        print(f"  Total rules: {stats.get('total_rules', 0)}")
        print(f"  Passed rules: {stats.get('passed_rules', 0)}")
        print(f"  Failed rules: {stats.get('failed_rules', 0)}")
        print(f"  Error rules: {stats.get('error_rules', 0)}")
        print(f"  Pass rate: {stats.get('pass_rate', 0)}%")
        
        # Determine exit code
        failed_count = stats.get('failed_rules', 0)
        error_count = stats.get('error_rules', 0)
        
        if failed_count > 0 or error_count > 0:
            print(f"\n❌ Found {failed_count} failures and {error_count} errors")
            return 1
        else:
            print("\n✅ All data quality checks passed")
            return 0
            
    except Exception as e:
        print(f"\n❌ Scenario execution failed: {e}")
        return 1


def validate_config(config_manager: ConfigManager):
    """Validate configuration"""
    print("Validating configuration file...")
    print("=" * 30)
    
    errors = config_manager.validate_config()
    
    if not errors:
        print("✓ Configuration validation passed")
        
        # Display configuration summary
        summary = config_manager.get_config_summary()
        print("\nConfiguration summary:")
        print(f"  Environment: {summary.get('environment', 'unknown')}")
        print(f"  Config file: {summary.get('config_path', 'unknown')}")
        print(f"  Database type: {summary.get('database_type', 'unknown')}")
        print(f"  Database host: {summary.get('database_host', 'unknown')}")
        print(f"  Max parallel jobs: {summary.get('max_parallel_jobs', 5)}")
        print(f"  Report formats: {', '.join(summary.get('report_formats', []))}")
        print(f"  Rule paths: {', '.join(summary.get('rules_paths', []))}")
        print(f"  Available scenarios: {len(summary.get('available_scenarios', []))}")
        
        return True
    else:
        print("✗ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Data Quality Check Tool v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s --list-scenarios                    # List all available scenarios
  %(prog)s --list-databases                    # List supported database types
  %(prog)s --test-connection                   # Test default database connection
  %(prog)s --validate-config                   # Validate configuration file
  %(prog)s --scenario clickhouse_smoke_test    # Run ClickHouse smoke test
  %(prog)s --scenario mysql_regression --env prod  # Run MySQL regression test in production environment
        """
    )
    
    # General parameters
    parser.add_argument('--config', '-c', 
                       help='Configuration file path (default: configs/data-quality-config.yml)')
    parser.add_argument('--env', '-e', default='default',
                       help='Environment name (default, dev, test, prod)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Log level')
    
    # Function parameters
    parser.add_argument('--list-scenarios', action='store_true',
                       help='List all available test scenarios')
    parser.add_argument('--list-databases', action='store_true', 
                       help='List supported database types')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test database connection')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate configuration file')
    
    # Execution parameters
    parser.add_argument('--scenario', '-s',
                       help='Scenario name to execute')
    parser.add_argument('--database',
                       help='Database name (override default configuration)')
    parser.add_argument('--output-dir', '-o',
                       help='Report output directory')
    parser.add_argument('--max-workers', type=int,
                       help='Maximum parallel execution count')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(args.config, args.env)
        
        # Handle list commands
        if args.list_scenarios:
            list_scenarios(config_manager)
            return 0
        
        if args.list_databases:
            list_databases()
            return 0
        
        if args.validate_config:
            success = validate_config(config_manager)
            return 0 if success else 1
        
        if args.test_connection:
            success = test_database_connection(config_manager, args.database)
            return 0 if success else 1
        
        # Handle scenario execution
        if args.scenario:
            # Initialize data quality engine
            engine = DataQualityEngine(args.config, args.env)
            
            # Override configuration
            if args.output_dir:
                engine.config_manager.set_config_value('report.output_dir', args.output_dir)
            
            if args.max_workers:
                engine.config_manager.set_config_value('execution.max_parallel_jobs', args.max_workers)
            
            # Get database configuration
            database_config = None
            if args.database:
                database_config = config_manager.get_database_config(args.database)
            
            # Run scenario
            return run_scenario(engine, args.scenario, database_config)
        
        # If no operation specified, show help
        parser.print_help()
        return 0
        
    except KeyboardInterrupt:
        print("\nUser interrupted execution")
        return 130
    except Exception as e:
        print(f"Execution failed: {e}")
        logging.exception("Execution exception")
        return 1


if __name__ == "__main__":
    sys.exit(main())

