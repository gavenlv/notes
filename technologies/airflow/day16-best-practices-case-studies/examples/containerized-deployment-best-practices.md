# Apache Airflow 容器化部署最佳实践

## 1. 概述

### 1.1 目的
本文档旨在为Apache Airflow提供容器化部署的最佳实践指南，涵盖Docker镜像构建、Kubernetes部署、资源配置、安全加固、监控告警等方面，帮助团队高效、安全地部署和运维Airflow集群。

### 1.2 适用范围
本指南适用于所有使用Docker和Kubernetes部署Apache Airflow的项目，包括开发、测试、预生产和生产环境。

### 1.3 架构概览
```yaml
# 容器化部署架构图
architecture:
  layers:
    - name: "基础设施层"
      components: ["Kubernetes集群", "持久化存储", "网络"]
      
    - name: "平台服务层"
      components: ["Docker Registry", "监控系统", "日志系统"]
      
    - name: "Airflow服务层"
      components: ["Web Server", "Scheduler", "Worker", "Triggerer", "数据库"]
      
    - name: "应用层"
      components: ["DAGs", "插件", "配置"]
      
  networking:
    internal_communication: "Kubernetes Service"
    external_access: "Ingress Controller"
    security: "Network Policies"
```

## 2. Docker镜像构建最佳实践

### 2.1 基础镜像选择
```dockerfile
# Dockerfile.best_practices
# 使用官方Airflow镜像作为基础
FROM apache/airflow:2.7.0-python3.9

# 设置标签
LABEL maintainer="devops@company.com"
LABEL version="1.0"
LABEL description="Apache Airflow生产环境镜像"

# 使用非root用户运行
USER root

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /opt/airflow

# 切换回airflow用户
USER airflow
```

### 2.2 依赖管理
```dockerfile
# requirements.txt
# 生产环境依赖
apache-airflow[celery,crypto,jdbc,odbc,password,postgres,redis,ssh]==2.7.0
apache-airflow-providers-amazon==8.0.0
apache-airflow-providers-google==10.0.0
apache-airflow-providers-microsoft-azure==6.0.0
apache-airflow-providers-slack==7.0.0
apache-airflow-providers-snowflake==4.0.0
pandas==2.0.3
numpy==1.24.3
requests==2.31.0
boto3==1.28.0
google-cloud-storage==2.10.0
snowflake-connector-python==3.0.4

# 开发依赖
pytest==7.4.0
black==23.7.0
flake8==6.0.0
mypy==1.4.1
```

```dockerfile
# 安装Python依赖
COPY requirements.txt /opt/airflow/
RUN pip install --no-cache-dir -r requirements.txt

# 安装额外工具
COPY scripts/install_tools.sh /opt/airflow/scripts/
RUN chmod +x /opt/airflow/scripts/install_tools.sh && \
    /opt/airflow/scripts/install_tools.sh
```

### 2.3 安全加固
```dockerfile
# 安全加固措施
# 1. 使用最小化基础镜像
FROM python:3.9-slim

# 2. 避免安装不必要的包
# 3. 使用多阶段构建
# 4. 扫描镜像漏洞
# 5. 签名和验证镜像

# 多阶段构建示例
# 构建阶段
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
```

### 2.4 镜像优化
```bash
#!/bin/bash
# docker_build_optimization.sh

# 镜像构建优化脚本

# 启用BuildKit
export DOCKER_BUILDKIT=1

# 使用.dockerignore文件
cat > .dockerignore << EOF
.git
.gitignore
README.md
*.md
.env
*.log
__pycache__
*.pyc
.coverage
.pytest_cache
EOF

# 多阶段构建
docker build \
  --target production \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  --build-arg VERSION=1.0.0 \
  -t company/airflow:1.0.0 .

# 镜像安全扫描
docker scan company/airflow:1.0.0

# 推送镜像到Registry
docker push company/airflow:1.0.0
```

## 3. Kubernetes部署配置

