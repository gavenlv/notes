#!/usr/bin/env python3
"""
Refactored setup script to create ClickHouse tables for data quality reporting
Using SOLID architecture
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

from core.configuration import EnvironmentConfigurationManager
from core.database_connections import DatabaseConnectionFactory
from core.logging import LoggerFactory
from core.interfaces import ILogger


class ClickHouseTableSetup:
    """ClickHouse table setup using refactored architecture"""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
    
    def setup_tables(self) -> bool:
        """Setup ClickHouse tables for data quality reporting"""
        try:
            self._logger.info("Setting up ClickHouse tables for data quality reporting...")
            
            # Load configuration
            env_file = Path(project_root) / 'config' / 'environment.env'
            config_manager = EnvironmentConfigurationManager(str(env_file))
            
            # Create ClickHouse DQ connection
            ch_dq_connection = DatabaseConnectionFactory.create_clickhouse_dq_connection(config_manager)
            
            if not ch_dq_connection.connect():
                self._logger.error("Failed to connect to ClickHouse DQ database")
                return False
            
            # Read schema file
            schema_path = Path(project_root) / 'sql' / 'clickhouse_dq_schema.sql'
            if not schema_path.exists():
                self._logger.error(f"Schema file not found: {schema_path}")
                return False
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Parse and execute SQL statements
            statements = self._parse_sql_statements(schema_sql)
            
            client = ch_dq_connection.get_client()
            
            for i, statement in enumerate(statements, 1):
                if statement.strip():
                    self._logger.info(f"Executing statement {i}: {statement[:50]}...")
                    try:
                        client.command(statement)
                        self._logger.info(f"Successfully executed statement {i}")
                    except Exception as e:
                        self._logger.error(f"Error executing statement {i}: {str(e)}")
                        return False
            
            self._logger.info("✅ ClickHouse tables setup completed successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"ClickHouse table setup failed: {str(e)}")
            return False
    
    def _parse_sql_statements(self, sql_content: str) -> list:
        """Parse SQL content into individual statements"""
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Check if statement is complete (ends with semicolon)
            if line.endswith(';'):
                statement = ' '.join(current_statement)
                statements.append(statement)
                current_statement = []
        
        # Add any remaining statement
        if current_statement:
            statement = ' '.join(current_statement)
            statements.append(statement)
        
        return statements


def main():
    """Main setup function"""
    try:
        # Create logger
        logger = LoggerFactory.create_application_logger(project_root)
        
        # Create setup instance
        setup = ClickHouseTableSetup(logger)
        
        # Setup tables
        success = setup.setup_tables()
        
        if success:
            logger.info("🚀 ClickHouse table setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ ClickHouse table setup failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
