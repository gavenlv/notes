# ClickHouse 监控检查脚本
# Day 9: 监控和运维
# =============================================

param(
    [string]$ClickHouseHost = "localhost",
    [int]$ClickHousePort = 8123,
    [string]$AlertWebhook = "",
    [string]$LogFile = "monitoring.log",
    [switch]$Verbose
)

# 初始化
$script:alertCount = 0
$script:checkResults = @()

# 记录日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Output $logEntry
    $logEntry | Out-File -FilePath $LogFile -Append
}

# 发送告警函数
function Send-Alert {
    param(
        [string]$Severity,
        [string]$Title,
        [string]$Message
    )
    
    $script:alertCount++
    Write-Log "ALERT [$Severity] $Title`: $Message" "ALERT"
    
    if ($AlertWebhook) {
        try {
            $alertData = @{
                severity = $Severity
                title = $Title
                message = $Message
                timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
                source = "ClickHouse-Monitor"
            } | ConvertTo-Json
            
            Invoke-RestMethod -Uri $AlertWebhook -Method Post -Body $alertData -ContentType "application/json"
            Write-Log "Alert sent to webhook: $AlertWebhook"
        }
        catch {
            Write-Log "Failed to send alert to webhook: $($_.Exception.Message)" "ERROR"
        }
    }
}

# 执行ClickHouse查询
function Invoke-ClickHouseQuery {
    param([string]$Query)
    
    try {
                 $uri = "http://${ClickHouseHost}`:${ClickHousePort}/"
         $response = Invoke-RestMethod -Uri $uri -Method Post -Body $Query -TimeoutSec 30
        return $response
    }
    catch {
        Write-Log "Query failed: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# 检查服务状态
function Test-ServiceStatus {
    Write-Log "检查ClickHouse服务状态..."
    
         try {
         $uri = "http://${ClickHouseHost}`:${ClickHousePort}/"
         $response = Invoke-WebRequest -Uri $uri -TimeoutSec 10
        
        if ($response.StatusCode -eq 200) {
            Write-Log "✅ ClickHouse服务正常运行"
            $script:checkResults += @{
                Check = "Service Status"
                Status = "OK"
                Value = "Running"
                Message = "Service is healthy"
            }
            return $true
        }
        else {
            Send-Alert "CRITICAL" "Service Down" "ClickHouse服务响应异常: $($response.StatusCode)"
            return $false
        }
    }
    catch {
        Send-Alert "CRITICAL" "Service Down" "ClickHouse服务不可访问: $($_.Exception.Message)"
        $script:checkResults += @{
            Check = "Service Status"
            Status = "CRITICAL"
            Value = "Down"
            Message = $_.Exception.Message
        }
        return $false
    }
}

# 检查查询性能
function Test-QueryPerformance {
    Write-Log "检查查询性能..."
    
    $query = @"
SELECT 
    quantile(0.95)(query_duration_ms) as p95_duration,
    count() as query_count,
    countIf(query_duration_ms > 10000) as slow_queries
FROM system.query_log 
WHERE event_time >= now() - INTERVAL 5 MINUTE
  AND type = 'QueryFinish'
"@
    
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        $lines = $result -split "`n"
        if ($lines.Count -gt 0) {
            $values = $lines[0] -split "`t"
            if ($values.Count -ge 3) {
                $p95Duration = [double]$values[0]
                $queryCount = [int]$values[1]
                $slowQueries = [int]$values[2]
                
                Write-Log "📊 查询性能: P95=$p95Duration ms, 总查询=$queryCount, 慢查询=$slowQueries"
                
                $script:checkResults += @{
                    Check = "Query Performance"
                    Status = if ($p95Duration -gt 10000) { "WARNING" } else { "OK" }
                    Value = "$p95Duration ms"
                    Message = "P95 duration: $p95Duration ms, Slow queries: $slowQueries"
                }
                
                if ($p95Duration -gt 10000) {
                    Send-Alert "WARNING" "High Query Duration" "P95查询时间过长: $p95Duration ms"
                }
                
                if ($slowQueries -gt 5) {
                    Send-Alert "WARNING" "Too Many Slow Queries" "慢查询过多: $slowQueries 个"
                }
            }
        }
    }
}

# 检查错误率
function Test-ErrorRate {
    Write-Log "检查错误率..."
    
    $query = @"
SELECT 
    count() as total_queries,
    countIf(type = 'ExceptionWhileProcessing') as error_count,
    if(count() > 0, countIf(type = 'ExceptionWhileProcessing') * 100.0 / count(), 0) as error_rate
FROM system.query_log 
WHERE event_time >= now() - INTERVAL 5 MINUTE
"@
    
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        $lines = $result -split "`n"
        if ($lines.Count -gt 0) {
            $values = $lines[0] -split "`t"
            if ($values.Count -ge 3) {
                $totalQueries = [int]$values[0]
                $errorCount = [int]$values[1]
                $errorRate = [double]$values[2]
                
                Write-Log "🚨 错误监控: 总查询=$totalQueries, 错误=$errorCount, 错误率=$errorRate%"
                
                $script:checkResults += @{
                    Check = "Error Rate"
                    Status = if ($errorRate -gt 5) { "CRITICAL" } elseif ($errorRate -gt 2) { "WARNING" } else { "OK" }
                    Value = "$errorRate%"
                    Message = "Error rate: $errorRate% ($errorCount/$totalQueries)"
                }
                
                if ($errorRate -gt 5) {
                    Send-Alert "CRITICAL" "High Error Rate" "错误率过高: $errorRate%"
                }
                elseif ($errorRate -gt 2) {
                    Send-Alert "WARNING" "Elevated Error Rate" "错误率升高: $errorRate%"
                }
            }
        }
    }
}

