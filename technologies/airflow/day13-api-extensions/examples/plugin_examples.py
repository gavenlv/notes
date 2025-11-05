"""
Airflow插件开发示例
展示如何开发自定义插件扩展Airflow功能
"""

# 自定义操作符示例
class CustomOperators:
    """自定义操作符集合"""
    
    def create_database_operator(self):
        """创建数据库操作符"""
        code = '''
from airflow.models import BaseOperator
from airflow.hooks.base_hook import BaseHook
from airflow.utils.decorators import apply_defaults
import pandas as pd

class DatabaseOperator(BaseOperator):
    """
    数据库操作符示例
    支持执行SQL查询并将结果保存到XCom
    """
    
    @apply_defaults
    def __init__(
        self,
        sql,
        connection_id,
        output_xcom_key=None,
        *args,
        **kwargs
    ):
        super(DatabaseOperator, self).__init__(*args, **kwargs)
        self.sql = sql
        self.connection_id = connection_id
        self.output_xcom_key = output_xcom_key
    
    def execute(self, context):
        self.log.info(f"Executing SQL: {self.sql}")
        
        # 获取数据库连接
        conn = BaseHook.get_connection(self.connection_id)
        
        # 根据连接类型执行相应的操作
        if conn.conn_type == 'postgres':
            from airflow.hooks.postgres_hook import PostgresHook
            hook = PostgresHook(postgres_conn_id=self.connection_id)
            result = hook.get_pandas_df(self.sql)
        elif conn.conn_type == 'mysql':
            from airflow.hooks.mysql_hook import MySqlHook
            hook = MySqlHook(mysql_conn_id=self.connection_id)
            result = hook.get_pandas_df(self.sql)
        else:
            raise ValueError(f"Unsupported connection type: {conn.conn_type}")
        
        self.log.info(f"Query returned {len(result)} rows")
        
        # 如果指定了XCom键，则将结果推送到XCom
        if self.output_xcom_key:
            context['task_instance'].xcom_push(
                key=self.output_xcom_key,
                value=result.to_dict('records')
            )
        
        return f"Successfully executed query, returned {len(result)} rows"
'''
        return code
    
    def create_notification_operator(self):
        """创建通知操作符"""
        code = '''
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationOperator(BaseOperator):
    """
    通知操作符示例
    支持发送邮件通知
    """
    
    @apply_defaults
    def __init__(
        self,
        subject,
        message,
        to_email,
        from_email=None,
        smtp_conn_id='smtp_default',
        *args,
        **kwargs
    ):
        super(NotificationOperator, self).__init__(*args, **kwargs)
        self.subject = subject
        self.message = message
        self.to_email = to_email
        self.from_email = from_email
        self.smtp_conn_id = smtp_conn_id
    
    def execute(self, context):
        self.log.info(f"Sending notification to {self.to_email}")
        
        # 获取SMTP连接信息
        from airflow.hooks.base_hook import BaseHook
        conn = BaseHook.get_connection(self.smtp_conn_id)
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = self.from_email or conn.login
        msg['To'] = self.to_email
        msg['Subject'] = self.subject
        
        # 添加邮件内容
        body = MIMEText(self.message, 'plain')
        msg.attach(body)
        
        # 发送邮件
        try:
            server = smtplib.SMTP(conn.host, conn.port or 587)
            if conn.extra_dejson.get('use_tls', True):
                server.starttls()
            
            if conn.login and conn.password:
                server.login(conn.login, conn.password)
            
            server.send_message(msg)
            server.quit()
            
            self.log.info("Notification sent successfully")
            return "Notification sent successfully"
        except Exception as e:
            self.log.error(f"Failed to send notification: {str(e)}")
            raise
'''
        return code

# 自定义传感器示例
class CustomSensors:
    """自定义传感器集合"""
    
    def create_file_sensor(self):
        """创建文件传感器"""
        code = '''
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
import os

class FileSensor(BaseSensorOperator):
    """
    文件传感器示例
    检查指定路径的文件是否存在
    """
    
    @apply_defaults
    def __init__(
        self,
        filepath,
        check_interval=60,
        *args,
        **kwargs
    ):
        super(FileSensor, self).__init__(*args, **kwargs)
        self.filepath = filepath
        self.check_interval = check_interval
    
    def poke(self, context):
        self.log.info(f"Checking for file: {self.filepath}")
        
        # 检查文件是否存在
        if os.path.exists(self.filepath):
            self.log.info(f"File found: {self.filepath}")
            return True
        else:
            self.log.info(f"File not found: {self.filepath}")
            return False
'''
        return code
    
    def create_api_sensor(self):
        """创建API传感器"""
        code = '''
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
import requests

class APISensor(BaseSensorOperator):
    """
    API传感器示例
    检查API端点的响应状态
    """
    
    @apply_defaults
    def __init__(
        self,
        url,
        expected_status=200,
        method='GET',
        headers=None,
        timeout=30,
        *args,
        **kwargs
    ):
        super(APISensor, self).__init__(*args, **kwargs)
        self.url = url
        self.expected_status = expected_status
        self.method = method
        self.headers = headers or {}
        self.timeout = timeout
    
    def poke(self, context):
        self.log.info(f"Checking API endpoint: {self.url}")
        
        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == self.expected_status:
                self.log.info(f"API check passed with status {response.status_code}")
                return True
            else:
                self.log.info(f"API check failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log.warning(f"API check failed with exception: {str(e)}")
            return False
'''
        return code

