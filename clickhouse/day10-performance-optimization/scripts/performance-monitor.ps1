# ClickHouse Day 10: 性能监控和测试脚本
# 用于监控 ClickHouse 性能指标和执行基准测试

param(
    [string]$ClickHouseHost = "localhost",
    [int]$ClickHousePort = 8123,
    [string]$Database = "default",
    [string]$User = "default",
    [string]$Password = "",
    [string]$Action = "monitor", # monitor, benchmark, capacity
    [int]$TestRecords = 1000000
)

# ===============================================
# 配置和初始化
# ===============================================

$ClickHouseUrl = "http://${ClickHouseHost}:${ClickHousePort}"
$Headers = @{}
if ($User -and $Password) {
    $encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes("${User}:${Password}"))
    $Headers["Authorization"] = "Basic $encodedCreds"
}

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

# 执行ClickHouse查询函数
function Invoke-ClickHouseQuery {
    param(
        [string]$Query,
        [string]$Format = "JSONEachRow"
    )
    
    try {
        $body = @{
            query = $Query
            database = $Database
            default_format = $Format
        }
        
        $response = Invoke-RestMethod -Uri $ClickHouseUrl -Method Post -Body $body -Headers $Headers -ContentType "application/x-www-form-urlencoded"
        return $response
    }
    catch {
        Write-ColorOutput "查询执行失败: $($_.Exception.Message)" "Red"
        return $null
    }
}

# ===============================================
# 性能监控功能
# ===============================================

function Show-SystemMetrics {
    Write-ColorOutput "`n=== 系统性能指标 ===" "Cyan"
    
    # CPU 和内存使用
    $metricsQuery = @"
SELECT 
    metric,
    value
FROM system.asynchronous_metrics 
WHERE metric IN (
    'OSCPUWaitMicroseconds',
    'OSCPUVirtualTimeMicroseconds',
    'OSMemoryTotal',
    'OSMemoryAvailable',
    'OSMemoryFree'
)
ORDER BY metric
"@
    
    $metrics = Invoke-ClickHouseQuery -Query $metricsQuery -Format "TSV"
    if ($metrics) {
        Write-ColorOutput $metrics "White"
    }
}

function Show-QueryPerformance {
    Write-ColorOutput "`n=== 查询性能统计 ===" "Cyan"
    
    $queryStatsQuery = @"
SELECT 
    'Total Queries' as metric,
    toString(count()) as value
FROM system.query_log 
WHERE event_time >= now() - 3600

UNION ALL

SELECT 
    'Avg Duration (ms)' as metric,
    toString(round(avg(query_duration_ms), 2)) as value
FROM system.query_log 
WHERE type = 'QueryFinish' AND event_time >= now() - 3600

UNION ALL

SELECT 
    'Slow Queries (>1s)' as metric,
    toString(count()) as value
FROM system.query_log 
WHERE type = 'QueryFinish' 
AND query_duration_ms > 1000 
AND event_time >= now() - 3600

UNION ALL

SELECT 
    'Failed Queries' as metric,
    toString(count()) as value
FROM system.query_log 
WHERE type = 'ExceptionWhileProcessing' 
AND event_time >= now() - 3600
"@
    
    $queryStats = Invoke-ClickHouseQuery -Query $queryStatsQuery -Format "TSV"
    if ($queryStats) {
        Write-ColorOutput $queryStats "Green"
    }
}

function Show-MemoryUsage {
    Write-ColorOutput "`n=== 内存使用情况 ===" "Cyan"
    
    $memoryQuery = @"
SELECT 
    event,
    value,
    description
FROM system.events 
WHERE event LIKE '%Memory%' 
AND value > 0
ORDER BY value DESC
LIMIT 10
"@
    
    $memoryStats = Invoke-ClickHouseQuery -Query $memoryQuery -Format "TSV"
    if ($memoryStats) {
        Write-ColorOutput $memoryStats "Yellow"
    }
}

