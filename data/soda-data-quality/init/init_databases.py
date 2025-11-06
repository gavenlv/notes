#!/usr/bin/env python3
"""
Refactored Database Initialization Script
Initializes PostgreSQL and ClickHouse databases using SOLID architecture
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

from core.factories import DataQualityApplicationFactory
from core.interfaces import ILogger


class DatabaseInitializer:
    """Database initialization using refactored architecture"""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
    
    def initialize_all_databases(self) -> bool:
        """Initialize all databases"""
        self._logger.info("Starting database initialization...")
        
        try:
            # Initialize PostgreSQL
            postgres_success = self._initialize_postgresql()
            
            # Initialize ClickHouse
            clickhouse_success = self._initialize_clickhouse()
            
            if postgres_success and clickhouse_success:
                self._logger.info("✅ All databases initialized successfully!")
                return True
            else:
                self._logger.error("❌ Some databases failed to initialize!")
                return False
                
        except Exception as e:
            self._logger.error(f"Database initialization failed: {str(e)}")
            return False
    
    def _initialize_postgresql(self) -> bool:
        """Initialize PostgreSQL database"""
        self._logger.info("Initializing PostgreSQL database...")
        
        try:
            # Use the refactored PostgreSQL connection
            from core.database_connections import DatabaseConnectionFactory
            from core.configuration import EnvironmentConfigurationManager
            
            # Load configuration
            env_file = Path(project_root) / 'config' / 'environment.env'
            config_manager = EnvironmentConfigurationManager(str(env_file))
            
            # Create PostgreSQL connection
            pg_connection = DatabaseConnectionFactory.create_postgresql_connection(config_manager)
            
            if not pg_connection.connect():
                self._logger.error("Failed to connect to PostgreSQL")
                return False
            
            # Read and execute SQL script
            sql_file = Path(project_root) / 'init' / 'scripts' / 'init_postgresql.sql'
            if not sql_file.exists():
                self._logger.warning(f"PostgreSQL SQL script not found: {sql_file}")
                return True  # Not a critical error
            
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            
            # Execute script
            conn = pg_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql_script)
            cursor.close()
            
            self._logger.info("✅ PostgreSQL database initialized successfully!")
            return True
            
        except Exception as e:
            self._logger.error(f"PostgreSQL initialization failed: {str(e)}")
            return False
    
    def _initialize_clickhouse(self) -> bool:
        """Initialize ClickHouse database"""
        self._logger.info("Initializing ClickHouse database...")
        
        try:
            # Use the refactored ClickHouse connection
            from core.database_connections import DatabaseConnectionFactory
            from core.configuration import EnvironmentConfigurationManager
            
            # Load configuration
            env_file = Path(project_root) / 'config' / 'environment.env'
            config_manager = EnvironmentConfigurationManager(str(env_file))
            
            # Create ClickHouse connection
            ch_connection = DatabaseConnectionFactory.create_clickhouse_connection(config_manager)
            
            if not ch_connection.connect():
                self._logger.error("Failed to connect to ClickHouse")
                return False
            
            # Read and execute SQL script
            sql_file = Path(project_root) / 'init' / 'scripts' / 'init_clickhouse.sql'
            if not sql_file.exists():
                self._logger.warning(f"ClickHouse SQL script not found: {sql_file}")
                return True  # Not a critical error
            
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            
            # Execute script
            client = ch_connection.get_client()
            client.command(sql_script)
            
            self._logger.info("✅ ClickHouse database initialized successfully!")
            return True
            
        except Exception as e:
            self._logger.error(f"ClickHouse initialization failed: {str(e)}")
            return False


def main():
    """Main initialization function"""
    try:
        # Create logger
        from core.logging import LoggerFactory
        logger = LoggerFactory.create_application_logger(project_root)
        
        # Create initializer
        initializer = DatabaseInitializer(logger)
        
        # Initialize databases
        success = initializer.initialize_all_databases()
        
        if success:
            logger.info("🚀 Database initialization completed successfully!")
            logger.info("Ready to run data quality checks!")
            sys.exit(0)
        else:
            logger.error("❌ Database initialization failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
