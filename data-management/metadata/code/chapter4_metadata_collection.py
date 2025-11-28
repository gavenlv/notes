"""
第4章：元数据收集与提取 - 配套代码示例
本文件包含第4章中所有可运行的代码示例，帮助读者通过实践理解元数据收集与提取技术
"""

import os
import json
import re
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

# ===================== 4.1.1 自动收集技术 =====================

# ===================== 数据库元数据收集 =====================

class DatabaseMetadataExtractor(ABC):
    """数据库元数据提取器基类"""
    
    def __init__(self, connection_config):
        self.connection_config = connection_config
        self.connection = None
    
    @abstractmethod
    def connect(self):
        """连接数据库"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开数据库连接"""
        pass
    
    @abstractmethod
    def extract_schema_metadata(self, schema_name=None):
        """提取模式元数据"""
        pass
    
    @abstractmethod
    def extract_table_metadata(self, schema_name, table_name):
        """提取表元数据"""
        pass
    
    @abstractmethod
    def extract_column_metadata(self, schema_name, table_name):
        """提取列元数据"""
        pass

# 简化的MySQL元数据提取器（不需要实际MySQL连接）
class SimpleMySQLMetadataExtractor:
    """简化的MySQL元数据提取器（用于演示）"""
    
    def __init__(self, connection_config):
        self.connection_config = connection_config
        # 模拟数据库数据
        self.mock_data = {
            "databases": ["ecommerce", "analytics", "userdb"],
            "tables": {
                "ecommerce": [
                    {
                        "name": "users",
                        "engine": "InnoDB",
                        "row_count": 500000,
                        "data_size": 1073741824,  # 1GB
                        "collation": "utf8mb4_unicode_ci",
                        "comment": "用户基本信息"
                    },
                    {
                        "name": "orders",
                        "engine": "InnoDB",
                        "row_count": 2000000,
                        "data_size": 2147483648,  # 2GB
                        "collation": "utf8mb4_unicode_ci",
                        "comment": "订单信息"
                    }
                ],
                "analytics": [
                    {
                        "name": "user_behavior",
                        "engine": "InnoDB",
                        "row_count": 10000000,
                        "data_size": 5368709120,  # 5GB
                        "collation": "utf8mb4_unicode_ci",
                        "comment": "用户行为数据"
                    }
                ]
            },
            "columns": {
                "ecommerce.users": [
                    {
                        "name": "user_id",
                        "type": "bigint",
                        "nullable": False,
                        "key": "PRI",
                        "default": None,
                        "extra": "auto_increment"
                    },
                    {
                        "name": "username",
                        "type": "varchar(50)",
                        "nullable": False,
                        "key": "UNI",
                        "default": None,
                        "extra": ""
                    },
                    {
                        "name": "email",
                        "type": "varchar(100)",
                        "nullable": False,
                        "key": "UNI",
                        "default": None,
                        "extra": ""
                    }
                ],
                "ecommerce.orders": [
                    {
                        "name": "order_id",
                        "type": "bigint",
                        "nullable": False,
                        "key": "PRI",
                        "default": None,
                        "extra": "auto_increment"
                    },
                    {
                        "name": "user_id",
                        "type": "bigint",
                        "nullable": False,
                        "key": "MUL",
                        "default": None,
                        "extra": ""
                    },
                    {
                        "name": "amount",
                        "type": "decimal(10,2)",
                        "nullable": False,
                        "key": "",
                        "default": None,
                        "extra": ""
                    }
                ]
            },
            "constraints": {
                "ecommerce.orders": [
                    {
                        "column": "user_id",
                        "referenced_table": "users",
                        "referenced_column": "user_id"
                    }
                ]
            },
            "indexes": {
                "ecommerce.users": [
                    {
                        "name": "PRIMARY",
                        "columns": ["user_id"],
                        "unique": True
                    },
                    {
                        "name": "idx_username",
                        "columns": ["username"],
                        "unique": True
                    }
                ],
                "ecommerce.orders": [
                    {
                        "name": "PRIMARY",
                        "columns": ["order_id"],
                        "unique": True
                    },
                    {
                        "name": "idx_user_id",
                        "columns": ["user_id"],
                        "unique": False
                    }
                ]
            }
        }
    
    def connect(self):
        """模拟连接MySQL数据库"""
        print(f"连接到MySQL数据库: {self.connection_config.get('host', 'localhost')}")
        return True
    
    def disconnect(self):
        """断开MySQL连接"""
        print("已断开MySQL连接")
    
    def extract_schema_metadata(self, schema_name=None):
        """提取MySQL模式元数据"""
        print(f"提取MySQL模式元数据: {schema_name or '所有'}")
        
        schemas = []
        db_list = self.mock_data["databases"]
        
        if schema_name:
            if schema_name in db_list:
                schemas.append({
                    "name": schema_name,
                    "type": "database",
                    "charset": "utf8mb4"
                })
        else:
            for db_name in db_list:
                schemas.append({
                    "name": db_name,
                    "type": "database",
                    "charset": "utf8mb4"
                })
        
        return schemas
    
    def extract_table_metadata(self, schema_name):
        """提取MySQL表元数据"""
        print(f"提取MySQL表元数据: {schema_name}")
        
        tables = []
        if schema_name in self.mock_data["tables"]:
            for table in self.mock_data["tables"][schema_name]:
                tables.append({
                    "name": table["name"],
                    "schema": schema_name,
                    "engine": table["engine"],
                    "row_count": table["row_count"],
                    "data_size": table["data_size"],
                    "collation": table["collation"],
                    "comment": table["comment"]
                })
        
        return tables
    
    def extract_column_metadata(self, schema_name, table_name):
        """提取MySQL列元数据"""
        print(f"提取MySQL列元数据: {schema_name}.{table_name}")
        
        table_key = f"{schema_name}.{table_name}"
        columns = []
        
        if table_key in self.mock_data["columns"]:
            for column in self.mock_data["columns"][table_key]:
                columns.append({
                    "name": column["name"],
                    "type": column["type"],
                    "nullable": column["nullable"],
                    "key": column["key"],
                    "default": column["default"],
                    "extra": column["extra"]
                })
        
        return columns
    
    def extract_constraints(self, schema_name, table_name):
        """提取约束信息"""
        print(f"提取MySQL约束信息: {schema_name}.{table_name}")
        
        table_key = f"{schema_name}.{table_name}"
        foreign_keys = []
        
        if table_key in self.mock_data["constraints"]:
            for constraint in self.mock_data["constraints"][table_key]:
                foreign_keys.append({
                    "column": constraint["column"],
                    "referenced_table": constraint["referenced_table"],
                    "referenced_column": constraint["referenced_column"]
                })
        
        return foreign_keys
    
    def extract_indexes(self, schema_name, table_name):
        """提取索引信息"""
        print(f"提取MySQL索引信息: {schema_name}.{table_name}")
        
        table_key = f"{schema_name}.{table_name}"
        indexes = []
        
        if table_key in self.mock_data["indexes"]:
            for index in self.mock_data["indexes"][table_key]:
                indexes.append({
                    "name": index["name"],
                    "columns": index["columns"],
                    "unique": index["unique"]
                })
        
        return indexes

