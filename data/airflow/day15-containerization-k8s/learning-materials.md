# Day 15: 容器化与Kubernetes集成 - 学习材料

## 1. Docker容器化基础

### 1.1 Docker镜像构建

Docker镜像是容器化部署的基础。Airflow提供了官方的基础镜像，我们可以基于它构建自定义镜像。

```dockerfile
# 基础Airflow镜像
FROM apache/airflow:2.7.0

# 设置环境变量
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# 安装额外的依赖
COPY requirements.txt /
RUN pip install --no-cache -r /requirements.txt

# 复制自定义DAGs
COPY dags/ /opt/airflow/dags/

# 复制自定义插件
COPY plugins/ /opt/airflow/plugins/
```

### 1.2 多阶段构建优化

为了减小镜像体积，可以使用多阶段构建：

```dockerfile
# 构建阶段
FROM apache/airflow:2.7.0 as builder

# 安装编译依赖
RUN apt-get update && apt-get install -y build-essential

# 安装Python依赖
COPY requirements.txt /
RUN pip install --no-cache -r /requirements.txt

# 运行阶段
FROM apache/airflow:2.7.0

# 从构建阶段复制已安装的包
COPY --from=builder /home/airflow/.local /home/airflow/.local

# 设置PATH
ENV PATH=/home/airflow/.local/bin:$PATH

# 复制应用代码
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
```

### 1.3 Docker Compose部署

使用Docker Compose可以简化多容器应用的部署：

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_db_volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    restart: always

  redis:
    image: redis:latest
    ports:
      - 6379:6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 30s
      retries: 50
    restart: always

  airflow-webserver:
    build: .
    command: webserver
    ports:
      - 8080:8080
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5
    restart: always

  airflow-scheduler:
    build: .
    command: scheduler
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

  airflow-worker:
    build: .
    command: celery worker
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

volumes:
  postgres_db_volume:
```

## 2. Kubernetes基础概念

### 2.1 核心概念

#### Pod
Pod是Kubernetes中最小的可部署单元，可以包含一个或多个容器：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: airflow-webserver
spec:
  containers:
  - name: webserver
    image: apache/airflow:2.7.0
    command: ["airflow", "webserver"]
    ports:
    - containerPort: 8080
    env:
    - name: AIRFLOW__CORE__EXECUTOR
      value: "LocalExecutor"
```

#### Deployment
Deployment用于管理Pod的部署和更新：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-webserver
spec:
  replicas: 2
  selector:
    matchLabels:
      app: airflow-webserver
  template:
    metadata:
      labels:
        app: airflow-webserver
    spec:
      containers:
      - name: webserver
        image: apache/airflow:2.7.0
        command: ["airflow", "webserver"]
        ports:
        - containerPort: 8080
        env:
        - name: AIRFLOW__CORE__EXECUTOR
          value: "LocalExecutor"
```

#### Service
Service为Pod提供稳定的网络访问入口：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: airflow-webserver
spec:
  selector:
    app: airflow-webserver
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: LoadBalancer
```

### 2.2 ConfigMap和Secret

ConfigMap用于存储非敏感配置数据：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: airflow-config
data:
  AIRFLOW__CORE__EXECUTOR: "CeleryExecutor"
  AIRFLOW__CORE__LOAD_EXAMPLES: "False"
```

Secret用于存储敏感信息：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: airflow-secrets
type: Opaque
data:
  postgres-password: cG9zdGdyZXM=
  redis-password: cmVkaXM=
```

## 3. Airflow Helm Chart

### 3.1 Helm基础

Helm是Kubernetes的包管理工具，使用Chart来描述应用的部署配置。

安装Helm：
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

