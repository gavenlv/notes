"""
HTTP传感器示例
演示如何使用HttpSensor等待HTTP端点返回特定响应
"""

from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.trigger_rule import TriggerRule

# 定义默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建DAG
with DAG(
    dag_id='http_sensor_example',
    default_args=default_args,
    description='HTTP传感器示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sensor', 'http', 'example'],
) as dag:
    
    # 等待API可用的传感器
    wait_for_api = HttpSensor(
        task_id='wait_for_api',
        http_conn_id='http_default',  # 需要在Airflow UI中配置
        endpoint='api/health',
        request_params={},
        headers={},
        response_check=lambda response: "ok" in response.text.lower(),
        poke_interval=30,  # 每30秒检查一次
        timeout=600,       # 10分钟超时
        mode='poke',
    )
    
    # 获取数据的任务
    get_data = SimpleHttpOperator(
        task_id='get_data',
        http_conn_id='http_default',
        endpoint='api/data',
        method='GET',
        headers={"Content-Type": "application/json"},
        response_filter=lambda response: response.json(),
        log_response=True,
    )
    
    # 处理数据的任务
    def process_api_data(**context):
        """处理API数据"""
        # 获取上游任务的XComs
        api_data = context['task_instance'].xcom_pull(task_ids='get_data')
        
        print(f"获取到的API数据: {api_data}")
        
        # 处理数据
        if isinstance(api_data, dict) and 'items' in api_data:
            items = api_data['items']
            print(f"处理 {len(items)} 条数据")
            
            # 模拟数据处理
            processed_items = []
            for item in items:
                processed_item = {
                    'id': item.get('id'),
                    'name': item.get('name', '').upper(),
                    'processed_at': datetime.now().isoformat()
                }
                processed_items.append(processed_item)
            
            return f"处理了 {len(processed_items)} 条数据"
        
        return "没有找到可处理的数据"
    
    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_api_data,
    )
    
    # 定义任务依赖关系
    wait_for_api >> get_data >> process_data_task

