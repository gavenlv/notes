#!/usr/bin/env python3
"""
元数据质量评估工具
提供元数据质量评估、监控和改进功能
"""

import os
import json
import sqlite3
import datetime
import re
import hashlib
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """质量维度枚举"""
    COMPLETENESS = "completeness"      # 完整性
    ACCURACY = "accuracy"              # 准确性
    CONSISTENCY = "consistency"        # 一致性
    TIMELINESS = "timeliness"          # 及时性
    VALIDITY = "validity"              # 有效性
    UNIQUENESS = "uniqueness"          # 唯一性

class QualityLevel(Enum):
    """质量等级枚举"""
    EXCELLENT = "excellent"            # 优秀 (0.9-1.0)
    GOOD = "good"                      # 良好 (0.8-0.9)
    ACCEPTABLE = "acceptable"          # 可接受 (0.6-0.8)
    NEEDS_IMPROVEMENT = "needs_improvement"  # 需要改进 (0.4-0.6)
    POOR = "poor"                      # 差 (0.0-0.4)

@dataclass
class QualityMetric:
    """质量指标数据类"""
    name: str
    dimension: QualityDimension
    description: str
    score: float
    weight: float
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'dimension': self.dimension.value,
            'description': self.description,
            'score': self.score,
            'weight': self.weight,
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityMetric':
        """从字典创建实例"""
        data['dimension'] = QualityDimension(data['dimension'])
        return cls(**data)