# 简化的MongoDB元数据提取器（不需要实际MongoDB连接）
class SimpleMongoMetadataExtractor:
    """简化的MongoDB元数据提取器（用于演示）"""
    
    def __init__(self, connection_config):
        self.connection_config = connection_config
        # 模拟数据库数据
        self.mock_data = {
            "databases": [
                {
                    "name": "userdb",
                    "size": 5368709120,  # 5GB
                    "collections": 5
                },
                {
                    "name": "eventdb",
                    "size": 10737418240,  # 10GB
                    "collections": 8
                }
            ],
            "collections": {
                "userdb": [
                    {
                        "name": "users",
                        "count": 1000000,
                        "size": 1073741824,  # 1GB
                        "avg_size": 1024,
                        "indexes": 2
                    },
                    {
                        "name": "user_sessions",
                        "count": 5000000,
                        "size": 2147483648,  # 2GB
                        "avg_size": 512,
                        "indexes": 3
                    }
                ],
                "eventdb": [
                    {
                        "name": "click_events",
                        "count": 10000000,
                        "size": 5368709120,  # 5GB
                        "avg_size": 640,
                        "indexes": 4
                    }
                ]
            },
            "fields": {
                "userdb.users": [
                    {
                        "name": "_id",
                        "types": ["ObjectId"],
                        "count": 1000000,
                        "null_count": 0
                    },
                    {
                        "name": "username",
                        "types": ["str"],
                        "count": 1000000,
                        "null_count": 0
                    },
                    {
                        "name": "email",
                        "types": ["str"],
                        "count": 1000000,
                        "null_count": 50000
                    },
                    {
                        "name": "age",
                        "types": ["int", "NoneType"],
                        "count": 1000000,
                        "null_count": 100000
                    }
                ]
            }
        }
    
    def connect(self):
        """模拟连接MongoDB"""
        print(f"连接到MongoDB: {self.connection_config.get('host', 'localhost')}")
        return True
    
    def disconnect(self):
        """断开MongoDB连接"""
        print("已断开MongoDB连接")
    
    def extract_schema_metadata(self, schema_name=None):
        """提取MongoDB数据库元数据"""
        print(f"提取MongoDB数据库元数据: {schema_name or '所有'}")
        
        databases = []
        db_list = self.mock_data["databases"]
        
        if schema_name:
            for db in db_list:
                if db["name"] == schema_name:
                    databases.append({
                        "name": db["name"],
                        "type": "database",
                        "size": db["size"],
                        "collections": db["collections"]
                    })
        else:
            for db in db_list:
                databases.append({
                    "name": db["name"],
                    "type": "database",
                    "size": db["size"],
                    "collections": db["collections"]
                })
        
        return databases
    
    def extract_table_metadata(self, schema_name):
        """提取MongoDB集合元数据"""
        print(f"提取MongoDB集合元数据: {schema_name}")
        
        collections = []
        if schema_name in self.mock_data["collections"]:
            for collection in self.mock_data["collections"][schema_name]:
                collections.append({
                    "name": collection["name"],
                    "schema": schema_name,
                    "type": "collection",
                    "count": collection["count"],
                    "size": collection["size"],
                    "avg_size": collection["avg_size"],
                    "indexes": collection["indexes"]
                })
        
        return collections
    
    def extract_column_metadata(self, schema_name, table_name):
        """提取MongoDB字段元数据"""
        print(f"提取MongoDB字段元数据: {schema_name}.{table_name}")
        
        collection_key = f"{schema_name}.{table_name}"
        columns = []
        
        if collection_key in self.mock_data["fields"]:
            for field in self.mock_data["fields"][collection_key]:
                null_ratio = field["null_count"] / field["count"] if field["count"] > 0 else 0
                
                columns.append({
                    "name": field["name"],
                    "types": field["types"],
                    "count": field["count"],
                    "null_count": field["null_count"],
                    "null_ratio": null_ratio
                })
        
        return columns

