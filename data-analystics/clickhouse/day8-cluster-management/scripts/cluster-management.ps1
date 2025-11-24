# ClickHouse Cluster Management Script
# Day 8: Cluster Management and Distributed
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

# Color output function
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Execute ClickHouse query
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
        Write-ColorOutput "Query execution failed: $($_.Exception.Message)" "Red"
        return $null
    }
}

# Check cluster status
function Check-ClusterStatus {
    Write-ColorOutput "🔍 Checking cluster status..." "Cyan"
    
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

# Check replica status
function Check-ReplicaStatus {
    Write-ColorOutput "🔄 Checking replica status..." "Cyan"
    
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

# Check distributed tables
function Check-DistributedTables {
    Write-ColorOutput "📊 Checking distributed tables..." "Cyan"
    
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

# Check ZooKeeper connection
function Check-ZooKeeperConnection {
    Write-ColorOutput "🐘 Checking ZooKeeper connection..." "Cyan"
    
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
        Write-ColorOutput "ZooKeeper connection may have issues" "Yellow"
    }
}

# Show cluster performance metrics
function Show-ClusterMetrics {
    Write-ColorOutput "📈 Cluster performance metrics..." "Cyan"
    
    # Query statistics
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
    
    # System resources
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

# Run cluster health check
function Run-HealthCheck {
    Write-ColorOutput "🏥 Running cluster health check..." "Yellow"
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
    Write-ColorOutput "✅ Health check completed" "Green"
}

# Sync replica
function Sync-Replica {
    param([string]$TableName)
    
    if (-not $TableName) {
        Write-ColorOutput "Please specify table name" "Red"
        return
    }
    
    Write-ColorOutput "🔄 Syncing replica table: $TableName" "Cyan"
    
    $query = "SYSTEM SYNC REPLICA $TableName"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result -ne $null) {
        Write-ColorOutput "✅ Replica sync completed" "Green"
    }
}

# Restart replica queue
function Restart-ReplicaQueue {
    param([string]$TableName)
    
    if (-not $TableName) {
        Write-ColorOutput "Please specify table name" "Red"
        return
    }
    
    Write-ColorOutput "🔄 Restarting replica queue: $TableName" "Cyan"
    
    $query = "SYSTEM RESTART REPLICA $TableName"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result -ne $null) {
        Write-ColorOutput "✅ Replica queue restart completed" "Green"
    }
}

# Optimize tables
function Optimize-ClusterTables {
    param([string]$DatabaseName = "default")
    
    Write-ColorOutput "🚀 Optimizing cluster tables..." "Cyan"
    
    # Get all MergeTree tables
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
                    
                    Write-ColorOutput "Optimizing table: $db.$table" "Yellow"
                    $optimizeQuery = "OPTIMIZE TABLE $db.$table FINAL"
                    Invoke-ClickHouseQuery -Query $optimizeQuery | Out-Null
                }
            }
        }
        Write-ColorOutput "✅ Table optimization completed" "Green"
    }
}

# Show distributed DDL queue
function Show-DDLQueue {
    Write-ColorOutput "📋 Distributed DDL queue..." "Cyan"
    
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
        Write-ColorOutput "DDL queue is empty" "Yellow"
    }
}