### 3.1 Helm Chart配置
```yaml
# values.yaml
# Airflow Helm Chart配置

# 全局配置
global:
  airflowHome: "/opt/airflow"
  image:
    repository: "company/airflow"
    tag: "1.0.0"
    pullPolicy: "Always"
    pullSecret: "registry-secret"
    
# Web Server配置
webserver:
  replicas: 2
  resources:
    limits:
      cpu: "1"
      memory: "2Gi"
    requests:
      cpu: "500m"
      memory: "1Gi"
  service:
    type: "ClusterIP"
    port: 8080
  ingress:
    enabled: true
    hosts:
      - host: "airflow.company.com"
        paths:
          - path: "/"
            pathType: "ImplementationSpecific"
    tls:
      - secretName: "airflow-tls"
        hosts:
          - "airflow.company.com"
          
# Scheduler配置
scheduler:
  replicas: 2
  resources:
    limits:
      cpu: "1"
      memory: "2Gi"
    requests:
      cpu: "500m"
      memory: "1Gi"
  podAnnotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    
# Worker配置
workers:
  replicas: 3
  resources:
    limits:
      cpu: "2"
      memory: "4Gi"
    requests:
      cpu: "1"
      memory: "2Gi"
  podAnnotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    
# Triggerer配置
triggerer:
  replicas: 1
  resources:
    limits:
      cpu: "500m"
      memory: "1Gi"
    requests:
      cpu: "250m"
      memory: "512Mi"
      
# 数据库配置
postgresql:
  enabled: false
externalDatabase:
  host: "postgres.company.com"
  port: 5432
  user: "airflow"
  passwordSecret: "airflow-postgres-password"
  database: "airflow"
  
# Redis配置
redis:
  enabled: true
  auth:
    enabled: true
    passwordSecret: "airflow-redis-password"
    
# 配置
config:
  core:
    executor: "CeleryExecutor"
    load_examples: "False"
    store_serialized_dags: "True"
  webserver:
    expose_config: "False"
    workers: "4"
    worker_class: "sync"
  scheduler:
    catchup_by_default: "False"
    max_tis_per_query: "16"
  celery:
    worker_concurrency: "16"
    worker_prefetch_multiplier: "1"
```

### 3.2 自定义资源配置
```yaml
# custom-values.yaml
# 自定义配置覆盖

# 环境特定配置
env:
  - name: "ENVIRONMENT"
    value: "production"
  - name: "LOG_LEVEL"
    value: "INFO"
  - name: "ENABLE_DEBUG"
    value: "False"
    
# 卷挂载
extraVolumeMounts:
  - name: "dags"
    mountPath: "/opt/airflow/dags"
    readOnly: true
  - name: "logs"
    mountPath: "/opt/airflow/logs"
    
extraVolumes:
  - name: "dags"
    persistentVolumeClaim:
      claimName: "airflow-dags-pvc"
  - name: "logs"
    persistentVolumeClaim:
      claimName: "airflow-logs-pvc"
      
# 初始化容器
extraInitContainers:
  - name: "init-dags"
    image: "busybox:1.35"
    command: ["sh", "-c", "echo Initializing DAGs volume"]
    volumeMounts:
      - name: "dags"
        mountPath: "/opt/airflow/dags"
        
# 侧车容器
extraContainers:
  - name: "log-forwarder"
    image: "fluent/fluent-bit:1.9"
    volumeMounts:
      - name: "logs"
        mountPath: "/opt/airflow/logs"
    env:
      - name: "FLUENT_BIT_CONFIG"
        valueFrom:
          configMapKeyRef:
            name: "fluent-bit-config"
            key: "fluent-bit.conf"
```

### 3.3 网络策略
```yaml
# network-policies.yaml
# 网络安全策略

# 允许Web Server访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-webserver-policy
spec:
  podSelector:
    matchLabels:
      component: webserver
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # 允许来自Ingress的流量
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
    # 允许来自内部的健康检查
    - from:
        - podSelector:
            matchLabels:
              app: prometheus
      ports:
        - protocol: TCP
          port: 8080
  egress:
    # 允许访问数据库
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8
      ports:
        - protocol: TCP
          port: 5432
    # 允许访问Redis
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
          
# 允许Scheduler访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-scheduler-policy
spec:
  podSelector:
    matchLabels:
      component: scheduler
  policyTypes:
    - Egress
  egress:
    # 允许访问数据库
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8
      ports:
        - protocol: TCP
          port: 5432
    # 允许访问Redis
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    # 允许访问Worker
    - to:
        - podSelector:
            matchLabels:
              component: worker
      ports:
        - protocol: TCP
          port: 8793
          
# 默认拒绝所有流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

## 4. 资源管理和优化

### 4.1 资源请求和限制
```yaml
# resource-management.yaml
# 资源管理配置

# HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-webserver-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-webserver
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
          
# VPA配置
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: airflow-worker-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: airflow-worker
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: "worker"
        maxAllowed:
          cpu: "4"
          memory: "8Gi"
        minAllowed:
          cpu: "500m"
          memory: "1Gi"
          
# 资源配额
apiVersion: v1
kind: ResourceQuota
metadata:
  name: airflow-resource-quota
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    persistentvolumeclaims: "20"
    services.loadbalancers: "2"
```

### 4.2 存储配置
```yaml
# storage-configuration.yaml
# 存储配置

# PV配置
apiVersion: v1
kind: PersistentVolume
metadata:
  name: airflow-dags-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  nfs:
    server: nfs-server.company.com
    path: "/exports/airflow/dags"
    
# PVC配置
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airflow-dags-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs
  
# StorageClass配置
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: airflow-fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### 4.3 配置管理
```yaml
# config-management.yaml
# 配置管理

# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: airflow-config
data:
  airflow.cfg: |
    [core]
    executor = CeleryExecutor
    sql_alchemy_conn = postgresql+psycopg2://airflow:password@postgres:5432/airflow
    load_examples = False
    
    [webserver]
    rbac = True
    expose_config = False
    
    [celery]
    broker_url = redis://:password@redis:6379/0
    result_backend = redis://:password@redis:6379/0
    
  logging_config.py: |
    import logging
    
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'airflow': {
                'format': '[%(asctime)s] %(levelname)s - %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'airflow',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
    
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: airflow-secrets
type: Opaque
data:
  postgres-password: <base64_encoded_password>
  redis-password: <base64_encoded_password>
  fernet-key: <base64_encoded_fernet_key>
  webserver-secret-key: <base64_encoded_secret_key>
```

## 5. 安全加固

### 5.1 镜像安全
```bash
#!/bin/bash
# image_security.sh
# 镜像安全检查脚本

# 镜像扫描
trivy image company/airflow:1.0.0

# CVE修复
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity HIGH,CRITICAL company/airflow:1.0.0

# 签名验证
cosign verify --key cosign.pub company/airflow:1.0.0

# SBOM生成
syft company/airflow:1.0.0 -o spdx-json > airflow-sbom.json
```

### 5.2 运行时安全
```yaml
# runtime-security.yaml
# 运行时安全配置

# PodSecurityPolicy (已弃用，使用PSA替代)
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: airflow-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  readOnlyRootFilesystem: true
  
# PSA配置
apiVersion: v1
kind: Namespace
metadata:
  name: airflow
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

### 5.3 网络安全
```yaml
# network-security.yaml
# 网络安全配置

# NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-deny-external
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # 只允许来自同一命名空间的流量
    - from:
        - namespaceSelector:
            matchLabels:
              name: airflow
  egress:
    # 只允许访问必要的外部服务
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8  # 内部网络
        - ipBlock:
            cidr: 0.0.0.0/0   # 允许所有外部流量（可根据需要限制）
      ports:
        - protocol: TCP
          port: 53  # DNS
        - protocol: UDP
          port: 53  # DNS
        - protocol: TCP
          port: 443 # HTTPS
          
# ServiceMesh配置 (Istio示例)
apiVersion: networking.istio.io/v1alpha3
kind: AuthorizationPolicy
metadata:
  name: airflow-authz
  namespace: airflow
spec:
  selector:
    matchLabels:
      app: airflow
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/airflow/sa/airflow"]
      to:
        - operation:
            methods: ["GET", "POST", "PUT", "DELETE"]