def demo_database_metadata_extraction():
    """演示数据库元数据提取"""
    print("=" * 50)
    print("4.1.1 数据库元数据自动收集示例")
    print("=" * 50)
    
    # MySQL连接配置
    mysql_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "password",
        "database": "ecommerce"
    }
    
    # 创建MySQL元数据提取器
    mysql_extractor = SimpleMySQLMetadataExtractor(mysql_config)
    
    # 连接并提取元数据
    if mysql_extractor.connect():
        print("成功连接到MySQL数据库")
        
        # 提取表元数据
        tables = mysql_extractor.extract_table_metadata("ecommerce")
        print(f"MySQL中的表数量: {len(tables)}")
        
        # 提取第一个表的列元数据
        if tables:
            first_table = tables[0]
            columns = mysql_extractor.extract_column_metadata("ecommerce", first_table["name"])
            print(f"表 {first_table['name']} 的列数量: {len(columns)}")
            
            # 提取约束信息
            constraints = mysql_extractor.extract_constraints("ecommerce", first_table["name"])
            print(f"表 {first_table['name']} 的约束数量: {len(constraints)}")
        
        mysql_extractor.disconnect()
    
    # MongoDB连接配置
    mongo_config = {
        "host": "localhost",
        "port": 27017,
        "database": "userdb"
    }
    
    # 创建MongoDB元数据提取器
    mongo_extractor = SimpleMongoMetadataExtractor(mongo_config)
    
    # 连接并提取元数据
    if mongo_extractor.connect():
        print("成功连接到MongoDB")
        
        # 提取集合元数据
        collections = mongo_extractor.extract_table_metadata("userdb")
        print(f"MongoDB中的集合数量: {len(collections)}")
        
        # 提取第一个集合的字段元数据
        if collections:
            first_collection = collections[0]
            fields = mongo_extractor.extract_column_metadata("userdb", first_collection["name"])
            print(f"集合 {first_collection['name']} 的字段数量: {len(fields)}")
            
            # 显示字段统计
            for field in fields:
                print(f"  字段 {field['name']}: 类型 {', '.join(field['types'])}, 空值率 {field['null_ratio']:.2%}")
        
        mongo_extractor.disconnect()
    
    return mysql_extractor, mongo_extractor

# ===================== 文件系统元数据收集 =====================