# 自定义Web界面示例
class CustomWebUI:
    """自定义Web界面示例"""
    
    def create_blueprint(self):
        """创建Flask蓝图"""
        code = '''
from flask import Blueprint, jsonify, request
from flask_admin import BaseView, expose
from airflow.www.app import csrf

# 创建蓝图
api_blueprint = Blueprint(
    "custom_api",
    __name__,
    url_prefix="/custom_api"
)

@api_blueprint.route("/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@api_blueprint.route("/stats", methods=["GET"])
def get_stats():
    """获取统计信息"""
    # 这里可以实现获取Airflow统计信息的逻辑
    return jsonify({
        "total_dags": 0,
        "active_dag_runs": 0,
        "running_tasks": 0
    })
'''
        return code
    
    def create_admin_view(self):
        """创建管理视图"""
        code = '''
from flask_admin import BaseView, expose
from airflow.www.app import csrf
from flask import request, flash, redirect, url_for
from airflow.models import DagRun

class CustomAdminView(BaseView):
    """自定义管理视图"""
    
    @expose('/')
    def list(self):
        """显示自定义页面"""
        # 获取DAG运行统计
        dag_runs = DagRun.get_latest_runs()
        return self.render("custom_admin/list.html", dag_runs=dag_runs)
    
    @expose('/details/<string:dag_id>')
    def details(self, dag_id):
        """显示DAG详细信息"""
        return self.render("custom_admin/details.html", dag_id=dag_id)
    
    @expose('/trigger', methods=['POST'])
    @csrf.exempt
    def trigger_dag(self):
        """触发DAG运行"""
        dag_id = request.form.get('dag_id')
        if dag_id:
            # 实现触发DAG的逻辑
            flash(f"DAG {dag_id} triggered successfully")
        else:
            flash("DAG ID is required")
        return redirect(url_for('CustomAdminView.list'))
'''
        return code

# 主插件定义
class PluginDefinition:
    """插件定义示例"""
    
    def create_main_plugin(self):
        """创建主插件文件"""
        code = '''
"""
自定义Airflow插件示例
"""
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint

# 导入自定义组件
# from custom_plugin.operators.database_operator import DatabaseOperator
# from custom_plugin.operators.notification_operator import NotificationOperator
# from custom_plugin.sensors.file_sensor import FileSensor
# from custom_plugin.sensors.api_sensor import APISensor
# from custom_plugin.views.custom_admin_view import CustomAdminView

# 创建蓝图
custom_blueprint = Blueprint(
    "custom_plugin",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/custom"
)

class CustomPlugin(AirflowPlugin):
    name = "custom_plugin"
    
    # 注册操作符
    # operators = [DatabaseOperator, NotificationOperator]
    
    # 注册传感器
    # sensors = [FileSensor, APISensor]
    
    # 注册钩子
    # hooks = []
    
    # 注册执行器
    # executors = []
    
    # 注册宏
    # macros = []
    
    # 注册蓝图
    # flask_blueprints = [custom_blueprint]
    
    # 注册管理视图
    # appbuilder_views = [
    #     {
    #         "name": "Custom Admin",
    #         "category": "Custom Plugins",
    #         "view": CustomAdminView()
    #     }
    # ]
    
    # 注册菜单项
    # appbuilder_menu_items = [
    #     {
    #         "name": "Custom Dashboard",
    #         "category": "Custom Plugins",
    #         "href": "/custom/dashboard"
    #     }
    # ]
'''
        return code

# 演示插件使用
def demo_plugin_usage():
    """演示插件使用"""
    print("=== Airflow插件开发示例 ===")
    print("1. 自定义操作符")
    print("2. 自定义传感器")
    print("3. 自定义Web界面")
    print("4. 插件注册")
    print("\n查看生成的示例代码文件了解详细实现。")

if __name__ == "__main__":
    demo_plugin_usage()