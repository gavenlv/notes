"""
Day 6: 高级DAG设计 - 动态DAG生成器示例

这个示例展示了如何动态生成DAG，包括基于配置文件、数据库和API的动态DAG生成。
动态DAG生成使得Airflow能够适应不断变化的需求和环境。
"""

import os
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator


class DynamicDAGGenerator:
    """动态DAG生成器基类"""
    
    def __init__(self):
        self.generated_dags = {}
    
    def generate_dags(self) -> Dict[str, DAG]:
        """生成DAGs"""
        raise NotImplementedError("子类必须实现此方法")
    
    def get_dag_configs(self) -> List[Dict[str, Any]]:
        """获取DAG配置列表"""
        raise NotImplementedError("子类必须实现此方法")
    
    def create_dag_from_config(self, config: Dict[str, Any]) -> DAG:
        """根据配置创建DAG"""
        dag_id = config['dag_id']
        
        default_args = {
            'owner': config.get('owner', 'airflow'),
            'depends_on_past': config.get('depends_on_past', False),
            'start_date': datetime.strptime(config['start_date'], '%Y-%m-%d'),
            'email_on_failure': config.get('email_on_failure', False),
            'email_on_retry': config.get('email_on_retry', False),
            'retries': config.get('retries', 1),
            'retry_delay': timedelta(minutes=config.get('retry_delay_minutes', 5)),
        }
        
        dag = DAG(
            dag_id=dag_id,
            default_args=default_args,
            description=config.get('description', ''),
            schedule_interval=config.get('schedule_interval', '@daily'),
            catchup=config.get('catchup', False),
            tags=config.get('tags', []),
            max_active_runs=config.get('max_active_runs', 1)
        )
        
        self._build_dag_tasks(dag, config)
        return dag
    
    def _build_dag_tasks(self, dag: DAG, config: Dict[str, Any]):
        """构建DAG任务"""
        tasks_config = config.get('tasks', [])
        task_objects = {}
        
        # 创建所有任务
        for task_config in tasks_config:
            task_id = task_config['task_id']
            task_type = task_config['type']
            
            if task_type == 'python':
                task_objects[task_id] = PythonOperator(
                    task_id=task_id,
                    python_callable=self._get_python_callable(task_config),
                    op_kwargs=task_config.get('kwargs', {}),
                    dag=dag
                )
            elif task_type == 'bash':
                task_objects[task_id] = BashOperator(
                    task_id=task_id,
                    bash_command=task_config['bash_command'],
                    dag=dag
                )
            elif task_type == 'dummy':
                task_objects[task_id] = DummyOperator(
                    task_id=task_id,
                    dag=dag
                )
        
        # 设置任务依赖关系
        for task_config in tasks_config:
            task_id = task_config['task_id']
            dependencies = task_config.get('dependencies', [])
            
            for dep in dependencies:
                if dep in task_objects and task_id in task_objects:
                    task_objects[dep] >> task_objects[task_id]
    
    def _get_python_callable(self, task_config: Dict[str, Any]) -> Callable:
        """获取Python可调用函数"""
        callable_name = task_config.get('callable', 'default_task')
        
        if callable_name == 'extract_data':
            return self._extract_data_task
        elif callable_name == 'transform_data':
            return self._transform_data_task
        elif callable_name == 'load_data':
            return self._load_data_task
        elif callable_name == 'validate_data':
            return self._validate_data_task
        else:
            return self._default_task
    
    # 默认任务函数
    def _default_task(self, **kwargs):
        """默认任务函数"""
        print(f"执行任务: {kwargs.get('task_id', 'unknown')}")
        return {"status": "success", "timestamp": datetime.now().isoformat()}
    
    def _extract_data_task(self, **kwargs):
        """数据提取任务"""
        print("执行数据提取任务")
        return {"data": [1, 2, 3, 4, 5], "source": "dynamic_source"}
    
    def _transform_data_task(self, **kwargs):
        """数据转换任务"""
        print("执行数据转换任务")
        return {"transformed": True, "records": 5}
    
    def _load_data_task(self, **kwargs):
        """数据加载任务"""
        print("执行数据加载任务")
        return {"loaded": True, "target": "database"}
    
    def _validate_data_task(self, **kwargs):
        """数据验证任务"""
        print("执行数据验证任务")
        return {"validated": True, "quality_score": 95}


