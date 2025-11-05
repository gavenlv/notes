"""
示例DAG：基于XComs的条件分支
演示如何使用XComs值来控制工作流的执行路径
"""

from airflow.decorators import dag, task, branch
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import random

@dag(
    dag_id='xcom_branching_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['xcoms', 'branching', 'conditional'],
    doc_md="""
    ### 基于XComs的条件分支示例
    
    这个DAG演示了如何使用XComs值来控制工作流的执行路径：
    - 根据数据类型选择不同的处理路径
    - 根据数据质量决定是否继续处理
    - 根据处理结果选择不同的通知方式
    """
)
def xcom_branching_example():
    
    @task
    def generate_data():
        """生成随机数据"""
        data_types = ["csv", "json", "xml", "parquet"]
        data_type = random.choice(data_types)
        data_size = random.randint(100, 1000)
        quality_score = random.uniform(0.5, 1.0)
        
        data = {
            "type": data_type,
            "size": data_size,
            "quality_score": quality_score,
            "source": f"source_{random.randint(1, 5)}"
        }
        
        print(f"Generated data: {data}")
        return data
    
    @branch
    def choose_processor(ti):
        """根据数据类型选择处理器"""
        data = ti.xcom_pull(task_ids='generate_data')
        data_type = data["type"]
        
        print(f"Choosing processor for data type: {data_type}")
        
        # 根据数据类型选择处理器
        if data_type == "csv":
            return 'process_csv'
        elif data_type == "json":
            return 'process_json'
        elif data_type == "xml":
            return 'process_xml'
        elif data_type == "parquet":
            return 'process_parquet'
        else:
            return 'process_unknown'
    
    @branch
    def check_quality(ti):
        """检查数据质量并决定是否继续处理"""
        data = ti.xcom_pull(task_ids='generate_data')
        quality_score = data["quality_score"]
        
        print(f"Checking data quality: {quality_score}")
        
        # 根据质量分数决定是否继续处理
        if quality_score >= 0.8:
            return 'continue_processing'
        elif quality_score >= 0.6:
            return 'clean_data'
        else:
            return 'reject_data'
    
    # 处理不同类型数据的任务
    @task
    def process_csv(ti):
        """处理CSV数据"""
        data = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing CSV data of size {data['size']}")
        
        result = {
            "data_type": "csv",
            "processed_records": data["size"],
            "processing_time": "2.5s",
            "status": "success"
        }
        
        return result
    
    @task
    def process_json(ti):
        """处理JSON数据"""
        data = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing JSON data of size {data['size']}")
        
        result = {
            "data_type": "json",
            "processed_records": data["size"],
            "processing_time": "3.2s",
            "status": "success"
        }
        
        return result
    
    @task
    def process_xml(ti):
        """处理XML数据"""
        data = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing XML data of size {data['size']}")
        
        result = {
            "data_type": "xml",
            "processed_records": data["size"],
            "processing_time": "4.1s",
            "status": "success"
        }
        
        return result
    
    @task
    def process_parquet(ti):
        """处理Parquet数据"""
        data = ti.xcom_pull(task_ids='generate_data')
        print(f"Processing Parquet data of size {data['size']}")
        
        result = {
            "data_type": "parquet",
            "processed_records": data["size"],
            "processing_time": "1.8s",
            "status": "success"
        }
        
        return result
    
    @task
    def process_unknown(ti):
        """处理未知类型数据"""
        data = ti.xcom_pull(task_ids='generate_data')
        print(f"Unknown data type: {data['type']}")
        
        result = {
            "data_type": data["type"],
            "processed_records": 0,
            "processing_time": "0s",
            "status": "failed",
            "error": "Unknown data type"
        }
        
        return result
    
    # 数据质量处理任务
    continue_processing = DummyOperator(task_id='continue_processing')
    
    @task
    def clean_data(ti):
        """清理低质量数据"""
        data = ti.xcom_pull(task_ids='generate_data')
        print(f"Cleaning data with quality score: {data['quality_score']}")
        
        # 模拟数据清理
        cleaned_size = int(data["size"] * 0.8)  # 清理后数据减少20%
        improved_quality = min(0.9, data["quality_score"] + 0.2)
        
        result = {
            "original_size": data["size"],
            "cleaned_size": cleaned_size,
            "original_quality": data["quality_score"],
            "improved_quality": improved_quality,
            "status": "cleaned"
        }
        
        return result
    
    reject_data = DummyOperator(task_id='reject_data')
    
    @branch
    def choose_notification(ti):
        """根据处理结果选择通知方式"""
        # 尝试从多个可能的处理任务中获取结果
        csv_result = ti.xcom_pull(task_ids='process_csv')
        json_result = ti.xcom_pull(task_ids='process_json')
        xml_result = ti.xcom_pull(task_ids='process_xml')
        parquet_result = ti.xcom_pull(task_ids='process_parquet')
        unknown_result = ti.xcom_pull(task_ids='process_unknown')
        clean_result = ti.xcom_pull(task_ids='clean_data')
        
        # 确定实际执行的结果
        result = (csv_result or json_result or xml_result or parquet_result or 
                 unknown_result or clean_result)
        
        if not result:
            return 'send_error_notification'
        
        status = result.get("status", "unknown")
        
        print(f"Choosing notification based on status: {status}")
        
        # 根据状态选择通知方式
        if status == "success":
            return 'send_success_notification'
        elif status == "cleaned":
            return 'send_warning_notification'
        else:
            return 'send_error_notification'
    
    # 通知任务
    @task
    def send_success_notification(ti):
        """发送成功通知"""
        # 获取处理结果
        csv_result = ti.xcom_pull(task_ids='process_csv')
        json_result = ti.xcom_pull(task_ids='process_json')
        xml_result = ti.xcom_pull(task_ids='process_xml')
        parquet_result = ti.xcom_pull(task_ids='process_parquet')
        
        result = (csv_result or json_result or xml_result or parquet_result)
        
        message = f"Successfully processed {result['processed_records']} {result['data_type']} records in {result['processing_time']}"
        print(f"Success notification: {message}")
        
        return {"notification_type": "success", "message": message}
    
    @task
    def send_warning_notification(ti):
        """发送警告通知"""
        clean_result = ti.xcom_pull(task_ids='clean_data')
        
        message = f"Data cleaned: {clean_result['original_size']} -> {clean_result['cleaned_size']} records"
        print(f"Warning notification: {message}")
        
        return {"notification_type": "warning", "message": message}
    
    @task
    def send_error_notification(ti):
        """发送错误通知"""
        data = ti.xcom_pull(task_ids='generate_data')
        
        message = f"Failed to process {data['type']} data from {data['source']}"
        print(f"Error notification: {message}")
        
        return {"notification_type": "error", "message": message}
    
    # 设置任务依赖
    generate_data() >> [choose_processor(), check_quality()]
    
    choose_processor() >> [
        process_csv(), 
        process_json(), 
        process_xml(), 
        process_parquet(), 
        process_unknown()
    ]
    
    check_quality() >> [continue_processing, clean_data, reject_data]
    
    # 所有处理路径都汇聚到通知选择
    [process_csv(), process_json(), process_xml(), process_parquet(), 
     process_unknown(), clean_data()] >> choose_notification()
    
    choose_notification() >> [
        send_success_notification(),
        send_warning_notification(),
        send_error_notification()
    ]

xcom_branching_dag = xcom_branching_example()