class SimpleFileSystemMetadataExtractor:
    """简化的文件系统元数据提取器（用于演示）"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.supported_formats = ['.csv', '.json', '.parquet', '.xlsx', '.txt', '.log']
        # 模拟文件数据
        self.mock_files = {
            "/data/users.csv": {
                "name": "users.csv",
                "path": "/data/users.csv",
                "type": "file",
                "extension": ".csv",
                "size": 1048576,  # 1MB
                "mime_type": "text/csv",
                "content_type": "csv",
                "columns": ["id", "name", "email", "age"],
                "column_count": 4,
                "estimated_rows": 10000,
                "encoding": "utf-8"
            },
            "/data/events.json": {
                "name": "events.json",
                "path": "/data/events.json",
                "type": "file",
                "extension": ".json",
                "size": 5242880,  # 5MB
                "mime_type": "application/json",
                "content_type": "json_array",
                "estimated_records": 50000,
                "fields": ["event_id", "user_id", "event_type", "timestamp"]
            },
            "/data/analytics": {
                "name": "analytics",
                "path": "/data/analytics",
                "type": "directory",
                "created_at": datetime(2023, 1, 15),
                "modified_at": datetime(2023, 11, 27),
                "size": 10737418240,  # 10GB
                "subdirectories": 5,
                "files": 120
            }
        }
    
    def extract_directory_metadata(self, directory_path=None):
        """提取目录元数据"""
        if directory_path:
            target_dir = Path(directory_path)
        else:
            target_dir = self.base_path
        
        print(f"提取目录元数据: {target_dir}")
        
        # 检查是否是模拟目录
        dir_path_str = str(target_dir)
        
        for path, metadata in self.mock_files.items():
            if metadata["type"] == "directory" and path == dir_path_str:
                return metadata
        
        # 如果不是模拟目录，返回默认信息
        return {
            "name": target_dir.name,
            "path": str(target_dir),
            "type": "directory",
            "created_at": datetime(2023, 1, 1),
            "modified_at": datetime.now(),
            "subdirectories": 3,
            "files": 50
        }
    
    def extract_file_metadata(self, file_path):
        """提取文件元数据"""
        print(f"提取文件元数据: {file_path}")
        
        file_path_str = str(file_path)
        
        # 检查是否是模拟文件
        for path, metadata in self.mock_files.items():
            if metadata["type"] == "file" and path == file_path_str:
                # 添加基本属性
                metadata["created_at"] = datetime(2023, 1, 15)
                metadata["modified_at"] = datetime(2023, 11, 27)
                return metadata
        
        # 如果不是模拟文件，返回默认信息
        path_obj = Path(file_path)
        return {
            "name": path_obj.name,
            "path": file_path_str,
            "type": "file",
            "extension": path_obj.suffix,
            "size": 1024 * 1024,  # 1MB
            "created_at": datetime(2023, 1, 1),
            "modified_at": datetime.now(),
            "mime_type": "application/octet-stream"
        }
    
    def extract_directory_tree(self, max_depth=3):
        """提取目录树元数据"""
        print(f"提取目录树元数据，最大深度: {max_depth}")
        
        # 简化实现：返回预定义的目录结构
        return {
            "name": "data",
            "path": "/data",
            "type": "directory",
            "created_at": datetime(2023, 1, 1),
            "modified_at": datetime.now(),
            "subdirectories": 3,
            "files": 50,
            "children": [
                self.mock_files["/data/users.csv"],
                self.mock_files["/data/events.json"],
                self.mock_files["/data/analytics"]
            ]
        }

def demo_file_system_metadata_extraction():
    """演示文件系统元数据提取"""
    print("\n" + "=" * 50)
    print("4.1.1 文件系统元数据自动收集示例")
    print("=" * 50)
    
    # 创建文件系统元数据提取器
    extractor = SimpleFileSystemMetadataExtractor("/data")
    
    # 提取目录元数据
    dir_metadata = extractor.extract_directory_metadata("/data/analytics")
    print(f"目录元数据:")
    print(f"  路径: {dir_metadata['path']}")
    print(f"  文件数: {dir_metadata['files']}")
    print(f"  子目录数: {dir_metadata['subdirectories']}")
    
    # 提取文件元数据
    csv_metadata = extractor.extract_file_metadata("/data/users.csv")
    print(f"\nCSV文件元数据:")
    print(f"  文件名: {csv_metadata['name']}")
    print(f"  大小: {csv_metadata['size']} 字节")
    print(f"  内容类型: {csv_metadata.get('content_type')}")
    if 'columns' in csv_metadata:
        print(f"  列: {csv_metadata['columns']}")
    
    json_metadata = extractor.extract_file_metadata("/data/events.json")
    print(f"\nJSON文件元数据:")
    print(f"  文件名: {json_metadata['name']}")
    print(f"  内容类型: {json_metadata.get('content_type')}")
    if 'estimated_records' in json_metadata:
        print(f"  估计记录数: {json_metadata['estimated_records']}")
    if 'fields' in json_metadata:
        print(f"  字段: {json_metadata['fields']}")
    
    # 提取目录树
    dir_tree = extractor.extract_directory_tree()
    print(f"\n目录树信息:")
    print(f"  根目录: {dir_tree['name']}")
    print(f"  子项数: {len(dir_tree.get('children', []))}")
    
    return extractor

# ===================== 4.1.2 半自动化收集方法 =====================

class SemiAutomatedMetadataCollector:
    """半自动化元数据收集器"""
    
    def __init__(self):
        self.collected_metadata = {}
        self.manual_reviews = []
        self.collection_rules = {}
    
    def configure_collection_rules(self, rules):
        """配置收集规则"""
        self.collection_rules = rules
        print(f"已配置收集规则: {len(rules)} 项")
    
    def auto_collect_basic_metadata(self, source_info):
        """自动收集基础元数据"""
        metadata_id = f"{source_info['type']}_{source_info['name']}_{int(datetime.now().timestamp())}"
        
        print(f"自动收集基础元数据: {metadata_id}")
        
        # 基础元数据
        basic_metadata = {
            "name": source_info.get("name"),
            "type": source_info.get("type"),
            "source": source_info.get("source"),
            "location": source_info.get("location"),
            "created_at": datetime.now(),
            "auto_generated": True
        }
        
        # 根据数据源类型收集特定元数据
        if source_info.get("type") == "api":
            api_metadata = self._collect_api_metadata(source_info)
            basic_metadata.update(api_metadata)
        elif source_info.get("type") == "file":
            file_metadata = self._collect_file_metadata(source_info)
            basic_metadata.update(file_metadata)
        elif source_info.get("type") == "database_table":
            db_metadata = self._collect_db_metadata(source_info)
            basic_metadata.update(db_metadata)
        
        # 存储自动收集的元数据
        self.collected_metadata[metadata_id] = {
            "basic": basic_metadata,
            "detailed": {},
            "manual_review_required": self._check_review_needed(basic_metadata)
        }
        
        return metadata_id
    
    def _collect_api_metadata(self, api_info):
        """收集API元数据"""
        print("收集API元数据")
        
        metadata = {
            "endpoint": api_info.get("endpoint"),
            "method": api_info.get("method", "GET"),
            "parameters": api_info.get("parameters", []),
            "headers": api_info.get("headers", {}),
            "response_format": api_info.get("response_format", "json")
        }
        
        # 尝试自动推断参数类型
        if "parameters" in metadata:
            for param in metadata["parameters"]:
                if "type" not in param:
                    param["type"] = self._infer_parameter_type(param)
        
        return metadata
    
    def _collect_file_metadata(self, file_info):
        """收集文件元数据"""
        print("收集文件元数据")
        
        file_path = Path(file_info.get("path", ""))
        
        # 模拟文件基本信息
        metadata = {
            "path": str(file_path),
            "extension": file_path.suffix,
            "size": 1024 * 1024,  # 假设1MB
            "modified_at": datetime.now()
        }
        
        # 如果是CSV文件，尝试分析结构
        if file_path.suffix == '.csv':
            csv_structure = {
                "columns": ["id", "name", "value"],  # 模拟列
                "column_count": 3,
                "estimated_rows": 10000,
                "encoding": "utf-8"
            }
            metadata.update(csv_structure)
        
        return metadata
    
    def _collect_db_metadata(self, db_info):
        """收集数据库表元数据"""
        print("收集数据库表元数据")
        
        metadata = {
            "database": db_info.get("database"),
            "schema": db_info.get("schema"),
            "table": db_info.get("table"),
            "estimated_rows": db_info.get("estimated_rows"),
            "refresh_frequency": db_info.get("refresh_frequency")
        }
        
        # 如果提供了列信息
        if "columns" in db_info:
            metadata["columns"] = db_info["columns"]
        
        return metadata
    
    def _infer_parameter_type(self, param):
        """推断参数类型"""
        param_name = param.get("name", "").lower()
        
        # 基于参数名推断类型
        if any(keyword in param_name for keyword in ["date", "time", "at", "from", "to"]):
            return "datetime"
        elif any(keyword in param_name for keyword in ["id", "count", "num", "size", "amount"]):
            return "integer"
        elif any(keyword in param_name for keyword in ["price", "rate", "value", "percent"]):
            return "float"
        elif any(keyword in param_name for keyword in ["flag", "is", "has", "active"]):
            return "boolean"
        elif "email" in param_name:
            return "email"
        
        return "string"
    
    def _check_review_needed(self, metadata):
        """检查是否需要人工审核"""
        # 如果有错误信息，需要人工审核
        if "error" in metadata:
            return True
        
        # 如果缺少关键信息，需要人工审核
        required_fields = self.collection_rules.get("required_fields", [])
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                return True
        
        # 如果是新的数据源类型，可能需要人工审核
        new_source_types = self.collection_rules.get("review_required_types", [])
        if metadata.get("type") in new_source_types:
            return True
        
        return False
    
    def request_manual_review(self, metadata_id, review_info):
        """请求人工审核"""
        if metadata_id not in self.collected_metadata:
            return False
        
        review = {
            "metadata_id": metadata_id,
            "requested_by": review_info.get("user"),
            "requested_at": datetime.now(),
            "reason": review_info.get("reason", "Standard review process"),
            "status": "pending",
            "notes": review_info.get("notes", "")
        }
        
        self.manual_reviews.append(review)
        print(f"已请求人工审核: {metadata_id}")
        return True
    
    def submit_manual_review(self, metadata_id, review_data):
        """提交人工审核结果"""
        if metadata_id not in self.collected_metadata:
            return False
        
        # 查找对应的审核请求
        review_request = None
        for review in self.manual_reviews:
            if review["metadata_id"] == metadata_id and review["status"] == "pending":
                review_request = review
                break
        
        if not review_request:
            return False
        
        # 更新审核状态
        review_request["status"] = "completed"
        review_request["completed_at"] = datetime.now()
        review_request["reviewer"] = review_data.get("reviewer")
        review_request["approved"] = review_data.get("approved", True)
        review_request["review_notes"] = review_data.get("notes", "")
        
        # 更新元数据
        if review_data.get("approved", True):
            self.collected_metadata[metadata_id]["detailed"] = review_data.get("metadata_updates", {})
            self.collected_metadata[metadata_id]["manual_review_required"] = False
        
        print(f"已完成人工审核: {metadata_id}")
        return True
    
    def get_metadata_for_review(self, status="pending"):
        """获取待审核的元数据"""
        result = []
        
        for review in self.manual_reviews:
            if review["status"] == status:
                metadata_id = review["metadata_id"]
                if metadata_id in self.collected_metadata:
                    result.append({
                        "review": review,
                        "metadata": self.collected_metadata[metadata_id]
                    })
        
        return result
    
    def finalize_metadata(self, metadata_id):
        """最终确定元数据"""
        if metadata_id not in self.collected_metadata:
            return None
        
        metadata_entry = self.collected_metadata[metadata_id]
        
        if metadata_entry["manual_review_required"]:
            return None  # 需要先完成人工审核
        
        # 合并基础元数据和详细元数据
        final_metadata = metadata_entry["basic"].copy()
        final_metadata.update(metadata_entry["detailed"])
        
        # 添加最终确定的标记
        final_metadata["finalized_at"] = datetime.now()
        final_metadata["finalized_by"] = "system"  # 实际应用中可能是审核人
        
        return final_metadata

def demo_semi_automated_collection():
    """演示半自动化元数据收集"""
    print("\n" + "=" * 50)
    print("4.1.2 半自动化元数据收集示例")
    print("=" * 50)
    
    # 创建收集器并配置规则
    collector = SemiAutomatedMetadataCollector()
    collector.configure_collection_rules({
        "required_fields": ["name", "type", "description"],
        "review_required_types": ["api"]
    })
    
    # 自动收集API元数据
    api_source = {
        "name": "用户服务API",
        "type": "api",
        "endpoint": "https://api.example.com/users",
        "method": "GET",
        "parameters": [
            {"name": "user_id", "type": "integer", "description": "用户ID"},
            {"name": "include_profile", "type": "boolean", "default": False, "description": "是否包含用户画像"}
        ],
        "response_format": "json"
    }
    
    api_metadata_id = collector.auto_collect_basic_metadata(api_source)
    print(f"已收集API元数据，ID: {api_metadata_id}")
    
    # 自动收集文件元数据
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,name,email\n")
        f.write("1,Alice,alice@example.com\n")
        f.write("2,Bob,bob@example.com\n")
        file_path = f.name
    
    file_source = {
        "name": "用户联系人",
        "type": "file",
        "path": file_path,
        "description": "用户联系人信息CSV文件"
    }
    
    file_metadata_id = collector.auto_collect_basic_metadata(file_source)
    print(f"已收集文件元数据，ID: {file_metadata_id}")
    
    # 请求人工审核
    collector.request_manual_review(api_metadata_id, {
        "user": "data_steward",
        "reason": "新API源需要验证参数定义"
    })
    
    # 查看待审核项
    pending_reviews = collector.get_metadata_for_review("pending")
    print(f"待审核项数量: {len(pending_reviews)}")
    
    # 模拟审核过程
    if pending_reviews:
        review = pending_reviews[0]
        metadata_id = review["review"]["metadata_id"]
        
        # 提交审核结果
        collector.submit_manual_review(metadata_id, {
            "reviewer": "data_steward",
            "approved": True,
            "metadata_updates": {
                "description": "用户服务API，提供用户基本信息查询功能",
                "owner": "用户服务团队",
                "api_documentation": "https://docs.example.com/api/users"
            },
            "notes": "API元数据已验证，参数定义正确"
        })
        
        print(f"已完成审核，ID: {metadata_id}")
    
    # 获取最终确定的元数据
    finalized_metadata = collector.finalize_metadata(api_metadata_id)
    if finalized_metadata:
        print(f"API最终元数据:")
        print(f"  名称: {finalized_metadata.get('name')}")
        print(f"  描述: {finalized_metadata.get('description')}")
        print(f"  所有者: {finalized_metadata.get('owner')}")
    
    # 清理临时文件
    os.unlink(file_path)
    
    return collector

# ===================== 4.2.1 结构化数据提取 =====================

class SimpleStructuredDataExtractor:
    """简化的结构化数据提取器（用于演示）"""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        # 模拟数据库数据
        self.mock_data = {
            "database": {
                "name": "ecommerce",
                "driver": "sqlite",
                "dialect": "sqlite"
            },
            "schemas": [
                {"name": "public", "table_count": 3}
            ],
            "tables": {
                "users": {
                    "name": "users",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                        {"name": "name", "type": "VARCHAR(50)", "nullable": False},
                        {"name": "email", "type": "VARCHAR(100)", "nullable": False}
                    ],
                    "indexes": [
                        {"name": "sqlite_autoindex_users_1", "columns": ["id"], "unique": True}
                    ],
                    "primary_keys": ["id"],
                    "row_count": 1000
                },
                "orders": {
                    "name": "orders",
                    "schema": "public",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                        {"name": "user_id", "type": "INTEGER", "nullable": False},
                        {"name": "amount", "type": "DECIMAL(10,2)", "nullable": False},
                        {"name": "order_date", "type": "DATE", "nullable": False}
                    ],
                    "indexes": [
                        {"name": "sqlite_autoindex_orders_1", "columns": ["id"], "unique": True}
                    ],
                    "primary_keys": ["id"],
                    "foreign_keys": [
                        {"name": "fk_orders_users", "columns": ["user_id"], "referred_table": "users", "referred_columns": ["id"]}
                    ],
                    "row_count": 2000
                }
            }
        }
    
    def extract_database_schema(self):
        """提取数据库模式"""
        print("提取数据库模式")
        return self.mock_data["database"]
    
    def extract_schemas(self):
        """提取所有模式"""
        print("提取所有模式")
        return self.mock_data["schemas"]
    
    def extract_tables(self, schema_name=None):
        """提取表信息"""
        print(f"提取表信息，模式: {schema_name or '所有'}")
        
        tables = []
        for table_name, table_info in self.mock_data["tables"].items():
            tables.append(table_info)
        
        return tables
    
    def extract_table_statistics(self, table_name, schema_name=None, sample_size=1000):
        """提取表统计信息"""
        print(f"提取表统计信息: {table_name}")
        
        if table_name not in self.mock_data["tables"]:
            return {"error": f"表 {table_name} 不存在"}
        
        table_info = self.mock_data["tables"][table_name]
        
        # 模拟统计信息
        stats = {
            "total_columns": len(table_info["columns"]),
            "sample_rows": min(sample_size, table_info["row_count"]),
            "column_statistics": {}
        }
        
        # 为每列生成统计信息
        for column in table_info["columns"]:
            column_name = column["name"]
            column_type = column["type"]
            
            column_stats = {
                "data_type": column_type,
                "null_count": 0,  # 简化：假设没有空值
                "null_percentage": 0
            }
            
            # 根据数据类型计算不同的统计信息
            if "INTEGER" in column_type or "DECIMAL" in column_type:
                column_stats.update({
                    "min": 1,
                    "max": 1000,
                    "mean": 500.5,
                    "std": 288.7
                })
            else:
                # 字符串类型
                column_stats.update({
                    "unique_count": 900,
                    "unique_percentage": 90.0,
                    "min_length": 5,
                    "max_length": 50,
                    "avg_length": 15.2
                })
            
            stats["column_statistics"][column_name] = column_stats
        
        return stats
    
    def extract_relationship_graph(self, schema_name=None):
        """提取表关系图"""
        print("提取表关系图")
        
        nodes = []
        edges = []
        
        # 创建节点（表）
        for table_name, table_info in self.mock_data["tables"].items():
            nodes.append({
                "id": f"{schema_name or 'public'}.{table_name}" if schema_name else table_name,
                "name": table_name,
                "type": "table",
                "schema": schema_name or "public"
            })
        
        # 创建边（关系）
        for table_name, table_info in self.mock_data["tables"].items():
            if "foreign_keys" in table_info:
                for fk in table_info["foreign_keys"]:
                    from_table = f"{schema_name or 'public'}.{table_name}" if schema_name else table_name
                    to_table = f"{schema_name or 'public'}.{fk['referred_table']}" if schema_name else fk['referred_table']
                    
                    edges.append({
                        "from": from_table,
                        "to": to_table,
                        "type": "foreign_key",
                        "from_columns": fk["columns"],
                        "to_columns": fk["referred_columns"]
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }

def demo_structured_data_extraction():
    """演示结构化数据提取"""
    print("\n" + "=" * 50)
    print("4.2.1 结构化数据提取示例")
    print("=" * 50)
    
    # 创建结构化数据提取器
    extractor = SimpleStructuredDataExtractor("sqlite:///:memory:")
    
    # 提取数据库模式
    database_info = extractor.extract_database_schema()
    print(f"数据库信息: {database_info['name']}")
    
    # 提取模式信息
    schemas = extractor.extract_schemas()
    print(f"模式数量: {len(schemas)}")
    
    # 提取表信息
    tables = extractor.extract_tables()
    print(f"表数量: {len(tables)}")
    
    for table in tables:
        print(f"\n表: {table['name']}")
        print(f"  列数: {len(table['columns'])}")
        print(f"  主键: {table['primary_keys']}")
        
        # 显示列信息
        for column in table['columns']:
            print(f"    {column['name']}: {column['type']} ({'NULL' if column.get('nullable', True) else 'NOT NULL'})")
        
        # 显示外键信息
        if 'foreign_keys' in table:
            for fk in table['foreign_keys']:
                print(f"    外键 {fk['columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # 提取表统计信息
    for table in tables:
        stats = extractor.extract_table_statistics(table['name'])
        if "error" not in stats:
            print(f"\n表 {table['name']} 统计信息:")
            print(f"  采样行数: {stats['sample_rows']}")
            
            for col_name, col_stats in stats['column_statistics'].items():
                print(f"    列 {col_name} ({col_stats['data_type']}): 空值率 {col_stats['null_percentage']:.1f}%")
                
                if 'min' in col_stats and col_stats['min'] is not None:
                    print(f"      范围: {col_stats['min']} - {col_stats['max']}")
                
                if 'unique_count' in col_stats:
                    print(f"      唯一值: {col_stats['unique_count']} ({col_stats['unique_percentage']:.1f}%)")
    
    # 提取关系图
    relationship_graph = extractor.extract_relationship_graph()
    print(f"\n关系图信息:")
    print(f"  节点数: {len(relationship_graph['nodes'])}")
    print(f"  边数: {len(relationship_graph['edges'])}")
    
    for edge in relationship_graph['edges']:
        print(f"  {edge['from']} -> {edge['to']} ({edge['type']})")
    
    return extractor

# ===================== 4.3.1 元数据映射与转换 =====================

class MetadataIntegrator:
    """元数据整合器"""
    
    def __init__(self):
        self.source_mappings = {}  # 源系统映射规则
        self.target_standards = {}  # 目标标准
        self.transformation_rules = {}  # 转换规则
        self.integrated_metadata = {}  # 已整合的元数据
    
    def register_source_system(self, system_id, system_config):
        """注册源系统"""
        self.source_mappings[system_id] = {
            "name": system_config["name"],
            "metadata_format": system_config.get("metadata_format", "json"),
            "field_mappings": system_config.get("field_mappings", {}),
            "data_types": system_config.get("data_types", {}),
            "timestamp_formats": system_config.get("timestamp_formats", {})
        }
        print(f"已注册源系统: {system_id} - {system_config['name']}")
    
    def define_target_standard(self, standard_name, standard_schema):
        """定义目标标准"""
        self.target_standards[standard_name] = standard_schema
        print(f"已定义目标标准: {standard_name}")
    
    def add_transformation_rule(self, rule_id, rule_config):
        """添加转换规则"""
        self.transformation_rules[rule_id] = {
            "source_pattern": rule_config["source_pattern"],
            "target_format": rule_config["target_format"],
            "transformation_function": rule_config.get("function")
        }
        print(f"已添加转换规则: {rule_id}")
    
    def integrate_metadata(self, source_system_id, metadata, target_standard="default"):
        """整合元数据到目标标准"""
        if source_system_id not in self.source_mappings:
            raise ValueError(f"未知源系统: {source_system_id}")
        
        if target_standard not in self.target_standards:
            raise ValueError(f"未知目标标准: {target_standard}")
        
        print(f"整合元数据: {source_system_id} -> {target_standard}")
        
        source_mapping = self.source_mappings[source_system_id]
        target_schema = self.target_standards[target_standard]
        
        # 初始化结果
        integrated = {
            "source_system": source_system_id,
            "source_system_name": source_mapping["name"],
            "integration_timestamp": datetime.now().isoformat(),
            "target_standard": target_standard
        }
        
        # 应用字段映射
        self._apply_field_mappings(metadata, integrated, source_mapping["field_mappings"])
        
        # 应用数据类型转换
        self._apply_type_conversions(integrated, source_mapping["data_types"], target_schema)
        
        # 应用转换规则
        self._apply_transformation_rules(integrated)
        
        # 标准化格式
        self._standardize_format(integrated, target_schema)
        
        # 存储整合结果
        metadata_id = f"{source_system_id}_{int(datetime.now().timestamp())}"
        self.integrated_metadata[metadata_id] = integrated
        
        return metadata_id
    
    def _apply_field_mappings(self, source, target, field_mappings):
        """应用字段映射"""
        for source_field, target_field in field_mappings.items():
            if source_field in source:
                target[target_field] = source[source_field]
    
    def _apply_type_conversions(self, metadata, type_mapping, target_schema):
        """应用数据类型转换"""
        for field, expected_type in target_schema.get("fields", {}).items():
            if field in metadata:
                current_value = metadata[field]
                
                # 根据源系统类型映射进行转换
                source_type = type_mapping.get(field)
                
                if source_type and expected_type:
                    converted_value = self._convert_type(
                        current_value, 
                        source_type, 
                        expected_type
                    )
                    metadata[field] = converted_value
    
    def _convert_type(self, value, from_type, to_type):
        """数据类型转换"""
        # 简化实现，实际应用中会更复杂
        if from_type == "string" and to_type == "integer":
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        elif from_type == "string" and to_type == "float":
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        elif from_type == "string" and to_type == "datetime":
            # 尝试解析为ISO格式日期时间
            try:
                return datetime.fromisoformat(value).isoformat()
            except (ValueError, TypeError):
                return value
        
        elif from_type == "integer" and to_type == "string":
            return str(value)
        
        elif from_type == "timestamp" and to_type == "datetime":
            if isinstance(value, datetime):
                return value.isoformat()
            return value
        
        return value
    
    def _apply_transformation_rules(self, metadata):
        """应用转换规则"""
        for rule_id, rule in self.transformation_rules.items():
            pattern = rule["source_pattern"]
            target_format = rule["target_format"]
            
            # 检查是否有字段匹配模式
            for field, value in metadata.items():
                if isinstance(value, str) and re.match(pattern, value):
                    # 应用转换函数
                    if rule["transformation_function"]:
                        try:
                            # 使用内置转换函数
                            if rule["transformation_function"] == "upper":
                                metadata[field] = value.upper()
                            elif rule["transformation_function"] == "lower":
                                metadata[field] = value.lower()
                            elif rule["transformation_function"] == "snake_to_camel":
                                metadata[field] = self._snake_to_camel_case(value)
                            # 可以添加更多转换函数
                        except Exception as e:
                            print(f"应用转换规则 {rule_id} 失败: {e}")
    
    def _snake_to_camel_case(self, snake_str):
        """将下划线命名转换为驼峰命名"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])
    
    def _standardize_format(self, metadata, target_schema):
        """标准化格式"""
        # 确保必填字段存在
        required_fields = target_schema.get("required_fields", [])
        for field in required_fields:
            if field not in metadata:
                metadata[field] = None
        
        # 设置默认值
        default_values = target_schema.get("default_values", {})
        for field, default_value in default_values.items():
            if field in metadata and metadata[field] is None:
                metadata[field] = default_value
        
        # 确保字段名格式正确
        if "field_name_format" in target_schema:
            name_format = target_schema["field_name_format"]
            if name_format == "snake_case":
                # 转换为下划线命名
                new_metadata = {}
                for field, value in metadata.items():
                    new_field = self._camel_to_snake_case(field)
                    new_metadata[new_field] = value
                metadata.clear()
                metadata.update(new_metadata)
    
    def _camel_to_snake_case(self, camel_str):
        """将驼峰命名转换为下划线命名"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def get_integrated_metadata(self, metadata_id):
        """获取已整合的元数据"""
        return self.integrated_metadata.get(metadata_id)
    
    def query_integrated_metadata(self, filters=None):
        """查询已整合的元数据"""
        results = []
        
        for metadata_id, metadata in self.integrated_metadata.items():
            match = True
            
            if filters:
                for field, value in filters.items():
                    if field in metadata:
                        if isinstance(value, str) and isinstance(metadata[field], str):
                            if value.lower() not in metadata[field].lower():
                                match = False
                                break
                        elif metadata[field] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
            
            if match:
                results.append({
                    "id": metadata_id,
                    "metadata": metadata
                })
        
        return results
    
    def merge_metadata(self, metadata_ids, merge_strategy="overwrite"):
        """合并多个元数据"""
        merged = {}
        
        for metadata_id in metadata_ids:
            metadata = self.integrated_metadata.get(metadata_id)
            if not metadata:
                continue
            
            if merge_strategy == "overwrite":
                merged.update(metadata)
            elif merge_strategy == "merge":
                for key, value in metadata.items():
                    if key in merged:
                        if isinstance(merged[key], list) and isinstance(value, list):
                            merged[key].extend(value)
                        elif isinstance(merged[key], dict) and isinstance(value, dict):
                            merged[key].update(value)
                        else:
                            # 对于简单类型，保留第一个值
                            pass
                    else:
                        merged[key] = value
        
        return merged

def demo_metadata_integration():
    """演示元数据整合"""
    print("\n" + "=" * 50)
    print("4.3.1 元数据映射与转换示例")
    print("=" * 50)
    
    # 创建元数据整合器
    integrator = MetadataIntegrator()
    
    # 注册源系统
    integrator.register_source_system("mysql_system", {
        "name": "MySQL业务系统",
        "metadata_format": "json",
        "field_mappings": {
            "TableName": "table_name",
            "TableType": "table_type",
            "Columns": "columns",
            "RowCount": "row_count",
            "CreatedDate": "created_at"
        },
        "data_types": {
            "table_name": "string",
            "table_type": "string",
            "row_count": "integer",
            "created_at": "timestamp"
        }
    })
    
    integrator.register_source_system("oracle_system", {
        "name": "Oracle数据仓库",
        "metadata_format": "json",
        "field_mappings": {
            "OBJECT_NAME": "table_name",
            "OBJECT_TYPE": "table_type",
            "COLUMN_INFO": "columns",
            "NUM_ROWS": "row_count",
            "CREATED": "created_at"
        },
        "data_types": {
            "table_name": "string",
            "table_type": "string",
            "row_count": "number",
            "created_at": "date"
        }
    })
    
    # 定义目标标准
    integrator.define_target_standard("unified_table", {
        "fields": {
            "table_name": "string",
            "table_type": "string",
            "columns": "array",
            "row_count": "integer",
            "created_at": "datetime"
        },
        "required_fields": ["table_name", "table_type"],
        "default_values": {
            "table_type": "TABLE"
        },
        "field_name_format": "snake_case"
    })
    
    # 添加转换规则
    integrator.add_transformation_rule("normalize_table_names", {
        "source_pattern": r"^[A-Z_]+$",
        "target_format": "lowercase",
        "transformation_function": "lower"
    })
    
    # 模拟MySQL系统元数据
    mysql_metadata = {
        "TableName": "USER_PROFILE",
        "TableType": "TABLE",
        "Columns": [
            {"name": "USER_ID", "type": "BIGINT"},
            {"name": "USER_NAME", "type": "VARCHAR(50)"},
            {"name": "EMAIL", "type": "VARCHAR(100)"}
        ],
        "RowCount": "1000000",
        "CreatedDate": "2023-01-15T10:30:00Z"
    }
    
    # 模拟Oracle系统元数据
    oracle_metadata = {
        "OBJECT_NAME": "SALES_SUMMARY",
        "OBJECT_TYPE": "TABLE",
        "COLUMN_INFO": [
            {"name": "SALE_ID", "type": "NUMBER"},
            {"name": "PRODUCT_ID", "type": "NUMBER"},
            {"name": "AMOUNT", "type": "NUMBER(10,2)"}
        ],
        "NUM_ROWS": 5000000,
        "CREATED": "15-JAN-23"
    }
    
    # 整合MySQL元数据
    mysql_id = integrator.integrate_metadata("mysql_system", mysql_metadata, "unified_table")
    print(f"已整合MySQL元数据，ID: {mysql_id}")
    
    # 整合Oracle元数据
    oracle_id = integrator.integrate_metadata("oracle_system", oracle_metadata, "unified_table")
    print(f"已整合Oracle元数据，ID: {oracle_id}")
    
    # 查看整合结果
    mysql_result = integrator.get_integrated_metadata(mysql_id)
    print(f"\nMySQL整合结果:")
    print(f"  表名: {mysql_result['table_name']}")
    print(f"  行数: {mysql_result['row_count']}")
    print(f"  创建时间: {mysql_result['created_at']}")
    
    oracle_result = integrator.get_integrated_metadata(oracle_id)
    print(f"\nOracle整合结果:")
    print(f"  表名: {oracle_result['table_name']}")
    print(f"  行数: {oracle_result['row_count']}")
    print(f"  创建时间: {oracle_result['created_at']}")
    
    # 查询整合的元数据
    query_results = integrator.query_integrated_metadata({"source_system": "mysql_system"})
    print(f"\n查询MySQL系统的元数据: {len(query_results)} 条")
    
    # 合并元数据
    merged_metadata = integrator.merge_metadata([mysql_id, oracle_id], "merge")
    print(f"\n合并后的元数据字段数: {len(merged_metadata)}")
    
    return integrator

# ===================== 主函数 - 运行所有演示 =====================

def main():
    """运行所有演示示例"""
    print("第4章：元数据收集与提取 - 代码示例")
    print("=" * 80)
    
    # 演示数据库元数据收集
    mysql_extractor, mongo_extractor = demo_database_metadata_extraction()
    
    # 演示文件系统元数据收集
    file_extractor = demo_file_system_metadata_extraction()
    
    # 演示半自动化元数据收集
    semi_collector = demo_semi_automated_collection()
    
    # 演示结构化数据提取
    structured_extractor = demo_structured_data_extraction()
    
    # 演示元数据整合
    integrator = demo_metadata_integration()
    
    print("\n" + "=" * 80)
    print("所有演示完成！您可以根据自己的需求修改和扩展这些示例。")

if __name__ == "__main__":
    main()