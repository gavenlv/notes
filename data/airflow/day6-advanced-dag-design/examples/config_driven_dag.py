"""
Day 6: 高级DAG设计 - 配置驱动DAG示例

这个示例展示了如何使用配置文件来驱动DAG的生成。
配置驱动的方法使得DAG更加灵活，易于维护和扩展。
"""

import yaml
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from typing import Dict, List, Any


# 示例配置文件内容
CONFIG_YAML = """
# DAG配置
dag_config:
  dag_id: "config_driven_etl_pipeline"
  description: "基于配置的ETL数据管道"
  schedule_interval: "@daily"
  start_date: "2024-01-01"
  tags: ["config-driven", "etl", "advanced"]

# 数据源配置
data_sources:
  - name: "user_data"
    type: "database"
    connection: "postgres_default"
    query: "SELECT * FROM users WHERE created_at >= '{{ ds }}'"
    
  - name: "order_data" 
    type: "api"
    connection: "http_default"
    endpoint: "/api/orders?date={{ ds }}"
    
  - name: "log_data"
    type: "file"
    path: "/data/logs/{{ ds }}/app.log"

# 处理步骤配置
processing_steps:
  - step_id: "extract"
    type: "extraction"
    data_sources: ["user_data", "order_data", "log_data"]
    
  - step_id: "transform"
    type: "transformation"
    operations:
      - name: "clean_data"
        function: "data_cleaning.clean_records"
      - name: "enrich_data"
        function: "data_enrichment.add_metadata"
      - name: "aggregate_data"
        function: "data_aggregation.calculate_metrics"
        
  - step_id: "load"
    type: "loading"
    targets:
      - type: "database"
        connection: "postgres_default"
        table: "analytics_results"
      - type: "file"
        path: "/data/output/{{ ds }}/results.json"
        
  - step_id: "validate"
    type: "validation"
    checks:
      - name: "data_quality"
        function: "validation.check_data_quality"
      - name: "completeness"
        function: "validation.verify_completeness"

# 错误处理配置
error_handling:
  retries: 3
  retry_delay: 300  # 秒
  email_on_failure: true
  email_recipients: ["admin@company.com"]
"""


