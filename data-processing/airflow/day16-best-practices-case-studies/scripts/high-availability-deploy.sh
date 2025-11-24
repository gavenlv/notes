#!/bin/bash

# Airflow高可用部署脚本
# 用于部署和配置高可用Airflow集群

set -e  # 遇到错误时退出

# 配置变量
KUBE_NAMESPACE="airflow"
KUBE_CONTEXT="production"
RELEASE_NAME="airflow"
CHART_REPO="https://airflow.apache.org"
CHART_NAME="airflow"
CHART_VERSION="1.9.0"
VALUES_FILE="values-ha.yaml"
LOG_FILE="/var/log/airflow/ha-deploy.log"
REPORT_DIR="/tmp/airflow-ha-deploy-report-$(date +%Y%m%d-%H%M%S)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_info() {
    log "${GREEN}INFO${NC} - $1"
}

log_warn() {
    log "${YELLOW}WARN${NC} - $1"
}

log_error() {
    log "${RED}ERROR${NC} - $1"
}

log_debug() {
    log "${BLUE}DEBUG${NC} - $1"
}

# 检查必要命令
check_dependencies() {
    log_info "检查必要命令..."
    
    commands=("kubectl" "helm" "openssl" "jq")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 命令未找到，请安装后重试"
            exit 1
        fi
    done
    
    log_info "所有必要命令检查通过"
}

# 检查Kubernetes环境
check_kubernetes_environment() {
    log_info "检查Kubernetes环境..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 检查命名空间是否存在
    if ! kubectl get namespace $KUBE_NAMESPACE &> /dev/null; then
        log_info "创建命名空间: $KUBE_NAMESPACE"
        kubectl create namespace $KUBE_NAMESPACE
    else
        log_info "命名空间已存在: $KUBE_NAMESPACE"
    fi
    
    # 检查Helm仓库
    if ! helm repo list | grep -q "apache-airflow"; then
        log_info "添加Apache Airflow Helm仓库"
        helm repo add apache-airflow $CHART_REPO
    fi
    
    # 更新Helm仓库
    helm repo update
    
    log_info "Kubernetes环境检查完成"
}

# 生成Fernet密钥
generate_fernet_key() {
    log_info "生成Fernet密钥..."
    
    # 生成Fernet密钥
    FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null)
    
    if [ -n "$FERNET_KEY" ]; then
        log_info "Fernet密钥生成完成"
        echo "$FERNET_KEY" > /tmp/fernet-key.txt
    else
        log_error "Fernet密钥生成失败"
        return 1
    fi
}

# 创建Secret
create_secrets() {
    log_info "创建Secret..."
    
    # 生成或获取Fernet密钥
    if [ ! -f /tmp/fernet-key.txt ]; then
        generate_fernet_key
    fi
    
    FERNET_KEY=$(cat /tmp/fernet-key.txt)
    
    # 创建Airflow Secret
    cat > /tmp/airflow-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: airflow-secrets
  namespace: $KUBE_NAMESPACE
type: Opaque
data:
  fernet-key: $(echo -n "$FERNET_KEY" | base64)
  redis-password: $(openssl rand -base64 20 | tr -d '\n' | base64)
  webserver-secret-key: $(openssl rand -base64 20 | tr -d '\n' | base64)
EOF
    
    kubectl apply -f /tmp/airflow-secrets.yaml
    
    # 创建数据库密码Secret
    cat > /tmp/database-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: airflow-postgresql
  namespace: $KUBE_NAMESPACE
type: Opaque
data:
  postgresql-password: $(openssl rand -base64 20 | tr -d '\n' | base64)
EOF
    
    kubectl apply -f /tmp/database-secrets.yaml
    
    # 创建外部数据库密码Secret（如果使用外部数据库）
    cat > /tmp/external-database-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: external-database-secrets
  namespace: $KUBE_NAMESPACE
type: Opaque
data:
  connection: $(echo -n "postgresql://airflow:$(openssl rand -base64 20 | tr -d '\n')@external-db.example.com:5432/airflow" | base64)
EOF
    
    kubectl apply -f /tmp/external-database-secrets.yaml
    
    log_info "Secret创建完成"
}

