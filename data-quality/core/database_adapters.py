#!/usr/bin/env python3
"""
数据库适配器
提供统一的数据库访问接口，支持多种数据库类型
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class DatabaseAdapter(ABC):
    """数据库适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据库适配器
        
        Args:
            config: 数据库配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.is_connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """
        连接到数据库
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开数据库连接"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """
        执行查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict]: 查询结果
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否正常
        """
        pass
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Returns:
            Dict: 数据库信息
        """
        return {
            'type': self.__class__.__name__.replace('Adapter', '').lower(),
            'host': self.config.get('host', 'unknown'),
            'port': self.config.get('port', 'unknown'),
            'database': self.config.get('database', 'unknown'),
            'user': self.config.get('user', 'unknown'),
            'connected': self.is_connected
        }


class ClickHouseAdapter(DatabaseAdapter):
    """ClickHouse数据库适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        
    def connect(self) -> bool:
        """连接到ClickHouse"""
        try:
            port = self.config.get('port', 9000)
            
            # 如果是8123端口，使用HTTP接口
            if port == 8123:
                return self._connect_http()
            else:
                return self._connect_native()
                
        except Exception as e:
            self.logger.error(f"连接ClickHouse失败: {e}")
            return False
    
    def _connect_native(self) -> bool:
        """使用原生协议连接ClickHouse"""
        try:
            from clickhouse_driver import Client
            
            self.client = Client(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 9000),
                database=self.config.get('database', 'default'),
                user=self.config.get('user', 'default'),
                password=self.config.get('password', ''),
                secure=self.config.get('secure', False),
                settings={'timeout': self.config.get('timeout', 60)}
            )
            
            # 测试连接
            self.client.execute('SELECT 1')
            self.is_connected = True
            self.logger.info("成功连接到ClickHouse (原生协议)")
            return True
            
        except ImportError:
            self.logger.error("ClickHouse原生驱动未安装，请运行: pip install clickhouse-driver")
            return False
        
    def _connect_http(self) -> bool:
        """使用HTTP接口连接ClickHouse"""
        try:
            import requests
            
            self.http_session = requests.Session()
            self.base_url = f"http://{self.config.get('host', 'localhost')}:{self.config.get('port', 8123)}"
            
            # 设置认证
            user = self.config.get('user', 'default')
            password = self.config.get('password', '')
            if user and password:
                self.http_session.auth = (user, password)
            
            # 测试连接
            response = self.http_session.get(
                f"{self.base_url}/",
                params={'query': 'SELECT 1'},
                timeout=self.config.get('timeout', 60)
            )
            
            if response.status_code == 200:
                self.is_connected = True
                self.logger.info("成功连接到ClickHouse (HTTP接口)")
                return True
            else:
                self.logger.error(f"ClickHouse HTTP连接失败，状态码: {response.status_code}")
                return False
                
        except ImportError:
            self.logger.error("HTTP请求库未安装，请运行: pip install requests")
            return False
    
    def disconnect(self):
        """断开ClickHouse连接"""
        if self.client:
            try:
                self.client.disconnect()
                self.is_connected = False
                self.logger.info("已断开ClickHouse连接")
            except Exception as e:
                self.logger.warning(f"断开ClickHouse连接时出错: {e}")
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """执行ClickHouse查询"""
        try:
            if not self.is_connected:
                raise Exception("数据库未连接")
            
            # 根据连接类型选择执行方式
            if hasattr(self, 'http_session'):
                return self._execute_http_query(query, params)
            else:
                return self._execute_native_query(query, params)
            
        except Exception as e:
            self.logger.error(f"执行ClickHouse查询失败: {e}")
            self.logger.debug(f"查询语句: {query}")
            return []
    
    def _execute_native_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """使用原生协议执行查询"""
        # 执行查询并获取列信息
        result = self.client.execute(query, with_column_types=True)
        
        if not result or not result[0]:
            return []
        
        # 解析结果
        rows = result[0]
        columns = [col[0] for col in result[1]]
        
        # 转换为字典列表
        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            results.append(row_dict)
        
        return results
    
    def _execute_http_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """使用HTTP接口执行查询"""
        import json
        
        # 确保查询不为空
        if not query or not query.strip():
            raise Exception("查询语句为空")
        
        # 添加FORMAT JSON以获取JSON格式结果
        if not query.strip().upper().endswith('FORMAT JSON'):
            query = query.strip() + ' FORMAT JSON'
        
        # 执行HTTP请求
        response = self.http_session.post(
            f"{self.base_url}/",
            data=query.encode('utf-8'),
            headers={'Content-Type': 'text/plain; charset=utf-8'},
            timeout=self.config.get('timeout', 60)
        )
        
        if response.status_code != 200:
            raise Exception(f"HTTP查询失败，状态码: {response.status_code}, 响应: {response.text}")
        
        # 解析JSON结果
        try:
            result_data = json.loads(response.text)
            if 'data' in result_data:
                return result_data['data']
            else:
                # 如果没有data字段，可能是单行结果
                return [result_data] if result_data else []
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试解析为简单文本
            lines = response.text.strip().split('\n')
            if len(lines) == 1 and lines[0]:
                # 简单值，创建一个字典
                return [{'result': lines[0]}]
            return []
    
    def test_connection(self) -> bool:
        """测试ClickHouse连接"""
        try:
            if not self.is_connected:
                return False
            
            if hasattr(self, 'http_session'):
                # HTTP接口测试
                response = self.http_session.get(
                    f"{self.base_url}/",
                    params={'query': 'SELECT 1'},
                    timeout=self.config.get('timeout', 60)
                )
                return response.status_code == 200
            else:
                # 原生协议测试
                result = self.client.execute('SELECT 1')
                return result is not None
            
        except Exception:
            return False


class MySQLAdapter(DatabaseAdapter):
    """MySQL数据库适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None
        
    def connect(self) -> bool:
        """连接到MySQL"""
        try:
            import pymysql
            
            self.connection = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('user', 'root'),
                password=self.config.get('password', ''),
                database=self.config.get('database', ''),
                charset=self.config.get('charset', 'utf8mb4'),
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=self.config.get('timeout', 60)
            )
            
            self.is_connected = True
            self.logger.info("成功连接到MySQL")
            return True
            
        except ImportError:
            self.logger.error("MySQL驱动未安装，请运行: pip install pymysql")
            return False
        except Exception as e:
            self.logger.error(f"连接MySQL失败: {e}")
            return False
    
    def disconnect(self):
        """断开MySQL连接"""
        if self.connection:
            try:
                self.connection.close()
                self.is_connected = False
                self.logger.info("已断开MySQL连接")
            except Exception as e:
                self.logger.warning(f"断开MySQL连接时出错: {e}")
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """执行MySQL查询"""
        try:
            if not self.is_connected:
                raise Exception("数据库未连接")
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return results or []
                
        except Exception as e:
            self.logger.error(f"执行MySQL查询失败: {e}")
            self.logger.debug(f"查询语句: {query}")
            return []
    
    def test_connection(self) -> bool:
        """测试MySQL连接"""
        try:
            if not self.is_connected:
                return False
            
            with self.connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                return result is not None
                
        except Exception:
            return False


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL数据库适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None
        
    def connect(self) -> bool:
        """连接到PostgreSQL"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                user=self.config.get('user', 'postgres'),
                password=self.config.get('password', ''),
                database=self.config.get('database', ''),
                connect_timeout=self.config.get('timeout', 60)
            )
            
            self.is_connected = True
            self.logger.info("成功连接到PostgreSQL")
            return True
            
        except ImportError:
            self.logger.error("PostgreSQL驱动未安装，请运行: pip install psycopg2-binary")
            return False
        except Exception as e:
            self.logger.error(f"连接PostgreSQL失败: {e}")
            return False
    
    def disconnect(self):
        """断开PostgreSQL连接"""
        if self.connection:
            try:
                self.connection.close()
                self.is_connected = False
                self.logger.info("已断开PostgreSQL连接")
            except Exception as e:
                self.logger.warning(f"断开PostgreSQL连接时出错: {e}")
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """执行PostgreSQL查询"""
        try:
            if not self.is_connected:
                raise Exception("数据库未连接")
            
            from psycopg2.extras import RealDictCursor
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                # 转换RealDictRow为普通字典
                return [dict(row) for row in results] if results else []
                
        except Exception as e:
            self.logger.error(f"执行PostgreSQL查询失败: {e}")
            self.logger.debug(f"查询语句: {query}")
            return []
    
    def test_connection(self) -> bool:
        """测试PostgreSQL连接"""
        try:
            if not self.is_connected:
                return False
            
            with self.connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                return result is not None
                
        except Exception:
            return False


class SQLServerAdapter(DatabaseAdapter):
    """SQL Server数据库适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None
        
    def connect(self) -> bool:
        """连接到SQL Server"""
        try:
            import pyodbc
            
            # 构建连接字符串
            server = self.config.get('host', 'localhost')
            port = self.config.get('port', 1433)
            database = self.config.get('database', '')
            username = self.config.get('user', '')
            password = self.config.get('password', '')
            driver = self.config.get('driver', '{ODBC Driver 17 for SQL Server}')
            
            connection_string = f"""
            DRIVER={driver};
            SERVER={server},{port};
            DATABASE={database};
            UID={username};
            PWD={password};
            ENCRYPT=yes;
            TrustServerCertificate=yes;
            """
            
            self.connection = pyodbc.connect(connection_string.strip())
            self.is_connected = True
            self.logger.info("成功连接到SQL Server")
            return True
            
        except ImportError:
            self.logger.error("SQL Server驱动未安装，请运行: pip install pyodbc")
            return False
        except Exception as e:
            self.logger.error(f"连接SQL Server失败: {e}")
            return False
    
    def disconnect(self):
        """断开SQL Server连接"""
        if self.connection:
            try:
                self.connection.close()
                self.is_connected = False
                self.logger.info("已断开SQL Server连接")
            except Exception as e:
                self.logger.warning(f"断开SQL Server连接时出错: {e}")
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """执行SQL Server查询"""
        try:
            if not self.is_connected:
                raise Exception("数据库未连接")
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            
            # 获取列名
            columns = [column[0] for column in cursor.description]
            
            # 获取数据并转换为字典列表
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                results.append(row_dict)
            
            cursor.close()
            return results
                
        except Exception as e:
            self.logger.error(f"执行SQL Server查询失败: {e}")
            self.logger.debug(f"查询语句: {query}")
            return []
    
    def test_connection(self) -> bool:
        """测试SQL Server连接"""
        try:
            if not self.is_connected:
                return False
            
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.close()
            return result is not None
                
        except Exception:
            return False


