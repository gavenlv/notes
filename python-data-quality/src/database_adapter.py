"""
Database Adapter for ClickHouse with SSL Support
Handles secure database connections and query execution.
"""

from typing import Dict, Any, List, Optional, Union
import logging
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickhouseError


class DatabaseAdapter:
    """Adapter for ClickHouse database operations with SSL support."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize database adapter.
        
        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.client: Optional[Client] = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Establish connection to ClickHouse database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Prepare SSL configuration if enabled
            ssl_config = None
            if self.config.get('secure', False):
                ssl_config = self.config.get('ssl', {})
            
            self.client = Client(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                secure=self.config.get('secure', False),
                verify=self.config.get('ssl', {}).get('verify', True) if ssl_config else True,
                ca_certs=self.config.get('ssl', {}).get('ca_certs') if ssl_config else None,
                cert=self.config.get('ssl', {}).get('cert') if ssl_config else None,
                key=self.config.get('ssl', {}).get('key') if ssl_config else None,
            )
            
            # Test connection
            self.client.execute('SELECT 1')
            self.logger.info(f"Successfully connected to ClickHouse at {self.config['host']}:{self.config['port']}")
            return True
            
        except ClickhouseError as e:
            self.logger.error(f"Failed to connect to ClickHouse: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.client:
            self.client.disconnect()
            self.client = None
            self.logger.info("Disconnected from ClickHouse")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result tuples
            
        Raises:
            ClickhouseError: If query execution fails
        """
        if not self.client:
            raise ClickhouseError("Database connection not established")
        
        try:
            result = self.client.execute(query, params or {})
            self.logger.debug(f"Executed query: {query}")
            return result
        except ClickhouseError as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        query = """
        SELECT 
            name, type, default_expression, comment
        FROM system.columns 
        WHERE table = %(table_name)s
        AND database = %(database)s
        ORDER BY position
        """
        
        params = {
            'table_name': table_name,
            'database': self.config['database']
        }
        
        try:
            columns = self.execute_query(query, params)
            return {
                'table_name': table_name,
                'columns': [
                    {
                        'name': col[0],
                        'type': col[1],
                        'default': col[2],
                        'comment': col[3]
                    } for col in columns
                ],
                'column_count': len(columns)
            }
        except ClickhouseError:
            return {'table_name': table_name, 'columns': [], 'column_count': 0}
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        
        try:
            result = self.execute_query(query)
            return result[0][0] if result else 0
        except ClickhouseError:
            return 0
    
    def check_custom_sql(self, sql: str, expected_result: Any = None) -> Dict[str, Any]:
        """Execute custom SQL for data quality checks.
        
        Args:
            sql: Custom SQL query
            expected_result: Expected result for validation
            
        Returns:
            Dictionary with check results
        """
        try:
            result = self.execute_query(sql)
            
            check_result = {
                'sql': sql,
                'executed_successfully': True,
                'result': result,
                'result_count': len(result),
                'first_row': result[0] if result else None
            }
            
            if expected_result is not None:
                check_result['expected_result'] = expected_result
                check_result['matches_expectation'] = (
                    result and len(result) > 0 and result[0][0] == expected_result
                )
            
            return check_result
            
        except ClickhouseError as e:
            return {
                'sql': sql,
                'executed_successfully': False,
                'error': str(e),
                'result': None,
                'result_count': 0
            }
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class DatabaseConnectionPool:
    """Simple connection pool for database adapters."""
    
    def __init__(self, config: Dict[str, Any], pool_size: int = 5):
        """Initialize connection pool.
        
        Args:
            config: Database configuration
            pool_size: Maximum number of connections
        """
        self.config = config
        self.pool_size = pool_size
        self.available_connections: List[DatabaseAdapter] = []
        self.in_use_connections: List[DatabaseAdapter] = []
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self) -> DatabaseAdapter:
        """Get a database connection from the pool.
        
        Returns:
            DatabaseAdapter instance
        """
        if self.available_connections:
            connection = self.available_connections.pop()
        elif len(self.in_use_connections) < self.pool_size:
            connection = DatabaseAdapter(self.config)
            if not connection.connect():
                raise ClickhouseError("Failed to create database connection")
        else:
            raise ClickhouseError("Connection pool exhausted")
        
        self.in_use_connections.append(connection)
        return connection
    
    def return_connection(self, connection: DatabaseAdapter) -> None:
        """Return a connection to the pool.
        
        Args:
            connection: DatabaseAdapter to return
        """
        if connection in self.in_use_connections:
            self.in_use_connections.remove(connection)
            self.available_connections.append(connection)
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        for connection in self.available_connections + self.in_use_connections:
            connection.disconnect()
        
        self.available_connections.clear()
        self.in_use_connections.clear()