# 创建高可用配置文件
create_ha_values_file() {
    log_info "创建高可用配置文件..."
    
    # 创建高可用配置文件
    cat > $VALUES_FILE << 'EOF'
# Apache Airflow高可用配置

# 全局配置
fullnameOverride: "airflow"

# 镜像配置
images:
  airflow:
    repository: apache/airflow
    tag: 2.7.0-python3.9
  useDefaultImageForMigration: true
  pullPolicy: IfNotPresent

# 并发配置
config:
  core:
    # 并行执行任务数
    parallelism: 32
    # 每个DAG最大活跃任务数
    max_active_tasks_per_dag: 16
    # 最大主动运行的DAG数
    max_active_runs_per_dag: 16
    # 启用DAG序列化
    store_serialized_dags: "True"
    # 启用DAG fetching
    store_dag_code: "True"
  scheduler:
    # 调度器心跳间隔
    scheduler_heartbeat_sec: 5
    # 调度器处理的DAG文件数
    max_dagruns_per_loop_to_schedule: 10
    # 调度器处理的文件解析进程数
    parsing_processes: 4
    # 文件处理超时时间
    file_process_timeout: 120
    # 调度器运行周期
    scheduler_idle_sleep_time: 1
    # 最小文件处理间隔
    min_file_process_interval: 30
    # 调度器Pod数量
    scheduler_replicas: 3
  webserver:
    # Webserver worker数
    workers: 4
    # Webserver worker类
    worker_class: sync
    # Webserver超时时间
    web_server_worker_timeout: 300
    # Webserver最大请求
    worker_max_requests: 1000
    # Webserver最大请求抖动
    worker_max_requests_jitter: 100
  celery:
    # Celery worker并发数
    worker_concurrency: 16
  logging:
    # 日志级别
    logging_level: INFO
    # 启用远程日志
    remote_logging: "True"

# Webserver配置
webserver:
  enabled: true
  replicas: 3
  resources:
    limits:
      cpu: "1"
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi
  service:
    type: ClusterIP
    ports:
      - name: airflow-ui
        port: 8080
  readinessProbe:
    enabled: true
    initialDelaySeconds: 60
    periodSeconds: 30
    timeoutSeconds: 10
    failureThreshold: 10
  livenessProbe:
    enabled: true
    initialDelaySeconds: 300
    periodSeconds: 60
    timeoutSeconds: 10
    failureThreshold: 5
  podDisruptionBudget:
    enabled: true
    maxUnavailable: 1

# Scheduler配置
scheduler:
  enabled: true
  replicas: 3
  resources:
    limits:
      cpu: "1"
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi
  podDisruptionBudget:
    enabled: true
    maxUnavailable: 1

# Worker配置
workers:
  enabled: true
  replicas: 5
  resources:
    limits:
      cpu: "1"
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi
  podDisruptionBudget:
    enabled: true
    maxUnavailable: 1
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 80

# Triggerer配置
triggerer:
  enabled: true
  replicas: 2
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 512Mi
  podDisruptionBudget:
    enabled: true
    maxUnavailable: 1

# 数据库配置
postgresql:
  enabled: true
  postgresqlUsername: airflow
  postgresqlDatabase: airflow
  existingSecret: airflow-postgresql
  persistence:
    enabled: true
    size: 20Gi
    storageClass: ""
  resources:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 512Mi
  replication:
    enabled: true
    readReplicas: 2
  service:
    ports:
      postgresql: 5432

# Redis配置（用于CeleryExecutor）
redis:
  enabled: true
  auth:
    enabled: true
    existingSecret: airflow-secrets
    existingSecretPasswordKey: redis-password
  master:
    persistence:
      enabled: true
      size: 8Gi
      storageClass: ""
    resources:
      limits:
        cpu: 500m
        memory: 1Gi
      requests:
        cpu: 250m
        memory: 512Mi
  replica:
    replicaCount: 3
    resources:
      limits:
        cpu: 500m
        memory: 1Gi
      requests:
        cpu: 250m
        memory: 512Mi
  sentinel:
    enabled: true
    masterSet: airflowsentinel
    quorum: 2
    parallelSyncs: 1
    downAfterMilliseconds: 60000
    failoverTimeout: 180000

# 外部数据库配置（如果使用外部数据库）
# externalDatabase:
#   type: postgres
#   host: external-db.example.com
#   port: 5432
#   user: airflow
#   passwordSecret: external-database-secrets
#   passwordSecretKey: connection
#   database: airflow

# 外部Redis配置（如果使用外部Redis）
# externalRedis:
#   host: external-redis.example.com
#   port: 6379
#   passwordSecret: airflow-secrets
#   passwordSecretKey: redis-password
#   databaseNumber: 1

# DAGs配置
dags:
  persistence:
    enabled: true
    size: 10Gi
    storageClass: ""
  gitSync:
    enabled: true
    repo: https://github.com/example/airflow-dags.git
    branch: main
    rev: HEAD
    depth: 1
    maxFailures: 0
    subPath: "dags"
    wait: 60
    containerName: git-sync
    resources:
      limits:
        cpu: 100m
        memory: 128Mi
      requests:
        cpu: 50m
        memory: 64Mi

# 日志配置
logs:
  persistence:
    enabled: true
    size: 20Gi
    storageClass: ""

# 网络策略
networkPolicies:
  enabled: true

# RBAC配置
rbac:
  create: true
  enabled: true

# 服务账户
serviceAccount:
  create: true
  name: "airflow"

# Ingress配置
ingress:
  enabled: true
  web:
    annotations:
      kubernetes.io/ingress.class: nginx
      nginx.ingress.kubernetes.io/rewrite-target: /
    hosts:
      - name: airflow.example.com
        path: /
    tls:
      - secretName: airflow-tls
        hosts:
          - airflow.example.com

# 监控配置
prometheusRule:
  enabled: true
  additionalLabels: {}
  namespace: ""
  rules:
    - alert: AirflowSchedulerDown
      expr: airflow_scheduler_heartbeat <= 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Airflow scheduler is down"
        description: "Airflow scheduler has not heartbeated for more than 5 minutes"

# 资源配额
resources:
  limits:
    cpu: "2"
    memory: 4Gi
  requests:
    cpu: "1"
    memory: 2Gi

# 节点选择器
nodeSelector: {}

# 容忍度
tolerations: []

# 亲和性
affinity: 
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: component
            operator: In
            values:
            - webserver
            - scheduler
            - worker
        topologyKey: kubernetes.io/hostname
EOF
    
    log_info "高可用配置文件创建完成: $VALUES_FILE"
}

