#!/bin/bash

# Airflow安全审计脚本
# 用于检查和验证Airflow部署的安全配置

set -e  # 遇到错误时退出

# 配置变量
AIRFLOW_HOME="/opt/airflow"
LOG_FILE="/var/log/airflow/security-audit.log"
KUBE_NAMESPACE="airflow"
KUBE_CONTEXT="production"
REPORT_DIR="/tmp/airflow-security-report-$(date +%Y%m%d-%H%M%S)"

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
    
    commands=("kubectl" "openssl" "curl" "jq" "awk" "sed")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 命令未找到，请安装后重试"
            exit 1
        fi
    done
    
    log_info "所有必要命令检查通过"
}

# 检查Airflow配置安全性
check_airflow_config_security() {
    log_info "检查Airflow配置安全性..."
    
    # 创建输出目录
    mkdir -p $REPORT_DIR/config-checks
    
    # 检查Fernet密钥
    if [ -z "$AIRFLOW__CORE__FERNET_KEY" ] || [ "$AIRFLOW__CORE__FERNET_KEY" = "your_fernet_key_here" ]; then
        log_warn "Fernet密钥未配置或使用默认值"
        echo "Fernet密钥未配置或使用默认值" > $REPORT_DIR/config-checks/fernet-key-warning.txt
    else
        log_info "Fernet密钥已配置"
        echo "FERNET_KEY已正确配置" > $REPORT_DIR/config-checks/fernet-key-ok.txt
    fi
    
    # 检查Executor配置
    if [ "$AIRFLOW__CORE__EXECUTOR" = "LocalExecutor" ] || [ "$AIRFLOW__CORE__EXECUTOR" = "SequentialExecutor" ]; then
        log_warn "使用不安全的Executor: $AIRFLOW__CORE__EXECUTOR"
        echo "使用不安全的Executor: $AIRFLOW__CORE__EXECUTOR" > $REPORT_DIR/config-checks/executor-warning.txt
    else
        log_info "使用安全的Executor: $AIRFLOW__CORE__EXECUTOR"
        echo "使用安全的Executor: $AIRFLOW__CORE__EXECUTOR" > $REPORT_DIR/config-checks/executor-ok.txt
    fi
    
    # 检查Webserver配置
    if [ "$AIRFLOW__WEBSERVER__RBAC" != "True" ]; then
        log_warn "RBAC未启用"
        echo "RBAC未启用" > $REPORT_DIR/config-checks/rbac-warning.txt
    else
        log_info "RBAC已启用"
        echo "RBAC已启用" > $REPORT_DIR/config-checks/rbac-ok.txt
    fi
    
    # 检查认证配置
    if [ "$AIRFLOW__WEBSERVER__AUTHENTICATE" != "True" ]; then
        log_warn "认证未启用"
        echo "认证未启用" > $REPORT_DIR/config-checks/auth-warning.txt
    else
        log_info "认证已启用"
        echo "认证已启用" > $REPORT_DIR/config-checks/auth-ok.txt
    fi
    
    # 检查敏感配置暴露
    if [ -n "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" ] && [[ "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" == *"password="* ]]; then
        log_warn "数据库连接字符串包含明文密码"
        echo "数据库连接字符串包含明文密码" > $REPORT_DIR/config-checks/db-password-warning.txt
    else
        log_info "数据库连接字符串未包含明文密码"
        echo "数据库连接字符串未包含明文密码" > $REPORT_DIR/config-checks/db-password-ok.txt
    fi
    
    log_info "Airflow配置安全性检查完成"
}

