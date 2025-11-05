# Day 9: 连接与密钥管理 - 实践练习

## 概述

今天的练习将帮助您掌握Airflow中连接和密钥管理的核心技能。通过实际操作，您将学会如何安全地配置和管理各种类型的连接，以及如何保护敏感信息。

## 练习目标

完成所有练习后，您将能够：
1. ✅ 创建和管理不同类型的连接
2. ✅ 安全地存储和使用敏感信息
3. ✅ 配置和使用密钥后端
4. ✅ 实现连接测试和诊断
5. ✅ 遵循安全最佳实践

---

## 练习1：连接创建和管理

### 目标
学会通过不同方式创建和管理Airflow连接。

### 场景
您需要为一个包含PostgreSQL数据库、AWS S3存储桶和HTTP API的数据管道配置连接。

### 任务

#### 1.1 通过CLI创建连接
编写脚本使用Airflow CLI创建以下连接：
- PostgreSQL数据库连接
- AWS S3连接
- HTTP API连接

```bash
# TODO: 在此处添加CLI命令创建连接
# 提示：使用 airflow connections add 命令
```

#### 1.2 通过Python代码创建连接
编写Python脚本创建相同的连接：

```python
from airflow.models import Connection
from airflow.utils.session import create_session

def create_connections():
    """
    创建练习所需的连接
    """
    # TODO: 创建PostgreSQL连接
    # 连接ID: exercise_postgres_conn
    # 类型: postgres
    # 主机: localhost
    # 端口: 5432
    # 用户名: airflow_user
    # 密码: secure_password123
    # 数据库: exercise_db
    
    # TODO: 创建AWS S3连接
    # 连接ID: exercise_s3_conn
    # 类型: aws
    # 登录: YOUR_AWS_ACCESS_KEY_ID
    # 密码: YOUR_AWS_SECRET_ACCESS_KEY
    # Extra参数: {"region_name": "us-east-1"}
    
    # TODO: 创建HTTP连接
    # 连接ID: exercise_http_conn
    # 类型: http
    # 主机: https://api.example.com
    # 登录: api_user
    # 密码: api_password123
    
    # 将连接保存到数据库
    with create_session() as session:
        # TODO: 添加连接到session并提交
        pass

# 调用函数创建连接
if __name__ == "__main__":
    create_connections()
    print("连接创建完成")
```

#### 1.3 通过环境变量创建连接
配置环境变量来创建连接：

```bash
# TODO: 设置环境变量创建PostgreSQL连接
# 环境变量格式: AIRFLOW_CONN_<CONN_ID>
# 提示: 连接ID为 env_postgres_conn
```

#### 1.4 验证连接
编写代码验证所有创建的连接：

```python
def test_connections():
    """
    测试所有创建的连接
    """
    connection_ids = [
        'exercise_postgres_conn',
        'exercise_s3_conn', 
        'exercise_http_conn',
        'env_postgres_conn'
    ]
    
    # TODO: 遍历连接ID并测试每个连接
    # 提示: 使用BaseHook.get_connection获取连接
    # 对于不同类型的连接，使用相应的Hook进行测试

# 调用函数测试连接
if __name__ == "__main__":
    test_connections()
    print("连接测试完成")
```

### 验证标准
- [ ] 成功创建了4个连接
- [ ] 每个连接都能通过测试
- [ ] 连接参数正确无误

---

## 练习2：密钥安全管理

### 目标
学会安全地管理敏感信息，避免密钥泄露。

### 场景
您的应用程序需要访问多个外部服务，需要安全地管理API密钥、数据库密码等敏感信息。

### 任务

#### 2.1 密钥加密存储
实现一个密钥管理类，用于安全地存储和检索敏感信息：