# 部署Airflow
deploy_airflow() {
    log_info "部署Airflow..."
    
    # 安装或升级Airflow
    if helm list -n $KUBE_NAMESPACE | grep -q $RELEASE_NAME; then
        log_info "升级现有Airflow部署"
        helm upgrade --install $RELEASE_NAME apache-airflow/airflow \
            --namespace $KUBE_NAMESPACE \
            --version $CHART_VERSION \
            --values $VALUES_FILE \
            --timeout 30m0s
    else
        log_info "全新安装Airflow"
        helm install $RELEASE_NAME apache-airflow/airflow \
            --namespace $KUBE_NAMESPACE \
            --version $CHART_VERSION \
            --values $VALUES_FILE \
            --timeout 30m0s
    fi
    
    if [ $? -eq 0 ]; then
        log_info "Airflow部署完成"
    else
        log_error "Airflow部署失败"
        return 1
    fi
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 等待部署完成
    log_info "等待Pod就绪..."
    kubectl wait --for=condition=ready pod -l component=webserver -n $KUBE_NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l component=scheduler -n $KUBE_NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l component=worker -n $KUBE_NAMESPACE --timeout=300s
    
    # 检查Pod状态
    log_info "检查Pod状态..."
    kubectl get pods -n $KUBE_NAMESPACE
    
    # 检查服务
    log_info "检查服务..."
    kubectl get services -n $KUBE_NAMESPACE
    
    # 检查Ingress
    log_info "检查Ingress..."
    kubectl get ingress -n $KUBE_NAMESPACE
    
    # 检查资源使用情况
    log_info "检查资源使用情况..."
    kubectl top pods -n $KUBE_NAMESPACE
    
    log_info "部署验证完成"
}