```

## 6. 监控和告警

### 6.1 Prometheus监控
```yaml
# prometheus-monitoring.yaml
# Prometheus监控配置

# ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: airflow-monitor
  labels:
    app: airflow
spec:
  selector:
    matchLabels:
      app: airflow
  endpoints:
    - port: metrics
      interval: 30s
      path: /admin/metrics
      
# PrometheusRule
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: airflow-rules
spec:
  groups:
    - name: airflow.rules
      rules:
        # Scheduler健康检查
        - alert: AirflowSchedulerDown
          expr: absent(up{job="airflow-scheduler"} == 1)
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Airflow Scheduler is down"
            description: "Airflow Scheduler has disappeared from Prometheus target discovery."
            
        # Worker健康检查
        - alert: AirflowWorkerDown
          expr: absent(up{job="airflow-worker"} == 1)
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Airflow Worker is down"
            description: "Airflow Worker has disappeared from Prometheus target discovery."
            
        # DAG执行延迟
        - alert: AirflowDagExecutionDelay
          expr: airflow_dag_run_duration > 3600
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Airflow DAG execution delay"
            description: "DAG execution duration exceeds 1 hour."
```

### 6.2 日志管理
```yaml
# logging-configuration.yaml
# 日志管理配置

# Fluent Bit配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         1
        Log_Level     info
        Daemon        off
        Parsers_File  parsers.conf
        HTTP_Server   On
        HTTP_Listen   0.0.0.0
        HTTP_Port     2020
        
    [INPUT]
        Name              tail
        Tag               airflow.*
        Path              /opt/airflow/logs/**/*.log
        Parser            docker
        DB                /var/log/flb_kube.db
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On
        Refresh_Interval  10
        
    [FILTER]
        Name                kubernetes
        Match               airflow.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           On
        Merge_Log_Key       log_processed
        K8S-Logging.Parser  On
        K8S-Logging.Exclude Off
        
    [OUTPUT]
        Name            loki
        Match           airflow.*
        Host            loki-gateway
        Port            80
        Labels          job=airflow
        BatchWait       1s
        BatchSize       1001024
        LineFormat      json
        LogLevel        warn
```

### 6.3 告警配置
```yaml
# alerting-configuration.yaml
# 告警配置

# Alertmanager配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: 'smtp.company.com:587'
      smtp_from: 'alertmanager@company.com'
      smtp_auth_username: 'alertmanager'
      smtp_auth_password: 'password'
      
    route:
      group_by: ['alertname']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'team-airflow'
      
    receivers:
      - name: 'team-airflow'
        email_configs:
          - to: 'airflow-team@company.com'
            send_resolved: true
        slack_configs:
          - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
            channel: '#airflow-alerts'
            send_resolved: true
            title: '{{ template "slack.airflow.title" . }}'
            text: '{{ template "slack.airflow.text" . }}'
            
    templates:
      - '/etc/alertmanager/template/*.tmpl'
```

## 7. 备份和灾难恢复

### 7.1 数据备份策略
```yaml
# backup-strategy.yaml
# 备份策略

# 数据库备份CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: airflow-db-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点执行
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: pgdump
              image: postgres:13
              command:
                - bash
                - -c
                - |
                  pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > /backup/airflow_$(date +%Y%m%d_%H%M%S).sql
                  # 上传到对象存储
                  aws s3 cp /backup/ s3://company-backups/airflow/ --recursive
              env:
                - name: DB_HOST
                  value: "postgres.company.com"
                - name: DB_USER
                  value: "airflow"
                - name: DB_NAME
                  value: "airflow"
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: airflow-db-secret
                      key: password
              volumeMounts:
                - name: backup-storage
                  mountPath: /backup
          volumes:
            - name: backup-storage
              emptyDir: {}
          restartPolicy: OnFailure
          
