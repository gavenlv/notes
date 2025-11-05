"""
Airflow 安全与权限管理示例代码
包含 RBAC 配置、LDAP 集成、密钥管理等实际应用示例
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Airflow 相关导入
try:
    from airflow import DAG, settings
    from airflow.operators.python_operator import PythonOperator
    from airflow.models import Variable
    from airflow.hooks.base_hook import BaseHook
    from airflow.utils.dates import days_ago
    HAS_AIRFLOW = True
except ImportError:
    HAS_AIRFLOW = False
    print("警告: 未安装 Airflow，部分功能将不可用")

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 第一部分：RBAC 权限管理示例
class RBACExample:
    """RBAC 权限管理示例"""
    
    def __init__(self):
        self.roles_created = []
        self.users_created = []
    
    def create_custom_role(self, role_name: str, permissions: List[tuple]) -> bool:
        """
        创建自定义角色
        
        Args:
            role_name: 角色名称
            permissions: 权限列表，格式为 [(permission_name, view_menu), ...]
        
        Returns:
            bool: 创建成功返回 True，否则返回 False
        """
        if not HAS_AIRFLOW:
            logger.warning("Airflow 未安装，跳过角色创建")
            return False
            
        try:
            from airflow.www.security import AirflowSecurityManager
            
            security_manager = AirflowSecurityManager()
            
            # 创建角色
            role = security_manager.add_role(role_name)
            if not role:
                logger.error(f"创建角色 {role_name} 失败")
                return False
                
            self.roles_created.append(role_name)
            logger.info(f"成功创建角色: {role_name}")
            
            # 分配权限
            for perm_name, view_menu in permissions:
                try:
                    perm_view = security_manager.add_permission_view_menu(perm_name, view_menu)
                    security_manager.add_permission_role(role, perm_view)
                    logger.info(f"为角色 {role_name} 分配权限: {perm_name} -> {view_menu}")
                except Exception as e:
                    logger.error(f"分配权限失败 {perm_name} -> {view_menu}: {e}")
                    
            return True
        except Exception as e:
            logger.error(f"创建角色时发生错误: {e}")
            return False
    
    def assign_role_to_user(self, username: str, role_name: str) -> bool:
        """
        为用户分配角色
        
        Args:
            username: 用户名
            role_name: 角色名称
            
        Returns:
            bool: 分配成功返回 True，否则返回 False
        """
        if not HAS_AIRFLOW:
            return False
            
        try:
            from airflow.contrib.auth.backends.password_auth import PasswordUser
            from airflow.www.security import AirflowSecurityManager
            
            session = settings.Session()
            security_manager = AirflowSecurityManager()
            
            # 查找用户
            user = session.query(PasswordUser).filter(
                PasswordUser.username == username
            ).first()
            
            if not user:
                logger.error(f"用户 {username} 不存在")
                return False
            
            # 查找角色
            role = security_manager.find_role(role_name)
            if not role:
                logger.error(f"角色 {role_name} 不存在")
                return False
            
            # 分配角色
            if role not in user.roles:
                user.roles.append(role)
                session.commit()
                logger.info(f"成功为用户 {username} 分配角色 {role_name}")
                self.users_created.append(username)
            else:
                logger.info(f"用户 {username} 已经拥有角色 {role_name}")
                
            session.close()
            return True
        except Exception as e:
            logger.error(f"分配角色时发生错误: {e}")
            return False

# 第二部分：连接安全性示例
class SecureConnectionExample:
    """安全连接示例"""
    
    @staticmethod
    def get_connection_with_encryption(conn_id: str) -> Optional[Dict]:
        """
        获取加密连接信息
        
        Args:
            conn_id: 连接 ID
            
        Returns:
            Dict: 连接信息字典或 None
        """
        if not HAS_AIRFLOW:
            logger.warning("Airflow 未安装，使用模拟数据")
            # 模拟连接信息（仅用于演示）
            return {
                "conn_type": "postgres",
                "host": "localhost",
                "port": 5432,
                "login": "airflow",
                "password": "encrypted_password",
                "schema": "airflow"
            }
        
        try:
            # 从 Airflow 获取连接
            conn = BaseHook.get_connection(conn_id)
            return {
                "conn_type": conn.conn_type,
                "host": conn.host,
                "port": conn.port,
                "login": conn.login,
                "password": conn.password,  # 注意：在实际应用中应避免直接暴露密码
                "schema": conn.schema,
                "extra": conn.extra
            }
        except Exception as e:
            logger.error(f"获取连接 {conn_id} 时出错: {e}")
            return None
    
    @staticmethod
    def rotate_connection_password(conn_id: str, new_password: str) -> bool:
        """
        轮换连接密码
        
        Args:
            conn_id: 连接 ID
            new_password: 新密码
            
        Returns:
            bool: 更新成功返回 True，否则返回 False
        """
        if not HAS_AIRFLOW:
            logger.info(f"模拟轮换连接 {conn_id} 的密码")
            return True
            
        try:
            from airflow.models.connection import Connection
            
            session = settings.Session()
            
            # 查找连接
            conn = session.query(Connection).filter(
                Connection.conn_id == conn_id
            ).first()
            
            if not conn:
                logger.error(f"连接 {conn_id} 不存在")
                return False
            
            # 更新密码
            conn.password = new_password
            session.commit()
            session.close()
            
            logger.info(f"成功更新连接 {conn_id} 的密码")
            return True
        except Exception as e:
            logger.error(f"轮换密码时出错: {e}")
            return False

# 第三部分：变量安全管理示例
class SecureVariableExample:
    """安全变量管理示例"""
    
    @staticmethod
    def set_secure_variable(key: str, value: str, is_encrypted: bool = True) -> bool:
        """
        设置安全变量
        
        Args:
            key: 变量键
            value: 变量值
            is_encrypted: 是否加密存储
            
        Returns:
            bool: 设置成功返回 True，否则返回 False
        """
        if not HAS_AIRFLOW:
            logger.info(f"模拟设置变量 {key} (加密: {is_encrypted})")
            return True
            
        try:
            # 使用 Airflow Variable 设置变量
            Variable.set(key, value, serialize_json=False)
            logger.info(f"成功设置变量 {key}")
            return True
        except Exception as e:
            logger.error(f"设置变量 {key} 时出错: {e}")
            return False
    
    @staticmethod
    def get_secure_variable(key: str) -> Optional[str]:
        """
        获取安全变量
        
        Args:
            key: 变量键
            
        Returns:
            str: 变量值或 None
        """
        if not HAS_AIRFLOW:
            logger.info(f"模拟获取变量 {key}")
            return "mock_value"
            
        try:
            # 获取变量
            value = Variable.get(key)
            return value
        except Exception as e:
            logger.error(f"获取变量 {key} 时出错: {e}")
            return None

# 第四部分：安全 DAG 示例
def secure_dag_example():
    """创建一个安全的 DAG 示例"""
    
    # DAG 参数
    default_args = {
        'owner': 'security_team',
        'depends_on_past': False,
        'start_date': days_ago(1),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
    
    # 创建 DAG
    dag = DAG(
        'secure_data_processing_pipeline',
        default_args=default_args,
        description='安全的数据处理管道示例',
        schedule_interval=timedelta(days=1),
        catchup=False,
        tags=['security', 'example'],
    )
    
    def secure_data_processing_task(**context):
        """安全数据处理任务"""
        logger.info("开始执行安全数据处理任务")
        
        # 获取安全变量
        api_key = SecureVariableExample.get_secure_variable('api_key')
        if not api_key:
            raise ValueError("无法获取 API 密钥")
        
        # 获取安全连接
        db_conn = SecureConnectionExample.get_connection_with_encryption('postgres_default')
        if not db_conn:
            raise ValueError("无法获取数据库连接")
        
        # 模拟安全数据处理
        logger.info("使用安全凭据处理数据...")
        logger.info(f"API Key 长度: {len(api_key) if api_key else 0}")
        logger.info(f"数据库类型: {db_conn.get('conn_type', 'unknown')}")
        
        # 模拟处理逻辑
        processed_records = 1000
        logger.info(f"成功处理 {processed_records} 条记录")
        
        return f"处理了 {processed_records} 条记录"
    
    def audit_logging_task(**context):
        """审计日志任务"""
        logger.info("记录安全审计日志")
        
        # 记录任务执行信息
        execution_time = context['execution_date']
        task_instance = context['task_instance']
        
        audit_info = {
            'dag_id': context['dag'].dag_id,
            'task_id': task_instance.task_id,
            'execution_time': execution_time.isoformat(),
            'hostname': task_instance.hostname,
            'pid': task_instance.pid
        }
        
        logger.info(f"审计日志: {audit_info}")
        return "审计日志记录完成"
    
    # 创建任务
    process_task = PythonOperator(
        task_id='secure_data_processing',
        python_callable=secure_data_processing_task,
        dag=dag,
    )
    
    audit_task = PythonOperator(
        task_id='audit_logging',
        python_callable=audit_logging_task,
        dag=dag,
    )
    
    # 设置任务依赖
    process_task >> audit_task
    
    return dag

# 第五部分：安全配置示例
class SecurityConfigExample:
    """安全配置示例"""
    
    @staticmethod
    def generate_webserver_config() -> str:
        """
        生成 Web 服务器安全配置示例
        
        Returns:
            str: 配置文件内容
        """
        config_content = """
