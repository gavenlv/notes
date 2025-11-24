#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主数据管理器
实现主数据的创建、维护、整合和分发功能
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import uuid
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MasterDataEntity:
    """主数据实体类"""
    entity_id: str
    entity_type: str
    attributes: Dict[str, Any]
    source_system: str
    creation_date: datetime
    last_update_date: datetime
    status: str = "active"
    version: int = 1
    golden_record: bool = False
    
    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['creation_date'] = self.creation_date.isoformat()
        result['last_update_date'] = self.last_update_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实体"""
        data['creation_date'] = datetime.fromisoformat(data['creation_date'])
        data['last_update_date'] = datetime.fromisoformat(data['last_update_date'])
        return cls(**data)


class MasterDataManager:
    """主数据管理器"""
    
    def __init__(self, db_path="mdm.db"):
        """初始化主数据管理器"""
        self.db_path = db_path
        self._initialize_database()
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化组件
        self.matcher = RecordMatcher(self.config.get('matching', {}))
        self.merger = RecordMerger(self.config.get('merging', {}))
        self.distributor = DataDistributor(self.config.get('distribution', {}))
        self.quality_assessor = DataQualityAssessor(self.config.get('quality', {}))
    
    def _initialize_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建主数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_data (
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            attributes TEXT NOT NULL,
            source_system TEXT NOT NULL,
            creation_date TEXT NOT NULL,
            last_update_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            version INTEGER DEFAULT 1,
            golden_record BOOLEAN DEFAULT FALSE
        )
        ''')
        
        # 创建匹配表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id TEXT PRIMARY KEY,
            entity_id TEXT,
            matched_entity_id TEXT,
            match_score REAL,
            match_type TEXT,
            creation_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (entity_id) REFERENCES master_data (entity_id),
            FOREIGN KEY (matched_entity_id) REFERENCES master_data (entity_id)
        )
        ''')
        
        # 创建合并表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS merges (
            merge_id TEXT PRIMARY KEY,
            golden_record_id TEXT,
            source_entity_ids TEXT NOT NULL,
            merge_strategy TEXT,
            creation_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (golden_record_id) REFERENCES master_data (entity_id)
        )
        ''')
        
        # 创建分发记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS distributions (
            distribution_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            target_system TEXT NOT NULL,
            distribution_type TEXT,
            creation_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            response_data TEXT,
            FOREIGN KEY (entity_id) REFERENCES master_data (entity_id)
        )
        ''')
        
        # 创建数据质量评估表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_assessments (
            assessment_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            assessment_date TEXT NOT NULL,
            dimensions TEXT NOT NULL,
            overall_score REAL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (entity_id) REFERENCES master_data (entity_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_config(self):
        """加载配置"""
        # 默认配置
        default_config = {
            "matching": {
                "threshold": 0.8,
                "algorithm": "weighted",
                "fields": ["name", "email", "phone"]
            },
            "merging": {
                "strategy": "source_priority",
                "conflict_resolution": "manual",
                "source_priorities": {
                    "CRM": 1,
                    "ERP": 2,
                    "Website": 3
                }
            },
            "distribution": {
                "type": "push",
                "retry_attempts": 3,
                "retry_interval": 60
            },
            "quality": {
                "dimensions": ["completeness", "accuracy", "consistency"],
                "thresholds": {
                    "completeness": 0.9,
                    "accuracy": 0.95,
                    "consistency": 0.9
                }
            }
        }
        
        # 尝试从文件加载配置
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # 合并配置
                for key, value in file_config.items():
                    if key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
        
        return default_config
    
    def create_entity(self, entity_type: str, attributes: Dict[str, Any], 
                     source_system: str) -> str:
        """创建主数据实体"""
        entity_id = str(uuid.uuid4())
        now = datetime.now()
        
        entity = MasterDataEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            attributes=attributes,
            source_system=source_system,
            creation_date=now,
            last_update_date=now
        )
        
        # 保存到数据库
        self._save_entity(entity)
        
        logger.info(f"Created {entity_type} entity {entity_id} from {source_system}")
        
        # 执行数据质量评估
        quality_score = self.quality_assessor.assess_entity(entity)
        
        # 分发数据（如果配置为自动分发）
        if self.config.get('auto_distribution', False):
            self.distributor.distribute_entity(entity)
        
        return entity_id
    
    def update_entity(self, entity_id: str, attributes: Dict[str, Any]) -> bool:
        """更新主数据实体"""
        entity = self._get_entity(entity_id)
        if not entity:
            logger.error(f"Entity {entity_id} not found")
            return False
        
        # 更新属性和时间戳
        entity.attributes.update(attributes)
        entity.last_update_date = datetime.now()
        entity.version += 1
        
        # 保存到数据库
        self._save_entity(entity)
        
        logger.info(f"Updated entity {entity_id}")
        
        # 执行数据质量评估
        quality_score = self.quality_assessor.assess_entity(entity)
        
        # 分发数据更新
        if self.config.get('auto_distribution', False):
            self.distributor.distribute_entity(entity)
        
        return True
    
    def match_entities(self, entity_type: str) -> List[Dict[str, Any]]:
        """匹配可能重复的实体"""
        # 获取指定类型的所有实体
        entities = self._get_entities_by_type(entity_type)
        
        matches = []
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                # 计算匹配分数
                score = self.matcher.match(entity1, entity2)
                
                if score >= self.config['matching']['threshold']:
                    match_id = str(uuid.uuid4())
                    match = {
                        'match_id': match_id,
                        'entity_id': entity1.entity_id,
                        'matched_entity_id': entity2.entity_id,
                        'match_score': score,
                        'match_type': 'automatic',
                        'creation_date': datetime.now(),
                        'status': 'pending'
                    }
                    matches.append(match)
                    
                    # 保存匹配结果
                    self._save_match(match)
        
        logger.info(f"Found {len(matches)} matches for {entity_type}")
        return matches
    
    def merge_entities(self, entity_ids: List[str], strategy: str = None) -> str:
        """合并实体"""
        if not entity_ids or len(entity_ids) < 2:
            logger.error("At least two entities required for merge")
            return None
        
        # 获取实体
        entities = [self._get_entity(entity_id) for entity_id in entity_ids]
        if None in entities:
            logger.error("One or more entities not found")
            return None
        
        # 使用配置的策略或传入的策略
        merge_strategy = strategy or self.config['merging']['strategy']
        
        # 执行合并
        golden_record = self.merger.merge(entities, merge_strategy)
        
        # 创建合并记录
        merge_id = str(uuid.uuid4())
        merge_record = {
            'merge_id': merge_id,
            'golden_record_id': golden_record.entity_id,
            'source_entity_ids': ','.join(entity_ids),
            'merge_strategy': merge_strategy,
            'creation_date': datetime.now(),
            'status': 'active'
        }
        
        # 保存黄金记录
        self._save_entity(golden_record)
        
        # 保存合并记录
        self._save_merge(merge_record)
        
        # 标记原始实体为非活动状态
        for entity_id in entity_ids:
            if entity_id != golden_record.entity_id:
                self._deactivate_entity(entity_id)
        
        logger.info(f"Merged {len(entity_ids)} entities into {golden_record.entity_id}")
        
        # 分发黄金记录
        if self.config.get('auto_distribution', False):
            self.distributor.distribute_entity(golden_record)
        
        return golden_record.entity_id
    
    def search_entities(self, entity_type: str = None, 
                       filters: Dict[str, Any] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """搜索主数据实体"""
        conn = sqlite3.connect(self.db_path)
        
        # 构建查询
        query = "SELECT * FROM master_data WHERE status = 'active'"
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if filters:
            for key, value in filters.items():
                query += f" AND json_extract(attributes, '$.{key}') = ?"
                params.append(value)
        
        query += " ORDER BY last_update_date DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            entity = self._row_to_entity(row)
            results.append(entity.to_dict())
        
        conn.close()
        
        return results
    
    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """获取主数据实体"""
        entity = self._get_entity(entity_id)
        if entity:
            return entity.to_dict()
        return None
    
    def get_entity_history(self, entity_id: str) -> Dict[str, Any]:
        """获取实体历史信息"""
        entity = self._get_entity(entity_id)
        if not entity:
            return None
        
        # 获取匹配记录
        matches = self._get_entity_matches(entity_id)
        
        # 获取合并记录
        merge = self._get_entity_merge(entity_id)
        
        # 获取分发记录
        distributions = self._get_entity_distributions(entity_id)
        
        # 获取质量评估记录
        quality_assessments = self._get_entity_quality_assessments(entity_id)
        
        return {
            'entity': entity.to_dict(),
            'matches': matches,
            'merge': merge,
            'distributions': distributions,
            'quality_assessments': quality_assessments
        }
    
    def get_golden_records(self, entity_type: str = None) -> List[Dict[str, Any]]:
        """获取黄金记录"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM master_data WHERE golden_record = TRUE AND status = 'active'"
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        query += " ORDER BY last_update_date DESC"
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            entity = self._row_to_entity(row)
            results.append(entity.to_dict())
        
        conn.close()
        
        return results
    
    def get_quality_report(self, entity_type: str = None) -> Dict[str, Any]:
        """获取数据质量报告"""
        conn = sqlite3.connect(self.db_path)
        
        # 构建查询
        query = "SELECT entity_id, dimensions, overall_score FROM quality_assessments WHERE status = 'active'"
        params = []
        
        if entity_type:
            query += " AND entity_id IN (SELECT entity_id FROM master_data WHERE entity_type = ?)"
            params.append(entity_type)
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # 收集质量评估数据
        quality_data = []
        for row in cursor.fetchall():
            quality_data.append({
                'entity_id': row[0],
                'dimensions': json.loads(row[1]),
                'overall_score': row[2]
            })
        
        conn.close()
        
        if not quality_data:
            return {
                'entity_count': 0,
                'average_score': 0,
                'score_distribution': {},
                'dimension_scores': {}
            }
        
        # 计算总体统计
        entity_count = len(quality_data)
        total_score = sum(q['overall_score'] for q in quality_data)
        average_score = total_score / entity_count
        
        # 计算分数分布
        score_ranges = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
        score_distribution = {}
        
        for min_score, max_score in score_ranges:
            range_label = f"{min_score}-{max_score}"
            count = sum(1 for q in quality_data if min_score <= q['overall_score'] < max_score)
            score_distribution[range_label] = count
        
        # 计算各维度平均分
        all_dimensions = set()
        for q in quality_data:
            all_dimensions.update(q['dimensions'].keys())
        
        dimension_scores = {}
        for dimension in all_dimensions:
            dimension_values = [q['dimensions'][dimension] for q in quality_data if dimension in q['dimensions']]
            if dimension_values:
                dimension_scores[dimension] = sum(dimension_values) / len(dimension_values)
        
        return {
            'entity_count': entity_count,
            'average_score': average_score,
            'score_distribution': score_distribution,
            'dimension_scores': dimension_scores
        }
    
    def _save_entity(self, entity: MasterDataEntity):
        """保存实体到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO master_data 
        (entity_id, entity_type, attributes, source_system, creation_date, 
         last_update_date, status, version, golden_record)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entity.entity_id,
            entity.entity_type,
            json.dumps(entity.attributes),
            entity.source_system,
            entity.creation_date.isoformat(),
            entity.last_update_date.isoformat(),
            entity.status,
            entity.version,
            entity.golden_record
        ))
        
        conn.commit()
        conn.close()
    
    def _get_entity(self, entity_id: str) -> Optional[MasterDataEntity]:
        """从数据库获取实体"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM master_data WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return self._row_to_entity(row)
        return None
    
    def _get_entities_by_type(self, entity_type: str) -> List[MasterDataEntity]:
        """获取指定类型的所有实体"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM master_data WHERE entity_type = ? AND status = 'active'", 
                      (entity_type,))
        
        entities = []
        for row in cursor.fetchall():
            entities.append(self._row_to_entity(row))
        
        conn.close()
        
        return entities
    
    def _row_to_entity(self, row) -> MasterDataEntity:
        """将数据库行转换为实体对象"""
        return MasterDataEntity(
            entity_id=row[0],
            entity_type=row[1],
            attributes=json.loads(row[2]),
            source_system=row[3],
            creation_date=datetime.fromisoformat(row[4]),
            last_update_date=datetime.fromisoformat(row[5]),
            status=row[6],
            version=row[7],
            golden_record=bool(row[8])
        )
    
    def _save_match(self, match: Dict[str, Any]):
        """保存匹配记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO matches 
        (match_id, entity_id, matched_entity_id, match_score, match_type, 
         creation_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            match['match_id'],
            match['entity_id'],
            match['matched_entity_id'],
            match['match_score'],
            match['match_type'],
            match['creation_date'].isoformat(),
            match['status']
        ))
        
        conn.commit()
        conn.close()
    
    def _save_merge(self, merge: Dict[str, Any]):
        """保存合并记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO merges 
        (merge_id, golden_record_id, source_entity_ids, merge_strategy, 
         creation_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            merge['merge_id'],
            merge['golden_record_id'],
            merge['source_entity_ids'],
            merge['merge_strategy'],
            merge['creation_date'].isoformat(),
            merge['status']
        ))
        
        conn.commit()
        conn.close()
    
    def _deactivate_entity(self, entity_id: str):
        """停用实体"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE master_data SET status = 'inactive' WHERE entity_id = ?", 
                      (entity_id,))
        
        conn.commit()
        conn.close()
    
    def _get_entity_matches(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取实体的匹配记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM matches 
        WHERE entity_id = ? OR matched_entity_id = ?
        ORDER BY creation_date DESC
        ''', (entity_id, entity_id))
        
        matches = []
        for row in cursor.fetchall():
            matches.append({
                'match_id': row[0],
                'entity_id': row[1],
                'matched_entity_id': row[2],
                'match_score': row[3],
                'match_type': row[4],
                'creation_date': row[5],
                'status': row[6]
            })
        
        conn.close()
        
        return matches
    
    def _get_entity_merge(self, entity_id: str) -> Dict[str, Any]:
        """获取实体的合并记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM merges 
        WHERE golden_record_id = ? OR source_entity_ids LIKE ?
        ORDER BY creation_date DESC
        LIMIT 1
        ''', (entity_id, f"%{entity_id}%"))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'merge_id': row[0],
                'golden_record_id': row[1],
                'source_entity_ids': row[2],
                'merge_strategy': row[3],
                'creation_date': row[4],
                'status': row[5]
            }
        return None
    
    def _get_entity_distributions(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取实体的分发记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM distributions 
        WHERE entity_id = ?
        ORDER BY creation_date DESC
        ''', (entity_id,))
        
        distributions = []
        for row in cursor.fetchall():
            distributions.append({
                'distribution_id': row[0],
                'entity_id': row[1],
                'target_system': row[2],
                'distribution_type': row[3],
                'creation_date': row[4],
                'status': row[5],
                'response_data': row[6]
            })
        
        conn.close()
        
        return distributions
    
    def _get_entity_quality_assessments(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取实体的质量评估记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM quality_assessments 
        WHERE entity_id = ?
        ORDER BY assessment_date DESC
        ''', (entity_id,))
        
        assessments = []
        for row in cursor.fetchall():
            assessments.append({
                'assessment_id': row[0],
                'entity_id': row[1],
                'assessment_date': row[2],
                'dimensions': json.loads(row[3]),
                'overall_score': row[4],
                'status': row[5]
            })
        
        conn.close()
        
        return assessments


