# 第二十一章：故障排除与诊断

## 21.1 故障排除概述

在 Apache Superset 的日常使用和运维过程中，难免会遇到各种问题和故障。有效的故障排除和诊断能力是保障系统稳定运行的关键技能。本章将详细介绍 Superset 中常见的故障类型、诊断方法和解决方案。

### 故障排除的重要性

良好的故障排除能力可以帮助我们：

1. **快速定位问题**：准确识别问题根源，缩短故障恢复时间
2. **预防潜在风险**：通过分析故障原因，提前发现和消除隐患
3. **提升系统可靠性**：建立完善的故障处理机制，提高系统稳定性
4. **优化运维效率**：积累故障处理经验，形成标准化的处理流程

### 故障分类与处理原则

#### 故障分类

按照故障的影响范围和严重程度，可以将 Superset 故障分为：

1. **系统级故障**：影响整个 Superset 服务的运行
2. **功能级故障**：影响特定功能模块的正常使用
3. **性能级故障**：不影响功能但影响使用体验的问题
4. **配置级故障**：由于配置不当导致的问题

#### 处理原则

1. **快速响应**：建立故障响应机制，及时发现和处理问题
2. **分级处理**：根据故障严重程度采用不同的处理策略
3. **记录分析**：详细记录故障现象和处理过程，便于后续分析
4. **预防为主**：通过监控和预警机制，尽可能预防故障发生

## 21.2 常见启动故障

### 应用无法启动

#### 端口占用问题

```bash
# 检查端口占用情况
netstat -an | grep :8088

# 或在 Linux/macOS 上使用
lsof -i :8088

# 在 Windows 上使用
netstat -ano | findstr :8088

# 杀死占用端口的进程（Linux/macOS）
kill -9 <PID>

# 在 Windows 上杀死进程
taskkill /PID <PID> /F
```

#### 依赖包缺失

```bash
# 检查 Python 环境
python --version
pip list | grep superset

# 重新安装依赖
pip install -r requirements.txt

# 或重新安装 Superset
pip install apache-superset

# 检查虚拟环境
which python
which pip
```

#### 数据库连接失败

```python
# database_connection_test.py
import psycopg2
import pymysql
import sqlite3
from sqlalchemy import create_engine

def test_database_connection(connection_string):
    """测试数据库连接"""
    try:
        engine = create_engine(connection_string)
        connection = engine.connect()
        result = connection.execute("SELECT 1")
        print("Database connection successful!")
        connection.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# 测试不同类型的数据库连接
test_cases = {
    'postgresql': 'postgresql://user:password@localhost:5432/superset',
    'mysql': 'mysql://user:password@localhost:3306/superset',
    'sqlite': 'sqlite:///superset.db'
}

for db_type, conn_string in test_cases.items():
    print(f"\nTesting {db_type} connection:")
    test_database_connection(conn_string)
```

### 配置文件错误

```python
# config_validator.py
import os
import sys
from superset.config import *

def validate_superset_config():
    """验证 Superset 配置文件"""
    errors = []
    
    # 检查必需的配置项
    required_configs = [
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI',
        'REDIS_HOST',
        'REDIS_PORT'
    ]
    
    for config in required_configs:
        if not globals().get(config):
            errors.append(f"Missing required configuration: {config}")
    
    # 检查 SECRET_KEY
    if len(SECRET_KEY) < 16:
        errors.append("SECRET_KEY should be at least 16 characters long")
    
    # 检查数据库 URI 格式
    if 'SQLALCHEMY_DATABASE_URI' in globals():
        uri = SQLALCHEMY_DATABASE_URI
        if not uri.startswith(('sqlite', 'postgresql', 'mysql')):
            errors.append("Invalid database URI format")
    
    # 检查缓存配置
    if 'CACHE_CONFIG' in globals():
        cache_config = CACHE_CONFIG
        if 'CACHE_TYPE' not in cache_config:
            errors.append("CACHE_CONFIG missing CACHE_TYPE")
    
    return errors

# 执行配置验证
if __name__ == "__main__":
    validation_errors = validate_superset_config()
    if validation_errors:
        print("Configuration validation failed:")
        for error in validation_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Configuration validation passed!")
```

## 21.3 数据源连接问题

### 数据库连接超时

```python
# connection_timeout_diagnoser.py
import time
import traceback
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, TimeoutError

class ConnectionTimeoutDiagnoser:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.engine = create_engine(connection_string, pool_pre_ping=True)
        
    def diagnose_connection(self, timeout=30):
        """诊断连接问题"""
        print("Starting connection diagnosis...")
        
        # 1. 测试基本连接
        start_time = time.time()
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
                elapsed = time.time() - start_time
                print(f"✓ Basic connection test passed ({elapsed:.2f}s)")
        except Exception as e:
            print(f"✗ Basic connection test failed: {e}")
            self.analyze_connection_error(e)
            return False
            
        # 2. 测试查询性能
        queries = [
            "SELECT COUNT(*) FROM information_schema.tables",
            "SELECT VERSION()",
            "SHOW STATUS LIKE 'Threads_connected'"
        ]
        
        for i, query in enumerate(queries, 1):
            try:
                start_time = time.time()
                with self.engine.connect() as connection:
                    result = connection.execute(query)
                    elapsed = time.time() - start_time
                    print(f"✓ Query {i} executed successfully ({elapsed:.2f}s)")
            except Exception as e:
                print(f"✗ Query {i} failed: {e}")
                self.analyze_query_error(e)
                
        return True
        
    def analyze_connection_error(self, error):
        """分析连接错误"""
        error_str = str(error).lower()
        
        if "timeout" in error_str or "timed out" in error_str:
            print("  → Connection timeout detected")
            print("  → Possible causes:")
            print("    - Network connectivity issues")
            print("    - Database server overload")
            print("    - Firewall blocking connections")
            print("  → Solutions:")
            print("    - Check network connectivity")
            print("    - Increase connection timeout settings")
            print("    - Optimize database performance")
            
        elif "authentication" in error_str or "access denied" in error_str:
            print("  → Authentication failure detected")
            print("  → Check username, password, and database permissions")
            
        elif "host" in error_str or "name or service not known" in error_str:
            print("  → Host resolution failure")
            print("  → Verify database host address and DNS settings")
            
    def analyze_query_error(self, error):
        """分析查询错误"""
        if isinstance(error, OperationalError):
            print("  → Operational database error")
        elif isinstance(error, TimeoutError):
            print("  → Query execution timeout")
        else:
            print(f"  → Unexpected error type: {type(error).__name__}")

# 使用示例
diagnoser = ConnectionTimeoutDiagnoser("postgresql://user:pass@localhost:5432/db")
diagnoser.diagnose_connection()
```