添加Airflow Helm仓库：
```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

### 3.2 官方Airflow Helm Chart详解

官方Chart的主要配置项：

```yaml
# values.yaml
# Airflow配置
airflow:
  # 镜像配置
  image:
    repository: apache/airflow
    tag: 2.7.0
  # 执行器配置
  executor: "CeleryExecutor"
  # 配置参数
  config:
    AIRFLOW__CORE__LOAD_EXAMPLES: "False"
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: "True"
  # 用户配置
  users:
    - username: admin
      password: admin
      role: Admin
      email: admin@example.com
      firstName: admin
      lastName: user

# 数据库配置
postgresql:
  enabled: true
  postgresqlPassword: airflow

# Redis配置（CeleryExecutor需要）
redis:
  enabled: true

# Webserver配置
webserver:
  replicas: 1
  # 资源限制
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 256Mi

# Scheduler配置
scheduler:
  replicas: 1
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 256Mi

# Worker配置（CeleryExecutor需要）
workers:
  replicas: 2
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 256Mi

# 触发器配置（Airlfow 2.2+）
triggerer:
  replicas: 1
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 256Mi
```

### 3.3 自定义Values配置

自定义DAGs和插件的挂载：

```yaml
# 持久化卷配置
dags:
  persistence:
    enabled: true
    storageClass: ""
    accessMode: ReadWriteOnce
    size: 1Gi
    existingClaim: ""

# 自定义DAGs挂载
extraVolumeMounts:
  - name: dags
    mountPath: /opt/airflow/dags
    subPath: dags

extraVolumes:
  - name: dags
    persistentVolumeClaim:
      claimName: airflow-dags-pvc

# 自定义插件挂载
extraVolumeMounts:
  - name: plugins
    mountPath: /opt/airflow/plugins
    subPath: plugins

extraVolumes:
  - name: plugins
    persistentVolumeClaim:
      claimName: airflow-plugins-pvc
```

## 4. Kubernetes Executor

### 4.1 KubernetesExecutor工作原理

KubernetesExecutor直接与Kubernetes API交互，为每个任务创建一个Pod：

```python
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'kubernetes_executor_example',
    default_args=default_args,
    description='A simple DAG using KubernetesExecutor',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

task1 = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["print('Hello from KubernetesExecutor!')"],
    name="hello-k8s-executor",
    task_id="hello_k8s_executor_task",
    get_logs=True,
    dag=dag,
)
```

### 4.2 Pod模板配置

可以为任务定义Pod模板：

```yaml
# pod_template.yaml
apiVersion: v1
kind: Pod
metadata:
  name: airflow-pod-template
spec:
  containers:
    - name: base
      image: apache/airflow:2.7.0
      imagePullPolicy: IfNotPresent
      resources:
        requests:
          memory: "512Mi"
          cpu: "250m"
        limits:
          memory: "1Gi"
          cpu: "500m"
      env:
        - name: AIRFLOW__CORE__EXECUTOR
          value: "KubernetesExecutor"
  restartPolicy: Never
```

### 4.3 资源请求和限制

在配置中设置资源限制：

```python
task2 = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["import time; time.sleep(30); print('Task completed!')"],
    name="resource-limited-task",
    task_id="resource_limited_task",
    get_logs=True,
    resources={
        'request_memory': '1Gi',
        'request_cpu': '500m',
        'limit_memory': '2Gi',
        'limit_cpu': '1000m'
    },
    dag=dag,
)
```

## 5. Kubernetes Pod Operator

### 5.1 KubernetesPodOperator使用

KubernetesPodOperator允许在Kubernetes集群中创建和管理Pod：

```python
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.providers.cncf.kubernetes.backcompat.backwards_compat_converters import (
    convert_env_vars,
)

# 基本使用
task = KubernetesPodOperator(
    namespace='default',
    image="ubuntu:latest",
    cmds=["bash", "-cx"],
    arguments=["echo", "10"],
    name="test-pod",
    task_id="task-one",
    get_logs=True,
    dag=dag,
)

