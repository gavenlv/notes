#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据同步工具
实现主数据在不同系统间的同步和分发功能
"""

import os
import json
import sqlite3
import requests
import pandas as pd
import time
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict
import logging
import hashlib
import uuid
import schedule

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class SyncTask:
    """同步任务"""
    task_id: str
    entity_id: str
    entity_type: str
    source_system: str
    target_systems: List[str]
    sync_type: str  # 'realtime', 'batch', 'on_demand'
    sync_direction: str  # 'push', 'pull'
    creation_date: datetime
    scheduled_date: Optional[datetime] = None
    status: str = "pending"  # 'pending', 'running', 'completed', 'failed'
    priority: int = 5  # 1-10, 10 is highest
    retry_count: int = 0
    max_retries: int = 3
    retry_interval: int = 60  # seconds
    error_message: Optional[str] = None
    
    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['creation_date'] = self.creation_date.isoformat()
        if self.scheduled_date:
            result['scheduled_date'] = self.scheduled_date.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建任务"""
        data['creation_date'] = datetime.fromisoformat(data['creation_date'])
        if data.get('scheduled_date'):
            data['scheduled_date'] = datetime.fromisoformat(data['scheduled_date'])
        return cls(**data)


@dataclass
class SyncResult:
    """同步结果"""
    task_id: str
    entity_id: str
    target_system: str
    status: str  # 'success', 'failed', 'partial'
    start_time: datetime
    end_time: datetime
    records_sent: int
    records_processed: int
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        """转换为字典"""
        result = asdict(self)
        result['start_time'] = self.start_time.isoformat()
        result['end_time'] = self.end_time.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建结果"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


class SyncConnector:
    """同步连接器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.system_name = config.get('system_name', 'unknown')
        self.connection_type = config.get('connection_type', 'api')
    
    def connect(self) -> bool:
        """建立连接"""
        raise NotImplementedError("Subclasses must implement connect method")
    
    def disconnect(self) -> bool:
        """断开连接"""
        raise NotImplementedError("Subclasses must implement disconnect method")
    
    def push_data(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """推送数据"""
        raise NotImplementedError("Subclasses must implement push_data method")
    
    def pull_data(self, entity_id: str) -> Dict[str, Any]:
        """拉取数据"""
        raise NotImplementedError("Subclasses must implement pull_data method")
    
    def test_connection(self) -> bool:
        """测试连接"""
        raise NotImplementedError("Subclasses must implement test_connection method")


class RestApiConnector(SyncConnector):
    """REST API连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url')
        self.headers = config.get('headers', {})
        self.auth = config.get('auth', None)
        self.timeout = config.get('timeout', 30)
        self.session = None
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            self.session = requests.Session()
            
            # 设置认证
            if self.auth:
                if self.auth['type'] == 'basic':
                    self.session.auth = (self.auth['username'], self.auth['password'])
                elif self.auth['type'] == 'bearer':
                    self.session.headers['Authorization'] = f"Bearer {self.auth['token']}"
            
            # 设置默认头部
            self.session.headers.update(self.headers)
            
            # 测试连接
            if self.test_connection():
                logger.info(f"Connected to {self.system_name}")
                return True
            else:
                logger.error(f"Failed to connect to {self.system_name}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to {self.system_name}: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        if self.session:
            self.session.close()
            self.session = None
        logger.info(f"Disconnected from {self.system_name}")
        return True
    
    def push_data(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """推送数据"""
        if not self.session:
            if not self.connect():
                raise ConnectionError(f"Could not connect to {self.system_name}")
        
        try:
            # 构建请求URL
            endpoint = self.config.get('push_endpoint', '/api/entities')
            url = f"{self.base_url}{endpoint}/{entity_id}"
            
            # 发送请求
            response = self.session.put(
                url,
                json=entity_data,
                timeout=self.timeout
            )
            
            # 处理响应
            if response.status_code in [200, 201, 204]:
                return {
                    'status': 'success',
                    'response_code': response.status_code,
                    'response_data': response.json() if response.content else None
                }
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(f"Error pushing data to {self.system_name}: {error_msg}")
                return {
                    'status': 'error',
                    'response_code': response.status_code,
                    'error_message': error_msg
                }
        except Exception as e:
            error_msg = f"Exception pushing data to {self.system_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error_message': error_msg
            }
    
    def pull_data(self, entity_id: str) -> Dict[str, Any]:
        """拉取数据"""
        if not self.session:
            if not self.connect():
                raise ConnectionError(f"Could not connect to {self.system_name}")
        
        try:
            # 构建请求URL
            endpoint = self.config.get('pull_endpoint', '/api/entities')
            url = f"{self.base_url}{endpoint}/{entity_id}"
            
            # 发送请求
            response = self.session.get(url, timeout=self.timeout)
            
            # 处理响应
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'response_code': response.status_code,
                    'entity_data': response.json()
                }
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(f"Error pulling data from {self.system_name}: {error_msg}")
                return {
                    'status': 'error',
                    'response_code': response.status_code,
                    'error_message': error_msg
                }
        except Exception as e:
            error_msg = f"Exception pulling data from {self.system_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error_message': error_msg
            }
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            # 构建测试URL
            endpoint = self.config.get('health_endpoint', '/api/health')
            url = f"{self.base_url}{endpoint}"
            
            # 发送请求
            response = self.session.get(url, timeout=self.timeout)
            
            # 检查响应
            if response.status_code == 200:
                return True
            else:
                logger.warning(f"Health check failed for {self.system_name}: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check exception for {self.system_name}: {e}")
            return False


