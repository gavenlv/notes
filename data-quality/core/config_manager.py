#!/usr/bin/env python3
"""
配置管理系统
支持多环境、多场景的配置管理和隔离
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from copy import deepcopy


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None, environment: str = "default"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
            environment: 环境名称
        """
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        self.config_cache = {}
        
        # 确定配置文件路径
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = self._find_default_config()
        
        # 加载配置
        self.base_config = self._load_base_config()
        self.env_config = self._load_environment_config()
        self.merged_config = self._merge_configs()
        
    def _find_default_config(self) -> str:
        """
        查找默认配置文件
        
        Returns:
            str: 配置文件路径
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
        
        # 如果没有找到，返回默认路径
        return "configs/data-quality-config.yml"
    
    def _load_base_config(self) -> Dict[str, Any]:
        """
        加载基础配置
        
        Returns:
            Dict: 基础配置
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.logger.info(f"成功加载基础配置: {self.config_path}")
            return config or {}
            
        except Exception as e:
            self.logger.error(f"加载基础配置失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """
        加载环境特定配置
        
        Returns:
            Dict: 环境配置
        """
        if self.environment == "default":
            return {}
        
        # 尝试加载环境特定配置文件
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
                    
                    self.logger.info(f"成功加载环境配置: {path}")
                    return config or {}
                    
                except Exception as e:
                    self.logger.error(f"加载环境配置失败 {path}: {e}")
        
        # 检查基础配置中是否有环境特定配置
        base_config = self.base_config or {}
        environments = base_config.get('environments', {})
        if self.environment in environments:
            self.logger.info(f"使用基础配置中的环境配置: {self.environment}")
            return environments[self.environment]
        
        self.logger.warning(f"未找到环境 '{self.environment}' 的配置，使用基础配置")
        return {}
    
    def _merge_configs(self) -> Dict[str, Any]:
        """
        合并基础配置和环境配置
        
        Returns:
            Dict: 合并后的配置
        """
        merged = deepcopy(self.base_config)
        
        if self.env_config:
            self._deep_merge_dict(merged, self.env_config)
        
        # 设置环境信息
        merged['_environment'] = self.environment
        merged['_config_path'] = self.config_path
        
        return merged
    
    def _deep_merge_dict(self, base: Dict, override: Dict):
        """
        深度合并字典
        
        Args:
            base: 基础字典（会被修改）
            override: 覆盖字典
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base[key], value)
            else:
                base[key] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict: 默认配置
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
        获取完整配置
        
        Returns:
            Dict: 完整配置
        """
        return self.merged_config
    
    def get_database_config(self, database_name: str = None) -> Dict[str, Any]:
        """
        获取数据库配置
        
        Args:
            database_name: 数据库名称，如果不指定则返回默认数据库配置
            
        Returns:
            Dict: 数据库配置
        """
        if database_name:
            databases = self.merged_config.get('databases', {})
            if database_name in databases:
                return databases[database_name]
            else:
                self.logger.warning(f"未找到数据库配置: {database_name}，使用默认配置")
        
        return self.merged_config.get('database', {})
    
    def get_scenario_config(self, scenario_name: str) -> Dict[str, Any]:
        """
        获取场景配置
        
        Args:
            scenario_name: 场景名称
            
        Returns:
            Dict: 场景配置
        """
        scenarios = self.merged_config.get('scenarios', {})
        if scenario_name in scenarios:
            return scenarios[scenario_name]
        
        # 如果没有找到具体场景配置，返回默认配置
        return {
            'name': scenario_name,
            'description': f'场景: {scenario_name}',
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
        获取可用的场景列表
        
        Returns:
            List[str]: 场景名称列表
        """
        scenarios = list(self.merged_config.get('scenarios', {}).keys())
        
        # 自动发现场景目录
        scenarios_dir = Path('scenarios')
        if scenarios_dir.exists():
            for item in scenarios_dir.iterdir():
                if item.is_dir() and item.name not in scenarios:
                    scenarios.append(item.name)
        
        # 添加一些默认场景
        default_scenarios = ['all', 'smoke_test', 'regression', 'monitoring']
        for default_scenario in default_scenarios:
            if default_scenario not in scenarios:
                scenarios.append(default_scenario)
        
        return sorted(scenarios)
    
    def get_available_environments(self) -> List[str]:
        """
        获取可用的环境列表
        
        Returns:
            List[str]: 环境名称列表
        """
        environments = ['default']
        
        # 从基础配置中获取环境列表
        base_environments = self.base_config.get('environments', {})
        environments.extend(base_environments.keys())
        
        # 自动发现环境配置文件
        config_dir = Path('configs')
        if config_dir.exists():
            for config_file in config_dir.glob('data-quality-config-*.yml'):
                env_name = config_file.stem.replace('data-quality-config-', '')
                if env_name not in environments:
                    environments.append(env_name)
        
        return sorted(list(set(environments)))
    
    def validate_config(self) -> List[str]:
        """
        验证配置的有效性
        
        Returns:
            List[str]: 验证错误列表
        """
        errors = []
        config = self.merged_config
        
        # 验证数据库配置
        database_config = config.get('database', {})
        if not database_config:
            errors.append("缺少数据库配置")
        else:
            required_db_fields = ['type', 'host', 'database']
            for field in required_db_fields:
                if not database_config.get(field):
                    errors.append(f"数据库配置缺少必填字段: {field}")
        
        # 验证执行配置
        execution_config = config.get('execution', {})
        max_jobs = execution_config.get('max_parallel_jobs', 5)
        if not isinstance(max_jobs, int) or max_jobs <= 0:
            errors.append("execution.max_parallel_jobs 必须是正整数")
        
        # 验证报告配置
        report_config = config.get('report', {})
        formats = report_config.get('formats', [])
        valid_formats = ['json', 'html', 'txt', 'csv', 'xml']
        for fmt in formats:
            if fmt not in valid_formats:
                errors.append(f"不支持的报告格式: {fmt}")
        
        # 验证规则路径
        rules_config = config.get('rules', {})
        rule_paths = rules_config.get('paths', [])
        for path in rule_paths:
            if not os.path.exists(path):
                errors.append(f"规则路径不存在: {path}")
        
        return errors
    
    def reload_config(self):
        """重新加载配置"""
        self.logger.info("重新加载配置...")
        self.base_config = self._load_base_config()
        self.env_config = self._load_environment_config()
        self.merged_config = self._merge_configs()
        self.config_cache.clear()
        self.logger.info("配置重新加载完成")
    
    def get_config_value(self, key_path: str, default_value: Any = None) -> Any:
        """
        根据路径获取配置值
        
        Args:
            key_path: 配置键路径，用.分隔，如 'database.host'
            default_value: 默认值
            
        Returns:
            Any: 配置值
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
        设置配置值（运行时修改，不会持久化）
        
        Args:
            key_path: 配置键路径，用.分隔
            value: 配置值
        """
        keys = key_path.split('.')
        current = self.merged_config
        
        # 导航到最后一级的父级
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值
        current[keys[-1]] = value
    
    def export_config(self, output_path: str, include_environment_only: bool = False):
        """
        导出配置到文件
        
        Args:
            output_path: 输出文件路径
            include_environment_only: 是否只导出环境特定配置
        """
        try:
            config_to_export = self.env_config if include_environment_only else self.merged_config
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_to_export, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            self.logger.info(f"配置已导出到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"导出配置失败: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要信息
        
        Returns:
            Dict: 配置摘要
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
        创建场景配置
        
        Args:
            scenario_name: 场景名称
            config: 场景配置
        """
        scenarios = self.merged_config.setdefault('scenarios', {})
        scenarios[scenario_name] = config
        self.logger.info(f"创建场景配置: {scenario_name}")
    
    def update_database_config(self, database_name: str, config: Dict[str, Any]):
        """
        更新数据库配置
        
        Args:
            database_name: 数据库名称
            config: 数据库配置
        """
        if database_name == 'default':
            self.merged_config['database'] = config
        else:
            databases = self.merged_config.setdefault('databases', {})
            databases[database_name] = config
        
        self.logger.info(f"更新数据库配置: {database_name}")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        获取环境信息
        
        Returns:
            Dict: 环境信息
        """
        return {
            'current_environment': self.environment,
            'available_environments': self.get_available_environments(),
            'base_config_path': self.config_path,
            'environment_config_loaded': bool(self.env_config),
            'config_errors': self.validate_config()
        }
