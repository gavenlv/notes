# 扩展数据库支持指南

本文档说明了如何在本项目中扩展新的数据库支持。

## 1. 实现数据库连接类

首先，需要创建一个新的数据库连接类，实现 `IDatabaseConnection` 接口。

示例：`src/core/mysql_connection.py`

```python
class MySQLConnection(IDatabaseConnection):
    def __init__(self, config_manager):
        # 初始化连接参数
    
    def connect(self) -> bool:
        # 实现连接逻辑
    
    def disconnect(self) -> None:
        # 实现断开连接逻辑
    
    def is_connected(self) -> bool:
        # 实现连接状态检查逻辑
    
    def get_connection_info(self) -> Dict[str, Any]:
        # 返回连接信息
    
    def get_connection(self):
        # 返回数据库连接对象
```

## 2. 更新数据库连接工厂

在 `DatabaseConnectionFactory` 类中添加创建新数据库连接的方法。

示例：

```python
@staticmethod
def create_mysql_connection(config_manager):
    """Create MySQL connection"""
    from .mysql_connection import MySQLConnection
    return MySQLConnection(config_manager)
```

## 3. 实现数据质量检查器

创建一个新的检查器类，继承 `BaseDataQualityChecker` 并实现具体的检查逻辑。

示例：`src/checkers/mysql_checker.py`

```python
class MySQLDataQualityChecker(BaseDataQualityChecker):
    def __init__(self, database_connection: MySQLConnection, logger: ILogger):
        super().__init__(database_connection, logger, 'mysql')
    
    def run_all_checks(self) -> Dict[str, Any]:
        # 实现检查逻辑
```

## 4. 更新工厂类

在 `DataQualityApplicationFactory` 类中添加创建新检查器的逻辑。

示例：

```python
# Create MySQL checker
try:
    mysql_connection = DatabaseConnectionFactory.create_mysql_connection(self._config_manager)
    if mysql_connection.connect():
        mysql_logger = LoggerFactory.create_module_logger('mysql_checker')
        mysql_checker = MySQLDataQualityChecker(mysql_connection, mysql_logger)
        checkers.append(mysql_checker)
except Exception as e:
    self._logger.warning(f"Could not create MySQL checker: {e}")
```

## 5. 实现数据质量报告器

创建一个新的报告器类，继承 `BaseDataQualityReporter` 并实现具体的报告逻辑。

示例：`src/reporters/mysql_reporter.py`

```python
class MySQLDataQualityReporter(BaseDataQualityReporter):
    def __init__(self, database_connection: MySQLConnection, logger: ILogger):
        super().__init__(database_connection, logger, 'mysql')
    
    def store_scan_results(self, scan_result: Dict[str, Any]) -> bool:
        # 实现存储扫描结果的逻辑
```

## 6. 更新工厂类

在 `DataQualityApplicationFactory` 类中添加创建新报告器的逻辑。

示例：

```python
# Create MySQL reporter if enabled
if self._config_manager.get_config('DQ_STORE_TO_MYSQL', 'false').lower() == 'true':
    try:
        mysql_connection = DatabaseConnectionFactory.create_mysql_connection(self._config_manager)
        if mysql_connection.connect():
            mysql_logger = LoggerFactory.create_module_logger('mysql_reporter')
            mysql_reporter = MySQLDataQualityReporter(mysql_connection, mysql_logger)
            reporters.append(mysql_reporter)
    except Exception as e:
        self._logger.warning(f"Could not create MySQL reporter: {e}")
```

## 7. 更新配置管理器

在 `EnvironmentConfigurationManager` 的 `validate_config` 方法中添加新数据库所需的配置项。

示例：

```python
required_keys = [
    # ... existing keys ...
    'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_DATABASE',
    'MYSQL_USERNAME', 'MYSQL_PASSWORD',
    'DQ_STORE_TO_MYSQL'
]
```

## 8. 配置环境变量

在 `.env` 文件中添加新数据库的配置项。

示例：

```
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=data_quality
MYSQL_USERNAME=user
MYSQL_PASSWORD=password
```

通过以上步骤，就可以成功扩展新的数据库支持，而无需修改现有代码。