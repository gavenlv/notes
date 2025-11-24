#!/usr/bin/env python3
"""
数据目录工具
提供数据资产发现、搜索、浏览和管理功能
"""

import os
import json
import sqlite3
import datetime
import re
import hashlib
import logging
import math
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DataAsset:
    """数据资产数据类"""
    id: str
    name: str
    description: str
    type: str
    format: str
    location: str
    owner: str
    steward: str
    tags: List[str]
    classification: str
    sensitivity: str
    quality_score: float
    usage_stats: Dict[str, Any]
    lineage: Dict[str, Any]
    schema: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    last_accessed: Optional[datetime.datetime] = None
    certified: bool = False
    retention_policy: str = ""
    access_requirements: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataAsset':
        """从字典创建实例"""
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
        if data['last_accessed']:
            data['last_accessed'] = datetime.datetime.fromisoformat(data['last_accessed'])
        return cls(**data)

class DataCatalogRepository:
    """数据目录存储库"""
    
    def __init__(self, db_path: str = "data_catalog.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    format TEXT,
                    location TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    steward TEXT,
                    tags TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    sensitivity TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    usage_stats TEXT NOT NULL,
                    lineage TEXT NOT NULL,
                    schema TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed TEXT,
                    certified BOOLEAN NOT NULL,
                    retention_policy TEXT,
                    access_requirements TEXT
                )
            """)
            
            # 创建全文搜索表
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS data_assets_fts USING fts5(
                    name, description, tags, owner, 
                    content='data_assets',
                    content_rowid='id'
                )
            """)
            
            # 创建触发器，在主表更新时同步到FTS表
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS data_assets_fts_insert AFTER INSERT ON data_assets BEGIN
                    INSERT INTO data_assets_fts(rowid, name, description, tags, owner)
                    VALUES (new.id, new.name, new.description, new.tags, new.owner);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS data_assets_fts_delete AFTER DELETE ON data_assets BEGIN
                    DELETE FROM data_assets_fts WHERE rowid = old.id;
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS data_assets_fts_update AFTER UPDATE ON data_assets BEGIN
                    DELETE FROM data_assets_fts WHERE rowid = old.id;
                    INSERT INTO data_assets_fts(rowid, name, description, tags, owner)
                    VALUES (new.id, new.name, new.description, new.tags, new.owner);
                END
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_data_assets_name ON data_assets (name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_data_assets_type ON data_assets (type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_data_assets_owner ON data_assets (owner)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_data_assets_classification ON data_assets (classification)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_data_assets_quality ON data_assets (quality_score)")
            
            conn.commit()
    
    def save_asset(self, asset: DataAsset) -> str:
        """保存数据资产"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO data_assets
                (id, name, description, type, format, location, owner, steward, tags,
                 classification, sensitivity, quality_score, usage_stats, lineage,
                 schema, created_at, updated_at, last_accessed, certified,
                 retention_policy, access_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset.id, asset.name, asset.description, asset.type, asset.format,
                asset.location, asset.owner, asset.steward, json.dumps(asset.tags),
                asset.classification, asset.sensitivity, asset.quality_score,
                json.dumps(asset.usage_stats), json.dumps(asset.lineage),
                json.dumps(asset.schema), asset.created_at.isoformat(),
                asset.updated_at.isoformat(),
                asset.last_accessed.isoformat() if asset.last_accessed else None,
                asset.certified, asset.retention_policy,
                json.dumps(asset.access_requirements) if asset.access_requirements else None
            ))
            conn.commit()
        
        return asset.id
    
    def get_asset_by_id(self, asset_id: str) -> Optional[DataAsset]:
        """根据ID获取数据资产"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM data_assets WHERE id = ?", (asset_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['tags'] = json.loads(data['tags'])
                data['usage_stats'] = json.loads(data['usage_stats'])
                data['lineage'] = json.loads(data['lineage'])
                data['schema'] = json.loads(data['schema'])
                if data['access_requirements']:
                    data['access_requirements'] = json.loads(data['access_requirements'])
                return DataAsset.from_dict(data)
            return None
    
    def search_assets(self, query: str = "", filters: Dict[str, Any] = None,
                     sort_by: str = "updated_at", sort_order: str = "DESC",
                     limit: int = 20, offset: int = 0) -> List[DataAsset]:
        """搜索数据资产"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 构建基本查询
            if query:
                # 使用FTS进行全文搜索
                sql = """
                    SELECT da.* FROM data_assets da
                    JOIN data_assets_fts fts ON da.id = fts.rowid
                    WHERE data_assets_fts MATCH ?
                """
                params = [query]
            else:
                sql = "SELECT * FROM data_assets WHERE 1=1"
                params = []
            
            # 添加过滤器
            if filters:
                if 'type' in filters and filters['type']:
                    sql += " AND type = ?"
                    params.append(filters['type'])
                
                if 'format' in filters and filters['format']:
                    sql += " AND format = ?"
                    params.append(filters['format'])
                
                if 'owner' in filters and filters['owner']:
                    sql += " AND owner = ?"
                    params.append(filters['owner'])
                
                if 'steward' in filters and filters['steward']:
                    sql += " AND steward = ?"
                    params.append(filters['steward'])
                
                if 'classification' in filters and filters['classification']:
                    sql += " AND classification = ?"
                    params.append(filters['classification'])
                
                if 'sensitivity' in filters and filters['sensitivity']:
                    sql += " AND sensitivity = ?"
                    params.append(filters['sensitivity'])
                
                if 'tags' in filters and filters['tags']:
                    for tag in filters['tags']:
                        sql += " AND tags LIKE ?"
                        params.append(f"%{tag}%")
                
                if 'certified' in filters:
                    sql += " AND certified = ?"
                    params.append(1 if filters['certified'] else 0)
                
                if 'min_quality_score' in filters:
                    sql += " AND quality_score >= ?"
                    params.append(filters['min_quality_score'])
                
                if 'max_quality_score' in filters:
                    sql += " AND quality_score <= ?"
                    params.append(filters['max_quality_score'])
                
                if 'created_after' in filters:
                    sql += " AND created_at >= ?"
                    params.append(filters['created_after'])
                
                if 'created_before' in filters:
                    sql += " AND created_at <= ?"
                    params.append(filters['created_before'])
            
            # 排序
            valid_sort_fields = ['name', 'type', 'owner', 'created_at', 'updated_at', 'last_accessed', 'quality_score']
            if sort_by in valid_sort_fields:
                sql += f" ORDER BY {sort_by} {sort_order}"
            else:
                sql += " ORDER BY updated_at DESC"
            
            # 分页
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            assets = []
            for row in rows:
                data = dict(row)
                data['tags'] = json.loads(data['tags'])
                data['usage_stats'] = json.loads(data['usage_stats'])
                data['lineage'] = json.loads(data['lineage'])
                data['schema'] = json.loads(data['schema'])
                if data['access_requirements']:
                    data['access_requirements'] = json.loads(data['access_requirements'])
                assets.append(DataAsset.from_dict(data))
            
            return assets
    
    def get_count(self, query: str = "", filters: Dict[str, Any] = None) -> int:
        """获取搜索结果总数"""
        with sqlite3.connect(self.db_path) as conn:
            # 构建基本查询
            if query:
                sql = """
                    SELECT COUNT(*) FROM data_assets da
                    JOIN data_assets_fts fts ON da.id = fts.rowid
                    WHERE data_assets_fts MATCH ?
                """
                params = [query]
            else:
                sql = "SELECT COUNT(*) FROM data_assets WHERE 1=1"
                params = []
            
            # 添加过滤器（与search_assets相同的逻辑）
            if filters:
                if 'type' in filters and filters['type']:
                    sql += " AND type = ?"
                    params.append(filters['type'])
                
                if 'format' in filters and filters['format']:
                    sql += " AND format = ?"
                    params.append(filters['format'])
                
                if 'owner' in filters and filters['owner']:
                    sql += " AND owner = ?"
                    params.append(filters['owner'])
                
                if 'steward' in filters and filters['steward']:
                    sql += " AND steward = ?"
                    params.append(filters['steward'])
                
                if 'classification' in filters and filters['classification']:
                    sql += " AND classification = ?"
                    params.append(filters['classification'])
                
                if 'sensitivity' in filters and filters['sensitivity']:
                    sql += " AND sensitivity = ?"
                    params.append(filters['sensitivity'])
                
                if 'tags' in filters and filters['tags']:
                    for tag in filters['tags']:
                        sql += " AND tags LIKE ?"
                        params.append(f"%{tag}%")
                
                if 'certified' in filters:
                    sql += " AND certified = ?"
                    params.append(1 if filters['certified'] else 0)
                
                if 'min_quality_score' in filters:
                    sql += " AND quality_score >= ?"
                    params.append(filters['min_quality_score'])
                
                if 'max_quality_score' in filters:
                    sql += " AND quality_score <= ?"
                    params.append(filters['max_quality_score'])
            
            cursor = conn.execute(sql, params)
            return cursor.fetchone()[0]
    
    def get_popular_assets(self, limit: int = 10) -> List[DataAsset]:
        """获取热门数据资产"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 使用usage_stats中的访问次数排序
            cursor = conn.execute("""
                SELECT * FROM data_assets 
                WHERE json_extract(usage_stats, '$.access_count') > 0
                ORDER BY json_extract(usage_stats, '$.access_count') DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            assets = []
            for row in rows:
                data = dict(row)
                data['tags'] = json.loads(data['tags'])
                data['usage_stats'] = json.loads(data['usage_stats'])
                data['lineage'] = json.loads(data['lineage'])
                data['schema'] = json.loads(data['schema'])
                if data['access_requirements']:
                    data['access_requirements'] = json.loads(data['access_requirements'])
                assets.append(DataAsset.from_dict(data))
            
            return assets
    
    def get_recent_assets(self, limit: int = 10) -> List[DataAsset]:
        """获取最近添加或更新的数据资产"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM data_assets 
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            assets = []
            for row in rows:
                data = dict(row)
                data['tags'] = json.loads(data['tags'])
                data['usage_stats'] = json.loads(data['usage_stats'])
                data['lineage'] = json.loads(data['lineage'])
                data['schema'] = json.loads(data['schema'])
                if data['access_requirements']:
                    data['access_requirements'] = json.loads(data['access_requirements'])
                assets.append(DataAsset.from_dict(data))
            
            return assets
    
    def get_related_assets(self, asset_id: str) -> List[DataAsset]:
        """获取相关数据资产"""
        asset = self.get_asset_by_id(asset_id)
        if not asset:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 基于标签和相关实体查找相关资产
            related_assets = []
            
            # 查找具有相同标签的资产
            if asset.tags:
                tag_query = " OR ".join(["tags LIKE ?" for _ in asset.tags])
                tag_params = [f"%{tag}%" for tag in asset.tags]
                
                cursor = conn.execute(f"""
                    SELECT * FROM data_assets 
                    WHERE id != ? AND ({tag_query})
                    LIMIT 20
                """, [asset_id] + tag_params)
                
                rows = cursor.fetchall()
                for row in rows:
                    data = dict(row)
                    data['tags'] = json.loads(data['tags'])
                    data['usage_stats'] = json.loads(data['usage_stats'])
                    data['lineage'] = json.loads(data['lineage'])
                    data['schema'] = json.loads(data['schema'])
                    if data['access_requirements']:
                        data['access_requirements'] = json.loads(data['access_requirements'])
                    related_assets.append(DataAsset.from_dict(data))
            
            # 查找具有相同类型的资产
            cursor = conn.execute("""
                SELECT * FROM data_assets 
                WHERE id != ? AND type = ?
                LIMIT 20
            """, (asset_id, asset.type))
            
            rows = cursor.fetchall()
            for row in rows:
                data = dict(row)
                data['tags'] = json.loads(data['tags'])
                data['usage_stats'] = json.loads(data['usage_stats'])
                data['lineage'] = json.loads(data['lineage'])
                data['schema'] = json.loads(data['schema'])
                if data['access_requirements']:
                    data['access_requirements'] = json.loads(data['access_requirements'])
                related_assets.append(DataAsset.from_dict(data))
            
            # 去重并返回
            unique_assets = {}
            for asset in related_assets:
                if asset.id not in unique_assets:
                    unique_assets[asset.id] = asset
            
            return list(unique_assets.values())[:10]
    
    def update_access_stats(self, asset_id: str, user: str = "system") -> bool:
        """更新访问统计"""
        asset = self.get_asset_by_id(asset_id)
        if not asset:
            return False
        
        # 更新访问统计
        access_count = asset.usage_stats.get('access_count', 0) + 1
        asset.usage_stats['access_count'] = access_count
        asset.usage_stats['last_access'] = datetime.datetime.now().isoformat()
        
        # 更新最后访问时间
        asset.last_accessed = datetime.datetime.now()
        asset.updated_at = datetime.datetime.now()
        
        # 如果访问次数超过阈值，可以增加流行度
        if access_count > 10:
            if 'popularity' not in asset.usage_stats:
                asset.usage_stats['popularity'] = 0
            asset.usage_stats['popularity'] += 1
        
        self.save_asset(asset)
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取数据目录统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总资产数
            cursor = conn.execute("SELECT COUNT(*) FROM data_assets")
            total_assets = cursor.fetchone()[0]
            
            # 按类型统计
            cursor = conn.execute("""
                SELECT type, COUNT(*) FROM data_assets 
                GROUP BY type
            """)
            type_distribution = dict(cursor.fetchall())
            
            # 按分类统计
            cursor = conn.execute("""
                SELECT classification, COUNT(*) FROM data_assets 
                GROUP BY classification
            """)
            classification_distribution = dict(cursor.fetchall())
            
            # 按敏感度统计
            cursor = conn.execute("""
                SELECT sensitivity, COUNT(*) FROM data_assets 
                GROUP BY sensitivity
            """)
            sensitivity_distribution = dict(cursor.fetchall())
            
            # 按所有者统计
            cursor = conn.execute("""
                SELECT owner, COUNT(*) FROM data_assets 
                GROUP BY owner
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            top_owners = dict(cursor.fetchall())
            
            # 认证资产数
            cursor = conn.execute("SELECT COUNT(*) FROM data_assets WHERE certified = 1")
            certified_assets = cursor.fetchone()[0]
            
            # 平均质量评分
            cursor = conn.execute("SELECT AVG(quality_score) FROM data_assets")
            avg_quality_score = cursor.fetchone()[0] or 0
            
            # 最近7天新增资产
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            cursor = conn.execute("""
                SELECT COUNT(*) FROM data_assets 
                WHERE created_at >= ?
            """, (seven_days_ago,))
            recent_assets = cursor.fetchone()[0]
        
        return {
            'total_assets': total_assets,
            'type_distribution': type_distribution,
            'classification_distribution': classification_distribution,
            'sensitivity_distribution': sensitivity_distribution,
            'top_owners': top_owners,
            'certified_assets': certified_assets,
            'certification_rate': certified_assets / total_assets if total_assets > 0 else 0,
            'average_quality_score': round(avg_quality_score, 2),
            'recent_assets': recent_assets,
            'last_updated': datetime.datetime.now().isoformat()
        }

class DataCatalog:
    """数据目录主类"""
    
    def __init__(self, repo: DataCatalogRepository = None):
        self.repo = repo or DataCatalogRepository()
    
    def register_asset(self, asset_data: Dict[str, Any]) -> str:
        """注册数据资产"""
        # 创建ID
        asset_id = str(uuid.uuid4())
        
        # 设置时间戳
        now = datetime.datetime.now()
        
        # 创建资产对象
        asset = DataAsset(
            id=asset_id,
            name=asset_data.get('name', ''),
            description=asset_data.get('description', ''),
            type=asset_data.get('type', 'unknown'),
            format=asset_data.get('format', ''),
            location=asset_data.get('location', ''),
            owner=asset_data.get('owner', ''),
            steward=asset_data.get('steward', asset_data.get('owner', '')),
            tags=asset_data.get('tags', []),
            classification=asset_data.get('classification', 'internal'),
            sensitivity=asset_data.get('sensitivity', 'internal'),
            quality_score=asset_data.get('quality_score', 0.0),
            usage_stats=asset_data.get('usage_stats', {'access_count': 0}),
            lineage=asset_data.get('lineage', {}),
            schema=asset_data.get('schema', {}),
            created_at=now,
            updated_at=now,
            last_accessed=None,
            certified=asset_data.get('certified', False),
            retention_policy=asset_data.get('retention_policy', ''),
            access_requirements=asset_data.get('access_requirements', [])
        )
        
        # 保存资产
        self.repo.save_asset(asset)
        logger.info(f"注册了数据资产: {asset.name} (ID: {asset.id})")
        
        return asset.id
    
    def search(self, query: str = "", filters: Dict[str, Any] = None,
               page: int = 1, page_size: int = 20, sort_by: str = "updated_at",
               sort_order: str = "DESC") -> Dict[str, Any]:
        """搜索数据资产"""
        offset = (page - 1) * page_size
        
        assets = self.repo.search_assets(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=page_size,
            offset=offset
        )
        
        total = self.repo.get_count(query, filters)
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return {
            'assets': [asset.to_dict() for asset in assets],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages
            }
        }
    
    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """获取数据资产详情"""
        asset = self.repo.get_asset_by_id(asset_id)
        if asset:
            # 更新访问统计
            self.repo.update_access_stats(asset_id)
            return asset.to_dict()
        return None
    
    def update_asset(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """更新数据资产"""
        asset = self.repo.get_asset_by_id(asset_id)
        if not asset:
            return False
        
        # 应用更新
        if 'name' in updates:
            asset.name = updates['name']
        
        if 'description' in updates:
            asset.description = updates['description']
        
        if 'type' in updates:
            asset.type = updates['type']
        
        if 'format' in updates:
            asset.format = updates['format']
        
        if 'location' in updates:
            asset.location = updates['location']
        
        if 'owner' in updates:
            asset.owner = updates['owner']
        
        if 'steward' in updates:
            asset.steward = updates['steward']
        
        if 'tags' in updates:
            asset.tags = updates['tags']
        
        if 'classification' in updates:
            asset.classification = updates['classification']
        
        if 'sensitivity' in updates:
            asset.sensitivity = updates['sensitivity']
        
        if 'quality_score' in updates:
            asset.quality_score = updates['quality_score']
        
        if 'usage_stats' in updates:
            asset.usage_stats = updates['usage_stats']
        
        if 'lineage' in updates:
            asset.lineage = updates['lineage']
        
        if 'schema' in updates:
            asset.schema = updates['schema']
        
        if 'certified' in updates:
            asset.certified = updates['certified']
        
        if 'retention_policy' in updates:
            asset.retention_policy = updates['retention_policy']
        
        if 'access_requirements' in updates:
            asset.access_requirements = updates['access_requirements']
        
        asset.updated_at = datetime.datetime.now()
        
        self.repo.save_asset(asset)
        return True
    
    def get_related_assets(self, asset_id: str) -> List[Dict[str, Any]]:
        """获取相关数据资产"""
        related_assets = self.repo.get_related_assets(asset_id)
        return [asset.to_dict() for asset in related_assets]
    
    def get_popular_assets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门数据资产"""
        popular_assets = self.repo.get_popular_assets(limit)
        return [asset.to_dict() for asset in popular_assets]
    
    def get_recent_assets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近添加或更新的数据资产"""
        recent_assets = self.repo.get_recent_assets(limit)
        return [asset.to_dict() for asset in recent_assets]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        return self.repo.get_statistics()
    
    def certify_asset(self, asset_id: str, certifier: str, notes: str = "") -> bool:
        """认证数据资产"""
        asset = self.repo.get_asset_by_id(asset_id)
        if not asset:
            return False
        
        asset.certified = True
        asset.updated_at = datetime.datetime.now()
        
        if 'certifications' not in asset.usage_stats:
            asset.usage_stats['certifications'] = []
        
        asset.usage_stats['certifications'].append({
            'certifier': certifier,
            'timestamp': datetime.datetime.now().isoformat(),
            'notes': notes
        })
        
        self.repo.save_asset(asset)
        return True
    
    def get_browse_categories(self) -> Dict[str, Any]:
        """获取浏览分类"""
        with sqlite3.connect(self.repo.db_path) as conn:
            # 资产类型
            cursor = conn.execute("SELECT DISTINCT type FROM data_assets ORDER BY type")
            types = [row[0] for row in cursor.fetchall()]
            
            # 分类
            cursor = conn.execute("SELECT DISTINCT classification FROM data_assets ORDER BY classification")
            classifications = [row[0] for row in cursor.fetchall()]
            
            # 敏感度
            cursor = conn.execute("SELECT DISTINCT sensitivity FROM data_assets ORDER BY sensitivity")
            sensitivities = [row[0] for row in cursor.fetchall()]
            
            # 所有者
            cursor = conn.execute("""
                SELECT DISTINCT owner FROM data_assets 
                ORDER BY owner
                LIMIT 50
            """)
            owners = [row[0] for row in cursor.fetchall()]
            
            # 格式
            cursor = conn.execute("SELECT DISTINCT format FROM data_assets WHERE format != '' ORDER BY format")
            formats = [row[0] for row in cursor.fetchall()]
            
            # 标签
            cursor = conn.execute("SELECT tags FROM data_assets")
            all_tags = []
            for row in cursor.fetchall():
                tags = json.loads(row[0])
                all_tags.extend(tags)
            
            # 获取出现频率最高的标签
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:50]
            popular_tags = [tag for tag, _ in popular_tags]
            
            return {
                'types': types,
                'classifications': classifications,
                'sensitivities': sensitivities,
                'owners': owners,
                'formats': formats,
                'popular_tags': popular_tags
            }

def main():
    """主函数，演示数据目录使用"""
    print("=" * 50)
    print("数据目录工具演示")
    print("=" * 50)
    
    # 创建数据目录
    catalog = DataCatalog()
    
    # 1. 注册一些示例数据资产
    print("\n1. 注册示例数据资产...")
    
    assets_data = [
        {
            'name': '客户信息表',
            'description': '包含客户基本信息的表',
            'type': 'table',
            'format': 'postgresql',
            'location': 'postgres://localhost:5432/mydb.public.customers',
            'owner': '数据管理部',
            'steward': '张三',
            'tags': ['客户', '个人信息', '核心业务'],
            'classification': 'internal',
            'sensitivity': 'confidential',
            'quality_score': 0.9,
            'schema': {
                'columns': [
                    {'name': 'id', 'type': 'integer', 'description': '客户ID'},
                    {'name': 'name', 'type': 'varchar', 'description': '客户姓名'},
                    {'name': 'email', 'type': 'varchar', 'description': '客户邮箱'}
                ]
            }
        },
        {
            'name': '销售数据',
            'description': '月度销售数据报表',
            'type': 'file',
            'format': 'csv',
            'location': '/data/sales/monthly_sales_2023.csv',
            'owner': '销售部',
            'tags': ['销售', '报表', '月度'],
            'classification': 'internal',
            'sensitivity': 'internal',
            'quality_score': 0.8,
            'schema': {
                'columns': [
                    {'name': 'month', 'type': 'date', 'description': '月份'},
                    {'name': 'product', 'type': 'varchar', 'description': '产品名称'},
                    {'name': 'sales', 'type': 'decimal', 'description': '销售额'}
                ]
            }
        },
        {
            'name': '用户行为日志',
            'description': '用户在平台上的行为日志数据',
            'type': 'table',
            'format': 'hive',
            'location': 'hive://data_lake.user_behavior_logs',
            'owner': '数据科学团队',
            'tags': ['用户行为', '日志', '大数据'],
            'classification': 'internal',
            'sensitivity': 'internal',
            'quality_score': 0.75,
            'schema': {
                'columns': [
                    {'name': 'user_id', 'type': 'string', 'description': '用户ID'},
                    {'name': 'action', 'type': 'string', 'description': '行为类型'},
                    {'name': 'timestamp', 'type': 'timestamp', 'description': '行为时间'}
                ]
            }
        }
    ]
    
    asset_ids = []
    for asset_data in assets_data:
        asset_id = catalog.register_asset(asset_data)
        asset_ids.append(asset_id)
        print(f"- 注册了: {asset_data['name']} (ID: {asset_id})")
    
    # 2. 搜索数据资产
    print("\n2. 搜索数据资产...")
    search_results = catalog.search("客户")
    print(f"搜索 '客户' 的结果: {len(search_results['assets'])} 个资产")
    for asset in search_results['assets']:
        print(f"- {asset['name']} ({asset['type']})")
    
    # 3. 获取资产详情
    if asset_ids:
        print("\n3. 获取资产详情...")
        asset = catalog.get_asset(asset_ids[0])
        if asset:
            print(f"资产名称: {asset['name']}")
            print(f"描述: {asset['description']}")
            print(f"所有者: {asset['owner']}")
            print(f"标签: {', '.join(asset['tags'])}")
            print(f"质量评分: {asset['quality_score']}")
    
    # 4. 获取相关资产
    if asset_ids:
        print("\n4. 获取相关资产...")
        related_assets = catalog.get_related_assets(asset_ids[0])
        print(f"相关资产数量: {len(related_assets)}")
        for asset in related_assets:
            print(f"- {asset['name']} ({asset['type']})")
    
    # 5. 获取热门资产
    print("\n5. 获取热门资产...")
    # 更新一些访问次数以模拟热门资产
    for i, asset_id in enumerate(asset_ids):
        for _ in range(i+1):
            catalog.repo.update_access_stats(asset_id)
    
    popular_assets = catalog.get_popular_assets(3)
    print("热门资产:")
    for asset in popular_assets:
        print(f"- {asset['name']} (访问次数: {asset['usage_stats'].get('access_count', 0)})")
    
    # 6. 获取最近资产
    print("\n6. 获取最近资产...")
    recent_assets = catalog.get_recent_assets(3)
    print("最近资产:")
    for asset in recent_assets:
        print(f"- {asset['name']} (更新时间: {asset['updated_at'][:10]})")
    
    # 7. 认证资产
    if asset_ids:
        print("\n7. 认证资产...")
        success = catalog.certify_asset(asset_ids[0], "数据治理专员", "数据质量检查通过")
        print(f"认证{'成功' if success else '失败'}")
        
        # 获取更新后的资产
        asset = catalog.get_asset(asset_ids[0])
        if asset:
            print(f"认证状态: {'已认证' if asset['certified'] else '未认证'}")
    
    # 8. 获取浏览分类
    print("\n8. 获取浏览分类...")
    categories = catalog.get_browse_categories()
    print(f"资产类型: {', '.join(categories['types'])}")
    print(f"分类: {', '.join(categories['classifications'])}")
    print(f"敏感度: {', '.join(categories['sensitivities'])}")
    print(f"热门标签: {', '.join(categories['popular_tags'][:5])}")
    
    # 9. 获取仪表板统计
    print("\n9. 获取仪表板统计...")
    stats = catalog.get_dashboard_stats()
    print(f"总资产数: {stats['total_assets']}")
    print(f"类型分布: {stats['type_distribution']}")
    print(f"分类分布: {stats['classification_distribution']}")
    print(f"认证资产数: {stats['certified_assets']}")
    print(f"认证率: {stats['certification_rate']:.2%}")
    print(f"平均质量评分: {stats['average_quality_score']}")
    print(f"最近7天新增: {stats['recent_assets']}")
    
    # 10. 高级搜索
    print("\n10. 高级搜索...")
    filters = {
        'type': 'table',
        'classification': 'internal',
        'min_quality_score': 0.8
    }
    
    advanced_results = catalog.search(filters=filters)
    print(f"高级搜索结果: {len(advanced_results['assets'])} 个资产")
    for asset in advanced_results['assets']:
        print(f"- {asset['name']} (类型: {asset['type']}, 评分: {asset['quality_score']})")

if __name__ == "__main__":
    main()