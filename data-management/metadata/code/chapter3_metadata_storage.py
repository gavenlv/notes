"""
第3章：元数据存储与模型 - 配套代码示例
本文件包含第3章中所有可运行的代码示例，帮助读者通过实践理解元数据存储与模型设计
"""

from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Optional, Any

# ===================== 3.1.1 集中式 vs 分布式存储 =====================

# ===================== 集中式元数据存储 =====================

class CentralizedMetadataStorage:
    """集中式元数据存储系统"""
    def __init__(self):
        self.metadata_repository = {}  # 中央元数据仓库
        self.access_control = {}        # 访问控制列表
        self.change_logs = []           # 变更日志
        self.search_index = {}          # 搜索索引
    
    def store_metadata(self, metadata_id, metadata_content, user_info):
        """存储元数据"""
        # 检查权限
        if not self._check_permission(user_info, "write"):
            raise PermissionError("用户无写入权限")
        
        # 记录变更
        if metadata_id in self.metadata_repository:
            old_content = self.metadata_repository[metadata_id]
            self._log_change(metadata_id, "update", user_info, old_content, metadata_content)
        else:
            self._log_change(metadata_id, "create", user_info, None, metadata_content)
        
        # 存储元数据
        self.metadata_repository[metadata_id] = {
            "content": metadata_content,
            "created_by": user_info["user_id"],
            "created_at": datetime.now(),
            "last_updated_by": user_info["user_id"],
            "last_updated_at": datetime.now()
        }
        
        # 更新搜索索引
        self._update_search_index(metadata_id, metadata_content)
        
        return metadata_id
    
    def retrieve_metadata(self, metadata_id, user_info):
        """检索元数据"""
        # 检查权限
        if not self._check_permission(user_info, "read"):
            raise PermissionError("用户无读取权限")
        
        metadata = self.metadata_repository.get(metadata_id)
        if metadata:
            return {
                "id": metadata_id,
                "content": metadata["content"],
                "created_by": metadata["created_by"],
                "created_at": metadata["created_at"],
                "last_updated_by": metadata["last_updated_by"],
                "last_updated_at": metadata["last_updated_at"]
            }
        return None
    
    def search_metadata(self, query, user_info):
        """搜索元数据"""
        # 检查权限
        if not self._check_permission(user_info, "read"):
            raise PermissionError("用户无读取权限")
        
        results = []
        
        # 简化的搜索实现（实际应用中会使用更复杂的搜索引擎）
        for metadata_id, index_entry in self.search_index.items():
            if query.lower() in index_entry["indexed_text"].lower():
                metadata = self.metadata_repository.get(metadata_id)
                if metadata:
                    results.append({
                        "id": metadata_id,
                        "title": index_entry.get("title", metadata_id),
                        "content_preview": index_entry.get("preview", ""),
                        "relevance_score": self._calculate_relevance(query, index_entry)
                    })
        
        # 按相关性排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results
    
    def _check_permission(self, user_info, action):
        """检查用户权限（简化实现）"""
        user_roles = user_info.get("roles", [])
        
        # 管理员有所有权限
        if "admin" in user_roles:
            return True
        
        # 检查具体权限（实际应用中会更复杂）
        if action == "read" and ("analyst" in user_roles or "user" in user_roles):
            return True
        
        if action == "write" and ("steward" in user_roles or "admin" in user_roles):
            return True
        
        return False
    
    def _log_change(self, metadata_id, change_type, user_info, old_content, new_content):
        """记录变更日志"""
        change_log = {
            "metadata_id": metadata_id,
            "change_type": change_type,
            "user_id": user_info["user_id"],
            "timestamp": datetime.now(),
            "old_content_hash": hash(str(old_content)) if old_content else None,
            "new_content_hash": hash(str(new_content))
        }
        self.change_logs.append(change_log)
    
    def _update_search_index(self, metadata_id, metadata_content):
        """更新搜索索引"""
        # 提取可搜索文本
        searchable_text = ""
        if isinstance(metadata_content, dict):
            # 递归提取所有文本内容
            searchable_text = self._extract_text_from_dict(metadata_content)
        
        self.search_index[metadata_id] = {
            "indexed_text": searchable_text.lower(),
            "title": metadata_content.get("name", metadata_id) if isinstance(metadata_content, dict) else metadata_id,
            "preview": searchable_text[:200] + "..." if len(searchable_text) > 200 else searchable_text
        }
    
    def _extract_text_from_dict(self, dict_obj, parent_key=""):
        """从字典中提取所有文本内容"""
        text_parts = []
        
        for key, value in dict_obj.items():
            if isinstance(value, str):
                text_parts.append(f"{key}:{value}")
            elif isinstance(value, dict):
                nested_text = self._extract_text_from_dict(value, f"{parent_key}.{key}" if parent_key else key)
                text_parts.append(nested_text)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        nested_text = self._extract_text_from_dict(item, f"{parent_key}.{key}" if parent_key else key)
                        text_parts.append(nested_text)
        
        return " ".join(text_parts)
    
    def _calculate_relevance(self, query, index_entry):
        """计算相关性得分（简化实现）"""
        query_terms = query.lower().split()
        indexed_text = index_entry["indexed_text"]
        
        score = 0
        for term in query_terms:
            if term in indexed_text:
                # 简单的词频统计
                score += indexed_text.count(term) * len(term)
        
        return score

def demo_centralized_storage():
    """演示集中式元数据存储的使用"""
    print("=" * 50)
    print("3.1.1 集中式元数据存储示例")
    print("=" * 50)
    
    # 创建集中式存储系统
    storage = CentralizedMetadataStorage()
    
    # 存储表元数据
    table_metadata = {
        "name": "用户表",
        "schema": "public",
        "database": "ecommerce",
        "columns": [
            {"name": "user_id", "type": "bigint", "description": "用户唯一标识"},
            {"name": "username", "type": "varchar(50)", "description": "用户名"},
            {"name": "email", "type": "varchar(100)", "description": "电子邮箱"}
        ],
        "owner": "数据团队",
        "description": "存储用户基本信息"
    }
    
    # 模拟用户信息
    user_info = {"user_id": "admin", "roles": ["admin"]}
    
    # 存储元数据
    metadata_id = storage.store_metadata("ecommerce.public.users", table_metadata, user_info)
    print(f"已存储元数据，ID: {metadata_id}")
    
    # 检索元数据
    retrieved_metadata = storage.retrieve_metadata("ecommerce.public.users", user_info)
    print(f"检索到的元数据标题: {retrieved_metadata['content']['name']}")
    
    # 搜索元数据
    search_results = storage.search_metadata("用户", user_info)
    print(f"搜索'用户'得到 {len(search_results)} 个结果")
    
    return storage

# ===================== 分布式元数据存储 =====================

