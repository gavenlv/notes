#!/usr/bin/env python3
"""
数据质量规则引擎
定义、执行和管理数据质量规则
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
import datetime
import re
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RuleType(Enum):
    """规则类型枚举"""
    NOT_NULL = "not_null"                # 非空规则
    RANGE = "range"                      # 范围规则
    REGEX = "regex"                      # 正则表达式规则
    UNIQUE = "unique"                    # 唯一性规则
    FOREIGN_KEY = "foreign_key"          # 外键规则
    LENGTH = "length"                    # 长度规则
    ENUM = "enum"                        # 枚举规则
    CUSTOM = "custom"                    # 自定义规则

class RuleSeverity(Enum):
    """规则严重级别枚举"""
    INFO = "info"                        # 信息
    WARNING = "warning"                  # 警告
    ERROR = "error"                      # 错误
    CRITICAL = "critical"                # 严重

class RuleStatus(Enum):
    """规则状态枚举"""
    ACTIVE = "active"                    # 激活
    INACTIVE = "inactive"                # 未激活
    DRAFT = "draft"                      # 草稿
    ARCHIVED = "archived"                # 已归档

@dataclass
class QualityRule:
    """质量规则数据类"""
    id: str
    name: str
    description: str
    rule_type: RuleType
    severity: RuleSeverity
    status: RuleStatus
    table_name: str
    column_name: str
    parameters: Dict[str, Any]
    message_template: str
    created_by: str
    created_at: datetime.datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['rule_type'] = self.rule_type.value
        data['severity'] = self.severity.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityRule':
        """从字典创建实例"""
        data['rule_type'] = RuleType(data['rule_type'])
        data['severity'] = RuleSeverity(data['severity'])
        data['status'] = RuleStatus(data['status'])
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if data['updated_at']:
            data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
        return cls(**data)

@dataclass
class QualityIssue:
    """质量问题数据类"""
    id: str
    rule_id: str
    table_name: str
    column_name: str
    row_identifier: Any
    issue_type: RuleSeverity
    issue_message: str
    issue_value: Any
    check_date: datetime.datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'table_name': self.table_name,
            'column_name': self.column_name,
            'row_identifier': self.row_identifier,
            'issue_type': self.issue_type.value,
            'issue_message': self.issue_message,
            'issue_value': str(self.issue_value) if self.issue_value is not None else None,
            'check_date': self.check_date.isoformat()
        }

@dataclass
class QualityCheckResult:
    """质量检查结果数据类"""
    rule_id: str
    table_name: str
    total_rows: int
    passed_rows: int
    failed_rows: int
    issues: List[QualityIssue]
    check_date: datetime.datetime
    execution_time_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'table_name': self.table_name,
            'total_rows': self.total_rows,
            'passed_rows': self.passed_rows,
            'failed_rows': self.failed_rows,
            'pass_rate': self.passed_rows / self.total_rows if self.total_rows > 0 else 0,
            'issues': [issue.to_dict() for issue in self.issues],
            'check_date': self.check_date.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

class RuleValidator(ABC):
    """规则验证器抽象基类"""
    
    @abstractmethod
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        """验证规则"""
        pass

class NotNullValidator(RuleValidator):
    """非空验证器"""
    
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        start_time = datetime.datetime.now()
        
        column = rule.column_name
        total_rows = len(df)
        
        # 检查列是否存在
        if column not in df.columns:
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 找出空值
        null_mask = df[column].isnull()
        failed_df = df[null_mask]
        failed_rows = len(failed_df)
        passed_rows = total_rows - failed_rows
        
        # 生成问题列表
        issues = []
        for idx, row in failed_df.iterrows():
            issue_id = str(uuid.uuid4())
            issue_message = rule.message_template.format(
                column=column,
                row_index=idx
            )
            
            issue = QualityIssue(
                id=issue_id,
                rule_id=rule.id,
                table_name=rule.table_name,
                column_name=column,
                row_identifier=idx,
                issue_type=rule.severity,
                issue_message=issue_message,
                issue_value=None,
                check_date=datetime.datetime.now()
            )
            issues.append(issue)
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        return QualityCheckResult(
            rule_id=rule.id,
            table_name=rule.table_name,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            issues=issues,
            check_date=datetime.datetime.now(),
            execution_time_ms=int(execution_time)
        )

class RangeValidator(RuleValidator):
    """范围验证器"""
    
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        start_time = datetime.datetime.now()
        
        column = rule.column_name
        min_val = rule.parameters.get('min_value')
        max_val = rule.parameters.get('max_value')
        inclusive = rule.parameters.get('inclusive', True)
        
        total_rows = len(df)
        
        # 检查列是否存在
        if column not in df.columns:
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 尝试转换为数值
        try:
            numeric_series = pd.to_numeric(df[column], errors='coerce')
        except:
            numeric_series = df[column]
        
        # 检查范围
        if inclusive:
            mask = (numeric_series >= min_val) & (numeric_series <= max_val)
        else:
            mask = (numeric_series > min_val) & (numeric_series < max_val)
        
        # 排除空值
        mask = mask | numeric_series.isnull()
        
        failed_df = df[~mask]
        failed_rows = len(failed_df)
        passed_rows = total_rows - failed_rows
        
        # 生成问题列表
        issues = []
        for idx, row in failed_df.iterrows():
            if pd.isnull(row[column]):  # 跳过空值，由非空规则处理
                continue
                
            issue_id = str(uuid.uuid4())
            issue_message = rule.message_template.format(
                column=column,
                row_index=idx,
                value=row[column],
                min_value=min_val,
                max_value=max_val
            )
            
            issue = QualityIssue(
                id=issue_id,
                rule_id=rule.id,
                table_name=rule.table_name,
                column_name=column,
                row_identifier=idx,
                issue_type=rule.severity,
                issue_message=issue_message,
                issue_value=row[column],
                check_date=datetime.datetime.now()
            )
            issues.append(issue)
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        return QualityCheckResult(
            rule_id=rule.id,
            table_name=rule.table_name,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            issues=issues,
            check_date=datetime.datetime.now(),
            execution_time_ms=int(execution_time)
        )

class RegexValidator(RuleValidator):
    """正则表达式验证器"""
    
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        start_time = datetime.datetime.now()
        
        column = rule.column_name
        pattern = rule.parameters.get('pattern')
        flags = rule.parameters.get('flags', 0)
        
        total_rows = len(df)
        
        # 检查列是否存在
        if column not in df.columns:
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 编译正则表达式
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            logger.error(f"正则表达式编译失败: {pattern}, 错误: {str(e)}")
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 检查正则表达式匹配
        def match_regex(value):
            if pd.isnull(value):
                return True  # 空值跳过检查，由非空规则处理
            return bool(regex.match(str(value)))
        
        mask = df[column].apply(match_regex)
        failed_df = df[~mask]
        failed_rows = len(failed_df)
        passed_rows = total_rows - failed_rows
        
        # 生成问题列表
        issues = []
        for idx, row in failed_df.iterrows():
            if pd.isnull(row[column]):  # 跳过空值
                continue
                
            issue_id = str(uuid.uuid4())
            issue_message = rule.message_template.format(
                column=column,
                row_index=idx,
                value=row[column],
                pattern=pattern
            )
            
            issue = QualityIssue(
                id=issue_id,
                rule_id=rule.id,
                table_name=rule.table_name,
                column_name=column,
                row_identifier=idx,
                issue_type=rule.severity,
                issue_message=issue_message,
                issue_value=row[column],
                check_date=datetime.datetime.now()
            )
            issues.append(issue)
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        return QualityCheckResult(
            rule_id=rule.id,
            table_name=rule.table_name,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            issues=issues,
            check_date=datetime.datetime.now(),
            execution_time_ms=int(execution_time)
        )

class UniqueValidator(RuleValidator):
    """唯一性验证器"""
    
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        start_time = datetime.datetime.now()
        
        column = rule.column_name
        total_rows = len(df)
        
        # 检查列是否存在
        if column not in df.columns:
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 检查唯一性
        duplicate_mask = df[column].duplicated(keep=False)
        failed_df = df[duplicate_mask]
        failed_rows = len(failed_df)
        passed_rows = total_rows - failed_rows
        
        # 生成问题列表
        issues = []
        for idx, row in failed_df.iterrows():
            if pd.isnull(row[column]):  # 跳过空值
                continue
                
            issue_id = str(uuid.uuid4())
            issue_message = rule.message_template.format(
                column=column,
                row_index=idx,
                value=row[column]
            )
            
            issue = QualityIssue(
                id=issue_id,
                rule_id=rule.id,
                table_name=rule.table_name,
                column_name=column,
                row_identifier=idx,
                issue_type=rule.severity,
                issue_message=issue_message,
                issue_value=row[column],
                check_date=datetime.datetime.now()
            )
            issues.append(issue)
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        return QualityCheckResult(
            rule_id=rule.id,
            table_name=rule.table_name,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            issues=issues,
            check_date=datetime.datetime.now(),
            execution_time_ms=int(execution_time)
        )

class EnumValidator(RuleValidator):
    """枚举验证器"""
    
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        start_time = datetime.datetime.now()
        
        column = rule.column_name
        allowed_values = rule.parameters.get('allowed_values', [])
        case_sensitive = rule.parameters.get('case_sensitive', True)
        
        total_rows = len(df)
        
        # 检查列是否存在
        if column not in df.columns:
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 准备允许的值
        if not case_sensitive:
            allowed_values = [str(v).lower() for v in allowed_values]
        
        # 检查枚举值
        def is_allowed(value):
            if pd.isnull(value):
                return True  # 空值跳过检查，由非空规则处理
            
            if not case_sensitive:
                return str(value).lower() in allowed_values
            else:
                return str(value) in allowed_values
        
        mask = df[column].apply(is_allowed)
        failed_df = df[~mask]
        failed_rows = len(failed_df)
        passed_rows = total_rows - failed_rows
        
        # 生成问题列表
        issues = []
        for idx, row in failed_df.iterrows():
            if pd.isnull(row[column]):  # 跳过空值
                continue
                
            issue_id = str(uuid.uuid4())
            issue_message = rule.message_template.format(
                column=column,
                row_index=idx,
                value=row[column],
                allowed_values=', '.join(str(v) for v in allowed_values)
            )
            
            issue = QualityIssue(
                id=issue_id,
                rule_id=rule.id,
                table_name=rule.table_name,
                column_name=column,
                row_identifier=idx,
                issue_type=rule.severity,
                issue_message=issue_message,
                issue_value=row[column],
                check_date=datetime.datetime.now()
            )
            issues.append(issue)
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        return QualityCheckResult(
            rule_id=rule.id,
            table_name=rule.table_name,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            issues=issues,
            check_date=datetime.datetime.now(),
            execution_time_ms=int(execution_time)
        )

class LengthValidator(RuleValidator):
    """长度验证器"""
    
    def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        start_time = datetime.datetime.now()
        
        column = rule.column_name
        min_length = rule.parameters.get('min_length')
        max_length = rule.parameters.get('max_length')
        
        total_rows = len(df)
        
        # 检查列是否存在
        if column not in df.columns:
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=0,
                failed_rows=total_rows,
                issues=[],
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
        
        # 检查长度
        def check_length(value):
            if pd.isnull(value):
                return True  # 空值跳过检查，由非空规则处理
                
            length = len(str(value))
            
            if min_length is not None and length < min_length:
                return False
            
            if max_length is not None and length > max_length:
                return False
                
            return True
        
        mask = df[column].apply(check_length)
        failed_df = df[~mask]
        failed_rows = len(failed_df)
        passed_rows = total_rows - failed_rows
        
        # 生成问题列表
        issues = []
        for idx, row in failed_df.iterrows():
            if pd.isnull(row[column]):  # 跳过空值
                continue
                
            issue_id = str(uuid.uuid4())
            length = len(str(row[column]))
            issue_message = rule.message_template.format(
                column=column,
                row_index=idx,
                value=row[column],
                length=length,
                min_length=min_length,
                max_length=max_length
            )
            
            issue = QualityIssue(
                id=issue_id,
                rule_id=rule.id,
                table_name=rule.table_name,
                column_name=column,
                row_identifier=idx,
                issue_type=rule.severity,
                issue_message=issue_message,
                issue_value=row[column],
                check_date=datetime.datetime.now()
            )
            issues.append(issue)
        
        execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
        return QualityCheckResult(
            rule_id=rule.id,
            table_name=rule.table_name,
            total_rows=total_rows,
            passed_rows=passed_rows,
            failed_rows=failed_rows,
            issues=issues,
            check_date=datetime.datetime.now(),
            execution_time_ms=int(execution_time)
        )

class DataQualityRuleEngine:
    """数据质量规则引擎"""
    
    def __init__(self):
        self.validators = {
            RuleType.NOT_NULL: NotNullValidator(),
            RuleType.RANGE: RangeValidator(),
            RuleType.REGEX: RegexValidator(),
            RuleType.UNIQUE: UniqueValidator(),
            RuleType.ENUM: EnumValidator(),
            RuleType.LENGTH: LengthValidator()
        }
    
    def validate_rule(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
        """验证单个规则"""
        validator = self.validators.get(rule.rule_type)
        if not validator:
            raise ValueError(f"不支持的规则类型: {rule.rule_type}")
        
        return validator.validate(df, rule)
    
    def validate_rules(self, df: pd.DataFrame, rules: List[QualityRule]) -> List[QualityCheckResult]:
        """验证多个规则"""
        results = []
        for rule in rules:
            if rule.status == RuleStatus.ACTIVE:
                try:
                    result = self.validate_rule(df, rule)
                    results.append(result)
                except Exception as e:
                    logger.error(f"验证规则失败: {rule.name}, 错误: {str(e)}")
        return results
    
    def register_validator(self, rule_type: RuleType, validator: RuleValidator):
        """注册自定义验证器"""
        self.validators[rule_type] = validator
        logger.info(f"注册了自定义验证器: {rule_type.value}")

class QualityRuleRepository:
    """质量规则存储库"""
    
    def __init__(self, db_path: str = "quality_rules.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    message_template TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_by TEXT,
                    updated_at TEXT,
                    version INTEGER NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_issues (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    row_identifier TEXT,
                    issue_type TEXT NOT NULL,
                    issue_message TEXT NOT NULL,
                    issue_value TEXT,
                    check_date TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_check_results (
                    rule_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    total_rows INTEGER NOT NULL,
                    passed_rows INTEGER NOT NULL,
                    failed_rows INTEGER NOT NULL,
                    issues TEXT NOT NULL,
                    check_date TEXT NOT NULL,
                    execution_time_ms INTEGER NOT NULL
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_rules_table_column ON quality_rules (table_name, column_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_rules_status ON quality_rules (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_rules_rule_type ON quality_rules (rule_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_issues_rule_id ON quality_issues (rule_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_issues_table_column ON quality_issues (table_name, column_name)")
            
            conn.commit()
    
    def save_rule(self, rule: QualityRule) -> str:
        """保存质量规则"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO quality_rules
                (id, name, description, rule_type, severity, status, table_name, column_name,
                 parameters, message_template, created_by, created_at, updated_by, updated_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.id, rule.name, rule.description, rule.rule_type.value, rule.severity.value,
                rule.status.value, rule.table_name, rule.column_name, json.dumps(rule.parameters),
                rule.message_template, rule.created_by, rule.created_at.isoformat(),
                rule.updated_by, rule.updated_at.isoformat() if rule.updated_at else None,
                rule.version
            ))
            conn.commit()
        
        return rule.id
    
    def get_rule_by_id(self, rule_id: str) -> Optional[QualityRule]:
        """根据ID获取规则"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM quality_rules WHERE id = ?", (rule_id,))
            row = cursor.fetchone()
            
            if row:
                return QualityRule.from_dict(dict(row))
            return None
    
    def get_rules_by_table(self, table_name: str, column_name: str = None) -> List[QualityRule]:
        """根据表名和列名获取规则"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if column_name:
                cursor = conn.execute("""
                    SELECT * FROM quality_rules 
                    WHERE table_name = ? AND column_name = ?
                """, (table_name, column_name))
            else:
                cursor = conn.execute("""
                    SELECT * FROM quality_rules 
                    WHERE table_name = ?
                """, (table_name,))
            
            rows = cursor.fetchall()
            return [QualityRule.from_dict(dict(row)) for row in rows]
    
    def get_all_rules(self, status: RuleStatus = None) -> List[QualityRule]:
        """获取所有规则"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if status:
                cursor = conn.execute("""
                    SELECT * FROM quality_rules 
                    WHERE status = ?
                """, (status.value,))
            else:
                cursor = conn.execute("SELECT * FROM quality_rules")
            
            rows = cursor.fetchall()
            return [QualityRule.from_dict(dict(row)) for row in rows]
    
    def save_check_result(self, result: QualityCheckResult):
        """保存检查结果"""
        with sqlite3.connect(self.db_path) as conn:
            # 保存检查结果摘要
            conn.execute("""
                INSERT INTO quality_check_results
                (rule_id, table_name, total_rows, passed_rows, failed_rows, 
                 issues, check_date, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.rule_id, result.table_name, result.total_rows, result.passed_rows,
                result.failed_rows, json.dumps([issue.to_dict() for issue in result.issues]),
                result.check_date.isoformat(), result.execution_time_ms
            ))
            
            # 保存问题详情
            for issue in result.issues:
                conn.execute("""
                    INSERT INTO quality_issues
                    (id, rule_id, table_name, column_name, row_identifier, 
                     issue_type, issue_message, issue_value, check_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    issue.id, issue.rule_id, issue.table_name, issue.column_name,
                    str(issue.row_identifier), issue.issue_type.value,
                    issue.issue_message, str(issue.issue_value) if issue.issue_value is not None else None,
                    issue.check_date.isoformat()
                ))
            
            conn.commit()
    
    def get_issues_by_table(self, table_name: str, column_name: str = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """根据表名和列名获取问题"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if column_name:
                cursor = conn.execute("""
                    SELECT * FROM quality_issues 
                    WHERE table_name = ? AND column_name = ?
                    ORDER BY check_date DESC
                    LIMIT ?
                """, (table_name, column_name, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM quality_issues 
                    WHERE table_name = ?
                    ORDER BY check_date DESC
                    LIMIT ?
                """, (table_name, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总规则数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_rules")
            total_rules = cursor.fetchone()[0]
            
            # 按状态统计
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM quality_rules 
                GROUP BY status
            """)
            status_distribution = dict(cursor.fetchall())
            
            # 按类型统计
            cursor = conn.execute("""
                SELECT rule_type, COUNT(*) FROM quality_rules 
                GROUP BY rule_type
            """)
            type_distribution = dict(cursor.fetchall())
            
            # 按严重级别统计
            cursor = conn.execute("""
                SELECT severity, COUNT(*) FROM quality_rules 
                GROUP BY severity
            """)
            severity_distribution = dict(cursor.fetchall())
            
            # 总问题数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_issues")
            total_issues = cursor.fetchone()[0]
            
            # 最近7天的问题数
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            cursor = conn.execute("""
                SELECT COUNT(*) FROM quality_issues 
                WHERE check_date >= ?
            """, (seven_days_ago,))
            recent_issues = cursor.fetchone()[0]
            
            return {
                'total_rules': total_rules,
                'status_distribution': status_distribution,
                'type_distribution': type_distribution,
                'severity_distribution': severity_distribution,
                'total_issues': total_issues,
                'recent_issues': recent_issues,
                'last_updated': datetime.datetime.now().isoformat()
            }

class QualityRuleManager:
    """质量规则管理器"""
    
    def __init__(self, engine: DataQualityRuleEngine = None, repository: QualityRuleRepository = None):
        self.engine = engine or DataQualityRuleEngine()
        self.repository = repository or QualityRuleRepository()
    
    def create_rule(self, name: str, description: str, rule_type: RuleType, 
                   severity: RuleSeverity, table_name: str, column_name: str,
                   parameters: Dict[str, Any], message_template: str = None,
                   created_by: str = "system") -> str:
        """创建质量规则"""
        
        # 设置默认消息模板
        if not message_template:
            if rule_type == RuleType.NOT_NULL:
                message_template = "列 '{column}' 在行 {row_index} 不能为空"
            elif rule_type == RuleType.RANGE:
                min_val = parameters.get('min_value')
                max_val = parameters.get('max_value')
                message_template = f"列 '{{column}}' 在行 {{row_index}} 的值 {{{{value}}}} 不在有效范围内 [{min_val}, {max_val}]"
            elif rule_type == RuleType.REGEX:
                pattern = parameters.get('pattern')
                message_template = f"列 '{{column}}' 在行 {{row_index}} 的值 {{{{value}}}} 不符合模式 '{pattern}'"
            elif rule_type == RuleType.UNIQUE:
                message_template = "列 '{column}' 在行 {row_index} 的值 '{value}' 不是唯一的"
            elif rule_type == RuleType.ENUM:
                allowed = parameters.get('allowed_values', [])
                message_template = f"列 '{{column}}' 在行 {{row_index}} 的值 {{{{value}}}} 不在允许的值中 [{', '.join(str(v) for v in allowed)}]"
            elif rule_type == RuleType.LENGTH:
                min_len = parameters.get('min_length')
                max_len = parameters.get('max_length')
                message_template = f"列 '{{column}}' 在行 {{row_index}} 的长度 {{{{length}}}} 不在有效范围内 [{min_len}, {max_len}]"
            else:
                message_template = "列 '{column}' 在行 {row_index} 验证失败"
        
        # 创建规则对象
        rule = QualityRule(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            rule_type=rule_type,
            severity=severity,
            status=RuleStatus.ACTIVE,
            table_name=table_name,
            column_name=column_name,
            parameters=parameters,
            message_template=message_template,
            created_by=created_by,
            created_at=datetime.datetime.now()
        )
        
        # 保存规则
        self.repository.save_rule(rule)
        logger.info(f"创建了质量规则: {name} (ID: {rule.id})")
        
        return rule.id
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any], updated_by: str = "system") -> bool:
        """更新质量规则"""
        rule = self.repository.get_rule_by_id(rule_id)
        if not rule:
            return False
        
        # 应用更新
        if 'name' in updates:
            rule.name = updates['name']
        
        if 'description' in updates:
            rule.description = updates['description']
        
        if 'severity' in updates:
            rule.severity = RuleSeverity(updates['severity'])
        
        if 'status' in updates:
            rule.status = RuleStatus(updates['status'])
        
        if 'parameters' in updates:
            rule.parameters = updates['parameters']
        
        if 'message_template' in updates:
            rule.message_template = updates['message_template']
        
        rule.updated_by = updated_by
        rule.updated_at = datetime.datetime.now()
        rule.version += 1
        
        # 保存更新
        self.repository.save_rule(rule)
        return True
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """获取规则详情"""
        rule = self.repository.get_rule_by_id(rule_id)
        return rule.to_dict() if rule else None
    
    def get_rules_by_table(self, table_name: str, column_name: str = None) -> List[Dict[str, Any]]:
        """根据表名和列名获取规则"""
        rules = self.repository.get_rules_by_table(table_name, column_name)
        return [rule.to_dict() for rule in rules]
    
    def get_all_rules(self, status: str = None) -> List[Dict[str, Any]]:
        """获取所有规则"""
        rule_status = RuleStatus(status) if status else None
        rules = self.repository.get_all_rules(rule_status)
        return [rule.to_dict() for rule in rules]
    
    def run_rules_on_table(self, df: pd.DataFrame, table_name: str, column_name: str = None) -> List[Dict[str, Any]]:
        """对表运行规则"""
        # 获取表的规则
        rules = self.repository.get_rules_by_table(table_name, column_name)
        
        if not rules:
            logger.warning(f"表 {table_name} 没有定义质量规则")
            return []
        
        # 执行规则验证
        results = self.engine.validate_rules(df, rules)
        
        # 保存检查结果
        for result in results:
            self.repository.save_check_result(result)
        
        # 转换为字典并返回
        return [result.to_dict() for result in results]
    
    def get_table_issues(self, table_name: str, column_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取表的问题"""
        return self.repository.get_issues_by_table(table_name, column_name, limit)
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        return self.repository.get_rule_statistics()
    
    def create_common_rules(self, table_name: str, df: pd.DataFrame, created_by: str = "system") -> List[str]:
        """为表创建常用规则"""
        created_rule_ids = []
        
        # 为每列创建规则
        for column in df.columns:
            # 非空规则（如果没有太多空值）
            null_ratio = df[column].isnull().sum() / len(df)
            if null_ratio < 0.5:  # 如果空值比例小于50%，创建非空规则
                rule_id = self.create_rule(
                    name=f"{table_name}_{column}_not_null",
                    description=f"确保 {table_name}.{column} 不为空",
                    rule_type=RuleType.NOT_NULL,
                    severity=RuleSeverity.ERROR,
                    table_name=table_name,
                    column_name=column,
                    parameters={},
                    created_by=created_by
                )
                created_rule_ids.append(rule_id)
            
            # 对于数值型列，创建范围规则
            try:
                numeric_series = pd.to_numeric(df[column], errors='coerce')
                if not numeric_series.isnull().all():
                    # 使用IQR方法计算范围
                    Q1 = numeric_series.quantile(0.25)
                    Q3 = numeric_series.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    # 设置合理的范围，排除极端异常值
                    min_val = max(Q1 - 3 * IQR, numeric_series.min())
                    max_val = min(Q3 + 3 * IQR, numeric_series.max())
                    
                    rule_id = self.create_rule(
                        name=f"{table_name}_{column}_range",
                        description=f"确保 {table_name}.{column} 在合理范围内",
                        rule_type=RuleType.RANGE,
                        severity=RuleSeverity.WARNING,
                        table_name=table_name,
                        column_name=column,
                        parameters={
                            'min_value': min_val,
                            'max_value': max_val,
                            'inclusive': True
                        },
                        created_by=created_by
                    )
                    created_rule_ids.append(rule_id)
            except:
                pass
            
            # 对于字符串列，创建长度规则
            if df[column].dtype == 'object':
                try:
                    lengths = df[column].dropna().apply(len)
                    if len(lengths) > 0:
                        # 设置合理的长度范围（基于数据的99%分位数）
                        max_length = lengths.quantile(0.99)
                        
                        rule_id = self.create_rule(
                            name=f"{table_name}_{column}_length",
                            description=f"确保 {table_name}.{column} 长度在合理范围内",
                            rule_type=RuleType.LENGTH,
                            severity=RuleSeverity.WARNING,
                            table_name=table_name,
                            column_name=column,
                            parameters={
                                'min_length': 0,
                                'max_length': int(max_length) + 10  # 给一些余量
                            },
                            created_by=created_by
                        )
                        created_rule_ids.append(rule_id)
                except:
                    pass
        
        return created_rule_ids

def main():
    """主函数，演示数据质量规则引擎使用"""
    print("=" * 50)
    print("数据质量规则引擎演示")
    print("=" * 50)
    
    # 创建质量规则管理器
    manager = QualityRuleManager()
    
    # 1. 创建示例数据
    print("\n1. 创建示例数据...")
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com', 
                  'eve@example.com', 'frank@example.com', 'grace@example.com', 'henry@example.com',
                  'ivy@example.com', 'invalid-email'],  # 包含一个无效邮箱
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 200],  # 包含一个异常年龄
        'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing', 'HR', 'IT', 'Finance', 'Marketing', None],  # 包含一个空值
        'join_date': ['2020-01-15', '2019-05-20', '2018-11-10', '2021-02-28', 
                      '2017-07-05', '2022-03-12', '2016-09-18', '2023-01-25', 
                      '2015-04-30', 'invalid-date']  # 包含一个无效日期
    }
    
    df = pd.DataFrame(data)
    print(f"创建了示例DataFrame，包含 {len(df)} 行和 {len(df.columns)} 列")
    
    # 2. 创建质量规则
    print("\n2. 创建质量规则...")
    
    # ID列 - 非空和唯一性规则
    id_not_null_rule = manager.create_rule(
        name="employees_id_not_null",
        description="确保员工ID不为空",
        rule_type=RuleType.NOT_NULL,
        severity=RuleSeverity.ERROR,
        table_name="employees",
        column_name="id",
        parameters={}
    )
    
    id_unique_rule = manager.create_rule(
        name="employees_id_unique",
        description="确保员工ID唯一",
        rule_type=RuleType.UNIQUE,
        severity=RuleSeverity.ERROR,
        table_name="employees",
        column_name="id",
        parameters={}
    )
    
    # 邮箱列 - 正则表达式规则
    email_regex_rule = manager.create_rule(
        name="employees_email_format",
        description="确保邮箱格式正确",
        rule_type=RuleType.REGEX,
        severity=RuleSeverity.ERROR,
        table_name="employees",
        column_name="email",
        parameters={
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'flags': 0
        }
    )
    
    # 年龄列 - 范围规则
    age_range_rule = manager.create_rule(
        name="employees_age_range",
        description="确保年龄在合理范围内",
        rule_type=RuleType.RANGE,
        severity=RuleSeverity.WARNING,
        table_name="employees",
        column_name="age",
        parameters={
            'min_value': 18,
            'max_value': 65,
            'inclusive': True
        }
    )
    
    # 部门列 - 枚举规则
    department_enum_rule = manager.create_rule(
        name="employees_department_enum",
        description="确保部门值在允许的范围内",
        rule_type=RuleType.ENUM,
        severity=RuleSeverity.WARNING,
        table_name="employees",
        column_name="department",
        parameters={
            'allowed_values': ['IT', 'HR', 'Finance', 'Marketing'],
            'case_sensitive': True
        }
    )
    
    # 加入日期列 - 正则表达式规则
    join_date_regex_rule = manager.create_rule(
        name="employees_join_date_format",
        description="确保加入日期格式正确",
        rule_type=RuleType.REGEX,
        severity=RuleSeverity.ERROR,
        table_name="employees",
        column_name="join_date",
        parameters={
            'pattern': r'^\d{4}-\d{2}-\d{2}$',
            'flags': 0
        }
    )
    
    print(f"创建了 6 个质量规则")
    
    # 3. 获取所有规则
    print("\n3. 获取所有规则...")
    rules = manager.get_all_rules()
    print(f"总共有 {len(rules)} 个规则:")
    for rule in rules:
        print(f"- {rule['name']} ({rule['rule_type']}) - {rule['status']}")
    
    # 4. 对数据运行规则
    print("\n4. 对数据运行规则...")
    results = manager.run_rules_on_table(df, "employees")
    
    print(f"执行了 {len(results)} 个规则检查:")
    for result in results:
        rule_id = result['rule_id']
        rule = manager.get_rule(rule_id)
        rule_name = rule['name'] if rule else "未知规则"
        total_rows = result['total_rows']
        passed_rows = result['passed_rows']
        failed_rows = result['failed_rows']
        pass_rate = result['pass_rate']
        
        print(f"- {rule_name}: {passed_rows}/{total_rows} 通过 ({pass_rate:.1%}), {failed_rows} 失败")
    
    # 5. 获取质量问题
    print("\n5. 获取质量问题...")
    issues = manager.get_table_issues("employees", limit=20)
    print(f"发现 {len(issues)} 个质量问题:")
    
    # 按规则分组显示问题
    issues_by_rule = {}
    for issue in issues:
        rule_id = issue['rule_id']
        if rule_id not in issues_by_rule:
            rule = manager.get_rule(rule_id)
            rule_name = rule['name'] if rule else "未知规则"
            issues_by_rule[rule_id] = {
                'rule_name': rule_name,
                'issues': []
            }
        issues_by_rule[rule_id]['issues'].append(issue)
    
    for rule_id, info in issues_by_rule.items():
        print(f"\n规则: {info['rule_name']}")
        for issue in info['issues'][:3]:  # 只显示前3个问题
            print(f"  - 行 {issue['row_identifier']}: {issue['issue_message']}")
        
        if len(info['issues']) > 3:
            print(f"  ... 还有 {len(info['issues']) - 3} 个问题")
    
    # 6. 自动创建常用规则
    print("\n6. 自动创建常用规则...")
    auto_rule_ids = manager.create_common_rules("auto_generated", df)
    print(f"自动创建了 {len(auto_rule_ids)} 个常用规则")
    
    # 7. 获取规则统计信息
    print("\n7. 获取规则统计信息...")
    stats = manager.get_rule_statistics()
    print(f"总规则数: {stats['total_rules']}")
    print(f"状态分布: {stats['status_distribution']}")
    print(f"类型分布: {stats['type_distribution']}")
    print(f"严重级别分布: {stats['severity_distribution']}")
    print(f"总问题数: {stats['total_issues']}")
    print(f"最近7天问题数: {stats['recent_issues']}")
    
    # 8. 更新规则状态
    print("\n8. 更新规则状态...")
    # 更新第一个规则为非激活状态
    if rules:
        rule_id = rules[0]['id']
        success = manager.update_rule(rule_id, {'status': 'inactive'}, "演示用户")
        print(f"更新规则 {rules[0]['name']} 状态为非激活: {'成功' if success else '失败'}")
    
    # 9. 创建自定义验证器（演示）
    print("\n9. 创建自定义验证器（演示）...")
    
    class CustomValidator(RuleValidator):
        """自定义验证器示例：检查ID是否为偶数"""
        
        def validate(self, df: pd.DataFrame, rule: QualityRule) -> QualityCheckResult:
            start_time = datetime.datetime.now()
            
            column = rule.column_name
            total_rows = len(df)
            
            # 检查列是否存在
            if column not in df.columns:
                execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
                return QualityCheckResult(
                    rule_id=rule.id,
                    table_name=rule.table_name,
                    total_rows=total_rows,
                    passed_rows=0,
                    failed_rows=total_rows,
                    issues=[],
                    check_date=datetime.datetime.now(),
                    execution_time_ms=int(execution_time)
                )
            
            # 检查ID是否为偶数
            try:
                is_even = df[column] % 2 == 0
            except:
                is_even = pd.Series([False] * total_rows)
            
            failed_df = df[~is_even]
            failed_rows = len(failed_df)
            passed_rows = total_rows - failed_rows
            
            # 生成问题列表
            issues = []
            for idx, row in failed_df.iterrows():
                issue_id = str(uuid.uuid4())
                issue_message = rule.message_template.format(
                    column=column,
                    row_index=idx,
                    value=row[column]
                )
                
                issue = QualityIssue(
                    id=issue_id,
                    rule_id=rule.id,
                    table_name=rule.table_name,
                    column_name=column,
                    row_identifier=idx,
                    issue_type=rule.severity,
                    issue_message=issue_message,
                    issue_value=row[column],
                    check_date=datetime.datetime.now()
                )
                issues.append(issue)
            
            execution_time = (datetime.datetime.now() - start_time).total_seconds() * 1000
            return QualityCheckResult(
                rule_id=rule.id,
                table_name=rule.table_name,
                total_rows=total_rows,
                passed_rows=passed_rows,
                failed_rows=failed_rows,
                issues=issues,
                check_date=datetime.datetime.now(),
                execution_time_ms=int(execution_time)
            )
    
    # 注册自定义验证器
    manager.engine.register_validator(RuleType.CUSTOM, CustomValidator())
    
    # 创建自定义规则
    custom_rule_id = manager.create_rule(
        name="employees_id_even",
        description="确保员工ID为偶数（自定义规则示例）",
        rule_type=RuleType.CUSTOM,
        severity=RuleSeverity.WARNING,
        table_name="employees",
        column_name="id",
        parameters={},
        message_template="列 '{column}' 在行 {row_index} 的值 '{value}' 不是偶数"
    )
    
    # 运行自定义规则
    custom_results = manager.run_rules_on_table(df, "employees", "id")
    custom_result = [r for r in custom_results if r['rule_id'] == custom_rule_id][0]
    
    print(f"自定义规则结果: {custom_result['passed_rows']}/{custom_result['total_rows']} 通过, {custom_result['failed_rows']} 失败")

if __name__ == "__main__":
    main()