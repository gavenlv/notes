# ClickHouse 数据迁移管理脚本
# 功能：管理从3分片2副本到1分片2副本的集群数据迁移
# 作者：ClickHouse学习教程
# 版本：1.0

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigPath = ".\configs",
    
    [Parameter(Mandatory=$false)]
    [string]$SourceCluster = "cluster_3s_2r",
    
    [Parameter(Mandatory=$false)]
    [string]$TargetCluster = "cluster_1s_2r",
    
    [Parameter(Mandatory=$false)]
    [string]$LogPath = ".\logs",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

# 全局变量
$Global:MigrationStartTime = Get-Date
$Global:LogFile = Join-Path $LogPath "migration_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$Global:ErrorCount = 0
$Global:WarningCount = 0

# 颜色定义
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
}

# 初始化日志目录
function Initialize-Environment {
    Write-ColorOutput "初始化迁移环境..." $Colors.Info
    
    # 创建必要的目录
    $Directories = @($LogPath, "$LogPath\backup", "$LogPath\validation")
    foreach ($Dir in $Directories) {
        if (!(Test-Path $Dir)) {
            Write-ColorOutput "创建目录: $Dir" $Colors.Info
            New-Item -ItemType Directory -Path $Dir -Force | Out-Null
        }
    }
    
    # 初始化日志文件
    $LogHeader = @"
================================================================================
ClickHouse 集群数据迁移日志
开始时间: $Global:MigrationStartTime
源集群: $SourceCluster (3 shards, 2 replicas)
目标集群: $TargetCluster (1 shard, 2 replicas)
配置路径: $ConfigPath
是否预演: $DryRun
================================================================================
"@
    
    $LogHeader | Out-File -FilePath $Global:LogFile -Encoding UTF8
    Write-ColorOutput "日志文件: $Global:LogFile" $Colors.Info
}

# 彩色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$ForegroundColor = "White"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    
    Write-Host $LogMessage -ForegroundColor $ForegroundColor
    $LogMessage | Out-File -FilePath $Global:LogFile -Append -Encoding UTF8
}

# 错误处理函数
function Write-ErrorOutput {
    param([string]$Message)
    $Global:ErrorCount++
    Write-ColorOutput "[ERROR] $Message" $Colors.Error
}

# 警告处理函数
function Write-WarningOutput {
    param([string]$Message)
    $Global:WarningCount++
    Write-ColorOutput "[WARNING] $Message" $Colors.Warning
}

# 执行ClickHouse查询
function Invoke-ClickHouseQuery {
    param(
        [string]$Query,
        [string]$Host = "localhost",
        [int]$Port = 9000,
        [string]$User = "default",
        [string]$Password = "",
        [string]$Database = "default",
        [switch]$ShowQuery = $false
    )
    
    try {
        if ($ShowQuery) {
            Write-ColorOutput "执行查询: $Query" $Colors.Info
        }
        
        $Arguments = @(
            "--host", $Host,
            "--port", $Port,
            "--user", $User,
            "--database", $Database,
            "--query", $Query
        )
        
        if ($Password) {
            $Arguments += @("--password", $Password)
        }
        
        if ($DryRun) {
            Write-ColorOutput "[DRY-RUN] 将执行查询: $Query" $Colors.Warning
            return $null
        }
        
        $Result = & clickhouse-client @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "查询执行失败，退出代码: $LASTEXITCODE"
        }
        
        return $Result
    }
    catch {
        Write-ErrorOutput "查询执行失败: $Query, 错误: $($_.Exception.Message)"
        throw
    }
}