class FileBasedDAGGenerator(DynamicDAGGenerator):
    """基于文件的DAG生成器"""
    
    def __init__(self, config_file_path: str):
        super().__init__()
        self.config_file_path = config_file_path
    
    def get_dag_configs(self) -> List[Dict[str, Any]]:
        """从文件获取DAG配置"""
        if not os.path.exists(self.config_file_path):
            # 返回示例配置
            return self._get_sample_configs()
        
        with open(self.config_file_path, 'r') as f:
            if self.config_file_path.endswith('.json'):
                return json.load(f)
            elif self.config_file_path.endswith('.yaml') or self.config_file_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                raise ValueError("不支持的配置文件格式")
    
    def generate_dags(self) -> Dict[str, DAG]:
        """生成DAGs"""
        configs = self.get_dag_configs()
        
        for config in configs:
            dag = self.create_dag_from_config(config)
            self.generated_dags[config['dag_id']] = dag
        
        return self.generated_dags
    
    def _get_sample_configs(self) -> List[Dict[str, Any]]:
        """获取示例配置"""
        return [
            {
                "dag_id": "dynamic_etl_pipeline_1",
                "description": "动态ETL管道示例1",
                "start_date": "2024-01-01",
                "schedule_interval": "@daily",
                "owner": "airflow",
                "tags": ["dynamic", "etl", "file-based"],
                "tasks": [
                    {
                        "task_id": "start",
                        "type": "dummy"
                    },
                    {
                        "task_id": "extract_data",
                        "type": "python",
                        "callable": "extract_data",
                        "dependencies": ["start"]
                    },
                    {
                        "task_id": "transform_data",
                        "type": "python", 
                        "callable": "transform_data",
                        "dependencies": ["extract_data"]
                    },
                    {
                        "task_id": "load_data",
                        "type": "python",
                        "callable": "load_data", 
                        "dependencies": ["transform_data"]
                    },
                    {
                        "task_id": "end",
                        "type": "dummy",
                        "dependencies": ["load_data"]
                    }
                ]
            },
            {
                "dag_id": "dynamic_data_quality_check",
                "description": "动态数据质量检查",
                "start_date": "2024-01-01", 
                "schedule_interval": "@hourly",
                "owner": "data_team",
                "tags": ["dynamic", "quality", "monitoring"],
                "tasks": [
                    {
                        "task_id": "start_check",
                        "type": "dummy"
                    },
                    {
                        "task_id": "validate_schema",
                        "type": "python",
                        "callable": "validate_data",
                        "kwargs": {"check_type": "schema"},
                        "dependencies": ["start_check"]
                    },
                    {
                        "task_id": "check_completeness",
                        "type": "python",
                        "callable": "validate_data", 
                        "kwargs": {"check_type": "completeness"},
                        "dependencies": ["validate_schema"]
                    },
                    {
                        "task_id": "generate_report",
                        "type": "bash",
                        "bash_command": "echo '生成质量报告'",
                        "dependencies": ["check_completeness"]
                    },
                    {
                        "task_id": "end_check",
                        "type": "dummy",
                        "dependencies": ["generate_report"]
                    }
                ]
            }
        ]


class DatabaseDrivenDAGGenerator(DynamicDAGGenerator):
    """基于数据库的DAG生成器"""
    
    def __init__(self, db_connection_string: str):
        super().__init__()
        self.db_connection_string = db_connection_string
    
    def get_dag_configs(self) -> List[Dict[str, Any]]:
        """从数据库获取DAG配置"""
        # 模拟从数据库获取配置
        # 实际实现中会连接数据库查询配置
        return self._get_database_configs()
    
    def _get_database_configs(self) -> List[Dict[str, Any]]:
        """模拟数据库配置"""
        return [
            {
                "dag_id": "db_driven_reporting",
                "description": "数据库驱动的报表生成",
                "start_date": "2024-01-01",
                "schedule_interval": "0 2 * * *",  # 每天凌晨2点
                "owner": "reporting_team",
                "tags": ["database", "reporting", "dynamic"],
                "tasks": [
                    {
                        "task_id": "extract_sales",
                        "type": "python",
                        "callable": "extract_data",
                        "kwargs": {"table": "sales", "date": "{{ ds }}"}
                    },
                    {
                        "task_id": "extract_customers", 
                        "type": "python",
                        "callable": "extract_data",
                        "kwargs": {"table": "customers", "date": "{{ ds }}"},
                        "dependencies": ["extract_sales"]
                    },
                    {
                        "task_id": "generate_daily_report",
                        "type": "python",
                        "callable": "transform_data",
                        "kwargs": {"report_type": "daily"},
                        "dependencies": ["extract_customers"]
                    },
                    {
                        "task_id": "archive_report",
                        "type": "bash", 
                        "bash_command": "echo '归档报表到S3'",
                        "dependencies": ["generate_daily_report"]
                    }
                ]
            }
        ]


