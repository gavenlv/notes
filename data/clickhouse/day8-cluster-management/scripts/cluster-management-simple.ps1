# ClickHouse Cluster Management Script - Simplified Version
# Day 8: Cluster Management and Distributed
# =====================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$Host = "localhost",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8123
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
    param([string]$Query)
    
    try {
        $uri = "http://$($Host):$($Port)/"
        $body = "query=" + [System.Web.HttpUtility]::UrlEncode($Query)
        
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
    
    $query = "SELECT cluster, shard_num, replica_num, host_name, port FROM system.clusters ORDER BY cluster, shard_num, replica_num"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "Unable to get cluster status" "Yellow"
    }
}

# Check replica status
function Check-ReplicaStatus {
    Write-ColorOutput "🔄 Checking replica status..." "Cyan"
    
    $query = "SELECT database, table, replica_name, is_leader, absolute_delay, queue_size FROM system.replicas LIMIT 10"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "No replica tables or unable to access replica information" "Yellow"
    }
}

# Check distributed tables
function Check-DistributedTables {
    Write-ColorOutput "📊 Checking distributed tables..." "Cyan"
    
    $query = "SELECT database, name, engine FROM system.tables WHERE engine LIKE '%Distributed%'"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    } else {
        Write-ColorOutput "No distributed tables found" "Yellow"
    }
}

# Show basic information
function Show-BasicInfo {
    Write-ColorOutput "ℹ️ Basic information..." "Cyan"
    
    $query = "SELECT version() as clickhouse_version, hostName() as hostname"
    $result = Invoke-ClickHouseQuery -Query $query
    
    if ($result) {
        Write-ColorOutput $result "Green"
    }
}

# Run health check
function Run-HealthCheck {
    Write-ColorOutput "🏥 Running cluster health check..." "Yellow"
    Write-ColorOutput "=" * 50 "Yellow"
    
    Show-BasicInfo
    Write-ColorOutput ""
    
    Check-ClusterStatus
    Write-ColorOutput ""
    
    Check-ReplicaStatus
    Write-ColorOutput ""
    
    Check-DistributedTables
    
    Write-ColorOutput "=" * 50 "Yellow"
    Write-ColorOutput "✅ Health check completed" "Green"
}

# Show help information
function Show-Help {
    Write-ColorOutput "ClickHouse Cluster Management Script - Simplified Version" "Yellow"
    Write-ColorOutput "=" * 45 "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "Usage: .\cluster-management-simple.ps1 -Action <action> [parameters]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Available actions:" "Cyan"
    Write-ColorOutput "  health      - Run complete health check" "White"
    Write-ColorOutput "  status      - Check cluster status" "White"
    Write-ColorOutput "  replicas    - Check replica status" "White"
    Write-ColorOutput "  tables      - Check distributed tables" "White"
    Write-ColorOutput "  info        - Show basic information" "White"
    Write-ColorOutput "  help        - Show this help information" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Parameters:" "Cyan"
    Write-ColorOutput "  -Host       - ClickHouse host (default: localhost)" "White"
    Write-ColorOutput "  -Port       - ClickHouse port (default: 8123)" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" "Cyan"
    Write-ColorOutput "  .\cluster-management-simple.ps1 -Action health" "White"
    Write-ColorOutput "  .\cluster-management-simple.ps1 -Action status -Host 192.168.1.100" "White"
}

# Main program logic
function Main {
    Write-ColorOutput "🚀 ClickHouse Cluster Management Tool (Simplified Version)" "Magenta"
    Write-ColorOutput "Connecting to: $($Host):$($Port)" "Gray"
    Write-ColorOutput ""
    
    switch ($Action.ToLower()) {
        "health" { Run-HealthCheck }
        "status" { Check-ClusterStatus }
        "replicas" { Check-ReplicaStatus }
        "tables" { Check-DistributedTables }
        "info" { Show-BasicInfo }
        "help" { Show-Help }
        default { 
            Write-ColorOutput "Unknown action: $Action" "Red"
            Show-Help 
        }
    }
}

# Execute main program
try {
    # Load System.Web assembly for URL encoding
    Add-Type -AssemblyName System.Web
    
    Main
}
catch {
    Write-ColorOutput "Script execution error: $($_.Exception.Message)" "Red"
    Write-ColorOutput "Please check ClickHouse connection and parameter settings" "Yellow"
}

Write-ColorOutput ""
Write-ColorOutput "Script execution completed" "Green" 