class DistributedMetadataStorage:
    """分布式元数据存储系统"""
    def __init__(self, nodes=3):
        self.nodes = [MetadataNode(i) for i in range(nodes)]  # 元数据节点
        self.directory_service = MetadataDirectory()          # 目录服务
        self.replication_factor = 2                            # 副本数量
        self.consistency_level = "eventual"                    # 一致性级别
    
    def store_metadata(self, metadata_id, metadata_content, user_info):
        """存储元数据到分布式系统"""
        # 确定存储节点
        primary_node, replica_nodes = self._determine_nodes(metadata_id)
        
        # 存储到主节点
        success = primary_node.store(metadata_id, metadata_content, user_info)
        if not success:
            raise RuntimeError("主节点存储失败")
        
        # 异步复制到副本节点
        for replica_node in replica_nodes:
            # 在实际应用中，这将是异步操作
            replica_node.store(metadata_id, metadata_content, user_info)
        
        # 更新目录服务
        self.directory_service.register_metadata(metadata_id, primary_node.id, replica_nodes)
        
        return metadata_id
    
    def retrieve_metadata(self, metadata_id, user_info):
        """从分布式系统检索元数据"""
        # 从目录服务获取节点信息
        node_info = self.directory_service.get_metadata_nodes(metadata_id)
        if not node_info:
            return None
        
        # 尝试从主节点读取
        primary_node = self.nodes[node_info["primary"]]
        metadata = primary_node.retrieve(metadata_id, user_info)
        
        if not metadata and self.consistency_level == "eventual":
            # 如果主节点读取失败，尝试从副本节点读取
            for replica_id in node_info["replicas"]:
                replica_node = self.nodes[replica_id]
                metadata = replica_node.retrieve(metadata_id, user_info)
                if metadata:
                    break
        
        return metadata
    
    def search_metadata(self, query, user_info):
        """在分布式系统中搜索元数据"""
        # 并行搜索所有节点
        all_results = []
        
        for node in self.nodes:
            try:
                results = node.search(query, user_info)
                all_results.extend(results)
            except Exception as e:
                print(f"节点 {node.id} 搜索失败: {e}")
                continue
        
        # 去重和排序
        unique_results = {}
        for result in all_results:
            result_id = result["id"]
            if result_id not in unique_results or result.get("relevance_score", 0) > unique_results[result_id].get("relevance_score", 0):
                unique_results[result_id] = result
        
        # 转换为列表并排序
        final_results = list(unique_results.values())
        final_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return final_results
    
    def _determine_nodes(self, metadata_id):
        """确定存储节点（使用一致性哈希简化实现）"""
        # 简化实现：使用哈希确定主节点
        hash_value = hash(metadata_id) % len(self.nodes)
        primary_node = self.nodes[hash_value]
        
        # 选择副本节点
        replica_nodes = []
        for i in range(1, self.replication_factor + 1):
            replica_index = (hash_value + i) % len(self.nodes)
            if replica_index != hash_value:
                replica_nodes.append(self.nodes[replica_index])
        
        return primary_node, replica_nodes

class MetadataNode:
    """元数据存储节点"""
    def __init__(self, node_id):
        self.id = node_id
        self.storage = {}  # 本地存储
        self.index = {}     # 本地索引
    
    def store(self, metadata_id, metadata_content, user_info):
        """在节点上存储元数据"""
        try:
            self.storage[metadata_id] = {
                "content": metadata_content,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "updated_by": user_info.get("user_id")
            }
            
            # 更新本地索引
            self._update_local_index(metadata_id, metadata_content)
            return True
        except Exception as e:
            print(f"节点 {self.id} 存储失败: {e}")
            return False
    
    def retrieve(self, metadata_id, user_info):
        """从节点检索元数据"""
        return self.storage.get(metadata_id)
    
    def search(self, query, user_info):
        """在节点上搜索元数据"""
        results = []
        query_lower = query.lower()
        
        for metadata_id, index_entry in self.index.items():
            if query_lower in index_entry["indexed_text"]:
                metadata = self.storage.get(metadata_id)
                if metadata:
                    results.append({
                        "id": metadata_id,
                        "title": index_entry.get("title", metadata_id),
                        "preview": index_entry.get("preview", ""),
                        "node_id": self.id,
                        "relevance_score": self._calculate_relevance(query, index_entry)
                    })
        
        return results
    
    def _update_local_index(self, metadata_id, metadata_content):
        """更新本地搜索索引"""
        # 提取可搜索文本
        searchable_text = ""
        if isinstance(metadata_content, dict):
            # 递归提取所有文本内容
            searchable_text = self._extract_text_from_dict(metadata_content)
        
        self.index[metadata_id] = {
            "indexed_text": searchable_text.lower(),
            "title": metadata_content.get("name", metadata_id) if isinstance(metadata_content, dict) else metadata_id,
            "preview": searchable_text[:200] + "..." if len(searchable_text) > 200 else searchable_text
        }
    
    def _extract_text_from_dict(self, dict_obj):
        """从字典中提取所有文本内容"""
        text_parts = []
        
        for key, value in dict_obj.items():
            if isinstance(value, str):
                text_parts.append(f"{key}:{value}")
            elif isinstance(value, dict):
                nested_text = self._extract_text_from_dict(value)
                text_parts.append(nested_text)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        nested_text = self._extract_text_from_dict(item)
                        text_parts.append(nested_text)
        
        return " ".join(text_parts)
    
    def _calculate_relevance(self, query, index_entry):
        """计算相关性得分"""
        query_terms = query.lower().split()
        indexed_text = index_entry["indexed_text"]
        
        score = 0
        for term in query_terms:
            if term in indexed_text:
                score += indexed_text.count(term) * len(term)
        
        return score

class MetadataDirectory:
    """元数据目录服务"""
    def __init__(self):
        self.directory = {}  # 元数据位置目录
    
    def register_metadata(self, metadata_id, primary_node_id, replica_nodes):
        """注册元数据位置"""
        self.directory[metadata_id] = {
            "primary": primary_node_id,
            "replicas": [node.id for node in replica_nodes]
        }
    
    def get_metadata_nodes(self, metadata_id):
        """获取元数据所在节点"""
        return self.directory.get(metadata_id)

def demo_distributed_storage():
    """演示分布式元数据存储的使用"""
    print("\n" + "=" * 50)
    print("3.1.1 分布式元数据存储示例")
    print("=" * 50)
    
    # 创建分布式存储系统（3个节点）
    storage = DistributedMetadataStorage(nodes=3)
    
    # 存储表元数据
    table_metadata = {
        "name": "订单表",
        "schema": "public",
        "database": "ecommerce",
        "columns": [
            {"name": "order_id", "type": "bigint", "description": "订单唯一标识"},
            {"name": "user_id", "type": "bigint", "description": "用户ID"},
            {"name": "amount", "type": "decimal(10,2)", "description": "订单金额"}
        ],
        "owner": "数据团队",
        "description": "存储订单信息"
    }
    
    # 模拟用户信息
    user_info = {"user_id": "admin", "roles": ["admin"]}
    
    # 存储元数据
    metadata_id = storage.store_metadata("ecommerce.public.orders", table_metadata, user_info)
    print(f"已存储元数据到分布式系统，ID: {metadata_id}")
    
    # 检索元数据
    retrieved_metadata = storage.retrieve_metadata("ecommerce.public.orders", user_info)
    print(f"检索到的元数据标题: {retrieved_metadata['content']['name']}")
    
    # 搜索元数据
    search_results = storage.search_metadata("订单", user_info)
    print(f"搜索'订单'得到 {len(search_results)} 个结果")
    
    return storage

# ===================== 混合式元数据存储 =====================