```python
import os
import base64
from cryptography.fernet import Fernet
from airflow.models import Variable

class SecureKeyManager:
    """
    安全密钥管理器
    """
    
    def __init__(self):
        """
        初始化密钥管理器
        """
        # TODO: 生成或加载加密密钥
        self.key = None
        self.cipher_suite = None
    
    def _generate_key(self):
        """
        生成新的加密密钥
        """
        # TODO: 生成Fernet密钥
        pass
    
    def _load_key(self):
        """
        从环境变量或文件加载密钥
        """
        # TODO: 从环境变量加载密钥，如果不存在则生成新密钥
        pass
    
    def store_secret(self, key_name, secret_value):
        """
        加密并存储敏感信息
        
        Args:
            key_name (str): 密钥名称
            secret_value (str): 敏感信息值
        """
        # TODO: 加密secret_value并存储到Airflow变量中
        pass
    
    def retrieve_secret(self, key_name):
        """
        检索并解密敏感信息
        
        Args:
            key_name (str): 密钥名称
            
        Returns:
            str: 解密后的敏感信息
        """
        # TODO: 从Airflow变量中获取加密数据并解密
        pass
    
    def rotate_key(self):
        """
        轮换加密密钥
        """
        # TODO: 实现密钥轮换逻辑
        pass

# 使用示例
if __name__ == "__main__":
    # 创建密钥管理器
    key_manager = SecureKeyManager()
    
    # 存储敏感信息
    key_manager.store_secret("database_password", "super_secret_password_123")
    key_manager.store_secret("api_key", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    # 检索敏感信息
    db_password = key_manager.retrieve_secret("database_password")
    api_key = key_manager.retrieve_secret("api_key")
    
    print("密钥存储和检索完成")
```

#### 2.2 环境变量安全使用
实现安全的环境变量管理：

```python
import os
from typing import Optional

class EnvironmentVariableManager:
    """
    环境变量安全管理器
    """
    
    @staticmethod
    def get_required_env_var(var_name: str, default: Optional[str] = None) -> str:
        """
        获取必需的环境变量，如果不存在则抛出异常
        
        Args:
            var_name (str): 环境变量名称
            default (Optional[str]): 默认值
            
        Returns:
            str: 环境变量值
            
        Raises:
            ValueError: 如果环境变量不存在且没有默认值
        """
        # TODO: 实现环境变量获取逻辑
        pass
    
    @staticmethod
    def load_env_file(file_path: str = ".env"):
        """
        从文件加载环境变量
        
        Args:
            file_path (str): 环境变量文件路径
        """
        # TODO: 实现从.env文件加载环境变量
        # 注意：不要在生产环境中使用此方法
        pass
    
    @staticmethod
    def mask_sensitive_value(value: str, show_chars: int = 4) -> str:
        """
        掩盖敏感信息显示
        
        Args:
            value (str): 原始值
            show_chars (int): 显示的字符数
            
        Returns:
            str: 掩盖后的值
        """
        # TODO: 实现敏感信息掩盖
        pass

# 使用示例
if __name__ == "__main__":
    # 安全获取环境变量
    try:
        db_host = EnvironmentVariableManager.get_required_env_var("DB_HOST", "localhost")
        db_port = EnvironmentVariableManager.get_required_env_var("DB_PORT", "5432")
        print(f"数据库配置: {db_host}:{db_port}")
    except ValueError as e:
        print(f"环境变量错误: {e}")
    
    # 掩盖敏感信息显示
    sensitive_data = "very_secret_password_123"
    masked_data = EnvironmentVariableManager.mask_sensitive_value(sensitive_data)
    print(f"掩盖后的敏感信息: {masked_data}")
```

#### 2.3 密钥后端配置
配置AWS Secrets Manager作为密钥后端：

```python
# airflow.cfg 配置示例
"""
[secrets]
backend = airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend
backend_kwargs = {
    "connections_prefix": "airflow/connections",
    "variables_prefix": "airflow/variables",
    "profile_name": "default"
}
"""

class AWSSecretsManagerSetup:
    """
    AWS Secrets Manager配置助手
    """
    
    def __init__(self):
        self.region = "us-east-1"
        self.profile = "default"
    
    def create_secret_structure(self):
        """
        创建AWS Secrets Manager中的密钥结构
        """
        # TODO: 实现创建密钥结构的逻辑
        # 1. 创建连接密钥
        # 2. 创建变量密钥
        # 3. 设置适当的标签和权限
        pass
    
    def migrate_existing_secrets(self):
        """
        迁移现有的连接和变量到AWS Secrets Manager
        """
        # TODO: 实现迁移现有密钥的逻辑
        # 1. 获取现有的Airflow连接
        # 2. 获取现有的Airflow变量
        # 3. 将它们存储到AWS Secrets Manager
        pass
    
    def validate_configuration(self):
        """
        验证AWS Secrets Manager配置
        """
        # TODO: 实现配置验证逻辑
        # 1. 测试连接到AWS Secrets Manager
        # 2. 验证密钥读取权限
        # 3. 验证密钥写入权限（如果需要）
        pass

# 配置验证代码
def test_aws_secrets_backend():
    """
    测试AWS Secrets Manager后端配置
    """
    # TODO: 实现测试逻辑
    # 1. 尝试从AWS Secrets Manager获取连接
    # 2. 验证获取的连接是否正确
    # 3. 检查错误处理
    pass
```