# DAG备份CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: airflow-dag-backup
spec:
  schedule: "0 3 * * *"  # 每天凌晨3点执行
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: dag-backup
              image: busybox:1.35
              command:
                - sh
                - -c
                - |
                  tar -czf /backup/dags_$(date +%Y%m%d_%H%M%S).tar.gz /opt/airflow/dags
                  # 上传到对象存储
                  aws s3 cp /backup/dags_*.tar.gz s3://company-backups/airflow/dags/
              volumeMounts:
                - name: dags-volume
                  mountPath: /opt/airflow/dags
                - name: backup-storage
                  mountPath: /backup
          volumes:
            - name: dags-volume
              persistentVolumeClaim:
                claimName: airflow-dags-pvc
            - name: backup-storage
              emptyDir: {}
          restartPolicy: OnFailure
```

### 7.2 灾难恢复计划
```yaml
# disaster-recovery.yaml
# 灾难恢复配置

# 恢复脚本ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: airflow-dr-scripts
data:
  restore-db.sh: |
    #!/bin/bash
    # 数据库恢复脚本
    
    # 下载最新备份
    aws s3 cp s3://company-backups/airflow/database/latest.sql /tmp/
    
    # 恢复数据库
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f /tmp/latest.sql
    
    # 验证恢复
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM dag;"
    
  restore-dags.sh: |
    #!/bin/bash
    # DAG恢复脚本
    
    # 下载最新备份
    aws s3 cp s3://company-backups/airflow/dags/latest.tar.gz /tmp/
    
    # 解压备份
    tar -xzf /tmp/latest.tar.gz -C /opt/airflow/dags
    
    # 重新加载DAGs
    airflow dags reserialize
    
  dr-test.sh: |
    #!/bin/bash
    # 灾难恢复测试脚本
    
    echo "开始灾难恢复测试..."
    
    # 停止当前服务
    kubectl scale deployment airflow-webserver --replicas=0
    kubectl scale deployment airflow-scheduler --replicas=0
    kubectl scale deployment airflow-worker --replicas=0
    
    # 执行恢复
    ./restore-db.sh
    ./restore-dags.sh
    
    # 启动服务
    kubectl scale deployment airflow-webserver --replicas=2
    kubectl scale deployment airflow-scheduler --replicas=2
    kubectl scale deployment airflow-worker --replicas=3
    
    # 验证服务
    sleep 60
    kubectl get pods -l app=airflow
    
    echo "灾难恢复测试完成"
```

## 8. 性能优化

### 8.1 调度器优化
```yaml
# scheduler-optimization.yaml
# 调度器优化配置

# 调度器配置优化
apiVersion: v1
kind: ConfigMap
metadata:
  name: airflow-scheduler-config
data:
  airflow.cfg: |
    [scheduler]
    # 减少查询频率
    processor_poll_interval = 10
    # 增加并行处理DAG的数量
    max_threads = 4
    # 减少心跳间隔
    scheduler_heartbeat_sec = 5
    # 启用缓存
    use_row_level_locking = True
    # 优化查询
    max_tis_per_query = 16
    # 减少僵尸检测频率
    zombie_detection_interval = 300
    
    [core]
    # 启用序列化DAG
    store_serialized_dags = True
    # 减少DAG解析频率
    min_serialized_dag_update_interval = 30
```

### 8.2 Worker优化
```yaml
# worker-optimization.yaml
# Worker优化配置

# Worker资源配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: airflow
      component: worker
  template:
    metadata:
      labels:
        app: airflow
        component: worker
    spec:
      containers:
        - name: worker
          image: company/airflow:1.0.0
          command: ["airflow", "celery", "worker"]
          env:
            # 并发设置
            - name: AIRFLOW__CELERY__WORKER_CONCURRENCY
              value: "8"
            # 预取乘数
            - name: AIRFLOW__CELERY__WORKER_PREFETCH_MULTIPLIER
              value: "1"
            # 内存软限制
            - name: AIRFLOW__CELERY__WORKER_AUTOSCALE
              value: "8,2"
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
          # 健康检查
          livenessProbe:
            exec:
              command:
                - python
                - -c
                - |
                  import celery
                  from airflow.executors.celery_executor import app as celery_app
                  inspect = celery_app.control.inspect()
                  stats = inspect.stats()
                  if not stats:
                      exit(1)
            initialDelaySeconds: 60
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
```

### 8.3 数据库优化
```sql
-- database-optimization.sql
-- 数据库优化脚本

