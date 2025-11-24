"""
Kubernetes Pod Operator示例DAG
展示如何在Kubernetes环境中使用KubernetesPodOperator执行任务
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.providers.cncf.kubernetes.backcompat.backwards_compat_converters import (
    convert_env_vars,
)
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
    'k8s_pod_operator_examples',
    default_args=default_args,
    description='Kubernetes Pod Operator使用示例',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'kubernetes'],
)

# 基本KubernetesPodOperator使用
basic_pod_task = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["print('Hello from Kubernetes Pod!')"],
    name="basic-pod-task",
    task_id="basic_pod_task",
    get_logs=True,
    dag=dag,
)

# 带环境变量的Pod任务
env_var_pod_task = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["import os; print('Environment Variable:', os.environ.get('MY_VAR', 'Not found'))"],
    env_vars={
        'MY_VAR': 'Hello from Airflow!',
    },
    name="env-var-pod-task",
    task_id="env_var_pod_task",
    get_logs=True,
    dag=dag,
)

# 带资源限制的Pod任务
resource_limited_pod_task = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["import time; time.sleep(30); print('Task completed!')"],
    name="resource-limited-pod-task",
    task_id="resource_limited_pod_task",
    get_logs=True,
    resources={
        'request_memory': '1Gi',
        'request_cpu': '500m',
        'limit_memory': '2Gi',
        'limit_cpu': '1000m'
    },
    dag=dag,
)

# 带卷挂载的Pod任务
volume_mount_pod_task = KubernetesPodOperator(
    namespace='default',
    image="busybox:latest",
    cmds=["sh", "-c"],
    arguments=["echo 'Data written to volume' > /data/output.txt && cat /data/output.txt"],
    name="volume-mount-pod-task",
    task_id="volume_mount_pod_task",
    get_logs=True,
    volumes=[
        k8s.V1Volume(
            name='data-volume',
            persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
                claim_name='data-pvc'
            )
        )
    ],
    volume_mounts=[
        k8s.V1VolumeMount(
            name='data-volume',
            mount_path='/data',
            sub_path=None,
            read_only=False
        )
    ],
    dag=dag,
)

# 使用私有镜像仓库的Pod任务
private_image_pod_task = KubernetesPodOperator(
    namespace='default',
    image="my-private-registry.com/my-airflow-image:latest",
    cmds=["airflow", "version"],
    name="private-image-pod-task",
    task_id="private_image_pod_task",
    get_logs=True,
    image_pull_secrets=[k8s.V1LocalObjectReference("airflow-registry-secret")],
    dag=dag,
)

# 设置任务依赖关系
basic_pod_task >> env_var_pod_task >> resource_limited_pod_task
volume_mount_pod_task >> resource_limited_pod_task
private_image_pod_task >> resource_limited_pod_task