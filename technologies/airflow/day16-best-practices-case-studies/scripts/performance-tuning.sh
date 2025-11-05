#!/bin/bash

# Airflow性能调优脚本
# 用于分析和优化Airflow性能

set -e  # 遇到错误时退出

# 配置变量
AIRFLOW_HOME="/opt/airflow"
LOG_FILE="/var/log/airflow/performance-tuning.log"
KUBE_NAMESPACE="airflow"
KUBE_CONTEXT="production"

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
    
    commands=("kubectl" "psql" "curl" "jq" "awk" "sed")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 命令未找到，请安装后重试"
            exit 1
        fi
    done
    
    log_info "所有必要命令检查通过"
}

# 收集系统资源使用情况
collect_system_metrics() {
    log_info "收集系统资源使用情况..."
    
    # 创建输出目录
    mkdir -p /tmp/airflow-metrics
    
    # 收集CPU使用情况
    top -b -n 1 | head -20 > /tmp/airflow-metrics/cpu_usage.txt
    
    # 收集内存使用情况
    free -h > /tmp/airflow-metrics/memory_usage.txt
    
    # 收集磁盘使用情况
    df -h >> /tmp/airflow-metrics/disk_usage.txt
    
    # 收集网络使用情况
    netstat -i > /tmp/airflow-metrics/network_usage.txt
    
    log_info "系统资源使用情况收集完成"
}

# 收集数据库性能指标
collect_database_metrics() {
    log_info "收集数据库性能指标..."
    
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
    
    # 创建SQL查询文件
    cat > /tmp/db_queries.sql << 'EOF'
-- 慢查询统计
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 表大小统计
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- 索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_tup_read DESC
LIMIT 10;

-- 连接数统计
SELECT 
    datname,
    numbackends as connections,
    xact_commit,
    xact_rollback
FROM pg_stat_database
WHERE datname = 'airflow';

-- 锁等待情况
SELECT 
    pg_stat_activity.datname,
    pg_stat_activity.query,
    pg_stat_activity.state,
    pg_stat_activity.wait_event_type,
    pg_stat_activity.wait_event
FROM pg_stat_activity
WHERE pg_stat_activity.state = 'active';
EOF
    
    # 执行查询并保存结果
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f /tmp/db_queries.sql > /tmp/airflow-metrics/database_metrics.txt
    
    if [ $? -eq 0 ]; then
        log_info "数据库性能指标收集完成"
    else
        log_error "数据库性能指标收集失败"
    fi
}

# 收集Airflow指标
collect_airflow_metrics() {
    log_info "收集Airflow指标..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 获取Airflow Webserver Pod
    WEB_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=webserver -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "$WEB_POD" ]; then
        log_error "未找到Airflow Webserver Pod"
        return 1
    fi
    
    # 从Webserver获取指标
    kubectl exec -n $KUBE_NAMESPACE $WEB_POD -- curl -s http://localhost:8080/api/v1/monitoring/metrics > /tmp/airflow-metrics/airflow_metrics.txt
    
    # 获取Pod资源使用情况
    kubectl top pods -n $KUBE_NAMESPACE > /tmp/airflow-metrics/pod_resources.txt
    
    # 获取Scheduler状态
    SCHED_POD=$(kubectl get pods -n $KUBE_NAMESPACE -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
    if [ -n "$SCHED_POD" ]; then
        kubectl logs $SCHED_POD -n $KUBE_NAMESPACE --tail=100 > /tmp/airflow-metrics/scheduler_logs.txt
    fi
    
    log_info "Airflow指标收集完成"
}