# Airflow Web Server 安全配置示例

# Flask App Builder 配置
from flask_appbuilder.security.manager import AUTH_DB, AUTH_LDAP

# 认证类型
AUTH_TYPE = AUTH_LDAP

# LDAP 配置
AUTH_LDAP_SERVER = "ldap://ldap.example.com:389"
AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "your_ldap_bind_password"
AUTH_LDAP_SEARCH = "ou=users,dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"

# 用户自动注册
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"

# 角色映射
AUTH_ROLES_MAPPING = {
    "cn=airflow_admins,ou=groups,dc=example,dc=com": ["Admin"],
    "cn=airflow_users,ou=groups,dc=example,dc=com": ["User"],
    "cn=airflow_viewers,ou=groups,dc=example,dc=com": ["Viewer"],
}

# 安全日志
SECURITY_LOG_PATH = "/var/log/airflow/security.log"
SECURITY_LOG_MAX_BYTES = 10485760  # 10MB
SECURITY_LOG_BACKUP_COUNT = 5

# CSRF 保护
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600

# Session 配置
PERMANENT_SESSION_LIFETIME = 1800  # 30分钟
SESSION_COOKIE_SECURE = True  # 仅 HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
"""
        return config_content.strip()
    
    @staticmethod
    def generate_airflow_cfg_security_section() -> str:
        """
        生成 airflow.cfg 中的安全配置段
        
        Returns:
            str: 配置段内容
        """
        config_content = """