class DatabaseConnector(SyncConnector):
    """数据库连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.db_type = config.get('db_type', 'sqlite')
        self.connection_string = config.get('connection_string')
        self.table_name = config.get('table_name', 'entities')
        self.id_column = config.get('id_column', 'id')
        self.data_column = config.get('data_column', 'data')
        self.connection = None
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.connection_string)
            elif self.db_type == 'mysql':
                import pymysql
                self.connection = pymysql.connect(
                    host=self.config.get('host'),
                    user=self.config.get('user'),
                    password=self.config.get('password'),
                    database=self.config.get('database'),
                    port=self.config.get('port', 3306)
                )
            elif self.db_type == 'postgresql':
                import psycopg2
                self.connection = psycopg2.connect(
                    host=self.config.get('host'),
                    user=self.config.get('user'),
                    password=self.config.get('password'),
                    database=self.config.get('database'),
                    port=self.config.get('port', 5432)
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # 测试连接
            if self.test_connection():
                logger.info(f"Connected to {self.system_name}")
                return True
            else:
                logger.error(f"Failed to connect to {self.system_name}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to {self.system_name}: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
        logger.info(f"Disconnected from {self.system_name}")
        return True
    
    def push_data(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """推送数据"""
        if not self.connection:
            if not self.connect():
                raise ConnectionError(f"Could not connect to {self.system_name}")
        
        try:
            cursor = self.connection.cursor()
            
            # 准备数据
            data_json = json.dumps(entity_data)
            
            # 检查记录是否存在
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.table_name} WHERE {self.id_column} = ?",
                (entity_id,)
            )
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # 更新记录
                cursor.execute(
                    f"UPDATE {self.table_name} SET {self.data_column} = ? WHERE {self.id_column} = ?",
                    (data_json, entity_id)
                )
            else:
                # 插入记录
                cursor.execute(
                    f"INSERT INTO {self.table_name} ({self.id_column}, {self.data_column}) VALUES (?, ?)",
                    (entity_id, data_json)
                )
            
            self.connection.commit()
            
            return {
                'status': 'success',
                'operation': 'update' if exists else 'insert',
                'entity_id': entity_id
            }
        except Exception as e:
            error_msg = f"Exception pushing data to {self.system_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error_message': error_msg
            }
    
    def pull_data(self, entity_id: str) -> Dict[str, Any]:
        """拉取数据"""
        if not self.connection:
            if not self.connect():
                raise ConnectionError(f"Could not connect to {self.system_name}")
        
        try:
            cursor = self.connection.cursor()
            
            # 查询数据
            cursor.execute(
                f"SELECT {self.data_column} FROM {self.table_name} WHERE {self.id_column} = ?",
                (entity_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'status': 'success',
                    'entity_data': json.loads(result[0])
                }
            else:
                return {
                    'status': 'error',
                    'error_message': f"Entity {entity_id} not found"
                }
        except Exception as e:
            error_msg = f"Exception pulling data from {self.system_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error_message': error_msg
            }
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"Connection test failed for {self.system_name}: {e}")
            return False


class FileConnector(SyncConnector):
    """文件连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = config.get('file_path')
        self.file_type = config.get('file_type', 'csv')  # csv, json, excel
        self.encoding = config.get('encoding', 'utf-8')
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.file_path):
                # 创建文件
                if self.file_type == 'csv':
                    pd.DataFrame(columns=['id', 'data']).to_csv(self.file_path, index=False)
                elif self.file_type == 'json':
                    with open(self.file_path, 'w', encoding=self.encoding) as f:
                        json.dump([], f)
                elif self.file_type == 'excel':
                    pd.DataFrame(columns=['id', 'data']).to_excel(self.file_path, index=False)
            
            logger.info(f"Connected to {self.system_name}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to {self.system_name}: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        logger.info(f"Disconnected from {self.system_name}")
        return True
    
    def push_data(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """推送数据"""
        try:
            # 读取现有数据
            existing_data = self._read_file()
            
            # 查找记录
            entity_index = None
            for i, record in enumerate(existing_data):
                if record.get('id') == entity_id:
                    entity_index = i
                    break
            
            # 更新或添加记录
            record = {
                'id': entity_id,
                'data': json.dumps(entity_data),
                'last_updated': datetime.now().isoformat()
            }
            
            if entity_index is not None:
                existing_data[entity_index] = record
            else:
                existing_data.append(record)
            
            # 写回文件
            self._write_file(existing_data)
            
            return {
                'status': 'success',
                'operation': 'update' if entity_index is not None else 'insert',
                'entity_id': entity_id
            }
        except Exception as e:
            error_msg = f"Exception pushing data to {self.system_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error_message': error_msg
            }
    
    def pull_data(self, entity_id: str) -> Dict[str, Any]:
        """拉取数据"""
        try:
            # 读取数据
            data = self._read_file()
            
            # 查找记录
            for record in data:
                if record.get('id') == entity_id:
                    return {
                        'status': 'success',
                        'entity_data': json.loads(record.get('data', '{}'))
                    }
            
            return {
                'status': 'error',
                'error_message': f"Entity {entity_id} not found"
            }
        except Exception as e:
            error_msg = f"Exception pulling data from {self.system_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error_message': error_msg
            }
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            return os.path.exists(self.file_path) or os.access(os.path.dirname(self.file_path), os.W_OK)
        except Exception as e:
            logger.error(f"Connection test failed for {self.system_name}: {e}")
            return False
    
    def _read_file(self) -> List[Dict[str, Any]]:
        """读取文件数据"""
        if self.file_type == 'csv':
            df = pd.read_csv(self.file_path, encoding=self.encoding)
            return df.to_dict('records')
        elif self.file_type == 'json':
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                return json.load(f)
        elif self.file_type == 'excel':
            df = pd.read_excel(self.file_path)
            return df.to_dict('records')
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")
    
    def _write_file(self, data: List[Dict[str, Any]]):
        """写入文件数据"""
        if self.file_type == 'csv':
            df = pd.DataFrame(data)
            df.to_csv(self.file_path, index=False)
        elif self.file_type == 'json':
            with open(self.file_path, 'w', encoding=self.encoding) as f:
                json.dump(data, f, indent=2)
        elif self.file_type == 'excel':
            df = pd.DataFrame(data)
            df.to_excel(self.file_path, index=False)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")