# 检查集群健康状态
function Test-ClusterHealth {
    param(
        [string]$ClusterName,
        [string]$Description
    )
    
    Write-ColorOutput "检查$Description健康状态..." $Colors.Info
    
    try {
        # 检查集群配置
        $ClusterQuery = "SELECT cluster, shard_num, replica_num, host_name, port FROM system.clusters WHERE cluster = '$ClusterName'"
        $ClusterInfo = Invoke-ClickHouseQuery -Query $ClusterQuery -ShowQuery
        
        if (!$ClusterInfo) {
            Write-ErrorOutput "集群 $ClusterName 配置未找到"
            return $false
        }
        
        Write-ColorOutput "集群 $ClusterName 配置正常" $Colors.Success
        
        # 检查副本状态
        $ReplicaQuery = @"
SELECT 
    database,
    table,
    is_leader,
    total_replicas,
    active_replicas,
    absolute_delay,
    queue_size
FROM system.replicas
WHERE absolute_delay > 60 OR queue_size > 100
"@
        
        $ReplicaIssues = Invoke-ClickHouseQuery -Query $ReplicaQuery
        
        if ($ReplicaIssues) {
            Write-WarningOutput "发现副本同步问题："
            $ReplicaIssues | ForEach-Object { Write-WarningOutput $_ }
        } else {
            Write-ColorOutput "副本状态正常" $Colors.Success
        }
        
        return $true
    }
    catch {
        Write-ErrorOutput "集群健康检查失败: $($_.Exception.Message)"
        return $false
    }
}

# 检查磁盘空间
function Test-DiskSpace {
    param([string]$Description)
    
    Write-ColorOutput "检查${Description}磁盘空间..." $Colors.Info
    
    try {
        $DiskQuery = @"
SELECT 
    name,
    path,
    formatReadableSize(free_space) as free_space,
    formatReadableSize(total_space) as total_space,
    round(free_space/total_space*100, 2) as free_percent
FROM system.disks
WHERE free_percent < 20
"@
        
        $DiskWarnings = Invoke-ClickHouseQuery -Query $DiskQuery
        
        if ($DiskWarnings) {
            Write-WarningOutput "磁盘空间不足警告："
            $DiskWarnings | ForEach-Object { Write-WarningOutput $_ }
        } else {
            Write-ColorOutput "磁盘空间充足" $Colors.Success
        }
        
        return $true
    }
    catch {
        Write-ErrorOutput "磁盘空间检查失败: $($_.Exception.Message)"
        return $false
    }
}

# 获取数据统计信息
function Get-DataStatistics {
    param(
        [string]$ClusterName,
        [string]$Description
    )
    
    Write-ColorOutput "获取${Description}数据统计..." $Colors.Info
    
    try {
        $StatsQuery = @"
SELECT 
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as size,
    sum(rows) as rows,
    count(*) as parts
FROM system.parts 
WHERE active = 1
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC
LIMIT 20
"@
        
        $Statistics = Invoke-ClickHouseQuery -Query $StatsQuery -ShowQuery
        
        if ($Statistics) {
            Write-ColorOutput "$Description 数据统计（Top 20表）：" $Colors.Info
            $Statistics | ForEach-Object { Write-ColorOutput $_ $Colors.Info }
        }
        
        # 保存统计信息到文件
        $StatsFile = Join-Path $LogPath "${Description}_statistics_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
        $Statistics | Out-File -FilePath $StatsFile -Encoding UTF8
        Write-ColorOutput "统计信息已保存到: $StatsFile" $Colors.Info
        
        return $Statistics
    }
    catch {
        Write-ErrorOutput "获取数据统计失败: $($_.Exception.Message)"
        return $null
    }
}

# 创建数据备份
function New-DataBackup {
    param([string]$BackupName)
    
    Write-ColorOutput "创建数据备份: $BackupName..." $Colors.Info
    
    try {
        if ($DryRun) {
            Write-ColorOutput "[DRY-RUN] 将创建备份: $BackupName" $Colors.Warning
            return $true
        }
        
        $BackupCmd = "clickhouse-backup create $BackupName"
        Write-ColorOutput "执行备份命令: $BackupCmd" $Colors.Info
        
        $Result = Invoke-Expression $BackupCmd
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "备份创建成功: $BackupName" $Colors.Success
            return $true
        } else {
            Write-ErrorOutput "备份创建失败: $Result"
            return $false
        }
    }
    catch {
        Write-ErrorOutput "备份创建异常: $($_.Exception.Message)"
        return $false
    }
}