# 生成部署报告
generate_deployment_report() {
    log_info "生成部署报告..."
    
    # 创建报告目录
    mkdir -p $REPORT_DIR
    
    # 生成汇总报告
    cat > $REPORT_DIR/summary.txt << EOF
Airflow高可用部署报告
生成时间: $(date)
部署名称: $RELEASE_NAME
命名空间: $KUBE_NAMESPACE
Chart版本: $CHART_VERSION

部署状态:
1. Webserver: $(kubectl get deployment airflow-webserver -n $KUBE_NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo 0)/$(kubectl get deployment airflow-webserver -n $KUBE_NAMESPACE -o jsonpath='{.status.replicas}' 2>/dev/null || echo 0) 就绪
2. Scheduler: $(kubectl get deployment airflow-scheduler -n $KUBE_NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo 0)/$(kubectl get deployment airflow-scheduler -n $KUBE_NAMESPACE -o jsonpath='{.status.replicas}' 2>/dev/null || echo 0) 就绪
3. Worker: $(kubectl get deployment airflow-worker -n $KUBE_NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo 0)/$(kubectl get deployment airflow-worker -n $KUBE_NAMESPACE -o jsonpath='{.status.replicas}' 2>/dev/null || echo 0) 就绪
4. Triggerer: $(kubectl get deployment airflow-triggerer -n $KUBE_NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo 0)/$(kubectl get deployment airflow-triggerer -n $KUBE_NAMESPACE -o jsonpath='{.status.replicas}' 2>/dev/null || echo 0) 就绪
5. PostgreSQL: $(if kubectl get statefulset airflow-postgresql -n $KUBE_NAMESPACE &>/dev/null; then echo "运行中"; else echo "未部署"; fi)
6. Redis: $(if kubectl get statefulset airflow-redis-master -n $KUBE_NAMESPACE &>/dev/null; then echo "运行中"; else echo "未部署"; fi)

资源配置:
1. Webserver资源: $(kubectl get deployment airflow-webserver -n $KUBE_NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null || echo "未知")
2. Scheduler资源: $(kubectl get deployment airflow-scheduler -n $KUBE_NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null || echo "未知")
3. Worker资源: $(kubectl get deployment airflow-worker -n $KUBE_NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null || echo "未知")

网络配置:
1. Ingress: $(if kubectl get ingress airflow-ingress -n $KUBE_NAMESPACE &>/dev/null; then echo "已配置"; else echo "未配置"; fi)
2. 网络策略: $(if kubectl get networkpolicy -n $KUBE_NAMESPACE &>/dev/null; then echo "已启用"; else echo "未启用"; fi)
EOF
    
    # 保存Pod详细信息
    kubectl get pods -n $KUBE_NAMESPACE -o wide > $REPORT_DIR/pods.txt
    
    # 保存服务信息
    kubectl get services -n $KUBE_NAMESPACE -o wide > $REPORT_DIR/services.txt
    
    # 保存Ingress信息
    kubectl get ingress -n $KUBE_NAMESPACE -o yaml > $REPORT_DIR/ingress.yaml 2>/dev/null || echo "未配置Ingress"
    
    # 保存配置信息
    helm get values $RELEASE_NAME -n $KUBE_NAMESPACE > $REPORT_DIR/values.yaml
    
    # 压缩报告
    tar -czf $REPORT_DIR.tar.gz -C /tmp airflow-ha-deploy-report-$(date +%Y%m%d-%H%M%S)
    
    log_info "部署报告生成完成: $REPORT_DIR.tar.gz"
}

