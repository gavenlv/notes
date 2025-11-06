"""
钩子集成示例
演示如何使用各种钩子与外部系统交互
"""

from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.slack.operators.slack import SlackAPIPostOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3DeleteBucketOperator
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
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
    dag_id='hooks_integration_example',
    default_args=default_args,
    description='钩子集成示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['hook', 'integration', 'example'],
) as dag:
    
    # 使用Postgres钩子创建表
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS sales_data (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                sale_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
    )
    
    # 使用Python操作Postgres钩子插入数据
    def insert_sales_data(**context):
        """插入销售数据"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        import random
        from datetime import date
        
        # 获取Postgres钩子
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 生成示例数据
        products = [
            ('P001', '笔记本电脑', random.randint(1, 10), random.uniform(500, 1500)),
            ('P002', '智能手机', random.randint(5, 20), random.uniform(200, 800)),
            ('P003', '平板电脑', random.randint(2, 15), random.uniform(300, 900)),
            ('P004', '智能手表', random.randint(10, 30), random.uniform(100, 400)),
            ('P005', '无线耳机', random.randint(15, 50), random.uniform(50, 200)),
        ]
        
        # 插入数据
        for product_id, product_name, quantity, price in products:
            postgres_hook.run(
                """
                INSERT INTO sales_data (product_id, product_name, quantity, price, sale_date) 
                VALUES (%s, %s, %s, %s, %s);
                """,
                parameters=[product_id, product_name, quantity, price, date.today()]
            )
        
        return f"插入了 {len(products)} 条销售数据"
    
    insert_data_task = PythonOperator(
        task_id='insert_sales_data',
        python_callable=insert_sales_data,
    )
    
    # 使用Python操作Postgres钩子查询数据
    def query_sales_data(**context):
        """查询销售数据"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        # 获取Postgres钩子
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # 查询数据
        records = postgres_hook.get_records(
            """
            SELECT product_id, product_name, SUM(quantity) as total_quantity, 
                   SUM(quantity * price) as total_revenue
            FROM sales_data
            GROUP BY product_id, product_name
            ORDER BY total_revenue DESC;
            """
        )
        
        # 格式化结果
        result = []
        for record in records:
            result.append({
                'product_id': record[0],
                'product_name': record[1],
                'total_quantity': record[2],
                'total_revenue': float(record[3])
            })
        
        print(f"查询结果: {result}")
        
        # 将结果推送到XCom
        return result
    
    query_data_task = PythonOperator(
        task_id='query_sales_data',
        python_callable=query_sales_data,
    )
    
    # 使用Slack钩子发送通知
    def send_slack_notification(**context):
        """发送Slack通知"""
        from airflow.providers.slack.hooks.slack import SlackHook
        
        # 获取查询结果
        sales_data = context['task_instance'].xcom_pull(task_ids='query_sales_data')
        
        # 格式化消息
        message = "销售数据报告:\n"
        for item in sales_data:
            message += f"- {item['product_name']}: 销量 {item['total_quantity']}, 收入 ${item['total_revenue']:.2f}\n"
        
        # 获取Slack钩子
        slack_hook = SlackHook(slack_conn_id='slack_default')
        
        # 发送消息
        slack_hook.call(
            api_method='chat.postMessage',
            json={
                'channel': '#airflow-reports',
                'text': message
            }
        )
        
        return "Slack通知已发送"
    
    slack_notification_task = PythonOperator(
        task_id='send_slack_notification',
        python_callable=send_slack_notification,
    )
    
    # 定义任务依赖关系
    create_table >> insert_data_task >> query_data_task >> slack_notification_task

