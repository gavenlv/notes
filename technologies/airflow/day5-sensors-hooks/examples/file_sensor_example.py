"""
文件传感器示例
演示如何使用FileSensor等待文件出现，并处理文件内容
"""

from datetime import datetime, timedelta
from pathlib import Path

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
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
    dag_id='file_sensor_example',
    default_args=default_args,
    description='文件传感器示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sensor', 'example'],
) as dag:
    
    # 创建目录任务
    create_directory = BashOperator(
        task_id='create_directory',
        bash_command='mkdir -p /tmp/airflow_data',
    )
    
    # 等待数据文件出现的传感器
    # 注意：在实际使用中，文件路径应该是绝对路径
    wait_for_data_file = FileSensor(
        task_id='wait_for_data_file',
        filepath='/tmp/airflow_data/data.csv',
        poke_interval=30,  # 每30秒检查一次
        timeout=600,       # 10分钟超时
        mode='poke',       # poke模式（持续检查）
        soft_fail=False,   # 超时后是否标记为失败
    )
    
    # 等待配置文件出现的传感器（使用resume模式）
    wait_for_config_file = FileSensor(
        task_id='wait_for_config_file',
        filepath='/tmp/airflow_data/config.json',
        poke_interval=60,  # 每60秒检查一次
        timeout=300,       # 5分钟超时
        mode='reschedule', # reschedule模式（释放工作槽位）
    )
    
    # 处理数据文件的任务
    def process_data_file(**context):
        """处理数据文件"""
        file_path = '/tmp/airflow_data/data.csv'
        
        # 读取文件内容
        with open(file_path, 'r') as f:
            content = f.read()
            print(f"文件内容: {content}")
        
        # 返回处理结果
        return f"处理了 {len(content)} 字节的数据"
    
    process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_data_file,
    )
    
    # 读取配置文件的任务
    def read_config_file(**context):
        """读取配置文件"""
        import json
        
        file_path = '/tmp/airflow_data/config.json'
        
        # 读取配置
        with open(file_path, 'r') as f:
            config = json.load(f)
            print(f"配置内容: {config}")
        
        # 返回配置
        return config
    
    read_config = PythonOperator(
        task_id='read_config',
        python_callable=read_config_file,
    )
    
    # 合并数据和配置的任务
    def merge_data_and_config(**context):
        """合并数据和配置"""
        # 获取上游任务的XComs
        data_result = context['task_instance'].xcom_pull(task_ids='process_data')
        config = context['task_instance'].xcom_pull(task_ids='read_config')
        
        print(f"数据结果: {data_result}")
        print(f"配置: {config}")
        
        # 模拟合并处理
        merged_result = {
            'data_info': data_result,
            'config': config,
            'processed_at': datetime.now().isoformat()
        }
        
        return merged_result
    
    merge_data_config = PythonOperator(
        task_id='merge_data_config',
        python_callable=merge_data_and_config,
    )
    
    # 清理任务
    cleanup = BashOperator(
        task_id='cleanup',
        bash_command='rm -f /tmp/airflow_data/data.csv /tmp/airflow_data/config.json',
        trigger_rule=TriggerRule.ALL_DONE,  # 无论上游任务成功或失败都执行
    )
    
    # 定义任务依赖关系
    create_directory >> [wait_for_data_file, wait_for_config_file]
    wait_for_data_file >> process_data
    wait_for_config_file >> read_config
    [process_data, read_config] >> merge_data_config
    merge_data_config >> cleanup

# 高级示例：使用模板路径的文件传感器
with DAG(
    dag_id='advanced_file_sensor_example',
    default_args=default_args,
    description='高级文件传感器示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'advanced'],
) as advanced_dag:
    
    # 创建日期目录
    create_date_directory = BashOperator(
        task_id='create_date_directory',
        bash_command='mkdir -p /tmp/airflow_data/{{ ds }}',
    )
    
    # 使用Jinja模板的文件路径
    wait_for_date_file = FileSensor(
        task_id='wait_for_date_file',
        filepath='/tmp/airflow_data/{{ ds }}/data_{{ ds }}.csv',
        poke_interval=30,
        timeout=600,
    )
    
    # 处理日期特定文件
    def process_date_file(**context):
        """处理特定日期的文件"""
        ds = context['ds']  # 获取执行日期
        file_path = f'/tmp/airflow_data/{ds}/data_{ds}.csv'
        
        # 读取文件内容
        with open(file_path, 'r') as f:
            content = f.read()
            print(f"文件内容: {content}")
        
        return f"处理了 {ds} 的数据文件"
    
    process_date_data = PythonOperator(
        task_id='process_date_data',
        python_callable=process_date_file,
    )
    
    # 定义任务依赖关系
    create_date_directory >> wait_for_date_file >> process_date_data

# 传感器模式对比示例
with DAG(
    dag_id='sensor_mode_comparison',
    default_args=default_args,
    description='传感器模式对比示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'comparison'],
) as comparison_dag:
    
    # 创建测试文件
    create_test_file = BashOperator(
        task_id='create_test_file',
        bash_command='sleep 60 && touch /tmp/airflow_data/test_file.txt',
    )
    
    # Poke模式传感器（占用工作槽位）
    poke_mode_sensor = FileSensor(
        task_id='poke_mode_sensor',
        filepath='/tmp/airflow_data/test_file.txt',
        poke_interval=10,
        timeout=120,
        mode='poke',
    )
    
    # Reschedule模式传感器（释放工作槽位）
    reschedule_mode_sensor = FileSensor(
        task_id='reschedule_mode_sensor',
        filepath='/tmp/airflow_data/test_file.txt',
        poke_interval=10,
        timeout=120,
        mode='reschedule',
    )
    
    # 处理文件
    process_test_file = BashOperator(
        task_id='process_test_file',
        bash_command='cat /tmp/airflow_data/test_file.txt',
    )
    
    # 清理
    cleanup_test_file = BashOperator(
        task_id='cleanup_test_file',
        bash_command='rm -f /tmp/airflow_data/test_file.txt',
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    # 定义任务依赖关系
    create_test_file >> [poke_mode_sensor, reschedule_mode_sensor] >> process_test_file >> cleanup_test_file