### SSL/TLS 连接问题

```python
# ssl_connection_fix.py
import ssl
import urllib3
from sqlalchemy import create_engine

def configure_ssl_connection(connection_string, ssl_mode='require'):
    """配置 SSL 连接"""
    # 禁用 SSL 警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 根据数据库类型添加 SSL 参数
    if connection_string.startswith('postgresql'):
        if '?' in connection_string:
            connection_string += f"&sslmode={ssl_mode}"
        else:
            connection_string += f"?sslmode={ssl_mode}"
            
    elif connection_string.startswith('mysql'):
        if '?' in connection_string:
            connection_string += f"&ssl_disabled=false"
        else:
            connection_string += f"?ssl_disabled=false"
            
    return connection_string

def test_ssl_connection(connection_string):
    """测试 SSL 连接"""
    try:
        # 配置 SSL
        ssl_conn_string = configure_ssl_connection(connection_string)
        
        # 创建引擎
        engine = create_engine(
            ssl_conn_string,
            connect_args={
                "ssl": {
                    "ssl_ca": "/path/to/ca-cert.pem",
                    "ssl_cert": "/path/to/client-cert.pem",
                    "ssl_key": "/path/to/client-key.pem"
                }
            } if 'mysql' in connection_string else {}
        )
        
        # 测试连接
        with engine.connect() as connection:
            result = connection.execute("SELECT VERSION()")
            version = result.fetchone()[0]
            print(f"SSL connection successful! Database version: {version}")
            return True
            
    except ssl.SSLError as e:
        print(f"SSL connection failed: {e}")
        print("Troubleshooting steps:")
        print("1. Verify SSL certificate paths")
        print("2. Check certificate validity and permissions")
        print("3. Ensure SSL is enabled on database server")
        return False
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# 使用示例
test_connection_string = "postgresql://user:pass@secure-host:5432/db"
test_ssl_connection(test_connection_string)
```

## 21.4 查询执行问题

### 查询失败诊断

```python
# query_failure_analyzer.py
import re
import json
import logging
from datetime import datetime
from superset import db
from superset.models.core import Query

class QueryFailureAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_failed_query(self, query_id):
        """分析失败的查询"""
        try:
            # 获取查询信息
            query = db.session.query(Query).filter(Query.id == query_id).first()
            if not query:
                return {"error": "Query not found"}
                
            analysis = {
                "query_id": query.id,
                "sql": query.sql,
                "error_message": query.error_message,
                "execution_time": query.end_time - query.start_time if query.end_time else None,
                "user": query.user.username if query.user else "Unknown",
                "database": query.database.database_name if query.database else "Unknown"
            }
            
            # 错误类型分析
            error_analysis = self.analyze_error_message(query.error_message)
            analysis.update(error_analysis)
            
            # SQL 结构分析
            sql_analysis = self.analyze_sql_structure(query.sql)
            analysis.update(sql_analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze query {query_id}: {e}")
            return {"error": str(e)}
            
    def analyze_error_message(self, error_message):
        """分析错误消息"""
        if not error_message:
            return {"error_type": "unknown", "suggestions": []}
            
        error_lower = error_message.lower()
        suggestions = []
        
        # 语法错误
        if "syntax error" in error_lower or "syntax" in error_lower:
            return {
                "error_type": "syntax_error",
                "suggestions": [
                    "Check SQL syntax for typos",
                    "Verify column and table names",
                    "Ensure proper use of keywords"
                ]
            }
            
        # 权限错误
        if "permission denied" in error_lower or "access denied" in error_lower:
            return {
                "error_type": "permission_error",
                "suggestions": [
                    "Verify database user permissions",
                    "Check table/column access rights",
                    "Contact database administrator"
                ]
            }
            
        # 表不存在
        if "does not exist" in error_lower or "not found" in error_lower:
            return {
                "error_type": "object_not_found",
                "suggestions": [
                    "Verify table and column names",
                    "Check database schema",
                    "Ensure proper case sensitivity"
                ]
            }
            
        # 数据类型错误
        if "type mismatch" in error_lower or "cannot cast" in error_lower:
            return {
                "error_type": "type_error",
                "suggestions": [
                    "Check data type compatibility",
                    "Verify column data types",
                    "Use explicit type casting"
                ]
            }
            
        return {
            "error_type": "other",
            "suggestions": ["Review the error message for specific details"]
        }
        
    def analyze_sql_structure(self, sql):
        """分析 SQL 结构"""
        analysis = {
            "query_type": self.identify_query_type(sql),
            "complexity_score": self.calculate_complexity(sql),
            "potential_issues": []
        }
        
        # 检查潜在问题
        if "SELECT *" in sql.upper():
            analysis["potential_issues"].append("Avoid using SELECT * for better performance")
            
        if sql.count("JOIN") > 3:
            analysis["potential_issues"].append("Consider simplifying complex joins")
            
        if "DISTINCT" in sql.upper() and "GROUP BY" in sql.upper():
            analysis["potential_issues"].append("Redundant DISTINCT with GROUP BY")
            
        return analysis
        
    def identify_query_type(self, sql):
        """识别查询类型"""
        sql_upper = sql.upper().strip()
        if sql_upper.startswith("SELECT"):
            return "SELECT"
        elif sql_upper.startswith("INSERT"):
            return "INSERT"
        elif sql_upper.startswith("UPDATE"):
            return "UPDATE"
        elif sql_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "OTHER"
            
    def calculate_complexity(self, sql):
        """计算查询复杂度"""
        score = 0
        
        # JOIN 数量
        join_count = len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE))
        score += join_count * 2
        
        # 子查询数量
        subquery_count = sql.count('(') - sql.count(')')
        score += max(0, subquery_count)
        
        # 条件复杂度
        where_match = re.search(r'WHERE\s+(.*?)(?:GROUP BY|ORDER BY|LIMIT|$)', sql, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_text = where_match.group(1)
            condition_count = len(re.findall(r'\b(AND|OR)\b', where_text, re.IGNORECASE))
            score += condition_count
            
        return score

# 使用示例
analyzer = QueryFailureAnalyzer()
result = analyzer.analyze_failed_query(12345)
print(json.dumps(result, indent=2, default=str))
```