class RecordMatcher:
    """记录匹配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.matching_fields = config.get('fields', ['name', 'email', 'phone'])
        self.algorithm = config.get('algorithm', 'weighted')
        self.threshold = config.get('threshold', 0.8)
    
    def match(self, entity1: MasterDataEntity, entity2: MasterDataEntity) -> float:
        """计算两个实体的匹配分数"""
        if entity1.entity_type != entity2.entity_type:
            return 0.0  # 不同类型的实体不能匹配
        
        if self.algorithm == 'simple':
            return self._simple_match(entity1, entity2)
        elif self.algorithm == 'weighted':
            return self._weighted_match(entity1, entity2)
        else:
            return self._advanced_match(entity1, entity2)
    
    def _simple_match(self, entity1: MasterDataEntity, entity2: MasterDataEntity) -> float:
        """简单匹配算法"""
        matches = 0
        total = 0
        
        for field in self.matching_fields:
            if field in entity1.attributes and field in entity2.attributes:
                total += 1
                if entity1.attributes[field] == entity2.attributes[field]:
                    matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def _weighted_match(self, entity1: MasterDataEntity, entity2: MasterDataEntity) -> float:
        """加权匹配算法"""
        # 字段权重
        field_weights = {
            'name': 0.4,
            'email': 0.3,
            'phone': 0.2,
            'address': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for field in self.matching_fields:
            if field in entity1.attributes and field in entity2.attributes:
                weight = field_weights.get(field, 0.1)
                similarity = self._calculate_similarity(
                    str(entity1.attributes[field]),
                    str(entity2.attributes[field])
                )
                
                total_score += similarity * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _advanced_match(self, entity1: MasterDataEntity, entity2: MasterDataEntity) -> float:
        """高级匹配算法"""
        # 这里可以实现更复杂的匹配逻辑，例如使用机器学习模型
        # 为了简单起见，这里使用加权算法作为示例
        return self._weighted_match(entity1, entity2)
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        # 标准化字符串
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()
        
        if s1 == s2:
            return 1.0
        
        # 使用编辑距离计算相似度
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        # 计算编辑距离
        dp = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
        
        for i in range(len(s1) + 1):
            dp[i][0] = i
        
        for j in range(len(s2) + 1):
            dp[0][j] = j
        
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,  # 删除
                        dp[i][j-1] + 1,  # 插入
                        dp[i-1][j-1] + 1  # 替换
                    )
        
        edit_distance = dp[len(s1)][len(s2)]
        similarity = 1 - edit_distance / max_len
        
        return similarity


class RecordMerger:
    """记录合并器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strategy = config.get('strategy', 'source_priority')
        self.conflict_resolution = config.get('conflict_resolution', 'manual')
        self.source_priorities = config.get('source_priorities', {})
    
    def merge(self, entities: List[MasterDataEntity], strategy: str = None) -> MasterDataEntity:
        """合并实体列表"""
        if not entities:
            raise ValueError("No entities to merge")
        
        if len(entities) == 1:
            return entities[0]
        
        merge_strategy = strategy or self.strategy
        
        # 使用合并策略
        if merge_strategy == 'source_priority':
            return self._merge_by_source_priority(entities)
        elif merge_strategy == 'most_complete':
            return self._merge_by_completeness(entities)
        elif merge_strategy == 'latest_update':
            return self._merge_by_latest_update(entities)
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
    
    def _merge_by_source_priority(self, entities: List[MasterDataEntity]) -> MasterDataEntity:
        """按源系统优先级合并"""
        # 按优先级排序实体
        sorted_entities = sorted(entities, key=lambda e: self.source_priorities.get(e.source_system, 999))
        
        # 使用优先级最高的实体作为基础
        base_entity = sorted_entities[0]
        
        # 合并其他实体的属性
        merged_attributes = base_entity.attributes.copy()
        
        for entity in sorted_entities[1:]:
            for key, value in entity.attributes.items():
                if key not in merged_attributes or not merged_attributes[key]:
                    merged_attributes[key] = value
        
        # 创建新的黄金记录
        golden_record = MasterDataEntity(
            entity_id=str(uuid.uuid4()),
            entity_type=base_entity.entity_type,
            attributes=merged_attributes,
            source_system="MDM",
            creation_date=min(e.creation_date for e in entities),
            last_update_date=datetime.now(),
            version=1,
            golden_record=True
        )
        
        return golden_record
    
    def _merge_by_completeness(self, entities: List[MasterDataEntity]) -> MasterDataEntity:
        """按完整性合并"""
        # 计算每个实体的完整性得分
        def completeness_score(entity):
            non_empty_fields = sum(1 for v in entity.attributes.values() if v)
            total_fields = len(entity.attributes)
            return non_empty_fields / total_fields if total_fields > 0 else 0
        
        # 按完整性排序
        sorted_entities = sorted(entities, key=completeness_score, reverse=True)
        
        # 使用最完整的实体作为基础
        base_entity = sorted_entities[0]
        
        # 合并其他实体的属性
        merged_attributes = base_entity.attributes.copy()
        
        for entity in sorted_entities[1:]:
            for key, value in entity.attributes.items():
                if key not in merged_attributes or not merged_attributes[key]:
                    merged_attributes[key] = value
        
        # 创建新的黄金记录
        golden_record = MasterDataEntity(
            entity_id=str(uuid.uuid4()),
            entity_type=base_entity.entity_type,
            attributes=merged_attributes,
            source_system="MDM",
            creation_date=min(e.creation_date for e in entities),
            last_update_date=datetime.now(),
            version=1,
            golden_record=True
        )
        
        return golden_record
    
    def _merge_by_latest_update(self, entities: List[MasterDataEntity]) -> MasterDataEntity:
        """按最新更新时间合并"""
        # 按更新时间排序
        sorted_entities = sorted(entities, key=lambda e: e.last_update_date, reverse=True)
        
        # 使用最新更新的实体作为基础
        base_entity = sorted_entities[0]
        
        # 合并其他实体的属性
        merged_attributes = base_entity.attributes.copy()
        
        for entity in sorted_entities[1:]:
            for key, value in entity.attributes.items():
                if key not in merged_attributes or not merged_attributes[key]:
                    merged_attributes[key] = value
        
        # 创建新的黄金记录
        golden_record = MasterDataEntity(
            entity_id=str(uuid.uuid4()),
            entity_type=base_entity.entity_type,
            attributes=merged_attributes,
            source_system="MDM",
            creation_date=min(e.creation_date for e in entities),
            last_update_date=datetime.now(),
            version=1,
            golden_record=True
        )
        
        return golden_record


