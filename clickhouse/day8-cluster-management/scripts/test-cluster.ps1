# Simple ClickHouse Cluster Test Script
# Day 8: Cluster Management

Write-Host "ClickHouse Cluster Test" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green

$server = "localhost"
$port = 8123

Write-Host "Testing connection to $server`:$port" -ForegroundColor Cyan

try {
    $uri = "http://$server`:$port/"
    $response = Invoke-RestMethod -Uri $uri -Method GET
    
    if ($response) {
        Write-Host "SUCCESS: ClickHouse is running" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Cannot connect to ClickHouse" -ForegroundColor Red
    Write-Host "Please ensure ClickHouse is running on $server`:$port" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test completed" -ForegroundColor Green 