### 查询性能问题

```python
# query_performance_troubleshooter.py
import time
import psutil
from sqlalchemy import text

class QueryPerformanceTroubleshooter:
    def __init__(self, engine):
        self.engine = engine
        
    def troubleshoot_slow_query(self, query, params=None):
        """诊断慢查询"""
        print("Starting slow query troubleshooting...")
        
        # 1. 收集系统资源基线
        baseline_resources = self.get_system_resources()
        print(f"Baseline resources: CPU {baseline_resources['cpu']}%, "
              f"Memory {baseline_resources['memory']}%")
        
        # 2. 执行查询并计时
        start_time = time.time()
        start_resources = self.get_system_resources()
        
        try:
            with self.engine.connect() as connection:
                # 执行查询
                result = connection.execute(text(query), params or {})
                rows_fetched = len(result.fetchall())
                
                end_time = time.time()
                end_resources = self.get_system_resources()
                
                execution_time = end_time - start_time
                print(f"Query executed in {execution_time:.2f} seconds")
                print(f"Rows fetched: {rows_fetched}")
                
                # 3. 分析资源使用变化
                resource_diff = self.calculate_resource_difference(
                    start_resources, end_resources
                )
                print(f"Resource usage during query:")
                print(f"  CPU: {resource_diff['cpu_change']:+.1f}%")
                print(f"  Memory: {resource_diff['memory_change']:+.1f}%")
                
                # 4. 获取查询执行计划（PostgreSQL 示例）
                explain_query = f"EXPLAIN ANALYZE {query}"
                plan_result = connection.execute(text(explain_query), params or {})
                plan = plan_result.fetchall()
                
                # 5. 分析执行计划
                plan_analysis = self.analyze_execution_plan(plan)
                
                return {
                    "execution_time": execution_time,
                    "rows_fetched": rows_fetched,
                    "resource_usage": resource_diff,
                    "plan_analysis": plan_analysis,
                    "recommendations": self.generate_recommendations(
                        execution_time, plan_analysis, resource_diff
                    )
                }
                
        except Exception as e:
            print(f"Query execution failed: {e}")
            return {"error": str(e)}
            
    def get_system_resources(self):
        """获取系统资源使用情况"""
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk_io": psutil.disk_io_counters()
        }
        
    def calculate_resource_difference(self, start, end):
        """计算资源使用差异"""
        return {
            "cpu_change": end["cpu"] - start["cpu"],
            "memory_change": end["memory"] - start["memory"]
        }
        
    def analyze_execution_plan(self, plan_rows):
        """分析执行计划"""
        analysis = {
            "steps": [],
            "cost_estimates": [],
            "actual_times": [],
            "warnings": []
        }
        
        for row in plan_rows:
            plan_text = str(row[0])
            analysis["steps"].append(plan_text)
            
            # 提取成本估算
            cost_match = re.search(r'cost=(\d+\.\d+)\.\.(\d+\.\d+)', plan_text)
            if cost_match:
                analysis["cost_estimates"].append(float(cost_match.group(2)))
                
            # 提取实际执行时间
            time_match = re.search(r'actual time=(\d+\.\d+)\.\.(\d+\.\d+)', plan_text)
            if time_match:
                analysis["actual_times"].append(float(time_match.group(2)))
                
            # 检查警告
            if "Seq Scan" in plan_text and "Filter:" not in plan_text:
                analysis["warnings"].append("Sequential scan without filter detected")
                
            if "Sort Method: external" in plan_text:
                analysis["warnings"].append("External sort used, consider adding indexes")
                
        return analysis
        
    def generate_recommendations(self, execution_time, plan_analysis, resource_diff):
        """生成优化建议"""
        recommendations = []
        
        # 基于执行时间的建议
        if execution_time > 10:
            recommendations.append("Query execution time is high, consider optimization")
            
        # 基于执行计划的建议
        for warning in plan_analysis["warnings"]:
            recommendations.append(warning)
            
        # 基于资源使用的建议
        if resource_diff["cpu_change"] > 50:
            recommendations.append("High CPU usage detected during query execution")
            
        if resource_diff["memory_change"] > 20:
            recommendations.append("Significant memory usage increase detected")
            
        # 通用优化建议
        recommendations.extend([
            "Consider adding appropriate indexes",
            "Limit result set size with LIMIT clause",
            "Avoid SELECT * in production queries",
            "Review JOIN conditions and order"
        ])
        
        return recommendations

# 使用示例
# troubleshooter = QueryPerformanceTroubleshooter(engine)
# result = troubleshooter.troubleshoot_slow_query("SELECT * FROM large_table")
```

