# ClickHouse Day 13: 性能调优和监控脚本
# PowerShell脚本用于ClickHouse性能分析、调优和监控

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("analyze", "optimize", "monitor", "benchmark", "report", "cleanup")]
    [string]$Action,
    
    [string]$Host = "localhost",
    [int]$Port = 9000,
    [string]$Username = "default",
    [string]$Password = "",
    [string]$Database = "",
    [string]$Table = "",
    [int]$Days = 7,
    [string]$OutputPath = "D:\ClickHouse\Reports",
    [switch]$Verbose,
    [switch]$AutoFix
)

# 全局变量
$script:LogFile = Join-Path $OutputPath "performance-tuning-$(Get-Date -Format 'yyyyMMdd').log"
$script:ConnectionString = "clickhouse-client --host=$Host --port=$Port --user=$Username"
if ($Password) { $script:ConnectionString += " --password=$Password" }

# 确保输出目录存在
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
        "DEBUG" { if ($Verbose) { Write-Host $logMessage -ForegroundColor Gray } }
        default { Write-Host $logMessage -ForegroundColor White }
    }
    
    Add-Content -Path $script:LogFile -Value $logMessage
}

# 执行ClickHouse查询
function Invoke-ClickHouseQuery {
    param(
        [string]$Query,
        [string]$Format = "TabSeparated",
        [switch]$Silent
    )
    
    try {
        $cmd = "$script:ConnectionString --query=`"$Query`""
        if ($Format -ne "TabSeparated") {
            $cmd += " --format=$Format"
        }
        
        if (!$Silent) {
            Write-Log "执行查询: $($Query.Substring(0, [Math]::Min(100, $Query.Length)))..." "DEBUG"
        }
        
        $result = Invoke-Expression $cmd
        return $result
    }
    catch {
        Write-Log "查询执行失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 性能分析
function Start-PerformanceAnalysis {
    Write-Log "开始性能分析..." "INFO"
    
    $report = @{}
    
    # 1. 系统资源分析
    Write-Log "分析系统资源使用..." "INFO"
    $report.SystemMetrics = Get-SystemMetrics
    
    # 2. 查询性能分析
    Write-Log "分析查询性能..." "INFO"
    $report.QueryPerformance = Get-QueryPerformance
    
    # 3. 表结构分析
    Write-Log "分析表结构..." "INFO"
    $report.TableAnalysis = Get-TableAnalysis
    
    # 4. 索引使用分析
    Write-Log "分析索引使用..." "INFO"
    $report.IndexAnalysis = Get-IndexAnalysis
    
    # 5. 内存使用分析
    Write-Log "分析内存使用..." "INFO"
    $report.MemoryAnalysis = Get-MemoryAnalysis
    
    # 生成分析报告
    $reportPath = Join-Path $OutputPath "performance-analysis-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Log "性能分析完成，报告保存至: $reportPath" "INFO"
    return $report
}

# 获取系统指标
function Get-SystemMetrics {
    $metrics = @{}
    
    try {
        # ClickHouse系统指标
        $systemMetrics = Invoke-ClickHouseQuery "SELECT metric, value FROM system.metrics" -Silent
        $asyncMetrics = Invoke-ClickHouseQuery "SELECT metric, value FROM system.asynchronous_metrics WHERE metric LIKE '%Memory%' OR metric LIKE '%CPU%'" -Silent
        
        $metrics.ClickHouseMetrics = $systemMetrics
        $metrics.AsyncMetrics = $asyncMetrics
        
        # 当前运行查询
        $runningQueries = Invoke-ClickHouseQuery "SELECT query_id, user, elapsed, formatReadableSize(memory_usage) as memory, read_rows, substring(query, 1, 100) as query_preview FROM system.processes WHERE query != ''" -Silent
        $metrics.RunningQueries = $runningQueries
        
        # 连接统计
        $connections = Invoke-ClickHouseQuery "SELECT metric, value FROM system.metrics WHERE metric LIKE '%Connection%'" -Silent
        $metrics.Connections = $connections
        
    }
    catch {
        Write-Log "获取系统指标失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $metrics
}

# 获取查询性能数据
function Get-QueryPerformance {
    $performance = @{}
    
    try {
        # 慢查询分析
        $slowQueries = Invoke-ClickHouseQuery @"
SELECT 
    query_id,
    user,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) as read_bytes,
    formatReadableSize(memory_usage) as memory_usage,
    substring(query, 1, 200) as query_preview
FROM system.query_log
WHERE event_date >= today() - $Days
    AND type = 'QueryFinish'
    AND query_duration_ms > 5000
ORDER BY query_duration_ms DESC
LIMIT 20
"@ -Silent
        
        $performance.SlowQueries = $slowQueries
        
        # 查询统计
        $queryStats = Invoke-ClickHouseQuery @"
SELECT 
    toStartOfHour(event_time) as hour,
    count() as query_count,
    avg(query_duration_ms) as avg_duration,
    quantile(0.5)(query_duration_ms) as median_duration,
    quantile(0.95)(query_duration_ms) as p95_duration,
    quantile(0.99)(query_duration_ms) as p99_duration,
    max(query_duration_ms) as max_duration
FROM system.query_log
WHERE event_date >= today() - $Days
    AND type = 'QueryFinish'
GROUP BY hour
ORDER BY hour DESC
LIMIT 24
"@ -Silent
        
        $performance.QueryStats = $queryStats
        
        # 错误查询分析
        $errorQueries = Invoke-ClickHouseQuery @"
SELECT 
    exception_code,
    exception,
    count() as error_count,
    any(substring(query, 1, 200)) as example_query
FROM system.query_log
WHERE event_date >= today() - $Days
    AND type = 'ExceptionWhileProcessing'
GROUP BY exception_code, exception
ORDER BY error_count DESC
LIMIT 10
"@ -Silent
        
        $performance.ErrorQueries = $errorQueries
        
        # 用户查询统计
        $userStats = Invoke-ClickHouseQuery @"
SELECT 
    user,
    count() as query_count,
    avg(query_duration_ms) as avg_duration,
    sum(read_rows) as total_read_rows,
    formatReadableSize(sum(read_bytes)) as total_read_bytes
FROM system.query_log
WHERE event_date >= today() - $Days
    AND type = 'QueryFinish'
GROUP BY user
ORDER BY query_count DESC
"@ -Silent
        
        $performance.UserStats = $userStats
        
    }
    catch {
        Write-Log "获取查询性能数据失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $performance
}

# 获取表分析数据
function Get-TableAnalysis {
    $analysis = @{}
    
    try {
        # 表大小统计
        $tableSizes = Invoke-ClickHouseQuery @"
SELECT 
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as size_on_disk,
    formatReadableSize(sum(bytes)) as uncompressed_size,
    sum(rows) as total_rows,
    count() as parts_count,
    avg(bytes_on_disk / rows) as avg_row_size
FROM system.parts
WHERE active = 1
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC
LIMIT 20
"@ -Silent
        
        $analysis.TableSizes = $tableSizes
        
        # 分区分析
        $partitionAnalysis = Invoke-ClickHouseQuery @"
SELECT 
    database,
    table,
    partition,
    formatReadableSize(sum(bytes_on_disk)) as partition_size,
    sum(rows) as partition_rows,
    count() as parts_in_partition,
    min(min_date) as min_date,
    max(max_date) as max_date
FROM system.parts
WHERE active = 1
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY database, table, partition
HAVING count() > 10
ORDER BY sum(bytes_on_disk) DESC
LIMIT 20
"@ -Silent
        
        $analysis.PartitionAnalysis = $partitionAnalysis
        
        # 表引擎统计
        $engineStats = Invoke-ClickHouseQuery @"
SELECT 
    engine,
    count() as table_count,
    formatReadableSize(sum(total_bytes)) as total_size
FROM system.tables t
LEFT JOIN (
    SELECT 
        database,
        table,
        sum(bytes_on_disk) as total_bytes
    FROM system.parts
    WHERE active = 1
    GROUP BY database, table
) p ON t.database = p.database AND t.table = p.table
WHERE t.database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
GROUP BY engine
ORDER BY table_count DESC
"@ -Silent
        
        $analysis.EngineStats = $engineStats
        
    }
    catch {
        Write-Log "获取表分析数据失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $analysis
}

# 获取索引分析数据
function Get-IndexAnalysis {
    $indexAnalysis = @{}
    
    try {
        # 跳数索引统计
        $skipIndexes = Invoke-ClickHouseQuery @"
SELECT 
    database,
    table,
    name,
    type,
    expr,
    granularity
FROM system.data_skipping_indices
WHERE database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
ORDER BY database, table, name
"@ -Silent
        
        $indexAnalysis.SkipIndexes = $skipIndexes
        
        # 主键使用分析
        $primaryKeys = Invoke-ClickHouseQuery @"
SELECT 
    database,
    table,
    sorting_key,
    primary_key,
    sampling_key
FROM system.tables
WHERE engine LIKE '%MergeTree%'
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
ORDER BY database, table
"@ -Silent
        
        $indexAnalysis.PrimaryKeys = $primaryKeys
        
    }
    catch {
        Write-Log "获取索引分析数据失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $indexAnalysis
}

# 获取内存分析数据
function Get-MemoryAnalysis {
    $memoryAnalysis = @{}
    
    try {
        # 内存使用统计
        $memoryUsage = Invoke-ClickHouseQuery @"
SELECT 
    formatReadableSize(value) as memory_usage,
    metric
FROM system.asynchronous_metrics
WHERE metric IN (
    'MemoryTracking',
    'MemoryCode',
    'MemoryDataAndStack',
    'MemoryResident',
    'MemoryVirtual',
    'MemoryShared'
)
"@ -Silent
        
        $memoryAnalysis.MemoryUsage = $memoryUsage
        
        # 缓存使用情况
        $cacheUsage = Invoke-ClickHouseQuery @"
SELECT 
    metric,
    formatReadableSize(value) as cache_size
FROM system.asynchronous_metrics
WHERE metric LIKE '%Cache%'
ORDER BY value DESC
"@ -Silent
        
        $memoryAnalysis.CacheUsage = $cacheUsage
        
        # 当前查询内存使用
        $queryMemory = Invoke-ClickHouseQuery @"
SELECT 
    query_id,
    user,
    formatReadableSize(memory_usage) as current_memory,
    formatReadableSize(peak_memory_usage) as peak_memory,
    elapsed
FROM system.processes
WHERE query != ''
ORDER BY memory_usage DESC
"@ -Silent
        
        $memoryAnalysis.QueryMemory = $queryMemory
        
    }
    catch {
        Write-Log "获取内存分析数据失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $memoryAnalysis
}

# 性能优化
function Start-PerformanceOptimization {
    Write-Log "开始性能优化..." "INFO"
    
    $optimizations = @()
    
    # 1. 检查表结构优化建议
    $optimizations += Get-TableOptimizationSuggestions
    
    # 2. 检查查询优化建议
    $optimizations += Get-QueryOptimizationSuggestions
    
    # 3. 检查配置优化建议
    $optimizations += Get-ConfigOptimizationSuggestions
    
    # 4. 检查索引优化建议
    $optimizations += Get-IndexOptimizationSuggestions
    
    # 输出优化建议
    foreach ($optimization in $optimizations) {
        Write-Log "优化建议: $($optimization.Description)" "INFO"
        if ($optimization.Severity -eq "HIGH") {
            Write-Log "  严重程度: 高" "WARN"
        }
        Write-Log "  建议操作: $($optimization.Recommendation)" "INFO"
        
        if ($AutoFix -and $optimization.AutoFixable) {
            Write-Log "  自动修复: $($optimization.AutoFixCommand)" "INFO"
            try {
                Invoke-ClickHouseQuery $optimization.AutoFixCommand -Silent
                Write-Log "  自动修复成功" "INFO"
            }
            catch {
                Write-Log "  自动修复失败: $($_.Exception.Message)" "ERROR"
            }
        }
    }
    
    # 保存优化建议
    $reportPath = Join-Path $OutputPath "optimization-suggestions-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $optimizations | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Log "优化建议保存至: $reportPath" "INFO"
}

# 获取表优化建议
function Get-TableOptimizationSuggestions {
    $suggestions = @()
    
    try {
        # 检查分区过多的表
        $partitionIssues = Invoke-ClickHouseQuery @"
SELECT 
    database,
    table,
    count() as partition_count
FROM system.parts
WHERE active = 1
GROUP BY database, table
HAVING count() > 1000
ORDER BY count() DESC
"@ -Silent
        
        if ($partitionIssues) {
            $suggestions += @{
                Type = "TABLE_STRUCTURE"
                Severity = "HIGH"
                Description = "发现分区过多的表，可能影响查询性能"
                Tables = $partitionIssues
                Recommendation = "考虑调整分区策略，减少分区数量"
                AutoFixable = $false
            }
        }
        
        # 检查小分区
        $smallPartitions = Invoke-ClickHouseQuery @"
SELECT 
    database,
    table,
    partition,
    formatReadableSize(sum(bytes_on_disk)) as partition_size,
    count() as parts_count
FROM system.parts
WHERE active = 1
    AND bytes_on_disk < 1048576  -- 小于1MB
GROUP BY database, table, partition
HAVING count() > 1
ORDER BY sum(bytes_on_disk)
LIMIT 20
"@ -Silent
        
        if ($smallPartitions) {
            $suggestions += @{
                Type = "PARTITION_SIZE"
                Severity = "MEDIUM"
                Description = "发现过小的分区，建议合并"
                Partitions = $smallPartitions
                Recommendation = "使用OPTIMIZE TABLE命令合并小分区"
                AutoFixable = $true
                AutoFixCommand = "OPTIMIZE TABLE {database}.{table} PARTITION '{partition}'"
            }
        }
        
    }
    catch {
        Write-Log "获取表优化建议失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $suggestions
}

# 获取查询优化建议
function Get-QueryOptimizationSuggestions {
    $suggestions = @()
    
    try {
        # 检查全表扫描查询
        $fullScanQueries = Invoke-ClickHouseQuery @"
SELECT 
    substring(query, 1, 200) as query_preview,
    avg(query_duration_ms) as avg_duration,
    count() as execution_count
FROM system.query_log
WHERE event_date >= today() - $Days
    AND type = 'QueryFinish'
    AND read_rows > 1000000  -- 读取行数超过100万
    AND query NOT LIKE '%system.%'
GROUP BY substring(query, 1, 200)
HAVING count() > 5
ORDER BY avg_duration DESC
LIMIT 10
"@ -Silent
        
        if ($fullScanQueries) {
            $suggestions += @{
                Type = "QUERY_PERFORMANCE"
                Severity = "HIGH"
                Description = "发现可能存在全表扫描的查询"
                Queries = $fullScanQueries
                Recommendation = "添加WHERE条件或优化索引"
                AutoFixable = $false
            }
        }
        
    }
    catch {
        Write-Log "获取查询优化建议失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $suggestions
}

# 获取配置优化建议
function Get-ConfigOptimizationSuggestions {
    $suggestions = @()
    
    try {
        # 检查内存配置
        $memoryConfig = Invoke-ClickHouseQuery "SELECT value FROM system.settings WHERE name = 'max_memory_usage'" -Silent
        
        if ([int64]$memoryConfig -eq 0) {
            $suggestions += @{
                Type = "MEMORY_CONFIG"
                Severity = "MEDIUM"
                Description = "未设置查询内存限制"
                Recommendation = "设置合适的max_memory_usage值"
                AutoFixable = $false
            }
        }
        
    }
    catch {
        Write-Log "获取配置优化建议失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $suggestions
}

# 获取索引优化建议
function Get-IndexOptimizationSuggestions {
    $suggestions = @()
    
    try {
        # 检查缺少索引的大表
        $largeTablesWithoutIndexes = Invoke-ClickHouseQuery @"
SELECT 
    t.database,
    t.table,
    formatReadableSize(p.total_bytes) as table_size
FROM system.tables t
JOIN (
    SELECT 
        database,
        table,
        sum(bytes_on_disk) as total_bytes
    FROM system.parts
    WHERE active = 1
    GROUP BY database, table
    HAVING sum(bytes_on_disk) > 1073741824  -- 大于1GB
) p ON t.database = p.database AND t.table = p.table
LEFT JOIN system.data_skipping_indices i ON t.database = i.database AND t.table = i.table
WHERE t.engine LIKE '%MergeTree%'
    AND i.name IS NULL
    AND t.database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
ORDER BY p.total_bytes DESC
LIMIT 10
"@ -Silent
        
        if ($largeTablesWithoutIndexes) {
            $suggestions += @{
                Type = "INDEX_MISSING"
                Severity = "MEDIUM"
                Description = "发现缺少跳数索引的大表"
                Tables = $largeTablesWithoutIndexes
                Recommendation = "考虑为常用查询字段添加跳数索引"
                AutoFixable = $false
            }
        }
        
    }
    catch {
        Write-Log "获取索引优化建议失败: $($_.Exception.Message)" "ERROR"
    }
    
    return $suggestions
}

# 性能监控
function Start-PerformanceMonitoring {
    Write-Log "开始性能监控..." "INFO"
    
    $monitoringInterval = 60  # 60秒间隔
    $maxIterations = 60       # 最多监控60次（1小时）
    
    for ($i = 0; $i -lt $maxIterations; $i++) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Log "[$timestamp] 监控迭代 $($i + 1)/$maxIterations" "INFO"
        
        try {
            # 收集关键指标
            $metrics = @{
                Timestamp = $timestamp
                RunningQueries = (Invoke-ClickHouseQuery "SELECT count() FROM system.processes WHERE query != ''" -Silent)
                MemoryUsage = (Invoke-ClickHouseQuery "SELECT formatReadableSize(value) FROM system.asynchronous_metrics WHERE metric = 'MemoryTracking'" -Silent)
                CPUUsage = (Invoke-ClickHouseQuery "SELECT value FROM system.asynchronous_metrics WHERE metric LIKE '%CPU%' LIMIT 1" -Silent)
                DiskUsage = (Invoke-ClickHouseQuery "SELECT formatReadableSize(sum(bytes_on_disk)) FROM system.parts WHERE active = 1" -Silent)
            }
            
            # 检查告警条件
            $runningQueries = [int]$metrics.RunningQueries
            if ($runningQueries -gt 50) {
                Write-Log "告警: 运行查询数过多 ($runningQueries)" "WARN"
            }
            
            # 记录指标
            $metricsJson = $metrics | ConvertTo-Json -Compress
            Add-Content -Path (Join-Path $OutputPath "monitoring-metrics.log") -Value $metricsJson
            
            Write-Log "运行查询: $($metrics.RunningQueries), 内存使用: $($metrics.MemoryUsage)" "DEBUG"
            
        }
        catch {
            Write-Log "监控数据收集失败: $($_.Exception.Message)" "ERROR"
        }
        
        if ($i -lt $maxIterations - 1) {
            Start-Sleep -Seconds $monitoringInterval
        }
    }
    
    Write-Log "性能监控完成" "INFO"
}

# 性能基准测试
function Start-PerformanceBenchmark {
    Write-Log "开始性能基准测试..." "INFO"
    
    $benchmarkResults = @{}
    
    try {
        # 1. 简单查询测试
        Write-Log "执行简单查询测试..." "INFO"
        $simpleQueryStart = Get-Date
        Invoke-ClickHouseQuery "SELECT count() FROM system.numbers LIMIT 1000000" -Silent | Out-Null
        $simpleQueryEnd = Get-Date
        $benchmarkResults.SimpleQuery = ($simpleQueryEnd - $simpleQueryStart).TotalMilliseconds
        
        # 2. 聚合查询测试
        Write-Log "执行聚合查询测试..." "INFO"
        $aggregateQueryStart = Get-Date
        Invoke-ClickHouseQuery "SELECT number % 1000 as group_key, count(), avg(number) FROM system.numbers LIMIT 10000000 GROUP BY group_key" -Silent | Out-Null
        $aggregateQueryEnd = Get-Date
        $benchmarkResults.AggregateQuery = ($aggregateQueryEnd - $aggregateQueryStart).TotalMilliseconds
        
        # 3. 写入性能测试
        Write-Log "执行写入性能测试..." "INFO"
        $insertStart = Get-Date
        Invoke-ClickHouseQuery "CREATE TABLE IF NOT EXISTS benchmark_test (id UInt64, value String) ENGINE = MergeTree() ORDER BY id" -Silent
        Invoke-ClickHouseQuery "INSERT INTO benchmark_test SELECT number, toString(number) FROM system.numbers LIMIT 1000000" -Silent
        $insertEnd = Get-Date
        $benchmarkResults.InsertQuery = ($insertEnd - $insertStart).TotalMilliseconds
        
        # 清理测试表
        Invoke-ClickHouseQuery "DROP TABLE IF EXISTS benchmark_test" -Silent
        
        # 输出结果
        Write-Log "基准测试结果:" "INFO"
        Write-Log "  简单查询: $($benchmarkResults.SimpleQuery) ms" "INFO"
        Write-Log "  聚合查询: $($benchmarkResults.AggregateQuery) ms" "INFO"
        Write-Log "  写入查询: $($benchmarkResults.InsertQuery) ms" "INFO"
        
        # 保存结果
        $reportPath = Join-Path $OutputPath "benchmark-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
        $benchmarkResults | ConvertTo-Json | Out-File -FilePath $reportPath -Encoding UTF8
        
    }
    catch {
        Write-Log "性能基准测试失败: $($_.Exception.Message)" "ERROR"
    }
}

# 生成性能报告
function New-PerformanceReport {
    Write-Log "生成性能报告..." "INFO"
    
    try {
        # 收集所有数据
        $analysis = Start-PerformanceAnalysis
        
        # 生成HTML报告
        $htmlReport = @"
<!DOCTYPE html>
<html>
<head>
    <title>ClickHouse性能报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .metric { margin: 5px 0; }
        .warning { color: red; font-weight: bold; }
        .info { color: blue; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ClickHouse性能分析报告</h1>
        <p>生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p>分析周期: 最近 $Days 天</p>
    </div>
    
    <div class="section">
        <h2>系统概览</h2>
        <div class="metric">连接数: $($analysis.SystemMetrics.Connections -join ', ')</div>
        <div class="metric">运行查询: $($analysis.SystemMetrics.RunningQueries.Count)</div>
    </div>
    
    <div class="section">
        <h2>查询性能统计</h2>
        <p>慢查询数量: $($analysis.QueryPerformance.SlowQueries.Count)</p>
        <p>错误查询数量: $($analysis.QueryPerformance.ErrorQueries.Count)</p>
    </div>
    
    <div class="section">
        <h2>表存储分析</h2>
        <p>最大表数量: $($analysis.TableAnalysis.TableSizes.Count)</p>
        <p>分区问题数量: $($analysis.TableAnalysis.PartitionAnalysis.Count)</p>
    </div>
    
    <div class="section">
        <h2>优化建议</h2>
        <p>建议定期检查慢查询并优化</p>
        <p>建议监控内存使用情况</p>
        <p>建议定期清理过期数据</p>
    </div>
</body>
</html>
"@
        
        $reportPath = Join-Path $OutputPath "performance-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"
        $htmlReport | Out-File -FilePath $reportPath -Encoding UTF8
        
        Write-Log "性能报告生成完成: $reportPath" "INFO"
        
        # 打开报告
        Start-Process $reportPath
        
    }
    catch {
        Write-Log "生成性能报告失败: $($_.Exception.Message)" "ERROR"
    }
}

# 清理优化
function Start-PerformanceCleanup {
    Write-Log "开始性能清理..." "INFO"
    
    try {
        # 1. 优化表
        $tables = Invoke-ClickHouseQuery @"
SELECT database, table
FROM system.tables
WHERE engine LIKE '%MergeTree%'
    AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')
"@ -Silent
        
        $tableList = $tables -split "`n" | Where-Object { $_ -ne "" }
        foreach ($tableInfo in $tableList) {
            $parts = $tableInfo -split "`t"
            if ($parts.Length -eq 2) {
                $database = $parts[0]
                $table = $parts[1]
                
                Write-Log "优化表: $database.$table" "INFO"
                try {
                    Invoke-ClickHouseQuery "OPTIMIZE TABLE $database.$table" -Silent
                }
                catch {
                    Write-Log "优化表失败: $database.$table - $($_.Exception.Message)" "WARN"
                }
            }
        }
        
        # 2. 清理系统表
        Write-Log "清理系统日志表..." "INFO"
        $systemTables = @("query_log", "query_thread_log", "part_log", "text_log")
        
        foreach ($table in $systemTables) {
            try {
                Invoke-ClickHouseQuery "ALTER TABLE system.$table DELETE WHERE event_date < today() - 30" -Silent
                Write-Log "清理系统表: $table" "INFO"
            }
            catch {
                Write-Log "清理系统表失败: $table - $($_.Exception.Message)" "WARN"
            }
        }
        
    }
    catch {
        Write-Log "性能清理失败: $($_.Exception.Message)" "ERROR"
    }
}

# 主执行函数
function Main {
    Write-Log "ClickHouse性能调优工具启动" "INFO"
    Write-Log "操作: $Action" "INFO"
    Write-Log "主机: $Host:$Port" "INFO"
    
    try {
        switch ($Action.ToLower()) {
            "analyze" {
                Start-PerformanceAnalysis
            }
            "optimize" {
                Start-PerformanceOptimization
            }
            "monitor" {
                Start-PerformanceMonitoring
            }
            "benchmark" {
                Start-PerformanceBenchmark
            }
            "report" {
                New-PerformanceReport
            }
            "cleanup" {
                Start-PerformanceCleanup
            }
            default {
                throw "不支持的操作: $Action"
            }
        }
        
        Write-Log "操作完成" "INFO"
    }
    catch {
        Write-Log "操作失败: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# 执行主函数
Main 