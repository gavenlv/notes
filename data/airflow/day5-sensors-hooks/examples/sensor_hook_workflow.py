"""
传感器与钩子结合的完整工作流示例
演示如何在实际场景中结合使用传感器和钩子
"""

from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.sensors.sql import SqlSensor
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from airflow.providers.slack.operators.slack import SlackAPIPostOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.time_sensor import TimeSensor
from airflow.sensors.external_task import ExternalTaskSensor
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
    dag_id='sensor_hook_workflow',
    default_args=default_args,
    description='传感器与钩子结合的完整工作流',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sensor', 'hook', 'workflow'],
) as dag:
    
    # 开始任务
    start = DummyOperator(task_id='start')
    
    # 等待特定时间（例如，等待数据源系统完成每日备份）
    wait_for_backup_time = TimeSensor(
        task_id='wait_for_backup_time',
        target_time=(datetime.now() + timedelta(hours=2)).time(),
        mode='reschedule',
    )
    
    # 等待外部DAG完成（例如，数据提取DAG）
    wait_for_data_extraction = ExternalTaskSensor(
        task_id='wait_for_data_extraction',
        external_dag_id='data_extraction_dag',
        external_task_id='extract_data',
        allowed_states=['success'],
        failed_states=['failed', 'skipped'],
        mode='reschedule',
        poke_interval=60,
        timeout=3600,
    )
    
    # 等待API服务可用
    wait_for_api_service = HttpSensor(
        task_id='wait_for_api_service',
        http_conn_id='http_default',
        endpoint='api/health',
        response_check=lambda response: response.status_code == 200 and response.json().get('status') == 'ready',
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 等待数据文件出现
    wait_for_data_file = FileSensor(
        task_id='wait_for_data_file',
        filepath='/tmp/daily_data/{{ ds }}.csv',
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 等待数据库中有新数据
    wait_for_new_data = SqlSensor(
        task_id='wait_for_new_data',
        conn_id='postgres_default',
        sql="""
            SELECT COUNT(*) FROM daily_data 
            WHERE data_date = '{{ ds }}';
        """,
        poke_interval=60,
        timeout=1800,
        mode='reschedule',
        check_success=lambda value: int(value[0][0]) > 0,
    )
    
    # 创建处理表
    create_processing_table = PostgresOperator(
        task_id='create_processing_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS processed_data (
                id SERIAL PRIMARY KEY,
                source_data_id INTEGER,
                processed_value VARCHAR(255),
                processing_status VARCHAR(50),
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_data_id) REFERENCES daily_data(id)
            );
        """,
    )
    
    # 使用钩子获取和处理数据
    def fetch_and_process_data(**context):
        """获取和处理数据"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from airflow.providers.http.hooks.http import HttpHook
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import json
        
        # 1. 使用Postgres钩子获取原始数据
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        records = postgres_hook.get_records(
            """
            SELECT id, data_value, metadata 
            FROM daily_data 
            WHERE data_date = %s AND processed = FALSE;
            """,
            parameters=[context['ds']]
        )
        
        if not records:
            return "没有需要处理的数据"
        
        print(f"获取到 {len(records)} 条未处理的数据")
        
        # 2. 使用HTTP钩子调用外部API处理数据
        http_hook = HttpHook(http_conn_id='http_default', method='POST')
        
        processed_data = []
        for record in records:
            data_id = record[0]
            data_value = record[1]
            metadata = json.loads(record[2]) if record[2] else {}
            
            # 调用API处理数据
            response = http_hook.run(
                endpoint='api/process',
                data={'value': data_value, 'metadata': metadata},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                processed_value = response.json().get('processed_value')
                processed_data.append({
                    'source_data_id': data_id,
                    'processed_value': processed_value,
                    'processing_status': 'success'
                })
            else:
                processed_data.append({
                    'source_data_id': data_id,
                    'processed_value': None,
                    'processing_status': 'failed'
                })
        
        # 3. 使用Postgres钩子保存处理结果
        for data in processed_data:
            postgres_hook.run(
                """
                INSERT INTO processed_data (source_data_id, processed_value, processing_status)
                VALUES (%s, %s, %s);
                """,
                parameters=[data['source_data_id'], data['processed_value'], data['processing_status']]
            )
            
            # 更新原始数据状态
            postgres_hook.run(
                """
                UPDATE daily_data 
                SET processed = TRUE 
                WHERE id = %s;
                """,
                parameters=[data['source_data_id']]
            )
        
        # 4. 使用S3钩子备份处理结果
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        # 准备备份数据
        backup_data = {
            'processing_date': context['ds'],
            'processed_count': len(processed_data),
            'success_count': len([d for d in processed_data if d['processing_status'] == 'success']),
            'failed_count': len([d for d in processed_data if d['processing_status'] == 'failed']),
            'processed_data': processed_data
        }
        
        # 上传到S3
        s3_hook.load_string(
            string_data=json.dumps(backup_data),
            key=f'processed_data_backup/{context["ds"]}.json',
            bucket_name='airflow-data-processing',
            replace=True
        )
        
        return f"处理完成: 成功 {backup_data['success_count']}, 失败 {backup_data['failed_count']}"
    
    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=fetch_and_process_data,
    )
    
    # 检查处理结果
    def check_processing_results(**context):
        """检查处理结果"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        # 获取Postgres钩子
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 查询处理结果
        records = postgres_hook.get_records(
            """
            SELECT 
                processing_status,
                COUNT(*) as count
            FROM processed_data
            WHERE DATE(processed_at) = %s
            GROUP BY processing_status;
            """,
            parameters=[context['ds']]
        )
        
        # 统计结果
        result_dict = {record[0]: record[1] for record in records}
        total_processed = sum(result_dict.values())
        success_count = result_dict.get('success', 0)
        failed_count = result_dict.get('failed', 0)
        
        print(f"处理结果统计: 总计 {total_processed}, 成功 {success_count}, 失败 {failed_count}")
        
        # 如果失败率超过20%，返回False
        if total_processed > 0 and failed_count / total_processed > 0.2:
            raise Exception(f"处理失败率过高: {failed_count}/{total_processed} ({failed_count/total_processed:.2%})")
        
        return f"处理质量检查通过: 成功率 {success_count/total_processed:.2%}"
    
    check_results_task = PythonOperator(
        task_id='check_processing_results',
        python_callable=check_processing_results,
    )
    
    # 创建S3存储桶（如果不存在）
    create_s3_bucket = S3CreateBucketOperator(
        task_id='create_s3_bucket',
        bucket_name='airflow-data-processing',
        aws_conn_id='aws_default',
        region_name='us-east-1',
    )
    
    # 导出处理结果到S3
    export_results_to_s3 = SqlToS3Operator(
        task_id='export_results_to_s3',
        sql_conn_id='postgres_default',
        aws_conn_id='aws_default',
        query="""
            SELECT 
                pd.id,
                pd.source_data_id,
                dd.data_value,
                pd.processed_value,
                pd.processing_status,
                pd.processed_at
            FROM processed_data pd
            JOIN daily_data dd ON pd.source_data_id = dd.id
            WHERE DATE(pd.processed_at) = '{{ ds }}';
        """,
        s3_bucket='airflow-data-processing',
        s3_key='processed_results/{{ ds }}.csv',
        table_name='processed_data',
        pd_kwargs={"index": False},
    )
    
    # 发送Slack通知
    send_slack_notification = SlackAPIPostOperator(
        task_id='send_slack_notification',
        slack_conn_id='slack_default',
        channel='#data-processing',
        text="""
        数据处理完成 - {{ ds }}
        处理结果: {{ ti.xcom_pull(task_ids='process_data') }}
        质量检查: {{ ti.xcom_pull(task_ids='check_processing_results') }}
        """,
    )
    
    # 结束任务
    end = DummyOperator(task_id='end', trigger_rule=TriggerRule.ALL_DONE)
    
    # 错误处理任务
    error_handler = BashOperator(
        task_id='error_handler',
        bash_command='echo "处理过程中发生错误，请检查日志"',
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    
    # 定义任务依赖关系
    start >> [
        wait_for_backup_time,
        wait_for_data_extraction,
        wait_for_api_service,
        wait_for_data_file,
        wait_for_new_data
    ] >> create_processing_table >> process_data_task >> check_results_task
    
    check_results_task >> create_s3_bucket >> export_results_to_s3 >> send_slack_notification >> end
    
    # 错误处理
    [process_data_task, check_results_task] >> error_handler
    error_handler >> end

# 条件分支工作流示例
with DAG(
    dag_id='conditional_sensor_workflow',
    default_args=default_args,
    description='基于传感器的条件分支工作流',
    schedule_interval=None,
    catchup=False,
    tags=['sensor', 'conditional', 'workflow'],
) as conditional_dag:
    
    # 开始任务
    start = DummyOperator(task_id='start')
    
    # 等待数据文件
    wait_for_file = FileSensor(
        task_id='wait_for_file',
        filepath='/tmp/input_data.csv',
        poke_interval=30,
        timeout=600,
        mode='poke',
    )
    
    # 检查文件内容的任务
    def check_file_content(**context):
        """检查文件内容并决定处理路径"""
        import csv
        
        # 读取文件
        with open('/tmp/input_data.csv', 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # 检查文件大小
            file_size = len(rows)
            
            # 检查数据类型（假设第一行是标题，第二行是数据）
            if len(rows) > 1:
                data_type = rows[1][0] if rows[1] else 'unknown'
            else:
                data_type = 'empty'
            
            # 决定处理路径
            if file_size > 1000:
                return 'large_data_processing'
            elif data_type == 'premium':
                return 'premium_data_processing'
            else:
                return 'standard_data_processing'
    
    check_content = PythonOperator(
        task_id='check_content',
        python_callable=check_file_content,
    )
    
    # 大数据处理分支
    large_data_processing = BashOperator(
        task_id='large_data_processing',
        bash_command='echo "处理大数据集..."',
    )
    
    # 高级数据处理分支
    premium_data_processing = BashOperator(
        task_id='premium_data_processing',
        bash_command='echo "处理高级数据..."',
    )
    
    # 标准数据处理分支
    standard_data_processing = BashOperator(
        task_id='standard_data_processing',
        bash_command='echo '处理标准数据...'',
    )
    
    # 合并任务
    merge_results = BashOperator(
        task_id='merge_results',
        bash_command='echo "合并处理结果..."',
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    
    # 结束任务
    end = DummyOperator(task_id='end')
    
    # 定义任务依赖关系
    start >> wait_for_file >> check_content
    
    # 条件分支
    check_content >> [large_data_processing, premium_data_processing, standard_data_processing] >> merge_results >> end