class ConflictResolver:
    """冲突解决器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.resolution_strategy = config.get('strategy', 'timestamp')
        self.source_priorities = config.get('source_priorities', {})
    
    def resolve_conflict(self, entity_id: str, source_data: Dict[str, Any], 
                        target_data: Dict[str, Any]) -> Dict[str, Any]:
        """解决数据冲突"""
        if self.resolution_strategy == 'source_priority':
            return self._resolve_by_source_priority(source_data, target_data)
        elif self.resolution_strategy == 'timestamp':
            return self._resolve_by_timestamp(source_data, target_data)
        elif self.resolution_strategy == 'merge':
            return self._merge_data(source_data, target_data)
        elif self.resolution_strategy == 'manual':
            return self._manual_resolution(source_data, target_data)
        else:
            return self._default_resolution(source_data, target_data)
    
    def _resolve_by_source_priority(self, source_data: Dict[str, Any], 
                                   target_data: Dict[str, Any]) -> Dict[str, Any]:
        """按源优先级解决冲突"""
        source_system = source_data.get('source_system', '')
        target_system = target_data.get('source_system', '')
        
        source_priority = self.source_priorities.get(source_system, 999)
        target_priority = self.source_priorities.get(target_system, 999)
        
        if source_priority <= target_priority:
            return source_data
        else:
            return target_data
    
    def _resolve_by_timestamp(self, source_data: Dict[str, Any], 
                             target_data: Dict[str, Any]) -> Dict[str, Any]:
        """按时间戳解决冲突"""
        source_timestamp = source_data.get('last_update_date', '')
        target_timestamp = target_data.get('last_update_date', '')
        
        try:
            source_dt = datetime.fromisoformat(source_timestamp)
            target_dt = datetime.fromisoformat(target_timestamp)
            
            if source_dt >= target_dt:
                return source_data
            else:
                return target_data
        except:
            # 如果时间戳无效，默认使用源数据
            return source_data
    
    def _merge_data(self, source_data: Dict[str, Any], 
                   target_data: Dict[str, Any]) -> Dict[str, Any]:
        """合并数据"""
        # 简单的合并策略：优先使用源数据，如果源数据为空则使用目标数据
        merged_data = target_data.copy()
        
        for key, value in source_data.items():
            if value is not None and value != '':
                merged_data[key] = value
        
        # 更新合并时间戳
        merged_data['last_update_date'] = datetime.now().isoformat()
        merged_data['merged_from'] = [source_data.get('entity_id'), target_data.get('entity_id')]
        
        return merged_data
    
    def _manual_resolution(self, source_data: Dict[str, Any], 
                          target_data: Dict[str, Any]) -> Dict[str, Any]:
        """手动解决冲突"""
        # 在实际应用中，这里应该记录冲突，等待人工决策
        logger.warning(f"Manual resolution required for entity {source_data.get('entity_id')}")
        return source_data  # 默认返回源数据
    
    def _default_resolution(self, source_data: Dict[str, Any], 
                            target_data: Dict[str, Any]) -> Dict[str, Any]:
        """默认解决策略"""
        return source_data


class DataSyncTool:
    """数据同步工具"""
    
    def __init__(self, config_path: str = None):
        """初始化数据同步工具"""
        self.config = self._load_config(config_path)
        
        # 初始化数据库
        self.db_path = self.config.get('db_path', 'data_sync.db')
        self._initialize_database()
        
        # 初始化连接器
        self.connectors = {}
        self._initialize_connectors()
        
        # 初始化冲突解决器
        self.conflict_resolver = ConflictResolver(self.config.get('conflict_resolution', {}))
        
        # 初始化任务队列和工作线程
        self.task_queue = queue.PriorityQueue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.is_running = False
        self.worker_count = self.config.get('worker_count', 3)
        
        # 启动调度器
        self.scheduler_started = False
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "db_path": "data_sync.db",
            "worker_count": 3,
            "conflict_resolution": {
                "strategy": "timestamp",
                "source_priorities": {
                    "MDM": 1,
                    "ERP": 2,
                    "CRM": 3,
                    "Website": 4
                }
            },
            "systems": {
                "MDM": {
                    "type": "database",
                    "connection_type": "sqlite",
                    "connection_string": "mdm.db",
                    "table_name": "master_data"
                },
                "CRM": {
                    "type": "rest_api",
                    "connection_type": "api",
                    "base_url": "https://api.crm.example.com",
                    "auth": {
                        "type": "bearer",
                        "token": "your-api-token"
                    },
                    "headers": {
                        "Content-Type": "application/json"
                    }
                },
                "ERP": {
                    "type": "database",
                    "connection_type": "mysql",
                    "host": "localhost",
                    "port": 3306,
                    "user": "erp_user",
                    "password": "erp_password",
                    "database": "erp_db",
                    "table_name": "products"
                },
                "E-Commerce": {
                    "type": "file",
                    "connection_type": "file",
                    "file_path": "ecommerce_data.csv",
                    "file_type": "csv"
                }
            },
            "schedules": [
                {
                    "name": "daily_sync",
                    "entity_type": "customer",
                    "sync_type": "batch",
                    "target_systems": ["CRM", "ERP"],
                    "schedule": "0 2 * * *"  # 每天凌晨2点
                }
            ]
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
        
        # 创建同步任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_tasks (
            task_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            source_system TEXT NOT NULL,
            target_systems TEXT NOT NULL,
            sync_type TEXT NOT NULL,
            sync_direction TEXT NOT NULL,
            creation_date TEXT NOT NULL,
            scheduled_date TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 5,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            retry_interval INTEGER DEFAULT 60,
            error_message TEXT
        )
        ''')
        
        # 创建同步结果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_results (
            result_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            target_system TEXT NOT NULL,
            status TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            records_sent INTEGER DEFAULT 0,
            records_processed INTEGER DEFAULT 0,
            error_message TEXT,
            response_data TEXT,
            FOREIGN KEY (task_id) REFERENCES sync_tasks (task_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_connectors(self):
        """初始化连接器"""
        for system_name, system_config in self.config['systems'].items():
            system_type = system_config.get('type')
            
            connector = None
            if system_type == 'rest_api':
                connector = RestApiConnector(system_config)
            elif system_type == 'database':
                connector = DatabaseConnector(system_config)
            elif system_type == 'file':
                connector = FileConnector(system_config)
            
            if connector:
                connector.system_name = system_name
                self.connectors[system_name] = connector
                logger.info(f"Initialized connector for {system_name}")
    
    def start(self):
        """启动数据同步服务"""
        if self.is_running:
            logger.warning("Data sync service is already running")
            return
        
        # 启动工作线程
        self.is_running = True
        for i in range(self.worker_count):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {self.worker_count} worker threads")
        
        # 启动调度器
        if not self.scheduler_started:
            self._start_scheduler()
            self.scheduler_started = True
        
        logger.info("Data sync service started")
    
    def stop(self):
        """停止数据同步服务"""
        self.is_running = False
        
        # 等待所有工作线程结束
        for worker in self.workers:
            worker.join(timeout=5)
        
        # 断开所有连接器
        for connector in self.connectors.values():
            connector.disconnect()
        
        logger.info("Data sync service stopped")
    
    def schedule_sync(self, entity_id: str, entity_type: str, source_system: str, 
                     target_systems: List[str], sync_type: str = "realtime", 
                     sync_direction: str = "push", scheduled_date: datetime = None,
                     priority: int = 5) -> str:
        """调度同步任务"""
        task_id = str(uuid.uuid4())
        
        task = SyncTask(
            task_id=task_id,
            entity_id=entity_id,
            entity_type=entity_type,
            source_system=source_system,
            target_systems=target_systems,
            sync_type=sync_type,
            sync_direction=sync_direction,
            creation_date=datetime.now(),
            scheduled_date=scheduled_date,
            priority=priority
        )
        
        # 保存任务
        self._save_task(task)
        
        # 如果是实时同步，立即加入队列
        if sync_type == "realtime" or (scheduled_date and scheduled_date <= datetime.now()):
            self.task_queue.put((-priority, task_id))  # 使用负优先级实现最大优先级队列
            logger.info(f"Scheduled immediate sync task {task_id} for entity {entity_id}")
        else:
            logger.info(f"Scheduled future sync task {task_id} for entity {entity_id} at {scheduled_date}")
        
        return task_id
    
    def batch_sync(self, entity_type: str, source_system: str, 
                  target_systems: List[str], entity_ids: List[str] = None,
                  batch_size: int = 100) -> List[str]:
        """批量同步"""
        task_ids = []
        
        # 如果没有提供实体ID，从源系统获取
        if not entity_ids:
            entity_ids = self._get_entity_ids(source_system, entity_type)
        
        # 分批处理
        for i in range(0, len(entity_ids), batch_size):
            batch = entity_ids[i:i+batch_size]
            
            # 为每个实体创建同步任务
            for entity_id in batch:
                task_id = self.schedule_sync(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    source_system=source_system,
                    target_systems=target_systems,
                    sync_type="batch"
                )
                task_ids.append(task_id)
        
        logger.info(f"Scheduled {len(task_ids)} batch sync tasks for {len(entity_ids)} entities")
        return task_ids
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task = self._get_task(task_id)
        if not task:
            return None
        
        results = self._get_task_results(task_id)
        
        return {
            'task': task.to_dict(),
            'results': [result.to_dict() for result in results]
        }
    
    def get_sync_history(self, entity_id: str = None, entity_type: str = None,
                        target_system: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取同步历史"""
        conn = sqlite3.connect(self.db_path)
        
        # 构建查询
        query = '''
        SELECT r.*, t.entity_type, t.source_system
        FROM sync_results r
        JOIN sync_tasks t ON r.task_id = t.task_id
        WHERE 1=1
        '''
        params = []
        
        if entity_id:
            query += " AND r.entity_id = ?"
            params.append(entity_id)
        
        if entity_type:
            query += " AND t.entity_type = ?"
            params.append(entity_type)
        
        if target_system:
            query += " AND r.target_system = ?"
            params.append(target_system)
        
        query += " ORDER BY r.end_time DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            result = SyncResult(
                result_id=row[0],
                task_id=row[1],
                entity_id=row[2],
                target_system=row[3],
                status=row[4],
                start_time=datetime.fromisoformat(row[5]),
                end_time=datetime.fromisoformat(row[6]),
                records_sent=row[7],
                records_processed=row[8],
                error_message=row[9],
                response_data=json.loads(row[10]) if row[10] else None
            )
            result_dict = result.to_dict()
            result_dict['entity_type'] = row[11]
            result_dict['source_system'] = row[12]
            results.append(result_dict)
        
        conn.close()
        
        return results
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """获取同步统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总任务数
        cursor.execute("SELECT COUNT(*) FROM sync_tasks")
        total_tasks = cursor.fetchone()[0]
        
        # 按状态统计任务
        cursor.execute("""
        SELECT status, COUNT(*) 
        FROM sync_tasks 
        GROUP BY status
        """)
        task_status_counts = dict(cursor.fetchall())
        
        # 按系统统计结果
        cursor.execute("""
        SELECT target_system, status, COUNT(*) 
        FROM sync_results 
        GROUP BY target_system, status
        """)
        system_status_counts = {}
        for target_system, status, count in cursor.fetchall():
            if target_system not in system_status_counts:
                system_status_counts[target_system] = {}
            system_status_counts[target_system][status] = count
        
        # 最近24小时的同步活动
        cursor.execute("""
        SELECT COUNT(*) 
        FROM sync_results 
        WHERE end_time > datetime('now', '-1 day')
        """)
        recent_syncs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tasks': total_tasks,
            'task_status_counts': task_status_counts,
            'system_status_counts': system_status_counts,
            'recent_syncs_24h': recent_syncs
        }
    
    def _worker(self):
        """工作线程"""
        logger.info(f"Worker thread {threading.current_thread().name} started")
        
        while self.is_running:
            try:
                # 获取任务
                try:
                    priority, task_id = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # 获取任务详情
                task = self._get_task(task_id)
                if not task:
                    logger.warning(f"Task {task_id} not found")
                    continue
                
                # 检查任务是否已取消
                if task.status in ['completed', 'failed', 'cancelled']:
                    continue
                
                # 更新任务状态
                task.status = 'running'
                self._save_task(task)
                
                # 执行同步
                try:
                    self._execute_sync_task(task)
                except Exception as e:
                    logger.error(f"Error executing sync task {task_id}: {e}")
                    
                    # 检查是否需要重试
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.error_message = str(e)
                        task.status = 'pending'
                        
                        # 安排重试
                        retry_time = datetime.now() + timedelta(seconds=task.retry_interval)
                        self.task_queue.put((-task.priority, task_id))
                        
                        logger.info(f"Scheduled retry {task.retry_count}/{task.max_retries} for task {task_id} at {retry_time}")
                    else:
                        task.status = 'failed'
                        task.error_message = str(e)
                    
                    self._save_task(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker thread error: {e}")
        
        logger.info(f"Worker thread {threading.current_thread().name} stopped")
    
    def _execute_sync_task(self, task: SyncTask):
        """执行同步任务"""
        # 获取源系统连接器
        source_connector = self.connectors.get(task.source_system)
        if not source_connector:
            raise ValueError(f"No connector found for source system {task.source_system}")
        
        # 获取实体数据
        entity_data_result = source_connector.pull_data(task.entity_id)
        if entity_data_result['status'] != 'success':
            raise ValueError(f"Failed to pull data from source: {entity_data_result.get('error_message', 'Unknown error')}")
        
        entity_data = entity_data_result['entity_data']
        
        # 同步到每个目标系统
        for target_system in task.target_systems:
            result_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # 获取目标系统连接器
            target_connector = self.connectors.get(target_system)
            if not target_connector:
                error_msg = f"No connector found for target system {target_system}"
                self._save_sync_result(
                    SyncResult(
                        result_id=result_id,
                        task_id=task.task_id,
                        entity_id=task.entity_id,
                        target_system=target_system,
                        status='failed',
                        start_time=start_time,
                        end_time=datetime.now(),
                        records_sent=0,
                        records_processed=0,
                        error_message=error_msg
                    )
                )
                continue
            
            try:
                # 检查目标系统中是否已存在数据
                target_data_result = target_connector.pull_data(task.entity_id)
                
                if target_data_result['status'] == 'success':
                    # 解决冲突
                    resolved_data = self.conflict_resolver.resolve_conflict(
                        task.entity_id, entity_data, target_data_result['entity_data']
                    )
                else:
                    # 目标系统中不存在数据，使用源数据
                    resolved_data = entity_data
                
                # 推送数据
                push_result = target_connector.push_data(task.entity_id, resolved_data)
                
                # 记录结果
                end_time = datetime.now()
                status = 'success' if push_result['status'] == 'success' else 'failed'
                
                self._save_sync_result(
                    SyncResult(
                        result_id=result_id,
                        task_id=task.task_id,
                        entity_id=task.entity_id,
                        target_system=target_system,
                        status=status,
                        start_time=start_time,
                        end_time=end_time,
                        records_sent=1,
                        records_processed=1 if status == 'success' else 0,
                        error_message=push_result.get('error_message') if status == 'failed' else None,
                        response_data=push_result if status == 'success' else None
                    )
                )
                
                logger.info(f"Synced {task.entity_id} to {target_system}: {status}")
                
            except Exception as e:
                # 记录错误
                self._save_sync_result(
                    SyncResult(
                        result_id=result_id,
                        task_id=task.task_id,
                        entity_id=task.entity_id,
                        target_system=target_system,
                        status='failed',
                        start_time=start_time,
                        end_time=datetime.now(),
                        records_sent=0,
                        records_processed=0,
                        error_message=str(e)
                    )
                )
                
                logger.error(f"Failed to sync {task.entity_id} to {target_system}: {e}")
        
        # 更新任务状态
        task.status = 'completed'
        self._save_task(task)
    
    def _start_scheduler(self):
        """启动调度器"""
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        
        # 设置定时任务
        for sched in self.config.get('schedules', []):
            schedule.every().day.at("02:00").do(
                self._scheduled_sync,
                sched.get('name'),
                sched.get('entity_type'),
                sched.get('sync_type', 'batch'),
                sched.get('target_systems', [])
            )
        
        # 启动调度线程
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("Scheduler started")
    
    def _scheduled_sync(self, name: str, entity_type: str, sync_type: str, target_systems: List[str]):
        """执行定时同步"""
        logger.info(f"Running scheduled sync '{name}' for {entity_type}")
        
        # 获取需要同步的实体
        entity_ids = self._get_entity_ids("MDM", entity_type)
        
        # 创建批量同步任务
        task_ids = self.batch_sync(
            entity_type=entity_type,
            source_system="MDM",
            target_systems=target_systems,
            entity_ids=entity_ids
        )
        
        logger.info(f"Scheduled {len(task_ids)} tasks for scheduled sync '{name}'")
    
    def _get_entity_ids(self, source_system: str, entity_type: str) -> List[str]:
        """从源系统获取实体ID列表"""
        # 这里简化处理，实际应该从数据库或API获取
        if source_system == "MDM":
            conn = sqlite3.connect("mdm.db")
            cursor = conn.cursor()
            cursor.execute("SELECT entity_id FROM master_data WHERE entity_type = ?", (entity_type,))
            entity_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            return entity_ids
        
        return []
    
    def _save_task(self, task: SyncTask):
        """保存任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO sync_tasks 
        (task_id, entity_id, entity_type, source_system, target_systems, 
         sync_type, sync_direction, creation_date, scheduled_date, status, 
         priority, retry_count, max_retries, retry_interval, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id,
            task.entity_id,
            task.entity_type,
            task.source_system,
            ','.join(task.target_systems),
            task.sync_type,
            task.sync_direction,
            task.creation_date.isoformat(),
            task.scheduled_date.isoformat() if task.scheduled_date else None,
            task.status,
            task.priority,
            task.retry_count,
            task.max_retries,
            task.retry_interval,
            task.error_message
        ))
        
        conn.commit()
        conn.close()
    
    def _get_task(self, task_id: str) -> Optional[SyncTask]:
        """获取任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sync_tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return SyncTask(
                task_id=row[0],
                entity_id=row[1],
                entity_type=row[2],
                source_system=row[3],
                target_systems=row[4].split(','),
                sync_type=row[5],
                sync_direction=row[6],
                creation_date=datetime.fromisoformat(row[7]),
                scheduled_date=datetime.fromisoformat(row[8]) if row[8] else None,
                status=row[9],
                priority=row[10],
                retry_count=row[11],
                max_retries=row[12],
                retry_interval=row[13],
                error_message=row[14]
            )
        
        return None
    
    def _save_sync_result(self, result: SyncResult):
        """保存同步结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO sync_results 
        (result_id, task_id, entity_id, target_system, status, 
         start_time, end_time, records_sent, records_processed, 
         error_message, response_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.result_id,
            result.task_id,
            result.entity_id,
            result.target_system,
            result.status,
            result.start_time.isoformat(),
            result.end_time.isoformat(),
            result.records_sent,
            result.records_processed,
            result.error_message,
            json.dumps(result.response_data) if result.response_data else None
        ))
        
        conn.commit()
        conn.close()
    
    def _get_task_results(self, task_id: str) -> List[SyncResult]:
        """获取任务结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sync_results WHERE task_id = ?", (task_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append(SyncResult(
                result_id=row[0],
                task_id=row[1],
                entity_id=row[2],
                target_system=row[3],
                status=row[4],
                start_time=datetime.fromisoformat(row[5]),
                end_time=datetime.fromisoformat(row[6]),
                records_sent=row[7],
                records_processed=row[8],
                error_message=row[9],
                response_data=json.loads(row[10]) if row[10] else None
            ))
        
        conn.close()
        
        return results


def generate_sample_data():
    """生成示例数据"""
    print("Generating sample data...")
    
    # 创建主数据数据库
    conn = sqlite3.connect("mdm.db")
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
    
    # 插入示例数据
    sample_entities = [
        ('cust-001', 'customer', '{"name": "张三", "email": "zhangsan@example.com", "phone": "+86-13812345678"}', 'MDM', '2023-01-01T00:00:00', '2023-06-15T10:30:00'),
        ('cust-002', 'customer', '{"name": "李四", "email": "lisi@example.com", "phone": "+86-13912345678"}', 'MDM', '2023-01-02T00:00:00', '2023-06-16T11:20:00'),
        ('prod-001', 'product', '{"name": "智能手机", "sku": "PHONE-001", "price": 2999.99}', 'MDM', '2023-01-03T00:00:00', '2023-06-17T09:15:00'),
        ('supp-001', 'supplier', '{"name": "供应商A", "contact_email": "contact@suppliera.com"}', 'MDM', '2023-01-04T00:00:00', '2023-06-18T14:45:00')
    ]
    
    for entity in sample_entities:
        cursor.execute('''
        INSERT OR REPLACE INTO master_data 
        (entity_id, entity_type, attributes, source_system, creation_date, last_update_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', entity)
    
    conn.commit()
    conn.close()
    
    print("Sample data generated successfully")


def demonstrate_sync_capabilities():
    """演示同步能力"""
    # 生成示例数据
    generate_sample_data()
    
    # 创建同步工具
    sync_tool = DataSyncTool()
    
    # 启动同步服务
    sync_tool.start()
    
    try:
        print("\n=== 数据同步能力演示 ===")
        
        # 1. 实时同步
        print("\n1. 执行实时同步:")
        task_id = sync_tool.schedule_sync(
            entity_id='cust-001',
            entity_type='customer',
            source_system='MDM',
            target_systems=['CRM', 'ERP'],
            sync_type='realtime'
        )
        print(f"  调度实时同步任务: {task_id}")
        
        # 等待任务完成
        time.sleep(2)
        
        # 查看任务状态
        task_status = sync_tool.get_task_status(task_id)
        if task_status:
            print(f"  任务状态: {task_status['task']['status']}")
            for result in task_status['results']:
                print(f"  同步到 {result['target_system']}: {result['status']}")
        
        # 2. 批量同步
        print("\n2. 执行批量同步:")
        task_ids = sync_tool.batch_sync(
            entity_type='customer',
            source_system='MDM',
            target_systems=['CRM', 'ERP']
        )
        print(f"  调度了 {len(task_ids)} 个批量同步任务")
        
        # 等待任务完成
        time.sleep(3)
        
        # 3. 同步历史
        print("\n3. 查看同步历史:")
        sync_history = sync_tool.get_sync_history(limit=5)
        for record in sync_history:
            print(f"  实体 {record['entity_id']} 到 {record['target_system']}: {record['status']} ({record['end_time']})")
        
        # 4. 同步统计
        print("\n4. 查看同步统计:")
        sync_stats = sync_tool.get_sync_statistics()
        print(f"  总任务数: {sync_stats['total_tasks']}")
        print(f"  任务状态统计: {sync_stats['task_status_counts']}")
        print(f"  系统状态统计: {sync_stats['system_status_counts']}")
        print(f"  最近24小时同步数: {sync_stats['recent_syncs_24h']}")
        
    finally:
        # 停止同步服务
        sync_tool.stop()


if __name__ == "__main__":
    demonstrate_sync_capabilities()