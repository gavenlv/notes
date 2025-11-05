import logging
import os
from typing import Dict, Any

# Airflow日志配置示例
LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'airflow': {
            'format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'airflow',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'airflow.utils.log.file_task_handler.FileTaskHandler',
            'formatter': 'airflow',
            'base_log_folder': os.path.expanduser('~/airflow/logs'),
            'filename_template': '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log',
        },
        's3': {
            'class': 'airflow.providers.amazon.aws.log.s3_task_handler.S3TaskHandler',
            'formatter': 'airflow',
            'base_log_folder': os.path.expanduser('~/airflow/logs'),
            's3_log_folder': 's3://your-bucket/airflow-logs',
            'filename_template': '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.log',
        },
        'json_file': {
            'class': 'airflow.utils.log.file_task_handler.FileTaskHandler',
            'formatter': 'json',
            'base_log_folder': os.path.expanduser('~/airflow/logs'),
            'filename_template': '{{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ try_number }}.json',
        },
    },
    'loggers': {
        'airflow': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'airflow.processor': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'airflow.task': {
            'handlers': ['console', 's3'],
            'level': 'INFO',
            'propagate': False,
        },
        'airflow.task_runner': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'flask_appbuilder': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        }
    }
}

# 自定义日志处理器示例
class CustomTaskHandler(logging.Handler):
    """自定义任务日志处理器"""
    
    def __init__(self, custom_param=None):
        super().__init__()
        self.custom_param = custom_param
    
    def emit(self, record):
        # 自定义日志处理逻辑
        log_entry = self.format(record)
        # 这里可以添加发送到外部系统的逻辑
        print(f"Custom Handler: {log_entry}")

# 高级日志配置示例
ADVANCED_LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '[%(asctime)s] %(name)s %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'debug_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/debug.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'custom': {
            'class': '__main__.CustomTaskHandler',
            'level': 'INFO',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'debug_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'airflow': {
            'handlers': ['console', 'debug_file', 'error_file', 'custom'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}