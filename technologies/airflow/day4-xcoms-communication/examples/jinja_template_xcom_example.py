"""
示例DAG：Jinja模板与XComs结合使用
演示如何在BashOperator中使用Jinja模板和XComs
"""

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models.dag import DAG
from datetime import datetime
import json

with DAG(
    dag_id='jinja_template_xcom_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['xcoms', 'jinja', 'templates'],
    doc_md="""
    ### Jinja模板与XComs示例
    
    这个DAG演示了如何在BashOperator中使用Jinja模板和XComs：
    - 使用数据时间宏
    - 使用变量和参数
    - 在Bash命令中引用XComs
    - 动态生成命令
    """
) as dag:
    
    # 示例1: 使用数据时间宏
    print_date_info = BashOperator(
        task_id='print_date_info',
        bash_command="""
        echo "Execution date: {{ ds }}"
        echo "Previous execution date: {{ prev_ds }}"
        echo "Next execution date: {{ next_ds }}"
        echo "Execution date without dashes: {{ ds_nodash }}"
        echo "Timestamp: {{ ts }}"
        """,
        doc_md="使用Airflow内置的数据时间宏"
    )
    
    # 示例2: 使用DAG运行变量
    print_dag_info = BashOperator(
        task_id='print_dag_info',
        bash_command="""
        echo "DAG ID: {{ dag.dag_id }}"
        echo "DAG run ID: {{ dag_run.run_id }}"
        echo "Execution date: {{ dag_run.execution_date }}"
        echo "Logical date: {{ dag_run.logical_date }}"
        """,
        doc_md="使用DAG和DAG运行变量"
    )
    
    # 示例3: 推送文件信息并使用Jinja模板引用
    push_file_info = BashOperator(
        task_id='push_file_info',
        bash_command='echo '{"path": "/data/input", "filename": "data_{{ ds_nodash }}.csv", "format": "csv"}'',
        xcom_push=True,
        doc_md="推送包含Jinja模板渲染结果的文件信息"
    )
    
    # 示例4: 使用Jinja模板拉取XComs
    process_file = BashOperator(
        task_id='process_file',
        bash_command="""
        echo "Processing file: {{ ti.xcom_pull(task_ids='push_file_info')['filename'] }}"
        echo "File path: {{ ti.xcom_pull(task_ids='push_file_info')['path'] }}"
        echo "File format: {{ ti.xcom_pull(task_ids='push_file_info')['format'] }}"
        
        # 使用XComs值构建命令
        INPUT_FILE="{{ ti.xcom_pull(task_ids='push_file_info')['path'] }}/{{ ti.xcom_pull(task_ids='push_file_info')['filename'] }}"
        OUTPUT_FILE="/data/output/processed_{{ ds_nodash }}.csv"
        
        echo "Input file: $INPUT_FILE"
        echo "Output file: $OUTPUT_FILE"
        
        # 模拟处理命令
        echo "Processing $INPUT_FILE to $OUTPUT_FILE..."
        """,
        doc_md="使用Jinja模板拉取XComs并构建动态命令"
    )
    
    # 示例5: Python任务中使用模板参数
    def process_with_template(**kwargs):
        """使用模板参数的Python函数"""
        file_info = kwargs['file_info']
        processing_date = kwargs['processing_date']
        
        print(f"Processing file info: {file_info}")
        print(f"Processing date: {processing_date}")
        
        # 模拟处理过程
        result = {
            "status": "success",
            "file": file_info['filename'],
            "processed_at": processing_date,
            "record_count": 1000
        }
        
        return result
    
    python_with_template = PythonOperator(
        task_id='python_with_template',
        python_callable=process_with_template,
        templates_dict={
            'file_info': '{{ ti.xcom_pull(task_ids="push_file_info") }}',
            'processing_date': '{{ ds }}'
        },
        doc_md="在PythonOperator中使用模板参数"
    )
    
    # 示例6: 使用Jinja模板处理Python任务的返回值
    finalize_processing = BashOperator(
        task_id='finalize_processing',
        bash_command="""
        PROCESS_RESULT="{{ ti.xcom_pull(task_ids='python_with_template') }}"
        echo "Final processing result: $PROCESS_RESULT"
        
        # 使用JSON解析工具处理结果
        RECORD_COUNT=$(echo "$PROCESS_RESULT" | python -c "import sys, json; print(json.load(sys.stdin)['record_count'])")
        echo "Processed $RECORD_COUNT records"
        
        # 创建摘要文件
        echo "Processing Summary - {{ ds }}" > /tmp/summary_{{ ds_nodash }}.txt
        echo "Records processed: $RECORD_COUNT" >> /tmp/summary_{{ ds_nodash }}.txt
        echo "Status: Success" >> /tmp/summary_{{ ds_nodash }}.txt
        """,
        doc_md="使用Jinja模板处理Python任务的返回值并执行后续命令"
    )
    
    # 示例7: 条件执行基于XComs值
    def check_result(**kwargs):
        """检查处理结果并决定下一步操作"""
        result = kwargs['result']
        
        if result.get('status') == 'success' and result.get('record_count', 0) > 500:
            return 'send_notification'
        else:
            return 'skip_notification'
    
    check_result_task = PythonOperator(
        task_id='check_result',
        python_callable=check_result,
        templates_dict={
            'result': '{{ ti.xcom_pull(task_ids="python_with_template") }}'
        }
    )
    
    send_notification = BashOperator(
        task_id='send_notification',
        bash_command="""
        RESULT="{{ ti.xcom_pull(task_ids='python_with_template') }}"
        echo "Sending notification for processing result: $RESULT"
        echo "Notification sent successfully"
        """,
        trigger_rule='one_success'
    )
    
    skip_notification = BashOperator(
        task_id='skip_notification',
        bash_command="""
        echo "Skipping notification - threshold not met"
        """,
        trigger_rule='one_success'
    )
    
    # 设置任务依赖
    print_date_info >> print_dag_info >> push_file_info
    push_file_info >> [process_file, python_with_template]
    python_with_template >> finalize_processing
    finalize_processing >> check_result_task
    check_result_task >> [send_notification, skip_notification]