## 21.5 权限和安全问题

### 用户权限故障

```python
# permission_troubleshooter.py
from superset import security_manager, db
from superset.models.core import User, Role
from flask_appbuilder.security.sqla.models import Permission, PermissionView, ViewMenu

class PermissionTroubleshooter:
    def __init__(self):
        self.security_manager = security_manager
        
    def troubleshoot_user_access(self, username, resource, action):
        """诊断用户访问权限"""
        print(f"Troubleshooting access for user '{username}' to '{resource}' with action '{action}'")
        
        # 1. 获取用户信息
        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            return {"error": f"User '{username}' not found"}
            
        print(f"User found: {user.username} (ID: {user.id})")
        
        # 2. 检查用户角色
        user_roles = [role.name for role in user.roles]
        print(f"User roles: {user_roles}")
        
        # 3. 检查角色权限
        permissions = []
        for role in user.roles:
            role_perms = self.get_role_permissions(role)
            permissions.extend(role_perms)
            
        print(f"Total permissions: {len(permissions)}")
        
        # 4. 检查特定资源权限
        has_access = self.check_resource_access(user, resource, action)
        print(f"Has access: {has_access}")
        
        # 5. 生成诊断报告
        return self.generate_access_report(user, resource, action, has_access, permissions)
        
    def get_role_permissions(self, role):
        """获取角色权限"""
        permissions = []
        for perm_view in role.permissions:
            if perm_view.permission and perm_view.view_menu:
                permissions.append({
                    "permission": perm_view.permission.name,
                    "view": perm_view.view_menu.name
                })
        return permissions
        
    def check_resource_access(self, user, resource, action):
        """检查资源访问权限"""
        return self.security_manager.has_access(action, resource, user)
        
    def generate_access_report(self, user, resource, action, has_access, permissions):
        """生成访问诊断报告"""
        report = {
            "user": user.username,
            "requested_resource": resource,
            "requested_action": action,
            "has_access": has_access,
            "user_roles": [role.name for role in user.roles],
            "permissions_granted": permissions,
            "troubleshooting_steps": []
        }
        
        if not has_access:
            report["troubleshooting_steps"].extend([
                "Verify user role assignments",
                "Check if required permissions exist",
                "Ensure resource name matches exactly",
                "Review role-based access control configuration"
            ])
            
            # 检查是否有相似权限
            similar_perms = self.find_similar_permissions(permissions, resource, action)
            if similar_perms:
                report["similar_permissions"] = similar_perms
                report["troubleshooting_steps"].append(
                    "Found similar permissions, check if they can be used instead"
                )
                
        return report
        
    def find_similar_permissions(self, permissions, target_resource, target_action):
        """查找相似权限"""
        similar = []
        target_resource_lower = target_resource.lower()
        
        for perm in permissions:
            if (target_resource_lower in perm["view"].lower() or 
                perm["view"].lower() in target_resource_lower):
                similar.append(perm)
                
        return similar

# 使用示例
# troubleshooter = PermissionTrouboubleshooter()
# result = troubleshooter.troubleshoot_user_access("john_doe", "Dashboard", "can_read")
```

### 安全配置问题

```python
# security_config_checker.py
import os
import hashlib
from cryptography.fernet import Fernet

class SecurityConfigChecker:
    def __init__(self, config):
        self.config = config
        
    def check_security_configuration(self):
        """检查安全配置"""
        issues = []
        
        # 1. 检查 SECRET_KEY
        secret_key = self.config.get('SECRET_KEY')
        if not secret_key:
            issues.append("MISSING: SECRET_KEY is not configured")
        elif len(secret_key) < 16:
            issues.append("WEAK: SECRET_KEY should be at least 16 characters")
        elif secret_key == 'YOUR_OWN_RANDOM_GENERATED_STRING':
            issues.append("INSECURE: Using default SECRET_KEY value")
            
        # 2. 检查密码策略
        password_requirements = self.config.get('PASSWORD_REQUIREMENTS', {})
        if not password_requirements:
            issues.append("MISSING: Password requirements not configured")
            
        # 3. 检查 TLS/SSL 配置
        enable_https = self.config.get('ENABLE_HTTPS', False)
        if not enable_https:
            issues.append("WARNING: HTTPS is not enabled")
            
        # 4. 检查会话配置
        session_config = self.config.get('SESSION_COOKIE_SECURE', False)
        if not session_config:
            issues.append("WARNING: Session cookies are not secured")
            
        # 5. 检查 CORS 配置
        cors_origins = self.config.get('CORS_OPTIONS', {}).get('origins', [])
        if '*' in cors_origins:
            issues.append("INSECURE: CORS allows all origins (*)")
            
        # 6. 检查认证配置
        auth_type = self.config.get('AUTH_TYPE')
        if not auth_type:
            issues.append("MISSING: Authentication type not configured")
            
        return issues
        
    def generate_security_report(self):
        """生成安全报告"""
        issues = self.check_security_configuration()
        
        report = {
            "timestamp": str(datetime.now()),
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i.startswith(("MISSING:", "INSECURE:"))]),
            "warning_issues": len([i for i in issues if i.startswith("WARNING:")]),
            "issues": issues,
            "recommendations": self.get_recommendations(issues)
        }
        
        return report
        
    def get_recommendations(self, issues):
        """获取安全建议"""
        recommendations = []
        
        if any("SECRET_KEY" in issue for issue in issues):
            recommendations.append("Generate a strong SECRET_KEY using os.urandom(32)")
            
        if any("HTTPS" in issue for issue in issues):
            recommendations.append("Enable HTTPS in production environment")
            
        if any("CORS" in issue for issue in issues):
            recommendations.append("Restrict CORS origins to specific domains")
            
        if any("Password" in issue for issue in issues):
            recommendations.append("Configure strong password requirements")
            
        return recommendations

# 使用示例
# config_checker = SecurityConfigChecker(current_app.config)
# security_report = config_checker.generate_security_report()
# print(json.dumps(security_report, indent=2))
```

