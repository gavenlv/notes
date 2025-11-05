"""
Airflow API使用示例
展示如何使用Airflow REST API管理DAG和任务
"""

import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import time

class AirflowAPIClient:
    """Airflow REST API客户端"""
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)
        self.api_url = f"{self.base_url}/api/v1"
    
    def get_dags(self, limit=100, offset=0):
        """获取DAG列表"""
        params = {
            "limit": limit,
            "offset": offset
        }
        response = requests.get(
            f"{self.api_url}/dags",
            params=params,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def get_dag(self, dag_id):
        """获取特定DAG的信息"""
        response = requests.get(
            f"{self.api_url}/dags/{dag_id}",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def get_dag_runs(self, dag_id, limit=100):
        """获取DAG运行历史"""
        params = {
            "limit": limit
        }
        response = requests.get(
            f"{self.api_url}/dags/{dag_id}/dagRuns",
            params=params,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_dag(self, dag_id, conf=None, execution_date=None):
        """触发DAG运行"""
        data = {}
        if conf:
            data["conf"] = conf
        if execution_date:
            data["execution_date"] = execution_date
            
        response = requests.post(
            f"{self.api_url}/dags/{dag_id}/dagRuns",
            json=data,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def get_dag_run(self, dag_id, dag_run_id):
        """获取特定DAG运行的详细信息"""
        response = requests.get(
            f"{self.api_url}/dags/{dag_id}/dagRuns/{dag_run_id}",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def get_task_instances(self, dag_id, dag_run_id):
        """获取DAG运行中的任务实例"""
        response = requests.get(
            f"{self.api_url}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def pause_dag(self, dag_id, paused=True):
        """暂停/恢复DAG"""
        data = {"is_paused": paused}
        response = requests.patch(
            f"{self.api_url}/dags/{dag_id}",
            json=data,
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()

# 自定义插件示例
class CustomPluginExample:
    """自定义插件示例"""
    
    def __init__(self):
        pass
    
    def create_sample_operator(self):
        """创建示例操作符"""
        operator_code = '''
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class SampleOperator(BaseOperator):
    """
    示例自定义操作符
    """
    
    @apply_defaults
    def __init__(self, sample_param, *args, **kwargs):
        super(SampleOperator, self).__init__(*args, **kwargs)
        self.sample_param = sample_param
    
    def execute(self, context):
        self.log.info(f"Executing SampleOperator with param: {self.sample_param}")
        # 在这里实现你的业务逻辑
        return "Sample operator executed successfully"
'''
        return operator_code
    
    def create_sample_sensor(self):
        """创建示例传感器"""
        sensor_code = '''
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

class SampleSensor(BaseSensorOperator):
    """
    示例自定义传感器
    """
    
    @apply_defaults
    def __init__(self, sample_param, *args, **kwargs):
        super(SampleSensor, self).__init__(*args, **kwargs)
        self.sample_param = sample_param
    
    def poke(self, context):
        self.log.info(f"Poking with param: {self.sample_param}")
        # 在这里实现你的传感器逻辑
        # 返回True表示条件满足，False表示继续等待
        return True
'''
        return sensor_code
    
    def create_sample_plugin(self):
        """创建示例插件"""
        plugin_code = '''
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
from flask_admin import BaseView, expose

# 导入你的自定义组件
# from my_plugin.operators.sample_operator import SampleOperator
# from my_plugin.sensors.sample_sensor import SampleSensor

# 创建Flask蓝图用于Web界面
sample_blueprint = Blueprint(
    "sample_plugin",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# 创建自定义视图
class SampleView(BaseView):
    @expose('/')
    def list(self):
        return self.render("sample_plugin/sample_view.html")

# 定义插件
class SamplePlugin(AirflowPlugin):
    name = "sample_plugin"
    
    # 注册自定义组件
    # operators = [SampleOperator]
    # sensors = [SampleSensor]
    
    # 注册Flask组件
    # flask_blueprints = [sample_blueprint]
    # appbuilder_views = [{"name": "Sample View", "category": "Sample Plugin", "view": SampleView()}]
'''
        return plugin_code

# API使用示例
def demo_api_usage():
    """演示API使用"""
    # 初始化客户端
    client = AirflowAPIClient(
        base_url="http://localhost:8080",
        username="admin",
        password="admin"
    )
    
    try:
        # 1. 获取DAG列表
        print("=== 获取DAG列表 ===")
        dags = client.get_dags()
        print(f"找到 {dags['total_entries']} 个DAG")
        for dag in dags['dags'][:5]:  # 只显示前5个
            print(f"- {dag['dag_id']}: {dag['description']}")
        
        if dags['dags']:
            # 2. 获取第一个DAG的详细信息
            first_dag_id = dags['dags'][0]['dag_id']
            print(f"\n=== 获取DAG '{first_dag_id}' 的详细信息 ===")
            dag_info = client.get_dag(first_dag_id)
            print(f"DAG ID: {dag_info['dag_id']}")
            print(f"描述: {dag_info['description']}")
            print(f"是否暂停: {dag_info['is_paused']}")
            print(f"调度间隔: {dag_info['schedule_interval']}")
            
            # 3. 触发DAG运行
            print(f"\n=== 触发DAG '{first_dag_id}' 运行 ===")
            dag_run = client.trigger_dag(
                first_dag_id,
                conf={"triggered_by": "api_demo", "timestamp": str(datetime.now())}
            )
            dag_run_id = dag_run['dag_run_id']
            print(f"DAG运行已触发，运行ID: {dag_run_id}")
            
            # 4. 获取DAG运行状态
            print(f"\n=== 获取DAG运行状态 ===")
            run_info = client.get_dag_run(first_dag_id, dag_run_id)
            print(f"运行状态: {run_info['state']}")
            print(f"开始时间: {run_info['start_date']}")
            print(f"执行日期: {run_info['execution_date']}")
            
            # 5. 获取任务实例
            print(f"\n=== 获取任务实例 ===")
            task_instances = client.get_task_instances(first_dag_id, dag_run_id)
            print(f"找到 {len(task_instances['task_instances'])} 个任务实例")
            for task in task_instances['task_instances'][:3]:  # 只显示前3个
                print(f"- {task['task_id']}: {task['state']}")
        
        print("\n=== API使用演示完成 ===")
        
    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    demo_api_usage()