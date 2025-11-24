# ClickHouse Cluster Check Script
# Day 8: Cluster Management and Distributed

param(
    [string]$ServerHost = "localhost",
    [int]$Port = 8123
)

Write-Host "🚀 ClickHouse Cluster Check Tool" -ForegroundColor Magenta
Write-Host "Connecting to: $ServerHost`:$Port" -ForegroundColor Gray
Write-Host ""

try {
    # Check ClickHouse connection
    Write-Host "🔍 Checking ClickHouse connection..." -ForegroundColor Cyan
    
    $uri = "http://$ServerHost`:$Port/"
    $query = "SELECT version() as version"
    $body = "query=$query"
    
    $response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/x-www-form-urlencoded"
    
    if ($response) {
        Write-Host "✅ ClickHouse connection successful" -ForegroundColor Green
        Write-Host "Version: $response" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # Check cluster configuration
    Write-Host "🔍 Checking cluster configuration..." -ForegroundColor Cyan
    $clusterQuery = "SELECT cluster, shard_num, replica_num, host_name FROM system.clusters LIMIT 5"
    $clusterBody = "query=$clusterQuery"
    
    $clusterResponse = Invoke-RestMethod -Uri $uri -Method POST -Body $clusterBody -ContentType "application/x-www-form-urlencoded"
    
    if ($clusterResponse) {
        Write-Host "✅ Cluster configuration:" -ForegroundColor Green
        Write-Host $clusterResponse -ForegroundColor White
    } else {
        Write-Host "⚠️ No cluster configured or running in standalone mode" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Check distributed tables
    Write-Host "🔍 Checking distributed tables..." -ForegroundColor Cyan
    $tableQuery = "SELECT database, name FROM system.tables WHERE engine LIKE '%Distributed%' LIMIT 5"
    $tableBody = "query=$tableQuery"
    
    $tableResponse = Invoke-RestMethod -Uri $uri -Method POST -Body $tableBody -ContentType "application/x-www-form-urlencoded"
    
    if ($tableResponse) {
        Write-Host "✅ Distributed tables:" -ForegroundColor Green
        Write-Host $tableResponse -ForegroundColor White
    } else {
        Write-Host "⚠️ No distributed tables found" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "✅ Cluster check completed" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Connection failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please ensure ClickHouse service is running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Script execution completed" -ForegroundColor Green 