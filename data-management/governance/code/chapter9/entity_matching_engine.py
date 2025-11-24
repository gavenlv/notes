#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实体匹配引擎
实现主数据的智能匹配和去重功能
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict
import re
import logging
import hashlib
import uuid
import difflib
from collections import defaultdict
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """匹配结果"""
    entity1_id: str
    entity2_id: str
    similarity_score: float
    match_type: str  # 'exact', 'high', 'medium', 'low'
    match_confidence: float  # 0.0-1.0
    match_method: str  # 'deterministic', 'probabilistic', 'ml'
    field_similarities: Dict[str, float]
    creation_date: datetime
    
    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['creation_date'] = self.creation_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建结果"""
        data['creation_date'] = datetime.fromisoformat(data['creation_date'])
        return cls(**data)


@dataclass
class MatchingRule:
    """匹配规则"""
    rule_id: str
    name: str
    description: str
    entity_type: str
    field_weights: Dict[str, float]
    similarity_threshold: float
    confidence_threshold: float
    match_method: str  # 'deterministic', 'probabilistic', 'ml'
    creation_date: datetime
    is_active: bool = True
    
    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['creation_date'] = self.creation_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建规则"""
        data['creation_date'] = datetime.fromisoformat(data['creation_date'])
        return cls(**data)


class SimilarityCalculator:
    """相似度计算器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.string_weight = self.config.get('string_weight', 1.0)
        self.number_weight = self.config.get('number_weight', 1.0)
        self.date_weight = self.config.get('date_weight', 1.0)
        self.boolean_weight = self.config.get('boolean_weight', 1.0)
    
    def calculate_similarity(self, value1: Any, value2: Any, value_type: str = None) -> float:
        """计算两个值的相似度"""
        if value1 is None or value2 is None:
            return 0.0 if value1 != value2 else 1.0
        
        if value1 == value2:
            return 1.0
        
        # 推断类型
        if value_type is None:
            if isinstance(value1, str):
                value_type = 'string'
            elif isinstance(value1, (int, float)):
                value_type = 'number'
            elif isinstance(value1, datetime):
                value_type = 'date'
            elif isinstance(value1, bool):
                value_type = 'boolean'
            else:
                value_type = 'string'
        
        # 根据类型计算相似度
        if value_type == 'string':
            return self._string_similarity(str(value1), str(value2))
        elif value_type == 'number':
            return self._number_similarity(float(value1), float(value2))
        elif value_type == 'date':
            return self._date_similarity(value1, value2)
        elif value_type == 'boolean':
            return self._boolean_similarity(bool(value1), bool(value2))
        else:
            return self._string_similarity(str(value1), str(value2))
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        # 标准化字符串
        s1 = self._normalize_string(str1)
        s2 = self._normalize_string(str2)
        
        # 精确匹配
        if s1 == s2:
            return 1.0
        
        # 计算编辑距离
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        # 使用difflib计算相似度
        similarity = difflib.SequenceMatcher(None, s1, s2).ratio()
        
        # 应用权重
        return similarity * self.string_weight
    
    def _number_similarity(self, num1: float, num2: float) -> float:
        """计算数值相似度"""
        if num1 == num2:
            return 1.0
        
        # 计算相对差异
        avg = (abs(num1) + abs(num2)) / 2
        if avg == 0:
            return 1.0
        
        diff = abs(num1 - num2) / avg
        similarity = max(0, 1 - diff)
        
        # 应用权重
        return similarity * self.number_weight
    
    def _date_similarity(self, date1: datetime, date2: datetime) -> float:
        """计算日期相似度"""
        if date1 == date2:
            return 1.0
        
        # 计算天数差异
        diff_days = abs((date1 - date2).days)
        
        # 1周内视为高相似度
        if diff_days <= 7:
            similarity = 0.9
        # 1个月内视为中等相似度
        elif diff_days <= 30:
            similarity = 0.7
        # 3个月内视为低相似度
        elif diff_days <= 90:
            similarity = 0.5
        else:
            similarity = max(0, 0.3 - (diff_days - 90) / 365)
        
        # 应用权重
        return similarity * self.date_weight
    
    def _boolean_similarity(self, bool1: bool, bool2: bool) -> float:
        """计算布尔值相似度"""
        similarity = 1.0 if bool1 == bool2 else 0.0
        return similarity * self.boolean_weight
    
    def _normalize_string(self, s: str) -> str:
        """标准化字符串"""
        # 转换为小写
        s = s.lower()
        
        # 移除多余的空格
        s = re.sub(r'\s+', ' ', s).strip()
        
        # 移除标点符号（可选）
        # s = re.sub(r'[^\w\s]', '', s)
        
        # 标准化常见的变体
        replacements = {
            '&': ' and ',
            '@': ' at ',
            '#': ' number ',
            '0': ' zero ',
            '1': ' one ',
            '2': ' two ',
            '3': ' three ',
            '4': ' four ',
            '5': ' five ',
            '6': ' six ',
            '7': ' seven ',
            '8': ' eight ',
            '9': ' nine '
        }
        
        for old, new in replacements.items():
            s = s.replace(old, new)
        
        return s.strip()


class DeterministicMatcher:
    """确定性匹配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.key_fields = self.config.get('key_fields', ['id', 'code', 'email'])
        self.similarity_calculator = SimilarityCalculator()
    
    def match(self, entity1: Dict[str, Any], entity2: Dict[str, Any], 
              rule: MatchingRule) -> Optional[MatchResult]:
        """确定性匹配"""
        # 检查关键字段
        for field in self.key_fields:
            if field in entity1 and field in entity2:
                similarity = self.similarity_calculator.calculate_similarity(
                    entity1[field], entity2[field]
                )
                
                # 如果关键字段完全匹配，则认为是同一实体
                if similarity == 1.0:
                    return self._create_match_result(
                        entity1.get('entity_id'), entity2.get('entity_id'), 
                        1.0, 'exact', rule
                    )
        
        # 如果没有关键字段完全匹配，计算综合相似度
        field_similarities = {}
        total_weight = 0.0
        weighted_similarity = 0.0
        
        for field, weight in rule.field_weights.items():
            if field in entity1 and field in entity2:
                similarity = self.similarity_calculator.calculate_similarity(
                    entity1[field], entity2[field]
                )
                field_similarities[field] = similarity
                weighted_similarity += similarity * weight
                total_weight += weight
        
        # 如果没有共同字段，则无法匹配
        if total_weight == 0:
            return None
        
        # 计算加权平均相似度
        overall_similarity = weighted_similarity / total_weight
        
        # 判断是否匹配
        if overall_similarity >= rule.similarity_threshold:
            match_type = 'high' if overall_similarity >= 0.9 else 'medium'
            return self._create_match_result(
                entity1.get('entity_id'), entity2.get('entity_id'), 
                overall_similarity, match_type, rule, field_similarities
            )
        
        return None
    
    def _create_match_result(self, entity1_id: str, entity2_id: str, 
                          similarity_score: float, match_type: str, 
                          rule: MatchingRule, field_similarities: Dict[str, float] = None) -> MatchResult:
        """创建匹配结果"""
        confidence = min(1.0, similarity_score * 1.2)  # 确定性匹配置信度略高
        
        return MatchResult(
            entity1_id=entity1_id,
            entity2_id=entity2_id,
            similarity_score=similarity_score,
            match_type=match_type,
            match_confidence=confidence,
            match_method='deterministic',
            field_similarities=field_similarities or {},
            creation_date=datetime.now()
        )


