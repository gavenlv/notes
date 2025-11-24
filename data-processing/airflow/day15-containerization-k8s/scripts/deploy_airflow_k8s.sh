#!/bin/bash

# Airflow Kubernetes部署脚本
# 用于在Kubernetes集群上部署和管理Airflow

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# 检查必要命令
check_prerequisites() {
    log "检查必要命令..."
    
    commands=("kubectl" "helm" "docker")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "$cmd 未安装，请先安装 $cmd"
            exit 1
        fi
    done
    
    log "所有必要命令检查通过"
}

# 检查Kubernetes集群连接
check_k8s_connection() {
    log "检查Kubernetes集群连接..."
    
    if ! kubectl cluster-info &> /dev/null; then
        error "无法连接到Kubernetes集群，请检查kubectl配置"
        exit 1
    fi
    
    log "Kubernetes集群连接正常"
    kubectl cluster-info
}

# 创建命名空间
create_namespace() {
    local namespace=$1
    log "创建命名空间: $namespace"
    
    if kubectl get namespace "$namespace" &> /dev/null; then
        warn "命名空间 $namespace 已存在"
    else
        kubectl create namespace "$namespace"
        log "命名空间 $namespace 创建成功"
    fi
}

# 构建自定义Airflow镜像
build_airflow_image() {
    local image_name=$1
    local tag=$2
    local dockerfile_path=$3
    
    log "构建自定义Airflow镜像: $image_name:$tag"
    
    if [ ! -f "$dockerfile_path" ]; then
        error "Dockerfile 不存在: $dockerfile_path"
        exit 1
    fi
    
    docker build -t "$image_name:$tag" -f "$dockerfile_path" .
    
    log "Airflow镜像构建完成: $image_name:$tag"
}

# 推送镜像到仓库
push_image() {
    local image_name=$1
    local tag=$2
    local registry=$3
    
    log "推送镜像到仓库: $registry"
    
    # 重新标记镜像
    docker tag "$image_name:$tag" "$registry/$image_name:$tag"
    
    # 推送镜像
    docker push "$registry/$image_name:$tag"
    
    log "镜像推送完成: $registry/$image_name:$tag"
}

# 使用Helm部署Airflow
deploy_with_helm() {
    local release_name=$1
    local namespace=$2
    local chart_path=$3
    local values_file=$4
    
    log "使用Helm部署Airflow..."
    
    # 添加Apache Airflow Helm仓库
    helm repo add apache-airflow https://airflow.apache.org/
    helm repo update
    
    # 部署或升级Airflow
    if helm list -n "$namespace" | grep -q "^$release_name "; then
        log "升级现有的Airflow部署..."
        helm upgrade "$release_name" "$chart_path" \
            --namespace "$namespace" \
            --values "$values_file" \
            --timeout 15m \
            --atomic
    else
        log "首次部署Airflow..."
        helm install "$release_name" "$chart_path" \
            --namespace "$namespace" \
            --values "$values_file" \
            --timeout 15m \
            --atomic
    fi
    
    log "Airflow部署完成"
}

# 等待Pod就绪
wait_for_pods() {
    local namespace=$1
    local timeout=${2:-300}  # 默认5分钟超时
    
    log "等待Pod就绪 (超时: ${timeout}秒)..."
    
    # 等待所有Pod运行
    kubectl wait --for=condition=Ready pods --all --namespace "$namespace" --timeout="${timeout}s" || {
        error "Pod未在指定时间内就绪"
        kubectl get pods --namespace "$namespace"
        exit 1
    }
    
    log "所有Pod已就绪"
}

# 验证部署
verify_deployment() {
    local namespace=$1
    local release_name=$2
    
    log "验证部署..."
    
    # 检查Pod状态
    log "检查Pod状态:"
    kubectl get pods --namespace "$namespace"
    
    # 检查服务状态
    log "检查服务状态:"
    kubectl get services --namespace "$namespace"
    
    # 检查Helm发布状态
    log "检查Helm发布状态:"
    helm status "$release_name" --namespace "$namespace"
    
    log "部署验证完成"
}

