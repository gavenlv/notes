"""
示例DAG：跨任务组的XComs通信
演示如何在任务组之间传递数据
"""

from airflow.decorators import dag, task, task_group
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
import random

@dag(
    dag_id='cross_taskgroup_xcom_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['xcoms', 'taskgroups', 'cross-communication'],
    doc_md="""
    ### 跨任务组XComs通信示例
    
    这个DAG演示了如何在任务组之间传递XComs数据：
    - 从一个任务组拉取数据到另一个任务组
    - 跨多个任务组的数据传递
    - 任务组内的数据处理和传递
    """
)
def cross_taskgroup_xcom_example():
    
    @task_group
    def data_extraction():
        """数据提取任务组"""
        
        @task
        def extract_customer_data():
            """提取客户数据"""
            customers = [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
            ]
            print(f"Extracted {len(customers)} customers")
            return {"customers": customers, "count": len(customers)}
        
        @task
        def extract_order_data():
            """提取订单数据"""
            orders = [
                {"id": 101, "customer_id": 1, "amount": 100.50, "date": "2023-01-15"},
                {"id": 102, "customer_id": 2, "amount": 75.25, "date": "2023-01-16"},
                {"id": 103, "customer_id": 1, "amount": 50.00, "date": "2023-01-17"},
                {"id": 104, "customer_id": 3, "amount": 200.75, "date": "2023-01-18"}
            ]
            print(f"Extracted {len(orders)} orders")
            return {"orders": orders, "count": len(orders)}
        
        @task
        def extract_product_data():
            """提取产品数据"""
            products = [
                {"id": 1001, "name": "Product A", "price": 25.00},
                {"id": 1002, "name": "Product B", "price": 50.00},
                {"id": 1003, "name": "Product C", "price": 75.00}
            ]
            print(f"Extracted {len(products)} products")
            return {"products": products, "count": len(products)}
        
        # 设置任务组内依赖
        extract_customer_data() >> extract_order_data() >> extract_product_data()
    
    @task_group
    def data_transformation():
        """数据转换任务组"""
        
        @task
        def transform_customer_data(ti):
            """转换客户数据"""
            # 从数据提取任务组拉取客户数据
            customer_data = ti.xcom_pull(task_ids='data_extraction.extract_customer_data')
            
            # 转换数据
            transformed_customers = []
            for customer in customer_data["customers"]:
                transformed_customer = {
                    "customer_id": customer["id"],
                    "full_name": customer["name"],
                    "contact": customer["email"],
                    "status": "active"
                }
                transformed_customers.append(transformed_customer)
            
            result = {
                "customers": transformed_customers,
                "count": len(transformed_customers),
                "transformed_at": "{{ ds }}"
            }
            print(f"Transformed {result['count']} customers")
            return result
        
        @task
        def transform_order_data(ti):
            """转换订单数据"""
            # 从数据提取任务组拉取订单数据
            order_data = ti.xcom_pull(task_ids='data_extraction.extract_order_data')
            
            # 转换数据
            transformed_orders = []
            for order in order_data["orders"]:
                transformed_order = {
                    "order_id": order["id"],
                    "customer_id": order["customer_id"],
                    "total_amount": order["amount"],
                    "order_date": order["date"],
                    "status": "completed"
                }
                transformed_orders.append(transformed_order)
            
            result = {
                "orders": transformed_orders,
                "count": len(transformed_orders),
                "transformed_at": "{{ ds }}"
            }
            print(f"Transformed {result['count']} orders")
            return result
        
        @task
        def join_data(ti):
            """合并转换后的数据"""
            # 拉取转换后的客户和订单数据
            customer_result = ti.xcom_pull(task_ids='transform_customer_data')
            order_result = ti.xcom_pull(task_ids='transform_order_data')
            
            # 合并数据
            joined_data = {
                "customers": customer_result["customers"],
                "orders": order_result["orders"],
                "summary": {
                    "customer_count": customer_result["count"],
                    "order_count": order_result["count"],
                    "total_revenue": sum(order["total_amount"] for order in order_result["orders"])
                },
                "joined_at": "{{ ds }}"
            }
            
            print(f"Joined data: {joined_data['summary']}")
            return joined_data
        
        # 设置任务组内依赖
        [transform_customer_data(), transform_order_data()] >> join_data()
    
    @task_group
    def data_analysis():
        """数据分析任务组"""
        
        @task
        def analyze_customer_behavior(ti):
            """分析客户行为"""
            # 从数据转换任务组拉取合并数据
            joined_data = ti.xcom_pull(task_ids='data_transformation.join_data')
            
            # 分析客户行为
            customer_orders = {}
            for order in joined_data["orders"]:
                customer_id = order["customer_id"]
                if customer_id not in customer_orders:
                    customer_orders[customer_id] = {
                        "order_count": 0,
                        "total_spent": 0.0
                    }
                customer_orders[customer_id]["order_count"] += 1
                customer_orders[customer_id]["total_spent"] += order["total_amount"]
            
            # 生成分析结果
            analysis_result = {
                "customer_behavior": customer_orders,
                "top_customer": max(customer_orders.items(), key=lambda x: x[1]["total_spent"]),
                "analysis_date": "{{ ds }}"
            }
            
            print(f"Customer behavior analysis: {analysis_result}")
            return analysis_result
        
        @task
        def generate_report(ti):
            """生成报告"""
            # 从数据转换任务组拉取合并数据
            joined_data = ti.xcom_pull(task_ids='data_transformation.join_data')
            
            # 从客户行为分析拉取结果
            behavior_analysis = ti.xcom_pull(task_ids='analyze_customer_behavior')
            
            # 生成报告
            report = {
                "summary": joined_data["summary"],
                "top_customer": behavior_analysis["top_customer"],
                "report_date": "{{ ds }}",
                "generated_by": "Airflow DAG"
            }
            
            print(f"Generated report: {report}")
            return report
        
        # 设置任务组内依赖
        analyze_customer_behavior() >> generate_report()
    
    @task_group
    def data_export():
        """数据导出任务组"""
        
        @task
        def export_to_csv(ti):
            """导出到CSV"""
            # 从数据分析任务组拉取报告
            report = ti.xcom_pull(task_ids='data_analysis.generate_report')
            
            # 模拟导出到CSV
            csv_file = f"report_{{{{ ds_nodash }}}}.csv"
            print(f"Exporting report to CSV: {csv_file}")
            print(f"Report content: {report}")
            
            return {
                "export_type": "csv",
                "file": csv_file,
                "status": "success",
                "records": report["summary"]["order_count"]
            }
        
        @task
        def export_to_json(ti):
            """导出到JSON"""
            # 从数据分析任务组拉取报告
            report = ti.xcom_pull(task_ids='data_analysis.generate_report')
            
            # 模拟导出到JSON
            json_file = f"report_{{{{ ds_nodash }}}}.json"
            print(f"Exporting report to JSON: {json_file}")
            print(f"Report content: {report}")
            
            return {
                "export_type": "json",
                "file": json_file,
                "status": "success",
                "records": report["summary"]["order_count"]
            }
        
        # 并行导出
        [export_to_csv(), export_to_json()]
    
    # 设置任务组间的依赖
    data_extraction() >> data_transformation() >> data_analysis() >> data_export()

cross_taskgroup_xcom_dag = cross_taskgroup_xcom_example()