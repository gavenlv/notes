# ClickHouse 集群管理脚本 - 简化版
# Day 8: 集群管理和分布式
# =====================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$Host = "localhost",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8123
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
    param([string]$Query)
    
    try {
        $uri = "http://$($Host):$($Port)/"
        $body = "query=" + [System.Web.HttpUtility]::UrlEncode($Query)
        
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
    
    $query = "SELECT cluster, shard_num, replica_num, host_name, port FROM system.clusters ORDER BY cluster, shard_num, replica_num"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "无法获取集群状态" "Yellow"
    }
}

# 检查副本状态
function Check-ReplicaStatus {
    Write-ColorOutput "🔄 检查副本状态..." "Cyan"
    
    $query = "SELECT database, table, replica_name, is_leader, absolute_delay, queue_size FROM system.replicas LIMIT 10"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "无副本表或无法访问副本信息" "Yellow"
    }
}

# 检查分布式表
function Check-DistributedTables {
    Write-ColorOutput "📊 检查分布式表..." "Cyan"
    
    $query = "SELECT database, name, engine FROM system.tables WHERE engine LIKE '%Distributed%'"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "未找到分布式表" "Yellow"
    }
}

# 显示基本信息
function Show-BasicInfo {
    Write-ColorOutput "ℹ️ 基本信息..." "Cyan"
    
    $query = "SELECT version() as clickhouse_version, hostName() as hostname"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    }
}

# 执行健康检查
function Run-HealthCheck {
    Write-ColorOutput "🏥 执行集群健康检查..." "Yellow"
    Write-ColorOutput "=" * 50 "Yellow"
    
    Show-BasicInfo
    Write-ColorOutput ""
    
    Check-ClusterStatus
    Write-ColorOutput ""
    
    Check-ReplicaStatus
    Write-ColorOutput ""
    
    Check-DistributedTables
    
    Write-ColorOutput "=" * 50 "Yellow"
    Write-ColorOutput "✅ 健康检查完成" "Green"
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput "ClickHouse 集群管理脚本 - 简化版" "Yellow"
    Write-ColorOutput "=" * 45 "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "用法: .\cluster-management-simple.ps1 -Action <action> [参数]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "可用操作:" "Cyan"
    Write-ColorOutput "  health      - 执行完整健康检查" "White"
    Write-ColorOutput "  status      - 检查集群状态" "White"
    Write-ColorOutput "  replicas    - 检查副本状态" "White"
    Write-ColorOutput "  tables      - 检查分布式表" "White"
    Write-ColorOutput "  info        - 显示基本信息" "White"
    Write-ColorOutput "  help        - 显示此帮助信息" "White"
    Write-ColorOutput ""
    Write-ColorOutput "参数:" "Cyan"
    Write-ColorOutput "  -Host       - ClickHouse主机 (默认: localhost)" "White"
    Write-ColorOutput "  -Port       - ClickHouse端口 (默认: 8123)" "White"
    Write-ColorOutput ""
    Write-ColorOutput "示例:" "Cyan"
    Write-ColorOutput "  .\cluster-management-simple.ps1 -Action health" "White"
    Write-ColorOutput "  .\cluster-management-simple.ps1 -Action status -Host 192.168.1.100" "White"
}

# 主程序逻辑
function Main {
    Write-ColorOutput "🚀 ClickHouse 集群管理工具 (简化版)" "Magenta"
    Write-ColorOutput "连接到: $($Host):$($Port)" "Gray"
    Write-ColorOutput ""
    
    switch ($Action.ToLower()) {
        "health" { Run-HealthCheck }
        "status" { Check-ClusterStatus }
        "replicas" { Check-ReplicaStatus }
        "tables" { Check-DistributedTables }
        "info" { Show-BasicInfo }
        "help" { Show-Help }
        default { 
            Write-ColorOutput "未知操作: $Action" "Red"
            Show-Help 
        }
    }
}

# 执行主程序
try {
    # 加载System.Web程序集用于URL编码
    Add-Type -AssemblyName System.Web
    
    Main
}
catch {
    Write-ColorOutput "脚本执行出错: $($_.Exception.Message)" "Red"
    Write-ColorOutput "请检查ClickHouse连接和参数设置" "Yellow"
}

Write-ColorOutput ""
Write-ColorOutput "脚本执行完成" "Green" 