class HybridMetadataStorage:
    """混合式元数据存储系统"""
    def __init__(self):
        self.central_storage = CentralizedMetadataStorage()     # 集中式存储
        self.distributed_storage = DistributedMetadataStorage() # 分布式存储
        self.storage_rules = {}                                   # 存储规则
    
    def configure_storage_rules(self, rules_config):
        """配置存储规则"""
        self.storage_rules = rules_config
    
    def store_metadata(self, metadata_id, metadata_content, user_info, storage_type=None):
        """存储元数据（根据规则自动选择存储类型）"""
        # 如果未指定存储类型，根据规则确定
        if not storage_type:
            storage_type = self._determine_storage_type(metadata_id, metadata_content)
        
        # 根据存储类型选择存储系统
        if storage_type == "centralized":
            return self.central_storage.store_metadata(metadata_id, metadata_content, user_info)
        elif storage_type == "distributed":
            return self.distributed_storage.store_metadata(metadata_id, metadata_content, user_info)
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")
    
    def retrieve_metadata(self, metadata_id, user_info):
        """检索元数据（自动查找存储位置）"""
        # 先尝试集中式存储
        try:
            user_info["roles"] = ["admin"]  # 临时添加权限
            metadata = self.central_storage.retrieve_metadata(metadata_id, user_info)
            if metadata:
                return metadata
        except:
            pass
        
        # 再尝试分布式存储
        try:
            metadata = self.distributed_storage.retrieve_metadata(metadata_id, user_info)
            if metadata:
                return metadata
        except:
            pass
        
        return None
    
    def search_metadata(self, query, user_info):
        """搜索元数据（同时搜索两个存储系统）"""
        central_results = []
        distributed_results = []
        
        # 搜索集中式存储
        try:
            user_info["roles"] = ["admin"]  # 临时添加权限
            central_results = self.central_storage.search_metadata(query, user_info)
        except:
            pass
        
        # 搜索分布式存储
        try:
            distributed_results = self.distributed_storage.search_metadata(query, user_info)
        except:
            pass
        
        # 合并结果
        all_results = central_results + distributed_results
        
        # 去重
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        # 排序
        unique_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return unique_results
    
    def _determine_storage_type(self, metadata_id, metadata_content):
        """根据规则确定存储类型"""
        # 检查显式规则
        for pattern, storage_type in self.storage_rules.get("patterns", {}).items():
            if pattern in metadata_id:
                return storage_type
        
        # 检查内容类型规则
        if isinstance(metadata_content, dict):
            content_type = metadata_content.get("type")
            if content_type in self.storage_rules.get("content_types", {}):
                return self.storage_rules["content_types"][content_type]
        
        # 检查大小规则
        content_size = len(str(metadata_content))
        size_thresholds = self.storage_rules.get("size_thresholds", {})
        for threshold, storage_type in sorted(size_thresholds.items(), key=lambda x: int(x[0]), reverse=True):
            if content_size >= int(threshold):
                return storage_type
        
        # 默认存储类型
        return self.storage_rules.get("default", "centralized")

def demo_hybrid_storage():
    """演示混合式元数据存储的使用"""
    print("\n" + "=" * 50)
    print("3.1.2 混合式元数据存储示例")
    print("=" * 50)
    
    # 创建混合式存储系统
    storage = HybridMetadataStorage()
    
    # 配置存储规则
    storage.configure_storage_rules({
        "patterns": {
            "critical_": "centralized",  # 关键数据存集中式
            "user_profile": "distributed"  # 用户画像数据存分布式
        },
        "content_types": {
            "schema": "centralized",      # 模式定义存集中式
            "statistics": "distributed"    # 统计数据存分布式
        },
        "size_thresholds": {
            "10000": "distributed",       # 大于10KB存分布式
            "1000": "centralized"         # 大于1KB小于10KB存集中式
        },
        "default": "centralized"
    })
    
    # 模拟用户信息
    user_info = {"user_id": "admin"}
    
    # 存储不同类型的元数据
    # 1. 关键配置（根据模式规则存储到集中式）
    critical_config = {
        "type": "configuration",
        "description": "关键系统配置"
    }
    storage.store_metadata("critical_system_config", critical_config, user_info)
    
    # 2. 用户画像数据（根据模式规则存储到分布式）
    user_profile = {
        "type": "profile",
        "user_count": 1000000,
        "attributes": ["age", "gender", "location"]
    }
    storage.store_metadata("user_profile_2023", user_profile, user_info)
    
    # 3. 表模式（根据内容类型规则存储到集中式）
    table_schema = {
        "type": "schema",
        "tables": ["users", "orders", "products"]
    }
    storage.store_metadata("ecommerce_schema", table_schema, user_info)
    
    # 4. 大数据量统计（根据大小阈值规则存储到分布式）
    large_stats = "x" * 15000  # 15KB数据
    storage.store_metadata("large_statistics", large_stats, user_info)
    
    print("已存储不同类型的元数据到混合存储系统")
    
    # 搜索元数据
    search_results = storage.search_metadata("用户", user_info)
    print(f"搜索'用户'得到 {len(search_results)} 个结果")
    
    return storage

# ===================== 3.2.1 关系型元数据模型 =====================

