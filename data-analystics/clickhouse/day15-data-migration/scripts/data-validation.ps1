# ClickHouse 数据校验脚本
# 功能：全面的数据完整性和一致性校验
# 作者：ClickHouse学习教程
# 版本：1.0

param(
    [Parameter(Mandatory=$false)]
    [string]$SourceCluster = "cluster_3s_2r",
    
    [Parameter(Mandatory=$false)]
    [string]$TargetCluster = "cluster_1s_2r",
    
    [Parameter(Mandatory=$false)]
    [string]$SourceHost = "10.0.1.1",
    
    [Parameter(Mandatory=$false)]
    [string]$TargetHost = "10.0.1.1",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\validation_results",
    
    [Parameter(Mandatory=$false)]
    [int]$SamplePercent = 1,
    
    [Parameter(Mandatory=$false)]
    [switch]$DetailedReport = $false,
    
    [Parameter(Mandatory=$false)]
    [string[]]$ExcludeDatabases = @("system", "information_schema", "INFORMATION_SCHEMA")
)

# 初始化
$ValidationResults = @()
$ErrorCount = 0
$WarningCount = 0
$StartTime = Get-Date

# 创建输出目录
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    $Color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    
    Write-Host $LogMessage -ForegroundColor $Color
    
    # 写入日志文件
    $LogFile = Join-Path $OutputPath "validation_$(Get-Date -Format 'yyyyMMdd').log"
    $LogMessage | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

