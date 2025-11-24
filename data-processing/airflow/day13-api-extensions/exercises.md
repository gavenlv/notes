# Day 13 练习题

## 练习1: 使用Airflow REST API管理DAG

### 目标
学会使用Airflow REST API来管理DAG，包括获取DAG列表、触发DAG运行、获取DAG运行状态等。

### 步骤
1. 启动Airflow Web服务器
2. 配置API认证
3. 使用curl或Python requests库调用API
4. 实现以下功能：
   - 获取所有DAG列表
   - 获取特定DAG的详细信息
   - 触发DAG运行
   - 获取DAG运行状态
   - 停止正在运行的DAG

### 代码示例
```python
import requests
from requests.auth import HTTPBasicAuth

# Airflow API基础配置
AIRFLOW_API_URL = "http://localhost:8080/api/v1"
USERNAME = "admin"
PASSWORD = "admin"

def get_dags():
    """获取所有DAG列表"""
    response = requests.get(
        f"{AIRFLOW_API_URL}/dags",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    return response.json()

def get_dag_details(dag_id):
    """获取特定DAG的详细信息"""
    response = requests.get(
        f"{AIRFLOW_API_URL}/dags/{dag_id}",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    return response.json()

def trigger_dag_run(dag_id, conf=None):
    """触发DAG运行"""
    data = {}
    if conf:
        data["conf"] = conf
    
    response = requests.post(
        f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns",
        json=data,
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    return response.json()
```

## 练习2: 开发自定义插件

### 目标
开发一个自定义插件，扩展Airflow功能，包括自定义操作符、传感器和Web界面。

### 步骤
1. 创建插件目录结构
2. 实现自定义操作符
3. 实现自定义传感器
4. 添加自定义Web界面
5. 注册插件

### 代码示例
```python
# my_plugin.py
from airflow.models import BaseOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint
from flask_admin import BaseView, expose

# 自定义操作符
class MyCustomOperator(BaseOperator):
    def __init__(self, my_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_param = my_param
    
    def execute(self, context):
        self.log.info(f"Executing MyCustomOperator with param: {self.my_param}")
        # 实现操作符逻辑
        return "Custom operator executed successfully"

# 自定义传感器
class MyCustomSensor(BaseSensorOperator):
    def __init__(self, my_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_param = my_param
    
    def poke(self, context):
        self.log.info(f"Poking with param: {self.my_param}")
        # 实现传感器逻辑
        return True  # 返回True表示条件满足

# 自定义Web界面
class MyView(BaseView):
    @expose('/')
    def list(self):
        return self.render("my_plugin/my_view.html")

# 创建蓝图
my_blueprint = Blueprint(
    "my_plugin",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# 定义插件
class MyPlugin(AirflowPlugin):
    name = "my_plugin"
    
    operators = [MyCustomOperator]
    sensors = [MyCustomSensor]
    flask_blueprints = [my_blueprint]
    appbuilder_views = [{"name": "My View", "category": "My Plugin", "view": MyView()}]
```

## 练习3: API安全配置

### 目标
配置API安全认证，包括基于Token的认证和RBAC权限控制。

### 步骤
1. 配置基于Token的认证
2. 创建API用户和角色
3. 分配API权限
4. 测试安全访问

### 配置示例
```ini
# airflow.cfg 安全配置
[api]
auth_backend = airflow.api.auth.backend.basic_auth

# 启用RBAC
rbac = True

# 创建API角色
[core]
default_pool = default_pool
```

## 练习4: 第三方系统集成

### 目标
实现与第三方系统的集成，通过Webhook接收外部事件并触发Airflow工作流。

### 步骤
1. 创建Webhook端点
2. 实现事件处理逻辑
3. 验证与外部系统的集成
4. 测试端到端流程

### 代码示例
```python
# webhook_handler.py
from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Airflow配置
AIRFLOW_API_URL = "http://localhost:8080/api/v1"
AIRFLOW_USERNAME = "admin"
AIRFLOW_PASSWORD = "admin"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """处理Webhook事件"""
    data = request.json
    
    # 验证事件
    if not validate_event(data):
        return jsonify({"error": "Invalid event"}), 400
    
    # 触发相应的DAG
    dag_id = data.get("dag_id")
    if dag_id:
        trigger_dag(dag_id, data.get("conf", {}))
        return jsonify({"status": "DAG triggered"}), 200
    else:
        return jsonify({"error": "No DAG ID provided"}), 400

def validate_event(data):
    """验证事件数据"""
    # 实现事件验证逻辑
    return True

def trigger_dag(dag_id, conf):
    """触发DAG运行"""
    response = requests.post(
        f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns",
        json={"conf": conf},
        auth=HTTPBasicAuth(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
    )
    return response.status_code == 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 总结
完成这些练习后，你将能够：
1. 熟练使用Airflow REST API管理DAG和任务
2. 开发自定义插件扩展Airflow功能
3. 配置API安全认证和权限控制
4. 实现与第三方系统的集成