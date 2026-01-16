# ClickHouse + Prometheus + Grafana 监控系统 PowerShell启动脚本

Write-Host "==========================================" -ForegroundColor Green
Write-Host "ClickHouse + Prometheus + Grafana 监控系统" -ForegroundColor Green
Write-Host "使用专用镜像源: zlsmshoqvwt6q1.xuanyuan.run" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green

# 检查Docker是否安装
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "错误: Docker未安装，请先安装Docker" -ForegroundColor Red
    exit 1
}

# 检查Docker Compose是否安装
if (-not (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
    Write-Host "错误: Docker Compose未安装，请先安装Docker Compose" -ForegroundColor Red
    exit 1
}

# 创建必要的目录
Write-Host "创建必要的目录..." -ForegroundColor Cyan
if (-not (Test-Path ".\clickhouse")) { New-Item -ItemType Directory -Path ".\clickhouse" | Out-Null }
if (-not (Test-Path ".\prometheus")) { New-Item -ItemType Directory -Path ".\prometheus" | Out-Null }
if (-not (Test-Path ".\grafana\provisioning\datasources")) { 
    New-Item -ItemType Directory -Path ".\grafana\provisioning\datasources" -Force | Out-Null 
}
if (-not (Test-Path ".\grafana\provisioning\dashboards")) { 
    New-Item -ItemType Directory -Path ".\grafana\provisioning\dashboards" -Force | Out-Null 
}
if (-not (Test-Path ".\grafana\dashboards")) { 
    New-Item -ItemType Directory -Path ".\grafana\dashboards" -Force | Out-Null 
}

# 拉取镜像并重新标记
Write-Host "从专用镜像源拉取镜像..." -ForegroundColor Cyan

$images = @(
    @{Original="clickhouse/clickhouse-server:latest"; Registry="zlsmshoqvwt6q1.xuanyuan.run"},
    @{Original="prom/prometheus:latest"; Registry="zlsmshoqvwt6q1.xuanyuan.run"},
    @{Original="grafana/grafana:latest"; Registry="zlsmshoqvwt6q1.xuanyuan.run"},
    @{Original="f1yegor/clickhouse-exporter:latest"; Registry="zlsmshoqvwt6q1.xuanyuan.run"},
    @{Original="prom/node-exporter:latest"; Registry="zlsmshoqvwt6q1.xuanyuan.run"}
)

foreach ($image in $images) {
    $original = $image.Original
    $registry = $image.Registry
    $newImage = "$registry/$original"
    
    Write-Host "处理镜像: $original" -ForegroundColor Yellow
    
    # 拉取镜像
    try {
        Write-Host "  拉取镜像: $newImage" -ForegroundColor Gray
        docker pull $newImage
        
        # 重新标记为原始名称
        Write-Host "  重新标记为: $original" -ForegroundColor Gray
        docker tag $newImage $original
        
        # 删除临时镜像
        Write-Host "  删除临时镜像" -ForegroundColor Gray
        docker rmi $newImage
        
        Write-Host "  ✓ 完成" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ 失败: $_" -ForegroundColor Red
    }
}

# 启动服务
Write-Host "启动监控服务..." -ForegroundColor Cyan
docker-compose up -d

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# 检查服务状态
Write-Host "检查服务状态..." -ForegroundColor Cyan
$services = @("clickhouse", "prometheus", "grafana", "clickhouse-exporter", "node-exporter")

foreach ($service in $services) {
    $result = docker ps --filter "name=$service" --format "table {{.Names}}\t{{.Status}}"
    if ($result -match $service) {
        Write-Host "✓ $service 运行正常" -ForegroundColor Green
    }
    else {
        Write-Host "✗ $service 启动失败" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "服务访问地址:" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "ClickHouse HTTP接口: http://localhost:8123" -ForegroundColor White
Write-Host "ClickHouse TCP接口: localhost:9000" -ForegroundColor White
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "Node Exporter: http://localhost:9100" -ForegroundColor White
Write-Host "ClickHouse Exporter: http://localhost:9333" -ForegroundColor White
Write-Host ""
Write-Host "Grafana登录信息:" -ForegroundColor Yellow
Write-Host "用户名: admin" -ForegroundColor White
Write-Host "密码: admin123" -ForegroundColor White
Write-Host ""
Write-Host "ClickHouse连接信息:" -ForegroundColor Yellow
Write-Host "用户名: admin" -ForegroundColor White
Write-Host "密码: admin123" -ForegroundColor White
Write-Host "数据库: monitoring" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "常用命令:" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "查看服务状态: docker-compose ps" -ForegroundColor Gray
Write-Host "查看日志: docker-compose logs [服务名]" -ForegroundColor Gray
Write-Host "停止服务: docker-compose down" -ForegroundColor Gray
Write-Host "重启服务: docker-compose restart" -ForegroundColor Gray
Write-Host "查看镜像: docker images" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Green

# 打开浏览器访问Grafana
$openGrafana = Read-Host "是否立即打开Grafana? (y/n)"
if ($openGrafana -eq "y" -or $openGrafana -eq "Y") {
    Start-Process "http://localhost:3000"
    Write-Host "已打开Grafana页面" -ForegroundColor Green
}

Write-Host "启动完成!" -ForegroundColor Green