function Show-DiskUsage {
    Write-ColorOutput "`n=== 磁盘使用情况 ===" "Cyan"
    
    $diskQuery = @"
SELECT 
    table,
    formatReadableSize(sum(bytes_on_disk)) as size_on_disk,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    round(sum(data_uncompressed_bytes) / sum(bytes_on_disk), 2) as compression_ratio,
    sum(rows) as total_rows
FROM system.parts 
WHERE active = 1
GROUP BY table
ORDER BY sum(bytes_on_disk) DESC
LIMIT 10
"@
    
    $diskStats = Invoke-ClickHouseQuery -Query $diskQuery -Format "TSV"
    if ($diskStats) {
        Write-ColorOutput $diskStats "Magenta"
    }
}

function Show-SlowQueries {
    Write-ColorOutput "`n=== 慢查询分析 ===" "Cyan"
    
    $slowQueryQuery = @"
SELECT 
    left(query, 80) as query_snippet,
    query_duration_ms,
    formatReadableSize(memory_usage) as memory_used,
    read_rows,
    formatReadableSize(read_bytes) as read_bytes,
    toDateTime(event_time) as execution_time
FROM system.query_log 
WHERE type = 'QueryFinish' 
AND query_duration_ms > 1000
AND event_time >= now() - 3600
ORDER BY query_duration_ms DESC
LIMIT 5
"@
    
    $slowQueries = Invoke-ClickHouseQuery -Query $slowQueryQuery -Format "TSV"
    if ($slowQueries) {
        Write-ColorOutput $slowQueries "Red"
    }
}

# ===============================================
# 基准测试功能
# ===============================================

function Run-BenchmarkTest {
    Write-ColorOutput "`n=== 开始基准测试 ===" "Cyan"
    
    # 创建测试表
    Write-ColorOutput "创建测试表..." "Yellow"
    $createTableQuery = @"
CREATE TABLE IF NOT EXISTS benchmark_test (
    id UInt64,
    category LowCardinality(String),
    value Float64,
    timestamp DateTime,
    data String
) ENGINE = MergeTree()
ORDER BY (category, timestamp)
PARTITION BY toYYYYMM(timestamp)
"@
    
    Invoke-ClickHouseQuery -Query $createTableQuery | Out-Null
    
    # 插入性能测试
    Write-ColorOutput "执行插入性能测试 ($TestRecords 条记录)..." "Yellow"
    $insertStartTime = Get-Date
    
    $insertQuery = @"
INSERT INTO benchmark_test 
SELECT 
    number as id,
    ['A', 'B', 'C', 'D', 'E'][number % 5 + 1] as category,
    rand() / 1000000 as value,
    now() - (number % (30 * 24 * 3600)) as timestamp,
    concat('data_', toString(number % 1000)) as data
FROM numbers($TestRecords)
"@
    
    Invoke-ClickHouseQuery -Query $insertQuery | Out-Null
    $insertEndTime = Get-Date
    $insertDuration = ($insertEndTime - $insertStartTime).TotalSeconds
    $insertRate = [math]::Round($TestRecords / $insertDuration, 0)
    
    Write-ColorOutput "插入完成: $insertRate 行/秒 (总耗时: $([math]::Round($insertDuration, 2)) 秒)" "Green"
    
    # 查询性能测试
    Write-ColorOutput "执行查询性能测试..." "Yellow"
    
    $queries = @(
        @{
            Name = "简单计数查询"
            Query = "SELECT count() FROM benchmark_test"
        },
        @{
            Name = "聚合查询"
            Query = "SELECT category, count(), avg(value) FROM benchmark_test GROUP BY category"
        },
        @{
            Name = "过滤查询"
            Query = "SELECT count() FROM benchmark_test WHERE value > 0.5"
        },
        @{
            Name = "复杂聚合查询"
            Query = "SELECT category, toDate(timestamp) as date, count(), avg(value), max(value) FROM benchmark_test GROUP BY category, date ORDER BY date DESC LIMIT 100"
        }
    )
    
    foreach ($queryTest in $queries) {
        $queryStartTime = Get-Date
        Invoke-ClickHouseQuery -Query $queryTest.Query | Out-Null
        $queryEndTime = Get-Date
        $queryDuration = ($queryEndTime - $queryStartTime).TotalMilliseconds
        
        Write-ColorOutput "$($queryTest.Name): $([math]::Round($queryDuration, 2)) ms" "Green"
    }
    
    # 清理测试表
    Write-ColorOutput "清理测试数据..." "Yellow"
    # Invoke-ClickHouseQuery -Query "DROP TABLE IF EXISTS benchmark_test" | Out-Null
    Write-ColorOutput "基准测试完成!" "Cyan"
}

