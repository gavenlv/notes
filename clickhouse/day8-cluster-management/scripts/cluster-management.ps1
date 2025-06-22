# ClickHouse 集群管理脚本
# Day 8: 集群管理和分布式
# =====================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$ClusterName = "production_cluster",
    
    [Parameter(Mandatory=$false)]
    [string]$Host = "localhost",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8123,
    
    [Parameter(Mandatory=$false)]
    [string]$Database = "default",
    
    [Parameter(Mandatory=$false)]
    [string]$User = "default",
    
    [Parameter(Mandatory=$false)]
    [string]$Password = ""
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 执行ClickHouse查询
function Invoke-ClickHouseQuery {
    param(
        [string]$Query,
        [string]$Format = "TabSeparated"
    )
    
    try {
        $uri = "http://$($Host):$($Port)/"
        $body = @{
            query = $Query
            format = $Format
            user = $User
            password = $Password
            database = $Database
        }
        
        $response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/x-www-form-urlencoded"
        return $response
    }
    catch {
        Write-ColorOutput "查询执行失败: $($_.Exception.Message)" "Red"
        return $null
    }
}

# 检查集群状态
function Check-ClusterStatus {
    Write-ColorOutput "🔍 检查集群状态..." "Cyan"
    
    $query = @"
SELECT 
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    is_local,
    errors_count,
    slowdowns_count,
    CASE 
        WHEN errors_count = 0 THEN 'Healthy'
        WHEN errors_count < 10 THEN 'Warning'
        ELSE 'Critical'
    END as status
FROM system.clusters 
WHERE cluster = '$ClusterName'
ORDER BY cluster, shard_num, replica_num
"@
    
    $result = Invoke-ClickHouseQuery -Query $query -Format "PrettyCompact"
    if ($result) {
        Write-ColorOutput $result "Green"
    }
}

# 检查副本状态
function Check-ReplicaStatus {
    Write-ColorOutput "🔄 检查副本状态..." "Cyan"
    
    $query = @"
SELECT 
    database,
    table,
    replica_name,
    is_leader,
    is_readonly,
    absolute_delay,
    queue_size,
    inserts_in_queue,
    merges_in_queue,
    CASE 
        WHEN absolute_delay < 60 THEN 'OK'
        WHEN absolute_delay < 300 THEN 'Warning'
        ELSE 'Critical'
    END as lag_status
FROM system.replicas
ORDER BY absolute_delay DESC
LIMIT 20
"@
    
    $result = Invoke-ClickHouseQuery -Query $query -Format "PrettyCompact"
    if ($result) {
        Write-ColorOutput $result "Green"
    }
}

# 检查分布式表
function Check-DistributedTables {
    Write-ColorOutput "📊 检查分布式表..." "Cyan"
    
    $query = @"
SELECT 
    database,
    name as table_name,
    engine,
    engine_full,
    total_rows,
    total_bytes
FROM system.tables 
WHERE engine LIKE '%Distributed%'
ORDER BY database, name
"@
    
    $result = Invoke-ClickHouseQuery -Query $query -Format "PrettyCompact"
    if ($result) {
        Write-ColorOutput $result "Green"
    }
}

# 检查ZooKeeper连接
function Check-ZooKeeperConnection {
    Write-ColorOutput "🐘 检查ZooKeeper连接..." "Cyan"
    
    $query = @"
SELECT 
    name,
    value,
    changed
FROM system.zookeeper 
WHERE path = '/'
LIMIT 10
"@
    
    $result = Invoke-ClickHouseQuery -Query $query -Format "PrettyCompact"
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "ZooKeeper连接可能存在问题" "Yellow"
    }
}

# 查看集群性能指标
function Show-ClusterMetrics {
    Write-ColorOutput "📈 集群性能指标..." "Cyan"
    
    # 查询统计
    $queryStats = @"
SELECT 
    'Query Statistics' as metric_type,
    count() as total_queries,
    avg(query_duration_ms) as avg_duration_ms,
    quantile(0.95)(query_duration_ms) as p95_duration_ms,
    sum(read_rows) as total_read_rows,
    formatReadableSize(sum(read_bytes)) as total_read_bytes
FROM system.query_log 
WHERE event_date = today()
  AND type = 'QueryFinish'
  AND query NOT LIKE '%system.%'
"@
    
    $result1 = Invoke-ClickHouseQuery -Query $queryStats -Format "PrettyCompact"
    if ($result1) {
        Write-ColorOutput $result1 "Green"
    }
    
    # 系统资源
    $systemStats = @"
SELECT 
    'System Resources' as metric_type,
    hostName() as hostname,
    uptime() as uptime_seconds,
    formatReadableSize(total_memory) as total_memory,
    round((total_memory - free_memory) / total_memory * 100, 2) as memory_usage_percent
FROM system.asynchronous_metrics
WHERE metric = 'MemoryTotal'
LIMIT 1
"@
    
    $result2 = Invoke-ClickHouseQuery -Query $systemStats -Format "PrettyCompact"
    if ($result2) {
        Write-ColorOutput $result2 "Green"
    }
}