# 分析任务性能
analyze_task_performance() {
    log_info "分析任务性能..."
    
    # 创建分析SQL
    cat > /tmp/task_analysis.sql << 'EOF'
-- 任务执行时间分析
SELECT 
    dag_id,
    task_id,
    AVG(duration) as avg_duration,
    MAX(duration) as max_duration,
    MIN(duration) as min_duration,
    COUNT(*) as execution_count
FROM task_instance
WHERE state = 'success'
AND start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id, task_id
ORDER BY avg_duration DESC
LIMIT 20;

-- 任务失败率分析
SELECT 
    dag_id,
    task_id,
    COUNT(*) as total_executions,
    SUM(CASE WHEN state = 'failed' THEN 1 ELSE 0 END) as failed_executions,
    ROUND(
        SUM(CASE WHEN state = 'failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as failure_rate_percent
FROM task_instance
WHERE start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id, task_id
HAVING COUNT(*) > 10
ORDER BY failure_rate_percent DESC
LIMIT 20;

-- 长时间运行的DAG
SELECT 
    dag_id,
    AVG(duration) as avg_duration,
    MAX(duration) as max_duration,
    COUNT(*) as run_count
FROM dag_run
WHERE state = 'success'
AND start_date > NOW() - INTERVAL '7 days'
GROUP BY dag_id
ORDER BY avg_duration DESC
LIMIT 10;
EOF
    
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
    
    # 执行分析查询
    PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f /tmp/task_analysis.sql > /tmp/airflow-metrics/task_performance.txt
    
    log_info "任务性能分析完成"
}

# 生成性能报告
generate_performance_report() {
    log_info "生成性能报告..."
    
    # 创建报告目录
    REPORT_DIR="/tmp/airflow-performance-report-$(date +%Y%m%d-%H%M%S)"
    mkdir -p $REPORT_DIR
    
    # 复制收集的指标
    cp -r /tmp/airflow-metrics/* $REPORT_DIR/
    
    # 生成汇总报告
    cat > $REPORT_DIR/summary.txt << EOF
Airflow性能分析报告
生成时间: $(date)
分析范围: 最近7天

主要发现:
1. 系统资源使用情况:
   - CPU使用率: $(grep "Cpu(s)" /tmp/airflow-metrics/cpu_usage.txt | awk '{print $2}')
   - 内存使用率: $(grep "Mem:" /tmp/airflow-metrics/memory_usage.txt | awk '{print $3/$2*100"%"}')
   - 磁盘使用率: $(grep "/$" /tmp/airflow-metrics/disk_usage.txt | awk '{print $5}')

2. 数据库性能:
   - 最慢的查询平均执行时间: $(head -1 /tmp/airflow-metrics/database_metrics.txt | awk '/mean_time/ {print $4}')
   - 最大的表: $(head -1 /tmp/airflow-metrics/database_metrics.txt | awk '/size/ {print $4}')

3. 任务性能:
   - 最慢的任务平均执行时间: $(head -1 /tmp/airflow-metrics/task_performance.txt | awk '/avg_duration/ {print $4}')
   - 任务失败率最高的任务: $(head -1 /tmp/airflow-metrics/task_performance.txt | awk '/failure_rate_percent/ {print $7"%"}')
EOF
    
    # 压缩报告
    tar -czf $REPORT_DIR.tar.gz -C /tmp airflow-performance-report-$(date +%Y%m%d-%H%M%S)
    
    log_info "性能报告生成完成: $REPORT_DIR.tar.gz"
}

# 优化建议
generate_optimization_recommendations() {
    log_info "生成优化建议..."
    
    # 分析收集的数据并生成建议
    cat > /tmp/airflow-metrics/optimization_recommendations.txt << 'EOF'
Airflow性能优化建议:

1. 数据库优化:
   - 检查并优化慢查询
   - 为频繁查询的字段添加索引
   - 定期清理历史数据
   - 考虑对大表进行分区

2. 任务优化:
   - 将长时间运行的任务拆分为更小的子任务
   - 使用批量处理替代逐条处理
   - 优化数据传输和处理逻辑
   - 考虑使用更高效的算法或库

3. 资源配置优化:
   - 根据实际使用情况调整Pod资源请求和限制
   - 启用自动扩缩容功能
   - 优化并行任务数配置
   - 调整工作进程数量

4. 系统级优化:
   - 监控并优化磁盘I/O性能
   - 确保网络连接稳定且低延迟
   - 定期更新Airflow版本
   - 使用SSD存储提高性能

5. 配置优化:
   - 调整parallelism和max_active_tasks_per_dag参数
   - 优化数据库连接池配置
   - 启用DAG序列化
   - 调整调度器相关参数
EOF
    
    log_info "优化建议生成完成"
}

# 应用优化配置
apply_optimizations() {
    log_info "应用优化配置..."
    
    # 备份当前配置
    cp $AIRFLOW_HOME/airflow.cfg $AIRFLOW_HOME/airflow.cfg.backup.$(date +%Y%m%d-%H%M%S)
    
    # 应用数据库优化
    # 这里应该根据实际分析结果来调整配置
    
    # 应用资源优化
    # 调整Kubernetes资源配置
    kubectl patch deployment airflow-webserver -n $KUBE_NAMESPACE -p='{"spec":{"template":{"spec":{"containers":[{"name":"webserver","resources":{"requests":{"memory":"1Gi","cpu":"500m"},"limits":{"memory":"2Gi","cpu":"1"}}}]}}}}'
    
    kubectl patch deployment airflow-scheduler -n $KUBE_NAMESPACE -p='{"spec":{"template":{"spec":{"containers":[{"name":"scheduler","resources":{"requests":{"memory":"512Mi","cpu":"250m"},"limits":{"memory":"1Gi","cpu":"500m"}}}]}}}}'
    
    kubectl patch deployment airflow-worker -n $KUBE_NAMESPACE -p='{"spec":{"template":{"spec":{"containers":[{"name":"worker","resources":{"requests":{"memory":"1Gi","cpu":"500m"},"limits":{"memory":"2Gi","cpu":"1"}}}]}}}}'
    
    log_info "优化配置应用完成"
}

# 验证优化效果
verify_optimizations() {
    log_info "验证优化效果..."
    
    # 重新收集指标
    collect_system_metrics
    collect_database_metrics
    collect_airflow_metrics
    
    # 比较优化前后的指标
    log_info "优化效果验证完成，请手动比较优化前后的指标报告"
}

# 主性能分析函数
perform_performance_analysis() {
    log_info "开始执行性能分析..."
    
    check_dependencies
    collect_system_metrics
    collect_database_metrics
    collect_airflow_metrics
    analyze_task_performance
    generate_performance_report
    generate_optimization_recommendations
    
    log_info "性能分析执行完成"
}

# 显示帮助信息
show_help() {
    echo "Airflow性能调优脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  analyze            执行完整性能分析"
    echo "  optimize           应用优化配置"
    echo "  verify             验证优化效果"
    echo "  report             生成性能报告"
    echo "  help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 analyze"
    echo "  $0 optimize"
    echo "  $0 verify"
}

# 主函数
main() {
    case "$1" in
        analyze)
            perform_performance_analysis
            ;;
        optimize)
            apply_optimizations
            ;;
        verify)
            verify_optimizations
            ;;
        report)
            generate_performance_report
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