# ===============================================
# 容量规划功能
# ===============================================

function Show-CapacityAnalysis {
    Write-ColorOutput "`n=== 容量规划分析 ===" "Cyan"
    
    # 数据增长趋势
    Write-ColorOutput "`n--- 数据增长趋势 ---" "Yellow"
    $growthQuery = @"
SELECT 
    toDate(event_time) as date,
    count() as query_count,
    sum(read_rows) as total_read_rows,
    formatReadableSize(sum(read_bytes)) as total_read_bytes
FROM system.query_log
WHERE event_time >= today() - 7
AND type = 'QueryFinish'
GROUP BY date
ORDER BY date DESC
LIMIT 7
"@
    
    $growthData = Invoke-ClickHouseQuery -Query $growthQuery -Format "TSV"
    if ($growthData) {
        Write-ColorOutput $growthData "White"
    }
    
    # 存储预测
    Write-ColorOutput "`n--- 存储容量预测 ---" "Yellow"
    $storageQuery = @"
SELECT 
    formatReadableSize(sum(bytes_on_disk)) as current_size,
    formatReadableSize(sum(bytes_on_disk) * 2) as projected_6_months,
    formatReadableSize(sum(bytes_on_disk) * 4) as projected_1_year
FROM system.parts 
WHERE active = 1
"@
    
    $storageData = Invoke-ClickHouseQuery -Query $storageQuery -Format "TSV"
    if ($storageData) {
        Write-ColorOutput $storageData "Cyan"
    }
    
    # 内存使用预测
    Write-ColorOutput "`n--- 内存使用分析 ---" "Yellow"
    $memoryAnalysisQuery = @"
SELECT 
    formatReadableSize(quantile(0.50)(memory_usage)) as p50_memory,
    formatReadableSize(quantile(0.95)(memory_usage)) as p95_memory,
    formatReadableSize(quantile(0.99)(memory_usage)) as p99_memory,
    formatReadableSize(max(memory_usage)) as max_memory
FROM system.query_log
WHERE type = 'QueryFinish' 
AND event_time >= today() - 7
AND memory_usage > 0
"@
    
    $memoryAnalysis = Invoke-ClickHouseQuery -Query $memoryAnalysisQuery -Format "TSV"
    if ($memoryAnalysis) {
        Write-ColorOutput $memoryAnalysis "Magenta"
    }
}

# ===============================================
# 性能优化建议
# ===============================================