-- 创建索引
CREATE INDEX CONCURRENTLY idx_task_instance_dag_id ON task_instance (dag_id);
CREATE INDEX CONCURRENTLY idx_task_instance_state ON task_instance (state);
CREATE INDEX CONCURRENTLY idx_task_instance_execution_date ON task_instance (execution_date);
CREATE INDEX CONCURRENTLY idx_dag_run_dag_id ON dag_run (dag_id);
CREATE INDEX CONCURRENTLY idx_dag_run_state ON dag_run (state);
CREATE INDEX CONCURRENTLY idx_dag_run_execution_date ON dag_run (execution_date);

-- 分区表
CREATE TABLE task_instance_2023 PARTITION OF task_instance
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE dag_run_2023 PARTITION OF dag_run
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

-- 清理旧数据
DELETE FROM task_instance WHERE execution_date < NOW() - INTERVAL '1 year';
DELETE FROM dag_run WHERE execution_date < NOW() - INTERVAL '1 year';
DELETE FROM log WHERE dttm < NOW() - INTERVAL '6 months';

-- 更新统计信息
ANALYZE task_instance;
ANALYZE dag_run;
ANALYZE log;
```

## 9. CI/CD集成

### 9.1 构建流水线
```yaml
# ci-cd-pipeline.yaml
# CI/CD流水线配置

# GitHub Actions示例
name: Airflow CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: company/airflow:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          
  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tests
        run: |
          docker run --rm company/airflow:${{ github.sha }} pytest /opt/airflow/tests
          
      - name: Security scan
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image company/airflow:${{ github.sha }}
          
  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install airflow ./helm-chart \
            --set image.tag=${{ github.sha }} \
            --namespace airflow \
            --create-namespace
```

### 9.2 部署策略
```yaml
# deployment-strategies.yaml
# 部署策略

# 蓝绿部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-webserver-blue
spec:
  replicas: 2
  selector:
    matchLabels:
      app: airflow
      version: blue
  template:
    metadata:
      labels:
        app: airflow
        version: blue
    spec:
      containers:
        - name: webserver
          image: company/airflow:1.0.0
          
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-webserver-green
spec:
  replicas: 0  # 初始为0
  selector:
    matchLabels:
      app: airflow
      version: green
  template:
    metadata:
      labels:
        app: airflow
        version: green
    spec:
      containers:
        - name: webserver
          image: company/airflow:1.0.1

# 金丝雀部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-worker-canary
spec:
  replicas: 1  # 少量副本用于金丝雀
  selector:
    matchLabels:
      app: airflow
      version: canary
  template:
    metadata:
      labels:
        app: airflow
        version: canary
    spec:
      containers:
        - name: worker
          image: company/airflow:1.0.1
          
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-worker-stable
spec:
  replicas: 3  # 稳定版本
  selector:
    matchLabels:
      app: airflow
      version: stable
  template:
    metadata:
      labels:
        app: airflow
        version: stable
    spec:
      containers:
        - name: worker
          image: company/airflow:1.0.0
```

## 10. 故障排除和调试

### 10.1 常见问题诊断
```bash
#!/bin/bash
# troubleshooting.sh
# 故障排除脚本

# 检查Pod状态
echo "=== 检查Airflow Pod状态 ==="
kubectl get pods -n airflow -o wide

# 检查服务状态
echo "=== 检查Airflow服务状态 ==="
kubectl get svc -n airflow

# 检查Ingress状态
echo "=== 检查Ingress状态 ==="
kubectl get ingress -n airflow

# 查看最近的日志
echo "=== 查看Web Server日志 ==="
kubectl logs -n airflow -l component=webserver --tail=100

echo "=== 查看Scheduler日志 ==="
kubectl logs -n airflow -l component=scheduler --tail=100

echo "=== 查看Worker日志 ==="
kubectl logs -n airflow -l component=worker --tail=100

# 检查资源使用情况
echo "=== 检查资源使用情况 ==="
kubectl top pods -n airflow

