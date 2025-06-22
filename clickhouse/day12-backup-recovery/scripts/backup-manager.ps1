# ClickHouse Day 12: 备份恢复管理脚本
# PowerShell脚本用于ClickHouse备份、恢复和版本升级管理

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("backup", "restore", "monitor", "upgrade", "cleanup", "disaster-recovery", "test")]
    [string]$Action,
    
    [string]$Host = "localhost",
    [int]$Port = 9000,
    [string]$Username = "default",
    [string]$Password = "",
    [string]$Database = "",
    [string]$BackupPath = "D:\ClickHouse\Backups",
    [string]$ConfigPath = "D:\ClickHouse\Config",
    [string]$LogPath = "D:\ClickHouse\Logs",
    [int]$RetentionDays = 30,
    [switch]$Verbose,
    [switch]$DryRun
)

# 全局变量
$script:LogFile = Join-Path $LogPath "backup-manager-$(Get-Date -Format 'yyyyMMdd').log"
$script:ConnectionString = "clickhouse-client --host=$Host --port=$Port --user=$Username"
if ($Password) { $script:ConnectionString += " --password=$Password" }

# 确保目录存在
@($BackupPath, $LogPath) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
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
    
    # 输出到控制台
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
        "DEBUG" { if ($Verbose) { Write-Host $logMessage -ForegroundColor Gray } }
        default { Write-Host $logMessage -ForegroundColor White }
    }
    
    # 写入日志文件
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
            Write-Log "执行查询: $Query" "DEBUG"
        }
        
        if ($DryRun) {
            Write-Log "DRY RUN: $cmd" "INFO"
            return "DRY_RUN_MODE"
        }
        
        $result = Invoke-Expression $cmd
        return $result
    }
    catch {
        Write-Log "查询执行失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 检查ClickHouse连接
function Test-ClickHouseConnection {
    Write-Log "检查ClickHouse连接..." "INFO"
    
    try {
        $version = Invoke-ClickHouseQuery "SELECT version()" -Silent
        Write-Log "ClickHouse版本: $version" "INFO"
        return $true
    }
    catch {
        Write-Log "无法连接到ClickHouse: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 获取数据库信息
function Get-DatabaseInfo {
    param([string]$DatabaseName = "")
    
    Write-Log "获取数据库信息..." "INFO"
    
    if ($DatabaseName) {
        $query = "SELECT database, table, engine, formatReadableSize(sum(bytes_on_disk)) as size FROM system.parts WHERE database = '$DatabaseName' GROUP BY database, table, engine ORDER BY sum(bytes_on_disk) DESC"
    } else {
        $query = "SELECT database, count() as table_count, formatReadableSize(sum(bytes_on_disk)) as total_size FROM system.parts WHERE database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA') GROUP BY database ORDER BY sum(bytes_on_disk) DESC"
    }
    
    return Invoke-ClickHouseQuery $query
}

# 备份功能
function Start-Backup {
    param(
        [string]$BackupType = "full",
        [string]$DatabaseName = "",
        [string]$TableName = ""
    )
    
    Write-Log "开始备份操作 - 类型: $BackupType" "INFO"
    
    if (!(Test-ClickHouseConnection)) {
        throw "无法连接到ClickHouse服务器"
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BackupPath "backup_$timestamp"
    
    if (!$DryRun) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
    
    try {
        switch ($BackupType.ToLower()) {
            "full" {
                Start-FullBackup -BackupDir $backupDir -DatabaseName $DatabaseName
            }
            "incremental" {
                Start-IncrementalBackup -BackupDir $backupDir -DatabaseName $DatabaseName
            }
            "schema" {
                Start-SchemaBackup -BackupDir $backupDir -DatabaseName $DatabaseName
            }
            "table" {
                if (!$TableName) {
                    throw "表备份需要指定表名"
                }
                Start-TableBackup -BackupDir $backupDir -DatabaseName $DatabaseName -TableName $TableName
            }
            "config" {
                Start-ConfigBackup -BackupDir $backupDir
            }
            default {
                throw "不支持的备份类型: $BackupType"
            }
        }
        
        # 创建备份元数据
        $metadata = @{
            backup_type = $BackupType
            timestamp = $timestamp
            database = $DatabaseName
            table = $TableName
            host = $Host
            port = $Port
            version = (Invoke-ClickHouseQuery "SELECT version()" -Silent)
        }
        
        if (!$DryRun) {
            $metadata | ConvertTo-Json | Out-File -FilePath (Join-Path $backupDir "metadata.json")
        }
        
        Write-Log "备份完成: $backupDir" "INFO"
        
        # 清理旧备份
        Start-BackupCleanup
        
    }
    catch {
        Write-Log "备份失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 全量备份
function Start-FullBackup {
    param(
        [string]$BackupDir,
        [string]$DatabaseName
    )
    
    Write-Log "执行全量备份..." "INFO"
    
    if ($DatabaseName) {
        $databases = @($DatabaseName)
    } else {
        $databases = (Invoke-ClickHouseQuery "SHOW DATABASES" -Silent) -split "`n" | Where-Object { $_ -notin @("system", "information_schema", "INFORMATION_SCHEMA", "") }
    }
    
    foreach ($db in $databases) {
        Write-Log "备份数据库: $db" "INFO"
        
        # 获取数据库中的表
        $tables = (Invoke-ClickHouseQuery "SHOW TABLES FROM $db" -Silent) -split "`n" | Where-Object { $_ -ne "" }
        
        foreach ($table in $tables) {
            Write-Log "备份表: $db.$table" "INFO"
            
            # 导出表结构
            $schemaFile = Join-Path $BackupDir "${db}_${table}_schema.sql"
            $createTableQuery = Invoke-ClickHouseQuery "SHOW CREATE TABLE $db.$table" -Silent
            
            if (!$DryRun) {
                $createTableQuery | Out-File -FilePath $schemaFile -Encoding UTF8
            }
            
            # 导出数据
            $dataFile = Join-Path $BackupDir "${db}_${table}_data.native"
            $exportCmd = "$script:ConnectionString --query=`"SELECT * FROM $db.$table FORMAT Native`" > `"$dataFile`""
            
            if ($DryRun) {
                Write-Log "DRY RUN: $exportCmd" "INFO"
            } else {
                Invoke-Expression $exportCmd
            }
        }
    }
}

# 增量备份
function Start-IncrementalBackup {
    param(
        [string]$BackupDir,
        [string]$DatabaseName
    )
    
    Write-Log "执行增量备份..." "INFO"
    
    # 查找最后一次全量备份
    $lastFullBackup = Get-ChildItem $BackupPath -Directory | 
        Where-Object { $_.Name -like "backup_*" } |
        Sort-Object CreationTime -Descending |
        Select-Object -First 1
    
    if (!$lastFullBackup) {
        Write-Log "未找到基础备份，执行全量备份" "WARN"
        Start-FullBackup -BackupDir $BackupDir -DatabaseName $DatabaseName
        return
    }
    
    $lastBackupTime = $lastFullBackup.CreationTime.ToString("yyyy-MM-dd HH:mm:ss")
    Write-Log "基于备份时间进行增量备份: $lastBackupTime" "INFO"
    
    # 这里应该实现基于时间戳的增量备份逻辑
    # 由于ClickHouse的特性，可以基于分区或修改时间来实现
    Write-Log "增量备份功能需要根据具体表结构实现" "WARN"
}

# 表结构备份
function Start-SchemaBackup {
    param(
        [string]$BackupDir,
        [string]$DatabaseName
    )
    
    Write-Log "执行表结构备份..." "INFO"
    
    if ($DatabaseName) {
        $databases = @($DatabaseName)
    } else {
        $databases = (Invoke-ClickHouseQuery "SHOW DATABASES" -Silent) -split "`n" | Where-Object { $_ -notin @("system", "information_schema", "INFORMATION_SCHEMA", "") }
    }
    
    foreach ($db in $databases) {
        $schemaFile = Join-Path $BackupDir "${db}_schema.sql"
        $schemaContent = @()
        
        # 数据库创建语句
        $schemaContent += "CREATE DATABASE IF NOT EXISTS $db;"
        $schemaContent += ""
        
        # 获取所有表的创建语句
        $tables = (Invoke-ClickHouseQuery "SHOW TABLES FROM $db" -Silent) -split "`n" | Where-Object { $_ -ne "" }
        
        foreach ($table in $tables) {
            $createStmt = Invoke-ClickHouseQuery "SHOW CREATE TABLE $db.$table" -Silent
            $schemaContent += $createStmt
            $schemaContent += ""
        }
        
        if (!$DryRun) {
            $schemaContent | Out-File -FilePath $schemaFile -Encoding UTF8
        }
    }
}

# 单表备份
function Start-TableBackup {
    param(
        [string]$BackupDir,
        [string]$DatabaseName,
        [string]$TableName
    )
    
    Write-Log "备份表: $DatabaseName.$TableName" "INFO"
    
    # 表结构
    $schemaFile = Join-Path $BackupDir "${DatabaseName}_${TableName}_schema.sql"
    $createTableQuery = Invoke-ClickHouseQuery "SHOW CREATE TABLE $DatabaseName.$TableName" -Silent
    
    if (!$DryRun) {
        $createTableQuery | Out-File -FilePath $schemaFile -Encoding UTF8
    }
    
    # 表数据
    $dataFile = Join-Path $BackupDir "${DatabaseName}_${TableName}_data.native"
    $exportCmd = "$script:ConnectionString --query=`"SELECT * FROM $DatabaseName.$TableName FORMAT Native`" > `"$dataFile`""
    
    if ($DryRun) {
        Write-Log "DRY RUN: $exportCmd" "INFO"
    } else {
        Invoke-Expression $exportCmd
    }
    
    # 表统计信息
    $statsFile = Join-Path $BackupDir "${DatabaseName}_${TableName}_stats.json"
    $stats = @{
        table_name = "$DatabaseName.$TableName"
        row_count = (Invoke-ClickHouseQuery "SELECT count() FROM $DatabaseName.$TableName" -Silent)
        size_bytes = (Invoke-ClickHouseQuery "SELECT sum(bytes_on_disk) FROM system.parts WHERE database='$DatabaseName' AND table='$TableName'" -Silent)
        backup_time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    if (!$DryRun) {
        $stats | ConvertTo-Json | Out-File -FilePath $statsFile -Encoding UTF8
    }
}

# 配置文件备份
function Start-ConfigBackup {
    param([string]$BackupDir)
    
    Write-Log "备份配置文件..." "INFO"
    
    $configBackupDir = Join-Path $BackupDir "config"
    
    if (!$DryRun) {
        New-Item -ItemType Directory -Path $configBackupDir -Force | Out-Null
        
        # 备份配置目录
        if (Test-Path $ConfigPath) {
            Copy-Item -Path "$ConfigPath\*" -Destination $configBackupDir -Recurse -Force
        }
    }
}

# 恢复功能
function Start-Restore {
    param(
        [string]$BackupPath,
        [string]$DatabaseName = "",
        [string]$TableName = "",
        [switch]$StructureOnly
    )
    
    Write-Log "开始恢复操作..." "INFO"
    
    if (!(Test-ClickHouseConnection)) {
        throw "无法连接到ClickHouse服务器"
    }
    
    if (!(Test-Path $BackupPath)) {
        throw "备份路径不存在: $BackupPath"
    }
    
    # 读取备份元数据
    $metadataFile = Join-Path $BackupPath "metadata.json"
    if (Test-Path $metadataFile) {
        $metadata = Get-Content $metadataFile | ConvertFrom-Json
        Write-Log "备份信息: 类型=$($metadata.backup_type), 时间=$($metadata.timestamp)" "INFO"
    }
    
    try {
        if ($TableName) {
            Restore-Table -BackupPath $BackupPath -DatabaseName $DatabaseName -TableName $TableName -StructureOnly:$StructureOnly
        } elseif ($DatabaseName) {
            Restore-Database -BackupPath $BackupPath -DatabaseName $DatabaseName -StructureOnly:$StructureOnly
        } else {
            Restore-AllDatabases -BackupPath $BackupPath -StructureOnly:$StructureOnly
        }
        
        Write-Log "恢复完成" "INFO"
    }
    catch {
        Write-Log "恢复失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 恢复表
function Restore-Table {
    param(
        [string]$BackupPath,
        [string]$DatabaseName,
        [string]$TableName,
        [switch]$StructureOnly
    )
    
    Write-Log "恢复表: $DatabaseName.$TableName" "INFO"
    
    # 恢复表结构
    $schemaFile = Join-Path $BackupPath "${DatabaseName}_${TableName}_schema.sql"
    if (Test-Path $schemaFile) {
        $createStmt = Get-Content $schemaFile -Raw
        
        if (!$DryRun) {
            Invoke-ClickHouseQuery $createStmt -Silent
        }
        Write-Log "表结构恢复完成" "INFO"
    }
    
    # 恢复数据
    if (!$StructureOnly) {
        $dataFile = Join-Path $BackupPath "${DatabaseName}_${TableName}_data.native"
        if (Test-Path $dataFile) {
            $importCmd = "$script:ConnectionString --query=`"INSERT INTO $DatabaseName.$TableName FORMAT Native`" < `"$dataFile`""
            
            if ($DryRun) {
                Write-Log "DRY RUN: $importCmd" "INFO"
            } else {
                Invoke-Expression $importCmd
            }
            Write-Log "表数据恢复完成" "INFO"
        }
    }
}

# 恢复数据库
function Restore-Database {
    param(
        [string]$BackupPath,
        [string]$DatabaseName,
        [switch]$StructureOnly
    )
    
    Write-Log "恢复数据库: $DatabaseName" "INFO"
    
    # 创建数据库
    if (!$DryRun) {
        Invoke-ClickHouseQuery "CREATE DATABASE IF NOT EXISTS $DatabaseName" -Silent
    }
    
    # 查找该数据库的所有备份文件
    $schemaFiles = Get-ChildItem $BackupPath -Filter "${DatabaseName}_*_schema.sql"
    
    foreach ($schemaFile in $schemaFiles) {
        $tableName = $schemaFile.BaseName -replace "${DatabaseName}_(.+)_schema", '$1'
        Restore-Table -BackupPath $BackupPath -DatabaseName $DatabaseName -TableName $tableName -StructureOnly:$StructureOnly
    }
}

# 恢复所有数据库
function Restore-AllDatabases {
    param(
        [string]$BackupPath,
        [switch]$StructureOnly
    )
    
    Write-Log "恢复所有数据库..." "INFO"
    
    # 获取所有数据库的备份
    $schemaFiles = Get-ChildItem $BackupPath -Filter "*_*_schema.sql"
    $databases = $schemaFiles | ForEach-Object { 
        ($_.BaseName -split "_")[0] 
    } | Sort-Object -Unique
    
    foreach ($db in $databases) {
        Restore-Database -BackupPath $BackupPath -DatabaseName $db -StructureOnly:$StructureOnly
    }
}

# 监控功能
function Start-Monitor {
    Write-Log "开始监控备份状态..." "INFO"
    
    if (!(Test-ClickHouseConnection)) {
        Write-Log "无法连接到ClickHouse服务器" "ERROR"
        return
    }
    
    # 检查备份目录状态
    Write-Log "=== 备份目录状态 ===" "INFO"
    if (Test-Path $BackupPath) {
        $backups = Get-ChildItem $BackupPath -Directory | Sort-Object CreationTime -Descending
        Write-Log "总备份数量: $($backups.Count)" "INFO"
        
        if ($backups.Count -gt 0) {
            $latestBackup = $backups[0]
            Write-Log "最新备份: $($latestBackup.Name) ($(Get-Date $latestBackup.CreationTime -Format 'yyyy-MM-dd HH:mm:ss'))" "INFO"
            
            $backupSize = (Get-ChildItem $latestBackup.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
            Write-Log "最新备份大小: $([math]::Round($backupSize / 1MB, 2)) MB" "INFO"
        }
    }
    
    # 检查数据库状态
    Write-Log "=== 数据库状态 ===" "INFO"
    $dbInfo = Get-DatabaseInfo
    Write-Log $dbInfo "INFO"
    
    # 检查磁盘空间
    Write-Log "=== 磁盘空间状态 ===" "INFO"
    $drive = (Get-Item $BackupPath).PSDrive
    $freeSpace = [math]::Round($drive.Free / 1GB, 2)
    $totalSpace = [math]::Round($drive.Used / 1GB + $drive.Free / 1GB, 2)
    Write-Log "备份驱动器 $($drive.Name): 可用空间 ${freeSpace}GB / 总空间 ${totalSpace}GB" "INFO"
    
    # 检查备份完整性
    Write-Log "=== 备份完整性检查 ===" "INFO"
    Test-BackupIntegrity
}

# 备份完整性检查
function Test-BackupIntegrity {
    $backups = Get-ChildItem $BackupPath -Directory | Sort-Object CreationTime -Descending | Select-Object -First 5
    
    foreach ($backup in $backups) {
        Write-Log "检查备份: $($backup.Name)" "INFO"
        
        $metadataFile = Join-Path $backup.FullName "metadata.json"
        if (Test-Path $metadataFile) {
            $metadata = Get-Content $metadataFile | ConvertFrom-Json
            Write-Log "  备份类型: $($metadata.backup_type)" "INFO"
            Write-Log "  备份时间: $($metadata.timestamp)" "INFO"
        } else {
            Write-Log "  警告: 缺少元数据文件" "WARN"
        }
        
        # 检查文件完整性
        $files = Get-ChildItem $backup.FullName -File
        $schemaFiles = $files | Where-Object { $_.Name -like "*_schema.sql" }
        $dataFiles = $files | Where-Object { $_.Name -like "*_data.native" }
        
        Write-Log "  结构文件: $($schemaFiles.Count), 数据文件: $($dataFiles.Count)" "INFO"
        
        # 检查是否有损坏的文件
        foreach ($file in $files) {
            if ($file.Length -eq 0) {
                Write-Log "  警告: 空文件 $($file.Name)" "WARN"
            }
        }
    }
}

# 备份清理
function Start-BackupCleanup {
    Write-Log "开始清理旧备份..." "INFO"
    
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $oldBackups = Get-ChildItem $BackupPath -Directory | Where-Object { $_.CreationTime -lt $cutoffDate }
    
    Write-Log "找到 $($oldBackups.Count) 个过期备份" "INFO"
    
    foreach ($backup in $oldBackups) {
        Write-Log "删除过期备份: $($backup.Name)" "INFO"
        
        if (!$DryRun) {
            Remove-Item $backup.FullName -Recurse -Force
        }
    }
}

# 版本升级
function Start-Upgrade {
    param(
        [string]$NewVersion,
        [switch]$PreUpgradeBackup = $true
    )
    
    Write-Log "开始版本升级..." "INFO"
    
    if (!(Test-ClickHouseConnection)) {
        throw "无法连接到ClickHouse服务器"
    }
    
    $currentVersion = Invoke-ClickHouseQuery "SELECT version()" -Silent
    Write-Log "当前版本: $currentVersion" "INFO"
    Write-Log "目标版本: $NewVersion" "INFO"
    
    # 升级前备份
    if ($PreUpgradeBackup) {
        Write-Log "执行升级前备份..." "INFO"
        Start-Backup -BackupType "full"
    }
    
    # 兼容性检查
    Write-Log "执行兼容性检查..." "INFO"
    Test-UpgradeCompatibility
    
    # 这里应该实现实际的升级逻辑
    Write-Log "升级逻辑需要根据具体环境实现" "WARN"
    Write-Log "建议步骤:" "INFO"
    Write-Log "1. 停止ClickHouse服务" "INFO"
    Write-Log "2. 备份配置文件" "INFO"
    Write-Log "3. 安装新版本" "INFO"
    Write-Log "4. 恢复配置文件" "INFO"
    Write-Log "5. 启动服务并验证" "INFO"
}

# 升级兼容性检查
function Test-UpgradeCompatibility {
    Write-Log "检查表引擎兼容性..." "INFO"
    
    $legacyEngines = Invoke-ClickHouseQuery "SELECT database, table, engine FROM system.tables WHERE engine IN ('Log', 'TinyLog', 'StripeLog') AND database NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')"
    
    if ($legacyEngines) {
        Write-Log "发现使用旧引擎的表:" "WARN"
        Write-Log $legacyEngines "WARN"
    }
    
    # 检查已更改的设置
    $changedSettings = Invoke-ClickHouseQuery "SELECT name, value FROM system.settings WHERE changed = 1"
    if ($changedSettings) {
        Write-Log "发现已修改的设置:" "INFO"
        Write-Log $changedSettings "INFO"
    }
}

# 灾难恢复测试
function Start-DisasterRecoveryTest {
    Write-Log "开始灾难恢复测试..." "INFO"
    
    # 创建测试数据库
    $testDb = "disaster_recovery_test"
    
    try {
        Write-Log "1. 创建测试环境..." "INFO"
        if (!$DryRun) {
            Invoke-ClickHouseQuery "CREATE DATABASE IF NOT EXISTS $testDb" -Silent
            Invoke-ClickHouseQuery "CREATE TABLE $testDb.test_table (id UInt64, data String) ENGINE = MergeTree() ORDER BY id" -Silent
            Invoke-ClickHouseQuery "INSERT INTO $testDb.test_table VALUES (1, 'test_data')" -Silent
        }
        
        Write-Log "2. 执行备份..." "INFO"
        Start-Backup -BackupType "full" -DatabaseName $testDb
        
        Write-Log "3. 模拟数据丢失..." "INFO"
        if (!$DryRun) {
            Invoke-ClickHouseQuery "DROP DATABASE $testDb" -Silent
        }
        
        Write-Log "4. 执行恢复..." "INFO"
        $latestBackup = Get-ChildItem $BackupPath -Directory | Sort-Object CreationTime -Descending | Select-Object -First 1
        Start-Restore -BackupPath $latestBackup.FullName -DatabaseName $testDb
        
        Write-Log "5. 验证恢复结果..." "INFO"
        $result = Invoke-ClickHouseQuery "SELECT count() FROM $testDb.test_table" -Silent
        
        if ($result -eq "1") {
            Write-Log "灾难恢复测试成功!" "INFO"
        } else {
            Write-Log "灾难恢复测试失败!" "ERROR"
        }
        
        # 清理测试环境
        if (!$DryRun) {
            Invoke-ClickHouseQuery "DROP DATABASE $testDb" -Silent
        }
        
    }
    catch {
        Write-Log "灾难恢复测试失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 主执行逻辑
function Main {
    Write-Log "ClickHouse备份管理器启动" "INFO"
    Write-Log "操作: $Action" "INFO"
    Write-Log "主机: $Host:$Port" "INFO"
    
    try {
        switch ($Action.ToLower()) {
            "backup" {
                Start-Backup -BackupType "full" -DatabaseName $Database
            }
            "restore" {
                if (!$BackupPath) {
                    throw "恢复操作需要指定备份路径"
                }
                Start-Restore -BackupPath $BackupPath -DatabaseName $Database
            }
            "monitor" {
                Start-Monitor
            }
            "upgrade" {
                Start-Upgrade
            }
            "cleanup" {
                Start-BackupCleanup
            }
            "disaster-recovery" {
                Start-DisasterRecoveryTest
            }
            "test" {
                Start-DisasterRecoveryTest
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