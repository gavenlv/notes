# Grafana 基础设置实验脚本
# 适用于 Windows 系统

Write-Host "=== Grafana 基础设置实验 ==="

# 检查Grafana是否已安装
$grafanaPath = "C:\Program Files\GrafanaLabs\grafana\bin\grafana-server.exe"
if (-not (Test-Path $grafanaPath)) {
    Write-Host "Grafana 未安装在默认路径，请先按照教程 1.2 安装 Grafana"
    exit 1
}

# 启动Grafana服务
Write-Host "启动 Grafana 服务..."
try {
    $service = Get-Service -Name "grafana" -ErrorAction SilentlyContinue
    if ($service) {
        Start-Service -Name "grafana"
        Write-Host "Grafana 服务已启动"
    } else {
        Write-Host "Grafana 服务不存在，请手动启动 Grafana"
        Write-Host "可执行以下命令:"
        Write-Host "cd 'C:\Program Files\GrafanaLabs\grafana\bin'"
        Write-Host ".\grafana-server.exe"
        exit 1
    }
} catch {
    Write-Host "启动服务时出错: $_"
    exit 1
}

# 检查服务状态
Write-Host "检查 Grafana 服务状态..."
try {
    Get-Service -Name "grafana"
} catch {
    Write-Host "无法获取服务状态: $_"
}

# 等待服务完全启动
Write-Host "等待 Grafana 服务启动..."
Start-Sleep -Seconds 10

# 检查端口是否开放
Write-Host "检查端口 3000 是否开放..."
try {
    $connection = New-Object System.Net.Sockets.TcpClient
    $connection.Connect("localhost", 3000)
    if ($connection.Connected) {
        Write-Host "端口 3000 已开放"
        $connection.Close()
    } else {
        Write-Host "端口 3000 未开放"
    }
} catch {
    Write-Host "检查端口时出错: $_"
}

# 显示访问信息
Write-Host "=== 访问信息 ==="
Write-Host "URL: http://localhost:3000"
Write-Host "默认用户名: admin"
Write-Host "默认密码: admin"
Write-Host ""
Write-Host "请按照教程 1.3 创建第一个仪表盘"

# 提供一些测试命令
Write-Host "=== 有用的测试命令 ==="
Write-Host "查看 Grafana 日志: Get-Content 'C:\Program Files\GrafanaLabs\grafana\logs\grafana.log' -Wait"
Write-Host "停止 Grafana 服务: Stop-Service -Name grafana"
Write-Host "重启 Grafana 服务: Restart-Service -Name grafana"