class DataDistributor:
    """数据分发器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.distribution_type = config.get('type', 'push')
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_interval = config.get('retry_interval', 60)
    
    def distribute_entity(self, entity: MasterDataEntity, target_systems: List[str] = None):
        """分发实体到目标系统"""
        if target_systems is None:
            target_systems = self._get_target_systems(entity.entity_type)
        
        for target_system in target_systems:
            distribution_id = str(uuid.uuid4())
            
            # 创建分发记录
            distribution = {
                'distribution_id': distribution_id,
                'entity_id': entity.entity_id,
                'target_system': target_system,
                'distribution_type': self.distribution_type,
                'creation_date': datetime.now(),
                'status': 'pending'
            }
            
            # 保存分发记录
            self._save_distribution(distribution)
            
            # 执行分发
            self._execute_distribution(distribution_id, entity, target_system)
    
    def _get_target_systems(self, entity_type: str) -> List[str]:
        """获取实体类型的目标系统"""
        # 这里简化处理，实际应该从配置中获取
        if entity_type == 'customer':
            return ['CRM', 'ERP', 'Marketing']
        elif entity_type == 'product':
            return ['ERP', 'E-Commerce', 'Inventory']
        elif entity_type == 'supplier':
            return ['ERP', 'Procurement']
        else:
            return ['Default']
    
    def _execute_distribution(self, distribution_id: str, entity: MasterDataEntity, 
                             target_system: str):
        """执行分发操作"""
        try:
            # 模拟API调用
            logger.info(f"Distributing entity {entity.entity_id} to {target_system}")
            
            # 更新分发状态
            self._update_distribution_status(
                distribution_id, 
                'completed',
                response_data={"status": "success", "message": "Data distributed successfully"}
            )
            
        except Exception as e:
            logger.error(f"Failed to distribute entity {entity.entity_id} to {target_system}: {e}")
            
            # 更新分发状态
            self._update_distribution_status(
                distribution_id,
                'failed',
                response_data={"status": "error", "message": str(e)}
            )
    
    def _save_distribution(self, distribution: Dict[str, Any]):
        """保存分发记录"""
        conn = sqlite3.connect("mdm.db")
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO distributions 
        (distribution_id, entity_id, target_system, distribution_type, 
         creation_date, status, response_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            distribution['distribution_id'],
            distribution['entity_id'],
            distribution['target_system'],
            distribution['distribution_type'],
            distribution['creation_date'].isoformat(),
            distribution['status'],
            json.dumps(distribution.get('response_data', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def _update_distribution_status(self, distribution_id: str, status: str, 
                                   response_data: Dict[str, Any] = None):
        """更新分发状态"""
        conn = sqlite3.connect("mdm.db")
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE distributions 
        SET status = ?, response_data = ?
        WHERE distribution_id = ?
        ''', (
            status,
            json.dumps(response_data or {}),
            distribution_id
        ))
        
        conn.commit()
        conn.close()


class DataQualityAssessor:
    """数据质量评估器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimensions = config.get('dimensions', ['completeness', 'accuracy', 'consistency'])
        self.thresholds = config.get('thresholds', {
            'completeness': 0.9,
            'accuracy': 0.95,
            'consistency': 0.9
        })
    
    def assess_entity(self, entity: MasterDataEntity) -> float:
        """评估实体数据质量"""
        dimension_scores = {}
        
        # 评估各维度
        if 'completeness' in self.dimensions:
            dimension_scores['completeness'] = self._assess_completeness(entity)
        
        if 'accuracy' in self.dimensions:
            dimension_scores['accuracy'] = self._assess_accuracy(entity)
        
        if 'consistency' in self.dimensions:
            dimension_scores['consistency'] = self._assess_consistency(entity)
        
        # 计算总体分数
        overall_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0
        
        # 保存评估结果
        self._save_quality_assessment(entity.entity_id, dimension_scores, overall_score)
        
        return overall_score
    
    def _assess_completeness(self, entity: MasterDataEntity) -> float:
        """评估完整性"""
        required_fields = self._get_required_fields(entity.entity_type)
        
        if not required_fields:
            return 1.0  # 如果没有必填字段，则认为是完整的
        
        filled_fields = sum(1 for field in required_fields 
                           if field in entity.attributes and entity.attributes[field])
        
        return filled_fields / len(required_fields)
    
    def _assess_accuracy(self, entity: MasterDataEntity) -> float:
        """评估准确性"""
        # 简化处理：根据属性值的格式和范围检查准确性
        accuracy_score = 1.0
        total_checks = 0
        passed_checks = 0
        
        # 检查邮箱格式
        if 'email' in entity.attributes and entity.attributes['email']:
            total_checks += 1
            email = entity.attributes['email']
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(email_pattern, email):
                passed_checks += 1
        
        # 检查电话格式
        if 'phone' in entity.attributes and entity.attributes['phone']:
            total_checks += 1
            phone = entity.attributes['phone']
            phone_pattern = r'^[\d\s\-\+\(\)]+$'
            if re.match(phone_pattern, phone) and len(phone.replace(' ', '').replace('-', '')) >= 7:
                passed_checks += 1
        
        # 检查邮编格式
        if 'postal_code' in entity.attributes and entity.attributes['postal_code']:
            total_checks += 1
            postal_code = entity.attributes['postal_code']
            postal_pattern = r'^[\d\-\s]+$'
            if re.match(postal_pattern, postal_code) and len(postal_code.replace('-', '').replace(' ', '')) >= 5:
                passed_checks += 1
        
        if total_checks > 0:
            accuracy_score = passed_checks / total_checks
        
        return accuracy_score
    
    def _assess_consistency(self, entity: MasterDataEntity) -> float:
        """评估一致性"""
        # 简化处理：检查不同属性之间的一致性
        consistency_score = 1.0
        total_checks = 0
        passed_checks = 0
        
        # 检查国家和城市的一致性
        if 'country' in entity.attributes and 'city' in entity.attributes:
            total_checks += 1
            # 这里简化处理，实际应该有一个国家-城市的对应表
            country = entity.attributes['country']
            city = entity.attributes['city']
            
            # 简单的例子：中国城市名称包含中文字符
            if country == 'China' and any('\u4e00' <= c <= '\u9fff' for c in city):
                passed_checks += 1
            elif country != 'China' and not any('\u4e00' <= c <= '\u9fff' for c in city):
                passed_checks += 1
        
        # 检查电话和国家代码的一致性
        if 'phone' in entity.attributes and 'country' in entity.attributes:
            total_checks += 1
            phone = entity.attributes['phone']
            country = entity.attributes['country']
            
            # 简化处理：中国电话以+86或13/14/15/16/17/18/19开头
            if country == 'China':
                if phone.startswith('+86') or (phone.startswith(('13', '14', '15', '16', '17', '18', '19')) and len(phone) == 11):
                    passed_checks += 1
            else:
                # 非中国电话
                passed_checks += 1  # 简化处理
        
        if total_checks > 0:
            consistency_score = passed_checks / total_checks
        
        return consistency_score
    
    def _get_required_fields(self, entity_type: str) -> List[str]:
        """获取实体类型的必填字段"""
        # 简化处理：根据实体类型返回必填字段
        if entity_type == 'customer':
            return ['name', 'email']
        elif entity_type == 'product':
            return ['name', 'sku', 'price']
        elif entity_type == 'supplier':
            return ['name', 'contact_email']
        else:
            return ['name']
    
    def _save_quality_assessment(self, entity_id: str, dimension_scores: Dict[str, float], 
                                overall_score: float):
        """保存质量评估结果"""
        assessment_id = str(uuid.uuid4())
        assessment_date = datetime.now().isoformat()
        
        conn = sqlite3.connect("mdm.db")
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO quality_assessments 
        (assessment_id, entity_id, assessment_date, dimensions, overall_score, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            assessment_id,
            entity_id,
            assessment_date,
            json.dumps(dimension_scores),
            overall_score,
            'active'
        ))
        
        conn.commit()
        conn.close()