### 验证标准
- [ ] 成功实现了安全密钥管理类
- [ ] 正确使用了环境变量管理
- [ ] 完成了AWS Secrets Manager配置
- [ ] 所有敏感信息都被正确加密和保护

---

## 练习3：连接测试和诊断

### 目标
学会诊断和解决连接问题。

### 场景
您的数据管道中的某些任务开始失败，怀疑是连接问题导致的。

### 任务

#### 3.1 连接诊断工具
实现一个连接诊断工具：

```python
from airflow.hooks.base import BaseHook
from typing import Dict, List, Any
import logging

class ConnectionDiagnosticTool:
    """
    连接诊断工具
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def diagnose_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """
        诊断所有连接
        
        Returns:
            Dict[str, Dict[str, Any]]: 连接诊断结果
        """
        # TODO: 获取所有连接并进行诊断
        pass
    
    def diagnose_connection(self, conn_id: str) -> Dict[str, Any]:
        """
        诊断特定连接
        
        Args:
            conn_id (str): 连接ID
            
        Returns:
            Dict[str, Any]: 连接诊断结果
        """
        # TODO: 实现单个连接的诊断逻辑
        # 1. 获取连接对象
        # 2. 验证连接参数
        # 3. 测试连接
        # 4. 返回诊断结果
        pass
    
    def test_connection_connectivity(self, conn_id: str) -> bool:
        """
        测试连接连通性
        
        Args:
            conn_id (str): 连接ID
            
        Returns:
            bool: 连接是否成功
        """
        # TODO: 根据连接类型测试实际连通性
        # 对于数据库连接：尝试建立连接
        # 对于HTTP连接：发送简单请求
        # 对于文件系统连接：检查路径是否存在
        pass
    
    def generate_diagnostic_report(self, conn_ids: List[str] = None) -> str:
        """
        生成诊断报告
        
        Args:
            conn_ids (List[str], optional): 要诊断的连接ID列表
            
        Returns:
            str: 诊断报告
        """
        # TODO: 生成详细的诊断报告
        # 包括：连接状态、响应时间、错误信息等
        pass

# 使用示例
if __name__ == "__main__":
    # 创建诊断工具
    diagnostic_tool = ConnectionDiagnosticTool()
    
    # 诊断所有连接
    report = diagnostic_tool.generate_diagnostic_report()
    print(report)
    
    # 诊断特定连接
    result = diagnostic_tool.diagnose_connection("exercise_postgres_conn")
    print(f"连接诊断结果: {result}")
```

#### 3.2 错误处理和重试机制
实现健壮的连接错误处理：