## 21.6 缓存和性能问题

### 缓存失效诊断

```python
# cache_troubleshooter.py
import redis
import pickle
from flask_caching import Cache

class CacheTroubleshooter:
    def __init__(self, cache_config):
        self.cache_config = cache_config
        self.cache = Cache(config=cache_config)
        
    def diagnose_cache_issues(self):
        """诊断缓存问题"""
        print("Starting cache diagnostics...")
        
        issues = []
        
        # 1. 检查缓存连接
        connection_status = self.test_cache_connection()
        if not connection_status["connected"]:
            issues.append({
                "type": "connection_failure",
                "description": "Unable to connect to cache backend",
                "details": connection_status["error"]
            })
            
        # 2. 检查缓存状态
        cache_stats = self.get_cache_statistics()
        if cache_stats:
            hit_rate = cache_stats.get("hit_rate", 0)
            if hit_rate < 0.5:  # 低于50%认为有问题
                issues.append({
                    "type": "low_hit_rate",
                    "description": f"Low cache hit rate: {hit_rate:.2%}",
                    "details": cache_stats
                })
                
        # 3. 检查缓存键空间
        key_space_info = self.analyze_key_space()
        if key_space_info.get("fragmentation_ratio", 0) > 0.3:
            issues.append({
                "type": "key_fragmentation",
                "description": "High key space fragmentation detected",
                "details": key_space_info
            })
            
        return {
            "timestamp": str(datetime.now()),
            "issues_found": len(issues),
            "issues": issues,
            "recommendations": self.generate_cache_recommendations(issues)
        }
        
    def test_cache_connection(self):
        """测试缓存连接"""
        try:
            # 尝试设置和获取测试值
            test_key = "cache_test_connection"
            test_value = "test_value"
            
            self.cache.set(test_key, test_value, timeout=10)
            retrieved_value = self.cache.get(test_key)
            
            # 清理测试键
            self.cache.delete(test_key)
            
            if retrieved_value == test_value:
                return {"connected": True}
            else:
                return {"connected": False, "error": "Value mismatch"}
                
        except Exception as e:
            return {"connected": False, "error": str(e)}
            
    def get_cache_statistics(self):
        """获取缓存统计信息"""
        try:
            if self.cache_config.get("CACHE_TYPE") == "redis":
                redis_client = redis.Redis(
                    host=self.cache_config.get("CACHE_REDIS_HOST", "localhost"),
                    port=self.cache_config.get("CACHE_REDIS_PORT", 6379),
                    db=self.cache_config.get("CACHE_REDIS_DB", 0)
                )
                
                info = redis_client.info()
                stats = {
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "total_commands": info.get("total_commands_processed", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "0B")
                }
                
                total_requests = stats["hits"] + stats["misses"]
                if total_requests > 0:
                    stats["hit_rate"] = stats["hits"] / total_requests
                    
                return stats
                
        except Exception as e:
            print(f"Failed to get cache statistics: {e}")
            return None
            
    def analyze_key_space(self):
        """分析键空间"""
        try:
            if self.cache_config.get("CACHE_TYPE") == "redis":
                redis_client = redis.Redis(
                    host=self.cache_config.get("CACHE_REDIS_HOST", "localhost"),
                    port=self.cache_config.get("CACHE_REDIS_PORT", 6379),
                    db=self.cache_config.get("CACHE_REDIS_DB", 0)
                )
                
                info = redis_client.info("keyspace")
                db_info = info.get("db0", {})  # 假设使用 db0
                
                return {
                    "keys": db_info.get("keys", 0),
                    "expires": db_info.get("expires", 0),
                    "avg_ttl": db_info.get("avg_ttl", 0)
                }
                
        except Exception as e:
            print(f"Failed to analyze key space: {e}")
            return {}
            
    def generate_cache_recommendations(self, issues):
        """生成缓存建议"""
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "connection_failure":
                recommendations.append("Check cache server connectivity and credentials")
                recommendations.append("Verify cache server is running and accessible")
                
            elif issue["type"] == "low_hit_rate":
                recommendations.append("Review cache key generation strategy")
                recommendations.append("Increase cache timeout for frequently accessed data")
                recommendations.append("Analyze cache invalidation patterns")
                
            elif issue["type"] == "key_fragmentation":
                recommendations.append("Run Redis memory optimization")
                recommendations.append("Implement cache key cleanup strategy")
                recommendations.append("Consider using Redis eviction policies")
                
        return recommendations

# 使用示例
# cache_config = {
#     "CACHE_TYPE": "redis",
#     "CACHE_REDIS_HOST": "localhost",
#     "CACHE_REDIS_PORT": 6379,
#     "CACHE_REDIS_DB": 0
# }
# troubleshooter = CacheTroubleshooter(cache_config)
# report = troubleshooter.diagnose_cache_issues()
```

## 21.7 日志分析和监控

### 日志模式识别