class APIDrivenDAGGenerator(DynamicDAGGenerator):
    """基于API的DAG生成器"""
    
    def __init__(self, api_endpoint: str):
        super().__init__()
        self.api_endpoint = api_endpoint
    
    def get_dag_configs(self) -> List[Dict[str, Any]]:
        """从API获取DAG配置"""
        # 模拟API调用获取配置
        # 实际实现中会调用API获取配置
        return self._get_api_configs()
    
    def _get_api_configs(self) -> List[Dict[str, Any]]:
        """模拟API配置"""
        return [
            {
                "dag_id": "api_monitoring_pipeline",
                "description": "API监控管道",
                "start_date": "2024-01-01",
                "schedule_interval": "*/15 * * * *",  # 每15分钟
                "owner": "monitoring_team",
                "tags": ["api", "monitoring", "dynamic"],
                "tasks": [
                    {
                        "task_id": "check_api_health",
                        "type": "python",
                        "callable": "extract_data",
                        "kwargs": {"endpoint": "/health"}
                    },
                    {
                        "task_id": "collect_metrics",
                        "type": "python",
                        "callable": "extract_data", 
                        "kwargs": {"endpoint": "/metrics"},
                        "dependencies": ["check_api_health"]
                    },
                    {
                        "task_id": "analyze_performance",
                        "type": "python",
                        "callable": "transform_data",
                        "kwargs": {"analysis_type": "performance"},
                        "dependencies": ["collect_metrics"]
                    },
                    {
                        "task_id": "send_alerts",
                        "type": "bash",
                        "bash_command": "echo '发送性能告警'",
                        "dependencies": ["analyze_performance"]
                    }
                ]
            }
        ]


# 全局DAG生成器实例
file_generator = FileBasedDAGGenerator("dags_config.json")
db_generator = DatabaseDrivenDAGGenerator("postgresql://user:pass@localhost/db")
api_generator = APIDrivenDAGGenerator("https://api.company.com/config")


# 生成所有DAGs
def generate_all_dags() -> Dict[str, DAG]:
    """生成所有动态DAGs"""
    all_dags = {}
    
    # 从文件生成DAGs
    file_dags = file_generator.generate_dags()
    all_dags.update(file_dags)
    
    # 从数据库生成DAGs
    db_dags = db_generator.generate_dags()
    all_dags.update(db_dags)
    
    # 从API生成DAGs
    api_dags = api_generator.generate_dags()
    all_dags.update(api_dags)
    
    return all_dags


# 测试函数
def test_dynamic_dag_generation():
    """测试动态DAG生成"""
    print("=== 文件驱动DAG生成测试 ===")
    file_dags = file_generator.generate_dags()
    for dag_id, dag in file_dags.items():
        print(f"DAG: {dag_id}, 任务数: {len(dag.tasks)}")
    
    print("\n=== 数据库驱动DAG生成测试 ===")
    db_dags = db_generator.generate_dags()
    for dag_id, dag in db_dags.items():
        print(f"DAG: {dag_id}, 任务数: {len(dag.tasks)}")
    
    print("\n=== API驱动DAG生成测试 ===")
    api_dags = api_generator.generate_dags()
    for dag_id, dag in api_dags.items():
        print(f"DAG: {dag_id}, 任务数: {len(dag.tasks)}")
    
    print(f"\n总共生成 {len(file_dags) + len(db_dags) + len(api_dags)} 个DAG")


if __name__ == "__main__":
    test_dynamic_dag_generation()