@dataclass
class QualityAssessment:
    """质量评估数据类"""
    id: str
    entity_id: str
    entity_type: str
    entity_name: str
    assessment_date: datetime.datetime
    overall_score: float
    quality_level: QualityLevel
    metrics: List[QualityMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    assessed_by: str
    next_assessment_date: Optional[datetime.datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'entity_name': self.entity_name,
            'assessment_date': self.assessment_date.isoformat(),
            'overall_score': self.overall_score,
            'quality_level': self.quality_level.value,
            'metrics': [metric.to_dict() for metric in self.metrics],
            'issues': self.issues,
            'recommendations': self.recommendations,
            'assessed_by': self.assessed_by,
            'next_assessment_date': self.next_assessment_date.isoformat() if self.next_assessment_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityAssessment':
        """从字典创建实例"""
        data['assessment_date'] = datetime.datetime.fromisoformat(data['assessment_date'])
        data['quality_level'] = QualityLevel(data['quality_level'])
        data['metrics'] = [QualityMetric.from_dict(metric) for metric in data['metrics']]
        if data['next_assessment_date']:
            data['next_assessment_date'] = datetime.datetime.fromisoformat(data['next_assessment_date'])
        return cls(**data)

class QualityAssessmentRepository:
    """质量评估存储库"""
    
    def __init__(self, db_path: str = "metadata_quality.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_assessments (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_name TEXT NOT NULL,
                    assessment_date TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    quality_level TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    issues TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    assessed_by TEXT NOT NULL,
                    next_assessment_date TEXT
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_assessments_entity_id ON quality_assessments (entity_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_assessments_entity_type ON quality_assessments (entity_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_assessments_date ON quality_assessments (assessment_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_assessments_level ON quality_assessments (quality_level)")
            
            conn.commit()
    
    def save_assessment(self, assessment: QualityAssessment) -> str:
        """保存质量评估"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO quality_assessments
                (id, entity_id, entity_type, entity_name, assessment_date, overall_score,
                 quality_level, metrics, issues, recommendations, assessed_by, next_assessment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment.id, assessment.entity_id, assessment.entity_type,
                assessment.entity_name, assessment.assessment_date.isoformat(),
                assessment.overall_score, assessment.quality_level.value,
                json.dumps([metric.to_dict() for metric in assessment.metrics]),
                json.dumps(assessment.issues),
                json.dumps(assessment.recommendations),
                assessment.assessed_by,
                assessment.next_assessment_date.isoformat() if assessment.next_assessment_date else None
            ))
            conn.commit()
        
        return assessment.id
    
    def get_assessment_by_id(self, assessment_id: str) -> Optional[QualityAssessment]:
        """根据ID获取质量评估"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM quality_assessments WHERE id = ?", (assessment_id,))
            row = cursor.fetchone()
            
            if row:
                return QualityAssessment.from_dict(dict(row))
            return None
    
    def get_latest_assessment(self, entity_id: str) -> Optional[QualityAssessment]:
        """获取实体的最新质量评估"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_assessments 
                WHERE entity_id = ? 
                ORDER BY assessment_date DESC
                LIMIT 1
            """, (entity_id,))
            row = cursor.fetchone()
            
            if row:
                return QualityAssessment.from_dict(dict(row))
            return None
    
    def get_assessments(self, entity_id: str = None, entity_type: str = None,
                       quality_level: str = None, limit: int = 100,
                       offset: int = 0) -> List[QualityAssessment]:
        """获取质量评估列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            sql = "SELECT * FROM quality_assessments WHERE 1=1"
            params = []
            
            # 添加过滤器
            if entity_id:
                sql += " AND entity_id = ?"
                params.append(entity_id)
            
            if entity_type:
                sql += " AND entity_type = ?"
                params.append(entity_type)
            
            if quality_level:
                sql += " AND quality_level = ?"
                params.append(quality_level)
            
            # 排序和分页
            sql += " ORDER BY assessment_date DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            return [QualityAssessment.from_dict(dict(row)) for row in rows]
    
    def get_assessment_history(self, entity_id: str, limit: int = 10) -> List[QualityAssessment]:
        """获取实体的评估历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM quality_assessments 
                WHERE entity_id = ? 
                ORDER BY assessment_date DESC
                LIMIT ?
            """, (entity_id, limit))
            
            rows = cursor.fetchall()
            return [QualityAssessment.from_dict(dict(row)) for row in rows]
    
    def get_quality_trend(self, entity_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取质量趋势"""
        with sqlite3.connect(self.db_path) as conn:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            
            cursor = conn.execute("""
                SELECT assessment_date, overall_score, quality_level
                FROM quality_assessments
                WHERE entity_id = ? AND assessment_date >= ?
                ORDER BY assessment_date ASC
            """, (entity_id, start_date))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取质量评估统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总评估数
            cursor = conn.execute("SELECT COUNT(*) FROM quality_assessments")
            total_assessments = cursor.fetchone()[0]
            
            # 按质量等级统计
            cursor = conn.execute("""
                SELECT quality_level, COUNT(*) FROM quality_assessments 
                GROUP BY quality_level
            """)
            quality_level_distribution = dict(cursor.fetchall())
            
            # 按实体类型统计
            cursor = conn.execute("""
                SELECT entity_type, COUNT(*) FROM quality_assessments 
                GROUP BY entity_type
            """)
            entity_type_distribution = dict(cursor.fetchall())
            
            # 平均质量评分
            cursor = conn.execute("SELECT AVG(overall_score) FROM quality_assessments")
            avg_score = cursor.fetchone()[0] or 0
            
            # 最近7天的评估数
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            cursor = conn.execute("""
                SELECT COUNT(*) FROM quality_assessments 
                WHERE assessment_date >= ?
            """, (seven_days_ago,))
            recent_assessments = cursor.fetchone()[0]
            
            # 评分最高的5个实体
            cursor = conn.execute("""
                SELECT entity_id, entity_name, entity_type, MAX(overall_score) as max_score
                FROM quality_assessments
                GROUP BY entity_id
                ORDER BY max_score DESC
                LIMIT 5
            """)
            top_entities = [dict(row) for row in cursor.fetchall()]
            
            # 评分最低的5个实体
            cursor = conn.execute("""
                SELECT entity_id, entity_name, entity_type, MAX(overall_score) as max_score
                FROM quality_assessments
                GROUP BY entity_id
                ORDER BY max_score ASC
                LIMIT 5
            """)
            bottom_entities = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_assessments': total_assessments,
            'quality_level_distribution': quality_level_distribution,
            'entity_type_distribution': entity_type_distribution,
            'average_score': round(avg_score, 2),
            'recent_assessments': recent_assessments,
            'top_entities': top_entities,
            'bottom_entities': bottom_entities,
            'last_updated': datetime.datetime.now().isoformat()
        }

class MetadataQualityAssessor:
    """元数据质量评估器"""
    
    def __init__(self, repo: QualityAssessmentRepository = None):
        self.repo = repo or QualityAssessmentRepository()
    
    def assess_completeness(self, entity: Dict[str, Any]) -> QualityMetric:
        """评估完整性"""
        # 检查必需字段
        required_fields = ['id', 'name', 'type', 'description']
        missing_required = sum(1 for field in required_fields if not entity.get(field))
        
        # 检查可选但推荐字段
        recommended_fields = ['owner', 'tags', 'classification', 'steward', 'created_at', 'updated_at']
        missing_recommended = sum(1 for field in recommended_fields if not entity.get(field))
        
        # 计算完整性评分
        # 必需字段权重70%，推荐字段权重30%
        required_score = max(0, 1 - missing_required / len(required_fields))
        recommended_score = 1 - missing_recommended / len(recommended_fields)
        completeness_score = (required_score * 0.7) + (recommended_score * 0.3)
        
        return QualityMetric(
            name="完整性",
            dimension=QualityDimension.COMPLETENESS,
            description="评估元数据记录是否包含必要的信息字段",
            score=completeness_score,
            weight=0.25,
            details={
                'required_fields_present': len(required_fields) - missing_required,
                'required_fields_total': len(required_fields),
                'recommended_fields_present': len(recommended_fields) - missing_recommended,
                'recommended_fields_total': len(recommended_fields),
                'missing_required': [field for field in required_fields if not entity.get(field)],
                'missing_recommended': [field for field in recommended_fields if not entity.get(field)]
            }
        )
    
    def assess_accuracy(self, entity: Dict[str, Any]) -> QualityMetric:
        """评估准确性"""
        # 简化的准确性检查 - 实际环境中可能需要更复杂的验证逻辑
        issues = []
        
        # 检查名称是否有效
        name = entity.get('name', '')
        if not name or not isinstance(name, str) or len(name.strip()) < 3:
            issues.append("名称无效或过短")
        
        # 检查描述是否有效
        description = entity.get('description', '')
        if not description or not isinstance(description, str) or len(description.strip()) < 10:
            issues.append("描述无效或过短")
        
        # 检查数据类型是否有效
        type_field = entity.get('type', '')
        valid_types = ['table', 'file', 'api', 'database', 'view', 'procedure']
        if type_field and type_field not in valid_types:
            issues.append("数据类型不在有效范围内")
        
        # 检查日期格式是否有效
        for date_field in ['created_at', 'updated_at']:
            date_value = entity.get(date_field)
            if date_value:
                try:
                    datetime.datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    issues.append(f"{date_field} 日期格式无效")
        
        # 计算准确性评分
        accuracy_score = max(0, 1 - len(issues) / 5)  # 假设最多5个潜在问题
        
        return QualityMetric(
            name="准确性",
            dimension=QualityDimension.ACCURACY,
            description="评估元数据信息的正确性和有效性",
            score=accuracy_score,
            weight=0.25,
            details={
                'issues': issues,
                'issue_count': len(issues)
            }
        )
    
    def assess_consistency(self, entity: Dict[str, Any], similar_entities: List[Dict[str, Any]] = None) -> QualityMetric:
        """评估一致性"""
        if not similar_entities:
            return QualityMetric(
                name="一致性",
                dimension=QualityDimension.CONSISTENCY,
                description="评估元数据与同类实体的一致性",
                score=1.0,  # 没有比较对象，给满分
                weight=0.15,
                details={
                    'message': "没有相似实体可供比较"
                }
            )
        
        # 检查命名一致性
        entity_name = entity.get('name', '').lower()
        entity_type = entity.get('type', '').lower()
        
        naming_issues = []
        
        for similar in similar_entities:
            similar_name = similar.get('name', '').lower()
            similar_type = similar.get('type', '').lower()
            
            # 如果类型相同，检查命名模式
            if entity_type == similar_type and entity_name and similar_name:
                # 检查命名约定（例如，表名是否都是小写加下划线）
                if entity_name.replace('_', '').replace('-', '').isalnum() and not similar_name.replace('_', '').replace('-', '').isalnum():
                    naming_issues.append(f"与 {similar_name} 的命名格式不一致")
        
        # 检查属性一致性
        attribute_issues = []
        common_attributes = ['tags', 'classification', 'sensitivity']
        
        for similar in similar_entities:
            for attr in common_attributes:
                entity_value = entity.get(attr)
                similar_value = similar.get(attr)
                
                if entity_value and similar_value:
                    # 检查相同属性的值是否在相同的可能值范围内
                    if attr == 'classification':
                        valid_classifications = ['public', 'internal', 'confidential', 'restricted']
                        if (entity_value in valid_classifications) != (similar_value in valid_classifications):
                            attribute_issues.append(f"与 {similar.get('name', '未知')} 的 {attr} 值范围不一致")
        
        # 计算一致性评分
        total_issues = len(naming_issues) + len(attribute_issues)
        consistency_score = max(0, 1 - total_issues / 10)  # 假设最多10个潜在问题
        
        return QualityMetric(
            name="一致性",
            dimension=QualityDimension.CONSISTENCY,
            description="评估元数据与同类实体的一致性",
            score=consistency_score,
            weight=0.15,
            details={
                'naming_issues': naming_issues,
                'attribute_issues': attribute_issues,
                'total_issues': total_issues
            }
        )
    
    def assess_timeliness(self, entity: Dict[str, Any]) -> QualityMetric:
        """评估及时性"""
        # 获取更新时间
        updated_at = entity.get('updated_at')
        created_at = entity.get('created_at')
        
        if not updated_at and not created_at:
            return QualityMetric(
                name="及时性",
                dimension=QualityDimension.TIMELINESS,
                description="评估元数据的更新频率和新鲜度",
                score=0.0,
                weight=0.1,
                details={
                    'message': "缺少时间戳信息"
                }
            )
        
        # 使用更新时间或创建时间
        last_date_str = updated_at or created_at
        try:
            last_date = datetime.datetime.fromisoformat(last_date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return QualityMetric(
                name="及时性",
                dimension=QualityDimension.TIMELINESS,
                description="评估元数据的更新频率和新鲜度",
                score=0.0,
                weight=0.1,
                details={
                    'message': "时间戳格式无效"
                }
            )
        
        # 计算距离现在的天数
        now = datetime.datetime.now()
        days_since_update = (now - last_date).days
        
        # 根据更新频率评估及时性
        if days_since_update <= 7:
            timeliness_score = 1.0  # 最近一周更新，非常及时
        elif days_since_update <= 30:
            timeliness_score = 0.8  # 最近一个月更新，及时
        elif days_since_update <= 90:
            timeliness_score = 0.6  # 最近三个月更新，一般
        elif days_since_update <= 365:
            timeliness_score = 0.4  # 最近一年更新，较差
        else:
            timeliness_score = 0.2  # 超过一年未更新，很差
        
        return QualityMetric(
            name="及时性",
            dimension=QualityDimension.TIMELINESS,
            description="评估元数据的更新频率和新鲜度",
            score=timeliness_score,
            weight=0.1,
            details={
                'last_updated': last_date_str,
                'days_since_update': days_since_update,
                'timeliness_level': self._get_timeliness_level(days_since_update)
            }
        )
    
    def assess_validity(self, entity: Dict[str, Any]) -> QualityMetric:
        """评估有效性"""
        validity_issues = []
        
        # 检查字段值的格式和有效性
        if 'tags' in entity and entity['tags']:
            if not isinstance(entity['tags'], list):
                validity_issues.append("tags 字段应该是列表类型")
            else:
                for tag in entity['tags']:
                    if not isinstance(tag, str) or not tag.strip():
                        validity_issues.append("标签应该是非空字符串")
        
        if 'owner' in entity:
            owner = entity['owner']
            if not isinstance(owner, str) or not owner.strip():
                validity_issues.append("所有者字段应该是非空字符串")
        
        # 检查分类值是否有效
        if 'classification' in entity:
            classification = entity['classification']
            valid_classifications = ['public', 'internal', 'confidential', 'restricted']
            if classification not in valid_classifications:
                validity_issues.append(f"分类值 '{classification}' 不在有效范围内")
        
        # 检查敏感度值是否有效
        if 'sensitivity' in entity:
            sensitivity = entity['sensitivity']
            valid_sensitivities = ['public', 'internal', 'confidential', 'restricted', 'pii', 'phi']
            if sensitivity not in valid_sensitivities:
                validity_issues.append(f"敏感度值 '{sensitivity}' 不在有效范围内")
        
        # 计算有效性评分
        validity_score = max(0, 1 - len(validity_issues) / 5)  # 假设最多5个潜在问题
        
        return QualityMetric(
            name="有效性",
            dimension=QualityDimension.VALIDITY,
            description="评估元数据字段值是否在有效的格式和范围内",
            score=validity_score,
            weight=0.15,
            details={
                'validity_issues': validity_issues,
                'issue_count': len(validity_issues)
            }
        )
    
    def assess_uniqueness(self, entity: Dict[str, Any], all_entities: List[Dict[str, Any]] = None) -> QualityMetric:
        """评估唯一性"""
        if not all_entities:
            return QualityMetric(
                name="唯一性",
                dimension=QualityDimension.UNIQUENESS,
                description="评估元数据标识符的唯一性",
                score=1.0,  # 没有其他实体可供比较，给满分
                weight=0.1,
                details={
                    'message': "没有其他实体可供比较唯一性"
                }
            )
        
        entity_id = entity.get('id')
        entity_name = entity.get('name')
        entity_type = entity.get('type')
        
        uniqueness_issues = []
        
        # 检查ID唯一性
        duplicate_ids = [e.get('name') for e in all_entities if e.get('id') == entity_id and e.get('id') != entity.get('id')]
        if duplicate_ids:
            uniqueness_issues.append(f"ID '{entity_id}' 与其他实体重复")
        
        # 检查名称+类型的组合唯一性
        duplicate_names = [e.get('name') for e in all_entities 
                           if e.get('name') == entity_name and 
                           e.get('type') == entity_type and 
                           e.get('id') != entity_id]
        if duplicate_names:
            uniqueness_issues.append(f"名称 '{entity_name}' 在类型 '{entity_type}' 中不唯一")
        
        # 计算唯一性评分
        uniqueness_score = max(0, 1 - len(uniqueness_issues) / 2)  # 最多2个潜在问题
        
        return QualityMetric(
            name="唯一性",
            dimension=QualityDimension.UNIQUENESS,
            description="评估元数据标识符的唯一性",
            score=uniqueness_score,
            weight=0.1,
            details={
                'uniqueness_issues': uniqueness_issues,
                'issue_count': len(uniqueness_issues)
            }
        )
    
    def _get_timeliness_level(self, days: int) -> str:
        """获取及时性级别"""
        if days <= 7:
            return "非常及时"
        elif days <= 30:
            return "及时"
        elif days <= 90:
            return "一般"
        elif days <= 365:
            return "较差"
        else:
            return "很差"
    
    def assess_metadata(self, entity: Dict[str, Any], all_entities: List[Dict[str, Any]] = None) -> QualityAssessment:
        """评估元数据质量"""
        # 创建评估ID
        assessment_id = str(uuid.uuid4())
        
        # 获取相似实体用于一致性和唯一性评估
        similar_entities = []
        if all_entities:
            entity_type = entity.get('type')
            similar_entities = [e for e in all_entities if e.get('type') == entity_type and e.get('id') != entity.get('id')]
        
        # 执行各维度评估
        completeness_metric = self.assess_completeness(entity)
        accuracy_metric = self.assess_accuracy(entity)
        consistency_metric = self.assess_consistency(entity, similar_entities)
        timeliness_metric = self.assess_timeliness(entity)
        validity_metric = self.assess_validity(entity)
        uniqueness_metric = self.assess_uniqueness(entity, all_entities)
        
        metrics = [
            completeness_metric,
            accuracy_metric,
            consistency_metric,
            timeliness_metric,
            validity_metric,
            uniqueness_metric
        ]
        
        # 计算加权总分
        overall_score = sum(metric.score * metric.weight for metric in metrics)
        
        # 确定质量等级
        if overall_score >= 0.9:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 0.6:
            quality_level = QualityLevel.ACCEPTABLE
        elif overall_score >= 0.4:
            quality_level = QualityLevel.NEEDS_IMPROVEMENT
        else:
            quality_level = QualityLevel.POOR
        
        # 收集所有问题
        issues = []
        for metric in metrics:
            if metric.details.get('issues'):
                issues.extend(metric.details['issues'])
            if metric.details.get('missing_required'):
                for field in metric.details['missing_required']:
                    issues.append(f"缺少必需字段: {field}")
            if metric.details.get('missing_recommended'):
                for field in metric.details['missing_recommended']:
                    issues.append(f"缺少推荐字段: {field}")
            if metric.details.get('validity_issues'):
                issues.extend(metric.details['validity_issues'])
            if metric.details.get('uniqueness_issues'):
                issues.extend(metric.details['uniqueness_issues'])
        
        # 生成改进建议
        recommendations = []
        
        if completeness_metric.score < 0.8:
            recommendations.append("添加缺失的必需字段和推荐字段，特别是描述、所有者和标签")
        
        if accuracy_metric.score < 0.8:
            recommendations.append("检查并更正无效的名称、描述和类型值")
        
        if consistency_metric.score < 0.8:
            recommendations.append("确保命名约定和属性值与同类实体保持一致")
        
        if timeliness_metric.score < 0.8:
            recommendations.append("定期更新元数据，确保信息保持最新")
        
        if validity_metric.score < 0.8:
            recommendations.append("确保字段值符合预期的格式和范围")
        
        if uniqueness_metric.score < 0.8:
            recommendations.append("确保实体ID和名称+类型组合的唯一性")
        
        # 设置下次评估日期
        if quality_level in [QualityLevel.EXCELLENT, QualityLevel.GOOD]:
            next_assessment_date = datetime.datetime.now() + datetime.timedelta(days=90)
        elif quality_level == QualityLevel.ACCEPTABLE:
            next_assessment_date = datetime.datetime.now() + datetime.timedelta(days=60)
        else:
            next_assessment_date = datetime.datetime.now() + datetime.timedelta(days=30)
        
        # 创建评估对象
        assessment = QualityAssessment(
            id=assessment_id,
            entity_id=entity.get('id', ''),
            entity_type=entity.get('type', ''),
            entity_name=entity.get('name', ''),
            assessment_date=datetime.datetime.now(),
            overall_score=overall_score,
            quality_level=quality_level,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            assessed_by="metadata_quality_assessor",
            next_assessment_date=next_assessment_date
        )
        
        # 保存评估
        self.repo.save_assessment(assessment)
        
        return assessment

class MetadataQualityManager:
    """元数据质量管理器"""
    
    def __init__(self, assessor: MetadataQualityAssessor = None):
        self.assessor = assessor or MetadataQualityAssessor()
    
    def assess_entity(self, entity: Dict[str, Any], all_entities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """评估单个实体"""
        assessment = self.assessor.assess_metadata(entity, all_entities)
        return assessment.to_dict()
    
    def assess_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量评估实体"""
        results = []
        
        for i, entity in enumerate(entities):
            # 评估当前实体
            assessment = self.assessor.assess_metadata(entity, entities)
            results.append(assessment.to_dict())
            
            # 打印进度
            if (i + 1) % 10 == 0 or i == len(entities) - 1:
                print(f"已完成 {i + 1}/{len(entities)} 个实体的评估")
        
        return results
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """获取评估结果"""
        assessment = self.assessor.repo.get_assessment_by_id(assessment_id)
        return assessment.to_dict() if assessment else None
    
    def get_latest_assessment(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取实体的最新评估结果"""
        assessment = self.assessor.repo.get_latest_assessment(entity_id)
        return assessment.to_dict() if assessment else None
    
    def get_assessment_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取实体的评估历史"""
        assessments = self.assessor.repo.get_assessment_history(entity_id)
        return [assessment.to_dict() for assessment in assessments]
    
    def get_quality_trend(self, entity_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取质量趋势"""
        return self.assessor.repo.get_quality_trend(entity_id, days)
    
    def get_quality_dashboard(self) -> Dict[str, Any]:
        """获取质量仪表板数据"""
        return self.assessor.repo.get_statistics()
    
    def get_improvement_plan(self, entity_id: str) -> Dict[str, Any]:
        """获取改进计划"""
        assessment = self.assessor.repo.get_latest_assessment(entity_id)
        if not assessment:
            return {'error': '未找到评估结果'}
        
        # 基于最新评估生成改进计划
        lowest_scores = sorted(assessment.metrics, key=lambda m: m.score * m.weight)[:3]
        
        improvement_plan = {
            'entity_id': entity_id,
            'entity_name': assessment.entity_name,
            'current_score': assessment.overall_score,
            'quality_level': assessment.quality_level.value,
            'priority_improvements': [],
            'recommendations': assessment.recommendations,
            'next_assessment_date': assessment.next_assessment_date.isoformat() if assessment.next_assessment_date else None
        }
        
        for metric in lowest_scores:
            improvement_plan['priority_improvements'].append({
                'dimension': metric.dimension.value,
                'name': metric.name,
                'current_score': metric.score,
                'weight': metric.weight,
                'impact': round(metric.weight * (1 - metric.score) * 100, 1),  # 对总分的影响
                'details': metric.details
            })
        
        return improvement_plan

def main():
    """主函数，演示元数据质量评估"""
    print("=" * 50)
    print("元数据质量评估工具演示")
    print("=" * 50)
    
    # 创建元数据质量管理器
    manager = MetadataQualityManager()
    
    # 1. 创建示例元数据实体
    print("\n1. 创建示例元数据实体...")
    
    entities = [
        {
            'id': 'customer_table_1',
            'name': 'customers',
            'type': 'table',
            'description': '客户基本信息表，包含客户的姓名、联系方式等基本信息',
            'owner': '销售部门',
            'steward': '张三',
            'tags': ['客户', '个人信息', '核心业务'],
            'classification': 'confidential',
            'sensitivity': 'pii',
            'created_at': '2023-01-15T10:30:00Z',
            'updated_at': '2023-05-20T14:25:00Z'
        },
        {
            'id': 'order_table_1',
            'name': 'orders',
            'type': 'table',
            'description': '订单信息表',
            'owner': '销售部门',
            'tags': ['订单'],
            'classification': 'internal',
            'created_at': '2022-11-10T09:15:00Z',
            'updated_at': '2023-04-05T11:30:00Z'
        },
        {
            'id': 'product_file_1',
            'name': 'product_catalog',
            'type': 'file',
            'description': '产品目录',
            'tags': ['产品', '目录'],
            'classification': 'public',
            'created_at': '2021-07-22T16:45:00Z'
        },
        {
            'id': 'customer_api_1',
            'name': 'customer_info_api',
            'type': 'api',
            'description': '获取客户信息的API接口',
            'owner': 'IT部门',
            'classification': 'confidential',
            'sensitivity': 'pii',
            'created_at': '2022-09-05T13:20:00Z',
            'updated_at': '2023-02-18T10:10:00Z'
        },
        {
            'id': 'sales_report_1',
            'name': 'monthly_sales_report',
            'type': 'file',
            'owner': '数据分析部门',
            # 缺少描述和标签，质量较低
            'created_at': '2020-05-15T08:30:00Z'  # 很久未更新
        }
    ]
    
    print(f"创建了 {len(entities)} 个示例元数据实体")
    
    # 2. 评估第一个实体
    print("\n2. 评估第一个实体...")
    first_assessment = manager.assess_entity(entities[0], entities)
    print(f"实体: {first_assessment['entity_name']}")
    print(f"总体评分: {first_assessment['overall_score']:.2f}")
    print(f"质量等级: {first_assessment['quality_level']}")
    print("各维度评分:")
    for metric in first_assessment['metrics']:
        print(f"- {metric['name']}: {metric['score']:.2f} (权重: {metric['weight']})")
    
    # 3. 批量评估所有实体
    print("\n3. 批量评估所有实体...")
    assessment_results = manager.assess_entities(entities)
    print(f"完成了 {len(assessment_results)} 个实体的评估")
    
    # 显示所有实体的评估结果摘要
    print("\n评估结果摘要:")
    for result in assessment_results:
        print(f"- {result['entity_name']} ({result['entity_type']}): {result['overall_score']:.2f} ({result['quality_level']})")
    
    # 4. 获取实体的改进计划
    print("\n4. 获取低质量实体的改进计划...")
    # 找到评分最低的实体
    lowest_score_entity = min(assessment_results, key=lambda x: x['overall_score'])
    improvement_plan = manager.get_improvement_plan(lowest_score_entity['entity_id'])
    
    print(f"改进计划: {improvement_plan['entity_name']}")
    print(f"当前评分: {improvement_plan['current_score']:.2f} ({improvement_plan['quality_level']})")
    print("优先改进项:")
    for item in improvement_plan['priority_improvements']:
        print(f"- {item['name']}: {item['current_score']:.2f} (影响: {item['impact']}%)")
    
    print("\n建议措施:")
    for recommendation in improvement_plan['recommendations']:
        print(f"- {recommendation}")
    
    # 5. 获取质量仪表板
    print("\n5. 获取质量仪表板...")
    dashboard = manager.get_quality_dashboard()
    
    print(f"总评估数: {dashboard['total_assessments']}")
    print(f"平均评分: {dashboard['average_score']}")
    print(f"质量等级分布: {dashboard['quality_level_distribution']}")
    print(f"最近7天评估数: {dashboard['recent_assessments']}")
    
    print("\n评分最高的实体:")
    for entity in dashboard['top_entities']:
        print(f"- {entity['entity_name']} ({entity['entity_type']}): {entity['max_score']:.2f}")
    
    print("\n评分最低的实体:")
    for entity in dashboard['bottom_entities']:
        print(f"- {entity['entity_name']} ({entity['entity_type']}): {entity['max_score']:.2f}")
    
    # 6. 获取评估历史
    print("\n6. 获取评估历史...")
    # 再次评估第一个实体以创建历史记录
    # 修改一些字段以模拟质量变化
    entities[0]['updated_at'] = datetime.datetime.now().isoformat() + 'Z'
    entities[0]['description'] = '更新后的客户基本信息表描述，更详细和准确'
    manager.assess_entity(entities[0], entities)
    
    history = manager.get_assessment_history(entities[0]['id'])
    print(f"实体 {entities[0]['name']} 的评估历史: {len(history)} 条记录")
    for record in history:
        print(f"- {record['assessment_date'][:10]}: {record['overall_score']:.2f} ({record['quality_level']})")
    
    # 7. 获取质量趋势
    print("\n7. 获取质量趋势...")
    trend = manager.get_quality_trend(entities[0]['id'], days=30)
    if trend:
        print("质量趋势:")
        for point in trend:
            print(f"- {point['assessment_date'][:10]}: {point['overall_score']:.2f} ({point['quality_level']})")
    else:
        print("暂无趋势数据")

if __name__ == "__main__":
    main()