# 执行集群健康检查
function Run-HealthCheck {
    Write-ColorOutput "🏥 执行集群健康检查..." "Yellow"
    Write-ColorOutput "=" * 50 "Yellow"
    
    Check-ClusterStatus
    Write-ColorOutput ""
    
    Check-ReplicaStatus
    Write-ColorOutput ""
    
    Check-DistributedTables
    Write-ColorOutput ""
    
    Check-ZooKeeperConnection
    Write-ColorOutput ""
    
    Show-ClusterMetrics
    
    Write-ColorOutput "=" * 50 "Yellow"
    Write-ColorOutput "✅ 健康检查完成" "Green"
}

# 同步副本
function Sync-Replica {
    param([string]$TableName)
    
    if (-not $TableName) {
        Write-ColorOutput "请指定表名" "Red"
        return
    }
    
    Write-ColorOutput "🔄 同步副本表: $TableName" "Cyan"
    
    $query = "SYSTEM SYNC REPLICA $TableName"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result -ne $null) {
        Write-ColorOutput "✅ 副本同步完成" "Green"
    }
}

# 重启副本队列
function Restart-ReplicaQueue {
    param([string]$TableName)
    
    if (-not $TableName) {
        Write-ColorOutput "请指定表名" "Red"
        return
    }
    
    Write-ColorOutput "🔄 重启副本队列: $TableName" "Cyan"
    
    $query = "SYSTEM RESTART REPLICA $TableName"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result -ne $null) {
        Write-ColorOutput "✅ 副本队列重启完成" "Green"
    }
}

# 优化表
function Optimize-ClusterTables {
    param([string]$DatabaseName = "default")
    
    Write-ColorOutput "🚀 优化集群表..." "Cyan"
    
    # 获取所有MergeTree表
    $query = @"
SELECT 
    database,
    name
FROM system.tables 
WHERE database = '$DatabaseName'
  AND engine LIKE '%MergeTree%'
"@
    
    $tables = Invoke-ClickHouseQuery -Query $query -Format "TSV"
    
    if ($tables) {
        $tableList = $tables -split "`n"
        foreach ($tableLine in $tableList) {
            if ($tableLine.Trim()) {
                $parts = $tableLine -split "`t"
                if ($parts.Length -eq 2) {
                    $db = $parts[0]
                    $table = $parts[1]
                    
                    Write-ColorOutput "优化表: $db.$table" "Yellow"
                    $optimizeQuery = "OPTIMIZE TABLE $db.$table FINAL"
                    Invoke-ClickHouseQuery -Query $optimizeQuery | Out-Null
                }
            }
        }
        Write-ColorOutput "✅ 表优化完成" "Green"
    }
}

# 查看分布式DDL队列
function Show-DDLQueue {
    Write-ColorOutput "📋 分布式DDL队列..." "Cyan"
    
    $query = @"
SELECT 
    entry,
    host,
    port,
    status,
    exception,
    query
FROM system.distributed_ddl_queue
ORDER BY entry DESC
LIMIT 10
"@
    
    $result = Invoke-ClickHouseQuery -Query $query -Format "PrettyCompact"
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "DDL队列为空" "Yellow"
    }
}

# 数据分布分析
function Analyze-DataDistribution {
    param([string]$TableName)
    
    if (-not $TableName) {
        Write-ColorOutput "请指定表名" "Red"
        return
    }
    
    Write-ColorOutput "📊 分析数据分布: $TableName" "Cyan"
    
    $query = @"
SELECT 
    hostName() as host,
    count() as row_count,
    formatReadableSize(sum(bytes_on_disk)) as size_on_disk,
    round(count() * 100.0 / (SELECT count() FROM cluster('$ClusterName', currentDatabase(), '$TableName')), 2) as percentage
FROM $TableName
GROUP BY hostName()
ORDER BY row_count DESC
"@
    
    $result = Invoke-ClickHouseQuery -Query $query -Format "PrettyCompact"
    if ($result) {
        Write-ColorOutput $result "Green"
    }
}