# 检查Kubernetes安全配置
check_kubernetes_security() {
    log_info "检查Kubernetes安全配置..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 创建输出目录
    mkdir -p $REPORT_DIR/k8s-checks
    
    # 检查命名空间是否存在
    if ! kubectl get namespace $KUBE_NAMESPACE &> /dev/null; then
        log_error "命名空间 $KUBE_NAMESPACE 不存在"
        echo "命名空间 $KUBE_NAMESPACE 不存在" > $REPORT_DIR/k8s-checks/namespace-error.txt
        return 1
    fi
    
    # 检查RBAC配置
    if kubectl get role -n $KUBE_NAMESPACE &> /dev/null; then
        log_info "发现Role配置"
        kubectl get role -n $KUBE_NAMESPACE -o yaml > $REPORT_DIR/k8s-checks/roles.yaml
    else
        log_warn "未发现Role配置"
        echo "未发现Role配置" > $REPORT_DIR/k8s-checks/roles-warning.txt
    fi
    
    if kubectl get rolebinding -n $KUBE_NAMESPACE &> /dev/null; then
        log_info "发现RoleBinding配置"
        kubectl get rolebinding -n $KUBE_NAMESPACE -o yaml > $REPORT_DIR/k8s-checks/rolebindings.yaml
    else
        log_warn "未发现RoleBinding配置"
        echo "未发现RoleBinding配置" > $REPORT_DIR/k8s-checks/rolebindings-warning.txt
    fi
    
    # 检查网络策略
    if kubectl get networkpolicy -n $KUBE_NAMESPACE &> /dev/null; then
        log_info "发现网络策略"
        kubectl get networkpolicy -n $KUBE_NAMESPACE -o yaml > $REPORT_DIR/k8s-checks/networkpolicies.yaml
    else
        log_warn "未发现网络策略"
        echo "未发现网络策略" > $REPORT_DIR/k8s-checks/networkpolicies-warning.txt
    fi
    
    # 检查Pod安全上下文
    WEB_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=webserver -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$WEB_POD" ]; then
        # 检查是否运行在root用户下
        RUN_AS_USER=$(kubectl get pod $WEB_POD -n $KUBE_NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.runAsUser}' 2>/dev/null || echo "")
        
        if [ -z "$RUN_AS_USER" ] || [ "$RUN_AS_USER" = "0" ]; then
            log_warn "Webserver Pod以root用户运行"
            echo "Webserver Pod以root用户运行" > $REPORT_DIR/k8s-checks/webserver-root-warning.txt
        else
            log_info "Webserver Pod以非root用户运行"
            echo "Webserver Pod以非root用户运行 (UID: $RUN_AS_USER)" > $REPORT_DIR/k8s-checks/webserver-root-ok.txt
        fi
        
        # 检查是否允许特权模式
        PRIVILEGED=$(kubectl get pod $WEB_POD -n $KUBE_NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.privileged}' 2>/dev/null || echo "")
        
        if [ "$PRIVILEGED" = "true" ]; then
            log_warn "Webserver Pod允许特权模式"
            echo "Webserver Pod允许特权模式" > $REPORT_DIR/k8s-checks/webserver-privileged-warning.txt
        else
            log_info "Webserver Pod不允许特权模式"
            echo "Webserver Pod不允许特权模式" > $REPORT_DIR/k8s-checks/webserver-privileged-ok.txt
        fi
    else
        log_warn "未找到Webserver Pod"
        echo "未找到Webserver Pod" > $REPORT_DIR/k8s-checks/webserver-not-found.txt
    fi
    
    log_info "Kubernetes安全配置检查完成"
}

# 检查SSL/TLS配置
check_ssl_tls() {
    log_info "检查SSL/TLS配置..."
    
    # 创建输出目录
    mkdir -p $REPORT_DIR/ssl-checks
    
    # 检查Webserver是否使用HTTPS
    if [ -n "$AIRFLOW__WEBSERVER__WEB_SERVER_SSL_CERT" ] && [ -n "$AIRFLOW__WEBSERVER__WEB_SERVER_SSL_KEY" ]; then
        log_info "Webserver配置了SSL证书"
        echo "Webserver配置了SSL证书" > $REPORT_DIR/ssl-checks/webserver-ssl-ok.txt
        
        # 检查证书有效性
        if [ -f "$AIRFLOW__WEBSERVER__WEB_SERVER_SSL_CERT" ]; then
            openssl x509 -in "$AIRFLOW__WEBSERVER__WEB_SERVER_SSL_CERT" -text -noout > $REPORT_DIR/ssl-checks/webserver-cert-details.txt
            log_info "Webserver证书详情已保存"
        fi
    else
        log_warn "Webserver未配置SSL证书"
        echo "Webserver未配置SSL证书" > $REPORT_DIR/ssl-checks/webserver-ssl-warning.txt
    fi
    
    # 检查数据库SSL连接
    if [[ "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" == *"sslmode=require"* ]] || [[ "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" == *"sslmode=verify-full"* ]]; then
        log_info "数据库连接使用SSL"
        echo "数据库连接使用SSL" > $REPORT_DIR/ssl-checks/database-ssl-ok.txt
    else
        log_warn "数据库连接未使用SSL"
        echo "数据库连接未使用SSL" > $REPORT_DIR/ssl-checks/database-ssl-warning.txt
    fi
    
    log_info "SSL/TLS配置检查完成"
}