# 执行完整高可用部署
perform_ha_deployment() {
    log_info "开始执行高可用部署..."
    
    check_dependencies
    check_kubernetes_environment
    create_secrets
    create_ha_values_file
    deploy_airflow
    verify_deployment
    generate_deployment_report
    
    log_info "高可用部署执行完成"
}

# 扩容Worker
scale_workers() {
    local replicas=$1
    
    if [ -z "$replicas" ]; then
        log_error "请提供要扩容的副本数"
        return 1
    fi
    
    log_info "扩容Worker到 $replicas 个副本..."
    
    helm upgrade --install $RELEASE_NAME apache-airflow/airflow \
        --namespace $KUBE_NAMESPACE \
        --version $CHART_VERSION \
        --values $VALUES_FILE \
        --set workers.replicas=$replicas
    
    if [ $? -eq 0 ]; then
        log_info "Worker扩容完成"
    else
        log_error "Worker扩容失败"
        return 1
    fi
}

# 更新配置
update_configuration() {
    local config_file=$1
    
    if [ -z "$config_file" ]; then
        log_error "请提供配置文件路径"
        return 1
    fi
    
    if [ ! -f "$config_file" ]; then
        log_error "配置文件不存在: $config_file"
        return 1
    fi
    
    log_info "更新配置文件: $config_file"
    
    # 备份当前配置
    cp $VALUES_FILE $VALUES_FILE.backup.$(date +%Y%m%d-%H%M%S)
    
    # 更新配置文件
    cp $config_file $VALUES_FILE
    
    # 应用新配置
    helm upgrade --install $RELEASE_NAME apache-airflow/airflow \
        --namespace $KUBE_NAMESPACE \
        --version $CHART_VERSION \
        --values $VALUES_FILE
    
    if [ $? -eq 0 ]; then
        log_info "配置更新完成"
    else
        log_error "配置更新失败"
        return 1
    fi
}

# 回滚部署
rollback_deployment() {
    log_info "回滚部署..."
    
    helm rollback $RELEASE_NAME -n $KUBE_NAMESPACE
    
    if [ $? -eq 0 ]; then
        log_info "部署回滚完成"
    else
        log_error "部署回滚失败"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "Airflow高可用部署脚本"
    echo "用法: $0 [选项] [参数]"
    echo ""
    echo "选项:"
    echo "  deploy             执行完整高可用部署"
    echo "  scale <replicas>   扩容Worker到指定副本数"
    echo "  update <file>      使用指定配置文件更新部署"
    echo "  rollback           回滚到上一个版本"
    echo "  report             生成部署报告"
    echo "  help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy"
    echo "  $0 scale 10"
    echo "  $0 update values-production.yaml"
    echo "  $0 rollback"
}

# 主函数
main() {
    case "$1" in
        deploy)
            perform_ha_deployment
            ;;
        scale)
            if [ -n "$2" ]; then
                scale_workers "$2"
            else
                log_error "请提供要扩容的副本数"
                show_help
                exit 1
            fi
            ;;
        update)
            if [ -n "$2" ]; then
                update_configuration "$2"
            else
                log_error "请提供配置文件路径"
                show_help
                exit 1
            fi
            ;;
        rollback)
            rollback_deployment
            ;;
        report)
            generate_deployment_report
            ;;
        help)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"