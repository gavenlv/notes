"""
Configuration Manager for Data Quality Framework
Handles environment variables, YAML configuration, and SSL settings.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration for the data quality framework."""
    
    def __init__(self, env_file: str = "config/environment.env", config_file: str = "config/data_quality.yml"):
        """Initialize configuration manager.
        
        Args:
            env_file: Path to environment file
            config_file: Path to YAML configuration file
        """
        self.env_file = Path(env_file)
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._env_vars: Dict[str, str] = {}
        
        self._load_environment()
        self._load_config()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Load ClickHouse configuration
        self._env_vars = {
            'clickhouse_host': os.getenv('CLICKHOUSE_HOST', 'localhost'),
            'clickhouse_port': int(os.getenv('CLICKHOUSE_PORT', '9440')),
            'clickhouse_user': os.getenv('CLICKHOUSE_USER', 'default'),
            'clickhouse_password': os.getenv('CLICKHOUSE_PASSWORD', ''),
            'clickhouse_database': os.getenv('CLICKHOUSE_DATABASE', 'default'),
            'clickhouse_ssl_enabled': os.getenv('CLICKHOUSE_SSL_ENABLED', 'true').lower() == 'true',
            'clickhouse_ssl_verify': os.getenv('CLICKHOUSE_SSL_VERIFY', 'true').lower() == 'true',
            'clickhouse_ssl_ca_cert': os.getenv('CLICKHOUSE_SSL_CA_CERT'),
            'clickhouse_ssl_cert': os.getenv('CLICKHOUSE_SSL_CERT'),
            'clickhouse_ssl_key': os.getenv('CLICKHOUSE_SSL_KEY'),
        }
    
    def _load_config(self) -> None:
        """Load YAML configuration file."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration with SSL support.
        
        Returns:
            Dictionary with database configuration
        """
        ssl_config = {}
        if self._env_vars['clickhouse_ssl_enabled']:
            ssl_config = {
                'verify': self._env_vars['clickhouse_ssl_verify'],
                'ca_certs': self._env_vars['clickhouse_ssl_ca_cert'],
                'cert': self._env_vars['clickhouse_ssl_cert'],
                'key': self._env_vars['clickhouse_ssl_key'],
            }
        
        return {
            'host': self._env_vars['clickhouse_host'],
            'port': self._env_vars['clickhouse_port'],
            'user': self._env_vars['clickhouse_user'],
            'password': self._env_vars['clickhouse_password'],
            'database': self._env_vars['clickhouse_database'],
            'secure': self._env_vars['clickhouse_ssl_enabled'],
            'ssl': ssl_config if ssl_config else None,
        }
    
    def get_rule_config(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific rule.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Rule configuration or None if not found
        """
        rules = self._config.get('rules', {})
        return rules.get(rule_name)
    
    def get_framework_config(self) -> Dict[str, Any]:
        """Get framework-level configuration.
        
        Returns:
            Framework configuration
        """
        return {
            'report_format': os.getenv('DATA_QUALITY_REPORT_FORMAT', 'html'),
            'output_dir': os.getenv('DATA_QUALITY_OUTPUT_DIR', 'reports/'),
            'log_level': os.getenv('DATA_QUALITY_LOG_LEVEL', 'INFO'),
            'custom_checks_enabled': os.getenv('CUSTOM_CHECKS_ENABLED', 'true').lower() == 'true',
            'max_parallel_checks': int(os.getenv('MAX_PARALLEL_CHECKS', '5')),
            'default_timeout': int(os.getenv('DEFAULT_TIMEOUT_SECONDS', '300')),
        }
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present.
        
        Returns:
            True if configuration is valid
        """
        required_env_vars = ['CLICKHOUSE_HOST', 'CLICKHOUSE_USER']
        
        for var in required_env_vars:
            if not os.getenv(var):
                return False
        
        return True


def create_sample_config() -> Dict[str, Any]:
    """Create a sample configuration for documentation.
    
    Returns:
        Sample configuration dictionary
    """
    return {
        'rules': {
            'table_completeness': {
                'description': 'Check if table has expected number of rows',
                'type': 'completeness',
                'table': 'your_table',
                'expected_rows': 1000,
                'tolerance': 0.1,
            },
            'data_accuracy': {
                'description': 'Check data accuracy using custom SQL',
                'type': 'accuracy',
                'custom_sql': 'SELECT COUNT(*) FROM table WHERE column IS NULL',
                'max_errors': 0,
            }
        },
        'framework': {
            'report_format': 'html',
            'parallel_execution': True,
            'timeout_seconds': 300,
        }
    }