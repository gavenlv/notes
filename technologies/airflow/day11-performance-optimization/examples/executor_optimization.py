"""
Airflow 执行器优化示例代码
展示不同执行器的配置和使用场景
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


# SequentialExecutor 示例 (适用于开发环境)
def sequential_executor_example():
    """
    SequentialExecutor 是默认执行器，按顺序执行任务
    优点：简单易用，不需要额外依赖
    缺点：不能并行执行，性能较低
    适用场景：开发测试环境
    """
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'sequential_executor_dag',
        default_args=default_args,
        description='Sequential Executor 示例',
        schedule_interval=timedelta(days=1),
        catchup=False,
    )

    def print_hello():
        print("Hello from SequentialExecutor!")

    task1 = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello,
        dag=dag,
    )

    task2 = BashOperator(
        task_id='print_date',
        bash_command='date',
        dag=dag,
    )

    task1 >> task2
    return dag


# LocalExecutor 示例 (适用于单机环境)
def local_executor_example():
    """
    LocalExecutor 在本地进程中并行执行任务
    优点：可以并行执行，性能较好
    缺点：受限于单机资源
    适用场景：生产环境小规模部署
    """
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'local_executor_dag',
        default_args=default_args,
        description='Local Executor 示例',
        schedule_interval=timedelta(days=1),
        catchup=False,
        max_active_runs=3,
    )

    def cpu_intensive_task(task_id):
        # 模拟 CPU 密集型任务
        import time
        time.sleep(5)
        print(f"Task {task_id} completed")

    # 创建多个并行任务来展示 LocalExecutor 的并行能力
    tasks = []
    for i in range(5):
        task = PythonOperator(
            task_id=f'cpu_task_{i}',
            python_callable=cpu_intensive_task,
            op_args=[i],
            dag=dag,
        )
        tasks.append(task)

    # 设置任务依赖关系
    for i in range(1, len(tasks)):
        tasks[i-1] >> tasks[i]
        
    return dag


# CeleryExecutor 示例 (适用于分布式环境)
def celery_executor_example():
    """
    CeleryExecutor 使用 Celery 分布式任务队列执行任务
    优点：可水平扩展，适合大规模部署
    缺点：配置复杂，需要额外依赖 (Redis/RabbitMQ)
    适用场景：生产环境大规模部署
    """
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'celery_executor_dag',
        default_args=default_args,
        description='Celery Executor 示例',
        schedule_interval=timedelta(hours=1),
        catchup=False,
        max_active_runs=5,
    )

    def distributed_task(worker_id):
        # 模拟分布式任务处理
        import random
        import time
        
        # 模拟不同的处理时间
        processing_time = random.randint(3, 10)
        time.sleep(processing_time)
        
        print(f"Distributed task processed by worker {worker_id} in {processing_time} seconds")

    # 创建多个任务分发到不同 worker
    workers = ['worker_a', 'worker_b', 'worker_c', 'worker_d']
    tasks = []
    
    for i, worker in enumerate(workers):
        task = PythonOperator(
            task_id=f'distributed_task_{worker}',
            python_callable=distributed_task,
            op_args=[worker],
            dag=dag,
            queue=worker,  # 指定队列，用于路由到特定 worker
        )
        tasks.append(task)

    # 可以设置部分任务并行，部分任务串行
    if len(tasks) >= 2:
        # 前两个任务并行
        tasks[0].execution_timeout = timedelta(seconds=30)
        tasks[1].execution_timeout = timedelta(seconds=30)
        
    return dag


# KubernetesExecutor 示例 (适用于容器化环境)
def kubernetes_executor_example():
    """
    KubernetesExecutor 在 Kubernetes 集群中动态创建 Pod 来执行任务
    优点：资源隔离好，弹性伸缩能力强
    缺点：需要 Kubernetes 集群，配置相对复杂
    适用场景：云原生环境，容器化部署
    """
    from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
    from kubernetes.client import models as k8s
    
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'kubernetes_executor_dag',
        default_args=default_args,
        description='Kubernetes Executor 示例',
        schedule_interval=timedelta(hours=2),
        catchup=False,
        max_active_runs=3,
    )

    # 定义资源请求和限制
    resources = k8s.V1ResourceRequirements(
        requests={
            'memory': '256Mi',
            'cpu': '250m'
        },
        limits={
            'memory': '512Mi',
            'cpu': '500m'
        }
    )

    # Kubernetes Pod Operator 示例
    k8s_task = KubernetesPodOperator(
        task_id='k8s_containerized_task',
        name='airflow-k8s-task',
        namespace='airflow',
        image='python:3.9-slim',
        cmds=['python', '-c'],
        arguments=['print("Hello from Kubernetes!"); import time; time.sleep(10); print("Task completed!")'],
        resources=resources,
        is_delete_operator_pod=True,
        in_cluster=False,
        config_file='/path/to/kubeconfig',
        dag=dag,
    )

    return dag


# 根据配置选择合适的执行器示例
def get_optimized_dag(executor_type='local'):
    """
    根据指定的执行器类型返回相应的 DAG 示例
    :param executor_type: 执行器类型 ('sequential', 'local', 'celery', 'kubernetes')
    :return: 对应的 DAG 实例
    """
    executors_map = {
        'sequential': sequential_executor_example,
        'local': local_executor_example,
        'celery': celery_executor_example,
        'kubernetes': kubernetes_executor_example
    }
    
    if executor_type in executors_map:
        return executors_map[executor_type]()
    else:
        raise ValueError(f"Unsupported executor type: {executor_type}")


# 主函数，用于演示如何使用不同的执行器
if __name__ == '__main__':
    print("Airflow Executor Optimization Examples")
    print("=" * 40)
    
    # 这里只是演示代码结构，实际在 Airflow 中不会直接运行
    print("Examples created for different executors:")
    print("- SequentialExecutor: Good for development")
    print("- LocalExecutor: Good for single machine production")
    print("- CeleryExecutor: Good for distributed production")
    print("- KubernetesExecutor: Good for containerized environments")