# S3钩子集成示例
with DAG(
    dag_id='s3_hook_integration',
    default_args=default_args,
    description='S3钩子集成示例',
    schedule_interval=None,
    catchup=False,
    tags=['hook', 's3', 'integration'],
) as s3_dag:
    
    # 创建S3存储桶
    create_bucket = S3CreateBucketOperator(
        task_id='create_bucket',
        bucket_name='airflow-sales-data-{{ ds_nodash }}',
        aws_conn_id='aws_default',
        region_name='us-east-1',
    )
    
    # 将SQL数据导出到S3
    export_to_s3 = SqlToS3Operator(
        task_id='export_to_s3',
        sql_conn_id='postgres_default',
        aws_conn_id='aws_default',
        query="""
            SELECT product_id, product_name, quantity, price, sale_date
            FROM sales_data
            WHERE sale_date = '{{ ds }}'
        """,
        s3_bucket='airflow-sales-data-{{ ds_nodash }}',
        s3_key='sales_data_{{ ds }}.csv',
        table_name='sales_data',
        pd_kwargs={"index": False},
    )
    
    # 使用Python操作S3钩子处理文件
    def process_s3_file(**context):
        """处理S3文件"""
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        import pandas as pd
        import io
        
        # 获取S3钩子
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        # 读取文件
        bucket_name = f'airflow-sales-data-{context["ds_nodash"]}'
        file_key = f'sales_data_{context["ds"]}.csv'
        
        file_content = s3_hook.read_key(key=file_key, bucket_name=bucket_name)
        
        # 使用pandas处理数据
        df = pd.read_csv(io.StringIO(file_content))
        
        # 计算总收入
        total_revenue = (df['quantity'] * df['price']).sum()
        
        # 添加汇总行
        summary_row = pd.DataFrame({
            'product_id': ['TOTAL'],
            'product_name': ['TOTAL'],
            'quantity': [df['quantity'].sum()],
            'price': [0],
            'sale_date': [context['ds']]
        })
        
        df = pd.concat([df, summary_row])
        
        # 将处理后的数据保存到S3
        processed_key = f'processed_sales_data_{context["ds"]}.csv'
        s3_hook.load_string(
            string_data=df.to_csv(index=False),
            key=processed_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        return f"处理完成，总收入: ${total_revenue:.2f}"
    
    process_s3_file_task = PythonOperator(
        task_id='process_s3_file',
        python_callable=process_s3_file,
    )
    
    # 删除S3存储桶
    delete_bucket = S3DeleteBucketOperator(
        task_id='delete_bucket',
        bucket_name='airflow-sales-data-{{ ds_nodash }}',
        aws_conn_id='aws_default',
        trigger_rule=TriggerRule.ALL_DONE,
        force_delete=True,
    )
    
    # 定义任务依赖关系
    create_bucket >> export_to_s3 >> process_s3_file_task >> delete_bucket

# HTTP钩子集成示例
with DAG(
    dag_id='http_hook_integration',
    default_args=default_args,
    description='HTTP钩子集成示例',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['hook', 'http', 'integration'],
) as http_dag:
    
    # 使用Python操作HTTP钩子获取数据
    def fetch_api_data(**context):
        """获取API数据"""
        from airflow.providers.http.hooks.http import HttpHook
        import json
        
        # 获取HTTP钩子
        http_hook = HttpHook(http_conn_id='http_default', method='GET')
        
        # 获取用户数据
        users_response = http_hook.run(
            endpoint='api/users',
            headers={"Content-Type": "application/json"}
        )
        
        users_data = users_response.json()
        
        # 获取订单数据
        orders_response = http_hook.run(
            endpoint='api/orders',
            headers={"Content-Type": "application/json"}
        )
        
        orders_data = orders_response.json()
        
        # 合并数据
        combined_data = {
            'users': users_data,
            'orders': orders_data,
            'fetch_time': datetime.now().isoformat()
        }
        
        # 将数据推送到XCom
        return combined_data
    
    fetch_data_task = PythonOperator(
        task_id='fetch_api_data',
        python_callable=fetch_api_data,
    )
    
    # 处理API数据
    def process_api_data(**context):
        """处理API数据"""
        from airflow.providers.http.hooks.http import HttpHook
        
        # 获取数据
        combined_data = context['task_instance'].xcom_pull(task_ids='fetch_api_data')
        
        users = combined_data.get('users', [])
        orders = combined_data.get('orders', [])
        
        # 计算每个用户的订单数量
        user_order_counts = {}
        for order in orders:
            user_id = order.get('user_id')
            if user_id in user_order_counts:
                user_order_counts[user_id] += 1
            else:
                user_order_counts[user_id] = 1
        
        # 准备报告数据
        report_data = []
        for user in users:
            user_id = user.get('id')
            order_count = user_order_counts.get(user_id, 0)
            report_data.append({
                'user_id': user_id,
                'user_name': user.get('name'),
                'order_count': order_count
            })
        
        # 获取HTTP钩子
        http_hook = HttpHook(http_conn_id='http_default', method='POST')
        
        # 发送报告数据
        response = http_hook.run(
            endpoint='api/reports',
            data={'report_data': report_data},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            return f"报告已提交，包含 {len(report_data)} 个用户的数据"
        else:
            raise Exception(f"报告提交失败，状态码: {response.status_code}")
    
    process_data_task = PythonOperator(
        task_id='process_api_data',
        python_callable=process_api_data,
    )
    
    # 定义任务依赖关系
    fetch_data_task >> process_data_task

# 多钩子集成示例
with DAG(
    dag_id='multi_hook_integration',
    default_args=default_args,
    description='多钩子集成示例',
    schedule_interval=None,
    catchup=False,
    tags=['hook', 'multi', 'integration'],
) as multi_hook_dag:
    
    # 使用Python操作多个钩子
    def multi_hook_workflow(**context):
        """多钩子工作流"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        from airflow.providers.http.hooks.http import HttpHook
        from airflow.providers.slack.hooks.slack import SlackHook
        import json
        
        # 1. 使用Postgres钩子获取数据
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        records = postgres_hook.get_records("SELECT * FROM sales_data LIMIT 10;")
        
        # 2. 使用S3钩子存储数据
        s3_hook = S3Hook(aws_conn_id='aws_default')
        data_json = json.dumps([dict(zip([column[0] for column in postgres_hook.get_records("SELECT * FROM sales_data LIMIT 1;")], record)) for record in records])
        s3_hook.load_string(
            string_data=data_json,
            key='sales_data_backup.json',
            bucket_name='airflow-backup-bucket',
            replace=True
        )
        
        # 3. 使用HTTP钩子发送数据到外部API
        http_hook = HttpHook(http_conn_id='http_default', method='POST')
        response = http_hook.run(
            endpoint='api/sales',
            data={'sales_data': data_json},
            headers={"Content-Type": "application/json"}
        )
        
        # 4. 使用Slack钩子发送通知
        slack_hook = SlackHook(slack_conn_id='slack_default')
        slack_hook.call(
            api_method='chat.postMessage',
            json={
                'channel': '#airflow-notifications',
                'text': f"已备份 {len(records)} 条销售数据到S3并同步到外部API"
            }
        )
        
        return f"多钩子工作流完成，处理了 {len(records)} 条记录"
    
    multi_hook_task = PythonOperator(
        task_id='multi_hook_workflow',
        python_callable=multi_hook_workflow,
    )
    
    # 定义任务依赖关系
    multi_hook_task  # 这个DAG只有一个任务