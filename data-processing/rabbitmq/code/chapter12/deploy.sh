#!/bin/bash
# RabbitMQ云原生部署脚本
# 用于在Kubernetes环境中快速部署RabbitMQ集群

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
NAMESPACE="rabbitmq-system"
CLUSTER_NAME="rabbitmq-cluster"
REPLICAS=3
IMAGE="rabbitmq:3.10-management-alpine"
STORAGE_CLASS="rabbitmq-storage"
STORAGE_SIZE="20Gi"

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl 未安装或不在PATH中"
        exit 1
    fi
    
    # 检查helm
    if ! command -v helm &> /dev/null; then
        print_error "Helm 未安装或不在PATH中"
        exit 1
    fi
    
    # 检查kubectl连接
    if ! kubectl cluster-info &> /dev/null; then
        print_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 函数：生成密码和令牌
generate_secrets() {
    print_info "生成安全凭据..."
    
    # 生成RabbitMQ Erlang cookie
    ERLANG_COOKIE=$(openssl rand -base64 32)
    export ERLANG_COOKIE
    
    # 生成管理员密码
    ADMIN_PASSWORD=$(openssl rand -base64 16)
    export ADMIN_PASSWORD
    
    # 生成服务账户令牌（如果需要）
    SERVICE_TOKEN=$(openssl rand -base64 24)
    export SERVICE_TOKEN
    
    print_success "安全凭据生成完成"
}

# 函数：创建命名空间
create_namespace() {
    print_info "创建命名空间 $NAMESPACE..."
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # 添加标签
    kubectl label namespace $NAMESPACE name=$NAMESPACE --overwrite
    
    print_success "命名空间 $NAMESPACE 创建完成"
}

# 函数：创建StorageClass
create_storage_class() {
    print_info "创建StorageClass..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: $STORAGE_CLASS
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
EOF

    print_success "StorageClass $STORAGE_CLASS 创建完成"
}

# 函数：创建ConfigMap
create_configmap() {
    print_info "创建ConfigMap..."
    
    # 创建RabbitMQ配置文件
    cat <<EOF > /tmp/rabbitmq.conf
# RabbitMQ服务器配置

# 循环用户限制
loopback_users = none

# 默认用户配置
default_user = admin
default_pass = $ADMIN_PASSWORD
default_permissions.configure = .*
default_permissions.read = .*
default_permissions.write = .*

# 集群配置
cluster_formation.peer_discovery_backend = classic_config
cluster_formation.classic_config.nodes.1 = rabbitmq-cluster-0.rabbitmq-cluster-headless.rabbitmq-system.svc.cluster.local
cluster_formation.classic_config.nodes.2 = rabbitmq-cluster-1.rabbitmq-cluster-headless.rabbitmq-system.svc.cluster.local
cluster_formation.classic_config.nodes.3 = rabbitmq-cluster-2.rabbitmq-cluster-headless.rabbitmq-system.svc.cluster.local

# 内存配置
vm_memory_high_watermark.relative = 1.20
vm_memory_high_watermark_paging_ratio = 0.7

# 磁盘空间配置
disk_free_limit.absolute = 6GB

# 网络配置
network_backlog = 1000

# 队列配置
default_queue_durable = true
default_queue_auto_delete = false

# 消息配置
max_message_size = 134217728

# 管理界面配置
management.tcp.port = 15672
management.tcp.ip = ::

# 监控配置
prometheus.tcp.port = 15692
prometheus.tcp.ip = ::

# 日志配置
log.console = true
log.console.level = info
log.file.level = info
EOF

    # 创建插件配置
    cat <<EOF > /tmp/enabled_plugins
[rabbitmq_management,rabbitmq_monitoring,rabbitmq_peer_discovery_k8s,rabbitmq_consistent_hash_exchange,rabbitmq_delayed_message_exchange,rabbitmq_federation,rabbitmq_shovel,rabbitmq_tracing].
EOF

    # 应用ConfigMap
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: $CLUSTER_NAME-config
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
data:
  rabbitmq.conf: |
$(cat /tmp/rabbitmq.conf | sed 's/^/    /')
  enabled_plugins: |
$(cat /tmp/enabled_plugins | sed 's/^/    /')
EOF

    # 清理临时文件
    rm -f /tmp/rabbitmq.conf /tmp/enabled_plugins
    
    print_success "ConfigMap $CLUSTER_NAME-config 创建完成"
}

