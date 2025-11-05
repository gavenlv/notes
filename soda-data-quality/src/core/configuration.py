"""
Configuration management following Single Responsibility Principle
"""

import os
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

from .interfaces import IConfigurationManager


class EnvironmentConfigurationManager(IConfigurationManager):
    """Manages configuration from environment variables"""
    
    def __init__(self, env_file_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self._env_file_path = env_file_path
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from environment file"""
        if self._env_file_path and os.path.exists(self._env_file_path):
            load_dotenv(self._env_file_path)
        
        # Load all environment variables
        self._config = dict(os.environ)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def validate_config(self) -> bool:
        """Validate required configuration"""
        required_keys = [
            'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DATABASE',
            'POSTGRES_USERNAME', 'POSTGRES_PASSWORD',
            'CLICKHOUSE_HOST', 'CLICKHOUSE_PORT', 'CLICKHOUSE_USERNAME',
            'CLICKHOUSE_PASSWORD', 'CLICKHOUSE_DATABASE',
            'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_DATABASE',
            'MYSQL_USERNAME', 'MYSQL_PASSWORD',
            'DQ_STORE_TO_MYSQL',
            'POSTGRES_SSLMODE', 'CLICKHOUSE_SECURE', 'MYSQL_SSL_CA'
        ]
        
        missing_keys = [key for key in required_keys if not self.get_config(key)]
        if missing_keys:
            raise ValueError(f"Missing required configuration: {missing_keys}")
        
        return True


class SodaConfigurationGenerator:
    """Generates Soda Core configuration YAML content"""
    
    def __init__(self, config_manager: IConfigurationManager):
        self._config = config_manager
    
    def generate_postgresql_config(self) -> str:
        """Generate PostgreSQL data source configuration"""
        return f"""
data_source postgresql:
  type: postgres
  host: {self._config.get_config('POSTGRES_HOST')}
  port: {self._config.get_config('POSTGRES_PORT')}
  database: {self._config.get_config('POSTGRES_DATABASE')}
  username: {self._config.get_config('POSTGRES_USERNAME')}
  password: {self._config.get_config('POSTGRES_PASSWORD')}
"""
    
    def generate_clickhouse_config(self) -> str:
        """Generate ClickHouse data source configuration with SSL support"""
        ssl_config = ""
        if self._config.get_config('CLICKHOUSE_SSL', 'false').lower() == 'true':
            ssl_config = f"""
  secure: true
  verify: {self._config.get_config('CLICKHOUSE_SSL_VERIFY', 'true').lower()}"""
            
            ssl_cert = self._config.get_config('CLICKHOUSE_SSL_CERT')
            ssl_key = self._config.get_config('CLICKHOUSE_SSL_KEY')
            ssl_ca = self._config.get_config('CLICKHOUSE_SSL_CA')
            
            if ssl_cert:
                ssl_config += f"\n  cert: {ssl_cert}"
            if ssl_key:
                ssl_config += f"\n  key: {ssl_key}"
            if ssl_ca:
                ssl_config += f"\n  ca: {ssl_ca}"
        
        return f"""
data_source clickhouse:
  type: clickhouse
  host: {self._config.get_config('CLICKHOUSE_HOST')}
  port: {self._config.get_config('CLICKHOUSE_PORT')}
  database: {self._config.get_config('CLICKHOUSE_DATABASE')}
  username: {self._config.get_config('CLICKHOUSE_USERNAME')}
  password: {self._config.get_config('CLICKHOUSE_PASSWORD')}{ssl_config}
"""
    
    def generate_full_config(self) -> str:
        """Generate complete Soda configuration"""
        return self.generate_postgresql_config() + self.generate_clickhouse_config()