# 执行ClickHouse查询
function Invoke-CHQuery {
    param(
        [string]$Query,
        [string]$Host = $TargetHost,
        [string]$Format = "TabSeparated"
    )
    
    try {
        $FullQuery = if ($Format -ne "TabSeparated") { "$Query FORMAT $Format" } else { $Query }
        $Result = & clickhouse-client --host $Host --query $FullQuery
        
        if ($LASTEXITCODE -ne 0) {
            throw "查询执行失败，退出代码: $LASTEXITCODE"
        }
        
        return $Result
    }
    catch {
        Write-Log "查询执行失败: $Query, 错误: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 获取所有需要校验的表
function Get-ValidationTables {
    Write-Log "获取需要校验的表列表..."
    
    $Query = @"
SELECT database, name as table
FROM system.tables
WHERE database NOT IN ('$(($ExcludeDatabases -join "', '"))')
AND engine LIKE '%MergeTree%'
ORDER BY database, name
"@
    
    try {
        $Result = Invoke-CHQuery -Query $Query
        $Tables = @()
        
        foreach ($Line in $Result) {
            if ($Line.Trim()) {
                $Parts = $Line -split "`t"
                $Tables += [PSCustomObject]@{
                    Database = $Parts[0]
                    Table = $Parts[1]
                    FullName = "$($Parts[0]).$($Parts[1])"
                }
            }
        }
        
        Write-Log "找到 $($Tables.Count) 个表需要校验"
        return $Tables
    }
    catch {
        Write-Log "获取表列表失败: $($_.Exception.Message)" "ERROR"
        return @()
    }
}

# 行数校验
function Test-RowCount {
    param([array]$Tables)
    
    Write-Log "开始执行行数校验..." "INFO"
    $Results = @()
    
    foreach ($Table in $Tables) {
        try {
            Write-Log "校验表: $($Table.FullName)"
            
            # 源集群行数
            $SourceQuery = "SELECT count(*) FROM remote('$SourceCluster', $($Table.FullName))"
            $SourceCount = Invoke-CHQuery -Query $SourceQuery -Host $SourceHost
            
            # 目标集群行数
            $TargetQuery = "SELECT count(*) FROM $($Table.FullName)"
            $TargetCount = Invoke-CHQuery -Query $TargetQuery -Host $TargetHost
            
            $SourceCountInt = [long]$SourceCount.Trim()
            $TargetCountInt = [long]$TargetCount.Trim()
            $Difference = $SourceCountInt - $TargetCountInt
            $Status = if ($Difference -eq 0) { "PASS" } else { "FAIL" }
            
            $Result = [PSCustomObject]@{
                TestType = "RowCount"
                Database = $Table.Database
                Table = $Table.Table
                SourceCount = $SourceCountInt
                TargetCount = $TargetCountInt
                Difference = $Difference
                Status = $Status
                Details = if ($Status -eq "FAIL") { "行数不匹配，差异: $Difference" } else { "行数匹配" }
            }
            
            $Results += $Result
            
            if ($Status -eq "PASS") {
                Write-Log "✓ $($Table.FullName): $TargetCountInt 行" "SUCCESS"
            } else {
                Write-Log "✗ $($Table.FullName): 源 $SourceCountInt 行, 目标 $TargetCountInt 行, 差异 $Difference" "ERROR"
                $global:ErrorCount++
            }
        }
        catch {
            Write-Log "校验表 $($Table.FullName) 行数失败: $($_.Exception.Message)" "ERROR"
            $global:ErrorCount++
            
            $Results += [PSCustomObject]@{
                TestType = "RowCount"
                Database = $Table.Database
                Table = $Table.Table
                SourceCount = "ERROR"
                TargetCount = "ERROR"
                Difference = "ERROR"
                Status = "ERROR"
                Details = $_.Exception.Message
            }
        }
    }
    
    return $Results
}

# 数据类型校验
function Test-DataTypes {
    param([array]$Tables)
    
    Write-Log "开始执行数据类型校验..." "INFO"
    $Results = @()
    
    foreach ($Table in $Tables) {
        try {
            Write-Log "校验表结构: $($Table.FullName)"
            
            # 获取源表结构
            $SourceQuery = "SELECT name, type FROM remote('$SourceCluster', system.columns) WHERE database = '$($Table.Database)' AND table = '$($Table.Table)' ORDER BY name"
            $SourceSchema = Invoke-CHQuery -Query $SourceQuery -Host $SourceHost
            
            # 获取目标表结构
            $TargetQuery = "SELECT name, type FROM system.columns WHERE database = '$($Table.Database)' AND table = '$($Table.Table)' ORDER BY name"
            $TargetSchema = Invoke-CHQuery -Query $TargetQuery -Host $TargetHost
            
            $SourceColumns = @{}
            $TargetColumns = @{}
            
            # 解析源表列
            foreach ($Line in $SourceSchema) {
                if ($Line.Trim()) {
                    $Parts = $Line -split "`t"
                    $SourceColumns[$Parts[0]] = $Parts[1]
                }
            }
            
            # 解析目标表列
            foreach ($Line in $TargetSchema) {
                if ($Line.Trim()) {
                    $Parts = $Line -split "`t"
                    $TargetColumns[$Parts[0]] = $Parts[1]
                }
            }
            
            # 比较列结构
            $MismatchedColumns = @()
            $MissingColumns = @()
            $ExtraColumns = @()
            
            # 检查源表中的列
            foreach ($Column in $SourceColumns.Keys) {
                if ($TargetColumns.ContainsKey($Column)) {
                    if ($SourceColumns[$Column] -ne $TargetColumns[$Column]) {
                        $MismatchedColumns += "$Column ($($SourceColumns[$Column]) vs $($TargetColumns[$Column]))"
                    }
                } else {
                    $MissingColumns += "$Column ($($SourceColumns[$Column]))"
                }
            }
            
            # 检查目标表中多出的列
            foreach ($Column in $TargetColumns.Keys) {
                if (!$SourceColumns.ContainsKey($Column)) {
                    $ExtraColumns += "$Column ($($TargetColumns[$Column]))"
                }
            }
            
            $HasIssues = $MismatchedColumns.Count -gt 0 -or $MissingColumns.Count -gt 0 -or $ExtraColumns.Count -gt 0
            $Status = if ($HasIssues) { "FAIL" } else { "PASS" }
            
            $Details = @()
            if ($MismatchedColumns.Count -gt 0) { $Details += "类型不匹配: $($MismatchedColumns -join ', ')" }
            if ($MissingColumns.Count -gt 0) { $Details += "缺失列: $($MissingColumns -join ', ')" }
            if ($ExtraColumns.Count -gt 0) { $Details += "多余列: $($ExtraColumns -join ', ')" }
            
            $Result = [PSCustomObject]@{
                TestType = "DataTypes"
                Database = $Table.Database
                Table = $Table.Table
                SourceColumns = $SourceColumns.Count
                TargetColumns = $TargetColumns.Count
                MismatchedColumns = $MismatchedColumns.Count
                Status = $Status
                Details = if ($Details.Count -gt 0) { $Details -join "; " } else { "表结构一致" }
            }
            
            $Results += $Result
            
            if ($Status -eq "PASS") {
                Write-Log "✓ $($Table.FullName): 表结构一致 ($($SourceColumns.Count) 列)" "SUCCESS"
            } else {
                Write-Log "✗ $($Table.FullName): 表结构不一致" "ERROR"
                Write-Log "  详情: $($Result.Details)" "ERROR"
                $global:ErrorCount++
            }
        }
        catch {
            Write-Log "校验表 $($Table.FullName) 结构失败: $($_.Exception.Message)" "ERROR"
            $global:ErrorCount++
            
            $Results += [PSCustomObject]@{
                TestType = "DataTypes"
                Database = $Table.Database
                Table = $Table.Table
                SourceColumns = "ERROR"
                TargetColumns = "ERROR"
                MismatchedColumns = "ERROR"
                Status = "ERROR"
                Details = $_.Exception.Message
            }
        }
    }
    
    return $Results
}

# 抽样数据校验
function Test-SampleData {
    param([array]$Tables)
    
    Write-Log "开始执行抽样数据校验（$SamplePercent% 抽样）..." "INFO"
    $Results = @()
    
    foreach ($Table in $Tables) {
        try {
            Write-Log "抽样校验表: $($Table.FullName)"
            
            # 获取表的主键或排序键
            $OrderQuery = "SELECT sorting_key FROM system.tables WHERE database = '$($Table.Database)' AND name = '$($Table.Table)'"
            $SortingKey = Invoke-CHQuery -Query $OrderQuery -Host $TargetHost
            
            if (!$SortingKey.Trim()) {
                Write-Log "表 $($Table.FullName) 没有排序键，跳过抽样校验" "WARNING"
                continue
            }
            
            # 抽样查询
            $SampleQuery = @"
SELECT * FROM $($Table.FullName) 
SAMPLE $SamplePercent/100 
ORDER BY $($SortingKey.Trim())
LIMIT 1000
"@
            
            $TargetSample = Invoke-CHQuery -Query $SampleQuery -Host $TargetHost
            
            # 从源集群获取相同的抽样数据（使用相同的种子）
            $SourceSampleQuery = @"
SELECT * FROM remote('$SourceCluster', $($Table.FullName))
SAMPLE $SamplePercent/100
ORDER BY $($SortingKey.Trim())
LIMIT 1000
"@
            
            $SourceSample = Invoke-CHQuery -Query $SourceSampleQuery -Host $SourceHost
            
            # 比较抽样数据行数
            $SourceSampleCount = if ($SourceSample) { $SourceSample.Count } else { 0 }
            $TargetSampleCount = if ($TargetSample) { $TargetSample.Count } else { 0 }
            
            # 简单的一致性检查（行数比较）
            $Difference = [Math]::Abs($SourceSampleCount - $TargetSampleCount)
            $Tolerance = [Math]::Max(1, [Math]::Ceiling($SourceSampleCount * 0.05))  # 5%容差
            
            $Status = if ($Difference -le $Tolerance) { "PASS" } else { "FAIL" }
            
            $Result = [PSCustomObject]@{
                TestType = "SampleData"
                Database = $Table.Database
                Table = $Table.Table
                SourceSampleCount = $SourceSampleCount
                TargetSampleCount = $TargetSampleCount
                Difference = $Difference
                Status = $Status
                Details = "抽样比较 (容差: $Tolerance)"
            }
            
            $Results += $Result
            
            if ($Status -eq "PASS") {
                Write-Log "✓ $($Table.FullName): 抽样数据一致 (源: $SourceSampleCount, 目标: $TargetSampleCount)" "SUCCESS"
            } else {
                Write-Log "✗ $($Table.FullName): 抽样数据差异过大 (源: $SourceSampleCount, 目标: $TargetSampleCount, 差异: $Difference)" "WARNING"
                $global:WarningCount++
            }
        }
        catch {
            Write-Log "抽样校验表 $($Table.FullName) 失败: $($_.Exception.Message)" "WARNING"
            $global:WarningCount++
            
            $Results += [PSCustomObject]@{
                TestType = "SampleData"
                Database = $Table.Database
                Table = $Table.Table
                SourceSampleCount = "ERROR"
                TargetSampleCount = "ERROR"
                Difference = "ERROR"
                Status = "ERROR"
                Details = $_.Exception.Message
            }
        }
    }
    
    return $Results
}

# 聚合数据校验
function Test-AggregateData {
    param([array]$Tables)
    
    Write-Log "开始执行聚合数据校验..." "INFO"
    $Results = @()
    
    foreach ($Table in $Tables) {
        try {
            Write-Log "聚合校验表: $($Table.FullName)"
            
            # 获取数值列
            $NumericQuery = @"
SELECT name FROM system.columns 
WHERE database = '$($Table.Database)' AND table = '$($Table.Table)'
AND type IN ('Int8', 'Int16', 'Int32', 'Int64', 'UInt8', 'UInt16', 'UInt32', 'UInt64', 'Float32', 'Float64', 'Decimal')
LIMIT 5
"@
            
            $NumericColumns = Invoke-CHQuery -Query $NumericQuery -Host $TargetHost
            
            if (!$NumericColumns -or $NumericColumns.Count -eq 0) {
                Write-Log "表 $($Table.FullName) 没有数值列，跳过聚合校验" "WARNING"
                continue
            }
            
            # 为每个数值列执行聚合校验
            foreach ($Column in $NumericColumns) {
                if (!$Column.Trim()) { continue }
                
                $ColName = $Column.Trim()
                
                # 源集群聚合
                $SourceAggQuery = @"
SELECT 
    count(*) as cnt,
    sum($ColName) as total_sum,
    avg($ColName) as avg_val,
    min($ColName) as min_val,
    max($ColName) as max_val
FROM remote('$SourceCluster', $($Table.FullName))
WHERE $ColName IS NOT NULL
"@
                
                $SourceAgg = Invoke-CHQuery -Query $SourceAggQuery -Host $SourceHost
                
                # 目标集群聚合
                $TargetAggQuery = @"
SELECT 
    count(*) as cnt,
    sum($ColName) as total_sum,
    avg($ColName) as avg_val,
    min($ColName) as min_val,
    max($ColName) as max_val
FROM $($Table.FullName)
WHERE $ColName IS NOT NULL
"@
                
                $TargetAgg = Invoke-CHQuery -Query $TargetAggQuery -Host $TargetHost
                
                # 解析结果
                $SourceParts = $SourceAgg -split "`t"
                $TargetParts = $TargetAgg -split "`t"
                
                if ($SourceParts.Count -ge 5 -and $TargetParts.Count -ge 5) {
                    $SourceSum = [decimal]$SourceParts[1]
                    $TargetSum = [decimal]$TargetParts[1]
                    $SumDiff = [Math]::Abs($SourceSum - $TargetSum)
                    $SumTolerance = [Math]::Max(1, [Math]::Abs($SourceSum * 0.001))  # 0.1%容差
                    
                    $Status = if ($SumDiff -le $SumTolerance) { "PASS" } else { "FAIL" }
                    
                    $Result = [PSCustomObject]@{
                        TestType = "AggregateData"
                        Database = $Table.Database
                        Table = $Table.Table
                        Column = $ColName
                        SourceSum = $SourceSum
                        TargetSum = $TargetSum
                        Difference = $SumDiff
                        Status = $Status
                        Details = "聚合值比较 (容差: $SumTolerance)"
                    }
                    
                    $Results += $Result
                    
                    if ($Status -eq "PASS") {
                        Write-Log "✓ $($Table.FullName).$ColName: 聚合值一致" "SUCCESS"
                    } else {
                        Write-Log "✗ $($Table.FullName).$ColName: 聚合值差异 (源: $SourceSum, 目标: $TargetSum)" "ERROR"
                        $global:ErrorCount++
                    }
                }
            }
        }
        catch {
            Write-Log "聚合校验表 $($Table.FullName) 失败: $($_.Exception.Message)" "WARNING"
            $global:WarningCount++
        }
    }
    
    return $Results
}

# 业务逻辑校验
function Test-BusinessLogic {
    Write-Log "开始执行业务逻辑校验..." "INFO"
    $Results = @()
    
    # 示例：检查时间分区数据
    try {
        $PartitionQuery = @"
SELECT 
    database,
    table,
    partition,
    sum(rows) as total_rows,
    formatReadableSize(sum(bytes_on_disk)) as size
FROM system.parts
WHERE active = 1
AND database NOT IN ('$(($ExcludeDatabases -join "', '"))')
GROUP BY database, table, partition
HAVING total_rows > 0
ORDER BY database, table, partition
"@
        
        $Partitions = Invoke-CHQuery -Query $PartitionQuery -Host $TargetHost
        
        if ($Partitions) {
            Write-Log "分区数据统计："
            foreach ($Partition in $Partitions) {
                Write-Log "  $Partition" "INFO"
            }
        }
        
        # 可以添加更多业务逻辑校验...
        
    }
    catch {
        Write-Log "业务逻辑校验失败: $($_.Exception.Message)" "WARNING"
        $global:WarningCount++
    }
    
    return $Results
}

# 生成HTML报告
function Generate-HTMLReport {
    param([array]$AllResults)
    
    $ReportFile = Join-Path $OutputPath "validation_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
    
    $PassCount = ($AllResults | Where-Object { $_.Status -eq "PASS" }).Count
    $FailCount = ($AllResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $ErrorCount = ($AllResults | Where-Object { $_.Status -eq "ERROR" }).Count
    
    $Html = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClickHouse 数据迁移校验报告</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 5px 0; opacity: 0.9; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { padding: 20px; border-radius: 8px; text-align: center; color: white; }
        .summary-card h3 { margin: 0; font-size: 2em; }
        .summary-card p { margin: 5px 0; opacity: 0.9; }
        .pass { background-color: #28a745; }
        .fail { background-color: #dc3545; }
        .error { background-color: #fd7e14; }
        .total { background-color: #6c757d; }
        .section { margin-bottom: 40px; }
        .section h2 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: 600; }
        .status-pass { color: #28a745; font-weight: bold; }
        .status-fail { color: #dc3545; font-weight: bold; }
        .status-error { color: #fd7e14; font-weight: bold; }
        .details { font-size: 0.9em; color: #666; }
        .test-type { background-color: #e9ecef; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ClickHouse 数据迁移校验报告</h1>
            <p>生成时间: $(Get-Date -Format 'yyyy年MM月dd日 HH:mm:ss')</p>
            <p>源集群: $SourceCluster → 目标集群: $TargetCluster</p>
            <p>执行时长: $((Get-Date) - $StartTime)</p>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>$($AllResults.Count)</h3>
                <p>总检查项</p>
            </div>
            <div class="summary-card pass">
                <h3>$PassCount</h3>
                <p>通过项</p>
            </div>
            <div class="summary-card fail">
                <h3>$FailCount</h3>
                <p>失败项</p>
            </div>
            <div class="summary-card error">
                <h3>$ErrorCount</h3>
                <p>错误项</p>
            </div>
        </div>
        
        <div class="section">
            <h2>详细检查结果</h2>
            <table>
                <thead>
                    <tr>
                        <th>检查类型</th>
                        <th>数据库</th>
                        <th>表名</th>
                        <th>状态</th>
                        <th>详细信息</th>
                    </tr>
                </thead>
                <tbody>
"@
    
    foreach ($Result in $AllResults) {
        $StatusClass = switch ($Result.Status) {
            "PASS" { "status-pass" }
            "FAIL" { "status-fail" }
            "ERROR" { "status-error" }
            default { "" }
        }
        
        $Html += @"
                    <tr>
                        <td><span class="test-type">$($Result.TestType)</span></td>
                        <td>$($Result.Database)</td>
                        <td>$($Result.Table)</td>
                        <td class="$StatusClass">$($Result.Status)</td>
                        <td class="details">$($Result.Details)</td>
                    </tr>
"@
    }
    
    $Html += @"
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"@
    
    $Html | Out-File -FilePath $ReportFile -Encoding UTF8
    Write-Log "HTML报告已生成: $ReportFile" "SUCCESS"
    
    return $ReportFile
}

# 生成CSV报告
function Generate-CSVReport {
    param([array]$AllResults)
    
    $CsvFile = Join-Path $OutputPath "validation_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    $AllResults | Export-Csv -Path $CsvFile -NoTypeInformation -Encoding UTF8
    
    Write-Log "CSV报告已生成: $CsvFile" "SUCCESS"
    return $CsvFile
}

# 主执行函数
function Main {
    Write-Log "开始ClickHouse数据校验..." "INFO"
    Write-Log "源集群: $SourceCluster, 目标集群: $TargetCluster"
    
    # 获取要校验的表
    $Tables = Get-ValidationTables
    if ($Tables.Count -eq 0) {
        Write-Log "没有找到需要校验的表，退出程序" "ERROR"
        return
    }
    
    $AllResults = @()
    
    # 1. 行数校验
    Write-Log "==================== 行数校验 ====================" "INFO"
    $RowCountResults = Test-RowCount -Tables $Tables
    $AllResults += $RowCountResults
    
    # 2. 数据类型校验
    Write-Log "==================== 数据类型校验 ====================" "INFO"
    $DataTypeResults = Test-DataTypes -Tables $Tables
    $AllResults += $DataTypeResults
    
    # 3. 抽样数据校验
    if ($SamplePercent -gt 0) {
        Write-Log "==================== 抽样数据校验 ====================" "INFO"
        $SampleResults = Test-SampleData -Tables $Tables
        $AllResults += $SampleResults
    }
    
    # 4. 聚合数据校验
    if ($DetailedReport) {
        Write-Log "==================== 聚合数据校验 ====================" "INFO"
        $AggregateResults = Test-AggregateData -Tables $Tables
        $AllResults += $AggregateResults
    }
    
    # 5. 业务逻辑校验
    Write-Log "==================== 业务逻辑校验 ====================" "INFO"
    $BusinessResults = Test-BusinessLogic
    $AllResults += $BusinessResults
    
    # 生成报告
    Write-Log "==================== 生成报告 ====================" "INFO"
    $HtmlReport = Generate-HTMLReport -AllResults $AllResults
    $CsvReport = Generate-CSVReport -AllResults $AllResults
    
    # 输出摘要
    $PassCount = ($AllResults | Where-Object { $_.Status -eq "PASS" }).Count
    $FailCount = ($AllResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $ErrorCount = ($AllResults | Where-Object { $_.Status -eq "ERROR" }).Count
    
    Write-Log "==================== 校验摘要 ====================" "INFO"
    Write-Log "总检查项: $($AllResults.Count)"
    Write-Log "通过项: $PassCount" "SUCCESS"
    Write-Log "失败项: $FailCount" $(if ($FailCount -gt 0) { "ERROR" } else { "INFO" })
    Write-Log "错误项: $ErrorCount" $(if ($ErrorCount -gt 0) { "ERROR" } else { "INFO" })
    Write-Log "成功率: $(if ($AllResults.Count -gt 0) { [Math]::Round($PassCount / $AllResults.Count * 100, 2) } else { 0 })%"
    
    Write-Log "报告文件:"
    Write-Log "  HTML: $HtmlReport"
    Write-Log "  CSV: $CsvReport"
    
    Write-Log "数据校验完成！" "SUCCESS"
}

# 执行主函数
try {
    Main
}
catch {
    Write-Log "脚本执行异常: $($_.Exception.Message)" "ERROR"
    Write-Log "错误位置: $($_.InvocationInfo.PositionMessage)" "ERROR"
    exit 1
} 