# 检查资源使用情况
function Test-ResourceUsage {
    Write-Log "检查资源使用情况..."
    
    # 检查内存使用
    $memoryQuery = @"
SELECT 
    formatReadableSize(total_memory) as total_memory,
    formatReadableSize(free_memory) as free_memory,
    round((total_memory - free_memory) * 100.0 / total_memory, 2) as memory_usage_percent
FROM (
    SELECT 
        value as total_memory
    FROM system.asynchronous_metrics 
    WHERE metric = 'MemoryTotal'
) 
CROSS JOIN (
    SELECT 
        value as free_memory
    FROM system.asynchronous_metrics 
    WHERE metric = 'MemoryAvailable'
)
"@
    
    $result = Invoke-ClickHouseQuery -Query $memoryQuery
    
    if ($result) {
        $lines = $result -split "`n"
        if ($lines.Count -gt 0) {
            $values = $lines[0] -split "`t"
            if ($values.Count -ge 3) {
                $totalMemory = $values[0]
                $freeMemory = $values[1]
                $memoryUsage = [double]$values[2]
                
                Write-Log "💾 内存使用: $memoryUsage% ($totalMemory 总内存, $freeMemory 可用)"
                
                $script:checkResults += @{
                    Check = "Memory Usage"
                    Status = if ($memoryUsage -gt 90) { "CRITICAL" } elseif ($memoryUsage -gt 80) { "WARNING" } else { "OK" }
                    Value = "$memoryUsage%"
                    Message = "Memory usage: $memoryUsage% ($freeMemory available)"
                }
                
                if ($memoryUsage -gt 90) {
                    Send-Alert "CRITICAL" "High Memory Usage" "内存使用率过高: $memoryUsage%"
                }
                elseif ($memoryUsage -gt 80) {
                    Send-Alert "WARNING" "Elevated Memory Usage" "内存使用率较高: $memoryUsage%"
                }
            }
        }
    }
    
    # 检查活跃连接
    $connectionQuery = @"
SELECT 
    count() as active_connections,
    uniq(user) as unique_users
FROM system.processes 
WHERE query != ''
"@
    
    $result = Invoke-ClickHouseQuery -Query $connectionQuery
    
    if ($result) {
        $lines = $result -split "`n"
        if ($lines.Count -gt 0) {
            $values = $lines[0] -split "`t"
            if ($values.Count -ge 2) {
                $activeConnections = [int]$values[0]
                $uniqueUsers = [int]$values[1]
                
                Write-Log "🔗 连接状态: $activeConnections 个活跃连接, $uniqueUsers 个用户"
                
                $script:checkResults += @{
                    Check = "Active Connections"
                    Status = if ($activeConnections -gt 100) { "WARNING" } else { "OK" }
                    Value = $activeConnections
                    Message = "$activeConnections active connections from $uniqueUsers users"
                }
                
                if ($activeConnections -gt 100) {
                    Send-Alert "WARNING" "High Connection Count" "活跃连接过多: $activeConnections"
                }
            }
        }
    }
}

# 检查存储使用情况
function Test-StorageUsage {
    Write-Log "检查存储使用情况..."
    
    $storageQuery = @"
SELECT 
    database,
    formatReadableSize(sum(data_compressed_bytes)) as total_size,
    sum(rows) as total_rows
FROM system.parts 
WHERE active = 1
  AND database NOT IN ('system', '_temporary_and_external_tables')
GROUP BY database
ORDER BY sum(data_compressed_bytes) DESC
LIMIT 10
"@
    
    $result = Invoke-ClickHouseQuery -Query $storageQuery
    
    if ($result) {
        Write-Log "📁 存储使用情况 (Top 10数据库):"
        $lines = $result -split "`n"
        foreach ($line in $lines) {
            if ($line.Trim()) {
                $values = $line -split "`t"
                if ($values.Count -ge 3) {
                    Write-Log "  - $($values[0]): $($values[1]) ($($values[2]) 行)"
                }
            }
        }
        
        $script:checkResults += @{
            Check = "Storage Usage"
            Status = "OK"
            Value = "Checked"
            Message = "Storage usage checked for top databases"
        }
    }
}

