"""
Kubernetes Executor配置示例
展示如何为Kubernetes Executor配置不同的任务资源和设置
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from kubernetes.client import models as k8s

# 默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG定义
dag = DAG(
    'k8s_executor_config_examples',
    default_args=default_args,
    description='Kubernetes Executor配置示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'kubernetes', 'executor'],
)

# 基本任务配置
def print_hello():
    print("Hello from Kubernetes Executor!")

basic_task = PythonOperator(
    task_id='basic_task',
    python_callable=print_hello,
    dag=dag,
)

# 带自定义资源配置的任务
resource_intensive_task = PythonOperator(
    task_id='resource_intensive_task',
    python_callable=lambda: [i**2 for i in range(1000000)],
    executor_config={
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                        resources=k8s.V1ResourceRequirements(
                            requests={
                                "cpu": "1",
                                "memory": "2Gi"
                            },
                            limits={
                                "cpu": "2",
                                "memory": "4Gi"
                            }
                        )
                    )
                ]
            )
        ),
    },
    dag=dag,
)

# 带环境变量的任务
env_var_task = BashOperator(
    task_id='env_var_task',
    bash_command='echo "Custom Environment Variable: $CUSTOM_VAR"',
    executor_config={
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                        env=[
                            k8s.V1EnvVar(
                                name="CUSTOM_VAR",
                                value="Hello from Kubernetes Executor!"
                            )
                        ]
                    )
                ]
            )
        )
    },
    dag=dag,
)

# 带卷挂载的任务
volume_mount_task = BashOperator(
    task_id='volume_mount_task',
    bash_command='echo "Writing to mounted volume" && echo "Data from task" > /mnt/data/output.txt',
    executor_config={
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                        volume_mounts=[
                            k8s.V1VolumeMount(
                                name="data-volume",
                                mount_path="/mnt/data",
                                sub_path=None,
                                read_only=False
                            )
                        ]
                    )
                ],
                volumes=[
                    k8s.V1Volume(
                        name="data-volume",
                        persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                            claim_name="task-data-pvc"
                        )
                    )
                ]
            )
        )
    },
    dag=dag,
)

# 使用特定服务账户的任务
service_account_task = BashOperator(
    task_id='service_account_task',
    bash_command='echo "Running with specific service account"',
    executor_config={
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                service_account_name="airflow-task-account"
            )
        )
    },
    dag=dag,
)

# 带节点选择器的任务
node_selector_task = BashOperator(
    task_id='node_selector_task',
    bash_command='echo "Running on specific node type"',
    executor_config={
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                node_selector={
                    "node-type": "high-memory"
                }
            )
        )
    },
    dag=dag,
)

# 带容忍度的任务
toleration_task = BashOperator(
    task_id='toleration_task',
    bash_command='echo "Running with tolerations"',
    executor_config={
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                tolerations=[
                    k8s.V1Toleration(
                        key="special-node",
                        operator="Equal",
                        value="airflow",
                        effect="NoSchedule"
                    )
                ]
            )
        )
    },
    dag=dag,
)

# 设置任务依赖关系
basic_task >> [resource_intensive_task, env_var_task, volume_mount_task]
resource_intensive_task >> [service_account_task, node_selector_task, toleration_task]