class RelationalMetadataModel:
    """关系型元数据模型"""
    def __init__(self):
        self.db_connection = self._init_database()
        self._create_tables()
    
    def _init_database(self):
        """初始化数据库连接（简化实现）"""
        # 在实际应用中，这里会是真实的数据库连接
        return {
            "databases": {},
            "schemas": {},
            "tables": {},
            "columns": {},
            "relationships": {}
        }
    
    def _create_tables(self):
        """创建元数据表结构"""
        # 表元数据表
        self.db_connection["tables_metadata"] = {
            "structure": {
                "table_id": "PRIMARY_KEY",
                "database_name": "VARCHAR(100)",
                "schema_name": "VARCHAR(100)",
                "table_name": "VARCHAR(100)",
                "table_type": "VARCHAR(20)",
                "description": "TEXT",
                "owner": "VARCHAR(100)",
                "created_at": "DATETIME",
                "updated_at": "DATETIME"
            }
        }
        
        # 列元数据表
        self.db_connection["columns_metadata"] = {
            "structure": {
                "column_id": "PRIMARY_KEY",
                "table_id": "FOREIGN_KEY",
                "column_name": "VARCHAR(100)",
                "data_type": "VARCHAR(50)",
                "length": "INTEGER",
                "nullable": "BOOLEAN",
                "default_value": "VARCHAR(255)",
                "description": "TEXT",
                "ordinal_position": "INTEGER",
                "created_at": "DATETIME",
                "updated_at": "DATETIME"
            }
        }
        
        # 关系元数据表
        self.db_connection["relationships_metadata"] = {
            "structure": {
                "relationship_id": "PRIMARY_KEY",
                "from_table": "VARCHAR(255)",
                "to_table": "VARCHAR(255)",
                "from_columns": "VARCHAR(255)",
                "to_columns": "VARCHAR(255)",
                "relationship_type": "VARCHAR(20)",
                "description": "TEXT",
                "created_at": "DATETIME",
                "updated_at": "DATETIME"
            }
        }
    
    def save_table_metadata(self, table_info):
        """保存表元数据"""
        table_id = f"{table_info['database']}.{table_info['schema']}.{table_info['name']}"
        
        # 保存表信息
        self.db_connection["tables"][table_id] = {
            "table_id": table_id,
            "database_name": table_info["database"],
            "schema_name": table_info["schema"],
            "table_name": table_info["name"],
            "table_type": table_info.get("type", "TABLE"),
            "description": table_info.get("description"),
            "owner": table_info.get("owner"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 保存列信息
        for i, column in enumerate(table_info.get("columns", [])):
            column_id = f"{table_id}.{column['name']}"
            self.db_connection["columns"][column_id] = {
                "column_id": column_id,
                "table_id": table_id,
                "column_name": column["name"],
                "data_type": column["type"],
                "length": column.get("length"),
                "nullable": column.get("nullable", True),
                "default_value": column.get("default_value"),
                "description": column.get("description"),
                "ordinal_position": i + 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        
        return table_id
    
    def save_relationship_metadata(self, relationship_info):
        """保存关系元数据"""
        rel_id = f"{relationship_info['from_table']}_to_{relationship_info['to_table']}"
        
        self.db_connection["relationships"][rel_id] = {
            "relationship_id": rel_id,
            "from_table": relationship_info["from_table"],
            "to_table": relationship_info["to_table"],
            "from_columns": ",".join(relationship_info["from_columns"]),
            "to_columns": ",".join(relationship_info["to_columns"]),
            "relationship_type": relationship_info["type"],
            "description": relationship_info.get("description"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return rel_id
    
    def get_table_metadata(self, table_id):
        """获取表元数据"""
        # 获取表信息
        table_info = self.db_connection["tables"].get(table_id)
        if not table_info:
            return None
        
        # 获取列信息
        columns = []
        for col_id, col_info in self.db_connection["columns"].items():
            if col_info["table_id"] == table_id:
                columns.append({
                    "name": col_info["column_name"],
                    "type": col_info["data_type"],
                    "length": col_info["length"],
                    "nullable": col_info["nullable"],
                    "default_value": col_info["default_value"],
                    "description": col_info["description"],
                    "ordinal_position": col_info["ordinal_position"]
                })
        
        # 按位置排序列
        columns.sort(key=lambda x: x["ordinal_position"])
        
        return {
            "table_id": table_id,
            "database": table_info["database_name"],
            "schema": table_info["schema_name"],
            "name": table_info["table_name"],
            "type": table_info["table_type"],
            "description": table_info["description"],
            "owner": table_info["owner"],
            "columns": columns,
            "created_at": table_info["created_at"],
            "updated_at": table_info["updated_at"]
        }
    
    def get_relationships(self, table_id=None):
        """获取关系元数据"""
        relationships = []
        
        for rel_id, rel_info in self.db_connection["relationships"].items():
            if table_id and table_id not in [rel_info["from_table"], rel_info["to_table"]]:
                continue
            
            relationships.append({
                "relationship_id": rel_id,
                "from_table": rel_info["from_table"],
                "to_table": rel_info["to_table"],
                "from_columns": rel_info["from_columns"].split(","),
                "to_columns": rel_info["to_columns"].split(","),
                "type": rel_info["relationship_type"],
                "description": rel_info["description"]
            })
        
        return relationships
    
    def query_metadata(self, query_type, params=None):
        """查询元数据"""
        if query_type == "tables_by_database":
            database_name = params.get("database")
            tables = []
            
            for table_id, table_info in self.db_connection["tables"].items():
                if table_info["database_name"] == database_name:
                    tables.append({
                        "table_id": table_id,
                        "name": table_info["table_name"],
                        "schema": table_info["schema_name"],
                        "description": table_info["description"]
                    })
            
            return tables
        
        elif query_type == "columns_by_table":
            table_id = params.get("table_id")
            columns = []
            
            for col_id, col_info in self.db_connection["columns"].items():
                if col_info["table_id"] == table_id:
                    columns.append({
                        "column_id": col_id,
                        "name": col_info["column_name"],
                        "type": col_info["data_type"],
                        "description": col_info["description"]
                    })
            
            # 按位置排序
            columns.sort(key=lambda x: int(x["column_id"].split(".")[-1]))
            return columns
        
        return []

def demo_relational_model():
    """演示关系型元数据模型的使用"""
    print("\n" + "=" * 50)
    print("3.2.1 关系型元数据模型示例")
    print("=" * 50)
    
    # 创建关系型元数据模型
    model = RelationalMetadataModel()
    
    # 定义用户表
    users_table = {
        "database": "ecommerce",
        "schema": "public",
        "name": "users",
        "type": "TABLE",
        "description": "用户基本信息表",
        "owner": "数据团队",
        "columns": [
            {
                "name": "user_id",
                "type": "BIGINT",
                "length": None,
                "nullable": False,
                "description": "用户唯一标识"
            },
            {
                "name": "username",
                "type": "VARCHAR",
                "length": 50,
                "nullable": False,
                "description": "用户名"
            },
            {
                "name": "email",
                "type": "VARCHAR",
                "length": 100,
                "nullable": False,
                "description": "电子邮箱"
            },
            {
                "name": "created_at",
                "type": "TIMESTAMP",
                "length": None,
                "nullable": False,
                "description": "创建时间"
            }
        ]
    }
    
    # 定义订单表
    orders_table = {
        "database": "ecommerce",
        "schema": "public",
        "name": "orders",
        "type": "TABLE",
        "description": "订单信息表",
        "owner": "数据团队",
        "columns": [
            {
                "name": "order_id",
                "type": "BIGINT",
                "length": None,
                "nullable": False,
                "description": "订单唯一标识"
            },
            {
                "name": "user_id",
                "type": "BIGINT",
                "length": None,
                "nullable": False,
                "description": "用户ID"
            },
            {
                "name": "order_amount",
                "type": "DECIMAL",
                "length": 10,
                "nullable": False,
                "description": "订单金额"
            },
            {
                "name": "order_date",
                "type": "DATE",
                "length": None,
                "nullable": False,
                "description": "订单日期"
            }
        ]
    }
    
    # 保存表元数据
    users_id = model.save_table_metadata(users_table)
    orders_id = model.save_table_metadata(orders_table)
    
    print(f"已保存用户表: {users_id}")
    print(f"已保存订单表: {orders_id}")
    
    # 定义表关系
    user_order_rel = {
        "from_table": users_id,
        "to_table": orders_id,
        "from_columns": ["user_id"],
        "to_columns": ["user_id"],
        "type": "ONE_TO_MANY",
        "description": "一个用户可以有多个订单"
    }
    
    rel_id = model.save_relationship_metadata(user_order_rel)
    print(f"已保存表关系: {rel_id}")
    
    # 查询元数据
    tables = model.query_metadata("tables_by_database", {"database": "ecommerce"})
    print(f"\necommerce数据库中的表数量: {len(tables)}")
    
    # 获取表详情
    table_detail = model.get_table_metadata(users_id)
    print(f"\n用户表详情:")
    print(f"  表名: {table_detail['name']}")
    print(f"  描述: {table_detail['description']}")
    print(f"  列数: {len(table_detail['columns'])}")
    
    # 获取关系
    relationships = model.get_relationships(users_id)
    print(f"\n用户表的关系数量: {len(relationships)}")
    
    return model

# ===================== 3.2.2 图形元数据模型 =====================

class GraphMetadataModel:
    """图形元数据模型"""
    def __init__(self):
        self.nodes = {}      # 节点存储
        self.edges = {}      # 边存储
        self.indexes = {}    # 索引存储
    
    def create_node(self, node_type, node_id, properties=None):
        """创建节点"""
        if node_id in self.nodes:
            raise ValueError(f"节点 {node_id} 已存在")
        
        node = {
            "id": node_id,
            "type": node_type,
            "properties": properties or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.nodes[node_id] = node
        
        # 更新索引
        self._update_indexes(node)
        
        return node
    
    def create_edge(self, edge_type, from_node, to_node, properties=None):
        """创建边（关系）"""
        edge_id = f"{from_node}->{to_node}"
        
        if edge_id in self.edges:
            raise ValueError(f"边 {edge_id} 已存在")
        
        edge = {
            "id": edge_id,
            "type": edge_type,
            "from": from_node,
            "to": to_node,
            "properties": properties or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        self.edges[edge_id] = edge
        
        return edge
    
    def update_node(self, node_id, properties):
        """更新节点"""
        if node_id not in self.nodes:
            raise ValueError(f"节点 {node_id} 不存在")
        
        node = self.nodes[node_id]
        node["properties"].update(properties)
        node["updated_at"] = datetime.now()
        
        # 更新索引
        self._update_indexes(node)
        
        return node
    
    def update_edge(self, from_node, to_node, properties):
        """更新边"""
        edge_id = f"{from_node}->{to_node}"
        
        if edge_id not in self.edges:
            raise ValueError(f"边 {edge_id} 不存在")
        
        edge = self.edges[edge_id]
        edge["properties"].update(properties)
        edge["updated_at"] = datetime.now()
        
        return edge
    
    def get_node(self, node_id):
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_edge(self, from_node, to_node):
        """获取边"""
        edge_id = f"{from_node}->{to_node}"
        return self.edges.get(edge_id)
    
    def query_nodes(self, node_type=None, properties=None):
        """查询节点"""
        results = []
        
        for node_id, node in self.nodes.items():
            match = True
            
            # 检查节点类型
            if node_type and node["type"] != node_type:
                match = False
                continue
            
            # 检查属性
            if properties:
                for key, value in properties.items():
                    if key not in node["properties"] or node["properties"][key] != value:
                        match = False
                        break
            
            if match:
                results.append(node)
        
        return results
    
    def find_paths(self, from_node, to_node, max_depth=3, path_type=None):
        """查找路径（血缘分析）"""
        if from_node not in self.nodes or to_node not in self.nodes:
            return []
        
        paths = []
        visited = set()
        
        def dfs(current, target, path, depth):
            if depth > max_depth:
                return
            
            if current == target:
                paths.append(path.copy())
                return
            
            visited.add(current)
            
            # 查找所有出边
            for edge_id, edge in self.edges.items():
                if edge["from"] == current:
                    next_node = edge["to"]
                    
                    # 检查路径类型
                    if path_type and edge["type"] != path_type:
                        continue
                    
                    if next_node not in visited:
                        path.append(edge)
                        dfs(next_node, target, path, depth + 1)
                        path.pop()
            
            visited.remove(current)
        
        dfs(from_node, to_node, [], 0)
        return paths
    
    def get_neighbors(self, node_id, direction="outgoing", edge_type=None):
        """获取邻居节点"""
        if node_id not in self.nodes:
            return []
        
        neighbors = []
        
        for edge_id, edge in self.edges.items():
            if edge_type and edge["type"] != edge_type:
                continue
            
            if direction == "outgoing" and edge["from"] == node_id:
                neighbors.append({
                    "node": self.nodes.get(edge["to"]),
                    "edge": edge
                })
            elif direction == "incoming" and edge["to"] == node_id:
                neighbors.append({
                    "node": self.nodes.get(edge["from"]),
                    "edge": edge
                })
        
        return neighbors
    
    def get_subgraph(self, center_node, depth=1):
        """获取子图"""
        if center_node not in self.nodes:
            return {"nodes": [], "edges": []}
        
        # 广度优先遍历
        visited_nodes = set([center_node])
        visited_edges = set()
        queue = [(center_node, 0)]
        
        while queue:
            current, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            # 获取所有邻居
            neighbors = self.get_neighbors(current)
            
            for neighbor_info in neighbors:
                neighbor_node = neighbor_info["node"]
                edge = neighbor_info["edge"]
                
                if neighbor_node:
                    neighbor_id = neighbor_node["id"]
                    
                    if neighbor_id not in visited_nodes:
                        visited_nodes.add(neighbor_id)
                        queue.append((neighbor_id, current_depth + 1))
                    
                    visited_edges.add(edge["id"])
        
        # 构建子图
        subgraph_nodes = [self.nodes[node_id] for node_id in visited_nodes]
        subgraph_edges = [self.edges[edge_id] for edge_id in visited_edges]
        
        return {
            "nodes": subgraph_nodes,
            "edges": subgraph_edges
        }
    
    def _update_indexes(self, node):
        """更新索引"""
        node_type = node["type"]
        
        if node_type not in self.indexes:
            self.indexes[node_type] = {}
        
        # 基于属性的简单索引
        for key, value in node["properties"].items():
            if key not in self.indexes[node_type]:
                self.indexes[node_type][key] = {}
            
            if value not in self.indexes[node_type][key]:
                self.indexes[node_type][key][value] = []
            
            if node["id"] not in self.indexes[node_type][key][value]:
                self.indexes[node_type][key][value].append(node["id"])
    
    def export_to_json(self):
        """导出为JSON格式"""
        return {
            "nodes": list(self.nodes.values()),
            "edges": list(self.edges.values())
        }
    
    def import_from_json(self, graph_data):
        """从JSON导入"""
        # 导入节点
        for node_data in graph_data.get("nodes", []):
            self.nodes[node_data["id"]] = node_data
            self._update_indexes(node_data)
        
        # 导入边
        for edge_data in graph_data.get("edges", []):
            self.edges[edge_data["id"]] = edge_data

def demo_graph_model():
    """演示图形元数据模型的使用"""
    print("\n" + "=" * 50)
    print("3.2.2 图形元数据模型示例")
    print("=" * 50)
    
    # 创建图形元数据模型
    model = GraphMetadataModel()
    
    # 创建数据源节点
    raw_db = model.create_node("Database", "mysql_raw", {
        "name": "MySQL原始数据库",
        "host": "raw-db.example.com",
        "type": "MySQL",
        "environment": "production"
    })
    
    # 创建数据表节点
    raw_users = model.create_node("Table", "raw_users", {
        "name": "用户原始表",
        "database": "mysql_raw",
        "row_count": 1000000
    })
    
    raw_orders = model.create_node("Table", "raw_orders", {
        "name": "订单原始表",
        "database": "mysql_raw",
        "row_count": 2000000
    })
    
    # 创建数据仓库节点
    dw = model.create_node("Database", "datawarehouse", {
        "name": "数据仓库",
        "type": "PostgreSQL",
        "environment": "production"
    })
    
    # 创建DW表节点
    dw_users = model.create_node("Table", "dw_users", {
        "name": "用户维度表",
        "database": "datawarehouse",
        "row_count": 950000,
        "refresh_frequency": "每日"
    })
    
    dw_orders = model.create_node("Table", "dw_orders", {
        "name": "订单事实表",
        "database": "datawarehouse",
        "row_count": 1900000,
        "refresh_frequency": "每日"
    })
    
    # 创建应用节点
    analytics = model.create_node("Application", "bi_analytics", {
        "name": "BI分析平台",
        "type": "Tableau",
        "owner": "数据分析团队"
    })
    
    # 创建数据报表节点
    sales_report = model.create_node("Report", "sales_dashboard", {
        "name": "销售仪表板",
        "application": "bi_analytics",
        "owner": "业务分析团队"
    })
    
    # 创建关系（边）
    model.create_edge("contains", "mysql_raw", "raw_users", {"created_at": "2023-01-01"})
    model.create_edge("contains", "mysql_raw", "raw_orders", {"created_at": "2023-01-01"})
    
    model.create_edge("contains", "datawarehouse", "dw_users", {"created_at": "2023-02-01"})
    model.create_edge("contains", "datawarehouse", "dw_orders", {"created_at": "2023-02-01"})
    
    model.create_edge("uses", "bi_analytics", "dw_users", {"created_at": "2023-03-01"})
    model.create_edge("uses", "bi_analytics", "dw_orders", {"created_at": "2023-03-01"})
    
    model.create_edge("contains", "bi_analytics", "sales_dashboard", {"created_at": "2023-04-01"})
    
    # 创建数据血缘关系
    model.create_edge("derived_from", "dw_users", "raw_users", {
        "transformation": "清洗和标准化",
        "etl_job": "user_etl",
        "schedule": "每日2:00"
    })
    
    model.create_edge("derived_from", "dw_orders", "raw_orders", {
        "transformation": "清洗和聚合",
        "etl_job": "order_etl",
        "schedule": "每日2:30"
    })
    
    # 查询节点
    tables = model.query_nodes("Table")
    print(f"数据表数量: {len(tables)}")
    
    # 查找数据血缘
    paths = model.find_paths("raw_users", "sales_dashboard", max_depth=4, path_type="derived_from")
    print(f"\n从原始用户表到销售报表的数据血缘路径数量: {len(paths)}")
    
    # 获取邻居节点
    dw_neighbors = model.get_neighbors("datawarehouse", direction="outgoing")
    print(f"\n数据仓库的下游节点数量: {len(dw_neighbors)}")
    
    # 获取子图
    subgraph = model.get_subgraph("dw_users", depth=2)
    print(f"\n以用户维度表为中心的子图包含:")
    print(f"  节点数: {len(subgraph['nodes'])}")
    print(f"  边数: {len(subgraph['edges'])}")
    
    return model

# ===================== 3.2.3 文档型元数据模型 =====================

class DocumentMetadataModel:
    """文档型元数据模型"""
    def __init__(self):
        self.collections = {}    # 集合存储
        self.indexes = {}        # 索引存储
        self._init_default_collections()
    
    def _init_default_collections(self):
        """初始化默认集合"""
        self.collections = {
            "datasets": {},
            "schemas": {},
            "processes": {},
            "quality_metrics": {}
        }
    
    def create_document(self, collection, document_id, document):
        """创建文档"""
        if collection not in self.collections:
            self.collections[collection] = {}
        
        if document_id in self.collections[collection]:
            raise ValueError(f"文档 {document_id} 已存在于集合 {collection} 中")
        
        # 添加元数据
        document["_id"] = document_id
        document["_created_at"] = datetime.now()
        document["_updated_at"] = datetime.now()
        
        # 存储文档
        self.collections[collection][document_id] = document
        
        # 更新索引
        self._update_indexes(collection, document_id, document)
        
        return document
    
    def update_document(self, collection, document_id, updates):
        """更新文档"""
        if collection not in self.collections or document_id not in self.collections[collection]:
            raise ValueError(f"文档 {document_id} 不存在于集合 {collection} 中")
        
        document = self.collections[collection][document_id]
        
        # 更新字段
        for key, value in updates.items():
            if key.startswith("_"):
                continue  # 跳过系统字段
            document[key] = value
        
        # 更新时间戳
        document["_updated_at"] = datetime.now()
        
        # 更新索引
        self._update_indexes(collection, document_id, document)
        
        return document
    
    def get_document(self, collection, document_id):
        """获取文档"""
        if collection not in self.collections:
            return None
        return self.collections[collection].get(document_id)
    
    def delete_document(self, collection, document_id):
        """删除文档"""
        if collection not in self.collections or document_id not in self.collections[collection]:
            return False
        
        document = self.collections[collection][document_id]
        
        # 删除索引
        self._remove_from_indexes(collection, document_id, document)
        
        # 删除文档
        del self.collections[collection][document_id]
        return True
    
    def query_documents(self, collection, query=None, limit=None, sort=None):
        """查询文档"""
        if collection not in self.collections:
            return []
        
        results = []
        
        for doc_id, document in self.collections[collection].items():
            # 如果没有查询条件，返回所有文档
            if not query:
                results.append(document)
                continue
            
            # 检查查询条件
            if self._match_query(document, query):
                results.append(document)
        
        # 排序
        if sort:
            results = self._sort_documents(results, sort)
        
        # 限制结果数量
        if limit and limit > 0:
            results = results[:limit]
        
        return results
    
    def aggregate_documents(self, collection, pipeline):
        """聚合文档（简化实现）"""
        if collection not in self.collections:
            return []
        
        documents = list(self.collections[collection].values())
        
        # 简化的管道处理
        for stage in pipeline:
            stage_type = stage.get("$type")
            
            if stage_type == "match":
                documents = [doc for doc in documents if self._match_query(doc, stage.get("query", {}))]
            
            elif stage_type == "group":
                group_key = stage.get("_id")
                groups = {}
                
                for doc in documents:
                    # 计算分组键
                    if isinstance(group_key, str) and group_key.startswith("$"):
                        key_value = doc.get(group_key[1:], "null")
                    else:
                        key_value = "null"
                    
                    if key_value not in groups:
                        groups[key_value] = []
                    
                    groups[key_value].append(doc)
                
                # 应用聚合函数
                documents = []
                for key, docs in groups.items():
                    result = {"_id": key}
                    
                    for field, func in stage.get("fields", {}).items():
                        if func == "$sum":
                            values = [doc.get(field, 0) for doc in docs]
                            result[field] = sum(values)
                        elif func == "$avg":
                            values = [doc.get(field, 0) for doc in docs if isinstance(doc.get(field, 0), (int, float))]
                            result[field] = sum(values) / len(values) if values else 0
                        elif func == "$count":
                            result[field] = len(docs)
                    
                    documents.append(result)
            
            elif stage_type == "sort":
                documents = self._sort_documents(documents, stage.get("sort", {}))
        
        return documents
    
    def create_index(self, collection, index_spec):
        """创建索引"""
        if collection not in self.indexes:
            self.indexes[collection] = {}
        
        index_name = "_".join([f"{k}_{v}" for k, v in index_spec.items()])
        
        self.indexes[collection][index_name] = {
            "fields": index_spec,
            "entries": {}
        }
        
        # 为现有文档构建索引
        for doc_id, document in self.collections[collection].items():
            self._add_to_index(collection, index_name, doc_id, document)
        
        return index_name
    
    def _match_query(self, document, query):
        """检查文档是否匹配查询条件"""
        for key, condition in query.items():
            if key.startswith("$"):
                continue
            
            document_value = document.get(key)
            
            if isinstance(condition, dict):
                # 处理操作符
                for op, value in condition.items():
                    if op == "$eq" and document_value != value:
                        return False
                    elif op == "$ne" and document_value == value:
                        return False
                    elif op == "$in" and document_value not in value:
                        return False
                    elif op == "$nin" and document_value in value:
                        return False
                    elif op == "$gt" and document_value <= value:
                        return False
                    elif op == "$gte" and document_value < value:
                        return False
                    elif op == "$lt" and document_value >= value:
                        return False
                    elif op == "$lte" and document_value > value:
                        return False
            else:
                # 简单相等
                if document_value != condition:
                    return False
        
        return True
    
    def _sort_documents(self, documents, sort_spec):
        """排序文档"""
        if not sort_spec:
            return documents
        
        def sort_key(doc):
            keys = []
            for field, direction in sort_spec.items():
                value = doc.get(field)
                keys.append((value, direction))
            return keys
        
        return sorted(documents, key=sort_key)
    
    def _update_indexes(self, collection, document_id, document):
        """更新索引"""
        if collection not in self.indexes:
            return
        
        for index_name, index_info in self.indexes[collection].items():
            self._add_to_index(collection, index_name, document_id, document)
    
    def _add_to_index(self, collection, index_name, document_id, document):
        """添加文档到索引"""
        if collection not in self.indexes or index_name not in self.indexes[collection]:
            return
        
        index_info = self.indexes[collection][index_name]
        index_entries = index_info["entries"]
        
        # 计算索引键
        index_key_parts = []
        for field in index_info["fields"].keys():
            index_key_parts.append(str(document.get(field, "")))
        
        index_key = "_".join(index_key_parts)
        
        # 添加到索引
        if index_key not in index_entries:
            index_entries[index_key] = []
        
        if document_id not in index_entries[index_key]:
            index_entries[index_key].append(document_id)
    
    def _remove_from_indexes(self, collection, document_id, document):
        """从索引中移除文档"""
        if collection not in self.indexes:
            return
        
        for index_name, index_info in self.indexes[collection].items():
            index_entries = index_info["entries"]
            
            # 计算索引键
            index_key_parts = []
            for field in index_info["fields"].keys():
                index_key_parts.append(str(document.get(field, "")))
            
            index_key = "_".join(index_key_parts)
            
            # 从索引中移除
            if index_key in index_entries and document_id in index_entries[index_key]:
                index_entries[index_key].remove(document_id)
                
                # 如果索引条目为空，删除它
                if not index_entries[index_key]:
                    del index_entries[index_key]

def demo_document_model():
    """演示文档型元数据模型的使用"""
    print("\n" + "=" * 50)
    print("3.2.3 文档型元数据模型示例")
    print("=" * 50)
    
    # 创建文档型元数据模型
    model = DocumentMetadataModel()
    
    # 创建数据集文档
    user_profile_dataset = {
        "name": "用户画像数据集",
        "type": "table",
        "database": "user_db",
        "schema": "analytics",
        "table": "user_profile",
        "description": "包含用户基本信息和行为数据的综合画像",
        "owner": "数据分析团队",
        "tags": ["用户", "画像", "行为"],
        "statistics": {
            "row_count": 10000000,
            "last_updated": "2023-11-27",
            "size_gb": 5.2
        },
        "columns": [
            {"name": "user_id", "type": "bigint", "description": "用户ID"},
            {"name": "age", "type": "integer", "description": "年龄"},
            {"name": "gender", "type": "varchar", "description": "性别"},
            {"name": "city", "type": "varchar", "description": "城市"}
        ]
    }
    
    model.create_document("datasets", "user_profile", user_profile_dataset)
    
    # 创建另一个数据集文档
    order_summary_dataset = {
        "name": "订单汇总数据集",
        "type": "table",
        "database": "order_db",
        "schema": "analytics",
        "table": "order_summary",
        "description": "订单数据的汇总统计信息",
        "owner": "业务运营团队",
        "tags": ["订单", "汇总", "业务"],
        "statistics": {
            "row_count": 5000000,
            "last_updated": "2023-11-27",
            "size_gb": 3.8
        },
        "columns": [
            {"name": "order_id", "type": "bigint", "description": "订单ID"},
            {"name": "user_id", "type": "bigint", "description": "用户ID"},
            {"name": "amount", "type": "decimal", "description": "订单金额"}
        ]
    }
    
    model.create_document("datasets", "order_summary", order_summary_dataset)
    
    # 创建处理流程文档
    etl_process = {
        "name": "用户画像ETL流程",
        "type": "batch_processing",
        "schedule": "每日3:00",
        "description": "从原始数据提取、转换和加载用户画像数据",
        "owner": "数据工程团队",
        "steps": [
            {
                "name": "数据抽取",
                "type": "extract",
                "source": "mysql_raw.users",
                "script": "extract_users.py"
            },
            {
                "name": "数据转换",
                "type": "transform",
                "script": "transform_users.py",
                "rules": ["标准化", "去重", "验证"]
            },
            {
                "name": "数据加载",
                "type": "load",
                "target": "user_db.analytics.user_profile",
                "script": "load_users.py"
            }
        ],
        "dependencies": ["原始用户数据"],
        "outputs": ["用户画像数据集"]
    }
    
    model.create_document("processes", "user_profile_etl", etl_process)
    
    # 创建质量指标文档
    quality_metrics = {
        "dataset_id": "user_profile",
        "check_date": "2023-11-27",
        "dimensions": {
            "completeness": 0.98,
            "accuracy": 0.95,
            "consistency": 0.97,
            "timeliness": 0.99
        },
        "overall_score": 0.97,
        "issues": [
            {
                "type": "completeness",
                "description": "部分用户年龄字段缺失",
                "severity": "medium",
                "affected_records": 25000
            }
        ]
    }
    
    model.create_document("quality_metrics", "user_profile_20231127", quality_metrics)
    
    # 查询文档
    all_datasets = model.query_documents("datasets")
    print(f"数据集文档数量: {len(all_datasets)}")
    
    # 条件查询
    user_datasets = model.query_documents("datasets", {
        "owner": "数据分析团队"
    })
    print(f"数据分析团队拥有的数据集数量: {len(user_datasets)}")
    
    # 创建索引
    index_name = model.create_index("datasets", {"owner": 1, "type": 1})
    print(f"\n已创建索引: {index_name}")
    
    # 聚合查询
    pipeline = [
        {"$type": "match", "query": {"type": "table"}},
        {"$type": "group", "_id": "$owner", "count": {"$count": 1}}
    ]
    
    aggregation_result = model.aggregate_documents("datasets", pipeline)
    print(f"\n按所有者分组的数据集统计:")
    for result in aggregation_result:
        print(f"  {result['_id']}: {result['count']} 个数据集")
    
    return model

# ===================== 3.3.1 元数据存储优化 =====================

# ===================== 索引优化 =====================

class MetadataIndexOptimizer:
    """元数据索引优化器"""
    def __init__(self):
        self.storage = None  # 关联的存储系统
        self.indexes = {}    # 索引配置
        self.usage_stats = {}  # 使用统计
    
    def register_storage(self, storage):
        """注册存储系统"""
        self.storage = storage
    
    def create_index(self, index_name, index_config):
        """创建索引"""
        self.indexes[index_name] = {
            "name": index_name,
            "fields": index_config["fields"],
            "type": index_config.get("type", "btree"),  # btree, hash, fulltext
            "unique": index_config.get("unique", False),
            "partial_filter": index_config.get("partial_filter"),
            "created_at": datetime.now()
        }
        
        # 初始化使用统计
        self.usage_stats[index_name] = {
            "queries": 0,
            "last_used": None,
            "efficiency": 0.0
        }
        
        return index_name
    
    def analyze_query_patterns(self, query_log):
        """分析查询模式以推荐索引"""
        field_usage = {}
        pattern_frequency = {}
        
        for query in query_log:
            # 分析查询中使用的字段
            query_fields = self._extract_query_fields(query)
            
            for field in query_fields:
                if field not in field_usage:
                    field_usage[field] = {
                        "count": 0,
                        "queries": []
                    }
                field_usage[field]["count"] += 1
                field_usage[field]["queries"].append(query["timestamp"])
            
            # 分析查询模式
            pattern = "_".join(sorted(query_fields))
            if pattern not in pattern_frequency:
                pattern_frequency[pattern] = 0
            pattern_frequency[pattern] += 1
        
        # 推荐索引
        recommendations = []
        
        for field, usage in field_usage.items():
            if usage["count"] >= 5:  # 使用频率高的字段
                recommendations.append({
                    "type": "single_field",
                    "field": field,
                    "reason": f"字段 '{field}' 在 {usage['count']} 个查询中使用",
                    "score": usage["count"]
                })
        
        for pattern, frequency in pattern_frequency.items():
            if frequency >= 3:  # 频繁出现的组合模式
                fields = pattern.split("_")
                recommendations.append({
                    "type": "composite",
                    "fields": fields,
                    "reason": f"字段组合在 {frequency} 个查询中共同使用",
                    "score": frequency
                })
        
        # 按评分排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def optimize_existing_indexes(self):
        """优化现有索引"""
        optimization_suggestions = []
        
        for index_name, index_info in self.indexes.items():
            stats = self.usage_stats.get(index_name, {})
            
            # 检查未使用的索引
            if stats.get("queries", 0) == 0:
                optimization_suggestions.append({
                    "type": "remove",
                    "index": index_name,
                    "reason": "索引从未被查询使用，建议删除以节省存储空间"
                })
            
            # 检查低效索引
            efficiency = stats.get("efficiency", 0)
            if 0 < efficiency < 0.3:  # 效率低于30%
                optimization_suggestions.append({
                    "type": "rebuild",
                    "index": index_name,
                    "reason": f"索引效率低({efficiency:.2%})，建议重建",
                    "current_efficiency": efficiency
                })
        
        return optimization_suggestions
    
    def suggest_partitioning_strategy(self, collection_name):
        """建议分区策略"""
        # 分析集合特征
        if not self.storage:
            return []
        
        # 获取集合统计信息（简化实现）
        collection_stats = self._get_collection_stats(collection_name)
        
        suggestions = []
        
        # 基于数据量的分区建议
        if collection_stats["document_count"] > 10000000:  # 超过1000万文档
            suggestions.append({
                "type": "range_partitioning",
                "field": "created_at",
                "reason": "数据量较大，建议按创建时间范围分区",
                "estimated_partitions": max(1, collection_stats["document_count"] // 5000000)
            })
        
        # 基于查询模式的分区建议
        query_patterns = self._analyze_collection_query_patterns(collection_name)
        
        if "date_range" in query_patterns:
            suggestions.append({
                "type": "date_partitioning",
                "field": "date_field",
                "reason": "频繁的日期范围查询，建议按日期分区"
            })
        
        if "category_filter" in query_patterns:
            suggestions.append({
                "type": "hash_partitioning",
                "field": "category",
                "reason": "频繁的分类查询，建议按类别哈希分区"
            })
        
        return suggestions
    
    def _extract_query_fields(self, query):
        """从查询中提取使用的字段"""
        fields = []
        
        if isinstance(query, dict):
            for key, value in query.items():
                if not key.startswith("$"):
                    fields.append(key)
                
                if isinstance(value, dict):
                    fields.extend(self._extract_query_fields(value))
        
        return fields
    
    def _get_collection_stats(self, collection_name):
        """获取集合统计信息（简化实现）"""
        # 在实际应用中，这里会从存储系统获取真实统计信息
        return {
            "document_count": 5000000,
            "size_mb": 2048,
            "avg_document_size_kb": 0.4
        }
    
    def _analyze_collection_query_patterns(self, collection_name):
        """分析集合的查询模式（简化实现）"""
        # 在实际应用中，这里会分析查询日志
        return ["date_range", "category_filter"]

def demo_index_optimization():
    """演示索引优化的使用"""
    print("\n" + "=" * 50)
    print("3.3.1 元数据索引优化示例")
    print("=" * 50)
    
    # 创建索引优化器
    optimizer = MetadataIndexOptimizer()
    
    # 创建一些索引
    optimizer.create_index("idx_owner", {
        "fields": ["owner"],
        "type": "btree"
    })
    
    optimizer.create_index("idx_owner_type", {
        "fields": ["owner", "type"],
        "type": "btree"
    })
    
    optimizer.create_index("idx_name_text", {
        "fields": ["name"],
        "type": "fulltext"
    })
    
    print(f"已创建 {len(optimizer.indexes)} 个索引")
    
    # 模拟查询日志
    query_log = [
        {"query": {"owner": "数据团队"}, "timestamp": "2023-11-27T10:00:00"},
        {"query": {"type": "table", "owner": "数据团队"}, "timestamp": "2023-11-27T10:05:00"},
        {"query": {"type": "table", "owner": "数据团队"}, "timestamp": "2023-11-27T10:10:00"},
        {"query": {"name": "用户"}, "timestamp": "2023-11-27T10:15:00"},
        {"query": {"owner": "数据团队"}, "timestamp": "2023-11-27T10:20:00"},
        {"query": {"type": "table", "owner": "业务团队"}, "timestamp": "2023-11-27T10:25:00"},
        {"query": {"name": "订单"}, "timestamp": "2023-11-27T10:30:00"}
    ]
    
    # 分析查询模式
    recommendations = optimizer.analyze_query_patterns(query_log)
    print(f"\n基于查询模式的索引推荐:")
    for rec in recommendations:
        print(f"  {rec['type']}: {rec['reason']}")
    
    # 优化现有索引
    optimization_suggestions = optimizer.optimize_existing_indexes()
    print(f"\n现有索引优化建议:")
    for suggestion in optimization_suggestions:
        print(f"  {suggestion['type']}: {suggestion['reason']}")
    
    return optimizer

# ===================== 主函数 - 运行所有演示 =====================

def main():
    """运行所有演示示例"""
    print("第3章：元数据存储与模型 - 代码示例")
    print("=" * 80)
    
    # 演示存储架构
    centralized_storage = demo_centralized_storage()
    distributed_storage = demo_distributed_storage()
    hybrid_storage = demo_hybrid_storage()
    
    # 演示元数据模型
    relational_model = demo_relational_model()
    graph_model = demo_graph_model()
    document_model = demo_document_model()
    
    # 演示索引优化
    index_optimizer = demo_index_optimization()
    
    print("\n" + "=" * 80)
    print("所有演示完成！您可以根据自己的需求修改和扩展这些示例。")

if __name__ == "__main__":
    main()