# 检查副本状态（如果使用副本）
function Test-ReplicationStatus {
    Write-Log "检查副本状态..."
    
    $replicaQuery = @"
SELECT 
    database,
    table,
    is_leader,
    absolute_delay,
    queue_size
FROM system.replicas
WHERE is_readonly = 0
"@
    
    $result = Invoke-ClickHouseQuery -Query $replicaQuery
    
    if ($result) {
        $lines = $result -split "`n"
        $replicaCount = 0
        
        foreach ($line in $lines) {
            if ($line.Trim()) {
                $replicaCount++
                $values = $line -split "`t"
                if ($values.Count -ge 5) {
                    $database = $values[0]
                    $table = $values[1]
                    $isLeader = $values[2]
                    $delay = [int]$values[3]
                    $queueSize = [int]$values[4]
                    
                    Write-Log "📋 副本: $database.$table, Leader=$isLeader, Delay=${delay}s, Queue=$queueSize"
                    
                    if ($delay -gt 300) {
                        Send-Alert "WARNING" "Replica Lag" "副本延迟过高: $database.$table 延迟 ${delay}s"
                    }
                    
                    if ($queueSize -gt 100) {
                        Send-Alert "WARNING" "Large Replica Queue" "副本队列过大: $database.$table 队列 $queueSize"
                    }
                }
            }
        }
        
        if ($replicaCount -gt 0) {
            $script:checkResults += @{
                Check = "Replication Status"
                Status = "OK"
                Value = "$replicaCount replicas"
                Message = "Checked $replicaCount replica tables"
            }
        } else {
            Write-Log "ℹ️ 未检测到副本表"
        }
    }
}

# 生成监控报告
function Write-MonitoringReport {
    Write-Log "=== ClickHouse 监控报告 ==="
    Write-Log "检查时间: $(Get-Date)"
    Write-Log "目标服务器: $ClickHouseHost:$ClickHousePort"
    Write-Log ""
    
    $criticalCount = ($script:checkResults | Where-Object { $_.Status -eq "CRITICAL" }).Count
    $warningCount = ($script:checkResults | Where-Object { $_.Status -eq "WARNING" }).Count
    $okCount = ($script:checkResults | Where-Object { $_.Status -eq "OK" }).Count
    
    Write-Log "📊 检查结果汇总:"
    Write-Log "  ✅ 正常: $okCount"
    Write-Log "  ⚠️ 警告: $warningCount"
    Write-Log "  🚨 严重: $criticalCount"
    Write-Log "  📢 告警数量: $script:alertCount"
    Write-Log ""
    
    Write-Log "📋 详细结果:"
    foreach ($result in $script:checkResults) {
        $icon = switch ($result.Status) {
            "OK" { "✅" }
            "WARNING" { "⚠️" }
            "CRITICAL" { "🚨" }
            default { "ℹ️" }
        }
        Write-Log "  $icon $($result.Check): $($result.Status) - $($result.Value)"
        if ($Verbose) {
            Write-Log "     $($result.Message)"
        }
    }
    
    # 整体健康状态
    $overallStatus = if ($criticalCount -gt 0) {
        "CRITICAL"
    } elseif ($warningCount -gt 0) {
        "WARNING" 
    } else {
        "HEALTHY"
    }
    
    Write-Log ""
    Write-Log "🏥 整体健康状态: $overallStatus"
    
    return $overallStatus
}

# 主函数
function Main {
    Write-Log "🚀 开始ClickHouse健康检查..."
    Write-Log "目标: $ClickHouseHost:$ClickHousePort"
    
    # 检查服务状态
    if (-not (Test-ServiceStatus)) {
        Write-Log "❌ 服务不可用，跳过其他检查"
        Write-MonitoringReport
        exit 1
    }
    
    # 执行各项检查
    Test-QueryPerformance
    Test-ErrorRate
    Test-ResourceUsage
    Test-StorageUsage
    Test-ReplicationStatus
    
    # 生成报告
    $status = Write-MonitoringReport
    
    Write-Log "✨ 监控检查完成"
    
    # 根据状态设置退出码
    switch ($status) {
        "HEALTHY" { exit 0 }
        "WARNING" { exit 1 }
        "CRITICAL" { exit 2 }
        default { exit 3 }
    }
}

# 执行主函数
try {
    Main
}
catch {
    Write-Log "💥 监控脚本执行失败: $($_.Exception.Message)" "ERROR"
    Send-Alert "CRITICAL" "Monitor Script Failed" "监控脚本执行失败: $($_.Exception.Message)"
    exit 4
} 