```python
# log_analyzer.py
import re
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class LogAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.patterns = {
            "error": r"ERROR|CRITICAL|FATAL",
            "warning": r"WARNING|WARN",
            "authentication": r"Authentication|Login|Logout",
            "database": r"Database|SQL|Query",
            "performance": r"Slow query|Timeout|Performance",
            "security": r"Security|Unauthorized|Forbidden"
        }
        
    def analyze_logs(self, hours_back=24):
        """分析日志文件"""
        print(f"Analyzing logs from the last {hours_back} hours...")
        
        # 计算时间范围
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # 统计数据
        stats = {
            "total_lines": 0,
            "pattern_matches": defaultdict(int),
            "error_counts": defaultdict(int),
            "hourly_distribution": defaultdict(int),
            "top_errors": Counter()
        }
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    stats["total_lines"] += 1
                    
                    # 解析时间戳
                    timestamp = self.extract_timestamp(line)
                    if timestamp and timestamp < cutoff_time:
                        continue
                        
                    if timestamp:
                        hour_key = timestamp.strftime("%Y-%m-%d %H:00")
                        stats["hourly_distribution"][hour_key] += 1
                        
                    # 匹配模式
                    for pattern_name, pattern in self.patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            stats["pattern_matches"][pattern_name] += 1
                            
                    # 特别处理错误
                    if re.search(self.patterns["error"], line, re.IGNORECASE):
                        error_type = self.classify_error(line)
                        stats["error_counts"][error_type] += 1
                        stats["top_errors"][line.strip()] += 1
                        
        except FileNotFoundError:
            return {"error": f"Log file not found: {self.log_file_path}"}
        except Exception as e:
            return {"error": f"Failed to analyze logs: {e}"}
            
        # 生成报告
        return self.generate_analysis_report(stats, hours_back)
        
    def extract_timestamp(self, line):
        """提取时间戳"""
        # 常见的时间戳格式
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
            r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group().strip('[]')
                    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
                    
        return None
        
    def classify_error(self, line):
        """分类错误类型"""
        error_indicators = {
            "database": ["database", "sql", "connection", "query"],
            "authentication": ["auth", "login", "password", "token"],
            "permission": ["permission", "access", "denied", "forbidden"],
            "performance": ["slow", "timeout", "memory", "cpu"],
            "configuration": ["config", "setting", "parameter"],
            "network": ["network", "connection", "timeout", "socket"]
        }
        
        line_lower = line.lower()
        for category, keywords in error_indicators.items():
            if any(keyword in line_lower for keyword in keywords):
                return category
                
        return "other"
        
    def generate_analysis_report(self, stats, hours_back):
        """生成分析报告"""
        report = {
            "period": f"Last {hours_back} hours",
            "total_lines_processed": stats["total_lines"],
            "pattern_distribution": dict(stats["pattern_matches"]),
            "error_breakdown": dict(stats["error_counts"]),
            "top_errors": dict(stats["top_errors"].most_common(10)),
            "hourly_activity": dict(sorted(stats["hourly_distribution"].items())),
            "recommendations": self.generate_recommendations(stats)
        }
        
        return report
        
    def generate_recommendations(self, stats):
        """生成建议"""
        recommendations = []
        
        # 基于错误数量的建议
        total_errors = sum(stats["error_counts"].values())
        if total_errors > 100:
            recommendations.append("High error volume detected, investigate root causes")
            
        # 基于错误类型的建议
        if stats["error_counts"]["database"] > stats["error_counts"]["other"]:
            recommendations.append("Database-related errors are prevalent, check database health")
            
        if stats["error_counts"]["authentication"] > 0:
            recommendations.append("Authentication errors detected, review login attempts")
            
        # 基于活动模式的建议
        hourly_activity = stats["hourly_distribution"]
        if hourly_activity:
            peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations.append(f"Peak activity hours: {[h[0] for h in peak_hours]}")
            
        return recommendations

# 使用示例
# analyzer = LogAnalyzer("/var/log/superset/superset.log")
# report = analyzer.analyze_logs(hours_back=24)
# print(json.dumps(report, indent=2))
```

## 21.8 系统资源监控

### 资源使用监控

