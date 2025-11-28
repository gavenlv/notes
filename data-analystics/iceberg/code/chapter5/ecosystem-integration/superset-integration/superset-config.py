# Superset Iceberg 集成配置示例
# 本示例演示如何在 Superset 中配置 Iceberg 数据源

import os
from flask_appbuilder.security.manager import AUTH_OAUTH

# 1. 基础配置
ROW_LIMIT = 5000
SUPERSET_WORKERS = 4
SUPERSET_WEBSERVER_PORT = 8088

# 2. 数据库连接配置
SQLALCHEMY_DATABASE_URI = 'postgresql://superset:superset@localhost:5432/superset'

# 3. Iceberg 数据源配置
# 在 Superset 中添加 Iceberg 数据源需要通过 SQLAlchemy 连接器
# 支持的连接器包括 PyHive (Hive), Presto/Trino SQLAlchemy

# Hive Metastore 方式连接 Iceberg
HIVE_ICEBERG_CONNECTION = {
    'name': 'hive_iceberg',
    'sqlalchemy_uri': 'hive://hive_user:hive_password@hive_host:10000/default',
    'extra': {
        'metadata_cache_timeout': {'metadata': 600},
        'engine_params': {
            'connect_args': {
                'configuration': {
                    'iceberg.engine.hive.enabled': 'true',
                    'iceberg.catalog.type': 'hive',
                    'iceberg.catalog.uri': 'thrift://hive_metastore_host:9083'
                }
            }
        }
    }
}

# Trino 方式连接 Iceberg
TRINO_ICEBERG_CONNECTION = {
    'name': 'trino_iceberg',
    'sqlalchemy_uri': 'trino://trino_user@trino_host:8080/iceberg',
    'extra': {
        'metadata_cache_timeout': {'metadata': 600},
        'engine_params': {
            'connect_args': {
                'timezone': 'UTC',
                'requests_kwargs': {
                    'verify': False
                }
            }
        }
    }
}

# 4. 认证配置
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'whitelist': ['@company.com'],
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': os.environ.get('GOOGLE_KEY'),
            'client_secret': os.environ.get('GOOGLE_SECRET'),
            'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
            'client_kwargs': {
                'scope': 'email profile'
            },
            'request_token_url': None,
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth'
        }
    }
]

# 5. 缓存配置
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
    'CACHE_REDIS_URL': 'redis://localhost:6379/1'
}

# 6. 查询配置
QUERY_SEARCH_LIMIT = 1000
DEFAULT_RELATIVE_START_TIME = 'LAST_WEEK'
DEFAULT_RELATIVE_END_TIME = 'NOW'

# 7. 可视化配置
DEFAULT_SQLLAB_LIMIT = 1000
DISPLAY_MAX_ROW = 10000
MAX_TABLE_ROWS = 10000

# 8. 特性标志
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'VERSIONED_EXPORT': True,
    'ALERT_REPORTS': True,
    'DASHBOARD_RBAC': True,
    'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': True,
    'ENABLE_JAVASCRIPT_CONTROLS': False,
    'SCHEDULED_QUERIES': True
}

# 9. 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
LOG_FILE = '/var/log/superset/superset.log'

# 10. 安全配置
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600

# 11. 应用配置
APP_NAME = 'Superset with Iceberg'
APP_ICON = '/static/assets/images/superset-logo-horiz.png'

# 12. 时间配置
# 设置默认时区
DEFAULT_TIMEZONE = 'Asia/Shanghai'

# 13. 文件上传配置
UPLOAD_FOLDER = '/tmp/superset/uploads/'
IMG_UPLOAD_FOLDER = '/tmp/superset/uploads/'
IMG_UPLOAD_URL = '/static/uploads/'

# 14. 示例数据集配置
# 在 Superset 中配置 Iceberg 表作为数据集
EXAMPLE_DATASETS = [
    {
        'database': 'trino_iceberg',
        'schema': 'analytics',
        'table_name': 'user_events',
        'description': '用户行为事件表',
        'columns': [
            {'column_name': 'event_id', 'type': 'VARCHAR'},
            {'column_name': 'user_id', 'type': 'BIGINT'},
            {'column_name': 'event_type', 'type': 'VARCHAR'},
            {'column_name': 'event_time', 'type': 'TIMESTAMP'},
            {'column_name': 'session_id', 'type': 'VARCHAR'}
        ]
    },
    {
        'database': 'trino_iceberg',
        'schema': 'analytics',
        'table_name': 'daily_metrics',
        'description': '每日指标聚合表',
        'columns': [
            {'column_name': 'metric_date', 'type': 'DATE'},
            {'column_name': 'active_users', 'type': 'BIGINT'},
            {'column_name': 'total_events', 'type': 'BIGINT'},
            {'column_name': 'revenue', 'type': 'DECIMAL'}
        ]
    }
]

# 15. 预设查询配置
PRESET_QUERIES = [
    {
        'name': '最近7天用户活跃度',
        'sql': '''
        SELECT 
            DATE(event_time) as event_date,
            COUNT(DISTINCT user_id) as active_users,
            COUNT(*) as total_events
        FROM analytics.user_events
        WHERE event_time >= DATE_ADD('day', -7, CURRENT_DATE)
        GROUP BY DATE(event_time)
        ORDER BY event_date
        ''',
        'database': 'trino_iceberg'
    },
    {
        'name': '热门事件类型排行',
        'sql': '''
        SELECT 
            event_type,
            COUNT(*) as event_count
        FROM analytics.user_events
        GROUP BY event_type
        ORDER BY event_count DESC
        LIMIT 10
        ''',
        'database': 'trino_iceberg'
    }
]

print("Superset Iceberg 集成配置已完成!")
print("请确保以下事项:")
print("1. 已安装必要的连接器 (PyHive, trino-sqlalchemy)")
print("2. Iceberg 表已在 Trino/Hive 中正确配置")
print("3. 网络连接和认证配置正确")
print("4. Redis 和 PostgreSQL 服务正在运行")