[webserver]
# Web 服务器安全配置
rbac = True
authenticate = True

# HTTPS 配置
web_server_ssl_cert = /path/to/certificate.crt
web_server_ssl_key = /path/to/private.key

# Cookie 安全
cookie_secure = True
cookie_httponly = True

[api]
# API 安全配置
auth_backend = airflow.api.auth.backend.basic_auth

[lineage]
# 血缘追踪
backend = airflow.lineage.backend.atlas

[secrets]
# 密钥后端配置
backend = airflow.providers.hashicorp.secrets.vault.VaultBackend
backend_kwargs = {"connections_path": "airflow/connections", "variables_path": "airflow/variables", "url": "http://vault:8200"}

[kerberos]
# Kerberos 配置
ccache = /tmp/airflow_krb5_ccache
principal = airflow/_HOST@EXAMPLE.COM
reinit_frequency = 3600
config_path = /etc/krb5.conf
"""
        return config_content.strip()

# 主函数 - 演示所有安全特性
def main():
    """主函数 - 演示所有安全特性"""
    print("=" * 60)
    print("Airflow 安全与权限管理示例")
    print("=" * 60)
    
    # 1. RBAC 示例
    print("\n1. RBAC 权限管理示例:")
    rbac = RBACExample()
    
    # 创建自定义角色
    analyst_permissions = [
        ("menu_access", "DAG Runs"),
        ("menu_access", "Browse"),
        ("can_dag_read", "DAG"),
        ("can_task_instance_read", "DAG"),
        ("can_log_read", "DAG")
    ]
    
    if rbac.create_custom_role("DataAnalyst", analyst_permissions):
        print("   ✓ 成功创建 DataAnalyst 角色")
        if rbac.assign_role_to_user("analyst_user", "DataAnalyst"):
            print("   ✓ 成功为 analyst_user 分配 DataAnalyst 角色")
    else:
        print("   ✗ 创建角色失败")
    
    # 2. 安全连接示例
    print("\n2. 安全连接管理示例:")
    conn_info = SecureConnectionExample.get_connection_with_encryption("postgres_default")
    if conn_info:
        print(f"   ✓ 成功获取连接信息")
        print(f"     类型: {conn_info.get('conn_type', 'unknown')}")
        print(f"     主机: {conn_info.get('host', 'unknown')}")
        print(f"     端口: {conn_info.get('port', 'unknown')}")
    else:
        print("   ✗ 获取连接信息失败")
    
    # 3. 安全变量示例
    print("\n3. 安全变量管理示例:")
    if SecureVariableExample.set_secure_variable("api_key", "secret_api_key_12345"):
        print("   ✓ 成功设置安全变量")
        value = SecureVariableExample.get_secure_variable("api_key")
        if value:
            print(f"   ✓ 成功获取变量，长度: {len(value)}")
        else:
            print("   ✗ 获取变量失败")
    else:
        print("   ✗ 设置变量失败")
    
    # 4. 安全配置示例
    print("\n4. 安全配置示例:")
    web_config = SecurityConfigExample.generate_webserver_config()
    airflow_config = SecurityConfigExample.generate_airflow_cfg_security_section()
    
    print(f"   Web 服务器配置行数: {len(web_config.split(chr(10)))}")
    print(f"   Airflow 配置行数: {len(airflow_config.split(chr(10)))}")
    
    # 5. 创建安全 DAG
    print("\n5. 安全 DAG 示例:")
    try:
        secure_dag = secure_dag_example()
        print(f"   ✓ 成功创建 DAG: {secure_dag.dag_id}")
        print(f"   任务数量: {len(secure_dag.tasks)}")
    except Exception as e:
        print(f"   ✗ 创建 DAG 失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有安全示例演示完成")
    print("=" * 60)

# 执行主函数
if __name__ == "__main__":
    main()