# 高级HTTP传感器示例：检查特定响应状态
with DAG(
    dag_id='advanced_http_sensor_example',
    default_args=default_args,
    description='高级HTTP传感器示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'http', 'advanced'],
) as advanced_dag:
    
    # 模拟启动服务的任务
    start_service = BashOperator(
        task_id='start_service',
        bash_command='echo "启动服务..." && sleep 30',
    )
    
    # 等待服务启动的传感器
    wait_for_service = HttpSensor(
        task_id='wait_for_service',
        http_conn_id='http_default',
        endpoint='status',
        request_params={},
        headers={},
        # 检查响应状态码和内容
        response_check=lambda response: response.status_code == 200 and "ready" in response.text.lower(),
        poke_interval=10,
        timeout=300,
        mode='reschedule',  # 使用reschedule模式
    )
    
    # 等待特定数据可用的传感器
    wait_for_data_ready = HttpSensor(
        task_id='wait_for_data_ready',
        http_conn_id='http_default',
        endpoint='api/data/ready',
        method='POST',
        headers={"Content-Type": "application/json"},
        request_params={'date': '{{ ds }}'},
        response_check=lambda response: response.json().get('ready', False),
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 处理就绪数据的任务
    def process_ready_data(**context):
        """处理就绪的数据"""
        from airflow.providers.http.hooks.http import HttpHook
        
        # 获取HTTP钩子
        http_hook = HttpHook(http_conn_id='http_default', method='GET')
        
        # 获取数据
        response = http_hook.run(
            endpoint='api/data',
            data={'date': context['ds']},
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        print(f"获取到数据: {data}")
        
        # 处理数据
        if data and 'results' in data:
            results = data['results']
            return f"处理了 {len(results)} 条记录"
        
        return "没有获取到数据"
    
    process_ready_data_task = PythonOperator(
        task_id='process_ready_data',
        python_callable=process_ready_data,
    )
    
    # 停止服务
    stop_service = BashOperator(
        task_id='stop_service',
        bash_command='echo "停止服务..."',
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    # 定义任务依赖关系
    start_service >> wait_for_service >> wait_for_data_ready >> process_ready_data_task >> stop_service

# HTTP传感器与钩子结合示例
with DAG(
    dag_id='http_sensor_hook_integration',
    default_args=default_args,
    description='HTTP传感器与钩子结合示例',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['sensor', 'http', 'hook'],
) as integration_dag:
    
    # 等待API可用的传感器
    wait_for_api_available = HttpSensor(
        task_id='wait_for_api_available',
        http_conn_id='http_default',
        endpoint='health',
        response_check=lambda response: response.status_code == 200,
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 使用钩子获取认证令牌的任务
    def get_auth_token(**context):
        """获取认证令牌"""
        from airflow.providers.http.hooks.http import HttpHook
        
        # 获取HTTP钩子
        http_hook = HttpHook(http_conn_id='http_default', method='POST')
        
        # 发送认证请求
        response = http_hook.run(
            endpoint='api/auth',
            data={'username': 'user', 'password': 'password'},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('token')
            if token:
                print("成功获取认证令牌")
                return token
        
        raise Exception("获取认证令牌失败")
    
    get_auth_token_task = PythonOperator(
        task_id='get_auth_token',
        python_callable=get_auth_token,
    )
    
    # 使用认证令牌获取数据的任务
    def get_protected_data(**context):
        """获取受保护的数据"""
        from airflow.providers.http.hooks.http import HttpHook
        
        # 获取认证令牌
        token = context['task_instance'].xcom_pull(task_ids='get_auth_token')
        
        # 获取HTTP钩子
        http_hook = HttpHook(http_conn_id='http_default', method='GET')
        
        # 发送带认证的请求
        response = http_hook.run(
            endpoint='api/protected/data',
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到受保护的数据: {data}")
            return data
        
        raise Exception("获取受保护数据失败")
    
    get_protected_data_task = PythonOperator(
        task_id='get_protected_data',
        python_callable=get_protected_data,
    )
    
    # 定义任务依赖关系
    wait_for_api_available >> get_auth_token_task >> get_protected_data_task

# 多端点HTTP传感器示例
with DAG(
    dag_id='multi_endpoint_http_sensor',
    default_args=default_args,
    description='多端点HTTP传感器示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'http', 'multi_endpoint'],
) as multi_endpoint_dag:
    
    # 等待主服务可用
    wait_for_main_service = HttpSensor(
        task_id='wait_for_main_service',
        http_conn_id='http_default',
        endpoint='api/main/health',
        response_check=lambda response: response.status_code == 200,
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 等待辅助服务可用
    wait_for_auxiliary_service = HttpSensor(
        task_id='wait_for_auxiliary_service',
        http_conn_id='http_default',
        endpoint='api/auxiliary/health',
        response_check=lambda response: response.status_code == 200,
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 等待数据库服务可用
    wait_for_db_service = HttpSensor(
        task_id='wait_for_db_service',
        http_conn_id='http_default',
        endpoint='api/db/health',
        response_check=lambda response: response.status_code == 200,
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 所有服务就绪后执行的任务
    all_services_ready = BashOperator(
        task_id='all_services_ready',
        bash_command='echo "所有服务已就绪，开始执行任务..."',
    )
    
    # 定义任务依赖关系
    [wait_for_main_service, wait_for_auxiliary_service, wait_for_db_service] >> all_services_ready

# 动态HTTP传感器示例
with DAG(
    dag_id='dynamic_http_sensor',
    default_args=default_args,
_args=default_args,
    description='动态HTTP传感器示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'http', 'dynamic'],
) as dynamic_dag:
    
    # 获取需要检查的端点列表
    get_endpoints = SimpleHttpOperator(
        task_id='get_endpoints',
        http_conn_id='http_default',
        endpoint='api/endpoints',
        method='GET',
        headers={"Content-Type": "application/json"},
        response_filter=lambda response: response.json(),
    )
    
    # 动态创建传感器任务
    def create_dynamic_sensors(**context):
        """动态创建传感器任务"""
        from airflow.providers.http.sensors.http import HttpSensor
        from airflow.operators.dummy import DummyOperator
        
        # 获取端点列表
        endpoints = context['task_instance'].xcom_pull(task_ids='get_endpoints')
        
        if not endpoints:
            print("没有获取到端点列表")
            return
        
        # 创建传感器任务
        sensor_tasks = []
        for endpoint in endpoints:
            endpoint_name = endpoint.get('name', 'unknown')
            endpoint_path = endpoint.get('path', '')
            
            # 创建传感器任务
            sensor = HttpSensor(
                task_id=f'wait_for_{endpoint_name}',
                http_conn_id='http_default',
                endpoint=endpoint_path,
                response_check=lambda response: response.status_code == 200,
                poke_interval=30,
                timeout=300,
                mode='poke',
            )
            
            sensor_tasks.append(sensor)
        
        # 创建汇总任务
        all_ready = DummyOperator(task_id='all_endpoints_ready')
        
        # 设置依赖关系
        for sensor in sensor_tasks:
            sensor >> all_ready
        
        return f"创建了 {len(sensor_tasks)} 个传感器任务"
    
    create_sensors = PythonOperator(
        task_id='create_sensors',
        python_callable=create_dynamic_sensors,
    )
    
    # 定义任务依赖关系
    get_endpoints >> create_sensors