```python
import time
import random
from functools import wraps
from typing import Callable, Any

def retry_on_connection_failure(max_retries: int = 3, backoff_factor: float = 1.0):
    """
    连接失败重试装饰器
    
    Args:
        max_retries (int): 最大重试次数
        backoff_factor (float): 退避因子
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # TODO: 实现重试逻辑
            # 1. 捕获连接相关的异常
            # 2. 实现指数退避重试
            # 3. 在最后一次失败时抛出原始异常
            pass
        return wrapper
    return decorator

class RobustConnectionHandler:
    """
    健壮的连接处理器
    """
    
    @retry_on_connection_failure(max_retries=3, backoff_factor=2.0)
    def execute_with_connection(self, conn_id: str, operation: Callable):
        """
        使用连接执行操作，带有重试机制
        
        Args:
            conn_id (str): 连接ID
            operation (Callable): 要执行的操作
            
        Returns:
            Any: 操作结果
        """
        # TODO: 实现连接操作执行逻辑
        # 1. 获取连接
        # 2. 执行操作
        # 3. 处理连接相关异常
        pass
    
    def handle_connection_timeout(self, conn_id: str, timeout: int = 30):
        """
        处理连接超时
        
        Args:
            conn_id (str): 连接ID
            timeout (int): 超时时间（秒）
        """
        # TODO: 实现连接超时处理
        # 1. 设置连接超时
        # 2. 处理超时异常
        # 3. 记录超时日志
        pass
    
    def circuit_breaker_pattern(self, conn_id: str, failure_threshold: int = 5):
        """
        熔断器模式实现
        
        Args:
            conn_id (str): 连接ID
            failure_threshold (int): 失败阈值
        """
        # TODO: 实现熔断器模式
        # 1. 跟踪连接失败次数
        # 2. 达到阈值时打开熔断器
        # 3. 在一段时间后尝试半开状态
        pass

# 使用示例
if __name__ == "__main__":
    handler = RobustConnectionHandler()
    
    # 使用重试机制执行操作
    def sample_operation(hook):
        # 模拟数据库操作
        return hook.get_records("SELECT 1")
    
    try:
        result = handler.execute_with_connection("exercise_postgres_conn", sample_operation)
        print(f"操作成功: {result}")
    except Exception as e:
        print(f"操作失败: {e}")
```

### 验证标准
- [ ] 实现了完整的连接诊断工具
- [ ] 正确处理了连接错误和异常
- [ ] 实现了重试机制和熔断器模式
- [ ] 能够生成详细的诊断报告

---

## 综合练习：安全数据管道

### 目标
构建一个安全的数据管道，综合运用所学的连接和密钥管理知识。

### 项目描述
构建一个从S3读取数据、处理数据并写入数据库的ETL管道，要求所有连接都安全配置。

### 项目要求

1. 使用环境变量或密钥后端管理所有敏感信息
2. 实现连接测试和健康检查
3. 包含错误处理和重试机制
4. 遵循安全最佳实践

### 代码框架

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable

# 导入自定义模块
from secure_key_manager import SecureKeyManager
from connection_diagnostic import ConnectionDiagnosticTool

# DAG定义
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'secure_etl_pipeline',
    default_args=default_args,
    description='安全的ETL数据管道',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def extract_data_from_s3(**context):
    """
    从S3提取数据
    """
    # TODO: 实现S3数据提取逻辑
    # 1. 安全获取S3连接信息
    # 2. 连接到S3
    # 3. 下载数据文件
    # 4. 处理连接错误
    pass

def transform_data(**context):
    """
    转换数据
    """
    # TODO: 实现数据转换逻辑
    # 1. 读取提取的数据
    # 2. 执行数据清洗和转换
    # 3. 准备加载到数据库的数据
    pass

def load_data_to_database(**context):
    """
    将数据加载到数据库
    """
    # TODO: 实现数据库加载逻辑
    # 1. 安全获取数据库连接信息
    # 2. 连接到数据库
    # 3. 执行批量插入操作
    # 4. 处理连接错误
    pass

def pipeline_health_check(**context):
    """
    管道健康检查
    """
    # TODO: 实现健康检查逻辑
    # 1. 检查所有必需的连接
    # 2. 验证密钥可用性
    # 3. 报告健康状态
    pass

# 任务定义
health_check_task = PythonOperator(
    task_id='health_check',
    python_callable=pipeline_health_check,
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data_from_s3,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data_to_database,
    dag=dag,
)

# 任务依赖
health_check_task >> extract_task >> transform_task >> load_task
```

### 项目交付物
1. 完整的DAG代码
2. 连接和密钥配置文档
3. 健康检查和监控脚本
4. 错误处理和恢复机制

### 成功标准
- [ ] ETL管道能正常运行
- [ ] 所有敏感信息都得到安全保护
- [ ] 实现了完善的错误处理机制
- [ ] 包含健康检查和监控功能

---

## 总结

通过今天的练习，您已经掌握了：
1. 如何创建和管理各种类型的连接
2. 如何安全地存储和使用敏感信息
3. 如何配置和使用密钥后端
4. 如何诊断和解决连接问题
5. 如何构建安全可靠的数据管道

这些技能对于在生产环境中安全地使用Airflow至关重要。