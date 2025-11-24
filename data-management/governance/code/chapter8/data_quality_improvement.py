#!/usr/bin/env python3
"""
数据质量改进工具
提供数据质量问题分析和改进建议
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

class IssueSeverity(Enum):
    """问题严重程度枚举"""
    LOW = "low"                        # 低
    MEDIUM = "medium"                  # 中
    HIGH = "high"                      # 高
    CRITICAL = "critical"              # 严重

class IssueCategory(Enum):
    """问题类别枚举"""
    COMPLETENESS = "completeness"      # 完整性问题
    VALIDITY = "validity"              # 有效性问题
    ACCURACY = "accuracy"              # 准确性问题
    CONSISTENCY = "consistency"        # 一致性问题
    UNIQUENESS = "uniqueness"          # 唯一性问题
    TIMELINESS = "timeliness"          # 及时性问题

class ImprovementStatus(Enum):
    """改进状态枚举"""
    PENDING = "pending"                # 待处理
    IN_PROGRESS = "in_progress"        # 进行中
    COMPLETED = "completed"            # 已完成
    CANCELLED = "cancelled"            # 已取消
    ON_HOLD = "on_hold"                # 暂停

class RecommendationType(Enum):
    """建议类型枚举"""
    DATA_CLEANING = "data_cleaning"    # 数据清洗
    VALIDATION_RULE = "validation_rule" # 验证规则
    PROCESS_CHANGE = "process_change"  # 流程变更
    SYSTEM_CHANGE = "system_change"    # 系统变更
    TRAINING = "training"              # 培训
    MONITORING = "monitoring"          # 监控

@dataclass
class QualityIssue:
    """质量问题数据类"""
    id: str
    table_name: str
    column_name: str
    row_identifier: Any
    issue_type: str
    issue_category: IssueCategory
    severity: IssueSeverity
    description: str
    detected_at: datetime.datetime
    source: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'table_name': self.table_name,
            'column_name': self.column_name,
            'row_identifier': str(self.row_identifier) if self.row_identifier is not None else None,
            'issue_type': self.issue_type,
            'issue_category': self.issue_category.value,
            'severity': self.severity.value,
            'description': self.description,
            'detected_at': self.detected_at.isoformat(),
            'source': self.source,
            'metadata': self.metadata
        }

@dataclass
class QualityRecommendation:
    """质量改进建议数据类"""
    id: str
    issue_id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    priority: int  # 1-10, 10为最高优先级
    effort: int  # 1-10, 10为最高工作量
    impact: int  # 1-10, 10为最高影响
    implementation_steps: List[str]
    prerequisites: List[str]
    expected_outcome: str
    created_at: datetime.datetime
    created_by: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'recommendation_type': self.recommendation_type.value,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'effort': self.effort,
            'impact': self.impact,
            'implementation_steps': self.implementation_steps,
            'prerequisites': self.prerequisites,
            'expected_outcome': self.expected_outcome,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }

@dataclass
class ImprovementPlan:
    """改进计划数据类"""
    id: str
    name: str
    description: str
    table_name: str
    issue_ids: List[str]
    recommendation_ids: List[str]
    status: ImprovementStatus
    assignee: str
    due_date: datetime.datetime
    created_at: datetime.datetime
    created_by: str
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    completion_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'table_name': self.table_name,
            'issue_ids': self.issue_ids,
            'recommendation_ids': self.recommendation_ids,
            'status': self.status.value,
            'assignee': self.assignee,
            'due_date': self.due_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
            'completion_percentage': self.completion_percentage
        }

class DataQualityImprovement:
    """数据质量改进分析器"""
    
    def __init__(self):
        pass
    
    def analyze_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析问题模式"""
        if not issues:
            return {"message": "没有问题需要分析"}
        
        # 按类别统计
        category_counts = {}
        for issue in issues:
            category = issue.get('issue_category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 按严重程度统计
        severity_counts = {}
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # 按表统计
        table_counts = {}
        for issue in issues:
            table = issue.get('table_name', 'unknown')
            table_counts[table] = table_counts.get(table, 0) + 1
        
        # 按列统计
        column_counts = {}
        for issue in issues:
            column = issue.get('column_name', 'unknown')
            table = issue.get('table_name', 'unknown')
            key = f"{table}.{column}"
            column_counts[key] = column_counts.get(key, 0) + 1
        
        # 按时间趋势分析
        time_trend = {}
        for issue in issues:
            date_str = issue.get('detected_at', '')
            if date_str:
                try:
                    date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_key = date.strftime('%Y-%m-%d')
                    time_trend[date_key] = time_trend.get(date_key, 0) + 1
                except:
                    pass
        
        # 找出最常见的问题类型
        most_common_category = max(category_counts.items(), key=lambda x: x[1]) if category_counts else None
        most_severe_issues = [issue for issue in issues if issue.get('severity') == 'critical']
        tables_with_most_issues = sorted(table_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_issues': len(issues),
            'category_distribution': category_counts,
            'severity_distribution': severity_counts,
            'table_distribution': table_counts,
            'column_distribution': column_counts,
            'time_trend': time_trend,
            'most_common_category': most_common_category,
            'most_severe_issues_count': len(most_severe_issues),
            'tables_with_most_issues': tables_with_most_issues
        }
    
    def generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成改进建议"""
        recommendations = []
        
        if not issues:
            return recommendations
        
        # 按类别分组问题
        issues_by_category = {}
        for issue in issues:
            category = issue.get('issue_category', 'unknown')
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue)
        
        # 为每个类别生成建议
        for category, category_issues in issues_by_category.items():
            if category == IssueCategory.COMPLETENESS.value:
                recommendations.extend(self._generate_completeness_recommendations(category_issues))
            elif category == IssueCategory.VALIDITY.value:
                recommendations.extend(self._generate_validity_recommendations(category_issues))
            elif category == IssueCategory.ACCURACY.value:
                recommendations.extend(self._generate_accuracy_recommendations(category_issues))
            elif category == IssueCategory.CONSISTENCY.value:
                recommendations.extend(self._generate_consistency_recommendations(category_issues))
            elif category == IssueCategory.UNIQUENESS.value:
                recommendations.extend(self._generate_uniqueness_recommendations(category_issues))
            elif category == IssueCategory.TIMELINESS.value:
                recommendations.extend(self._generate_timeliness_recommendations(category_issues))
        
        return recommendations
    
    def _generate_completeness_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成完整性问题的建议"""
        recommendations = []
        
        # 按表分组
        issues_by_table = {}
        for issue in issues:
            table = issue.get('table_name', 'unknown')
            if table not in issues_by_table:
                issues_by_table[table] = []
            issues_by_table[table].append(issue)
        
        # 为每个表生成建议
        for table, table_issues in issues_by_table.items():
            # 按列分组
            issues_by_column = {}
            for issue in table_issues:
                column = issue.get('column_name', 'unknown')
                if column not in issues_by_column:
                    issues_by_column[column] = []
                issues_by_column[column].append(issue)
            
            # 为每个列生成建议
            for column, column_issues in issues_by_column.items():
                # 计算问题严重程度
                critical_count = sum(1 for issue in column_issues if issue.get('severity') == 'critical')
                high_count = sum(1 for issue in column_issues if issue.get('severity') == 'high')
                medium_count = sum(1 for issue in column_issues if issue.get('severity') == 'medium')
                
                # 确定优先级
                priority = min(10, (critical_count * 3 + high_count * 2 + medium_count))
                
                # 确定工作量
                issue_count = len(column_issues)
                effort = min(10, issue_count / 10) if issue_count < 100 else 10
                
                # 确定影响
                impact = min(10, issue_count / 5) if issue_count < 50 else 10
                
                # 创建建议
                recommendation = QualityRecommendation(
                    id=str(uuid.uuid4()),
                    issue_id=column_issues[0]['id'],  # 使用第一个问题的ID
                    recommendation_type=RecommendationType.DATA_CLEANING,
                    title=f"修复 {table}.{column} 的缺失值",
                    description=f"发现 {len(column_issues)} 条 {column} 列的缺失值问题",
                    priority=priority,
                    effort=effort,
                    impact=impact,
                    implementation_steps=[
                        f"1. 分析 {column} 列缺失值的模式和原因",
                        f"2. 确定 {column} 列的默认值或填充策略",
                        f"3. 实施数据清洗脚本填充缺失值",
                        f"4. 添加非空约束防止未来的缺失值",
                        f"5. 验证修复结果"
                    ],
                    prerequisites=[
                        "备份原始数据",
                        "了解 {column} 列的业务含义"
                    ],
                    expected_outcome=f"消除 {column} 列的所有缺失值，提高数据完整性",
                    created_at=datetime.datetime.now(),
                    created_by="系统分析"
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_validity_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成有效性问题的建议"""
        recommendations = []
        
        # 按表分组
        issues_by_table = {}
        for issue in issues:
            table = issue.get('table_name', 'unknown')
            if table not in issues_by_table:
                issues_by_table[table] = []
            issues_by_table[table].append(issue)
        
        # 为每个表生成建议
        for table, table_issues in issues_by_table.items():
            # 创建验证规则建议
            recommendation = QualityRecommendation(
                id=str(uuid.uuid4()),
                issue_id=table_issues[0]['id'],
                recommendation_type=RecommendationType.VALIDATION_RULE,
                title=f"为 {table} 表添加数据验证规则",
                description=f"发现 {len(table_issues)} 条数据格式或范围不正确的问题",
                priority=8,
                effort=6,
                impact=9,
                implementation_steps=[
                    f"1. 分析 {table} 表的数据模式",
                    "2. 确定每个列的有效值范围和格式",
                    "3. 创建数据验证规则",
                    "4. 实施验证检查机制",
                    "5. 在数据输入点添加验证"
                ],
                prerequisites=[
                    "了解 {table} 表的业务规则",
                    "获取数据验证权限"
                ],
                expected_outcome="防止未来的数据有效性问题，提高数据质量",
                created_at=datetime.datetime.now(),
                created_by="系统分析"
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_accuracy_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成准确性问题的建议"""
        recommendations = []
        
        # 按表分组
        issues_by_table = {}
        for issue in issues:
            table = issue.get('table_name', 'unknown')
            if table not in issues_by_table:
                issues_by_table[table] = []
            issues_by_table[table].append(issue)
        
        # 为每个表生成建议
        for table, table_issues in issues_by_table.items():
            # 创建数据源验证建议
            recommendation = QualityRecommendation(
                id=str(uuid.uuid4()),
                issue_id=table_issues[0]['id'],
                recommendation_type=RecommendationType.PROCESS_CHANGE,
                title=f"改进 {table} 表的数据源验证",
                description=f"发现 {len(table_issues)} 条数据准确性问题",
                priority=9,
                effort=7,
                impact=8,
                implementation_steps=[
                    f"1. 分析 {table} 表的数据来源",
                    "2. 识别数据传输过程中的潜在问题",
                    "3. 改进数据源验证机制",
                    "4. 实施数据源质量检查",
                    "5. 建立数据准确性监控"
                ],
                prerequisites=[
                    "了解 {table} 表的数据来源",
                    "与数据源团队合作"
                ],
                expected_outcome="提高数据的准确性，减少错误数据",
                created_at=datetime.datetime.now(),
                created_by="系统分析"
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_consistency_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成一致性问题的建议"""
        recommendations = []
        
        # 创建主数据管理建议
        recommendation = QualityRecommendation(
            id=str(uuid.uuid4()),
            issue_id=issues[0]['id'],
            recommendation_type=RecommendationType.SYSTEM_CHANGE,
            title="实施主数据管理解决方案",
            description=f"发现 {len(issues)} 条数据一致性问题",
            priority=7,
            effort=9,
            impact=8,
            implementation_steps=[
                "1. 识别关键的主数据实体",
                "2. 设计主数据模型和标准",
                "3. 实施主数据管理系统",
                "4. 建立数据同步机制",
                "5. 推广主数据使用"
            ],
            prerequisites=[
                "获取管理层支持",
                "主数据管理工具评估"
            ],
            expected_outcome="确保关键数据在各系统间的一致性",
            created_at=datetime.datetime.now(),
            created_by="系统分析"
        )
        
        recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_uniqueness_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成唯一性问题的建议"""
        recommendations = []
        
        # 按表分组
        issues_by_table = {}
        for issue in issues:
            table = issue.get('table_name', 'unknown')
            if table not in issues_by_table:
                issues_by_table[table] = []
            issues_by_table[table].append(issue)
        
        # 为每个表生成建议
        for table, table_issues in issues_by_table.items():
            # 创建去重建议
            recommendation = QualityRecommendation(
                id=str(uuid.uuid4()),
                issue_id=table_issues[0]['id'],
                recommendation_type=RecommendationType.DATA_CLEANING,
                title=f"清理 {table} 表的重复数据",
                description=f"发现 {len(table_issues)} 条重复数据问题",
                priority=8,
                effort=5,
                impact=7,
                implementation_steps=[
                    f"1. 分析 {table} 表的重复模式",
                    "2. 确定保留记录的标准",
                    "3. 实施去重脚本",
                    "4. 添加唯一约束防止未来的重复",
                    "5. 验证去重结果"
                ],
                prerequisites=[
                    "备份原始数据",
                    "确定重复记录的判断标准"
                ],
                expected_outcome=f"消除 {table} 表的重复数据，确保记录唯一性",
                created_at=datetime.datetime.now(),
                created_by="系统分析"
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_timeliness_recommendations(self, issues: List[Dict[str, Any]]) -> List[QualityRecommendation]:
        """生成及时性问题的建议"""
        recommendations = []
        
        # 创建数据更新流程改进建议
        recommendation = QualityRecommendation(
            id=str(uuid.uuid4()),
            issue_id=issues[0]['id'],
            recommendation_type=RecommendationType.PROCESS_CHANGE,
            title="改进数据更新流程",
            description=f"发现 {len(issues)} 条数据及时性问题",
            priority=7,
            effort=6,
            impact=8,
            implementation_steps=[
                "1. 分析当前数据更新流程",
                "2. 识别流程中的瓶颈",
                "3. 设计优化的数据更新流程",
                "4. 实施自动化更新机制",
                "5. 建立数据及时性监控"
            ],
            prerequisites=[
                "了解当前数据更新流程",
                "流程改进授权"
            ],
            expected_outcome="提高数据的及时性，确保数据在需要时可用",
            created_at=datetime.datetime.now(),
            created_by="系统分析"
        )
        
        recommendations.append(recommendation)
        
        return recommendations
    
    def prioritize_recommendations(self, recommendations: List[QualityRecommendation]) -> List[QualityRecommendation]:
        """优先级排序建议"""
        # 按优先级、影响和工作量的综合分数排序
        def score(rec):
            # 优先级权重50%，影响权重30%，工作量负权重20%
            return (rec.priority * 0.5 + rec.impact * 0.3 - rec.effort * 0.2)
        
        return sorted(recommendations, key=score, reverse=True)

class QualityImprovementRepository:
    """质量改进存储库"""
    
    def __init__(self, db_path: str = "quality_improvement.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_issues (
                    id TEXT PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    row_identifier TEXT,
                    issue_type TEXT NOT NULL,
                    issue_category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_recommendations (
                    id TEXT PRIMARY KEY,
                    issue_id TEXT NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    effort INTEGER NOT NULL,
                    impact INTEGER NOT NULL,
                    implementation_steps TEXT NOT NULL,
                    prerequisites TEXT NOT NULL,
                    expected_outcome TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS improvement_plans (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    issue_ids TEXT NOT NULL,
                    recommendation_ids TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assignee TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    updated_at TEXT,
                    updated_by TEXT,
                    completion_percentage REAL NOT NULL
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_issues_table_name ON quality_issues (table_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_issues_category ON quality_issues (issue_category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_issues_severity ON quality_issues (severity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_recommendations_issue_id ON quality_recommendations (issue_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_recommendations_type ON quality_recommendations (recommendation_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_improvement_plans_table_name ON improvement_plans (table_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_improvement_plans_status ON improvement_plans (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_improvement_plans_assignee ON improvement_plans (assignee)")
            
            conn.commit()
    
    def save_issue(self, issue: QualityIssue) -> str:
        """保存质量问题"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO quality_issues
                (id, table_name, column_name, row_identifier, issue_type,
                 issue_category, severity, description, detected_at, source, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue.id, issue.table_name, issue.column_name,
                str(issue.row_identifier) if issue.row_identifier is not None else None,
                issue.issue_type, issue.issue_category.value, issue.severity.value,
                issue.description, issue.detected_at.isoformat(), issue.source,
                json.dumps(issue.metadata)
            ))
            conn.commit()
        
        return issue.id
    
    def save_recommendation(self, recommendation: QualityRecommendation) -> str:
        """保存改进建议"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO quality_recommendations
                (id, issue_id, recommendation_type, title, description,
                 priority, effort, impact, implementation_steps, prerequisites,
                 expected_outcome, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recommendation.id, recommendation.issue_id, recommendation.recommendation_type.value,
                recommendation.title, recommendation.description, recommendation.priority,
                recommendation.effort, recommendation.impact, json.dumps(recommendation.implementation_steps),
                json.dumps(recommendation.prerequisites), recommendation.expected_outcome,
                recommendation.created_at.isoformat(), recommendation.created_by
            ))
            conn.commit()
        
        return recommendation.id
    
    def save_improvement_plan(self, plan: ImprovementPlan) -> str:
        """保存改进计划"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO improvement_plans
                (id, name, description, table_name, issue_ids, recommendation_ids,
                 status, assignee, due_date, created_at, created_by,
                 updated_at, updated_by, completion_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan.id, plan.name, plan.description, plan.table_name,
                json.dumps(plan.issue_ids), json.dumps(plan.recommendation_ids),
                plan.status.value, plan.assignee, plan.due_date.isoformat(),
                plan.created_at.isoformat(), plan.created_by,
                plan.updated_at.isoformat() if plan.updated_at else None,
                plan.updated_by, plan.completion_percentage
            ))
            conn.commit()
        
        return plan.id
    
    def get_issues_by_table(self, table_name: str, limit: int = 100) -> List[QualityIssue]:
        """根据表名获取问题"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_issues
                WHERE table_name = ?
                ORDER BY detected_at DESC
                LIMIT ?
            """, (table_name, limit))
            
            rows = cursor.fetchall()
            issues = []
            for row in rows:
                data = dict(row)
                data['issue_category'] = IssueCategory(data['issue_category'])
                data['severity'] = IssueSeverity(data['severity'])
                data['detected_at'] = datetime.datetime.fromisoformat(data['detected_at'])
                data['metadata'] = json.loads(data['metadata'])
                issues.append(QualityIssue(**data))
            
            return issues
    
    def get_recommendations_by_issue(self, issue_id: str) -> List[QualityRecommendation]:
        """根据问题ID获取建议"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_recommendations
                WHERE issue_id = ?
                ORDER BY priority DESC, impact DESC
            """, (issue_id,))
            
            rows = cursor.fetchall()
            recommendations = []
            for row in rows:
                data = dict(row)
                data['recommendation_type'] = RecommendationType(data['recommendation_type'])
                data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
                data['implementation_steps'] = json.loads(data['implementation_steps'])
                data['prerequisites'] = json.loads(data['prerequisites'])
                recommendations.append(QualityRecommendation(**data))
            
            return recommendations
    
    def get_all_improvement_plans(self, status: str = None) -> List[ImprovementPlan]:
        """获取所有改进计划"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if status:
                cursor = conn.execute("""
                    SELECT * FROM improvement_plans
                    WHERE status = ?
                    ORDER BY due_date ASC
                """, (status,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM improvement_plans
                    ORDER BY due_date ASC
                """)
            
            rows = cursor.fetchall()
            plans = []
            for row in rows:
                data = dict(row)
                data['status'] = ImprovementStatus(data['status'])
                data['issue_ids'] = json.loads(data['issue_ids'])
                data['recommendation_ids'] = json.loads(data['recommendation_ids'])
                data['due_date'] = datetime.datetime.fromisoformat(data['due_date'])
                data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
                if data['updated_at']:
                    data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
                plans.append(ImprovementPlan(**data))
            
            return plans
    
    def update_improvement_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """更新改进计划"""
        with sqlite3.connect(self.db_path) as conn:
            # 构建更新语句
            set_clauses = []
            params = []
            
            if 'name' in updates:
                set_clauses.append("name = ?")
                params.append(updates['name'])
            
            if 'description' in updates:
                set_clauses.append("description = ?")
                params.append(updates['description'])
            
            if 'status' in updates:
                set_clauses.append("status = ?")
                params.append(updates['status'])
            
            if 'assignee' in updates:
                set_clauses.append("assignee = ?")
                params.append(updates['assignee'])
            
            if 'due_date' in updates:
                set_clauses.append("due_date = ?")
                params.append(updates['due_date'])
            
            if 'completion_percentage' in updates:
                set_clauses.append("completion_percentage = ?")
                params.append(updates['completion_percentage'])
            
            if 'updated_by' in updates:
                set_clauses.append("updated_by = ?")
                params.append(updates['updated_by'])
            
            if not set_clauses:
                return False
            
            # 添加更新时间
            set_clauses.append("updated_at = ?")
            params.append(datetime.datetime.now().isoformat())
            
            # 添加计划ID
            params.append(plan_id)
            
            # 执行更新
            sql = f"UPDATE improvement_plans SET {', '.join(set_clauses)} WHERE id = ?"
            cursor = conn.execute(sql, params)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_improvement_statistics(self) -> Dict[str, Any]:
        """获取改进统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总问题数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_issues")
            total_issues = cursor.fetchone()[0]
            
            # 按类别统计问题
            cursor = conn.execute("""
                SELECT issue_category, COUNT(*) FROM quality_issues
                GROUP BY issue_category
            """)
            issue_category_distribution = dict(cursor.fetchall())
            
            # 按严重程度统计问题
            cursor = conn.execute("""
                SELECT severity, COUNT(*) FROM quality_issues
                GROUP BY severity
            """)
            issue_severity_distribution = dict(cursor.fetchall())
            
            # 总建议数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_recommendations")
            total_recommendations = cursor.fetchone()[0]
            
            # 按类型统计建议
            cursor = conn.execute("""
                SELECT recommendation_type, COUNT(*) FROM quality_recommendations
                GROUP BY recommendation_type
            """)
            recommendation_type_distribution = dict(cursor.fetchall())
            
            # 总计划数
            cursor = conn.execute("SELECT COUNT(*) FROM improvement_plans")
            total_plans = cursor.fetchone()[0]
            
            # 按状态统计计划
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM improvement_plans
                GROUP BY status
            """)
            plan_status_distribution = dict(cursor.fetchall())
            
            return {
                'total_issues': total_issues,
                'issue_category_distribution': issue_category_distribution,
                'issue_severity_distribution': issue_severity_distribution,
                'total_recommendations': total_recommendations,
                'recommendation_type_distribution': recommendation_type_distribution,
                'total_plans': total_plans,
                'plan_status_distribution': plan_status_distribution,
                'last_updated': datetime.datetime.now().isoformat()
            }

class QualityImprovementManager:
    """质量改进管理器"""
    
    def __init__(self, repository: QualityImprovementRepository = None):
        self.improvement_analyzer = DataQualityImprovement()
        self.repository = repository or QualityImprovementRepository()
    
    def analyze_quality_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析质量问题"""
        # 将字典转换为QualityIssue对象
        quality_issues = []
        for issue_dict in issues:
            issue = QualityIssue(
                id=issue_dict.get('id', str(uuid.uuid4())),
                table_name=issue_dict.get('table_name', ''),
                column_name=issue_dict.get('column_name', ''),
                row_identifier=issue_dict.get('row_identifier'),
                issue_type=issue_dict.get('issue_type', ''),
                issue_category=IssueCategory(issue_dict.get('issue_category', 'unknown')),
                severity=IssueSeverity(issue_dict.get('severity', 'medium')),
                description=issue_dict.get('description', ''),
                detected_at=datetime.datetime.fromisoformat(issue_dict.get('detected_at', datetime.datetime.now().isoformat())),
                source=issue_dict.get('source', ''),
                metadata=issue_dict.get('metadata', {})
            )
            quality_issues.append(issue)
        
        # 保存问题
        for issue in quality_issues:
            self.repository.save_issue(issue)
        
        # 分析问题
        analysis = self.improvement_analyzer.analyze_issues(issues)
        
        return analysis
    
    def generate_improvement_recommendations(self, issues: List[Dict[str, Any]], save: bool = True) -> List[Dict[str, Any]]:
        """生成改进建议"""
        # 生成建议
        recommendations = self.improvement_analyzer.generate_recommendations(issues)
        
        # 优先级排序
        prioritized_recommendations = self.improvement_analyzer.prioritize_recommendations(recommendations)
        
        # 保存建议
        if save:
            for recommendation in prioritized_recommendations:
                self.repository.save_recommendation(recommendation)
        
        # 转换为字典
        return [rec.to_dict() for rec in prioritized_recommendations]
    
    def create_improvement_plan(self, name: str, description: str, table_name: str,
                               issue_ids: List[str], recommendation_ids: List[str],
                               assignee: str, due_days: int = 30, created_by: str = "system") -> str:
        """创建改进计划"""
        # 计算到期日期
        due_date = datetime.datetime.now() + datetime.timedelta(days=due_days)
        
        # 创建计划
        plan = ImprovementPlan(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            table_name=table_name,
            issue_ids=issue_ids,
            recommendation_ids=recommendation_ids,
            status=ImprovementStatus.PENDING,
            assignee=assignee,
            due_date=due_date,
            created_at=datetime.datetime.now(),
            created_by=created_by
        )
        
        # 保存计划
        self.repository.save_improvement_plan(plan)
        
        return plan.id
    
    def get_issues_by_table(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """根据表名获取问题"""
        issues = self.repository.get_issues_by_table(table_name, limit)
        return [issue.to_dict() for issue in issues]
    
    def get_recommendations_by_issue(self, issue_id: str) -> List[Dict[str, Any]]:
        """根据问题ID获取建议"""
        recommendations = self.repository.get_recommendations_by_issue(issue_id)
        return [rec.to_dict() for rec in recommendations]
    
    def get_improvement_plans(self, status: str = None) -> List[Dict[str, Any]]:
        """获取改进计划"""
        plans = self.repository.get_all_improvement_plans(status)
        return [plan.to_dict() for plan in plans]
    
    def update_improvement_plan(self, plan_id: str, updates: Dict[str, Any], updated_by: str = "system") -> bool:
        """更新改进计划"""
        if 'status' in updates:
            updates['status'] = ImprovementStatus(updates['status']).value
        
        if 'due_date' in updates and isinstance(updates['due_date'], str):
            updates['due_date'] = datetime.datetime.fromisoformat(updates['due_date']).isoformat()
        elif 'due_date' in updates and isinstance(updates['due_date'], datetime.datetime):
            updates['due_date'] = updates['due_date'].isoformat()
        
        updates['updated_by'] = updated_by
        
        return self.repository.update_improvement_plan(plan_id, updates)
    
    def get_improvement_statistics(self) -> Dict[str, Any]:
        """获取改进统计信息"""
        return self.repository.get_improvement_statistics()
    
    def generate_improvement_report(self, table_name: str = None) -> str:
        """生成改进报告"""
        issues = self.repository.get_issues_by_table(table_name) if table_name else []
        
        # 分析问题
        issues_dicts = [issue.to_dict() for issue in issues]
        analysis = self.improvement_analyzer.analyze_issues(issues_dicts)
        
        # 生成建议
        recommendations = self.improvement_analyzer.generate_recommendations(issues_dicts)
        
        # 构建报告
        report = []
        report.append("# 数据质量改进报告")
        report.append("")
        
        if table_name:
            report.append(f"## 表: {table_name}")
        else:
            report.append("## 全部表")
        
        report.append("")
        report.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 问题分析
        report.append("### 问题分析")
        report.append("")
        report.append(f"总问题数: {analysis.get('total_issues', 0)}")
        report.append("")
        
        # 按类别分布
        category_dist = analysis.get('category_distribution', {})
        if category_dist:
            report.append("#### 按类别分布:")
            for category, count in category_dist.items():
                report.append(f"- {category}: {count}")
            report.append("")
        
        # 按严重程度分布
        severity_dist = analysis.get('severity_distribution', {})
        if severity_dist:
            report.append("#### 按严重程度分布:")
            for severity, count in severity_dist.items():
                report.append(f"- {severity}: {count}")
            report.append("")
        
        # 改进建议
        if recommendations:
            report.append("### 改进建议")
            report.append("")
            
            for i, rec in enumerate(recommendations, 1):
                report.append(f"#### {i}. {rec.title}")
                report.append(f"**类型**: {rec.recommendation_type.value}")
                report.append(f"**优先级**: {rec.priority}/10")
                report.append(f"工作量**: {rec.effort}/10")
                report.append(f"影响**: {rec.impact}/10")
                report.append(f"**描述**: {rec.description}")
                report.append("")
                report.append("**实施步骤**:")
                for step in rec.implementation_steps:
                    report.append(f"- {step}")
                report.append("")
                report.append("**前提条件**:")
                for prereq in rec.prerequisites:
                    report.append(f"- {prereq}")
                report.append("")
                report.append(f"**预期结果**: {rec.expected_outcome}")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函数，演示数据质量改进工具使用"""
    print("=" * 50)
    print("数据质量改进工具演示")
    print("=" * 50)
    
    # 创建质量改进管理器
    manager = QualityImprovementManager()
    
    # 1. 创建模拟质量问题
    print("\n1. 创建模拟质量问题...")
    
    # 模拟从质量检查系统获取的问题
    issues_data = [
        {
            'id': str(uuid.uuid4()),
            'table_name': 'customers',
            'column_name': 'email',
            'row_identifier': 15,
            'issue_type': 'invalid_format',
            'issue_category': 'validity',
            'severity': 'high',
            'description': '邮箱格式不正确',
            'detected_at': datetime.datetime.now().isoformat(),
            'source': 'data_quality_check',
            'metadata': {'value': 'invalid-email-format', 'expected_format': 'user@domain.com'}
        },
        {
            'id': str(uuid.uuid4()),
            'table_name': 'customers',
            'column_name': 'name',
            'row_identifier': 22,
            'issue_type': 'null_value',
            'issue_category': 'completeness',
            'severity': 'critical',
            'description': '客户姓名为空',
            'detected_at': datetime.datetime.now().isoformat(),
            'source': 'data_quality_check',
            'metadata': {'rule': 'not_null'}
        },
        {
            'id': str(uuid.uuid4()),
            'table_name': 'orders',
            'column_name': 'customer_id',
            'row_identifier': 105,
            'issue_type': 'referential_integrity',
            'issue_category': 'accuracy',
            'severity': 'high',
            'description': '客户ID不存在',
            'detected_at': datetime.datetime.now().isoformat(),
            'source': 'data_quality_check',
            'metadata': {'value': 9999, 'referenced_table': 'customers'}
        },
        {
            'id': str(uuid.uuid4()),
            'table_name': 'customers',
            'column_name': 'email',
            'row_identifier': 33,
            'issue_type': 'duplicate_value',
            'issue_category': 'uniqueness',
            'severity': 'medium',
            'description': '邮箱地址重复',
            'detected_at': datetime.datetime.now().isoformat(),
            'source': 'data_quality_check',
            'metadata': {'value': 'duplicate@example.com'}
        },
        {
            'id': str(uuid.uuid4()),
            'table_name': 'products',
            'column_name': 'last_updated',
            'row_identifier': 12,
            'issue_type': 'outdated_data',
            'issue_category': 'timeliness',
            'severity': 'medium',
            'description': '数据超过一年未更新',
            'detected_at': datetime.datetime.now().isoformat(),
            'source': 'data_quality_check',
            'metadata': {'last_update': '2022-01-15', 'current_date': '2023-06-20'}
        }
    ]
    
    print(f"创建了 {len(issues_data)} 个模拟质量问题")
    
    # 2. 分析质量问题
    print("\n2. 分析质量问题...")
    analysis = manager.analyze_quality_issues(issues_data)
    
    print(f"问题分析结果:")
    print(f"- 总问题数: {analysis['total_issues']}")
    print(f"- 类别分布: {analysis['category_distribution']}")
    print(f"- 严重程度分布: {analysis['severity_distribution']}")
    print(f"- 表分布: {analysis['table_distribution']}")
    if analysis['most_common_category']:
        print(f"- 最常见问题类别: {analysis['most_common_category'][0]} ({analysis['most_common_category'][1]} 个)")
    
    # 3. 生成改进建议
    print("\n3. 生成改进建议...")
    recommendations = manager.generate_improvement_recommendations(issues_data)
    
    print(f"生成了 {len(recommendations)} 个改进建议:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']} (优先级: {rec['priority']}, 影响: {rec['impact']}, 工作量: {rec['effort']})")
    
    # 4. 创建改进计划
    print("\n4. 创建改进计划...")
    
    # 为客户表创建改进计划
    customer_issues = [issue['id'] for issue in issues_data if issue['table_name'] == 'customers']
    customer_recommendations = [rec['id'] for rec in recommendations if any(issue['table_name'] == 'customers' for issue in issues_data)]
    
    if customer_issues and customer_recommendations:
        plan_id = manager.create_improvement_plan(
            name="客户表数据质量改进计划",
            description="解决客户表的数据质量问题，提高数据质量",
            table_name="customers",
            issue_ids=customer_issues,
            recommendation_ids=customer_recommendations,
            assignee="数据治理团队",
            due_days=30,
            created_by="演示用户"
        )
        
        print(f"创建了改进计划，ID: {plan_id}")
    
    # 5. 获取改进计划
    print("\n5. 获取改进计划...")
    plans = manager.get_improvement_plans()
    print(f"共有 {len(plans)} 个改进计划:")
    for plan in plans:
        print(f"- {plan['name']} (状态: {plan['status']}, 负责人: {plan['assignee']}, 到期日: {plan['due_date'][:10]})")
    
    # 6. 更新改进计划状态
    if plans:
        print("\n6. 更新改进计划状态...")
        plan_id = plans[0]['id']
        success = manager.update_improvement_plan(
            plan_id,
            {
                'status': 'in_progress',
                'completion_percentage': 25.0
            },
            "演示用户"
        )
        
        print(f"更新计划状态: {'成功' if success else '失败'}")
        
        # 获取更新后的计划
        updated_plans = manager.get_improvement_plans()
        updated_plan = next(p for p in updated_plans if p['id'] == plan_id)
        print(f"更新后状态: {updated_plan['status']}, 完成度: {updated_plan['completion_percentage']}%")
    
    # 7. 获取改进统计信息
    print("\n7. 获取改进统计信息...")
    stats = manager.get_improvement_statistics()
    print(f"总问题数: {stats['total_issues']}")
    print(f"问题类别分布: {stats['issue_category_distribution']}")
    print(f"问题严重程度分布: {stats['issue_severity_distribution']}")
    print(f"总建议数: {stats['total_recommendations']}")
    print(f"建议类型分布: {stats['recommendation_type_distribution']}")
    print(f"总计划数: {stats['total_plans']}")
    print(f"计划状态分布: {stats['plan_status_distribution']}")
    
    # 8. 生成改进报告
    print("\n8. 生成改进报告...")
    report = manager.generate_improvement_report("customers")
    
    # 保存报告到文件
    report_file = "customers_improvement_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"改进报告已保存到: {report_file}")
    print("\n报告内容预览:")
    print(report[:500] + "..." if len(report) > 500 else report)

if __name__ == "__main__":
    main()