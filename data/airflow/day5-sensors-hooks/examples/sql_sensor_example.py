"""
SQL传感器示例
演示如何使用SqlSensor等待数据库中的特定条件满足
"""

from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.sensors.sql import SqlSensor
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
    dag_id='sql_sensor_example',
    default_args=default_args,
    description='SQL传感器示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sensor', 'sql', 'example'],
) as dag:
    
    # 创建表
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS data_processing_status (
                id SERIAL PRIMARY KEY,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            );
        """,
    )
    
    # 初始化状态记录
    init_status = PostgresOperator(
        task_id='init_status',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO data_processing_status (status) 
            VALUES ('pending') 
            ON CONFLICT DO NOTHING;
        """,
    )
    
    # 等待状态变为'ready'的传感器
    wait_for_ready_status = SqlSensor(
        task_id='wait_for_ready_status',
        conn_id='postgres_default',
        sql="""
            SELECT status FROM data_processing_status 
            WHERE status = 'ready' 
            ORDER BY created_at DESC 
            LIMIT 1;
        """,
        poke_interval=30,  # 每30秒检查一次
        timeout=600,       # 10分钟超时
        mode='poke',
        soft_fail=False,
    )
    
    # 处理数据的任务
    def process_data(**context):
        """处理数据"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        # 获取Postgres钩子
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 更新状态为'processing'
        postgres_hook.run(
            "UPDATE data_processing_status SET status = 'processing', processed_at = CURRENT_TIMESTAMP WHERE status = 'ready';"
        )
        
        # 模拟数据处理
        print("开始处理数据...")
        
        # 获取当前状态
        records = postgres_hook.get_records("SELECT * FROM data_processing_status ORDER BY created_at DESC LIMIT 1;")
        print(f"当前记录: {records}")
        
        # 更新状态为'completed'
        postgres_hook.run(
            "UPDATE data_processing_status SET status = 'completed' WHERE status = 'processing';"
        )
        
        return "数据处理完成"
    
    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    # 定义任务依赖关系
    create_table >> init_status >> wait_for_ready_status >> process_data_task

# 高级SQL传感器示例：检查记录数量
with DAG(
    dag_id='advanced_sql_sensor_example',
    default_args=default_args,
    description='高级SQL传感器示例',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['sensor', 'sql', 'advanced'],
) as advanced_dag:
    
    # 创建示例数据表
    create_data_table = PostgresOperator(
        task_id='create_data_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS sample_data (
                id SERIAL PRIMARY KEY,
                data_value VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
    )
    
    # 等待表中有足够数据的传感器
    wait_for_sufficient_data = SqlSensor(
        task_id='wait_for_sufficient_data',
        conn_id='postgres_default',
        sql="""
            SELECT COUNT(*) FROM sample_data 
            WHERE created_at >= '{{ execution_date }}'::date;
        """,
        poke_interval=60,  # 每分钟检查一次
        timeout=3600,      # 1小时超时
        mode='reschedule', # 使用reschedule模式
        # 检查条件：返回值大于0
        check_success=lambda value: int(value[0][0]) > 0,
    )
    
    # 处理数据的任务
    def process_sample_data(**context):
        """处理示例数据"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        # 获取Postgres钩子
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 获取数据
        records = postgres_hook.get_records(
            "SELECT * FROM sample_data WHERE created_at >= %s ORDER BY created_at;",
            parameters=[context['execution_date'].date()]
        )
        
        print(f"获取到 {len(records)} 条记录")
        
        # 处理每条记录
        for record in records:
            print(f"处理记录: {record}")
            # 这里可以添加实际的数据处理逻辑
        
        return f"处理了 {len(records)} 条记录"
    
    process_sample_data_task = PythonOperator(
        task_id='process_sample_data',
        python_callable=process_sample_data,
    )
    
    # 清理旧数据
    cleanup_old_data = PostgresOperator(
        task_id='cleanup_old_data',
        postgres_conn_id='postgres_default',
        sql="""
            DELETE FROM sample_data 
            WHERE created_at < '{{ execution_date }}'::date - INTERVAL '7 days';
        """,
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    # 定义任务依赖关系
    create_data_table >> wait_for_sufficient_data >> process_sample_data_task >> cleanup_old_data

# SQL传感器与钩子结合示例
with DAG(
    dag_id='sql_sensor_hook_integration',
    default_args=default_args,
    description='SQL传感器与钩子结合示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'sql', 'hook'],
) as integration_dag:
    
    # 创建任务状态表
    create_task_status_table = PostgresOperator(
        task_id='create_task_status_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS task_status (
                task_id VARCHAR(255) PRIMARY KEY,
                status VARCHAR(50) NOT NULL,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
    )
    
    # 初始化任务状态
    init_task_status = PostgresOperator(
        task_id='init_task_status',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO task_status (task_id, status) 
            VALUES ('data_extraction', 'pending')
            ON CONFLICT (task_id) DO UPDATE 
            SET status = 'pending', updated_at = CURRENT_TIMESTAMP;
        """,
    )
    
    # 等待数据提取完成的传感器
    wait_for_extraction_complete = SqlSensor(
        task_id='wait_for_extraction_complete',
        conn_id='postgres_default',
        sql="""
            SELECT status FROM task_status 
            WHERE task_id = 'data_extraction';
        """,
        poke_interval=15,
        timeout=1800,  # 30分钟超时
        mode='poke',
        # 检查状态是否为'completed'
        check_success=lambda value: value[0][0] == 'completed',
    )
    
    # 使用钩子处理数据的任务
    def process_with_hook(**context):
        """使用钩子处理数据"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        # 获取Postgres钩子
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 获取提取结果
        result = postgres_hook.get_first(
            "SELECT result FROM task_status WHERE task_id = 'data_extraction';"
        )
        
        print(f"提取结果: {result}")
        
        # 更新处理状态
        postgres_hook.run(
            """
            INSERT INTO task_status (task_id, status, result) 
            VALUES ('data_processing', 'in_progress', %s)
            ON CONFLICT (task_id) DO UPDATE 
            SET status = 'in_progress', result = %s, updated_at = CURRENT_TIMESTAMP;
            """,
            parameters=[f"基于提取结果处理: {result}", f"基于提取结果处理: {result}"]
        )
        
        # 模拟数据处理
        import time
        time.sleep(5)
        
        # 更新完成状态
        postgres_hook.run(
            """
            UPDATE task_status 
            SET status = 'completed', updated_at = CURRENT_TIMESTAMP 
            WHERE task_id = 'data_processing';
            """
        )
        
        return "数据处理完成"
    
    process_with_hook_task = PythonOperator(
        task_id='process_with_hook',
        python_callable=process_with_hook,
    )
    
    # 定义任务依赖关系
    create_task_status_table >> init_task_status >> wait_for_extraction_complete >> process_with_hook_task

# 多条件SQL传感器示例
with DAG(
    dag_id='multi_condition_sql_sensor',
    default_args=default_args,
    description='多条件SQL传感器示例',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'sql', 'multi_condition'],
) as multi_condition_dag:
    
    # 创建监控表
    create_monitoring_table = PostgresOperator(
        task_id='create_monitoring_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS system_monitoring (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                threshold_value FLOAT,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
    )
    
    # 等待多个条件满足的传感器
    wait_for_system_ready = SqlSensor(
        task_id='wait_for_system_ready',
        conn_id='postgres_default',
        sql="""
            SELECT 
                COUNT(CASE WHEN metric_name = 'cpu_usage' AND metric_value < 80 THEN 1 END) as cpu_ok,
                COUNT(CASE WHEN metric_name = 'memory_usage' AND metric_value < 85 THEN 1 END) as memory_ok,
                COUNT(CASE WHEN metric_name = 'disk_usage' AND metric_value < 90 THEN 1 END) as disk_ok
            FROM system_monitoring 
            WHERE created_at >= NOW() - INTERVAL '5 minutes';
        """,
        poke_interval=30,
        timeout=600,
        mode='poke',
        # 检查所有指标都正常
        check_success=lambda value: all(v > 0 for v in value[0]),
    )
    
    # 系统就绪后执行的任务
    system_ready_task = BashOperator(
        task_id='system_ready_task',
        bash_command='echo "系统就绪，开始执行任务..."',
    )
    
    # 定义任务依赖关系
    create_monitoring_table >> wait_for_system_ready >> system_ready_task