function Show-OptimizationSuggestions {
    Write-ColorOutput "`n=== 性能优化建议 ===" "Cyan"
    
    # 检查慢查询
    $slowQueryCount = Invoke-ClickHouseQuery -Query "SELECT count() FROM system.query_log WHERE type = 'QueryFinish' AND query_duration_ms > 5000 AND event_time >= now() - 3600" -Format "TabSeparated"
    if ([int]$slowQueryCount -gt 0) {
        Write-ColorOutput "⚠️  发现 $slowQueryCount 个慢查询 (>5秒)，建议优化查询或添加索引" "Red"
    }
    
    # 检查内存使用
    $highMemoryCount = Invoke-ClickHouseQuery -Query "SELECT count() FROM system.query_log WHERE type = 'QueryFinish' AND memory_usage > 10000000000 AND event_time >= now() - 3600" -Format "TabSeparated"
    if ([int]$highMemoryCount -gt 0) {
        Write-ColorOutput "⚠️  发现 $highMemoryCount 个高内存查询 (>10GB)，建议优化查询逻辑" "Red"
    }
    
    # 检查表引擎
    $nonOptimalTables = Invoke-ClickHouseQuery -Query "SELECT count() FROM system.tables WHERE engine NOT IN ('MergeTree', 'ReplicatedMergeTree', 'ReplacingMergeTree', 'SummingMergeTree', 'AggregatingMergeTree', 'CollapsingMergeTree', 'VersionedCollapsingMergeTree') AND database = '$Database'" -Format "TabSeparated"
    if ([int]$nonOptimalTables -gt 0) {
        Write-ColorOutput "⚠️  发现 $nonOptimalTables 个非MergeTree表，建议使用MergeTree引擎族" "Yellow"
    }
    
    # 检查分区策略
    Write-ColorOutput "✅ 建议定期检查分区策略，确保分区大小合理 (1-10GB/分区)" "Green"
    Write-ColorOutput "✅ 建议使用跳数索引优化过滤查询性能" "Green"
    Write-ColorOutput "✅ 建议监控合并操作，避免小文件过多" "Green"
}

# ===============================================
# 主函数
# ===============================================

function Main {
    Write-ColorOutput "ClickHouse 性能监控和测试工具" "Cyan"
    Write-ColorOutput "连接到: $ClickHouseUrl" "White"
    Write-ColorOutput "数据库: $Database" "White"
    Write-ColorOutput "操作: $Action" "White"
    Write-ColorOutput "=" * 50 "White"
    
    # 测试连接
    try {
        $testQuery = "SELECT version()"
        $version = Invoke-ClickHouseQuery -Query $testQuery -Format "TabSeparated"
        Write-ColorOutput "ClickHouse 版本: $version" "Green"
    }
    catch {
        Write-ColorOutput "无法连接到 ClickHouse 服务器: $($_.Exception.Message)" "Red"
        return
    }
    
    switch ($Action.ToLower()) {
        "monitor" {
            Show-SystemMetrics
            Show-QueryPerformance
            Show-MemoryUsage
            Show-DiskUsage
            Show-SlowQueries
            Show-OptimizationSuggestions
        }
        "benchmark" {
            Run-BenchmarkTest
        }
        "capacity" {
            Show-CapacityAnalysis
        }
        "all" {
            Show-SystemMetrics
            Show-QueryPerformance
            Show-MemoryUsage
            Show-DiskUsage
            Show-SlowQueries
            Show-CapacityAnalysis
            Show-OptimizationSuggestions
        }
        default {
            Write-ColorOutput "未知操作: $Action" "Red"
            Write-ColorOutput "可用操作: monitor, benchmark, capacity, all" "Yellow"
        }
    }
    
    Write-ColorOutput "`n性能分析完成!" "Cyan"
}

# ===============================================
# 执行脚本
# ===============================================

# 脚本使用说明
if ($args -contains "-help" -or $args -contains "--help" -or $args -contains "/?") {
    Write-ColorOutput @"
ClickHouse 性能监控脚本使用说明:

参数:
  -ClickHouseHost    ClickHouse 服务器地址 (默认: localhost)
  -ClickHousePort    ClickHouse HTTP 端口 (默认: 8123)
  -Database          数据库名称 (默认: default)
  -User              用户名 (默认: default)
  -Password          密码 (默认: 空)
  -Action            操作类型: monitor, benchmark, capacity, all (默认: monitor)
  -TestRecords       基准测试记录数 (默认: 1000000)

示例:
  .\performance-monitor.ps1 -Action monitor
  .\performance-monitor.ps1 -Action benchmark -TestRecords 500000
  .\performance-monitor.ps1 -Action capacity
  .\performance-monitor.ps1 -Action all -ClickHouseHost "192.168.1.100"

操作说明:
  monitor    - 显示系统性能指标和查询统计
  benchmark  - 执行基准测试
  capacity   - 显示容量规划分析
  all        - 执行所有分析
"@ "White"
    return
}

# 执行主函数
Main 