# Analyze data distribution
function Analyze-DataDistribution {
    param([string]$TableName)
    
    if (-not $TableName) {
        Write-ColorOutput "Please specify table name" "Red"
        return
    }
    
    Write-ColorOutput "📊 Analyzing data distribution: $TableName" "Cyan"
    
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

# Create test cluster table
function Create-TestClusterTable {
    Write-ColorOutput "🛠️ Creating test cluster table..." "Cyan"
    
    # Create local table
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
    
    # Create distributed table
    $distributedTableQuery = @"
CREATE TABLE IF NOT EXISTS test_cluster_distributed ON CLUSTER $ClusterName AS test_cluster_local
ENGINE = Distributed('$ClusterName', currentDatabase(), 'test_cluster_local', rand())
"@
    
    $result2 = Invoke-ClickHouseQuery -Query $distributedTableQuery
    
    if ($result1 -ne $null -and $result2 -ne $null) {
        Write-ColorOutput "✅ Test table creation completed" "Green"
        
        # Insert test data
        Write-ColorOutput "📝 Inserting test data..." "Yellow"
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
        Write-ColorOutput "✅ Test data insertion completed" "Green"
    }
}

# Show help information
function Show-Help {
    Write-ColorOutput "ClickHouse Cluster Management Script" "Yellow"
    Write-ColorOutput "=" * 40 "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "Usage: .\cluster-management.ps1 -Action <action> [parameters]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Available actions:" "Cyan"
    Write-ColorOutput "  health          - Run complete health check" "White"
    Write-ColorOutput "  status          - Check cluster status" "White"
    Write-ColorOutput "  replicas        - Check replica status" "White"
    Write-ColorOutput "  tables          - Check distributed tables" "White"
    Write-ColorOutput "  zookeeper       - Check ZooKeeper connection" "White"
    Write-ColorOutput "  metrics         - Show performance metrics" "White"
    Write-ColorOutput "  ddl-queue       - View DDL queue" "White"
    Write-ColorOutput "  sync-replica    - Sync replica (requires -TableName parameter)" "White"
    Write-ColorOutput "  restart-replica - Restart replica queue (requires -TableName parameter)" "White"
    Write-ColorOutput "  optimize        - Optimize tables" "White"
    Write-ColorOutput "  analyze-dist    - Analyze data distribution (requires -TableName parameter)" "White"
    Write-ColorOutput "  create-test     - Create test table" "White"
    Write-ColorOutput "  help            - Show this help information" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Parameters:" "Cyan"
    Write-ColorOutput "  -ClusterName    - Cluster name (default: production_cluster)" "White"
    Write-ColorOutput "  -Host           - ClickHouse host (default: localhost)" "White"
    Write-ColorOutput "  -Port           - ClickHouse port (default: 8123)" "White"
    Write-ColorOutput "  -Database       - Database name (default: default)" "White"
    Write-ColorOutput "  -User           - Username (default: default)" "White"
    Write-ColorOutput "  -Password       - Password (default: empty)" "White"
    Write-ColorOutput "  -TableName      - Table name (required for some operations)" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" "Cyan"
    Write-ColorOutput "  .\cluster-management.ps1 -Action health" "White"
    Write-ColorOutput "  .\cluster-management.ps1 -Action sync-replica -TableName user_events_local" "White"
    Write-ColorOutput "  .\cluster-management.ps1 -Action analyze-dist -TableName test_cluster_local" "White"
}

# Main program logic
function Main {
    Write-ColorOutput "🚀 ClickHouse Cluster Management Tool" "Magenta"
    Write-ColorOutput "Connecting to: $($Host):$($Port) (Cluster: $ClusterName)" "Gray"
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
                Write-ColorOutput "Please provide table name: -TableName <table_name>" "Red"
            }
        }
        "restart-replica" { 
            if ($args.Length -gt 0) {
                Restart-ReplicaQueue -TableName $args[0]
            } else {
                Write-ColorOutput "Please provide table name: -TableName <table_name>" "Red"
            }
        }
        "optimize" { Optimize-ClusterTables }
        "analyze-dist" { 
            if ($args.Length -gt 0) {
                Analyze-DataDistribution -TableName $args[0]
            } else {
                Write-ColorOutput "Please provide table name: -TableName <table_name>" "Red"
            }
        }
        "create-test" { Create-TestClusterTable }
        "help" { Show-Help }
        default { 
            Write-ColorOutput "Unknown action: $Action" "Red"
            Show-Help 
        }
    }
}

# Execute main program
try {
    Main
}
catch {
    Write-ColorOutput "Script execution error: $($_.Exception.Message)" "Red"
    Write-ColorOutput "Please check ClickHouse connection and parameter settings" "Yellow"
}

Write-ColorOutput ""
Write-ColorOutput "Script execution completed" "Green" 