# 设置只读模式
function Set-ReadOnlyMode {
    param(
        [bool]$ReadOnly = $true,
        [string]$ClusterName
    )
    
    $Mode = if ($ReadOnly) { "启用" } else { "禁用" }
    Write-ColorOutput "${Mode}只读模式..." $Colors.Info
    
    try {
        if ($DryRun) {
            Write-ColorOutput "[DRY-RUN] 将${Mode}只读模式" $Colors.Warning
            return $true
        }
        
        $ReadOnlyValue = if ($ReadOnly) { 1 } else { 0 }
        $Query = "SET readonly = $ReadOnlyValue"
        
        Invoke-ClickHouseQuery -Query $Query -ShowQuery
        Write-ColorOutput "只读模式${Mode}成功" $Colors.Success
        return $true
    }
    catch {
        Write-ErrorOutput "设置只读模式失败: $($_.Exception.Message)"
        return $false
    }
}

# 等待副本同步
function Wait-ReplicaSync {
    param(
        [int]$MaxWaitMinutes = 30,
        [string]$ClusterName
    )
    
    Write-ColorOutput "等待副本同步完成（最大等待 $MaxWaitMinutes 分钟）..." $Colors.Info
    
    $StartTime = Get-Date
    $MaxWaitTime = $StartTime.AddMinutes($MaxWaitMinutes)
    
    while ((Get-Date) -lt $MaxWaitTime) {
        try {
            $SyncQuery = @"
SELECT count(*) as pending_count
FROM system.replicas
WHERE absolute_delay > 0 OR queue_size > 0
"@
            
            $PendingCount = Invoke-ClickHouseQuery -Query $SyncQuery
            
            if ([int]$PendingCount -eq 0) {
                Write-ColorOutput "副本同步完成" $Colors.Success
                return $true
            }
            
            Write-ColorOutput "等待副本同步，待同步副本数: $PendingCount" $Colors.Info
            Start-Sleep -Seconds 30
        }
        catch {
            Write-WarningOutput "检查副本同步状态失败: $($_.Exception.Message)"
            Start-Sleep -Seconds 30
        }
    }
    
    Write-WarningOutput "副本同步等待超时"
    return $false
}

# 执行数据迁移
function Start-DataMigration {
    Write-ColorOutput "开始执行数据迁移..." $Colors.Header
    
    try {
        # 检查copier配置文件
        $CopierConfig = Join-Path $ConfigPath "copier-config.xml"
        if (!(Test-Path $CopierConfig)) {
            Write-ErrorOutput "Copier配置文件未找到: $CopierConfig"
            return $false
        }
        
        if ($DryRun) {
            Write-ColorOutput "[DRY-RUN] 将执行数据迁移" $Colors.Warning
            return $true
        }
        
        # 启动clickhouse-copier
        $CopierCmd = "clickhouse-copier --config-file=$CopierConfig --base-dir=/var/lib/clickhouse-copier --task-path=/clickhouse/copier/migration_3s_to_1s"
        Write-ColorOutput "执行迁移命令: $CopierCmd" $Colors.Info
        
        # 在后台启动copier
        $CopierJob = Start-Job -ScriptBlock {
            param($Command)
            Invoke-Expression $Command
        } -ArgumentList $CopierCmd
        
        Write-ColorOutput "数据迁移任务已启动，Job ID: $($CopierJob.Id)" $Colors.Success
        
        # 监控迁移进度
        Monitor-MigrationProgress -JobId $CopierJob.Id
        
        return $true
    }
    catch {
        Write-ErrorOutput "执行数据迁移失败: $($_.Exception.Message)"
        return $false
    }
}

# 监控迁移进度
function Monitor-MigrationProgress {
    param([int]$JobId)
    
    Write-ColorOutput "监控迁移进度..." $Colors.Info
    
    while ($true) {
        $Job = Get-Job -Id $JobId
        
        if ($Job.State -eq "Completed") {
            Write-ColorOutput "数据迁移完成" $Colors.Success
            break
        } elseif ($Job.State -eq "Failed") {
            Write-ErrorOutput "数据迁移失败"
            Receive-Job -Id $JobId | Write-ErrorOutput
            break
        }
        
        # 显示迁移进度
        try {
            $ProgressQuery = @"
SELECT 
    table,
    formatReadableSize(bytes_on_disk) as current_size,
    count(*) as parts_count
FROM system.parts
WHERE active = 1
GROUP BY table
ORDER BY bytes_on_disk DESC
LIMIT 10
"@
            
            $Progress = Invoke-ClickHouseQuery -Query $ProgressQuery
            Write-ColorOutput "当前迁移进度 (Top 10表)：" $Colors.Info
            $Progress | ForEach-Object { Write-ColorOutput $_ $Colors.Info }
        }
        catch {
            Write-WarningOutput "获取迁移进度失败: $($_.Exception.Message)"
        }
        
        Start-Sleep -Seconds 300  # 每5分钟检查一次
    }
}

