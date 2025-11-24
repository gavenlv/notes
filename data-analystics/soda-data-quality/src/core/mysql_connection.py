"""
MySQL database connection implementation following Dependency Inversion Principle
"""

import os
from typing import Dict, Any, Optional
import mysql.connector

from .interfaces import IDatabaseConnection


class MySQLConnection(IDatabaseConnection):
    """MySQL database connection"""
    
    def __init__(self, config_manager):
        self._config = config_manager
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._connection_info: Dict[str, Any] = {}
    
    def connect(self) -> bool:
        """Establish MySQL connection"""
        try:
            self._connection = mysql.connector.connect(
                host=self._config.get_config('MYSQL_HOST'),
                port=int(self._config.get_config('MYSQL_PORT')),
                database=self._config.get_config('MYSQL_DATABASE'),
                user=self._config.get_config('MYSQL_USERNAME'),
                password=self._config.get_config('MYSQL_PASSWORD')
            )
            
            self._connection_info = {
                'host': self._config.get_config('MYSQL_HOST'),
                'port': int(self._config.get_config('MYSQL_PORT')),
                'database': self._config.get_config('MYSQL_DATABASE'),
                'user': self._config.get_config('MYSQL_USERNAME')
            }
            
            return True
        except Exception as e:
            print(f"MySQL connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close MySQL connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """Check if MySQL connection is active"""
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
        """Get MySQL connection information"""
        return self._connection_info.copy()
    
    def get_connection(self):
        """Get MySQL connection (for specific operations)"""
        return self._connection