"""
Database connection management following Dependency Inversion Principle
"""

import os
from typing import Dict, Any, Optional
import clickhouse_connect
import psycopg2
import mysql.connector

from .interfaces import IDatabaseConnection


class ClickHouseConnection(IDatabaseConnection):
    """ClickHouse database connection"""
    
    def __init__(self, config_manager):
        self._config = config_manager
        self._client: Optional[clickhouse_connect.Client] = None
        self._connection_info: Dict[str, Any] = {}
    
    def connect(self) -> bool:
        """Establish ClickHouse connection with SSL support"""
        try:
            # Determine port (HTTP vs native)
            if self._config.get_config('CLICKHOUSE_HTTP_PORT'):
                port = int(self._config.get_config('CLICKHOUSE_HTTP_PORT'))
            else:
                native_port = int(self._config.get_config('CLICKHOUSE_PORT'))
                port = 8123 if native_port == 9000 else native_port
            
            # SSL configuration
            ssl_config = {}
            if self._config.get_config('CLICKHOUSE_SSL', 'false').lower() == 'true':
                ssl_config['secure'] = True
                ssl_config['verify'] = self._config.get_config('CLICKHOUSE_SSL_VERIFY', 'true').lower() == 'true'
                
                # Optional SSL certificates
                ssl_cert = self._config.get_config('CLICKHOUSE_SSL_CERT')
                ssl_key = self._config.get_config('CLICKHOUSE_SSL_KEY')
                ssl_ca = self._config.get_config('CLICKHOUSE_SSL_CA')
                
                if ssl_cert:
                    ssl_config['cert'] = ssl_cert
                if ssl_key:
                    ssl_config['key'] = ssl_key
                if ssl_ca:
                    ssl_config['ca'] = ssl_ca
            
            self._client = clickhouse_connect.get_client(
                host=self._config.get_config('CLICKHOUSE_HOST'),
                port=port,
                username=self._config.get_config('CLICKHOUSE_USERNAME'),
                password=self._config.get_config('CLICKHOUSE_PASSWORD'),
                database=self._config.get_config('CLICKHOUSE_DATABASE'),
                **ssl_config
            )
            
            self._connection_info = {
                'host': self._config.get_config('CLICKHOUSE_HOST'),
                'port': port,
                'database': self._config.get_config('CLICKHOUSE_DATABASE'),
                'username': self._config.get_config('CLICKHOUSE_USERNAME')
            }
            
            return True
        except Exception as e:
            print(f"ClickHouse connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close ClickHouse connection"""
        if self._client:
            self._client.close()
            self._client = None
    
    def is_connected(self) -> bool:
        """Check if ClickHouse connection is active"""
        if not self._client:
            return False
        try:
            self._client.query("SELECT 1")
            return True
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get ClickHouse connection information"""
        return self._connection_info.copy()
    
    def get_client(self):
        """Get ClickHouse client (for specific operations)"""
        return self._client


class PostgreSQLConnection(IDatabaseConnection):
    """PostgreSQL database connection"""
    
    def __init__(self, config_manager):
        self._config = config_manager
        self._connection: Optional[psycopg2.extensions.connection] = None
        self._connection_info: Dict[str, Any] = {}
    
    def connect(self) -> bool:
        """Establish PostgreSQL connection"""
        try:
            self._connection = psycopg2.connect(
                host=self._config.get_config('POSTGRES_HOST'),
                port=int(self._config.get_config('POSTGRES_PORT')),
                database=self._config.get_config('POSTGRES_DATABASE'),
                user=self._config.get_config('POSTGRES_USERNAME'),
                password=self._config.get_config('POSTGRES_PASSWORD')
            )
            
            self._connection_info = {
                'host': self._config.get_config('POSTGRES_HOST'),
                'port': int(self._config.get_config('POSTGRES_PORT')),
                'database': self._config.get_config('POSTGRES_DATABASE'),
                'user': self._config.get_config('POSTGRES_USERNAME')
            }
            
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """Check if PostgreSQL connection is active"""
        if not self._connection:
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get PostgreSQL connection information"""
        return self._connection_info.copy()
    
    def get_connection(self):
        """Get PostgreSQL connection (for specific operations)"""
        return self._connection


class ClickHouseDQConnection(IDatabaseConnection):
    """ClickHouse connection specifically for data quality reporting"""
    
    def __init__(self, config_manager):
        self._config = config_manager
        self._client: Optional[clickhouse_connect.Client] = None
        self._connection_info: Dict[str, Any] = {}
    
    def connect(self) -> bool:
        """Establish ClickHouse DQ connection with SSL support"""
        try:
            # SSL configuration
            ssl_config = {}
            if self._config.get_config('CLICKHOUSE_DQ_SSL', 'false').lower() == 'true':
                ssl_config['secure'] = True
                ssl_config['verify'] = self._config.get_config('CLICKHOUSE_DQ_SSL_VERIFY', 'true').lower() == 'true'
                
                # Optional SSL certificates
                ssl_cert = self._config.get_config('CLICKHOUSE_DQ_SSL_CERT')
                ssl_key = self._config.get_config('CLICKHOUSE_DQ_SSL_KEY')
                ssl_ca = self._config.get_config('CLICKHOUSE_DQ_SSL_CA')
                
                if ssl_cert:
                    ssl_config['cert'] = ssl_cert
                if ssl_key:
                    ssl_config['key'] = ssl_key
                if ssl_ca:
                    ssl_config['ca'] = ssl_ca
            
            self._client = clickhouse_connect.get_client(
                host=self._config.get_config('CLICKHOUSE_DQ_HOST'),
                port=int(self._config.get_config('CLICKHOUSE_DQ_HTTP_PORT')),
                username=self._config.get_config('CLICKHOUSE_DQ_USERNAME'),
                password=self._config.get_config('CLICKHOUSE_DQ_PASSWORD'),
                database=self._config.get_config('CLICKHOUSE_DQ_DATABASE'),
                **ssl_config
            )
            
            self._connection_info = {
                'host': self._config.get_config('CLICKHOUSE_DQ_HOST'),
                'port': int(self._config.get_config('CLICKHOUSE_DQ_HTTP_PORT')),
                'database': self._config.get_config('CLICKHOUSE_DQ_DATABASE'),
                'username': self._config.get_config('CLICKHOUSE_DQ_USERNAME')
            }
            
            return True
        except Exception as e:
            print(f"ClickHouse DQ connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close ClickHouse DQ connection"""
        if self._client:
            self._client.close()
            self._client = None
    
    def is_connected(self) -> bool:
        """Check if ClickHouse DQ connection is active"""
        if not self._client:
            return False
        try:
            self._client.query("SELECT 1")
            return True
        except:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get ClickHouse DQ connection information"""
        return self._connection_info.copy()
    
    def get_client(self):
        """Get ClickHouse DQ client (for specific operations)"""
        return self._client


class DatabaseConnectionFactory:
    """Factory for creating database connections"""
    
    @staticmethod
    def create_clickhouse_connection(config_manager) -> ClickHouseConnection:
        """Create ClickHouse connection"""
        return ClickHouseConnection(config_manager)
    
    @staticmethod
    def create_postgresql_connection(config_manager) -> PostgreSQLConnection:
        """Create PostgreSQL connection"""
        return PostgreSQLConnection(config_manager)
    
    @staticmethod
    def create_clickhouse_dq_connection(config_manager) -> ClickHouseDQConnection:
        """Create ClickHouse DQ connection"""
        return ClickHouseDQConnection(config_manager)
    
    @staticmethod
    def create_mysql_connection(config_manager):
        """Create MySQL connection"""
        from .mysql_connection import MySQLConnection
        return MySQLConnection(config_manager)
