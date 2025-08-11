"""
数据质量框架核心模块
支持多数据库、多场景的数据质量检查
"""

__version__ = "2.0.0"
__author__ = "Data Quality Team"

from .engine import DataQualityEngine
from .rule_engine import RuleEngine
from .template_engine import TemplateEngine
from .database_adapters import DatabaseAdapterFactory
from .config_manager import ConfigManager
from .report_generator import ReportGenerator

__all__ = [
    "DataQualityEngine",
    "RuleEngine", 
    "TemplateEngine",
    "DatabaseAdapterFactory",
    "ConfigManager",
    "ReportGenerator"
]