# 检查密钥管理
check_secret_management() {
    log_info "检查密钥管理..."
    
    # 创建输出目录
    mkdir -p $REPORT_DIR/secret-checks
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 检查Secret是否存在
    if kubectl get secret -n $KUBE_NAMESPACE &> /dev/null; then
        log_info "发现Secret资源"
        kubectl get secret -n $KUBE_NAMESPACE -o yaml > $REPORT_DIR/secret-checks/secrets.yaml
        
        # 检查是否有敏感信息以明文形式存储
        SECRET_COUNT=$(kubectl get secret -n $KUBE_NAMESPACE --no-headers | wc -l)
        log_info "发现 $SECRET_COUNT 个Secret"
        echo "发现 $SECRET_COUNT 个Secret" > $REPORT_DIR/secret-checks/secret-count.txt
    else
        log_warn "未发现Secret资源"
        echo "未发现Secret资源" > $REPORT_DIR/secret-checks/secrets-warning.txt
    fi
    
    log_info "密钥管理检查完成"
}

# 检查日志和审计配置
check_logging_audit() {
    log_info "检查日志和审计配置..."
    
    # 创建输出目录
    mkdir -p $REPORT_DIR/logging-checks
    
    # 检查日志级别
    if [ -n "$AIRFLOW__LOGGING__LOGGING_LEVEL" ]; then
        log_info "日志级别设置为: $AIRFLOW__LOGGING__LOGGING_LEVEL"
        echo "日志级别设置为: $AIRFLOW__LOGGING__LOGGING_LEVEL" > $REPORT_DIR/logging-checks/log-level.txt
    else
        log_warn "日志级别未明确设置"
        echo "日志级别未明确设置" > $REPORT_DIR/logging-checks/log-level-warning.txt
    fi
    
    # 检查审计日志配置
    if [ -n "$AIRFLOW__LOGGING__AUDIT_LOG" ] && [ "$AIRFLOW__LOGGING__AUDIT_LOG" = "True" ]; then
        log_info "审计日志已启用"
        echo "审计日志已启用" > $REPORT_DIR/logging-checks/audit-log-ok.txt
    else
        log_warn "审计日志未启用"
        echo "审计日志未启用" > $REPORT_DIR/logging-checks/audit-log-warning.txt
    fi
    
    log_info "日志和审计配置检查完成"
}