# 创建测试集群表
function Create-TestClusterTable {
    Write-ColorOutput "🛠️ 创建测试集群表..." "Cyan"
    
    # 创建本地表
    $localTableQuery = @"
CREATE TABLE IF NOT EXISTS test_cluster_local ON CLUSTER $ClusterName (
    id UInt32,
    timestamp DateTime DEFAULT now(),
    message String,
    value Float64
) ENGINE = MergeTree()
ORDER BY (id, timestamp)
PARTITION BY toYYYYMM(timestamp)
"@
    
    $result1 = Invoke-ClickHouseQuery -Query $localTableQuery
    
    # 创建分布式表
    $distributedTableQuery = @"
CREATE TABLE IF NOT EXISTS test_cluster_distributed ON CLUSTER $ClusterName AS test_cluster_local
ENGINE = Distributed('$ClusterName', currentDatabase(), 'test_cluster_local', rand())
"@
    
    $result2 = Invoke-ClickHouseQuery -Query $distributedTableQuery
    
    if ($result1 -ne $null -and $result2 -ne $null) {
        Write-ColorOutput "✅ 测试表创建完成" "Green"
        
        # 插入测试数据
        Write-ColorOutput "📝 插入测试数据..." "Yellow"
        $insertQuery = @"
INSERT INTO test_cluster_distributed 
SELECT 
    number as id,
    now() - toIntervalSecond(number) as timestamp,
    'test_message_' || toString(number) as message,
    rand() / 4294967295.0 as value
FROM numbers(1000)
"@
        
        Invoke-ClickHouseQuery -Query $insertQuery | Out-Null
        Write-ColorOutput "✅ 测试数据插入完成" "Green"
    }
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput "ClickHouse 集群管理脚本" "Yellow"
    Write-ColorOutput "=" * 40 "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "用法: .\cluster-management.ps1 -Action <action> [参数]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "可用操作:" "Cyan"
    Write-ColorOutput "  health          - 执行完整健康检查" "White"
    Write-ColorOutput "  status          - 检查集群状态" "White"
    Write-ColorOutput "  replicas        - 检查副本状态" "White"
    Write-ColorOutput "  tables          - 检查分布式表" "White"
    Write-ColorOutput "  zookeeper       - 检查ZooKeeper连接" "White"
    Write-ColorOutput "  metrics         - 显示性能指标" "White"
    Write-ColorOutput "  ddl-queue       - 查看DDL队列" "White"
    Write-ColorOutput "  sync-replica    - 同步副本 (需要-TableName参数)" "White"
    Write-ColorOutput "  restart-replica - 重启副本队列 (需要-TableName参数)" "White"
    Write-ColorOutput "  optimize        - 优化表" "White"
    Write-ColorOutput "  analyze-dist    - 分析数据分布 (需要-TableName参数)" "White"
    Write-ColorOutput "  create-test     - 创建测试表" "White"
    Write-ColorOutput "  help            - 显示此帮助信息" "White"
    Write-ColorOutput ""
    Write-ColorOutput "参数:" "Cyan"
    Write-ColorOutput "  -ClusterName    - 集群名称 (默认: production_cluster)" "White"
    Write-ColorOutput "  -Host           - ClickHouse主机 (默认: localhost)" "White"
    Write-ColorOutput "  -Port           - ClickHouse端口 (默认: 8123)" "White"
    Write-ColorOutput "  -Database       - 数据库名 (默认: default)" "White"
    Write-ColorOutput "  -User           - 用户名 (默认: default)" "White"
    Write-ColorOutput "  -Password       - 密码 (默认: 空)" "White"
    Write-ColorOutput "  -TableName      - 表名 (某些操作需要)" "White"
    Write-ColorOutput ""
    Write-ColorOutput "示例:" "Cyan"
    Write-ColorOutput "  .\cluster-management.ps1 -Action health" "White"
    Write-ColorOutput "  .\cluster-management.ps1 -Action sync-replica -TableName user_events_local" "White"
    Write-ColorOutput "  .\cluster-management.ps1 -Action analyze-dist -TableName test_cluster_local" "White"
}

# 主程序逻辑
function Main {
    Write-ColorOutput "🚀 ClickHouse 集群管理工具" "Magenta"
    Write-ColorOutput "连接到: $($Host):$($Port) (集群: $ClusterName)" "Gray"
    Write-ColorOutput ""
    
    switch ($Action.ToLower()) {
        "health" { Run-HealthCheck }
        "status" { Check-ClusterStatus }
        "replicas" { Check-ReplicaStatus }
        "tables" { Check-DistributedTables }
        "zookeeper" { Check-ZooKeeperConnection }
        "metrics" { Show-ClusterMetrics }
        "ddl-queue" { Show-DDLQueue }
        "sync-replica" { 
            if ($args.Length -gt 0) {
                Sync-Replica -TableName $args[0]
            } else {
                Write-ColorOutput "请提供表名: -TableName <table_name>" "Red"
            }
        }
        "restart-replica" { 
            if ($args.Length -gt 0) {
                Restart-ReplicaQueue -TableName $args[0]
            } else {
                Write-ColorOutput "请提供表名: -TableName <table_name>" "Red"
            }
        }
        "optimize" { Optimize-ClusterTables }
        "analyze-dist" { 
            if ($args.Length -gt 0) {
                Analyze-DataDistribution -TableName $args[0]
            } else {
                Write-ColorOutput "请提供表名: -TableName <table_name>" "Red"
            }
        }
        "create-test" { Create-TestClusterTable }
        "help" { Show-Help }
        default { 
            Write-ColorOutput "未知操作: $Action" "Red"
            Show-Help 
        }
    }
}

# 执行主程序
try {
    Main
}
catch {
    Write-ColorOutput "脚本执行出错: $($_.Exception.Message)" "Red"
    Write-ColorOutput "请检查ClickHouse连接和参数设置" "Yellow"
}

Write-ColorOutput ""
Write-ColorOutput "脚本执行完成" "Green" 