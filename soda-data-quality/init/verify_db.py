#!/usr/bin/env python3
"""
Refactored script to verify ClickHouse database and tables
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


class DatabaseVerifier:
    """Database verification using refactored architecture"""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
    
    def verify_clickhouse_database(self) -> bool:
        """Verify ClickHouse database and tables"""
        try:
            self._logger.info("Verifying ClickHouse database...")
            
            # Load configuration
            env_file = Path(project_root) / 'config' / 'environment.env'
            config_manager = EnvironmentConfigurationManager(str(env_file))
            
            # Create ClickHouse DQ connection
            ch_dq_connection = DatabaseConnectionFactory.create_clickhouse_dq_connection(config_manager)
            
            if not ch_dq_connection.connect():
                self._logger.error("Failed to connect to ClickHouse DQ database")
                return False
            
            client = ch_dq_connection.get_client()
            
            # Check if common database exists
            self._logger.info("Checking databases...")
            result = client.query("SHOW DATABASES")
            databases = [row[0] for row in result.result_rows]
            self._logger.info(f"Available databases: {databases}")
            
            if 'common' in databases:
                self._logger.info("✅ Common database exists")
                
                # Check tables
                self._logger.info("Checking tables in common database...")
                result = client.query("SHOW TABLES")
                tables = [row[0] for row in result.result_rows]
                self._logger.info(f"Available tables: {tables}")
                
                # Check specific tables
                required_tables = [
                    'data_quality_scans',
                    'data_quality_checks', 
                    'data_quality_logs'
                ]
                
                for table in required_tables:
                    if table in tables:
                        self._logger.info(f"✅ Table {table} exists")
                    else:
                        self._logger.error(f"❌ Table {table} missing")
                        return False
                
                self._logger.info("✅ All required tables exist")
                return True
            else:
                self._logger.error("❌ Common database does not exist")
                return False
                
        except Exception as e:
            self._logger.error(f"Database verification failed: {str(e)}")
            return False


def main():
    """Main verification function"""
    try:
        # Create logger
        logger = LoggerFactory.create_application_logger(project_root)
        
        # Create verifier
        verifier = DatabaseVerifier(logger)
        
        # Verify database
        success = verifier.verify_clickhouse_database()
        
        if success:
            logger.info("🚀 Database verification completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Database verification failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