# 生成安全报告
generate_security_report() {
    log_info "生成安全报告..."
    
    # 创建报告目录
    mkdir -p $REPORT_DIR
    
    # 生成汇总报告
    cat > $REPORT_DIR/summary.txt << EOF
Airflow安全审计报告
生成时间: $(date)
审计范围: Airflow配置、Kubernetes安全、SSL/TLS、密钥管理、日志审计

主要发现:
1. 配置安全性:
   - Fernet密钥: $(if [ -f "$REPORT_DIR/config-checks/fernet-key-ok.txt" ]; then echo "已配置"; else echo "未配置"; fi)
   - Executor: $(if [ -f "$REPORT_DIR/config-checks/executor-ok.txt" ]; then echo "安全"; else echo "不安全"; fi)
   - RBAC: $(if [ -f "$REPORT_DIR/config-checks/rbac-ok.txt" ]; then echo "已启用"; else echo "未启用"; fi)
   - 认证: $(if [ -f "$REPORT_DIR/config-checks/auth-ok.txt" ]; then echo "已启用"; else echo "未启用"; fi)

2. Kubernetes安全性:
   - Role配置: $(if [ -f "$REPORT_DIR/k8s-checks/roles.yaml" ]; then echo "已配置"; else echo "未配置"; fi)
   - 网络策略: $(if [ -f "$REPORT_DIR/k8s-checks/networkpolicies.yaml" ]; then echo "已配置"; else echo "未配置"; fi)
   - Pod安全上下文: $(if [ -f "$REPORT_DIR/k8s-checks/webserver-root-ok.txt" ]; then echo "安全"; else echo "不安全"; fi)

3. SSL/TLS配置:
   - Webserver SSL: $(if [ -f "$REPORT_DIR/ssl-checks/webserver-ssl-ok.txt" ]; then echo "已配置"; else echo "未配置"; fi)
   - 数据库SSL: $(if [ -f "$REPORT_DIR/ssl-checks/database-ssl-ok.txt" ]; then echo "已配置"; else echo "未配置"; fi)

4. 密钥管理:
   - Secret数量: $(if [ -f "$REPORT_DIR/secret-checks/secret-count.txt" ]; then cat $REPORT_DIR/secret-checks/secret-count.txt | awk '{print $2}'; else echo "0"; fi)

5. 日志和审计:
   - 日志级别: $(if [ -f "$REPORT_DIR/logging-checks/log-level.txt" ]; then cat $REPORT_DIR/logging-checks/log-level.txt | cut -d' ' -f4; else echo "默认"; fi)
   - 审计日志: $(if [ -f "$REPORT_DIR/logging-checks/audit-log-ok.txt" ]; then echo "已启用"; else echo "未启用"; fi)
EOF
    
    # 压缩报告
    tar -czf $REPORT_DIR.tar.gz -C /tmp airflow-security-report-$(date +%Y%m%d-%H%M%S)
    
    log_info "安全报告生成完成: $REPORT_DIR.tar.gz"
}

# 应用安全加固建议
apply_security_hardening() {
    log_info "应用安全加固建议..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 应用网络策略
    cat > $REPORT_DIR/network-policy.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-deny-all
  namespace: airflow
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-allow-web-ingress
  namespace: airflow
spec:
  podSelector:
    matchLabels:
      component: webserver
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-allow-egress-dns
  namespace: airflow
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
EOF
    
    kubectl apply -f $REPORT_DIR/network-policy.yaml -n $KUBE_NAMESPACE
    
    # 应用Pod安全策略
    kubectl patch deployment airflow-webserver -n $KUBE_NAMESPACE -p='{"spec":{"template":{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":1000,"fsGroup":2000},"containers":[{"name":"webserver","securityContext":{"allowPrivilegeEscalation":false,"readOnlyRootFilesystem":true}}]}}}}'
    
    kubectl patch deployment airflow-scheduler -n $KUBE_NAMESPACE -p='{"spec":{"template":{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":1000,"fsGroup":2000},"containers":[{"name":"scheduler","securityContext":{"allowPrivilegeEscalation":false,"readOnlyRootFilesystem":true}}]}}}}'
    
    log_info "安全加固建议应用完成"
}

# 主安全审计函数
perform_security_audit() {
    log_info "开始执行安全审计..."
    
    check_dependencies
    check_airflow_config_security
    check_kubernetes_security
    check_ssl_tls
    check_secret_management
    check_logging_audit
    generate_security_report
    
    log_info "安全审计执行完成"
}

# 显示帮助信息
show_help() {
    echo "Airflow安全审计脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  audit              执行完整安全审计"
    echo "  harden             应用安全加固建议"
    echo "  report             生成安全报告"
    echo "  help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 audit"
    echo "  $0 harden"
    echo "  $0 report"
}

# 主函数
main() {
    case "$1" in
        audit)
            perform_security_audit
            ;;
        harden)
            apply_security_hardening
            ;;
        report)
            generate_security_report
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