# 检查事件
echo "=== 检查Kubernetes事件 ==="
kubectl get events -n airflow --sort-by='.lastTimestamp'

# 检查配置
echo "=== 检查ConfigMap ==="
kubectl get configmap -n airflow

# 检查Secret
echo "=== 检查Secret ==="
kubectl get secret -n airflow

# 端口转发调试
echo "=== 设置端口转发进行调试 ==="
kubectl port-forward -n airflow svc/airflow-webserver 8080:8080
```

### 10.2 性能调试
```python
# performance_debugging.py
# 性能调试工具

import logging
import time
import psutil
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class AirflowPerformanceDebugger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = []
        
    def collect_system_metrics(self):
        """收集系统指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }
        
        self.metrics.append(metrics)
        return metrics
        
    def monitor_dag_execution(self, dag_id: str, execution_date: str):
        """监控DAG执行"""
        start_time = time.time()
        
        # 这里应该调用Airflow API来监控DAG执行
        # 简化实现
        time.sleep(5)  # 模拟DAG执行时间
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.logger.info(f"DAG {dag_id} 执行时间: {execution_time:.2f}秒")
        return execution_time
        
    def analyze_scheduler_performance(self):
        """分析调度器性能"""
        # 收集调度器指标
        scheduler_metrics = {
            'timestamp': datetime.now().isoformat(),
            'dag_processing_time': self._measure_dag_processing_time(),
            'task_scheduling_latency': self._measure_task_scheduling_latency(),
            'database_query_time': self._measure_database_query_time()
        }
        
        return scheduler_metrics
        
    def _measure_dag_processing_time(self):
        """测量DAG处理时间"""
        start_time = time.time()
        
        # 模拟DAG处理
        time.sleep(0.1)
        
        end_time = time.time()
        return end_time - start_time
        
    def _measure_task_scheduling_latency(self):
        """测量任务调度延迟"""
        # 简化实现
        return 0.05  # 50毫秒
        
    def _measure_database_query_time(self):
        """测量数据库查询时间"""
        start_time = time.time()
        
        # 模拟数据库查询
        time.sleep(0.02)
        
        end_time = time.time()
        return end_time - start_time
        
    def generate_performance_report(self):
        """生成性能报告"""
        if not self.metrics:
            self.logger.warning("没有收集到性能指标")
            return
            
        # 生成CPU使用率图表
        timestamps = [m['timestamp'] for m in self.metrics]
        cpu_usage = [m['cpu_percent'] for m in self.metrics]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, cpu_usage, marker='o')
        plt.title('CPU使用率')
        plt.xlabel('时间')
        plt.ylabel('CPU使用率 (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('/tmp/cpu_usage.png')
        
        # 生成内存使用率图表
        memory_usage = [m['memory_percent'] for m in self.metrics]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, memory_usage, marker='s', color='red')
        plt.title('内存使用率')
        plt.xlabel('时间')
        plt.ylabel('内存使用率 (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('/tmp/memory_usage.png')
        
        self.logger.info("性能报告已生成")

# 使用示例
def debug_airflow_performance():
    """调试Airflow性能"""
    debugger = AirflowPerformanceDebugger()
    
    # 收集系统指标
    for i in range(10):
        metrics = debugger.collect_system_metrics()
        print(f"系统指标: {metrics}")
        time.sleep(1)
        
    # 监控DAG执行
    execution_time = debugger.monitor_dag_execution('example_dag', '2023-01-01')
    print(f"DAG执行时间: {execution_time:.2f}秒")
    
    # 分析调度器性能
    scheduler_metrics = debugger.analyze_scheduler_performance()
    print(f"调度器性能指标: {scheduler_metrics}")
    
    # 生成性能报告
    debugger.generate_performance_report()

if __name__ == "__main__":
    debug_airflow_performance()
```

这份容器化部署最佳实践文档涵盖了从Docker镜像构建到Kubernetes部署、资源配置、安全加固、监控告警、备份恢复、性能优化、CI/CD集成以及故障排除的完整内容。它提供了详细的配置示例和最佳实践建议，可以帮助团队建立一个健壮、安全、高效的Airflow容器化部署环境。