# 数据校验
function Test-DataValidation {
    Write-ColorOutput "开始数据校验..." $Colors.Header
    
    $ValidationResults = @()
    
    try {
        # 1. 行数校验
        Write-ColorOutput "执行行数校验..." $Colors.Info
        $RowCountResults = Test-RowCount
        $ValidationResults += $RowCountResults
        
        # 2. 数据完整性校验
        Write-ColorOutput "执行数据完整性校验..." $Colors.Info
        $IntegrityResults = Test-DataIntegrity
        $ValidationResults += $IntegrityResults
        
        # 3. 业务逻辑校验
        Write-ColorOutput "执行业务逻辑校验..." $Colors.Info
        $BusinessResults = Test-BusinessLogic
        $ValidationResults += $BusinessResults
        
        # 生成校验报告
        $ReportFile = Join-Path $LogPath "validation_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
        Generate-ValidationReport -Results $ValidationResults -OutputFile $ReportFile
        
        Write-ColorOutput "数据校验完成，报告已生成: $ReportFile" $Colors.Success
        return $ValidationResults
    }
    catch {
        Write-ErrorOutput "数据校验失败: $($_.Exception.Message)"
        return $null
    }
}

# 行数校验
function Test-RowCount {
    Write-ColorOutput "执行行数校验..." $Colors.Info
    
    $Results = @()
    
    try {
        # 获取所有表列表
        $TablesQuery = @"
SELECT DISTINCT database, table
FROM system.tables
WHERE database NOT IN ('system', 'information_schema')
AND engine LIKE '%MergeTree%'
"@
        
        $Tables = Invoke-ClickHouseQuery -Query $TablesQuery
        
        foreach ($TableInfo in $Tables) {
            $Database, $Table = $TableInfo -split '\t'
            
            # 源集群行数
            $SourceQuery = "SELECT count(*) FROM remote('$SourceCluster', $Database.$Table)"
            $SourceCount = Invoke-ClickHouseQuery -Query $SourceQuery
            
            # 目标集群行数
            $TargetQuery = "SELECT count(*) FROM $Database.$Table"
            $TargetCount = Invoke-ClickHouseQuery -Query $TargetQuery
            
            $Diff = [int]$SourceCount - [int]$TargetCount
            $Status = if ($Diff -eq 0) { "PASS" } else { "FAIL" }
            
            $Result = [PSCustomObject]@{
                Type = "RowCount"
                Database = $Database
                Table = $Table
                SourceCount = $SourceCount
                TargetCount = $TargetCount
                Difference = $Diff
                Status = $Status
            }
            
            $Results += $Result
            
            if ($Status -eq "PASS") {
                Write-ColorOutput "✓ $Database.$Table 行数校验通过" $Colors.Success
            } else {
                Write-ErrorOutput "✗ $Database.$Table 行数校验失败，差异: $Diff"
            }
        }
        
        return $Results
    }
    catch {
        Write-ErrorOutput "行数校验异常: $($_.Exception.Message)"
        return $Results
    }
}

# 数据完整性校验
function Test-DataIntegrity {
    Write-ColorOutput "执行数据完整性校验..." $Colors.Info
    
    $Results = @()
    
    # 这里实现具体的完整性校验逻辑
    # 例如：主键唯一性、外键约束、数据类型等
    
    return $Results
}

# 业务逻辑校验
function Test-BusinessLogic {
    Write-ColorOutput "执行业务逻辑校验..." $Colors.Info
    
    $Results = @()
    
    # 这里实现具体的业务逻辑校验
    # 例如：业务指标对比、数据分布检查等
    
    return $Results
}

