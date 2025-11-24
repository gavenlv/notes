#!/bin/bash
# ClickHouse 2副本集群健康检查脚本 - treasurycluster
# 集群名称: treasurycluster
# 副本数量: 2

CLUSTER_NAME="treasurycluster"
LOG_FILE="/var/log/clickhouse/treasurycluster_health.log"
ALERT_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"  # 请替换为实际webhook

# 日志函数
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# 发送告警函数
send_alert() {
    local severity=$1
    local title=$2
    local message=$3
    
    log_message "ALERT [$severity]: $title - $message"
    
    # 发送到Slack（可选）
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$severity] Treasury集群告警 - $title: $message\"}" \
            $ALERT_WEBHOOK 2>/dev/null || true
    fi
}

# 检查集群节点状态
check_cluster_nodes() {
    log_message "开始检查集群节点状态..."
    
    # 获取活跃节点数量
    active_nodes=$(clickhouse-client --query="
        SELECT count() 
        FROM system.clusters 
        WHERE cluster = '$CLUSTER_NAME' AND is_active = 1" 2>/dev/null || echo "0")
    
    total_nodes=$(clickhouse-client --query="
        SELECT count() 
        FROM system.clusters 
        WHERE cluster = '$CLUSTER_NAME'" 2>/dev/null || echo "0")
    
    if [ "$active_nodes" -eq "0" ]; then
        send_alert "CRITICAL" "集群连接失败" "无法连接到ClickHouse集群"
        return 1
    fi
    
    if [ "$active_nodes" -lt "$total_nodes" ]; then
        send_alert "WARNING" "集群节点异常" "活跃节点: $active_nodes/$total_nodes"
        return 1
    fi
    
    log_message "✓ 集群节点状态正常 ($active_nodes/$total_nodes)"
    return 0
}

# 检查副本同步状态
check_replica_sync() {
    log_message "开始检查副本同步状态..."
    
    # 检查延迟副本数量
    lag_count=$(clickhouse-client --query="
        SELECT count() 
        FROM system.replicas 
        WHERE replica_delay > 60 AND is_active = 1" 2>/dev/null || echo "0")
    
    if [ "$lag_count" -gt 0 ]; then
        # 获取延迟详情
        lag_details=$(clickhouse-client --query="
            SELECT 
                database, table, replica_name, replica_delay
            FROM system.replicas 
            WHERE replica_delay > 60 AND is_active = 1
            ORDER BY replica_delay DESC
            LIMIT 5" 2>/dev/null || echo "无法获取延迟详情")
        
        send_alert "WARNING" "副本同步延迟" "有 $lag_count 个副本延迟超过60秒"
        log_message "延迟详情: $lag_details"
        return 1
    fi
    
    # 检查只读副本
    readonly_count=$(clickhouse-client --query="
        SELECT count() 
        FROM system.replicas 
        WHERE is_readonly = 1 AND is_active = 1" 2>/dev/null || echo "0")
    
    if [ "$readonly_count" -gt 0 ]; then
        send_alert "CRITICAL" "副本只读状态" "有 $readonly_count 个副本处于只读模式"
        return 1
    fi
    
    log_message "✓ 副本同步状态正常"
    return 0
}

# 检查数据分布均衡性
check_data_distribution() {
    log_message "开始检查数据分布均衡性..."
    
    # 计算分片间数据量差异
    distribution_ratio=$(clickhouse-client --query="
        SELECT 
            max(total_rows) / min(total_rows) as ratio
        FROM (
            SELECT shard_num, sum(rows) as total_rows
            FROM system.parts 
            WHERE active = 1
            GROUP BY shard_num
        )" 2>/dev/null || echo "1")
    
    if (( $(echo "$distribution_ratio > 2" | bc -l) )); then
        send_alert "WARNING" "数据分布不均" "分片数据量差异比: $distribution_ratio"
        return 1
    fi
    
    log_message "✓ 数据分布均衡性正常 (差异比: $distribution_ratio)"
    return 0
}

# 检查系统资源使用
check_system_resources() {
    log_message "开始检查系统资源使用..."
    
    # 检查内存使用
    memory_usage=$(clickhouse-client --query="
        SELECT value
        FROM system.asynchronous_metrics
        WHERE metric = 'MemoryTracking'
        LIMIT 1" 2>/dev/null || echo "0")
    
    memory_total=$(clickhouse-client --query="
        SELECT value
        FROM system.asynchronous_metrics
        WHERE metric = 'MemoryLimit'
        LIMIT 1" 2>/dev/null || echo "10737418240")  # 默认10GB
    
    if [ "$memory_usage" -gt "0" ] && [ "$memory_total" -gt "0" ]; then
        memory_ratio=$(echo "scale=2; $memory_usage * 100 / $memory_total" | bc)
        
        if (( $(echo "$memory_ratio > 80" | bc -l) )); then
            send_alert "WARNING" "内存使用过高" "内存使用率: $memory_ratio%"
            return 1
        fi
    fi
    
    # 检查磁盘空间
    disk_usage=$(clickhouse-client --query="
        SELECT 
            formatReadableSize(sum(bytes_on_disk)) as used,
            formatReadableSize(sum(primary_key_bytes_in_memory)) as index_size
        FROM system.parts 
        WHERE active = 1" 2>/dev/null || echo "N/A N/A")
    
    log_message "磁盘使用情况: $disk_usage"
    log_message "✓ 系统资源使用正常"
    return 0
}

# 检查查询性能
check_query_performance() {
    log_message "开始检查查询性能..."
    
    # 检查慢查询数量（最近5分钟）
    slow_queries=$(clickhouse-client --query="
        SELECT count()
        FROM system.query_log
        WHERE event_time >= now() - INTERVAL 5 MINUTE
          AND type = 'QueryFinish'
          AND query_duration_ms > 10000" 2>/dev/null || echo "0")
    
    if [ "$slow_queries" -gt 10 ]; then
        send_alert "WARNING" "查询性能下降" "最近5分钟有 $slow_queries 个慢查询(>10秒)"
        return 1
    fi
    
    # 检查失败查询
    failed_queries=$(clickhouse-client --query="
        SELECT count()
        FROM system.query_log
        WHERE event_time >= now() - INTERVAL 5 MINUTE
          AND type = 'ExceptionWhileProcessing'" 2>/dev/null || echo "0")
    
    if [ "$failed_queries" -gt 5 ]; then
        send_alert "WARNING" "查询失败率偏高" "最近5分钟有 $failed_queries 个查询失败"
        return 1
    fi
    
    log_message "✓ 查询性能正常 (慢查询: $slow_queries, 失败查询: $failed_queries)"
    return 0
}

# 生成健康报告
generate_health_report() {
    log_message "生成集群健康报告..."
    
    report=$(clickhouse-client --query="
        SELECT 
            '=== Treasury集群健康报告 ===' as section,
            '' as value
        
        UNION ALL
        
        SELECT '集群名称', '$CLUSTER_NAME'
        
        UNION ALL
        
        SELECT '检查时间', toString(now())
        
        UNION ALL
        
        SELECT '节点状态', 
            concat(
                (SELECT count() FROM system.clusters WHERE cluster = '$CLUSTER_NAME' AND is_active = 1),
                '/',
                (SELECT count() FROM system.clusters WHERE cluster = '$CLUSTER_NAME')
            )
        
        UNION ALL
        
        SELECT '副本同步',
            CASE 
                WHEN (SELECT count() FROM system.replicas WHERE replica_delay > 60) = 0 THEN '正常'
                ELSE concat('有', (SELECT count() FROM system.replicas WHERE replica_delay > 60), '个副本延迟')
            END
        
        UNION ALL
        
        SELECT '内存使用', 
            concat(
                formatReadableSize((SELECT value FROM system.asynchronous_metrics WHERE metric = 'MemoryTracking')),
                '/',
                formatReadableSize((SELECT value FROM system.asynchronous_metrics WHERE metric = 'MemoryLimit'))
            )
        
        UNION ALL
        
        SELECT '数据总量',
            formatReadableSize((SELECT sum(bytes) FROM system.parts WHERE active = 1))
        
        UNION ALL
        
        SELECT '表数量',
            toString((SELECT count() FROM system.tables WHERE database NOT IN ('system')))
        
        UNION ALL
        
        SELECT '5分钟查询统计',
            concat(
                '成功: ', toString((SELECT count() FROM system.query_log WHERE event_time >= now() - INTERVAL 5 MINUTE AND type = 'QueryFinish')),
                ', 失败: ', toString((SELECT count() FROM system.query_log WHERE event_time >= now() - INTERVAL 5 MINUTE AND type = 'ExceptionWhileProcessing'))
            )
    " 2>/dev/null || echo "无法生成报告")
    
    echo "$report" >> $LOG_FILE
}

# 主程序
main() {
    log_message "=== 开始Treasury集群健康检查 ==="
    
    # 执行各项检查
    check_cluster_nodes
    check_replica_sync
    check_data_distribution
    check_system_resources
    check_query_performance
    
    # 生成健康报告
    generate_health_report
    
    log_message "=== Treasury集群健康检查完成 ==="
    echo "健康检查完成，详情查看日志: $LOG_FILE"
}

# 执行主程序
main "$@"