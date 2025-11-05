"""
Factory classes following SOLID principles
"""

import os
from pathlib import Path
from typing import List, Optional

from .interfaces import (
    IDataQualityChecker, IDataQualityReporter, IDatabaseConnection,
    IConfigurationManager, ILogger, IFileManager
)
from .configuration import EnvironmentConfigurationManager, SodaConfigurationGenerator
from .logging import LoggerFactory
from .file_manager import StandardFileManager
from .database_connections import (
    DatabaseConnectionFactory, ClickHouseConnection, PostgreSQLConnection, ClickHouseDQConnection
)
from .scan_coordinator import DataQualityScanCoordinator

from checkers.clickhouse_checker import ClickHouseDataQualityChecker
from checkers.soda_checker import SodaDataQualityChecker
from checkers.mysql_checker import MySQLDataQualityChecker
from reporters.clickhouse_reporter import ClickHouseDataQualityReporter
from reporters.json_reporter import JSONDataQualityReporter
from reporters.mysql_reporter import MySQLDataQualityReporter


class DataQualityApplicationFactory:
    """Factory for creating the complete data quality application"""
    
    def __init__(self, project_root: str):
        self._project_root = Path(project_root)
        self._config_manager = None
        self._logger = None
        self._file_manager = None
    
    def create_application(self) -> 'RefactoredDataQualityApp':
        """Create the complete data quality application"""
        # Initialize core components
        self._config_manager = self._create_config_manager()
        self._logger = self._create_logger()
        self._file_manager = self._create_file_manager()
        
        # Create scan coordinator
        coordinator = DataQualityScanCoordinator(self._logger)
        
        # Create and register checkers
        checkers = self._create_checkers()
        for checker in checkers:
            coordinator.add_checker(checker)
        
        # Create and register reporters
        reporters = self._create_reporters()
        for reporter in reporters:
            coordinator.add_reporter(reporter)
        
        return RefactoredDataQualityApp(
            coordinator=coordinator,
            config_manager=self._config_manager,
            logger=self._logger,
            file_manager=self._file_manager
        )
    
    def _create_config_manager(self) -> IConfigurationManager:
        """Create configuration manager"""
        env_file = self._project_root / 'config' / 'environment.env'
        return EnvironmentConfigurationManager(str(env_file))
    
    def _create_logger(self) -> ILogger:
        """Create application logger"""
        return LoggerFactory.create_application_logger(str(self._project_root))
    
    def _create_file_manager(self) -> IFileManager:
        """Create file manager"""
        return StandardFileManager(str(self._project_root))
    
    def _create_checkers(self) -> List[IDataQualityChecker]:
        """Create all data quality checkers"""
        checkers = []
        
        # Create ClickHouse checker
        try:
            ch_connection = DatabaseConnectionFactory.create_clickhouse_connection(self._config_manager)
            if ch_connection.connect():
                ch_logger = LoggerFactory.create_module_logger('clickhouse_checker')
                checker = ClickHouseDataQualityChecker(ch_connection, ch_logger)
                checkers.append(checker)
        except Exception as e:
            self._logger.warning(f"Could not create ClickHouse checker: {e}")
        
        # Create Soda checkers for different data sources
        try:
            # PostgreSQL Soda checker
            pg_connection = DatabaseConnectionFactory.create_postgresql_connection(self._config_manager)
            if pg_connection.connect():
                pg_logger = LoggerFactory.create_module_logger('soda_postgresql')
                checks_path = str(self._project_root / 'config' / 'checks')
                pg_checker = SodaDataQualityChecker(
                    pg_connection, pg_logger, self._file_manager, 'postgresql', checks_path
                )
                checkers.append(pg_checker)
        except Exception as e:
            self._logger.warning(f"Could not create PostgreSQL Soda checker: {e}")
        
        # Create MySQL checker
        try:
            mysql_connection = DatabaseConnectionFactory.create_mysql_connection(self._config_manager)
            if mysql_connection.connect():
                mysql_logger = LoggerFactory.create_module_logger('mysql_checker')
                mysql_checker = MySQLDataQualityChecker(mysql_connection, mysql_logger)
                checkers.append(mysql_checker)
        except Exception as e:
            self._logger.warning(f"Could not create MySQL checker: {e}")
        
        return checkers
    
    def _create_reporters(self) -> List[IDataQualityReporter]:
        """Create all data quality reporters"""
        reporters = []
        
        # Always create JSON reporter
        json_logger = LoggerFactory.create_module_logger('json_reporter')
        json_reporter = JSONDataQualityReporter(self._file_manager, json_logger)
        reporters.append(json_reporter)
        
        # Create ClickHouse reporter if enabled
        if self._config_manager.get_config('DQ_STORE_TO_CLICKHOUSE', 'false').lower() == 'true':
            try:
                ch_dq_connection = DatabaseConnectionFactory.create_clickhouse_dq_connection(self._config_manager)
                if ch_dq_connection.connect():
                    ch_dq_logger = LoggerFactory.create_module_logger('clickhouse_reporter')
                    environment = self._config_manager.get_config('DQ_ENVIRONMENT', 'production')
                    ch_dq_reporter = ClickHouseDataQualityReporter(ch_dq_connection, ch_dq_logger, environment)
                    reporters.append(ch_dq_reporter)
            except Exception as e:
                self._logger.warning(f"Could not create ClickHouse reporter: {e}")
        
        # Create MySQL reporter if enabled
        if self._config_manager.get_config('DQ_STORE_TO_MYSQL', 'false').lower() == 'true':
            try:
                mysql_connection = DatabaseConnectionFactory.create_mysql_connection(self._config_manager)
                if mysql_connection.connect():
                    mysql_logger = LoggerFactory.create_module_logger('mysql_reporter')
                    mysql_reporter = MySQLDataQualityReporter(mysql_connection, mysql_logger)
                    reporters.append(mysql_reporter)
            except Exception as e:
                self._logger.warning(f"Could not create MySQL reporter: {e}")
        
        return reporters