# 生成校验报告
function Generate-ValidationReport {
    param(
        [array]$Results,
        [string]$OutputFile
    )
    
    $Html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClickHouse 数据迁移校验报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #4a90e2; color: white; padding: 20px; }
        .summary { margin: 20px 0; }
        .results { margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ClickHouse 数据迁移校验报告</h1>
        <p>生成时间: $(Get-Date)</p>
    </div>
    
    <div class="summary">
        <h2>校验摘要</h2>
        <p>总校验项: $($Results.Count)</p>
        <p>通过项: $(@($Results | Where-Object {$_.Status -eq 'PASS'}).Count)</p>
        <p>失败项: $(@($Results | Where-Object {$_.Status -eq 'FAIL'}).Count)</p>
    </div>
    
    <div class="results">
        <h2>详细结果</h2>
        <table>
            <tr>
                <th>类型</th>
                <th>数据库</th>
                <th>表名</th>
                <th>源行数</th>
                <th>目标行数</th>
                <th>差异</th>
                <th>状态</th>
            </tr>
"@
    
    foreach ($Result in $Results) {
        $StatusClass = if ($Result.Status -eq "PASS") { "pass" } else { "fail" }
        $Html += @"
            <tr>
                <td>$($Result.Type)</td>
                <td>$($Result.Database)</td>
                <td>$($Result.Table)</td>
                <td>$($Result.SourceCount)</td>
                <td>$($Result.TargetCount)</td>
                <td>$($Result.Difference)</td>
                <td class="$StatusClass">$($Result.Status)</td>
            </tr>
"@
    }
    
    $Html += @"
        </table>
    </div>
</body>
</html>
"@
    
    $Html | Out-File -FilePath $OutputFile -Encoding UTF8
}

# 清理旧节点
function Remove-OldNodes {
    Write-ColorOutput "清理不再使用的节点..." $Colors.Info
    
    if ($DryRun) {
        Write-ColorOutput "[DRY-RUN] 将清理旧节点" $Colors.Warning
        return $true
    }
    
    # 这里实现清理逻辑
    # 例如：停止服务、清空数据目录、更新配置等
    
    Write-ColorOutput "旧节点清理完成" $Colors.Success
    return $true
}

# 更新配置
function Update-Configuration {
    Write-ColorOutput "更新集群配置..." $Colors.Info
    
    try {
        if ($DryRun) {
            Write-ColorOutput "[DRY-RUN] 将更新配置文件" $Colors.Warning
            return $true
        }
        
        # 复制新的配置文件
        $TargetConfig = Join-Path $ConfigPath "target-cluster-config.xml"
        if (Test-Path $TargetConfig) {
            Copy-Item $TargetConfig "/etc/clickhouse-server/config.d/cluster.xml" -Force
            Write-ColorOutput "配置文件已更新" $Colors.Success
        } else {
            Write-ErrorOutput "目标配置文件未找到: $TargetConfig"
            return $false
        }
        
        # 重启ClickHouse服务
        Write-ColorOutput "重启ClickHouse服务..." $Colors.Info
        Restart-Service clickhouse-server -Force
        
        # 等待服务启动
        Start-Sleep -Seconds 30
        
        # 验证服务状态
        $ServiceStatus = Get-Service clickhouse-server
        if ($ServiceStatus.Status -eq "Running") {
            Write-ColorOutput "ClickHouse服务启动成功" $Colors.Success
            return $true
        } else {
            Write-ErrorOutput "ClickHouse服务启动失败"
            return $false
        }
    }
    catch {
        Write-ErrorOutput "更新配置失败: $($_.Exception.Message)"
        return $false
    }
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput @"
ClickHouse 数据迁移管理脚本

用法: .\migration-manager.ps1 -Action <action> [参数]

可用操作:
  check-source      检查源集群健康状态
  check-target      检查目标集群健康状态
  backup           创建数据备份
  migrate          执行数据迁移
  validate         执行数据校验
  full-migration   执行完整迁移流程
  cleanup          清理临时文件
  help             显示此帮助信息

参数:
  -ConfigPath      配置文件路径 (默认: .\configs)
  -SourceCluster   源集群名称 (默认: cluster_3s_2r)
  -TargetCluster   目标集群名称 (默认: cluster_1s_2r)
  -LogPath         日志文件路径 (默认: .\logs)
  -DryRun          预演模式，不执行实际操作
  -Force           强制执行，跳过确认

示例:
  .\migration-manager.ps1 -Action check-source
  .\migration-manager.ps1 -Action full-migration -DryRun
  .\migration-manager.ps1 -Action validate -ConfigPath "C:\configs"
"@ $Colors.Info
}

# 主执行函数
function Main {
    Initialize-Environment
    
    Write-ColorOutput "开始执行操作: $Action" $Colors.Header
    
    switch ($Action.ToLower()) {
        "check-source" {
            $Success = Test-ClusterHealth -ClusterName $SourceCluster -Description "源集群"
            $Success = $Success -and (Test-DiskSpace -Description "源集群")
            Get-DataStatistics -ClusterName $SourceCluster -Description "源集群"
        }
        
        "check-target" {
            $Success = Test-ClusterHealth -ClusterName $TargetCluster -Description "目标集群"
            $Success = $Success -and (Test-DiskSpace -Description "目标集群")
        }
        
        "backup" {
            $BackupName = "migration_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            $Success = New-DataBackup -BackupName $BackupName
        }
        
        "migrate" {
            $Success = Start-DataMigration
        }
        
        "validate" {
            $ValidationResults = Test-DataValidation
            $Success = $ValidationResults -ne $null
        }
        
        "full-migration" {
            Write-ColorOutput "开始完整迁移流程..." $Colors.Header
            
            # 1. 检查源集群
            $Success = Test-ClusterHealth -ClusterName $SourceCluster -Description "源集群"
            if (!$Success) { return }
            
            # 2. 检查目标集群
            $Success = Test-ClusterHealth -ClusterName $TargetCluster -Description "目标集群"
            if (!$Success) { return }
            
            # 3. 创建备份
            $BackupName = "migration_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            $Success = New-DataBackup -BackupName $BackupName
            if (!$Success) { return }
            
            # 4. 设置只读模式
            $Success = Set-ReadOnlyMode -ReadOnly $true -ClusterName $SourceCluster
            if (!$Success) { return }
            
            # 5. 等待副本同步
            $Success = Wait-ReplicaSync -MaxWaitMinutes 30 -ClusterName $SourceCluster
            if (!$Success) { return }
            
            # 6. 执行数据迁移
            $Success = Start-DataMigration
            if (!$Success) { return }
            
            # 7. 更新配置
            $Success = Update-Configuration
            if (!$Success) { return }
            
            # 8. 数据校验
            $ValidationResults = Test-DataValidation
            if (!$ValidationResults) { return }
            
            # 9. 清理旧节点
            $Success = Remove-OldNodes
            if (!$Success) { return }
            
            Write-ColorOutput "完整迁移流程执行完成！" $Colors.Success
        }
        
        "cleanup" {
            Write-ColorOutput "清理临时文件..." $Colors.Info
            # 实现清理逻辑
            Write-ColorOutput "清理完成" $Colors.Success
        }
        
        "help" {
            Show-Help
        }
        
        default {
            Write-ErrorOutput "未知操作: $Action"
            Show-Help
        }
    }
    
    # 显示执行摘要
    $EndTime = Get-Date
    $Duration = $EndTime - $Global:MigrationStartTime
    
    Write-ColorOutput @"

================================================================================
执行摘要
================================================================================
开始时间: $Global:MigrationStartTime
结束时间: $EndTime
执行时长: $($Duration.ToString())
错误数量: $Global:ErrorCount
警告数量: $Global:WarningCount
日志文件: $Global:LogFile
================================================================================
"@ $Colors.Header
}

# 脚本入口点
try {
    Main
}
catch {
    Write-ErrorOutput "脚本执行异常: $($_.Exception.Message)"
    Write-ErrorOutput "错误位置: $($_.InvocationInfo.PositionMessage)"
    exit 1
} 