class ProbabilisticMatcher:
    """概率性匹配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.field_weights = self.config.get('field_weights', {})
        self.similarity_calculator = SimilarityCalculator()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def match(self, entity1: Dict[str, Any], entity2: Dict[str, Any], 
              rule: MatchingRule) -> Optional[MatchResult]:
        """概率性匹配"""
        field_similarities = {}
        total_weight = 0.0
        weighted_similarity = 0.0
        
        # 计算各字段相似度
        for field, weight in rule.field_weights.items():
            if field in entity1 and field in entity2:
                value1 = entity1[field]
                value2 = entity2[field]
                
                # 对字符串类型使用更高级的相似度计算
                if isinstance(value1, str) and isinstance(value2, str):
                    similarity = self._advanced_string_similarity(value1, value2)
                else:
                    similarity = self.similarity_calculator.calculate_similarity(value1, value2)
                
                field_similarities[field] = similarity
                weighted_similarity += similarity * weight
                total_weight += weight
        
        # 如果没有共同字段，则无法匹配
        if total_weight == 0:
            return None
        
        # 计算加权平均相似度
        overall_similarity = weighted_similarity / total_weight
        
        # 使用概率模型计算置信度
        confidence = self._calculate_confidence(overall_similarity, field_similarities, rule)
        
        # 判断是否匹配
        if confidence >= rule.confidence_threshold:
            match_type = self._determine_match_type(confidence)
            return self._create_match_result(
                entity1.get('entity_id'), entity2.get('entity_id'), 
                overall_similarity, match_type, rule, field_similarities, confidence
            )
        
        return None
    
    def _advanced_string_similarity(self, str1: str, str2: str) -> float:
        """高级字符串相似度计算"""
        # 标准化字符串
        s1 = self.similarity_calculator._normalize_string(str1)
        s2 = self.similarity_calculator._normalize_string(str2)
        
        # 精确匹配
        if s1 == s2:
            return 1.0
        
        # 使用TF-IDF计算相似度
        try:
            # 创建文档集合
            documents = [s1, s2]
            
            # 向量化
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            
            # 计算余弦相似度
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
        except:
            # 如果TF-IDF失败，使用简单的字符串相似度
            return self.similarity_calculator._string_similarity(s1, s2)
    
    def _calculate_confidence(self, overall_similarity: float, 
                             field_similarities: Dict[str, float], 
                             rule: MatchingRule) -> float:
        """计算匹配置信度"""
        # 基础置信度等于整体相似度
        base_confidence = overall_similarity
        
        # 调整因子
        factors = []
        
        # 1. 高权重字段的匹配情况
        if rule.field_weights:
            high_weight_fields = {f: w for f, w in rule.field_weights.items() if w > 0.5}
            if high_weight_fields:
                high_weight_similarities = [
                    field_similarities.get(f, 0) for f in high_weight_fields
                ]
                avg_high_weight_similarity = sum(high_weight_similarities) / len(high_weight_similarities)
                factors.append(avg_high_weight_similarity)
        
        # 2. 匹配字段的比例
        match_ratio = len(field_similarities) / len(rule.field_weights)
        factors.append(match_ratio)
        
        # 3. 相似度分布的一致性
        if field_similarities:
            similarities = list(field_similarities.values())
            mean_similarity = sum(similarities) / len(similarities)
            variance = sum((s - mean_similarity) ** 2 for s in similarities) / len(similarities)
            consistency = max(0, 1 - variance)  # 方差越小，一致性越高
            factors.append(consistency)
        
        # 综合计算置信度
        if factors:
            adjusted_confidence = (base_confidence + sum(factors) / len(factors)) / 2
        else:
            adjusted_confidence = base_confidence
        
        return min(1.0, max(0.0, adjusted_confidence))
    
    def _determine_match_type(self, confidence: float) -> str:
        """确定匹配类型"""
        if confidence >= 0.95:
            return 'exact'
        elif confidence >= 0.85:
            return 'high'
        elif confidence >= 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _create_match_result(self, entity1_id: str, entity2_id: str, 
                          similarity_score: float, match_type: str, 
                          rule: MatchingRule, field_similarities: Dict[str, float], 
                          confidence: float) -> MatchResult:
        """创建匹配结果"""
        return MatchResult(
            entity1_id=entity1_id,
            entity2_id=entity2_id,
            similarity_score=similarity_score,
            match_type=match_type,
            match_confidence=confidence,
            match_method='probabilistic',
            field_similarities=field_similarities,
            creation_date=datetime.now()
        )


class MLMatcher:
    """机器学习匹配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_path = self.config.get('model_path', 'entity_matcher_model.pkl')
        self.model = None
        self.feature_columns = self.config.get('feature_columns', [])
        self.similarity_calculator = SimilarityCalculator()
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded ML matching model from {self.model_path}")
            else:
                logger.warning(f"Model file {self.model_path} not found, using default RandomForest")
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """训练模型"""
        if not training_data:
            logger.error("No training data provided")
            return {'status': 'error', 'message': 'No training data'}
        
        # 准备训练数据
        X = []
        y = []
        
        for item in training_data:
            entity1 = item.get('entity1', {})
            entity2 = item.get('entity2', {})
            is_match = item.get('is_match', False)
            
            # 提取特征
            features = self._extract_features(entity1, entity2)
            X.append(features)
            y.append(1 if is_match else 0)
        
        # 转换为numpy数组
        X = np.array(X)
        y = np.array(y)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 训练模型
        self.model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # 保存模型
        try:
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
        
        return {
            'status': 'success',
            'accuracy': accuracy,
            'classification_report': report,
            'feature_importance': dict(zip(
                self.feature_columns, 
                self.model.feature_importances_
            ))
        }
    
    def match(self, entity1: Dict[str, Any], entity2: Dict[str, Any], 
              rule: MatchingRule) -> Optional[MatchResult]:
        """机器学习匹配"""
        if self.model is None:
            logger.error("Model not trained or loaded")
            return None
        
        # 提取特征
        features = self._extract_features(entity1, entity2)
        
        # 预测
        try:
            match_proba = self.model.predict_proba([features])[0]
            match_probability = match_proba[1]  # 类别1的概率
            
            # 计算字段相似度
            field_similarities = {}
            for field in rule.field_weights:
                if field in entity1 and field in entity2:
                    similarity = self.similarity_calculator.calculate_similarity(
                        entity1[field], entity2[field]
                    )
                    field_similarities[field] = similarity
            
            # 计算整体相似度
            if field_similarities:
                overall_similarity = sum(field_similarities.values()) / len(field_similarities)
            else:
                overall_similarity = 0.0
            
            # 判断是否匹配
            if match_probability >= rule.confidence_threshold:
                match_type = self._determine_match_type(match_probability)
                return self._create_match_result(
                    entity1.get('entity_id'), entity2.get('entity_id'), 
                    overall_similarity, match_type, rule, field_similarities, match_probability
                )
            
            return None
        except Exception as e:
            logger.error(f"Error in ML matching: {e}")
            return None
    
    def _extract_features(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> List[float]:
        """提取特征"""
        features = []
        
        # 对于每个预定义的特征列，计算相似度
        for field in self.feature_columns:
            if field in entity1 and field in entity2:
                similarity = self.similarity_calculator.calculate_similarity(
                    entity1[field], entity2[field]
                )
                features.append(similarity)
            else:
                features.append(0.0)
        
        # 如果没有预定义的特征列，使用所有共同字段
        if not self.feature_columns:
            common_fields = set(entity1.keys()) & set(entity2.keys())
            common_fields.discard('entity_id')  # 排除实体ID
            
            for field in common_fields:
                similarity = self.similarity_calculator.calculate_similarity(
                    entity1[field], entity2[field]
                )
                features.append(similarity)
            
            # 记录使用的特征列
            self.feature_columns = list(common_fields)
        
        # 确保特征数量一致
        while len(features) < len(self.feature_columns):
            features.append(0.0)
        
        return features[:len(self.feature_columns)]
    
    def _determine_match_type(self, confidence: float) -> str:
        """确定匹配类型"""
        if confidence >= 0.95:
            return 'exact'
        elif confidence >= 0.85:
            return 'high'
        elif confidence >= 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _create_match_result(self, entity1_id: str, entity2_id: str, 
                          similarity_score: float, match_type: str, 
                          rule: MatchingRule, field_similarities: Dict[str, float], 
                          confidence: float) -> MatchResult:
        """创建匹配结果"""
        return MatchResult(
            entity1_id=entity1_id,
            entity2_id=entity2_id,
            similarity_score=similarity_score,
            match_type=match_type,
            match_confidence=confidence,
            match_method='ml',
            field_similarities=field_similarities,
            creation_date=datetime.now()
        )


class EntityMatchingEngine:
    """实体匹配引擎"""
    
    def __init__(self, config_path: str = None):
        """初始化匹配引擎"""
        self.config = self._load_config(config_path)
        
        # 初始化数据库
        self.db_path = self.config.get('db_path', 'entity_matching.db')
        self._initialize_database()
        
        # 初始化匹配器
        self.deterministic_matcher = DeterministicMatcher(self.config.get('deterministic', {}))
        self.probabilistic_matcher = ProbabilisticMatcher(self.config.get('probabilistic', {}))
        self.ml_matcher = MLMatcher(self.config.get('ml', {}))
        
        # 加载匹配规则
        self.rules = {}
        self._load_rules()
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "db_path": "entity_matching.db",
            "deterministic": {
                "key_fields": ["id", "code", "email", "phone"]
            },
            "probabilistic": {
                "field_weights": {}
            },
            "ml": {
                "model_path": "entity_matcher_model.pkl",
                "feature_columns": []
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # 合并配置
                for key, value in file_config.items():
                    if key in default_config and isinstance(default_config[key], dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
        
        return default_config
    
    def _initialize_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建匹配规则表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS matching_rules (
            rule_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            entity_type TEXT NOT NULL,
            field_weights TEXT NOT NULL,
            similarity_threshold REAL,
            confidence_threshold REAL,
            match_method TEXT NOT NULL,
            creation_date TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # 创建匹配结果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_results (
            match_id TEXT PRIMARY KEY,
            entity1_id TEXT NOT NULL,
            entity2_id TEXT NOT NULL,
            similarity_score REAL NOT NULL,
            match_type TEXT NOT NULL,
            match_confidence REAL NOT NULL,
            match_method TEXT NOT NULL,
            field_similarities TEXT,
            creation_date TEXT NOT NULL
        )
        ''')
        
        # 创建匹配记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_records (
            record_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            total_entities INTEGER NOT NULL,
            total_matches INTEGER NOT NULL,
            processing_time REAL NOT NULL,
            creation_date TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_rules(self):
        """加载匹配规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM matching_rules WHERE is_active = 1")
        rows = cursor.fetchall()
        
        for row in rows:
            rule = MatchingRule(
                rule_id=row[0],
                name=row[1],
                description=row[2],
                entity_type=row[3],
                field_weights=json.loads(row[4]),
                similarity_threshold=row[5],
                confidence_threshold=row[6],
                match_method=row[7],
                creation_date=datetime.fromisoformat(row[8]),
                is_active=bool(row[9])
            )
            self.rules[rule.rule_id] = rule
        
        conn.close()
        
        # 如果没有规则，创建默认规则
        if not self.rules:
            self._create_default_rules()
    
    def _create_default_rules(self):
        """创建默认匹配规则"""
        default_rules = [
            {
                "name": "客户确定性匹配",
                "description": "基于关键字段的客户确定性匹配",
                "entity_type": "customer",
                "field_weights": {
                    "email": 0.4,
                    "phone": 0.3,
                    "name": 0.2,
                    "address": 0.1
                },
                "similarity_threshold": 0.8,
                "confidence_threshold": 0.8,
                "match_method": "deterministic"
            },
            {
                "name": "客户概率性匹配",
                "description": "基于多字段权重的客户概率性匹配",
                "entity_type": "customer",
                "field_weights": {
                    "name": 0.4,
                    "email": 0.3,
                    "phone": 0.2,
                    "address": 0.1
                },
                "similarity_threshold": 0.7,
                "confidence_threshold": 0.7,
                "match_method": "probabilistic"
            },
            {
                "name": "产品确定性匹配",
                "description": "基于SKU的产品确定性匹配",
                "entity_type": "product",
                "field_weights": {
                    "sku": 0.5,
                    "name": 0.3,
                    "category": 0.2
                },
                "similarity_threshold": 0.9,
                "confidence_threshold": 0.9,
                "match_method": "deterministic"
            }
        ]
        
        for rule_data in default_rules:
            rule = MatchingRule(
                rule_id=str(uuid.uuid4()),
                creation_date=datetime.now(),
                **rule_data
            )
            self._save_rule(rule)
            self.rules[rule.rule_id] = rule
        
        logger.info(f"Created {len(default_rules)} default matching rules")
    
    def add_rule(self, name: str, entity_type: str, field_weights: Dict[str, float],
                similarity_threshold: float, confidence_threshold: float, 
                match_method: str, description: str = None) -> str:
        """添加匹配规则"""
        rule = MatchingRule(
            rule_id=str(uuid.uuid4()),
            name=name,
            description=description or f"{entity_type} matching rule",
            entity_type=entity_type,
            field_weights=field_weights,
            similarity_threshold=similarity_threshold,
            confidence_threshold=confidence_threshold,
            match_method=match_method,
            creation_date=datetime.now()
        )
        
        self._save_rule(rule)
        self.rules[rule.rule_id] = rule
        
        logger.info(f"Added matching rule: {name}")
        return rule.rule_id
    
    def update_rule(self, rule_id: str, **kwargs) -> bool:
        """更新匹配规则"""
        if rule_id not in self.rules:
            logger.error(f"Rule {rule_id} not found")
            return False
        
        rule = self.rules[rule_id]
        
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self._save_rule(rule)
        
        logger.info(f"Updated matching rule: {rule.name}")
        return True
    
    def delete_rule(self, rule_id: str) -> bool:
        """删除匹配规则"""
        if rule_id not in self.rules:
            logger.error(f"Rule {rule_id} not found")
            return False
        
        # 标记为非活动状态
        rule = self.rules[rule_id]
        rule.is_active = False
        
        self._save_rule(rule)
        del self.rules[rule_id]
        
        logger.info(f"Deleted matching rule: {rule.name}")
        return True
    
    def find_matches(self, entities: List[Dict[str, Any]], 
                    entity_type: str = None, rule_ids: List[str] = None) -> List[MatchResult]:
        """查找匹配的实体"""
        if len(entities) < 2:
            logger.warning("Need at least 2 entities to find matches")
            return []
        
        # 确定要使用的规则
        if rule_ids:
            rules_to_use = [self.rules[rule_id] for rule_id in rule_ids if rule_id in self.rules]
        else:
            # 根据实体类型筛选规则
            if entity_type:
                rules_to_use = [rule for rule in self.rules.values() 
                              if rule.entity_type == entity_type]
            else:
                rules_to_use = list(self.rules.values())
        
        if not rules_to_use:
            logger.warning("No matching rules available")
            return []
        
        start_time = datetime.now()
        match_results = []
        
        # 两两比较所有实体
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity1 = entities[i]
                entity2 = entities[j]
                
                # 应用每个规则
                for rule in rules_to_use:
                    match_result = self._apply_rule(entity1, entity2, rule)
                    if match_result:
                        match_results.append(match_result)
        
        # 记录匹配记录
        processing_time = (datetime.now() - start_time).total_seconds()
        self._save_match_record(
            entity_type=entity_type or 'unknown',
            total_entities=len(entities),
            total_matches=len(match_results),
            processing_time=processing_time
        )
        
        logger.info(f"Found {len(match_results)} matches among {len(entities)} entities in {processing_time:.2f}s")
        
        return match_results
    
    def find_duplicates(self, entities: List[Dict[str, Any]], 
                       entity_type: str = None, threshold: float = 0.8) -> List[List[str]]:
        """查找重复实体"""
        matches = self.find_matches(entities, entity_type)
        
        # 筛选高置信度匹配
        high_confidence_matches = [
            m for m in matches 
            if m.match_confidence >= threshold
        ]
        
        # 构建实体关系图
        entity_graph = defaultdict(set)
        for match in high_confidence_matches:
            entity_graph[match.entity1_id].add(match.entity2_id)
            entity_graph[match.entity2_id].add(match.entity1_id)
        
        # 查找连通分量（重复组）
        visited = set()
        duplicate_groups = []
        
        for entity_id in entity_graph:
            if entity_id not in visited:
                group = []
                stack = [entity_id]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        group.append(current)
                        stack.extend(entity_graph[current] - visited)
                
                if len(group) > 1:
                    duplicate_groups.append(group)
        
        logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        
        return duplicate_groups
    
    def train_ml_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """训练机器学习模型"""
        logger.info("Training ML matching model...")
        result = self.ml_matcher.train(training_data)
        
        if result['status'] == 'success':
            logger.info(f"Model trained with accuracy: {result['accuracy']:.2f}")
        else:
            logger.error(f"Model training failed: {result.get('message', 'Unknown error')}")
        
        return result
    
    def get_match_history(self, entity_id: str = None, entity_type: str = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """获取匹配历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
        SELECT r.* 
        FROM match_results r
        JOIN match_records rec ON r.match_id LIKE '%' || rec.record_id || '%'
        WHERE 1=1
        '''
        params = []
        
        if entity_id:
            query += " AND (r.entity1_id = ? OR r.entity2_id = ?)"
            params.extend([entity_id, entity_id])
        
        if entity_type:
            query += " AND rec.entity_type = ?"
            params.append(entity_type)
        
        query += " ORDER BY r.creation_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            result = MatchResult(
                match_id=row[0],
                entity1_id=row[1],
                entity2_id=row[2],
                similarity_score=row[3],
                match_type=row[4],
                match_confidence=row[5],
                match_method=row[6],
                field_similarities=json.loads(row[7]) if row[7] else {},
                creation_date=datetime.fromisoformat(row[8])
            )
            results.append(result.to_dict())
        
        conn.close()
        
        return results
    
    def get_matching_statistics(self) -> Dict[str, Any]:
        """获取匹配统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总匹配数
        cursor.execute("SELECT COUNT(*) FROM match_results")
        total_matches = cursor.fetchone()[0]
        
        # 按匹配类型统计
        cursor.execute("""
        SELECT match_type, COUNT(*) 
        FROM match_results 
        GROUP BY match_type
        """)
        match_type_counts = dict(cursor.fetchall())
        
        # 按匹配方法统计
        cursor.execute("""
        SELECT match_method, COUNT(*) 
        FROM match_results 
        GROUP BY match_method
        """)
        match_method_counts = dict(cursor.fetchall())
        
        # 平均置信度
        cursor.execute("SELECT AVG(match_confidence) FROM match_results")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # 最近24小时的匹配数
        cursor.execute("""
        SELECT COUNT(*) 
        FROM match_results 
        WHERE creation_date > datetime('now', '-1 day')
        """)
        recent_matches = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_matches': total_matches,
            'match_type_counts': match_type_counts,
            'match_method_counts': match_method_counts,
            'average_confidence': avg_confidence,
            'recent_matches_24h': recent_matches
        }
    
    def _apply_rule(self, entity1: Dict[str, Any], entity2: Dict[str, Any], 
                   rule: MatchingRule) -> Optional[MatchResult]:
        """应用匹配规则"""
        try:
            if rule.match_method == 'deterministic':
                return self.deterministic_matcher.match(entity1, entity2, rule)
            elif rule.match_method == 'probabilistic':
                return self.probabilistic_matcher.match(entity1, entity2, rule)
            elif rule.match_method == 'ml':
                return self.ml_matcher.match(entity1, entity2, rule)
            else:
                logger.warning(f"Unknown match method: {rule.match_method}")
                return None
        except Exception as e:
            logger.error(f"Error applying rule {rule.name}: {e}")
            return None
    
    def _save_rule(self, rule: MatchingRule):
        """保存匹配规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO matching_rules 
        (rule_id, name, description, entity_type, field_weights, 
         similarity_threshold, confidence_threshold, match_method, 
         creation_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.rule_id,
            rule.name,
            rule.description,
            rule.entity_type,
            json.dumps(rule.field_weights),
            rule.similarity_threshold,
            rule.confidence_threshold,
            rule.match_method,
            rule.creation_date.isoformat(),
            rule.is_active
        ))
        
        conn.commit()
        conn.close()
    
    def _save_match_result(self, result: MatchResult):
        """保存匹配结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        match_id = str(uuid.uuid4())
        
        cursor.execute('''
        INSERT INTO match_results 
        (match_id, entity1_id, entity2_id, similarity_score, match_type, 
         match_confidence, match_method, field_similarities, creation_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            result.entity1_id,
            result.entity2_id,
            result.similarity_score,
            result.match_type,
            result.match_confidence,
            result.match_method,
            json.dumps(result.field_similarities),
            result.creation_date.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_match_record(self, entity_type: str, total_entities: int, 
                          total_matches: int, processing_time: float):
        """保存匹配记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        record_id = str(uuid.uuid4())
        
        cursor.execute('''
        INSERT INTO match_records 
        (record_id, entity_type, total_entities, total_matches, 
         processing_time, creation_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            record_id,
            entity_type,
            total_entities,
            total_matches,
            processing_time,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()


def generate_sample_entities(entity_type: str, count: int = 20) -> List[Dict[str, Any]]:
    """生成示例实体"""
    import random
    
    if entity_type == 'customer':
        first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴']
        last_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军']
        domains = ['example.com', 'test.com', 'demo.com', 'sample.com']
        
        entities = []
        for i in range(count):
            name = f"{random.choice(first_names)}{random.choice(last_names)}"
            email = f"{name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"
            phone = f"+86-13{random.randint(100000000, 999999999)}"
            address = f"{random.choice(['北京市', '上海市', '广州市', '深圳市'])}某区某街道{random.randint(1, 100)}号"
            
            # 创建一些可能的重复记录
            if random.random() < 0.2:  # 20%的概率创建重复
                base_index = random.randint(0, max(0, len(entities) - 1))
                base_entity = entities[base_index]
                name = base_entity['name']
                email = base_entity['email']
                phone = base_entity['phone']
                if random.random() < 0.5:
                    address = f"{random.choice(['北京市', '上海市', '广州市', '深圳市'])}某区某街道{random.randint(1, 100)}号"
            
            entity = {
                'entity_id': f"cust-{i+1:03d}",
                'name': name,
                'email': email,
                'phone': phone,
                'address': address
            }
            entities.append(entity)
        
        return entities
    
    elif entity_type == 'product':
        products = ['智能手机', '笔记本电脑', '平板电脑', '智能手表', '蓝牙耳机']
        brands = ['品牌A', '品牌B', '品牌C', '品牌D']
        
        entities = []
        for i in range(count):
            product_name = random.choice(products)
            brand = random.choice(brands)
            sku = f"{brand[0]}{product_name[0]}{random.randint(1000, 9999)}"
            price = round(random.uniform(100.0, 5000.0), 2)
            category = random.choice(['电子产品', '数码配件', '智能设备'])
            
            # 创建一些可能的重复记录
            if random.random() < 0.2:  # 20%的概率创建重复
                base_index = random.randint(0, max(0, len(entities) - 1))
                base_entity = entities[base_index]
                product_name = base_entity['name']
                sku = base_entity['sku']
                if random.random() < 0.5:
                    price = base_entity['price'] * random.uniform(0.95, 1.05)
            
            entity = {
                'entity_id': f"prod-{i+1:03d}",
                'name': f"{brand} {product_name}",
                'sku': sku,
                'price': price,
                'category': category
            }
            entities.append(entity)
        
        return entities
    
    else:
        # 默认生成通用实体
        entities = []
        for i in range(count):
            entity = {
                'entity_id': f"entity-{i+1:03d}",
                'name': f"实体 {i+1}",
                'value': random.randint(1, 100)
            }
            entities.append(entity)
        
        return entities


def generate_training_data(entity_type: str, count: int = 100) -> List[Dict[str, Any]]:
    """生成训练数据"""
    import random
    
    entities = generate_sample_entities(entity_type, count // 2)
    training_data = []
    
    # 创建正例（匹配的实体对）
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            if random.random() < 0.3:  # 30%的概率创建正例
                entity1 = entities[i].copy()
                entity2 = entities[j].copy()
                
                # 增加一些相似性
                if random.random() < 0.5 and 'email' in entity1 and 'email' in entity2:
                    # 有50%的概率共享邮箱
                    entity2['email'] = entity1['email']
                
                training_data.append({
                    'entity1': entity1,
                    'entity2': entity2,
                    'is_match': True
                })
    
    # 创建负例（不匹配的实体对）
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            if random.random() < 0.2:  # 20%的概率创建负例
                entity1 = entities[i].copy()
                entity2 = entities[j].copy()
                
                # 确保它们不匹配
                if entity1.get('email') == entity2.get('email'):
                    entity2['email'] = f"different{entity2['email']}"
                
                training_data.append({
                    'entity1': entity1,
                    'entity2': entity2,
                    'is_match': False
                })
    
    return training_data


def demonstrate_matching_capabilities():
    """演示匹配能力"""
    # 创建匹配引擎
    matching_engine = EntityMatchingEngine()
    
    print("\n=== 实体匹配引擎演示 ===")
    
    # 1. 生成示例客户实体
    print("\n1. 生成示例客户实体:")
    customers = generate_sample_entities('customer', 15)
    for customer in customers[:5]:  # 只显示前5个
        print(f"  {customer['entity_id']}: {customer['name']}, {customer['email']}")
    
    # 2. 查找匹配
    print("\n2. 查找匹配:")
    matches = matching_engine.find_matches(customers, 'customer')
    
    print(f"  找到 {len(matches)} 个匹配:")
    for match in matches[:5]:  # 只显示前5个
        print(f"  {match['entity1_id']} ↔ {match['entity2_id']}: "
              f"{match['match_type']} (置信度: {match['match_confidence']:.2f})")
    
    # 3. 查找重复实体
    print("\n3. 查找重复实体:")
    duplicate_groups = matching_engine.find_duplicates(customers, 'customer')
    
    print(f"  找到 {len(duplicate_groups)} 个重复组:")
    for i, group in enumerate(duplicate_groups):
        print(f"  组 {i+1}: {', '.join(group)}")
    
    # 4. 添加自定义匹配规则
    print("\n4. 添加自定义匹配规则:")
    rule_id = matching_engine.add_rule(
        name="客户姓名匹配",
        entity_type="customer",
        field_weights={"name": 1.0},
        similarity_threshold=0.9,
        confidence_threshold=0.9,
        match_method="deterministic",
        description="基于姓名的客户匹配"
    )
    print(f"  添加规则 ID: {rule_id}")
    
    # 5. 使用新规则查找匹配
    print("\n5. 使用新规则查找匹配:")
    matches = matching_engine.find_matches(customers, 'customer', [rule_id])
    
    print(f"  找到 {len(matches)} 个匹配:")
    for match in matches:
        print(f"  {match['entity1_id']} ↔ {match['entity2_id']}: "
              f"{match['match_type']} (置信度: {match['match_confidence']:.2f})")
    
    # 6. 生成训练数据并训练ML模型
    print("\n6. 生成训练数据并训练ML模型:")
    training_data = generate_training_data('customer', 50)
    print(f"  生成 {len(training_data)} 个训练样本")
    
    train_result = matching_engine.train_ml_model(training_data)
    if train_result['status'] == 'success':
        print(f"  模型训练成功，准确率: {train_result['accuracy']:.2f}")
    else:
        print(f"  模型训练失败: {train_result.get('message', 'Unknown error')}")
    
    # 7. 使用ML模型查找匹配
    if train_result['status'] == 'success':
        print("\n7. 使用ML模型查找匹配:")
        ml_rule_id = matching_engine.add_rule(
            name="客户ML匹配",
            entity_type="customer",
            field_weights={"name": 0.4, "email": 0.3, "phone": 0.2, "address": 0.1},
            similarity_threshold=0.7,
            confidence_threshold=0.7,
            match_method="ml",
            description="基于机器学习的客户匹配"
        )
        
        matches = matching_engine.find_matches(customers[:10], 'customer', [ml_rule_id])
        
        print(f"  找到 {len(matches)} 个匹配:")
        for match in matches:
            print(f"  {match['entity1_id']} ↔ {match['entity2_id']}: "
                  f"{match['match_type']} (置信度: {match['match_confidence']:.2f})")
    
    # 8. 获取匹配统计
    print("\n8. 匹配统计信息:")
    stats = matching_engine.get_matching_statistics()
    print(f"  总匹配数: {stats['total_matches']}")
    print(f"  按类型统计: {stats['match_type_counts']}")
    print(f"  按方法统计: {stats['match_method_counts']}")
    print(f"  平均置信度: {stats['average_confidence']:.2f}")
    print(f"  最近24小时匹配数: {stats['recent_matches_24h']}")


if __name__ == "__main__":
    demonstrate_matching_capabilities()