# 获取访问信息
get_access_info() {
    local namespace=$1
    
    log "获取访问信息..."
    
    echo "=================== 访问信息 ==================="
    echo "Airflow Webserver:"
    kubectl get svc --namespace "$namespace" | grep webserver
    echo ""
    
    echo "Airflow Flower (Celery监控):"
    kubectl get svc --namespace "$namespace" | grep flower
    echo ""
    
    echo "获取Airflow Webserver端口转发命令:"
    echo "kubectl port-forward svc/airflow-webserver 8080:8080 --namespace $namespace"
    echo ""
    
    echo "获取Pod日志命令:"
    echo "kubectl logs -f deployment/airflow-webserver --namespace $namespace"
    echo "================================================"
}

# 清理资源
cleanup() {
    local namespace=$1
    local release_name=$2
    
    log "清理Airflow部署..."
    
    # 卸载Helm发布
    if helm list -n "$namespace" | grep -q "^$release_name "; then
        helm uninstall "$release_name" --namespace "$namespace"
        log "Helm发布 $release_name 已卸载"
    fi
    
    # 删除命名空间（可选）
    read -p "是否删除命名空间 $namespace? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace "$namespace"
        log "命名空间 $namespace 已删除"
    fi
    
    log "清理完成"
}

# 显示使用方法
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "选项:"
    echo "  deploy    部署Airflow到Kubernetes"
    echo "  cleanup   清理Airflow部署"
    echo "  verify    验证当前部署"
    echo "  help      显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  NAMESPACE         Kubernetes命名空间 (默认: airflow)"
    echo "  RELEASE_NAME      Helm发布名称 (默认: airflow)"
    echo "  REGISTRY          Docker镜像仓库 (默认: docker.io)"
    echo "  IMAGE_NAME        Docker镜像名称 (默认: custom-airflow)"
    echo "  TAG               Docker镜像标签 (默认: latest)"
    echo ""
    echo "示例:"
    echo "  $0 deploy"
    echo "  NAMESPACE=production RELEASE_NAME=airflow-prod $0 deploy"
}

# 主部署函数
main_deploy() {
    # 设置默认值
    local namespace=${NAMESPACE:-airflow}
    local release_name=${RELEASE_NAME:-airflow}
    local registry=${REGISTRY:-docker.io}
    local image_name=${IMAGE_NAME:-custom-airflow}
    local tag=${TAG:-latest}
    local chart_path="apache-airflow/airflow"
    local values_file="./helm-values.yaml"
    
    log "开始部署Airflow到Kubernetes"
    log "配置信息:"
    log "  命名空间: $namespace"
    log "  发布名称: $release_name"
    log "  镜像仓库: $registry"
    log "  镜像名称: $image_name:$tag"
    
    # 检查前提条件
    check_prerequisites
    check_k8s_connection
    
    # 创建命名空间
    create_namespace "$namespace"
    
    # 如果提供了Dockerfile，则构建和推送镜像
    if [ -f "./Dockerfile" ]; then
        build_airflow_image "$image_name" "$tag" "./Dockerfile"
        push_image "$image_name" "$tag" "$registry"
    else
        warn "未找到Dockerfile，将使用默认Airflow镜像"
    fi
    
    # 使用Helm部署
    deploy_with_helm "$release_name" "$namespace" "$chart_path" "$values_file"
    
    # 等待Pod就绪
    wait_for_pods "$namespace"
    
    # 验证部署
    verify_deployment "$namespace" "$release_name"
    
    # 获取访问信息
    get_access_info "$namespace"
    
    log "Airflow Kubernetes部署完成！"
}

# 主函数
main() {
    case "${1:-help}" in
        deploy)
            main_deploy
            ;;
        cleanup)
            local namespace=${NAMESPACE:-airflow}
            local release_name=${RELEASE_NAME:-airflow}
            cleanup "$namespace" "$release_name"
            ;;
        verify)
            local namespace=${NAMESPACE:-airflow}
            local release_name=${RELEASE_NAME:-airflow}
            verify_deployment "$namespace" "$release_name"
            get_access_info "$namespace"
            ;;
        help)
            usage
            ;;
        *)
            error "未知命令: $1"
            usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"