# 函数：创建Secret
create_secret() {
    print_info "创建Secret..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: $CLUSTER_NAME-credentials
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
type: Opaque
data:
  username: YWRtaW4=
  password: $(echo -n "$ADMIN_PASSWORD" | base64)
  erlang-cookie: $(echo -n "$ERLANG_COOKIE" | base64)
EOF

    print_success "Secret $CLUSTER_NAME-credentials 创建完成"
}

# 函数：创建ServiceAccount
create_serviceaccount() {
    print_info "创建ServiceAccount..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: $CLUSTER_NAME-sa
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
automountServiceAccountToken: true
EOF

    print_success "ServiceAccount $CLUSTER_NAME-sa 创建完成"
}

# 函数：创建RBAC配置
create_rbac() {
    print_info "创建RBAC配置..."
    
    # 创建Role
    cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: $CLUSTER_NAME-role
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
rules:
- apiGroups: [""]
  resources: ["endpoints"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["services"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
EOF

    # 创建RoleBinding
    cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: $CLUSTER_NAME-rolebinding
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
subjects:
- kind: ServiceAccount
  name: $CLUSTER_NAME-sa
  namespace: $NAMESPACE
roleRef:
  kind: Role
  name: $CLUSTER_NAME-role
  apiGroup: rbac.authorization.k8s.io
EOF

    print_success "RBAC配置创建完成"
}

# 函数：创建StatefulSet
create_statefulset() {
    print_info "创建StatefulSet..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: $CLUSTER_NAME
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
spec:
  serviceName: $CLUSTER_NAME-headless
  replicas: $REPLICAS
  selector:
    matchLabels:
      app: rabbitmq
      cluster: $CLUSTER_NAME
  template:
    metadata:
      labels:
        app: rabbitmq
        cluster: $CLUSTER_NAME
    spec:
      serviceAccountName: $CLUSTER_NAME-sa
      terminationGracePeriodSeconds: 30
      containers:
      - name: rabbitmq
        image: $IMAGE
        ports:
        - containerPort: 5672
          name: amqp
          protocol: TCP
        - containerPort: 15672
          name: management
          protocol: TCP
        - containerPort: 25672
          name: clustering
          protocol: TCP
        - containerPort: 15692
          name: metrics
          protocol: TCP
        env:
        - name: MY_POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: MY_POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: MY_POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        - name: MY_NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: RABBITMQ_DEFAULT_USER
          value: "admin"
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: $CLUSTER_NAME-credentials
              key: password
        - name: RABBITMQ_ERLANG_COOKIE
          valueFrom:
            secretKeyRef:
              name: $CLUSTER_NAME-credentials
              key: erlang-cookie
        - name: RABBITMQ_USE_LONGNAME
          value: "true"
        - name: RABBITMQ_NODENAME
          value: "rabbitmq@\$(MY_POD_NAME).\$(SERVICE_NAME).\$(MY_POD_NAMESPACE).svc.cluster.local"
        volumeMounts:
        - name: rabbitmq-data
          mountPath: /var/lib/rabbitmq
          subPath: rabbitmq
        - name: rabbitmq-config
          mountPath: /etc/rabbitmq
        livenessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - ping
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          exec:
            command:
            - rabbitmq-diagnostics
            - check_port_connectivity
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 6
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
        securityContext:
          runAsNonRoot: true
          runAsUser: 999
          runAsGroup: 999
          fsGroup: 999
      volumes:
      - name: rabbitmq-config
        configMap:
          name: $CLUSTER_NAME-config
  volumeClaimTemplates:
  - metadata:
      name: rabbitmq-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: $STORAGE_SIZE
      storageClassName: $STORAGE_CLASS
EOF

    print_success "StatefulSet $CLUSTER_NAME 创建完成"
}

# 函数：创建Service
create_service() {
    print_info "创建Service..."
    
    # Headless Service (集群内部通信)
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: $CLUSTER_NAME-headless
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
spec:
  clusterIP: None
  selector:
    app: rabbitmq
    cluster: $CLUSTER_NAME
  ports:
  - name: amqp
    port: 5672
    targetPort: 5672
    protocol: TCP
  - name: management
    port: 15672
    targetPort: 15672
    protocol: TCP
  - name: clustering
    port: 25672
    targetPort: 25672
    protocol: TCP
  - name: metrics
    port: 15692
    targetPort: 15692
    protocol: TCP
EOF

    # ClusterIP Service (外部访问)
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: $CLUSTER_NAME
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
spec:
  selector:
    app: rabbitmq
    cluster: $CLUSTER_NAME
  ports:
  - name: amqp
    port: 5672
    targetPort: 5672
    protocol: TCP
  - name: management
    port: 15672
    targetPort: 15672
    protocol: TCP
  - name: metrics
    port: 15692
    targetPort: 15692
    protocol: TCP
  type: ClusterIP
EOF

    print_success "Service 创建完成"
}

# 函数：创建Ingress
create_ingress() {
    if [ "$INGRESS_ENABLED" = "true" ]; then
        print_info "创建Ingress..."
        
        cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: $CLUSTER_NAME-ingress
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - rabbitmq.$DOMAIN_NAME
    secretName: rabbitmq-tls
  rules:
  - host: rabbitmq.$DOMAIN_NAME
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: $CLUSTER_NAME
            port:
              number: 15672
EOF

        print_success "Ingress 创建完成"
    fi
}

# 函数：创建HPA
create_hpa() {
    if [ "$HPA_ENABLED" = "true" ]; then
        print_info "创建HPA..."
        
        cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: $CLUSTER_NAME-hpa
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: $CLUSTER_NAME
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
EOF

        print_success "HPA 创建完成"
    fi
}

# 函数：创建PodDisruptionBudget
create_pdb() {
    print_info "创建PodDisruptionBudget..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: $CLUSTER_NAME-pdb
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: rabbitmq
      cluster: $CLUSTER_NAME
EOF

    print_success "PodDisruptionBudget 创建完成"
}

# 函数：创建ServiceMonitor
create_servicemonitor() {
    if [ "$MONITORING_ENABLED" = "true" ]; then
        print_info "创建ServiceMonitor..."
        
        cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: $CLUSTER_NAME-metrics
  namespace: $NAMESPACE
  labels:
    app: rabbitmq
    cluster: $CLUSTER_NAME
    monitoring: prometheus
spec:
  selector:
    matchLabels:
      app: rabbitmq
      cluster: $CLUSTER_NAME
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
EOF

        print_success "ServiceMonitor 创建完成"
    fi
}

# 函数：等待部署完成
wait_for_deployment() {
    print_info "等待部署完成..."
    
    # 等待StatefulSet就绪
    kubectl wait --for=condition=ready statefulset/$CLUSTER_NAME -n $NAMESPACE --timeout=600s
    
    # 检查Pod状态
    kubectl get pods -n $NAMESPACE -l app=rabbitmq,cluster=$CLUSTER_NAME
    
    print_success "部署完成"
}

# 函数：检查集群健康状态
check_health() {
    print_info "检查集群健康状态..."
    
    # 检查集群状态
    for i in $(seq 0 $((REPLICAS-1))); do
        POD_NAME="$CLUSTER_NAME-$i"
        print_info "检查Pod $POD_NAME..."
        
        # 检查Pod状态
        if kubectl get pod $POD_NAME -n $NAMESPACE | grep -q "Running"; then
            print_success "Pod $POD_NAME 运行正常"
        else
            print_error "Pod $POD_NAME 状态异常"
            kubectl describe pod $POD_NAME -n $NAMESPACE
        fi
    done
    
    # 检查集群节点
    kubectl exec $CLUSTER_NAME-0 -n $NAMESPACE -- rabbitmqctl cluster_status
    
    print_success "健康检查完成"
}

# 函数：显示访问信息
show_access_info() {
    print_info "RabbitMQ集群访问信息:"
    echo
    echo "  管理界面: http://$CLUSTER_NAME.$NAMESPACE.svc.cluster.local:15672"
    echo "  AMQP连接: amqp://admin:$ADMIN_PASSWORD@$CLUSTER_NAME.$NAMESPACE.svc.cluster.local:5672"
    echo "  集群状态: kubectl exec $CLUSTER_NAME-0 -n $NAMESPACE -- rabbitmqctl cluster_status"
    echo
    echo "配置信息:"
    echo "  命名空间: $NAMESPACE"
    echo "  集群名称: $CLUSTER_NAME"
    echo "  副本数: $REPLICAS"
    echo "  镜像: $IMAGE"
    echo "  存储类: $STORAGE_CLASS"
    echo "  存储大小: $STORAGE_SIZE"
    echo
}

# 清理函数
cleanup() {
    if [ "$CLEANUP" = "true" ]; then
        print_warning "清理部署..."
        kubectl delete namespace $NAMESPACE --ignore-not-found=true
        kubectl delete storageclass $STORAGE_CLASS --ignore-not-found=true
        print_success "清理完成"
    fi
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --cluster-name)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            --replicas)
                REPLICAS="$2"
                shift 2
                ;;
            --image)
                IMAGE="$2"
                shift 2
                ;;
            --storage-class)
                STORAGE_CLASS="$2"
                shift 2
                ;;
            --storage-size)
                STORAGE_SIZE="$2"
                shift 2
                ;;
            --ingress)
                INGRESS_ENABLED="true"
                DOMAIN_NAME="$2"
                shift 2
                ;;
            --hpa)
                HPA_ENABLED="true"
                shift
                ;;
            --monitoring)
                MONITORING_ENABLED="true"
                shift
                ;;
            --cleanup)
                CLEANUP="true"
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --namespace NAMESPACE       命名空间 (默认: rabbitmq-system)"
                echo "  --cluster-name NAME         集群名称 (默认: rabbitmq-cluster)"
                echo "  --replicas COUNT            副本数 (默认: 3)"
                echo "  --image IMAGE               镜像 (默认: rabbitmq:3.10-management-alpine)"
                echo "  --storage-class CLASS       存储类 (默认: rabbitmq-storage)"
                echo "  --storage-size SIZE         存储大小 (默认: 20Gi)"
                echo "  --ingress DOMAIN            启用Ingress并指定域名"
                echo "  --hpa                       启用水平自动扩缩容"
                echo "  --monitoring                启用Prometheus监控"
                echo "  --cleanup                   部署后清理所有资源"
                echo "  --help, -h                  显示此帮助信息"
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    print_info "开始RabbitMQ云原生部署..."
    print_info "配置信息: 命名空间=$NAMESPACE, 集群=$CLUSTER_NAME, 副本=$REPLICAS, 镜像=$IMAGE"
    
    # 检查依赖
    check_dependencies
    
    # 生成安全凭据
    generate_secrets
    
    # 创建所有资源
    create_namespace
    create_storage_class
    create_configmap
    create_secret
    create_serviceaccount
    create_rbac
    create_statefulset
    create_service
    create_ingress
    create_hpa
    create_pdb
    create_servicemonitor
    
    # 等待部署完成
    wait_for_deployment
    
    # 检查健康状态
    check_health
    
    # 显示访问信息
    show_access_info
    
    # 可选清理
    if [ "$CLEANUP" = "true" ]; then
        cleanup
    else
        print_success "RabbitMQ云原生部署完成!"
        print_info "使用以下命令查看集群状态:"
        echo "  kubectl get pods -n $NAMESPACE"
        echo "  kubectl get services -n $NAMESPACE"
        echo "  kubectl get pvc -n $NAMESPACE"
        echo
        print_info "卸载集群:"
        echo "  $0 --cleanup"
    fi
}

# 执行主函数
main "$@"