```python
# resource_monitor.py
import psutil
import time
import json
from datetime import datetime

class ResourceMonitor:
    def __init__(self, interval=60):
        self.interval = interval
        self.monitoring = False
        
    def start_monitoring(self, duration_minutes=60):
        """开始监控系统资源"""
        self.monitoring = True
        end_time = time.time() + (duration_minutes * 60)
        
        print(f"Starting resource monitoring for {duration_minutes} minutes...")
        print("Timestamp,CPU(%),Memory(%),Disk IO Read,Disk IO Write,Network Sent,Network Recv")
        
        baseline_net = psutil.net_io_counters()
        baseline_disk = psutil.disk_io_counters()
        
        while self.monitoring and time.time() < end_time:
            # 获取资源使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            # 计算差值
            disk_read = disk_io.read_bytes - baseline_disk.read_bytes
            disk_write = disk_io.write_bytes - baseline_disk.write_bytes
            net_sent = net_io.bytes_sent - baseline_net.bytes_sent
            net_recv = net_io.bytes_recv - baseline_net.bytes_recv
            
            # 输出数据
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp},{cpu_percent:.1f},{memory.percent:.1f},{disk_read},{disk_write},{net_sent},{net_recv}")
            
            # 更新基线
            baseline_net = net_io
            baseline_disk = disk_io
            
            time.sleep(self.interval)
            
        self.monitoring = False
        print("Monitoring completed.")
        
    def check_resource_thresholds(self):
        """检查资源使用阈值"""
        thresholds = {
            "cpu_warning": 80,
            "cpu_critical": 90,
            "memory_warning": 85,
            "memory_critical": 95,
            "disk_warning": 80,
            "disk_critical": 90
        }
        
        alerts = []
        
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > thresholds["cpu_critical"]:
            alerts.append({
                "level": "critical",
                "resource": "CPU",
                "usage": cpu_percent,
                "message": f"CPU usage critical: {cpu_percent}%"
            })
        elif cpu_percent > thresholds["cpu_warning"]:
            alerts.append({
                "level": "warning",
                "resource": "CPU",
                "usage": cpu_percent,
                "message": f"CPU usage high: {cpu_percent}%"
            })
            
        # 内存使用率
        memory = psutil.virtual_memory()
        if memory.percent > thresholds["memory_critical"]:
            alerts.append({
                "level": "critical",
                "resource": "Memory",
                "usage": memory.percent,
                "message": f"Memory usage critical: {memory.percent}%"
            })
        elif memory.percent > thresholds["memory_warning"]:
            alerts.append({
                "level": "warning",
                "resource": "Memory",
                "usage": memory.percent,
                "message": f"Memory usage high: {memory.percent}%"
            })
            
        # 磁盘使用率
        disk = psutil.disk_usage("/")
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > thresholds["disk_critical"]:
            alerts.append({
                "level": "critical",
                "resource": "Disk",
                "usage": disk_percent,
                "message": f"Disk usage critical: {disk_percent:.1f}%"
            })
        elif disk_percent > thresholds["disk_warning"]:
            alerts.append({
                "level": "warning",
                "resource": "Disk",
                "usage": disk_percent,
                "message": f"Disk usage high: {disk_percent:.1f}%"
            })
            
        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "alerts": alerts
        }

# 使用示例
# monitor = ResourceMonitor()
# status = monitor.check_resource_thresholds()
# print(json.dumps(status, indent=2))
```

## 21.9 故障恢复和应急响应

### 应急响应流程

```python
# incident_response.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class IncidentResponseManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def handle_incident(self, incident_type, details):
        """处理故障事件"""
        incident = {
            "id": self.generate_incident_id(),
            "type": incident_type,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "status": "detected"
        }
        
        self.logger.critical(f"Incident detected: {incident_type}", extra=incident)
        
        # 执行应急响应步骤
        response_steps = self.get_response_procedure(incident_type)
        
        for step in response_steps:
            try:
                self.execute_response_step(step, incident)
                incident["status"] = step["name"]
            except Exception as e:
                self.logger.error(f"Failed to execute step {step['name']}: {e}")
                incident["errors"] = incident.get("errors", []) + [str(e)]
                
        # 通知相关人员
        self.notify_stakeholders(incident)
        
        return incident
        
    def generate_incident_id(self):
        """生成故障ID"""
        return f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def get_response_procedure(self, incident_type):
        """获取响应流程"""
        procedures = {
            "database_down": [
                {"name": "check_database_connectivity", "function": self.check_db_connectivity},
                {"name": "restart_database_service", "function": self.restart_db_service},
                {"name": "verify_recovery", "function": self.verify_db_recovery}
            ],
            "high_cpu_usage": [
                {"name": "identify_high_cpu_processes", "function": self.identify_cpu_processes},
                {"name": "terminate_problematic_processes", "function": self.terminate_processes},
                {"name": "monitor_recovery", "function": self.monitor_cpu_recovery}
            ],
            "authentication_failure": [
                {"name": "check_auth_service", "function": self.check_auth_service},
                {"name": "review_logs", "function": self.review_auth_logs},
                {"name": "reset_authentication", "function": self.reset_auth_config}
            ]
        }
        
        return procedures.get(incident_type, [{"name": "generic_response", "function": self.generic_response}])
        
    def execute_response_step(self, step, incident):
        """执行响应步骤"""
        self.logger.info(f"Executing response step: {step['name']}")
        step["function"](incident)
        
    def notify_stakeholders(self, incident):
        """通知相关人员"""
        if not self.config.get("notifications_enabled", False):
            return
            
        recipients = self.config.get("notification_recipients", [])
        if not recipients:
            return
            
        subject = f"Superset Incident Alert: {incident['type']}"
        body = self.format_incident_report(incident)
        
        self.send_email_notification(subject, body, recipients)
        
    def send_email_notification(self, subject, body, recipients):
        """发送邮件通知"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get("smtp_sender", "noreply@example.com")
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.config.get("smtp_server", "localhost"),
                self.config.get("smtp_port", 587)
            )
            server.starttls()
            server.login(
                self.config.get("smtp_username"),
                self.config.get("smtp_password")
            )
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Incident notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            
    def format_incident_report(self, incident):
        """格式化故障报告"""
        return f"""
Superset Incident Report

Incident ID: {incident['id']}
Type: {incident['type']}
Time: {incident['timestamp']}
Status: {incident['status']}

Details:
{json.dumps(incident['details'], indent=2)}

Errors:
{chr(10).join(incident.get('errors', []))}
        """.strip()

# 具体的响应函数实现
    def check_db_connectivity(self, incident):
        """检查数据库连接"""
        # 实现数据库连接检查逻辑
        pass
        
    def restart_db_service(self, incident):
        """重启数据库服务"""
        # 实现数据库服务重启逻辑
        pass
        
    def verify_db_recovery(self, incident):
        """验证数据库恢复"""
        # 实现数据库恢复验证逻辑
        pass
        
    def identify_cpu_processes(self, incident):
        """识别高CPU进程"""
        # 实现进程识别逻辑
        pass
        
    def terminate_processes(self, incident):
        """终止问题进程"""
        # 实现进程终止逻辑
        pass
        
    def monitor_cpu_recovery(self, incident):
        """监控CPU恢复"""
        # 实现监控逻辑
        pass
        
    def check_auth_service(self, incident):
        """检查认证服务"""
        # 实现认证服务检查逻辑
        pass
        
    def review_auth_logs(self, incident):
        """审查认证日志"""
        # 实现日志审查逻辑
        pass
        
    def reset_auth_config(self, incident):
        """重置认证配置"""
        # 实现配置重置逻辑
        pass
        
    def generic_response(self, incident):
        """通用响应"""
        self.logger.info("Executing generic incident response")
        # 实现通用响应逻辑
        pass

# 使用示例
# config = {
#     "notifications_enabled": True,
#     "notification_recipients": ["admin@example.com"],
#     "smtp_server": "smtp.example.com",
#     "smtp_port": 587,
#     "smtp_username": "user",
#     "smtp_password": "password"
# }
# 
# incident_manager = IncidentResponseManager(config)
# incident_details = {
#     "error": "Database connection timeout",
#     "affected_users": 50,
#     "impact_level": "high"
# }
# 
# incident = incident_manager.handle_incident("database_down", incident_details)
```

