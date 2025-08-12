#!/usr/bin/env python3
"""
Configuration Management System
Supports multi-environment, multi-scenario configuration management and isolation
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from copy import deepcopy


class ConfigManager:
    """Configuration Manager"""
    
    def __init__(self, config_path: str = None, environment: str = "default"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Configuration file path
            environment: Environment name
        """
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        self.config_cache = {}
        
        # Determine configuration file path
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = self._find_default_config()
        
        # Load configuration
        self.base_config = self._load_base_config()
        self.env_config = self._load_environment_config()
        self.merged_config = self._merge_configs()
        
    def _find_default_config(self) -> str:
        """
        Find default configuration file
        
        Returns:
            str: Configuration file path
        """
        possible_paths = [
            "configs/data-quality-config.yml",
            "config/data-quality-config.yml", 
            "data-quality-config.yml",
            "config.yml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If not found, return default path
        return "configs/data-quality-config.yml"
    
    def _load_base_config(self) -> Dict[str, Any]:
        """
        Load base configuration
        
        Returns:
            Dict: Base configuration
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Configuration file does not exist: {self.config_path}, using default configuration")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.logger.info(f"Successfully loaded base configuration: {self.config_path}")
            return config or {}
            
        except Exception as e:
            self.logger.error(f"Failed to load base configuration: {e}, using default configuration")
            return self._get_default_config()
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """
        Load environment-specific configuration
        
        Returns:
            Dict: Environment configuration
        """
        if self.environment == "default":
            return {}
        
        # Try to load environment-specific configuration file
        env_config_paths = [
            f"configs/data-quality-config-{self.environment}.yml",
            f"config/data-quality-config-{self.environment}.yml",
            f"configs/{self.environment}.yml",
            f"config/{self.environment}.yml"
        ]
        
        for path in env_config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    
                    self.logger.info(f"Successfully loaded environment configuration: {path}")
                    return config or {}
                    
                except Exception as e:
                    self.logger.error(f"Failed to load environment configuration {path}: {e}")
        
        # Check if there's environment-specific configuration in base config
        base_config = self.base_config or {}
        environments = base_config.get('environments', {})
        if self.environment in environments:
            self.logger.info(f"Using environment configuration from base config: {self.environment}")
            return environments[self.environment]
        
        self.logger.warning(f"Environment '{self.environment}' configuration not found, using base configuration")
        return {}
    
    def _merge_configs(self) -> Dict[str, Any]:
        """
        Merge base configuration and environment configuration
        
        Returns:
            Dict: Merged configuration
        """
        merged = deepcopy(self.base_config)
        
        if self.env_config:
            self._deep_merge_dict(merged, self.env_config)
        
        # Set environment information
        merged['_environment'] = self.environment
        merged['_config_path'] = self.config_path
        
        return merged
    
    def _deep_merge_dict(self, base: Dict, override: Dict):
        """
        Deep merge dictionaries
        
        Args:
            base: Base dictionary (will be modified)
            override: Override dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base[key], value)
            else:
                base[key] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration
        
        Returns:
            Dict: Default configuration
        """
        return {
            'database': {
                'type': 'clickhouse',
                'host': 'localhost',
                'port': 9000,
                'database': 'data_quality_test',
                'user': 'admin',
                'password': 'admin',
                'secure': False,
                'timeout': 60
            },
            'execution': {
                'max_parallel_jobs': 5,
                'timeout': 300,
                'fail_fast': False
            },
            'rules': {
                'paths': ['rules/', 'scenarios/'],
                'cache_enabled': True,
                'validation_strict': True
            },
            'templates': {
                'base_dir': 'templates/',
                'cache_enabled': True
            },
            'report': {
                'formats': ['json', 'html', 'txt'],
                'output_dir': 'reports/',
                'include_samples': True,
                'max_samples': 5,
                'retention_days': 30
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/data-quality.log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'rotate': True,
                'max_size': 10485760,
                'backup_count': 5
            },
            'notifications': {
                'enabled': False,
                'channels': {
                    'email': {'enabled': False},
                    'slack': {'enabled': False}
                }
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get complete configuration
        
        Returns:
            Dict: Complete configuration
        """
        return self.merged_config
    
    def get_database_config(self, database_name: str = None) -> Dict[str, Any]:
        """
        Get database configuration
        
        Args:
            database_name: Database name, if not specified returns default database configuration
            
        Returns:
            Dict: Database configuration
        """
        if database_name:
            databases = self.merged_config.get('databases', {})
            if database_name in databases:
                return databases[database_name]
            else:
                self.logger.warning(f"Database configuration not found: {database_name}, using default configuration")
        
        return self.merged_config.get('database', {})
    
    def get_scenario_config(self, scenario_name: str) -> Dict[str, Any]:
        """
        Get scenario configuration
        
        Args:
            scenario_name: Scenario name
            
        Returns:
            Dict: Scenario configuration
        """
        scenarios = self.merged_config.get('scenarios', {})
        if scenario_name in scenarios:
            return scenarios[scenario_name]
        
        # If specific scenario configuration not found, return default configuration
        return {
            'name': scenario_name,
            'description': f'Scenario: {scenario_name}',
            'enabled': True,
            'rules': {
                'paths': ['rules/', f'scenarios/{scenario_name}/'],
                'filters': {}
            },
            'database': self.get_database_config(),
            'execution': self.merged_config.get('execution', {}),
            'report': self.merged_config.get('report', {})
        }
    
    def get_available_scenarios(self) -> List[str]:
        """
        Get available scenario list
        
        Returns:
            List[str]: Scenario name list
        """
        scenarios = list(self.merged_config.get('scenarios', {}).keys())
        
        # Auto-discover scenario directories
        scenarios_dir = Path('scenarios')
        if scenarios_dir.exists():
            for item in scenarios_dir.iterdir():
                if item.is_dir() and item.name not in scenarios:
                    scenarios.append(item.name)
        
        # Add some default scenarios
        default_scenarios = ['all', 'smoke_test', 'regression', 'monitoring']
        for default_scenario in default_scenarios:
            if default_scenario not in scenarios:
                scenarios.append(default_scenario)
        
        return sorted(scenarios)
    
    def get_available_environments(self) -> List[str]:
        """
        Get available environment list
        
        Returns:
            List[str]: Environment name list
        """
        environments = ['default']
        
        # Get environment list from base configuration
        base_environments = self.base_config.get('environments', {})
        environments.extend(base_environments.keys())
        
        # Auto-discover environment configuration files
        config_dir = Path('configs')
        if config_dir.exists():
            for config_file in config_dir.glob('data-quality-config-*.yml'):
                env_name = config_file.stem.replace('data-quality-config-', '')
                if env_name not in environments:
                    environments.append(env_name)
        
        return sorted(list(set(environments)))
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration validity
        
        Returns:
            List[str]: Validation error list
        """
        errors = []
        config = self.merged_config
        
        # Validate database configuration
        database_config = config.get('database', {})
        if not database_config:
            errors.append("Missing database configuration")
        else:
            required_db_fields = ['type', 'host', 'database']
            for field in required_db_fields:
                if not database_config.get(field):
                    errors.append(f"Database configuration missing required field: {field}")
        
        # Validate execution configuration
        execution_config = config.get('execution', {})
        max_jobs = execution_config.get('max_parallel_jobs', 5)
        if not isinstance(max_jobs, int) or max_jobs <= 0:
            errors.append("execution.max_parallel_jobs must be a positive integer")
        
        # Validate report configuration
        report_config = config.get('report', {})
        formats = report_config.get('formats', [])
        valid_formats = ['json', 'html', 'txt', 'csv', 'xml']
        for fmt in formats:
            if fmt not in valid_formats:
                errors.append(f"Unsupported report format: {fmt}")
        
        # Validate rule paths
        rules_config = config.get('rules', {})
        rule_paths = rules_config.get('paths', [])
        for path in rule_paths:
            if not os.path.exists(path):
                errors.append(f"Rule path does not exist: {path}")
        
        return errors
    
    def reload_config(self):
        """Reload configuration"""
        self.logger.info("Reloading configuration...")
        self.base_config = self._load_base_config()
        self.env_config = self._load_environment_config()
        self.merged_config = self._merge_configs()
        self.config_cache.clear()
        self.logger.info("Configuration reload completed")
    
    def get_config_value(self, key_path: str, default_value: Any = None) -> Any:
        """
        Get configuration value by path
        
        Args:
            key_path: Configuration key path, separated by dots, e.g. 'database.host'
            default_value: Default value
            
        Returns:
            Any: Configuration value
        """
        try:
            keys = key_path.split('.')
            value = self.merged_config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default_value
            
            return value
            
        except Exception:
            return default_value
    
    def set_config_value(self, key_path: str, value: Any):
        """
        Set configuration value (runtime modification, not persisted)
        
        Args:
            key_path: Configuration key path, separated by dots
            value: Configuration value
        """
        keys = key_path.split('.')
        current = self.merged_config
        
        # Navigate to the parent of the last level
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set value
        current[keys[-1]] = value
    
    def export_config(self, output_path: str, include_environment_only: bool = False):
        """
        Export configuration to file
        
        Args:
            output_path: Output file path
            include_environment_only: Whether to export only environment-specific configuration
        """
        try:
            config_to_export = self.env_config if include_environment_only else self.merged_config
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_to_export, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            self.logger.info(f"Configuration exported to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary information
        
        Returns:
            Dict: Configuration summary
        """
        config = self.merged_config
        
        return {
            'environment': self.environment,
            'config_path': self.config_path,
            'database_type': config.get('database', {}).get('type', 'unknown'),
            'database_host': config.get('database', {}).get('host', 'unknown'),
            'max_parallel_jobs': config.get('execution', {}).get('max_parallel_jobs', 5),
            'report_formats': config.get('report', {}).get('formats', []),
            'rules_paths': config.get('rules', {}).get('paths', []),
            'available_scenarios': self.get_available_scenarios(),
            'logging_level': config.get('logging', {}).get('level', 'INFO'),
            'config_valid': len(self.validate_config()) == 0
        }
    
    def create_scenario_config(self, scenario_name: str, config: Dict[str, Any]):
        """
        Create scenario configuration
        
        Args:
            scenario_name: Scenario name
            config: Scenario configuration
        """
        scenarios = self.merged_config.setdefault('scenarios', {})
        scenarios[scenario_name] = config
        self.logger.info(f"Created scenario configuration: {scenario_name}")
    
    def update_database_config(self, database_name: str, config: Dict[str, Any]):
        """
        Update database configuration
        
        Args:
            database_name: Database name
            config: Database configuration
        """
        if database_name == 'default':
            self.merged_config['database'] = config
        else:
            databases = self.merged_config.setdefault('databases', {})
            databases[database_name] = config
        
        self.logger.info(f"Updated database configuration: {database_name}")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get environment information
        
        Returns:
            Dict: Environment information
        """
        return {
            'current_environment': self.environment,
            'available_environments': self.get_available_environments(),
            'base_config_path': self.config_path,
            'environment_config_loaded': bool(self.env_config),
            'config_errors': self.validate_config()
        }