def generate_sample_data(mdm_manager: MasterDataManager):
    """生成示例数据"""
    print("Generating sample data...")
    
    # 创建客户主数据
    customers = [
        {
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "+86-13812345678",
            "address": "北京市朝阳区建国路1号",
            "city": "北京",
            "country": "China",
            "postal_code": "100000",
            "source": "CRM"
        },
        {
            "name": "李四",
            "email": "lisi@example.com",
            "phone": "+86-13912345678",
            "address": "上海市浦东新区世纪大道100号",
            "city": "上海",
            "country": "China",
            "postal_code": "200000",
            "source": "Website"
        },
        {
            "name": "王五",
            "email": "wangwu@example.com",
            "phone": "+86-13712345678",
            "address": "广州市天河区珠江新城",
            "city": "广州",
            "country": "China",
            "postal_code": "510000",
            "source": "ERP"
        },
        {
            "name": "张三",  # 潜在重复记录
            "email": "zhangsan.work@example.com",
            "phone": "+86-13812345678",  # 相同电话
            "address": "北京市朝阳区建国路1号",  # 相同地址
            "city": "北京",
            "country": "China",
            "postal_code": "100000",
            "source": "Marketing"
        },
        {
            "name": "赵六",
            "email": "zhaoliu@example.com",
            "phone": "+86-13612345678",
            "address": "深圳市南山区科技园",
            "city": "深圳",
            "country": "China",
            "postal_code": "518000",
            "source": "CRM"
        }
    ]
    
    for customer in customers:
        mdm_manager.create_entity(
            entity_type="customer",
            attributes={k: v for k, v in customer.items() if k != "source"},
            source_system=customer["source"]
        )
    
    # 创建产品主数据
    products = [
        {
            "name": "智能手机",
            "sku": "PHONE-001",
            "description": "高性能智能手机",
            "price": 2999.99,
            "category": "电子产品",
            "source": "ERP"
        },
        {
            "name": "笔记本电脑",
            "sku": "LAPTOP-001",
            "description": "轻薄笔记本电脑",
            "price": 5999.99,
            "category": "电子产品",
            "source": "E-Commerce"
        },
        {
            "name": "智能手机",  # 潜在重复记录
            "sku": "PHONE-002",  # 不同SKU
            "description": "高性能智能手机",
            "price": 3099.99,  # 不同价格
            "category": "电子产品",
            "source": "Website"
        }
    ]
    
    for product in products:
        mdm_manager.create_entity(
            entity_type="product",
            attributes={k: v for k, v in product.items() if k != "source"},
            source_system=product["source"]
        )
    
    # 创建供应商主数据
    suppliers = [
        {
            "name": "供应商A",
            "contact_email": "contact@suppliera.com",
            "phone": "+86-01012345678",
            "address": "北京市海淀区中关村",
            "city": "北京",
            "country": "China",
            "postal_code": "100080",
            "supplier_type": "电子元件",
            "source": "ERP"
        },
        {
            "name": "供应商B",
            "contact_email": "contact@supplierb.com",
            "phone": "+86-02112345678",
            "address": "上海市浦东新区张江高科技园区",
            "city": "上海",
            "country": "China",
            "postal_code": "201203",
            "supplier_type": "塑料原料",
            "source": "Procurement"
        }
    ]
    
    for supplier in suppliers:
        mdm_manager.create_entity(
            entity_type="supplier",
            attributes={k: v for k, v in supplier.items() if k != "source"},
            source_system=supplier["source"]
        )
    
    print(f"Created {len(customers)} customers, {len(products)} products, {len(suppliers)} suppliers")