class DatabaseAdapterFactory:
    """数据库适配器工厂"""
    
    _adapters = {
        'clickhouse': ClickHouseAdapter,
        'mysql': MySQLAdapter,
        'postgresql': PostgreSQLAdapter,
        'postgres': PostgreSQLAdapter,  # 别名
        'sqlserver': SQLServerAdapter,
        'mssql': SQLServerAdapter,  # 别名
    }
    
    @classmethod
    def create_adapter(cls, database_type: str, config: Dict[str, Any]) -> DatabaseAdapter:
        """
        创建数据库适配器
        
        Args:
            database_type: 数据库类型
            config: 数据库配置
            
        Returns:
            DatabaseAdapter: 数据库适配器实例
            
        Raises:
            ValueError: 不支持的数据库类型
        """
        database_type = database_type.lower()
        
        if database_type not in cls._adapters:
            supported_types = ', '.join(cls._adapters.keys())
            raise ValueError(f"不支持的数据库类型: {database_type}。支持的类型: {supported_types}")
        
        adapter_class = cls._adapters[database_type]
        return adapter_class(config)
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """
        获取支持的数据库类型
        
        Returns:
            List[str]: 支持的数据库类型列表
        """
        # 去除别名，只返回主要类型
        main_types = ['clickhouse', 'mysql', 'postgresql', 'sqlserver']
        return main_types
    
    @classmethod
    def register_adapter(cls, database_type: str, adapter_class: type):
        """
        注册新的数据库适配器
        
        Args:
            database_type: 数据库类型
            adapter_class: 适配器类
        """
        if not issubclass(adapter_class, DatabaseAdapter):
            raise ValueError("适配器类必须继承自DatabaseAdapter")
        
        cls._adapters[database_type.lower()] = adapter_class
    
    @classmethod
    def get_adapter_requirements(cls, database_type: str) -> List[str]:
        """
        获取数据库适配器的依赖包要求
        
        Args:
            database_type: 数据库类型
            
        Returns:
            List[str]: 依赖包列表
        """
        requirements = {
            'clickhouse': ['clickhouse-driver>=0.2.0'],
            'mysql': ['pymysql>=1.0.0'],
            'postgresql': ['psycopg2-binary>=2.8.0'],
            'postgres': ['psycopg2-binary>=2.8.0'],
            'sqlserver': ['pyodbc>=4.0.0'],
            'mssql': ['pyodbc>=4.0.0'],
        }
        
        return requirements.get(database_type.lower(), [])


# 导出便捷函数
def create_database_adapter(database_type: str, config: Dict[str, Any]) -> DatabaseAdapter:
    """
    创建数据库适配器的便捷函数
    
    Args:
        database_type: 数据库类型
        config: 数据库配置
        
    Returns:
        DatabaseAdapter: 数据库适配器实例
    """
    return DatabaseAdapterFactory.create_adapter(database_type, config)


def test_database_connection(database_type: str, config: Dict[str, Any]) -> bool:
    """
    测试数据库连接的便捷函数
    
    Args:
        database_type: 数据库类型
        config: 数据库配置
        
    Returns:
        bool: 连接是否成功
    """
    try:
        adapter = create_database_adapter(database_type, config)
        if adapter.connect():
            result = adapter.test_connection()
            adapter.disconnect()
            return result
        return False
    except Exception:
        return False