class RefactoredDataQualityApp:
    """Refactored data quality application following SOLID principles"""
    
    def __init__(self, 
                 coordinator: DataQualityScanCoordinator,
                 config_manager: IConfigurationManager,
                 logger: ILogger,
                 file_manager: IFileManager):
        self._coordinator = coordinator
        self._config_manager = config_manager
        self._logger = logger
        self._file_manager = file_manager
    
    def run(self) -> int:
        """Run the data quality application"""
        try:
            self._logger.info("Starting refactored data quality application")
            
            # Validate configuration
            self._config_manager.validate_config()
            
            # Run all scans
            results = self._coordinator.run_all_scans()
            
            # Generate summary
            summary = self._coordinator.get_summary(results)
            
            # Print summary
            self._print_summary(summary, results)
            
            # Determine exit code
            exit_code = 0 if summary['total_failed'] == 0 else 1
            
            self._logger.info(f"Application completed with exit code: {exit_code}")
            return exit_code
            
        except Exception as e:
            self._logger.error(f"Application error: {str(e)}")
            return 1
    
    def _print_summary(self, summary: dict, results: list) -> None:
        """Print scan summary"""
        print("\n" + "="*60)
        print("DATA QUALITY SCAN SUMMARY")
        print("="*60)
        
        for result in results:
            data_source = result.get('data_source', 'unknown').upper()
            status = "❌ ISSUES FOUND" if result.get('checks_failed', 0) > 0 else "✅ HEALTHY"
            print(f"\n{data_source}:")
            print(f"  Status: {status}")
            print(f"  Checks Passed: {result.get('checks_passed', 0)}")
            print(f"  Checks Failed: {result.get('checks_failed', 0)}")
            print(f"  Checks Warned: {result.get('checks_warned', 0)}")
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Total Checks Passed: {summary['total_passed']}")
        print(f"  Total Checks Failed: {summary['total_failed']}")
        print(f"  Total Checks Warned: {summary['total_warned']}")
        print(f"  Overall Status: {summary['overall_status']}")
        print("="*60)