class ConfigDrivenDAGBuilder:
    """配置驱动DAG构建器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dag = None
        self.tasks = {}
    
    def build_dag(self) -> DAG:
        """构建DAG"""
        dag_config = self.config['dag_config']
        
        default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'start_date': datetime.strptime(dag_config['start_date'], '%Y-%m-%d'),
            'email_on_failure': self.config.get('error_handling', {}).get('email_on_failure', False),
            'email': self.config.get('error_handling', {}).get('email_recipients', []),
            'retries': self.config.get('error_handling', {}).get('retries', 1),
            'retry_delay': timedelta(
                seconds=self.config.get('error_handling', {}).get('retry_delay', 300)
            ),
        }
        
        self.dag = DAG(
            dag_id=dag_config['dag_id'],
            default_args=default_args,
            description=dag_config['description'],
            schedule_interval=dag_config['schedule_interval'],
            catchup=False,
            tags=dag_config.get('tags', [])
        )
        
        self._build_tasks()
        self._set_dependencies()
        
        return self.dag
    
    def _build_tasks(self):
        """构建所有任务"""
        # 创建开始任务
        self.tasks['start'] = DummyOperator(
            task_id='start',
            dag=self.dag
        )
        
        # 创建数据处理步骤任务
        processing_steps = self.config.get('processing_steps', [])
        
        for step in processing_steps:
            step_id = step['step_id']
            step_type = step['type']
            
            if step_type == 'extraction':
                self._create_extraction_tasks(step)
            elif step_type == 'transformation':
                self._create_transformation_task(step)
            elif step_type == 'loading':
                self._create_loading_task(step)
            elif step_type == 'validation':
                self._create_validation_task(step)
    
    def _create_extraction_tasks(self, step_config: Dict[str, Any]):
        """创建数据提取任务"""
        data_sources = self.config.get('data_sources', [])
        step_id = step_config['step_id']
        
        # 为每个数据源创建提取任务
        for source in data_sources:
            if source['name'] in step_config.get('data_sources', []):
                task_id = f"extract_{source['name']}"
                
                self.tasks[task_id] = PythonOperator(
                    task_id=task_id,
                    python_callable=self._extract_data,
                    op_kwargs={'source_config': source},
                    dag=self.dag
                )
        
        # 创建提取完成汇总任务
        self.tasks[f"{step_id}_complete"] = DummyOperator(
            task_id=f"{step_id}_complete",
            dag=self.dag
        )
    
    def _create_transformation_task(self, step_config: Dict[str, Any]):
        """创建数据转换任务"""
        step_id = step_config['step_id']
        
        self.tasks[step_id] = PythonOperator(
            task_id=step_id,
            python_callable=self._transform_data,
            op_kwargs={'step_config': step_config},
            dag=self.dag
        )
    
    def _create_loading_task(self, step_config: Dict[str, Any]):
        """创建数据加载任务"""
        step_id = step_config['step_id']
        
        self.tasks[step_id] = PythonOperator(
            task_id=step_id,
            python_callable=self._load_data,
            op_kwargs={'step_config': step_config},
            dag=self.dag
        )
    
    def _create_validation_task(self, step_config: Dict[str, Any]):
        """创建数据验证任务"""
        step_id = step_config['step_id']
        
        self.tasks[step_id] = PythonOperator(
            task_id=step_id,
            python_callable=self._validate_data,
            op_kwargs={'step_config': step_config},
            dag=self.dag
        )
        
        # 创建结束任务
        self.tasks['end'] = DummyOperator(
            task_id='end',
            dag=self.dag
        )
    
    def _set_dependencies(self):
        """设置任务依赖关系"""
        # 开始任务依赖
        extraction_tasks = [task for task_id, task in self.tasks.items() 
                          if task_id.startswith('extract_')]
        
        if extraction_tasks:
            self.tasks['start'] >> extraction_tasks
        
        # 提取完成汇总
        extract_tasks = [task for task_id, task in self.tasks.items() 
                        if task_id.startswith('extract_')]
        
        if extract_tasks and 'extract_complete' in self.tasks:
            extract_tasks >> self.tasks['extract_complete']
        
        # 处理流程依赖
        processing_flow = ['extract_complete', 'transform', 'load', 'validate', 'end']
        
        for i in range(len(processing_flow) - 1):
            current_task = processing_flow[i]
            next_task = processing_flow[i + 1]
            
            if current_task in self.tasks and next_task in self.tasks:
                self.tasks[current_task] >> self.tasks[next_task]
    
    # 任务执行函数
    def _extract_data(self, source_config: Dict[str, Any], **kwargs) -> str:
        """数据提取函数"""
        print(f"提取数据从: {source_config['name']}")
        print(f"配置: {source_config}")
        return f"extracted_data_from_{source_config['name']}"
    
    def _transform_data(self, step_config: Dict[str, Any], **kwargs) -> str:
        """数据转换函数"""
        print(f"执行数据转换步骤: {step_config['step_id']}")
        print(f"操作: {step_config.get('operations', [])}")
        return "transformed_data"
    
    def _load_data(self, step_config: Dict[str, Any], **kwargs) -> str:
        """数据加载函数"""
        print(f"执行数据加载步骤: {step_config['step_id']}")
        print(f"目标: {step_config.get('targets', [])}")
        return "loaded_data"
    
    def _validate_data(self, step_config: Dict[str, Any], **kwargs) -> str:
        """数据验证函数"""
        print(f"执行数据验证步骤: {step_config['step_id']}")
        print(f"检查: {step_config.get('checks', [])}")
        return "validation_passed"


def load_config_from_yaml(yaml_content: str) -> Dict[str, Any]:
    """从YAML内容加载配置"""
    return yaml.safe_load(yaml_content)


def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """从文件加载配置"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def create_config_driven_dag() -> DAG:
    """创建配置驱动DAG"""
    config = load_config_from_yaml(CONFIG_YAML)
    builder = ConfigDrivenDAGBuilder(config)
    return builder.build_dag()


# 创建DAG实例
config_driven_dag = create_config_driven_dag()


# 测试函数
def test_config_driven_dag():
    """测试配置驱动DAG"""
    dag = create_config_driven_dag()
    
    print("配置驱动DAG信息:")
    print(f"DAG ID: {dag.dag_id}")
    print(f"描述: {dag.description}")
    print(f"任务数量: {len(dag.tasks)}")
    
    print("\n任务列表:")
    for task in dag.tasks:
        print(f"- {task.task_id}")
    
    print("\n依赖关系:")
    for task in dag.tasks:
        downstream = task.downstream_list
        if downstream:
            print(f"{task.task_id} -> {[t.task_id for t in downstream]}")


if __name__ == "__main__":
    test_config_driven_dag()