## 21.10 最佳实践总结

### 故障排除检查清单

```python
# troubleshooting_checklist.py
class TroubleshootingChecklist:
    def __init__(self):
        self.checklists = {
            "startup_issues": [
                "✓ Check if port 8088 is already in use",
                "✓ Verify all required dependencies are installed",
                "✓ Confirm database connection settings are correct",
                "✓ Validate configuration file syntax",
                "✓ Check file permissions for log and data directories",
                "✓ Ensure SECRET_KEY is properly configured"
            ],
            "database_connection_issues": [
                "✓ Test database connectivity with command line tools",
                "✓ Verify database credentials and permissions",
                "✓ Check network connectivity to database server",
                "✓ Review database connection pool settings",
                "✓ Examine firewall and security group configurations",
                "✓ Analyze database server logs for errors"
            ],
            "query_execution_problems": [
                "✓ Review query syntax for errors",
                "✓ Check if required tables and columns exist",
                "✓ Verify user has proper permissions on data source",
                "✓ Analyze query execution plan for bottlenecks",
                "✓ Monitor database server resource usage",
                "✓ Consider query optimization techniques"
            ],
            "performance_issues": [
                "✓ Monitor system resource utilization (CPU, memory, disk)",
                "✓ Analyze slow query logs",
                "✓ Review cache configuration and hit rates",
                "✓ Check database indexing strategy",
                "✓ Examine application server configuration",
                "✓ Profile code for performance bottlenecks"
            ]
        }
        
    def get_checklist(self, issue_type):
        """获取检查清单"""
        return self.checklists.get(issue_type, [])
        
    def print_checklist(self, issue_type):
        """打印检查清单"""
        checklist = self.get_checklist(issue_type)
        if not checklist:
            print(f"No checklist found for issue type: {issue_type}")
            return
            
        print(f"\n{issue_type.replace('_', ' ').title()} Checklist:")
        print("-" * 50)
        for item in checklist:
            print(item)

# 使用示例
# checklist = TroubleshootingChecklist()
# checklist.print_checklist("startup_issues")
```

### 常用诊断命令

```bash
#!/bin/bash
# diagnostic_commands.sh

echo "=== Superset Diagnostic Commands ==="

echo -e "\n1. Check Superset Process:"
ps aux | grep superset

echo -e "\n2. Check Port Usage:"
netstat -tlnp | grep :8088

echo -e "\n3. Check System Resources:"
free -h
df -h
top -bn1 | head -20

echo -e "\n4. Check Recent Logs:"
tail -n 50 /var/log/superset/superset.log

echo -e "\n5. Test Database Connection:"
# 替换为实际的数据库连接信息
# psql -h localhost -U superset -d superset -c "SELECT version();"

echo -e "\n6. Check Redis Connectivity:"
# redis-cli ping

echo -e "\n7. Verify Python Environment:"
which python
python --version
pip list | grep superset

echo -e "\n8. Check Configuration:"
# cat /path/to/superset_config.py | grep -E "^[^#].*="

echo -e "\n=== End Diagnostic Commands ==="
```

## 21.11 小结

本章全面介绍了 Apache Superset 的故障排除与诊断方法，涵盖了从启动故障、数据源连接问题、查询执行问题到权限安全、缓存性能、系统资源监控等各个方面的故障处理技巧：

1. **启动故障诊断**：解决了端口占用、依赖缺失、配置错误等常见启动问题
2. **数据源连接问题**：处理了连接超时、SSL配置、认证失败等数据库连接问题
3. **查询执行故障**：分析了查询失败原因并提供了性能优化建议
4. **权限和安全问题**：诊断了用户访问权限和安全配置相关问题
5. **缓存和性能问题**：解决了缓存失效和系统性能瓶颈
6. **日志分析和监控**：建立了日志模式识别和异常检测机制
7. **系统资源监控**：实现了资源使用监控和阈值告警
8. **故障恢复和应急响应**：制定了完整的故障响应流程

通过掌握本章介绍的故障排除方法和工具，您可以：

- 快速识别和定位 Superset 系统中的各类问题
- 建立完善的监控和预警机制
- 制定标准化的故障处理流程
- 提高系统的稳定性和可靠性

故障排除是一项实践经验很强的技能，建议您：

1. **建立监控体系**：部署全面的日志收集和监控系统
2. **制定应急预案**：针对不同类型故障制定详细的处理预案
3. **定期演练**：定期进行故障模拟演练，提高应急响应能力
4. **持续改进**：基于故障分析结果不断优化系统架构和配置

记住，预防胜于治疗。通过建立完善的监控和预警机制，很多故障可以在发生之前就被发现和解决，从而最大程度地保障 Superset 系统的稳定运行。