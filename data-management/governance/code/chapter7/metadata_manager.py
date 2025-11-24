#!/usr/bin/env python3
"""
元数据管理器
提供完整的元数据采集、存储、查询和管理功能
"""

import os
import json
import sqlite3
import datetime
import re
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetadataType(Enum):
    """元数据类型枚举"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"

class DataSourceType(Enum):
    """数据源类型枚举"""
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    API = "api"
    STREAM = "stream"
    MANUAL = "manual"

@dataclass
class MetadataEntity:
    """元数据实体数据类"""
    id: str
    name: str
    type: MetadataType
    source_type: DataSourceType
    source: str
    attributes: Dict[str, Any]
    relationships: List[Dict[str, str]]
    tags: List[str]
    owner: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    version: int = 1
    description: str = ""
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        data['source_type'] = self.source_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataEntity':
        """从字典创建实例"""
        data['type'] = MetadataType(data['type'])
        data['source_type'] = DataSourceType(data['source_type'])
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class MetadataConnector(ABC):
    """元数据连接器抽象基类"""
    
    @abstractmethod
    def extract(self, source_config: Dict[str, Any]) -> List[MetadataEntity]:
        """提取元数据"""
        pass

class DatabaseConnector(MetadataConnector):
    """数据库连接器"""
    
    def extract(self, source_config: Dict[str, Any]) -> List[MetadataEntity]:
        """从数据库提取元数据"""
        db_type = source_config.get('db_type', 'postgresql')
        connection_string = source_config.get('connection_string')
        schema_name = source_config.get('schema_name', 'public')
        
        logger.info(f"从数据库提取元数据: {db_type}")
        
        # 模拟数据库元数据提取
        entities = []
        
        # 模拟表元数据
        tables = [
            {
                'name': 'customers',
                'columns': [
                    {'name': 'id', 'type': 'integer', 'nullable': False},
                    {'name': 'name', 'type': 'varchar', 'nullable': False},
                    {'name': 'email', 'type': 'varchar', 'nullable': True},
                    {'name': 'created_at', 'type': 'timestamp', 'nullable': False}
                ],
                'row_count': 15000
            },
            {
                'name': 'orders',
                'columns': [
                    {'name': 'id', 'type': 'integer', 'nullable': False},
                    {'name': 'customer_id', 'type': 'integer', 'nullable': False},
                    {'name': 'order_date', 'type': 'date', 'nullable': False},
                    {'name': 'total', 'type': 'decimal', 'nullable': False}
                ],
                'row_count': 50000
            }
        ]
        
        for table in tables:
            table_id = str(uuid.uuid4())
            
            attributes = {
                'schema': schema_name,
                'columns': table['columns'],
                'row_count': table['row_count'],
                'estimated_size': table['row_count'] * 1024,  # 假设每行1KB
                'primary_key': 'id'
            }
            
            relationships = [
                {
                    'type': 'has_columns',
                    'target': f"{table['name']}_columns",
                    'description': f"Table {table['name']} has columns"
                }
            ]
            
            if table['name'] == 'orders':
                relationships.append({
                    'type': 'foreign_key',
                    'target': 'customers',
                    'target_field': 'id',
                    'source_field': 'customer_id',
                    'description': 'Orders.customer_id references Customers.id'
                })
            
            tags = ['table', 'database', schema_name]
            if 'id' in [col['name'] for col in table['columns']]:
                tags.append('has_primary_key')
            
            entity = MetadataEntity(
                id=table_id,
                name=table['name'],
                type=MetadataType.TECHNICAL,
                source_type=DataSourceType.DATABASE,
                source=connection_string,
                attributes=attributes,
                relationships=relationships,
                tags=tags,
                owner="database_admin",
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                description=f"Table {table['name']} in schema {schema_name}",
                quality_score=0.85
            )
            
            entities.append(entity)
        
        # 模拟列元数据
        for table in tables:
            for column in table['columns']:
                column_id = str(uuid.uuid4())
                
                attributes = {
                    'table': table['name'],
                    'schema': schema_name,
                    'data_type': column['type'],
                    'nullable': column['nullable'],
                    'unique_values': None,  # 实际环境中可以通过查询获取
                    'null_count': None,      # 实际环境中可以通过查询获取
                    'distinct_count': None   # 实际环境中可以通过查询获取
                }
                
                relationships = [
                    {
                        'type': 'belongs_to',
                        'target': table['name'],
                        'description': f"Column {column['name']} belongs to table {table['name']}"
                    }
                ]
                
                tags = ['column', 'database', schema_name, column['type'].lower()]
                
                entity = MetadataEntity(
                    id=column_id,
                    name=f"{table['name']}.{column['name']}",
                    type=MetadataType.TECHNICAL,
                    source_type=DataSourceType.DATABASE,
                    source=connection_string,
                    attributes=attributes,
                    relationships=relationships,
                    tags=tags,
                    owner="database_admin",
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                    description=f"Column {column['name']} in table {table['name']}",
                    quality_score=0.9
                )
                
                entities.append(entity)
        
        return entities

class FileSystemConnector(MetadataConnector):
    """文件系统连接器"""
    
    def extract(self, source_config: Dict[str, Any]) -> List[MetadataEntity]:
        """从文件系统提取元数据"""
        directory = source_config.get('directory')
        file_patterns = source_config.get('file_patterns', ['*.csv', '*.json', '*.parquet'])
        recursive = source_config.get('recursive', True)
        
        logger.info(f"从文件系统提取元数据: {directory}")
        
        # 模拟文件系统元数据提取
        entities = []
        
        # 模拟文件
        files = [
            {
                'name': 'customer_data.csv',
                'path': os.path.join(directory, 'customer_data.csv'),
                'size': 2048576,  # 2MB
                'format': 'csv',
                'encoding': 'utf-8',
                'created': datetime.datetime(2023, 1, 15),
                'modified': datetime.datetime(2023, 5, 20),
                'columns': [
                    {'name': 'customer_id', 'type': 'integer'},
                    {'name': 'name', 'type': 'string'},
                    {'name': 'email', 'type': 'string'},
                    {'name': 'address', 'type': 'string'}
                ],
                'row_count': 15000
            },
            {
                'name': 'sales_data.parquet',
                'path': os.path.join(directory, 'sales_data.parquet'),
                'size': 5242880,  # 5MB
                'format': 'parquet',
                'compression': 'snappy',
                'created': datetime.datetime(2023, 2, 10),
                'modified': datetime.datetime(2023, 6, 5),
                'columns': [
                    {'name': 'order_id', 'type': 'integer'},
                    {'name': 'customer_id', 'type': 'integer'},
                    {'name': 'product_id', 'type': 'integer'},
                    {'name': 'quantity', 'type': 'integer'},
                    {'name': 'price', 'type': 'decimal'},
                    {'name': 'order_date', 'type': 'date'}
                ],
                'row_count': 50000
            }
        ]
        
        for file in files:
            file_id = str(uuid.uuid4())
            
            attributes = {
                'path': file['path'],
                'size': file['size'],
                'format': file['format'],
                'encoding': file.get('encoding'),
                'compression': file.get('compression'),
                'created': file['created'].isoformat(),
                'modified': file['modified'].isoformat(),
                'columns': file['columns'],
                'row_count': file['row_count'],
                'estimated_size': file['size']
            }
            
            relationships = []
            
            tags = ['file', file['format'], 'data']
            
            entity = MetadataEntity(
                id=file_id,
                name=file['name'],
                type=MetadataType.TECHNICAL,
                source_type=DataSourceType.FILE_SYSTEM,
                source=directory,
                attributes=attributes,
                relationships=relationships,
                tags=tags,
                owner="data_engineer",
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                description=f"Data file: {file['name']} in {file['format']} format",
                quality_score=0.8
            )
            
            entities.append(entity)
        
        return entities

class MetadataRepository:
    """元数据存储库"""
    
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata_entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    attributes TEXT NOT NULL,
                    relationships TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    description TEXT,
                    quality_score REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata_history (
                    id TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    changes TEXT NOT NULL,
                    user TEXT NOT NULL,
                    PRIMARY KEY (id, entity_id),
                    FOREIGN KEY (entity_id) REFERENCES metadata_entities (id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_entities_name ON metadata_entities (name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_entities_type ON metadata_entities (type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metadata_entities_source ON metadata_entities (source)
            """)
            
            conn.commit()
    
    def save_entity(self, entity: MetadataEntity, user: str = "system") -> str:
        """保存元数据实体"""
        existing = self.get_entity_by_id(entity.id)
        
        with sqlite3.connect(self.db_path) as conn:
            if existing:
                # 更新现有实体
                old_data = json.dumps(existing.to_dict())
                
                # 更新实体
                entity.updated_at = datetime.datetime.now()
                entity.version += 1
                
                conn.execute("""
                    UPDATE metadata_entities 
                    SET name=?, type=?, source_type=?, source=?, attributes=?, 
                        relationships=?, tags=?, owner=?, updated_at=?, version=?, 
                        description=?, quality_score=?
                    WHERE id=?
                """, (
                    entity.name, entity.type.value, entity.source_type.value, entity.source,
                    json.dumps(entity.attributes), json.dumps(entity.relationships),
                    json.dumps(entity.tags), entity.owner, entity.updated_at.isoformat(),
                    entity.version, entity.description, entity.quality_score, entity.id
                ))
                
                # 记录历史
                new_data = json.dumps(entity.to_dict())
                history_id = str(uuid.uuid4())
                
                conn.execute("""
                    INSERT INTO metadata_history (id, entity_id, operation, timestamp, changes, user)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    history_id, entity.id, "update", datetime.datetime.now().isoformat(),
                    json.dumps({"old": old_data, "new": new_data}), user
                ))
                
            else:
                # 插入新实体
                conn.execute("""
                    INSERT INTO metadata_entities 
                    (id, name, type, source_type, source, attributes, relationships, 
                     tags, owner, created_at, updated_at, version, description, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.id, entity.name, entity.type.value, entity.source_type.value,
                    entity.source, json.dumps(entity.attributes),
                    json.dumps(entity.relationships), json.dumps(entity.tags),
                    entity.owner, entity.created_at.isoformat(), entity.updated_at.isoformat(),
                    entity.version, entity.description, entity.quality_score
                ))
                
                # 记录历史
                history_id = str(uuid.uuid4())
                new_data = json.dumps(entity.to_dict())
                
                conn.execute("""
                    INSERT INTO metadata_history (id, entity_id, operation, timestamp, changes, user)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    history_id, entity.id, "create", datetime.datetime.now().isoformat(),
                    json.dumps({"new": new_data}), user
                ))
            
            conn.commit()
        
        return entity.id
    
    def get_entity_by_id(self, entity_id: str) -> Optional[MetadataEntity]:
        """根据ID获取元数据实体"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM metadata_entities WHERE id = ?
            """, (entity_id,))
            
            row = cursor.fetchone()
            if row:
                return MetadataEntity.from_dict(dict(row))
            return None
    
    def search_entities(self, query: str, filters: Dict[str, Any] = None, 
                       limit: int = 100, offset: int = 0) -> List[MetadataEntity]:
        """搜索元数据实体"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 构建查询
            sql = "SELECT * FROM metadata_entities WHERE 1=1"
            params = []
            
            # 添加查询条件
            if query:
                sql += " AND (name LIKE ? OR description LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            # 添加过滤器
            if filters:
                if 'type' in filters:
                    sql += " AND type = ?"
                    params.append(filters['type'])
                
                if 'source_type' in filters:
                    sql += " AND source_type = ?"
                    params.append(filters['source_type'])
                
                if 'source' in filters:
                    sql += " AND source LIKE ?"
                    params.append(f"%{filters['source']}%")
                
                if 'owner' in filters:
                    sql += " AND owner = ?"
                    params.append(filters['owner'])
                
                if 'tags' in filters:
                    for tag in filters['tags']:
                        sql += " AND tags LIKE ?"
                        params.append(f"%{tag}%")
                
                if 'min_quality_score' in filters:
                    sql += " AND quality_score >= ?"
                    params.append(filters['min_quality_score'])
            
            # 排序和分页
            sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            return [MetadataEntity.from_dict(dict(row)) for row in rows]
    
    def get_related_entities(self, entity_id: str) -> Dict[str, List[MetadataEntity]]:
        """获取相关实体"""
        entity = self.get_entity_by_id(entity_id)
        if not entity:
            return {}
        
        related = {}
        
        # 通过关系获取相关实体
        for relationship in entity.relationships:
            target_name = relationship.get('target')
            if target_name:
                related_entities = self.search_entities(target_name, limit=50)
                if related_entities:
                    related[relationship['type']] = related_entities
        
        return related
    
    def get_entity_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """获取实体历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM metadata_history 
                WHERE entity_id = ? 
                ORDER BY timestamp DESC
            """, (entity_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def delete_entity(self, entity_id: str, user: str = "system") -> bool:
        """删除元数据实体"""
        entity = self.get_entity_by_id(entity_id)
        if not entity:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            # 记录删除历史
            history_id = str(uuid.uuid4())
            old_data = json.dumps(entity.to_dict())
            
            conn.execute("""
                INSERT INTO metadata_history (id, entity_id, operation, timestamp, changes, user)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                history_id, entity_id, "delete", datetime.datetime.now().isoformat(),
                json.dumps({"old": old_data}), user
            ))
            
            # 删除实体
            conn.execute("DELETE FROM metadata_entities WHERE id = ?", (entity_id,))
            
            conn.commit()
        
        return True

class MetadataManager:
    """元数据管理器主类"""
    
    def __init__(self, repo: MetadataRepository = None):
        self.repo = repo or MetadataRepository()
        self.connectors = {
            DataSourceType.DATABASE: DatabaseConnector(),
            DataSourceType.FILE_SYSTEM: FileSystemConnector(),
        }
    
    def register_connector(self, source_type: DataSourceType, connector: MetadataConnector):
        """注册连接器"""
        self.connectors[source_type] = connector
        logger.info(f"注册了 {source_type.value} 连接器")
    
    def collect_metadata(self, source_config: Dict[str, Any], user: str = "system") -> int:
        """从数据源采集元数据"""
        source_type_str = source_config.get('type')
        if not source_type_str:
            raise ValueError("源配置中缺少类型信息")
        
        try:
            source_type = DataSourceType(source_type_str)
        except ValueError:
            raise ValueError(f"不支持的数据源类型: {source_type_str}")
        
        connector = self.connectors.get(source_type)
        if not connector:
            raise ValueError(f"没有注册 {source_type.value} 类型的连接器")
        
        # 提取元数据
        entities = connector.extract(source_config)
        logger.info(f"从 {source_type.value} 提取了 {len(entities)} 个元数据实体")
        
        # 保存元数据
        count = 0
        for entity in entities:
            # 检查是否已存在
            existing = self.repo.get_entity_by_id(entity.id)
            if existing:
                # 更新现有实体
                entity.version = existing.version
                entity.created_at = existing.created_at
            
            self.repo.save_entity(entity, user)
            count += 1
        
        logger.info(f"成功保存了 {count} 个元数据实体")
        return count
    
    def search_metadata(self, query: str, filters: Dict[str, Any] = None, 
                       limit: int = 100, offset: int = 0) -> List[MetadataEntity]:
        """搜索元数据"""
        return self.repo.search_entities(query, filters, limit, offset)
    
    def get_metadata_detail(self, entity_id: str) -> Tuple[Optional[MetadataEntity], Dict[str, List[MetadataEntity]], List[Dict[str, Any]]]:
        """获取元数据详情，包括相关实体和历史"""
        entity = self.repo.get_entity_by_id(entity_id)
        if not entity:
            return None, {}, []
        
        related_entities = self.repo.get_related_entities(entity_id)
        history = self.repo.get_entity_history(entity_id)
        
        return entity, related_entities, history
    
    def update_metadata(self, entity_id: str, updates: Dict[str, Any], user: str = "system") -> bool:
        """更新元数据"""
        entity = self.repo.get_entity_by_id(entity_id)
        if not entity:
            return False
        
        # 应用更新
        if 'name' in updates:
            entity.name = updates['name']
        
        if 'description' in updates:
            entity.description = updates['description']
        
        if 'owner' in updates:
            entity.owner = updates['owner']
        
        if 'tags' in updates:
            entity.tags = updates['tags']
        
        if 'attributes' in updates:
            entity.attributes = updates['attributes']
        
        if 'relationships' in updates:
            entity.relationships = updates['relationships']
        
        if 'quality_score' in updates:
            entity.quality_score = updates['quality_score']
        
        # 保存更新
        self.repo.save_entity(entity, user)
        return True
    
    def delete_metadata(self, entity_id: str, user: str = "system") -> bool:
        """删除元数据"""
        return self.repo.delete_entity(entity_id, user)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取元数据统计信息"""
        # 获取所有实体的基本统计
        all_entities = self.repo.search_entities("", limit=10000)
        
        # 按类型统计
        type_counts = {}
        for entity in all_entities:
            type_name = entity.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # 按源类型统计
        source_type_counts = {}
        for entity in all_entities:
            source_type_name = entity.source_type.value
            source_type_counts[source_type_name] = source_type_counts.get(source_type_name, 0) + 1
        
        # 质量评分统计
        quality_scores = [entity.quality_score for entity in all_entities if entity.quality_score > 0]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 最新的10个实体
        recent_entities = sorted(all_entities, key=lambda x: x.updated_at, reverse=True)[:10]
        
        return {
            'total_entities': len(all_entities),
            'type_distribution': type_counts,
            'source_type_distribution': source_type_counts,
            'average_quality_score': avg_quality_score,
            'recent_entities': [entity.name for entity in recent_entities],
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def export_metadata(self, format: str = "json", filters: Dict[str, Any] = None) -> str:
        """导出元数据"""
        entities = self.repo.search_entities("", filters, limit=10000)
        
        if format.lower() == "json":
            return json.dumps([entity.to_dict() for entity in entities], indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def import_metadata(self, data: str, format: str = "json", user: str = "system", overwrite: bool = False) -> int:
        """导入元数据"""
        if format.lower() != "json":
            raise ValueError(f"不支持的导入格式: {format}")
        
        try:
            entities_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {str(e)}")
        
        count = 0
        for entity_data in entities_data:
            entity = MetadataEntity.from_dict(entity_data)
            existing = self.repo.get_entity_by_id(entity.id)
            
            if existing and not overwrite:
                continue
            
            if existing:
                entity.version = existing.version
                entity.created_at = existing.created_at
            
            self.repo.save_entity(entity, user)
            count += 1
        
        return count

def main():
    """主函数，演示元数据管理器使用"""
    print("=" * 50)
    print("元数据管理器演示")
    print("=" * 50)
    
    # 创建元数据管理器
    manager = MetadataManager()
    
    # 1. 采集数据库元数据
    print("\n1. 采集数据库元数据...")
    db_config = {
        'type': 'database',
        'db_type': 'postgresql',
        'connection_string': 'postgresql://user:pass@localhost:5432/mydb',
        'schema_name': 'public'
    }
    
    db_count = manager.collect_metadata(db_config, user="admin")
    print(f"从数据库采集了 {db_count} 个元数据实体")
    
    # 2. 采集文件系统元数据
    print("\n2. 采集文件系统元数据...")
    fs_config = {
        'type': 'file_system',
        'directory': '/data/files',
        'file_patterns': ['*.csv', '*.json', '*.parquet'],
        'recursive': True
    }
    
    fs_count = manager.collect_metadata(fs_config, user="admin")
    print(f"从文件系统采集了 {fs_count} 个元数据实体")
    
    # 3. 搜索元数据
    print("\n3. 搜索元数据...")
    customers = manager.search_metadata("customer", limit=5)
    for entity in customers:
        print(f"- {entity.name} ({entity.type.value}, 质量评分: {entity.quality_score})")
    
    # 4. 获取元数据详情
    if customers:
        print("\n4. 获取元数据详情...")
        entity, related, history = manager.get_metadata_detail(customers[0].id)
        print(f"实体: {entity.name}")
        print(f"描述: {entity.description}")
        print(f"属性: {len(entity.attributes)} 个")
        print(f"关系: {len(entity.relationships)} 个")
        print(f"标签: {', '.join(entity.tags)}")
        print(f"相关实体: {len(related)} 类")
        print(f"历史记录: {len(history)} 条")
    
    # 5. 更新元数据
    print("\n5. 更新元数据...")
    if customers:
        updates = {
            'description': 'Updated description for customer data',
            'tags': ['customer', 'important', 'pii'],
            'quality_score': 0.9
        }
        success = manager.update_metadata(customers[0].id, updates, user="data_steward")
        print(f"更新{'成功' if success else '失败'}")
    
    # 6. 获取统计信息
    print("\n6. 获取统计信息...")
    stats = manager.get_statistics()
    print(f"总实体数: {stats['total_entities']}")
    print(f"类型分布: {stats['type_distribution']}")
    print(f"源类型分布: {stats['source_type_distribution']}")
    print(f"平均质量评分: {stats['average_quality_score']:.2f}")
    print(f"最近更新: {stats['last_updated']}")
    
    # 7. 导出元数据
    print("\n7. 导出元数据...")
    exported_data = manager.export_metadata("json", {"type": "technical"})
    print(f"导出了 {len(exported_data)} 字符的元数据")
    
    # 8. 导入元数据
    print("\n8. 导入元数据...")
    imported_count = manager.import_metadata(exported_data, "json", user="admin", overwrite=True)
    print(f"导入了 {imported_count} 个元数据实体")

if __name__ == "__main__":
    main()