def demonstrate_mdm_capabilities(mdm_manager: MasterDataManager):
    """演示主数据管理能力"""
    print("\n=== 主数据管理能力演示 ===")
    
    # 1. 搜索实体
    print("\n1. 搜索客户实体:")
    customers = mdm_manager.search_entities(entity_type="customer", limit=5)
    for customer in customers:
        print(f"  - {customer['entity_id']}: {customer['attributes']['name']} ({customer['source_system']})")
    
    # 2. 实体匹配
    print("\n2. 执行实体匹配:")
    customer_matches = mdm_manager.match_entities("customer")
    print(f"  发现 {len(customer_matches)} 个潜在匹配")
    
    for match in customer_matches:
        print(f"  - 实体 {match['entity_id']} 与 {match['matched_entity_id']} 匹配分数: {match['match_score']:.2f}")
    
    # 3. 实体合并
    print("\n3. 合并重复实体:")
    if customer_matches:
        # 选择第一个匹配进行合并
        match = customer_matches[0]
        golden_record_id = mdm_manager.merge_entities([match['entity_id'], match['matched_entity_id']])
        print(f"  合并为黄金记录: {golden_record_id}")
        
        # 查看合并结果
        golden_record = mdm_manager.get_entity(golden_record_id)
        if golden_record:
            print(f"  合并后的实体: {golden_record['attributes']['name']} ({golden_record['source_system']})")
    
    # 4. 数据质量报告
    print("\n4. 数据质量报告:")
    quality_report = mdm_manager.get_quality_report()
    print(f"  总体平均质量分数: {quality_report['average_score']:.2f}")
    print("  质量分数分布:")
    for range_label, count in quality_report['score_distribution'].items():
        print(f"    {range_label}: {count} 个实体")
    print("  各维度平均分:")
    for dimension, score in quality_report['dimension_scores'].items():
        print(f"    {dimension}: {score:.2f}")
    
    # 5. 黄金记录
    print("\n5. 黄金记录:")
    golden_records = mdm_manager.get_golden_records()
    for record in golden_records:
        print(f"  - {record['entity_id']}: {record['attributes']['name']} ({record['entity_type']})")
    
    # 6. 实体历史
    print("\n6. 实体历史信息:")
    if golden_records:
        entity_history = mdm_manager.get_entity_history(golden_records[0]['entity_id'])
        print(f"  实体 ID: {entity_history['entity']['entity_id']}")
        print(f"  实体类型: {entity_history['entity']['entity_type']}")
        print(f"  创建日期: {entity_history['entity']['creation_date']}")
        print(f"  最后更新: {entity_history['entity']['last_update_date']}")
        print(f"  来源系统: {entity_history['entity']['source_system']}")
        print(f"  匹配记录数: {len(entity_history['matches'])}")
        print(f"  合并记录: {entity_history['merge'] is not None}")
        print(f"  分发记录数: {len(entity_history['distributions'])}")
        print(f"  质量评估数: {len(entity_history['quality_assessments'])}")


if __name__ == "__main__":
    # 创建主数据管理器
    mdm_manager = MasterDataManager()
    
    # 生成示例数据
    generate_sample_data(mdm_manager)
    
    # 演示主数据管理能力
    demonstrate_mdm_capabilities(mdm_manager)