# 使用环境变量
task_with_env = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["import os; print(os.environ.get('MY_VAR', 'Not found'))"],
    env_vars={
        'MY_VAR': 'Hello from Airflow!',
    },
    name="env-var-pod",
    task_id="env_var_task",
    get_logs=True,
    dag=dag,
)
```

### 5.2 动态Pod创建和管理

动态创建Pod执行任务：

```python
from airflow.models import Variable

def create_dynamic_pod(**context):
    # 从变量中获取配置
    image_name = Variable.get("docker_image_name", default_var="python:3.8")
    command = Variable.get("pod_command", default_var="echo 'Hello World'")
    
    task = KubernetesPodOperator(
        namespace='default',
        image=image_name,
        cmds=["bash", "-c"],
        arguments=[command],
        name=f"dynamic-pod-{context['run_id']}",
        task_id=f"dynamic_pod_task_{context['run_id']}",
        get_logs=True,
        dag=dag,
    )
    
    return task.execute(context)

dynamic_task = PythonOperator(
    task_id='create_dynamic_pod',
    python_callable=create_dynamic_pod,
    dag=dag,
)
```

### 5.3 环境变量和卷挂载

使用环境变量和卷挂载：

```python
task_with_volume = KubernetesPodOperator(
    namespace='default',
    image="python:3.8",
    cmds=["python", "-c"],
    arguments=["import os; print('Data:', open('/data/input.txt').read())"],
    name="volume-mount-pod",
    task_id="volume_mount_task",
    get_logs=True,
    volumes=[
        {
            'name': 'data-volume',
            'persistentVolumeClaim': {
                'claimName': 'data-pvc'
            }
        }
    ],
    volume_mounts=[
        {
            'name': 'data-volume',
            'mountPath': '/data',
            'subPath': None,
            'readOnly': False
        }
    ],
    dag=dag,
)
```

## 6. 安全和权限管理

### 6.1 RBAC角色和绑定

创建RBAC角色和绑定：

```yaml
# airflow-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: airflow-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "create", "delete"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]

---
# airflow-rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: airflow-rolebinding
  namespace: default
subjects:
- kind: ServiceAccount
  name: airflow-serviceaccount
  namespace: default
roleRef:
  kind: Role
  name: airflow-role
  apiGroup: rbac.authorization.k8s.io
```

### 6.2 网络策略配置

限制Pod网络访问：

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-network-policy
spec:
  podSelector:
    matchLabels:
      app: airflow
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: airflow-webserver
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
```

### 6.3 镜像拉取密钥

配置私有镜像仓库访问：

```yaml
# image-pull-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: airflow-registry-secret
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

在Pod中使用：

```python
task_with_private_image = KubernetesPodOperator(
    namespace='default',
    image="my-private-registry.com/my-airflow-image:latest",
    cmds=["airflow", "version"],
    name="private-image-pod",
    task_id="private_image_task",
    get_logs=True,
    image_pull_secrets=[k8s.V1LocalObjectReference("airflow-registry-secret")],
    dag=dag,
)
```

## 7. 监控和日志

### 7.1 Prometheus指标集成

配置Prometheus抓取Airflow指标：

```yaml
# prometheus-config.yaml
scrape_configs:
- job_name: 'airflow'
  static_configs:
  - targets: ['airflow-webserver:8080']
  metrics_path: '/admin/metrics/'
```

### 7.2 Grafana仪表板配置

创建Airflow监控仪表板：

```json
{
  "dashboard": {
    "id": null,
    "title": "Airflow Monitoring",
    "panels": [
      {
        "id": 1,
        "title": "DAG Runs",
        "type": "graph",
        "targets": [
          {
            "expr": "airflow_dag_run_duration",
            "legendFormat": "{{dag_id}}"
          }
        ]
      }
    ]
  }
}
```

### 7.3 日志收集方案

配置EFK日志收集：

```yaml
# fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/airflow-*.log
      pos_file /var/log/fluentd-airflow.log.pos
      tag airflow.*
      read_from_head true
      <parse>
        @type json
        time_key time
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
    
    <match airflow.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
    </match>
```