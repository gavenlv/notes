#!/bin/bash

# Airflow监控告警脚本
# 用于监控Airflow组件健康状况并发送告警

set -e  # 遇到错误时退出

# 配置变量
AIRFLOW_HOME="/opt/airflow"
LOG_FILE="/var/log/airflow/monitoring-alerting.log"
KUBE_NAMESPACE="airflow"
KUBE_CONTEXT="production"
PROMETHEUS_URL="http://prometheus-server.monitoring.svc.cluster.local:9090"
ALERTMANAGER_URL="http://alertmanager.monitoring.svc.cluster.local:9093"
SLACK_WEBHOOK_URL=""
EMAIL_TO=""
REPORT_DIR="/tmp/airflow-monitoring-report-$(date +%Y%m%d-%H%M%S)"

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
    
    commands=("kubectl" "curl" "jq" "awk" "sed" "bc")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 命令未找到，请安装后重试"
            exit 1
        fi
    done
    
    log_info "所有必要命令检查通过"
}

# 检查Airflow Webserver健康状态
check_webserver_health() {
    log_info "检查Airflow Webserver健康状态..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 获取Webserver Pod
    WEB_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=webserver -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$WEB_POD" ]; then
        log_error "未找到Airflow Webserver Pod"
        echo "未找到Airflow Webserver Pod" > $REPORT_DIR/webserver-health-error.txt
        return 1
    fi
    
    # 检查Pod状态
    POD_STATUS=$(kubectl get pod $WEB_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
    
    if [ "$POD_STATUS" != "Running" ]; then
        log_error "Webserver Pod状态异常: $POD_STATUS"
        echo "Webserver Pod状态异常: $POD_STATUS" > $REPORT_DIR/webserver-health-error.txt
        send_alert "Airflow Webserver Pod状态异常: $POD_STATUS"
        return 1
    fi
    
    # 检查就绪探针
    READINESS_STATUS=$(kubectl get pod $WEB_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
    
    if [ "$READINESS_STATUS" != "True" ]; then
        log_error "Webserver Pod未就绪"
        echo "Webserver Pod未就绪" > $REPORT_DIR/webserver-readiness-error.txt
        send_alert "Airflow Webserver Pod未就绪"
        return 1
    fi
    
    # 检查Webserver响应
    WEB_SERVICE=$(kubectl get service airflow-webserver -n $KUBE_NAMESPACE -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
    
    if [ -n "$WEB_SERVICE" ]; then
        # 在Scheduler Pod中测试Webserver连接
        SCHED_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=scheduler -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
        
        if [ -n "$SCHED_POD" ]; then
            if kubectl exec -n $KUBE_NAMESPACE $SCHED_POD -- curl -s -o /dev/null -w "%{http_code}" http://$WEB_SERVICE:8080/health 2>/dev/null | grep -q "200"; then
                log_info "Webserver健康检查通过"
                echo "Webserver健康检查通过" > $REPORT_DIR/webserver-health-ok.txt
            else
                log_error "Webserver健康检查失败"
                echo "Webserver健康检查失败" > $REPORT_DIR/webserver-health-failed.txt
                send_alert "Airflow Webserver健康检查失败"
                return 1
            fi
        fi
    fi
    
    log_info "Airflow Webserver健康状态检查完成"
}

# 检查Airflow Scheduler健康状态
check_scheduler_health() {
    log_info "检查Airflow Scheduler健康状态..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 获取Scheduler Pod
    SCHED_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=scheduler -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$SCHED_POD" ]; then
        log_error "未找到Airflow Scheduler Pod"
        echo "未找到Airflow Scheduler Pod" > $REPORT_DIR/scheduler-health-error.txt
        send_alert "未找到Airflow Scheduler Pod"
        return 1
    fi
    
    # 检查Pod状态
    POD_STATUS=$(kubectl get pod $SCHED_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
    
    if [ "$POD_STATUS" != "Running" ]; then
        log_error "Scheduler Pod状态异常: $POD_STATUS"
        echo "Scheduler Pod状态异常: $POD_STATUS" > $REPORT_DIR/scheduler-health-error.txt
        send_alert "Airflow Scheduler Pod状态异常: $POD_STATUS"
        return 1
    fi
    
    # 检查就绪探针
    READINESS_STATUS=$(kubectl get pod $SCHED_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
    
    if [ "$READINESS_STATUS" != "True" ]; then
        log_error "Scheduler Pod未就绪"
        echo "Scheduler Pod未就绪" > $REPORT_DIR/scheduler-readiness-error.txt
        send_alert "Airflow Scheduler Pod未就绪"
        return 1
    fi
    
    # 检查最近的心跳
    LAST_HEARTBEAT=$(kubectl logs $SCHED_POD -n $KUBE_NAMESPACE --tail=50 | grep "heartbeat" | tail -1 | awk '{print $1" "$2}' 2>/dev/null || echo "")
    
    if [ -n "$LAST_HEARTBEAT" ]; then
        # 解析心跳时间并检查是否在合理范围内（5分钟内）
        HEARTBEAT_TS=$(date -d "$LAST_HEARTBEAT" +%s 2>/dev/null || echo "0")
        CURRENT_TS=$(date +%s)
        TIME_DIFF=$((CURRENT_TS - HEARTBEAT_TS))
        
        if [ $TIME_DIFF -gt 300 ]; then
            log_error "Scheduler心跳超时 ($TIME_DIFF 秒前)"
            echo "Scheduler心跳超时 ($TIME_DIFF 秒前)" > $REPORT_DIR/scheduler-heartbeat-timeout.txt
            send_alert "Airflow Scheduler心跳超时 ($TIME_DIFF 秒前)"
            return 1
        else
            log_info "Scheduler心跳正常 ($TIME_DIFF 秒前)"
            echo "Scheduler心跳正常 ($TIME_DIFF 秒前)" > $REPORT_DIR/scheduler-heartbeat-ok.txt
        fi
    else
        log_warn "无法确定Scheduler心跳状态"
        echo "无法确定Scheduler心跳状态" > $REPORT_DIR/scheduler-heartbeat-unknown.txt
    fi
    
    log_info "Airflow Scheduler健康状态检查完成"
}

# 检查Airflow Worker健康状态
check_worker_health() {
    log_info "检查Airflow Worker健康状态..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 获取Worker Pods
    WORKER_PODS=$(kubectl get pods -n $KUBE_NAMESPACE -l component=worker -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$WORKER_PODS" ]; then
        log_warn "未找到Airflow Worker Pods"
        echo "未找到Airflow Worker Pods" > $REPORT_DIR/worker-health-warning.txt
        return 0
    fi
    
    # 检查每个Worker Pod的状态
    for WORKER_POD in $WORKER_PODS; do
        POD_STATUS=$(kubectl get pod $WORKER_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
        
        if [ "$POD_STATUS" != "Running" ]; then
            log_error "Worker Pod $WORKER_POD 状态异常: $POD_STATUS"
            echo "Worker Pod $WORKER_POD 状态异常: $POD_STATUS" > $REPORT_DIR/worker-$WORKER_POD-health-error.txt
            send_alert "Airflow Worker Pod $WORKER_POD 状态异常: $POD_STATUS"
            continue
        fi
        
        # 检查就绪探针
        READINESS_STATUS=$(kubectl get pod $WORKER_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
        
        if [ "$READINESS_STATUS" != "True" ]; then
            log_error "Worker Pod $WORKER_POD 未就绪"
            echo "Worker Pod $WORKER_POD 未就绪" > $REPORT_DIR/worker-$WORKER_POD-readiness-error.txt
            send_alert "Airflow Worker Pod $WORKER_POD 未就绪"
            continue
        fi
        
        log_info "Worker Pod $WORKER_POD 健康检查通过"
        echo "Worker Pod $WORKER_POD 健康检查通过" > $REPORT_DIR/worker-$WORKER_POD-health-ok.txt
    done
    
    log_info "Airflow Worker健康状态检查完成"
}

# 检查数据库连接
check_database_connection() {
    log_info "检查数据库连接..."
    
    # 从环境变量获取数据库连接信息
    DB_HOST=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN#*://}
    DB_USER=${DB_HOST%@*}
    DB_HOST=${DB_HOST#*@}
    DB_NAME=${DB_HOST#*/} 
    DB_HOST=${DB_HOST%/*}
    DB_PORT=${DB_HOST#*:}
    if [ "$DB_HOST" = "$DB_PORT" ]; then
        DB_PORT="5432"
    fi
    
    # 测试数据库连接
    if timeout 10 bash -c "</dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
        log_info "数据库连接正常"
        echo "数据库连接正常" > $REPORT_DIR/database-connection-ok.txt
    else
        log_error "数据库连接失败"
        echo "数据库连接失败" > $REPORT_DIR/database-connection-error.txt
        send_alert "Airflow数据库连接失败"
        return 1
    fi
    
    log_info "数据库连接检查完成"
}

# 检查Redis连接（如果使用CeleryExecutor）
check_redis_connection() {
    log_info "检查Redis连接..."
    
    # 检查是否使用CeleryExecutor
    if [ "$AIRFLOW__CORE__EXECUTOR" != "CeleryExecutor" ]; then
        log_info "未使用CeleryExecutor，跳过Redis连接检查"
        echo "未使用CeleryExecutor，跳过Redis连接检查" > $REPORT_DIR/redis-check-skipped.txt
        return 0
    fi
    
    # 从环境变量获取Redis连接信息
    REDIS_URL=${AIRFLOW__CELERY__BROKER_URL}
    REDIS_HOST=${REDIS_URL#*://}
    REDIS_HOST=${REDIS_HOST%:*}
    REDIS_PORT=${REDIS_URL#*://}
    REDIS_PORT=${REDIS_PORT#*:}
    
    # 测试Redis连接
    if timeout 10 bash -c "</dev/tcp/$REDIS_HOST/$REDIS_PORT" 2>/dev/null; then
        log_info "Redis连接正常"
        echo "Redis连接正常" > $REPORT_DIR/redis-connection-ok.txt
    else
        log_error "Redis连接失败"
        echo "Redis连接失败" > $REPORT_DIR/redis-connection-error.txt
        send_alert "Airflow Redis连接失败"
        return 1
    fi
    
    log_info "Redis连接检查完成"
}

# 查询Prometheus指标
query_prometheus() {
    local query=$1
    local output_file=$2
    
    log_debug "查询Prometheus指标: $query"
    
    # 构造Prometheus API查询URL
    ENCODED_QUERY=$(echo "$query" | sed 's/ /%20/g' | sed 's/\[/\\[/g' | sed 's/\]/\\]/g')
    API_URL="$PROMETHEUS_URL/api/v1/query?query=$ENCODED_QUERY"
    
    # 查询并保存结果
    if curl -s -m 30 "$API_URL" > "$output_file"; then
        log_debug "Prometheus查询成功"
        return 0
    else
        log_error "Prometheus查询失败: $API_URL"
        return 1
    fi
}

# 检查关键指标
check_critical_metrics() {
    log_info "检查关键指标..."
    
    # 创建输出目录
    mkdir -p $REPORT_DIR/metrics
    
    # 检查任务失败率
    query_prometheus 'rate(airflow_task_failures_total[5m])' $REPORT_DIR/metrics/task-failures.json
    
    if [ -f $REPORT_DIR/metrics/task-failures.json ]; then
        FAILURE_RATE=$(jq -r '.data.result[].value[1]' $REPORT_DIR/metrics/task-failures.json 2>/dev/null || echo "0")
        
        # 如果失败率大于阈值（例如0.1），发送告警
        if (( $(echo "$FAILURE_RATE > 0.1" | bc -l) )); then
            log_error "任务失败率过高: $FAILURE_RATE"
            echo "任务失败率过高: $FAILURE_RATE" > $REPORT_DIR/metrics/high-failure-rate.txt
            send_alert "Airflow任务失败率过高: $FAILURE_RATE"
        else
            log_info "任务失败率正常: $FAILURE_RATE"
            echo "任务失败率正常: $FAILURE_RATE" > $REPORT_DIR/metrics/failure-rate-normal.txt
        fi
    fi
    
    # 检查调度延迟
    query_prometheus 'airflow_dag_run_schedule_delay_seconds' $REPORT_DIR/metrics/schedule-delay.json
    
    if [ -f $REPORT_DIR/metrics/schedule-delay.json ]; then
        SCHEDULE_DELAY=$(jq -r '.data.result[].value[1]' $REPORT_DIR/metrics/schedule-delay.json 2>/dev/null || echo "0")
        
        # 如果调度延迟大于阈值（例如300秒），发送告警
        if (( $(echo "$SCHEDULE_DELAY > 300" | bc -l) )); then
            log_error "调度延迟过高: ${SCHEDULE_DELAY}秒"
            echo "调度延迟过高: ${SCHEDULE_DELAY}秒" > $REPORT_DIR/metrics/high-schedule-delay.txt
            send_alert "Airflow调度延迟过高: ${SCHEDULE_DELAY}秒"
        else
            log_info "调度延迟正常: ${SCHEDULE_DELAY}秒"
            echo "调度延迟正常: ${SCHEDULE_DELAY}秒" > $REPORT_DIR/metrics/schedule-delay-normal.txt
        fi
    fi
    
    # 检查Pod资源使用情况
    query_prometheus 'rate(container_cpu_usage_seconds_total{namespace="airflow"}[5m])' $REPORT_DIR/metrics/cpu-usage.json
    
    if [ -f $REPORT_DIR/metrics/cpu-usage.json ]; then
        HIGH_CPU_USAGE=$(jq -r '.data.result[] | select(.value[1] |tonumber > 0.8) | .metric.pod' $REPORT_DIR/metrics/cpu-usage.json 2>/dev/null || echo "")
        
        if [ -n "$HIGH_CPU_USAGE" ]; then
            log_warn "以下Pod CPU使用率超过80%: $HIGH_CPU_USAGE"
            echo "以下Pod CPU使用率超过80%: $HIGH_CPU_USAGE" > $REPORT_DIR/metrics/high-cpu-usage.txt
            send_alert "Airflow以下Pod CPU使用率超过80%: $HIGH_CPU_USAGE"
        else
            log_info "所有Pod CPU使用率正常"
            echo "所有Pod CPU使用率正常" > $REPORT_DIR/metrics/cpu-usage-normal.txt
        fi
    fi
    
    log_info "关键指标检查完成"
}

# 发送告警
send_alert() {
    local message=$1
    
    log_warn "发送告警: $message"
    
    # 发送到Slack（如果有配置）
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"Airflow监控告警: $message\"}" \
             $SLACK_WEBHOOK_URL 2>/dev/null || log_error "发送Slack告警失败"
    fi
    
    # 发送邮件（如果有配置）
    if [ -n "$EMAIL_TO" ]; then
        echo "Airflow监控告警: $message" | mail -s "Airflow监控告警" $EMAIL_TO 2>/dev/null || log_error "发送邮件告警失败"
    fi
    
    # 发送到Alertmanager
    ALERT_JSON=$(cat <<EOF
{
  "status": "firing",
  "labels": {
    "alertname": "AirflowHealthCheck",
    "service": "airflow",
    "severity":"page"
  },
  "annotations": {
    "summary": "Airflow health check failed",
    "description": "$message"
  },
  "generatorURL": "http://airflow-monitoring"
}
EOF
)
    
    curl -X POST -H "Content-Type: application/json" \
         -d "[$ALERT_JSON]" \
         $ALERTMANAGER_URL/api/v1/alerts 2>/dev/null || log_error "发送Alertmanager告警失败"
}

# 生成监控报告
generate_monitoring_report() {
    log_info "生成监控报告..."
    
    # 创建报告目录
    mkdir -p $REPORT_DIR
    
    # 生成汇总报告
    cat > $REPORT_DIR/summary.txt << EOF
Airflow监控报告
生成时间: $(date)
监控范围: Webserver、Scheduler、Worker、数据库、Redis、关键指标

健康状态:
1. Webserver: $(if [ -f "$REPORT_DIR/webserver-health-ok.txt" ]; then echo "健康"; elif [ -f "$REPORT_DIR/webserver-health-error.txt" ]; then echo "异常"; else echo "未知"; fi)
2. Scheduler: $(if [ -f "$REPORT_DIR/scheduler-heartbeat-ok.txt" ]; then echo "健康"; elif [ -f "$REPORT_DIR/scheduler-health-error.txt" ]; then echo "异常"; else echo "未知"; fi)
3. Worker: $(if ls $REPORT_DIR/worker-*-health-ok.txt 1> /dev/null 2>&1; then echo "健康"; elif ls $REPORT_DIR/worker-*-health-error.txt 1> /dev/null 2>&1; then echo "异常"; else echo "无或未知"; fi)
4. 数据库: $(if [ -f "$REPORT_DIR/database-connection-ok.txt" ]; then echo "连接正常"; else echo "连接异常"; fi)
5. Redis: $(if [ -f "$REPORT_DIR/redis-connection-ok.txt" ]; then echo "连接正常"; elif [ -f "$REPORT_DIR/redis-check-skipped.txt" ]; then echo "跳过检查"; else echo "连接异常"; fi)

关键指标:
1. 任务失败率: $(if [ -f "$REPORT_DIR/metrics/failure-rate-normal.txt" ]; then cat $REPORT_DIR/metrics/failure-rate-normal.txt; elif [ -f "$REPORT_DIR/metrics/high-failure-rate.txt" ]; then cat $REPORT_DIR/metrics/high-failure-rate.txt; else echo "未知"; fi)
2. 调度延迟: $(if [ -f "$REPORT_DIR/metrics/schedule-delay-normal.txt" ]; then cat $REPORT_DIR/metrics/schedule-delay-normal.txt; elif [ -f "$REPORT_DIR/metrics/high-schedule-delay.txt" ]; then cat $REPORT_DIR/metrics/high-schedule-delay.txt; else echo "未知"; fi)
3. CPU使用率: $(if [ -f "$REPORT_DIR/metrics/cpu-usage-normal.txt" ]; then echo "正常"; elif [ -f "$REPORT_DIR/metrics/high-cpu-usage.txt" ]; then echo "过高"; else echo "未知"; fi)
EOF
    
    # 压缩报告
    tar -czf $REPORT_DIR.tar.gz -C /tmp airflow-monitoring-report-$(date +%Y%m%d-%H%M%S)
    
    log_info "监控报告生成完成: $REPORT_DIR.tar.gz"
}

# 自动修复常见问题
auto_repair() {
    log_info "尝试自动修复常见问题..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 重启不健康的Pod
    WEB_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=webserver -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$WEB_POD" ]; then
        POD_STATUS=$(kubectl get pod $WEB_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
        READINESS_STATUS=$(kubectl get pod $WEB_POD -n $KUBE_NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
        
        if [ "$POD_STATUS" != "Running" ] || [ "$READINESS_STATUS" != "True" ]; then
            log_info "重启不健康的Webserver Pod: $WEB_POD"
            kubectl delete pod $WEB_POD -n $KUBE_NAMESPACE
            
            # 等待新Pod启动
            sleep 30
            
            # 检查新Pod状态
            NEW_WEB_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=webserver -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
            if [ -n "$NEW_WEB_POD" ] && [ "$NEW_WEB_POD" != "$WEB_POD" ]; then
                log_info "Webserver Pod重启成功"
                send_alert "Airflow Webserver Pod已自动重启"
            else
                log_error "Webserver Pod重启失败"
                send_alert "Airflow Webserver Pod重启失败"
            fi
        fi
    fi
    
    log_info "自动修复尝试完成"
}

# 主监控函数
perform_monitoring() {
    log_info "开始执行监控检查..."
    
    check_dependencies
    check_webserver_health
    check_scheduler_health
    check_worker_health
    check_database_connection
    check_redis_connection
    check_critical_metrics
    generate_monitoring_report
    
    log_info "监控检查执行完成"
}

# 显示帮助信息
show_help() {
    echo "Airflow监控告警脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  monitor            执行完整监控检查"
    echo "  repair             尝试自动修复常见问题"
    echo "  report             生成监控报告"
    echo "  alert              发送测试告警"
    echo "  help               显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  SLACK_WEBHOOK_URL  Slack webhook URL（可选）"
    echo "  EMAIL_TO           告警邮件接收者（可选）"
    echo ""
    echo "示例:"
    echo "  $0 monitor"
    echo "  $0 repair"
    echo "  $0 report"
    echo "  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...' $0 alert \"测试消息\""
}

# 主函数
main() {
    case "$1" in
        monitor)
            perform_monitoring
            ;;
        repair)
            auto_repair
            ;;
        report)
            generate_monitoring_report
            ;;
        alert)
            if [ -n "$2" ]; then
                send_alert "$2"
            else
                send_alert "测试告警消息"
            fi
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

# 创建报告目录
mkdir -p $REPORT_DIR

# 执行主函数
main "$@"