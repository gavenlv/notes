# ClickHouse 集群检查脚本
# Day 8: 集群管理和分布式

param(
    [string]$ServerHost = "localhost",
    [int]$Port = 8123
)

Write-Host "🚀 ClickHouse 集群检查工具" -ForegroundColor Magenta
Write-Host "连接到: $ServerHost`:$Port" -ForegroundColor Gray
Write-Host ""

try {
    # 检查ClickHouse连接
    Write-Host "🔍 检查ClickHouse连接..." -ForegroundColor Cyan
    
    $uri = "http://$ServerHost`:$Port/"
    $query = "SELECT version() as version"
    $body = "query=$query"
    
    $response = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/x-www-form-urlencoded"
    
    if ($response) {
        Write-Host "✅ ClickHouse连接成功" -ForegroundColor Green
        Write-Host "版本: $response" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # 检查集群配置
    Write-Host "🔍 检查集群配置..." -ForegroundColor Cyan
    $clusterQuery = "SELECT cluster, shard_num, replica_num, host_name FROM system.clusters LIMIT 5"
    $clusterBody = "query=$clusterQuery"
    
    $clusterResponse = Invoke-RestMethod -Uri $uri -Method POST -Body $clusterBody -ContentType "application/x-www-form-urlencoded"
    
    if ($clusterResponse) {
        Write-Host "✅ 集群配置:" -ForegroundColor Green
        Write-Host $clusterResponse -ForegroundColor White
    } else {
        Write-Host "⚠️ 未配置集群或单机模式" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # 检查分布式表
    Write-Host "🔍 检查分布式表..." -ForegroundColor Cyan
    $tableQuery = "SELECT database, name FROM system.tables WHERE engine LIKE '%Distributed%' LIMIT 5"
    $tableBody = "query=$tableQuery"
    
    $tableResponse = Invoke-RestMethod -Uri $uri -Method POST -Body $tableBody -ContentType "application/x-www-form-urlencoded"
    
    if ($tableResponse) {
        Write-Host "✅ 分布式表:" -ForegroundColor Green
        Write-Host $tableResponse -ForegroundColor White
    } else {
        Write-Host "⚠️ 未找到分布式表" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "✅ 集群检查完成" -ForegroundColor Green
    
} catch {
    Write-Host "❌ 连接失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请确保ClickHouse服务正在运行" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "脚本执行完成" -ForegroundColor Green 