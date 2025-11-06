"""
示例脚本：展示如何在Apache Airflow中安全地使用密钥后端

此脚本演示了多种安全处理敏感信息的方法：
1. 使用Airflow Variables
2. 使用Airflow Connections
3. 使用环境变量
4. 使用外部密钥管理系统（如AWS Secrets Manager, HashiCorp Vault等）
"""

import os
from airflow.models import Variable
from airflow.hooks.base_hook import BaseHook
import boto3
from botocore.exceptions import ClientError

def get_secret_from_variable(secret_name):
    """
    从Airflow Variables获取密钥
    
    Args:
        secret_name (str): 密钥名称
        
    Returns:
        str: 密钥值，如果未找到则返回None
    """
    try:
        secret_value = Variable.get(secret_name)
        return secret_value
    except Exception as e:
        print(f"无法从Variables获取密钥 {secret_name}: {e}")
        return None

def get_connection_creds(connection_id):
    """
    从Airflow Connections获取连接凭证
    
    Args:
        connection_id (str): 连接ID
        
    Returns:
        dict: 包含连接信息的字典
    """
    try:
        conn = BaseHook.get_connection(connection_id)
        return {
            'host': conn.host,
            'port': conn.port,
            'schema': conn.schema,
            'login': conn.login,
            'password': conn.password,
            'extra': conn.extra
        }
    except Exception as e:
        print(f"无法从Connections获取连接 {connection_id}: {e}")
        return None

def get_secret_from_env(env_var_name):
    """
    从环境变量获取密钥
    
    Args:
        env_var_name (str): 环境变量名称
        
    Returns:
        str: 环境变量值，如果未设置则返回None
    """
    try:
        secret_value = os.getenv(env_var_name)
        return secret_value
    except Exception as e:
        print(f"无法从环境变量获取密钥 {env_var_name}: {e}")
        return None

def get_secret_from_aws_secrets_manager(secret_name, region_name="us-east-1"):
    """
    从AWS Secrets Manager获取密钥
    
    Args:
        secret_name (str): 密钥名称
        region_name (str): AWS区域名称
        
    Returns:
        str: 密钥值，如果未找到则返回None
    """
    # 创建Secrets Manager客户端
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # 处理各种异常
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("密钥未找到")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("请求参数错误")
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("参数错误")
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("解密失败")
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("内部服务错误")
        else:
            print(f"AWS Secrets Manager错误: {e}")
        return None
    else:
        # 根据密钥类型返回相应值
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            # 二进制密钥处理
            import base64
            return base64.b64decode(get_secret_value_response['SecretBinary'])

def demonstrate_security_best_practices():
    """
    演示安全最佳实践
    """
    print("=== 安全最佳实践演示 ===")
    
    # 1. 优先使用环境变量
    print("1. 检查环境变量...")
    api_key = get_secret_from_env("API_KEY")
    if api_key:
        print("  成功从环境变量获取API密钥")
    else:
        print("  未能从环境变量获取API密钥")
    
    # 2. 使用Airflow Variables作为备选
    print("2. 检查Airflow Variables...")
    db_password = get_secret_from_variable("db_password")
    if db_password:
        print("  成功从Variables获取数据库密码")
    else:
        print("  未能从Variables获取数据库密码")
    
    # 3. 使用Airflow Connections存储连接信息
    print("3. 检查Airflow Connections...")
    db_creds = get_connection_creds("my_database")
    if db_creds:
        print("  成功从Connections获取数据库连接信息")
        print(f"  主机: {db_creds['host']}")
    else:
        print("  未能从Connections获取数据库连接信息")
    
    # 4. 对于高安全性要求的场景，使用外部密钥管理系统
    print("4. 检查AWS Secrets Manager...")
    # 注意：这需要有效的AWS凭证配置
    # aws_secret = get_secret_from_aws_secrets_manager("my-app/database-password")
    # if aws_secret:
    #     print("  成功从AWS Secrets Manager获取密钥")
    # else:
    #     print("  未能从AWS Secrets Manager获取密钥")
    
    print("\n=== 安全建议 ===")
    print("1. 永远不要在代码中硬编码敏感信息")
    print("2. 使用环境变量存储开发/测试环境的密钥")
    print("3. 在生产环境中使用专用的密钥管理系统")
    print("4. 定期轮换密钥和凭证")
    print("5. 限制对敏感信息的访问权限")
    print("6. 启用密钥的审计日志")

if __name__ == "__main__":
    demonstrate_security_best_practices()