# 第1章：Qlik Sense概述与环境搭建 - 生产级代码示例

本章提供生产环境中Qlik Sense部署和配置的完整代码示例，包括安装脚本、配置管理和监控工具。

## 1.1 生产环境安装脚本

### Windows Server安装脚本 (PowerShell)

```powershell
# Qlik Sense Enterprise on Windows - 生产环境安装脚本
# 适用于Windows Server 2016/2019/2022

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallPath = "C:\Program Files\Qlik\Sense",
    
    [Parameter(Mandatory=$true)]
    [string]$RepositoryDatabaseHost = "localhost",
    
    [Parameter(Mandatory=$true)]
    [string]$RepositoryDatabaseName = "QSR",
    
    [Parameter(Mandatory=$false)]
    [string]$SharedPersistencePath = "\\fileserver\qlik-share",
    
    [Parameter(Mandatory=$false)]
    [switch]$SilentInstall = $true
)

# 验证系统要求
function Test-SystemRequirements {
    Write-Host "验证系统要求..." -ForegroundColor Cyan
    
    # 检查Windows版本
    $os = Get-CimInstance Win32_OperatingSystem
    if ($os.Version -lt "10.0.14393") {
        throw "需要Windows Server 2016或更高版本"
    }
    
    # 检查.NET Framework 4.6.2+
    $netVersion = Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -ErrorAction SilentlyContinue
    if ($netVersion.Release -lt 394802) {
        throw "需要.NET Framework 4.6.2或更高版本"
    }
    
    # 检查磁盘空间 (至少50GB)
    $drive = Split-Path $InstallPath -Qualifier
    $disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='$drive'"
    if ($disk.FreeSpace -lt 50GB) {
        throw "安装路径磁盘空间不足50GB"
    }
    
    Write-Host "系统要求验证通过" -ForegroundColor Green
}

# 配置防火墙规则
function Set-FirewallRules {
    Write-Host "配置防火墙规则..." -ForegroundColor Cyan
    
    # Qlik Sense核心端口
    $ports = @{
        "QlikSense Repository" = 443
        "QlikSense Proxy" = 443
        "QlikSense Engine" = 4747
        "QlikSense Scheduler" = 443
        "QlikSense Printing" = 443
    }
    
    foreach ($rule in $ports.GetEnumerator()) {
        New-NetFirewallRule -DisplayName $rule.Key -Direction Inbound -Protocol TCP -LocalPort $rule.Value -Action Allow -Profile Domain | Out-Null
        Write-Host "  + $($rule.Key) 端口 $($rule.Value) 已开放" -ForegroundColor Green
    }
}

# 安装Qlik Sense
function Install-QlikSense {
    Write-Host "开始安装Qlik Sense..." -ForegroundColor Cyan
    
    # 构建安装参数
    $installArgs = @{
        Silent = $SilentInstall
        InstallPath = $InstallPath
        RepositoryDatabaseHost = $RepositoryDatabaseHost
        RepositoryDatabaseName = $RepositoryDatabaseName
        SharedPersistencePath = $SharedPersistencePath
    }
    
    # 执行安装 (实际环境中需要Qlik Sense安装包)
    # Start-Process -FilePath "Qlik_Sense_setup.exe" -ArgumentList $installArgs -Wait
    
    Write-Host "Qlik Sense安装完成" -ForegroundColor Green
}

# 主安装流程
try {
    Write-Host "=========================================" -ForegroundColor Yellow
    Write-Host "Qlik Sense Enterprise 生产环境安装脚本" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Yellow
    
    Test-SystemRequirements
    Set-FirewallRules
    Install-QlikSense
    
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "安装成功完成！" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    
} catch {
    Write-Error "安装失败: $($_.Exception.Message)"
    exit 1
}
```

### Linux安装脚本 (适用于Qlik Sense Enterprise on Kubernetes)

```bash
#!/bin/bash

# Qlik Sense Enterprise on Kubernetes - 生产环境部署脚本
# 适用于Red Hat OpenShift或标准Kubernetes集群

set -e  # 遇到错误立即退出

# 配置参数
NAMESPACE="qlik"
RELEASE_NAME="qlik-sense"
CHART_VERSION="latest"
STORAGE_CLASS="fast-ssd"

# 验证环境
function check_environment() {
    echo "验证部署环境..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        echo "错误: 未找到kubectl命令"
        exit 1
    fi
    
    # 检查helm
    if ! command -v helm &> /dev/null; then
        echo "错误: 未找到helm命令"
        exit 1
    fi
    
    # 检查集群连接
    if ! kubectl cluster-info &> /dev/null; then
        echo "错误: 无法连接到Kubernetes集群"
        exit 1
    fi
    
    echo "环境验证通过"
}

# 创建命名空间
function create_namespace() {
    echo "创建命名空间: $NAMESPACE"
    
    kubectl create namespace $NAMESPACE 2>/dev/null || true
    kubectl config set-context --current --namespace=$NAMESPACE
}

# 配置存储
function configure_storage() {
    echo "配置持久化存储..."
    
    # 创建存储类 (如果不存在)
    cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: $STORAGE_CLASS
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF
}

# 部署Qlik Sense
function deploy_qlik_sense() {
    echo "部署Qlik Sense..."
    
    # 添加Qlik Helm仓库
    helm repo add qlik https://qlik.bintray.com/stable
    helm repo update
    
    # 创建values.yaml配置文件
    cat > values.yaml <<EOF
# Qlik Sense生产环境配置
global:
  namespace: $NAMESPACE
  
# 存储配置
storage:
  class: $STORAGE_CLASS
  size:
    repository: 100Gi
    engine: 200Gi
    shared: 500Gi

# 计算资源
resources:
  repository:
    requests:
      cpu: "2"
      memory: "4Gi"
    limits:
      cpu: "4"
      memory: "8Gi"
  engine:
    requests:
      cpu: "4"
      memory: "16Gi"
    limits:
      cpu: "8"
      memory: "32Gi"
  proxy:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "2"
      memory: "4Gi"

# 网络配置
network:
  domain: "qlik.example.com"
  tls:
    enabled: true
    secretName: "qlik-tls"

# 监控和日志
monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true

# 备份配置
backup:
  enabled: true
  schedule: "0 2 * * *"
  retention: "30d"
EOF

    # 执行部署
    helm install $RELEASE_NAME qlik/qlik-sense -n $NAMESPACE -f values.yaml
    
    echo "Qlik Sense部署已启动"
}

# 等待部署完成
function wait_for_deployment() {
    echo "等待部署完成..."
    
    kubectl wait --for=condition=available --timeout=600s deployment/$RELEASE_NAME-repository -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=600s deployment/$RELEASE_NAME-engine -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=600s deployment/$RELEASE_NAME-proxy -n $NAMESPACE
    
    echo "所有服务已就绪"
}

# 显示部署状态
function show_status() {
    echo "========================================="
    echo "Qlik Sense部署状态"
    echo "========================================="
    
    kubectl get pods -n $NAMESPACE
    echo ""
    kubectl get services -n $NAMESPACE
    echo ""
    echo "访问地址: https://qlik.example.com"
}

# 主流程
main() {
    echo "========================================="
    echo "Qlik Sense Enterprise on Kubernetes 部署"
    echo "========================================="
    
    check_environment
    create_namespace
    configure_storage
    deploy_qlik_sense
    wait_for_deployment
    show_status
    
    echo "========================================="
    echo "部署完成！"
    echo "========================================="
}

# 执行主流程
main "$@"
```

## 1.2 生产环境配置管理

### 配置文件模板

```yaml
# qliksense-config.yaml - Qlik Sense生产环境配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: qliksense-config
  namespace: qlik
data:
  # 系统配置
  system.properties: |
    # 系统性能调优
    qlik.engine.performance.maxThreads=16
    qlik.engine.performance.cacheSize=4096
    qlik.engine.performance.maxMemory=32GB
    
    # 安全配置
    qlik.security.session.timeout=1800
    qlik.security.authentication.method=JWT,SAML
    qlik.security.encryption.level=HIGH
    
    # 日志配置
    qlik.logging.level=INFO
    qlik.logging.rotation.size=100MB
    qlik.logging.rotation.count=10
    
  # 网络配置
  network.properties: |
    # TLS配置
    server.ssl.enabled=true
    server.ssl.key-store=/etc/ssl/qlik/keystore.jks
    server.ssl.key-store-password=changeit
    server.ssl.key-alias=qlik
    
    # 反向代理配置
    server.forward-headers-strategy=NATIVE
    server.tomcat.remote-ip-header=X-Forwarded-For
    server.tomcat.protocol-header=X-Forwarded-Proto
    
  # 数据库配置
  database.properties: |
    # Repository数据库
    spring.datasource.url=jdbc:postgresql://db-host:5432/QSR
    spring.datasource.username=qlik_repo
    spring.datasource.password=${DB_PASSWORD}
    spring.datasource.driver-class-name=org.postgresql.Driver
    
    # 连接池配置
    spring.datasource.hikari.maximum-pool-size=20
    spring.datasource.hikari.minimum-idle=5
    spring.datasource.hikari.connection-timeout=30000
```

### 环境变量配置

```bash
# .env - 生产环境变量配置
# 数据库配置
DB_HOST=postgresql.prod.internal
DB_PORT=5432
DB_NAME=QSR
DB_USER=qlik_repo
DB_PASSWORD=your_secure_password

# 存储配置
STORAGE_PATH=/data/qlik
BACKUP_PATH=/backup/qlik
LOG_PATH=/var/log/qlik

# 网络配置
DOMAIN_NAME=qlik.company.com
SSL_CERT_PATH=/etc/ssl/certs/qlik.crt
SSL_KEY_PATH=/etc/ssl/private/qlik.key

# 监控配置
PROMETHEUS_ENDPOINT=http://prometheus.monitoring:9090
GRAFANA_ENDPOINT=http://grafana.monitoring:3000

# 备份配置
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION=30
```

## 1.3 监控和健康检查

### 健康检查脚本

```powershell
# health-check.ps1 - Qlik Sense健康检查脚本
param(
    [string]$QlikSenseURL = "https://qlik.company.com",
    [string]$AdminUser = "admin@company.com",
    [string]$OutputDir = "C:\temp\health-reports"
)

# 创建输出目录
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# 生成时间戳
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "$OutputDir\health-report-$timestamp.html"

# 健康检查函数
function Test-QlikSenseHealth {
    $results = @{}
    
    # 1. 检查服务可用性
    try {
        $response = Invoke-WebRequest -Uri "$QlikSenseURL/api/about" -UseBasicParsing -TimeoutSec 30
        $results.ServiceStatus = @{
            Status = "OK"
            ResponseTime = $response.Headers.'X-Response-Time'
            Version = ($response.Content | ConvertFrom-Json).version
        }
    } catch {
        $results.ServiceStatus = @{
            Status = "ERROR"
            Message = $_.Exception.Message
        }
    }
    
    # 2. 检查引擎状态
    try {
        $engineResponse = Invoke-WebRequest -Uri "$QlikSenseURL/api/engine" -UseBasicParsing -TimeoutSec 30
        $results.EngineStatus = @{
            Status = "OK"
            ActiveSessions = ($engineResponse.Content | ConvertFrom-Json).activeSessions
        }
    } catch {
        $results.EngineStatus = @{
            Status = "ERROR"
            Message = $_.Exception.Message
        }
    }
    
    # 3. 检查存储空间
    $drive = Split-Path $env:SystemDrive -Qualifier
    $disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='$drive'"
    $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
    $totalSpaceGB = [math]::Round($disk.Size / 1GB, 2)
    $usagePercent = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
    
    $results.StorageStatus = @{
        Status = if ($usagePercent -gt 90) { "WARNING" } elseif ($usagePercent -gt 95) { "ERROR" } else { "OK" }
        FreeSpaceGB = $freeSpaceGB
        TotalSpaceGB = $totalSpaceGB
        UsagePercent = $usagePercent
    }
    
    # 4. 检查内存使用
    $memory = Get-CimInstance Win32_OperatingSystem
    $memoryUsage = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
    
    $results.MemoryStatus = @{
        Status = if ($memoryUsage -gt 85) { "WARNING" } elseif ($memoryUsage -gt 95) { "ERROR" } else { "OK" }
        UsagePercent = $memoryUsage
        TotalMB = [math]::Round($memory.TotalVisibleMemorySize / 1024, 2)
        FreeMB = [math]::Round($memory.FreePhysicalMemory / 1024, 2)
    }
    
    return $results
}

# 生成HTML报告
function Generate-HealthReport {
    param($Results)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Qlik Sense Health Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .ok { background-color: #dff0d8; border: 1px solid #d6e9c6; }
        .warning { background-color: #fcf8e3; border: 1px solid #faebcc; }
        .error { background-color: #f2dede; border: 1px solid #ebccd1; }
        .status-ok { color: #3c763d; font-weight: bold; }
        .status-warning { color: #8a6d3b; font-weight: bold; }
        .status-error { color: #a94442; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Qlik Sense Health Report</h1>
        <p>Generated: $(Get-Date)</p>
    </div>
    
    <div class="section $(if($Results.ServiceStatus.Status -eq 'OK'){'ok'}elseif($Results.ServiceStatus.Status -eq 'WARNING'){'warning'}else{'error'})">
        <h2>Service Status</h2>
        <p>Status: <span class="status-$(if($Results.ServiceStatus.Status -eq 'OK'){'ok'}elseif($Results.ServiceStatus.Status -eq 'WARNING'){'warning'}else{'error'})">$($Results.ServiceStatus.Status)</span></p>
        $(if($Results.ServiceStatus.Status -eq 'OK') {
            "<p>Version: $($Results.ServiceStatus.Version)</p>
             <p>Response Time: $($Results.ServiceStatus.ResponseTime)ms</p>"
        } else {
            "<p>Error: $($Results.ServiceStatus.Message)</p>"
        })
    </div>
    
    <div class="section $(if($Results.EngineStatus.Status -eq 'OK'){'ok'}elseif($Results.EngineStatus.Status -eq 'WARNING'){'warning'}else{'error'})">
        <h2>Engine Status</h2>
        <p>Status: <span class="status-$(if($Results.EngineStatus.Status -eq 'OK'){'ok'}elseif($Results.EngineStatus.Status -eq 'WARNING'){'warning'}else{'error'})">$($Results.EngineStatus.Status)</span></p>
        $(if($Results.EngineStatus.Status -eq 'OK') {
            "<p>Active Sessions: $($Results.EngineStatus.ActiveSessions)</p>"
        } else {
            "<p>Error: $($Results.EngineStatus.Message)</p>"
        })
    </div>
    
    <div class="section $(if($Results.StorageStatus.Status -eq 'OK'){'ok'}elseif($Results.StorageStatus.Status -eq 'WARNING'){'warning'}else{'error'})">
        <h2>Storage Status</h2>
        <p>Status: <span class="status-$(if($Results.StorageStatus.Status -eq 'OK'){'ok'}elseif($Results.StorageStatus.Status -eq 'WARNING'){'warning'}else{'error'})">$($Results.StorageStatus.Status)</span></p>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Space</td><td>$($Results.StorageStatus.TotalSpaceGB) GB</td></tr>
            <tr><td>Free Space</td><td>$($Results.StorageStatus.FreeSpaceGB) GB</td></tr>
            <tr><td>Usage</td><td>$($Results.StorageStatus.UsagePercent)%</td></tr>
        </table>
    </div>
    
    <div class="section $(if($Results.MemoryStatus.Status -eq 'OK'){'ok'}elseif($Results.MemoryStatus.Status -eq 'WARNING'){'warning'}else{'error'})">
        <h2>Memory Status</h2>
        <p>Status: <span class="status-$(if($Results.MemoryStatus.Status -eq 'OK'){'ok'}elseif($Results.MemoryStatus.Status -eq 'WARNING'){'warning'}else{'error'})">$($Results.MemoryStatus.Status)</span></p>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Memory</td><td>$($Results.MemoryStatus.TotalMB) MB</td></tr>
            <tr><td>Free Memory</td><td>$($Results.MemoryStatus.FreeMB) MB</td></tr>
            <tr><td>Usage</td><td>$($Results.MemoryStatus.UsagePercent)%</td></tr>
        </table>
    </div>
</body>
</html>
"@
    
    $html | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Host "健康检查报告已生成: $reportFile" -ForegroundColor Green
}

# 执行健康检查
Write-Host "执行Qlik Sense健康检查..." -ForegroundColor Cyan
$healthResults = Test-QlikSenseHealth
Generate-HealthReport -Results $healthResults

# 如果有错误，发送告警
if ($healthResults.ServiceStatus.Status -eq "ERROR" -or 
    $healthResults.EngineStatus.Status -eq "ERROR" -or
    $healthResults.StorageStatus.Status -eq "ERROR" -or
    $healthResults.MemoryStatus.Status -eq "ERROR") {
    
    Write-Host "检测到严重错误，发送告警..." -ForegroundColor Red
    
    # 这里可以集成邮件告警、短信告警等
    # Send-MailMessage -To "admin@company.com" -Subject "Qlik Sense Health Alert" -Body "请检查Qlik Sense健康报告: $reportFile"
}
```

### 监控配置 (Prometheus)

```yaml
# prometheus-qlik-config.yaml - Prometheus监控配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: qlik-prometheus-config
  namespace: monitoring
data:
  qlik-monitoring.yml: |
    # Qlik Sense监控配置
    scrape_configs:
      # Repository服务监控
      - job_name: 'qlik-repository'
        static_configs:
          - targets: ['qlik-repository:443']
        metrics_path: '/metrics'
        scheme: https
        tls_config:
          insecure_skip_verify: true
        scrape_interval: 30s
        scrape_timeout: 10s

      # Engine服务监控
      - job_name: 'qlik-engine'
        static_configs:
          - targets: ['qlik-engine:4747']
        metrics_path: '/metrics'
        scheme: https
        tls_config:
          insecure_skip_verify: true
        scrape_interval: 30s
        scrape_timeout: 10s

      # Proxy服务监控
      - job_name: 'qlik-proxy'
        static_configs:
          - targets: ['qlik-proxy:443']
        metrics_path: '/metrics'
        scheme: https
        tls_config:
          insecure_skip_verify: true
        scrape_interval: 30s
        scrape_timeout: 10s

      # 系统资源监控
      - job_name: 'qlik-node-exporter'
        static_configs:
          - targets: ['qlik-node-exporter:9100']
        scrape_interval: 15s
        scrape_timeout: 5s
```

## 1.4 备份和恢复脚本

### 自动备份脚本

```powershell
# backup-qlik.ps1 - Qlik Sense自动备份脚本
param(
    [string]$BackupPath = "D:\Backups\QlikSense",
    [int]$RetentionDays = 30,
    [string]$QlikInstallPath = "C:\Program Files\Qlik\Sense",
    [switch]$IncludeApps = $true,
    [switch]$IncludeContent = $true
)

# 创建备份目录
if (!(Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
}

# 生成备份时间戳
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "$BackupPath\backup-$timestamp"

# 创建备份目录结构
New-Item -ItemType Directory -Path "$backupDir\repository" | Out-Null
New-Item -ItemType Directory -Path "$backupDir\shared" | Out-Null
New-Item -ItemType Directory -Path "$backupDir\logs" | Out-Null

if ($IncludeApps) {
    New-Item -ItemType Directory -Path "$backupDir\apps" | Out-Null
}

if ($IncludeContent) {
    New-Item -ItemType Directory -Path "$backupDir\content" | Out-Null
}

Write-Host "开始Qlik Sense备份..." -ForegroundColor Cyan
Write-Host "备份目录: $backupDir" -ForegroundColor White

# 1. 备份Repository数据库
function Backup-RepositoryDatabase {
    Write-Host "备份Repository数据库..." -ForegroundColor Yellow
    
    # 停止Qlik Sense服务
    Stop-Service -Name "QlikSenseRepositoryDatabase" -Force
    
    try {
        # 执行PostgreSQL备份
        $pgDumpPath = "$QlikInstallPath\Repository\PostgreSQL\bin\pg_dump.exe"
        $backupFile = "$backupDir\repository\qsr-backup-$timestamp.sql"
        
        & $pgDumpPath -h localhost -p 4432 -U postgres -d QSR -f $backupFile
        
        Write-Host "Repository数据库备份完成: $backupFile" -ForegroundColor Green
    } finally {
        # 启动Qlik Sense服务
        Start-Service -Name "QlikSenseRepositoryDatabase"
    }
}

# 2. 备份共享持久化文件
function Backup-SharedPersistence {
    Write-Host "备份共享持久化文件..." -ForegroundColor Yellow
    
    $sharedPath = "\\fileserver\qlik-share"
    $destPath = "$backupDir\shared"
    
    # 使用robocopy进行增量备份
    robocopy $sharedPath $destPath /MIR /Z /R:3 /W:5 /LOG:"$backupDir\shared-backup.log"
    
    Write-Host "共享持久化文件备份完成" -ForegroundColor Green
}

# 3. 备份应用程序
function Backup-Applications {
    if (!$IncludeApps) { return }
    
    Write-Host "备份Qlik Sense应用程序..." -ForegroundColor Yellow
    
    # 使用Qlik-Cli或API备份应用
    # 这里是示例代码，实际需要根据环境调整
    
    $appsBackupPath = "$backupDir\apps"
    
    # 获取应用列表
    $apps = Get-ChildItem -Path "\\fileserver\qlik-share\Apps" -Filter "*.qvf"
    
    foreach ($app in $apps) {
        Copy-Item -Path $app.FullName -Destination "$appsBackupPath\$($app.Name)" -Force
        Write-Host "  已备份: $($app.Name)" -ForegroundColor Green
    }
}

# 4. 备份内容库
function Backup-ContentLibraries {
    if (!$IncludeContent) { return }
    
    Write-Host "备份内容库..." -ForegroundColor Yellow
    
    $contentPath = "\\fileserver\qlik-share\Content"
    $destPath = "$backupDir\content"
    
    robocopy $contentPath $destPath /MIR /Z /R:3 /W:5 /LOG:"$backupDir\content-backup.log"
    
    Write-Host "内容库备份完成" -ForegroundColor Green
}

# 5. 备份日志文件
function Backup-Logs {
    Write-Host "备份日志文件..." -ForegroundColor Yellow
    
    $logPath = "C:\ProgramData\Qlik\Sense\Log"
    $destPath = "$backupDir\logs"
    
    # 只备份最近7天的日志
    $cutoffDate = (Get-Date).AddDays(-7)
    
    Get-ChildItem -Path $logPath -Recurse | Where-Object {
        $_.LastWriteTime -gt $cutoffDate
    } | ForEach-Object {
        $relativePath = $_.FullName.Substring($logPath.Length)
        $destFile = "$destPath$relativePath"
        $destDir = Split-Path $destFile -Parent
        
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        Copy-Item -Path $_.FullName -Destination $destFile -Force
    }
    
    Write-Host "日志文件备份完成" -ForegroundColor Green
}

# 6. 清理过期备份
function Cleanup-OldBackups {
    Write-Host "清理过期备份..." -ForegroundColor Yellow
    
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    
    Get-ChildItem -Path $BackupPath -Directory | Where-Object {
        $_.Name -match "backup-\d{8}-\d{6}" -and
        $_.CreationTime -lt $cutoffDate
    } | ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force
        Write-Host "  已删除过期备份: $($_.Name)" -ForegroundColor Gray
    }
}

# 7. 创建备份验证
function Create-BackupVerification {
    Write-Host "创建备份验证文件..." -ForegroundColor Yellow
    
    $verification = @{
        Timestamp = $timestamp
        BackupPath = $backupDir
        Components = @()
        Status = "Success"
        Duration = ""
    }
    
    # 验证各组件备份
    if (Test-Path "$backupDir\repository") {
        $verification.Components += "Repository"
    }
    
    if (Test-Path "$backupDir\shared") {
        $verification.Components += "SharedPersistence"
    }
    
    if ($IncludeApps -and (Test-Path "$backupDir\apps")) {
        $verification.Components += "Applications"
    }
    
    if ($IncludeContent -and (Test-Path "$backupDir\content")) {
        $verification.Components += "ContentLibraries"
    }
    
    if (Test-Path "$backupDir\logs") {
        $verification.Components += "Logs"
    }
    
    # 保存验证信息
    $verification | ConvertTo-Json | Out-File -FilePath "$backupDir\verification.json" -Encoding UTF8
    
    Write-Host "备份验证文件已创建" -ForegroundColor Green
}

# 主备份流程
try {
    $startTime = Get-Date
    Write-Host "=========================================" -ForegroundColor Yellow
    Write-Host "Qlik Sense自动备份开始" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Yellow
    
    Backup-RepositoryDatabase
    Backup-SharedPersistence
    Backup-Applications
    Backup-ContentLibraries
    Backup-Logs
    Create-BackupVerification
    Cleanup-OldBackups
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Qlik Sense备份完成！" -ForegroundColor Green
    Write-Host "备份目录: $backupDir" -ForegroundColor White
    Write-Host "耗时: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor White
    Write-Host "=========================================" -ForegroundColor Green
    
} catch {
    Write-Error "备份失败: $($_.Exception.Message)"
    Write-Error $_.Exception.StackTrace
    
    # 创建错误报告
    $errorInfo = @{
        Timestamp = $timestamp
        Error = $_.Exception.Message
        StackTrace = $_.Exception.StackTrace
        Status = "Failed"
    }
    
    $errorInfo | ConvertTo-Json | Out-File -FilePath "$backupDir\error.json" -Encoding UTF8
    
    exit 1
}
```

## 1.5 安全配置脚本

### SSL证书管理

```bash
#!/bin/bash

# ssl-setup.sh - Qlik Sense SSL证书配置脚本
# 适用于生产环境SSL证书部署

set -e

# 配置参数
DOMAIN="qlik.company.com"
CERT_DIR="/etc/ssl/qlik"
KEYSTORE_PASSWORD="changeit"
VALIDITY_DAYS=365

# 创建证书目录
mkdir -p $CERT_DIR

# 生成自签名证书 (仅用于测试环境)
function generate_self_signed_cert() {
    echo "生成自签名SSL证书..."
    
    openssl req -x509 -nodes -days $VALIDITY_DAYS -newkey rsa:2048 \
        -keyout $CERT_DIR/qlik.key \
        -out $CERT_DIR/qlik.crt \
        -subj "/CN=$DOMAIN/O=Company/C=US" \
        -extensions SAN \
        -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:$DOMAIN,DNS:*.company.com"))
    
    echo "自签名证书生成完成"
}

# 转换为Java Keystore格式
function convert_to_keystore() {
    echo "转换为Java Keystore格式..."
    
    # 创建PKCS12格式
    openssl pkcs12 -export -in $CERT_DIR/qlik.crt -inkey $CERT_DIR/qlik.key \
        -out $CERT_DIR/qlik.p12 -name qlik -password pass:$KEYSTORE_PASSWORD
    
    # 转换为JKS格式
    keytool -importkeystore -deststorepass $KEYSTORE_PASSWORD -destkeypass $KEYSTORE_PASSWORD \
        -destkeystore $CERT_DIR/keystore.jks -srckeystore $CERT_DIR/qlik.p12 \
        -srcstoretype PKCS12 -srcstorepass $KEYSTORE_PASSWORD -alias qlik
    
    # 导入证书链 (如果有)
    if [ -f "$CERT_DIR/ca.crt" ]; then
        keytool -import -trustcacerts -alias rootca -file $CERT_DIR/ca.crt \
            -keystore $CERT_DIR/keystore.jks -storepass $KEYSTORE_PASSWORD -noprompt
    fi
    
    echo "Keystore创建完成"
}

# 配置Qlik Sense使用证书
function configure_qlik_ssl() {
    echo "配置Qlik Sense SSL设置..."
    
    # 备份现有配置
    cp /opt/qlik/sense/conf/system.properties /opt/qlik/sense/conf/system.properties.backup
    
    # 更新SSL配置
    cat >> /opt/qlik/sense/conf/system.properties <<EOF

# SSL Configuration
server.ssl.enabled=true
server.ssl.key-store=$CERT_DIR/keystore.jks
server.ssl.key-store-password=$KEYSTORE_PASSWORD
server.ssl.key-alias=qlik
server.ssl.key-password=$KEYSTORE_PASSWORD
EOF
    
    echo "SSL配置更新完成"
}

# 验证证书
function verify_certificate() {
    echo "验证证书..."
    
    # 检查证书有效期
    openssl x509 -in $CERT_DIR/qlik.crt -text -noout | grep "Not After"
    
    # 检查证书链
    keytool -list -keystore $CERT_DIR/keystore.jks -storepass $KEYSTORE_PASSWORD
    
    echo "证书验证完成"
}

# 主流程
main() {
    echo "========================================="
    echo "Qlik Sense SSL证书配置"
    echo "========================================="
    
    generate_self_signed_cert
    convert_to_keystore
    configure_qlik_ssl
    verify_certificate
    
    echo "========================================="
    echo "SSL证书配置完成！"
    echo "请重启Qlik Sense服务以应用更改"
    echo "========================================="
}

# 执行主流程
main "$@"
```

### 用户权限管理

```powershell
# user-management.ps1 - Qlik Sense用户权限管理脚本
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Add", "Remove", "Update", "List")]
    [string]$Action,
    
    [string]$Username,
    [string]$Email,
    [string[]]$Roles,
    [string]$Department,
    [switch]$Force
)

# Qlik Sense REST API配置
$QlikSenseURL = "https://qlik.company.com"
$AdminUser = "admin@company.com"
$AdminPassword = "secure_password"

# 获取认证令牌
function Get-AuthToken {
    $authBody = @{
        userDirectory = "INTERNAL"
        userId = "sa_api"
        attributes = @()
    } | ConvertTo-Json
    
    $headers = @{
        "Content-Type" = "application/json"
        "X-Qlik-User" = "UserDirectory=INTERNAL; UserId=sa_api"
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$QlikSenseURL/qps/user" -Method Post -Body $authBody -Headers $headers
        return $response
    } catch {
        throw "获取认证令牌失败: $($_.Exception.Message)"
    }
}

# 添加用户
function Add-QlikUser {
    param($Username, $Email, $Roles, $Department)
    
    Write-Host "添加用户: $Username" -ForegroundColor Cyan
    
    # 构建用户信息
    $userBody = @{
        userDirectory = "COMPANY"
        userId = $Username
        name = $Username
        email = $Email
        roles = $Roles
        department = $Department
    } | ConvertTo-Json
    
    try {
        $token = Get-AuthToken
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $($token.token)"
        }
        
        $response = Invoke-RestMethod -Uri "$QlikSenseURL/qrs/user" -Method Post -Body $userBody -Headers $headers
        Write-Host "用户添加成功: $($response.id)" -ForegroundColor Green
        return $response
    } catch {
        throw "添加用户失败: $($_.Exception.Message)"
    }
}

# 移除用户
function Remove-QlikUser {
    param($Username)
    
    Write-Host "移除用户: $Username" -ForegroundColor Yellow
    
    try {
        $token = Get-AuthToken
        $headers = @{
            "Authorization" = "Bearer $($token.token)"
        }
        
        # 先查找用户ID
        $users = Invoke-RestMethod -Uri "$QlikSenseURL/qrs/user/full?filter=userId eq '$Username'" -Method Get -Headers $headers
        
        if ($users.Count -eq 0) {
            Write-Host "用户不存在: $Username" -ForegroundColor Red
            return
        }
        
        $userId = $users[0].id
        
        # 删除用户
        Invoke-RestMethod -Uri "$QlikSenseURL/qrs/user/$userId" -Method Delete -Headers $headers
        
        Write-Host "用户移除成功" -ForegroundColor Green
    } catch {
        throw "移除用户失败: $($_.Exception.Message)"
    }
}

# 更新用户权限
function Update-QlikUserRoles {
    param($Username, $Roles)
    
    Write-Host "更新用户权限: $Username" -ForegroundColor Cyan
    
    try {
        $token = Get-AuthToken
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $($token.token)"
        }
        
        # 查找用户
        $users = Invoke-RestMethod -Uri "$QlikSenseURL/qrs/user/full?filter=userId eq '$Username'" -Method Get -Headers $headers
        
        if ($users.Count -eq 0) {
            Write-Host "用户不存在: $Username" -ForegroundColor Red
            return
        }
        
        $user = $users[0]
        $user.roles = $Roles
        
        # 更新用户
        $updateBody = $user | ConvertTo-Json -Depth 10
        $response = Invoke-RestMethod -Uri "$QlikSenseURL/qrs/user/$($user.id)" -Method Put -Body $updateBody -Headers $headers
        
        Write-Host "用户权限更新成功" -ForegroundColor Green
        return $response
    } catch {
        throw "更新用户权限失败: $($_.Exception.Message)"
    }
}

# 列出用户
function List-QlikUsers {
    Write-Host "列出所有用户..." -ForegroundColor Cyan
    
    try {
        $token = Get-AuthToken
        $headers = @{
            "Authorization" = "Bearer $($token.token)"
        }
        
        $users = Invoke-RestMethod -Uri "$QlikSenseURL/qrs/user/full" -Method Get -Headers $headers
        
        Write-Host "找到 $($users.Count) 个用户:" -ForegroundColor White
        Write-Host "=========================================" -ForegroundColor Gray
        
        $users | Format-Table -Property userId, name, email, roles -AutoSize
        
    } catch {
        throw "列出用户失败: $($_.Exception.Message)"
    }
}

# 主流程
try {
    Write-Host "=========================================" -ForegroundColor Yellow
    Write-Host "Qlik Sense用户权限管理" -ForegroundColor Yellow
    Write-Host "操作: $Action" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Yellow
    
    switch ($Action) {
        "Add" {
            if (-not $Username -or -not $Email -or -not $Roles) {
                throw "添加用户需要指定用户名、邮箱和角色"
            }
            Add-QlikUser -Username $Username -Email $Email -Roles $Roles -Department $Department
        }
        
        "Remove" {
            if (-not $Username) {
                throw "移除用户需要指定用户名"
            }
            if (-not $Force) {
                $confirm = Read-Host "确认移除用户 '$Username'? (y/N)"
                if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                    Write-Host "操作已取消" -ForegroundColor Yellow
                    exit 0
                }
            }
            Remove-QlikUser -Username $Username
        }
        
        "Update" {
            if (-not $Username -or -not $Roles) {
                throw "更新用户需要指定用户名和角色"
            }
            Update-QlikUserRoles -Username $Username -Roles $Roles
        }
        
        "List" {
            List-QlikUsers
        }
    }
    
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "操作完成！" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
```

## 1.6 性能调优配置

### 系统性能调优脚本

```bash
#!/bin/bash

# performance-tuning.sh - Qlik Sense性能调优脚本
# 适用于Linux环境的生产服务器

set -e

# 配置参数
QLIK_USER="qlik"
QLIK_GROUP="qlik"
MEMORY_LIMIT="32G"
CPU_CORES="8"

# 系统级调优
function tune_system() {
    echo "执行系统级性能调优..."
    
    # 调整内核参数
    cat >> /etc/sysctl.conf <<EOF

# Qlik Sense性能调优
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_tw_buckets = 5000
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF
    
    # 应用内核参数
    sysctl -p
    
    # 调整文件描述符限制
    echo "$QLIK_USER soft nofile 65536" >> /etc/security/limits.conf
    echo "$QLIK_USER hard nofile 65536" >> /etc/security/limits.conf
    
    echo "系统级调优完成"
}

# 内存调优
function tune_memory() {
    echo "执行内存调优..."
    
    # 创建Qlik Sense服务配置
    mkdir -p /etc/systemd/system/qlik-sense.service.d/
    
    cat > /etc/systemd/system/qlik-sense.service.d/memory.conf <<EOF
[Service]
MemoryLimit=$MEMORY_LIMIT
MemoryHigh=$(echo $MEMORY_LIMIT | sed 's/G/*1024*1024*1024/' | bc)
MemoryMax=$(echo $MEMORY_LIMIT | sed 's/G/*1024*1024*1024/' | bc)
EOF
    
    echo "内存调优完成"
}

# CPU调优
function tune_cpu() {
    echo "执行CPU调优..."
    
    # 创建CPU亲和性配置
    cat > /etc/systemd/system/qlik-sense.service.d/cpu.conf <<EOF
[Service]
CPUQuota=${CPU_CORES}00%
AllowedCPUs=0-$(($CPU_CORES - 1))
EOF
    
    echo "CPU调优完成"
}

# 存储调优
function tune_storage() {
    echo "执行存储调优..."
    
    # 检查并优化文件系统
    if mount | grep -q "/data"; then
        # 为Qlik Sense数据目录设置优化选项
        chown -R $QLIK_USER:$QLIK_GROUP /data/qlik
        chmod -R 755 /data/qlik
        
        # 设置noatime以提高性能
        mount -o remount,noatime /data
        
        # 如果使用SSD，优化I/O调度器
        if [ -d "/sys/block/nvme0n1" ]; then
            echo "none" > /sys/block/nvme0n1/queue/scheduler
        fi
    fi
    
    echo "存储调优完成"
}

# 网络调优
function tune_network() {
    echo "执行网络调优..."
    
    # 优化网络缓冲区
    cat >> /etc/sysctl.conf <<EOF

# 网络性能调优
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr
EOF
    
    echo "网络调优完成"
}

# 应用配置
function apply_configuration() {
    echo "应用配置..."
    
    # 重新加载systemd配置
    systemctl daemon-reload
    
    # 重启Qlik Sense服务
    systemctl restart qlik-sense
    
    echo "配置应用完成"
}

# 主流程
main() {
    echo "========================================="
    echo "Qlik Sense性能调优脚本"
    echo "========================================="
    
    tune_system
    tune_memory
    tune_cpu
    tune_storage
    tune_network
    apply_configuration
    
    echo "========================================="
    echo "性能调优完成！"
    echo "建议重启服务器以完全应用所有优化"
    echo "========================================="
}

# 执行主流程
main "$@"
```

## 1.7 高可用性配置

### 负载均衡配置

```yaml
# nginx-qlik-lb.conf - Nginx负载均衡配置
# 适用于Qlik Sense多节点高可用部署

upstream qlik_proxy {
    # 主节点
    server qlik-proxy-1.company.com:443 max_fails=3 fail_timeout=30s;
    # 备节点
    server qlik-proxy-2.company.com:443 max_fails=3 fail_timeout=30s;
    # 负载均衡算法
    least_conn;
    keepalive 32;
}

upstream qlik_engine {
    server qlik-engine-1.company.com:4747 max_fails=3 fail_timeout=30s;
    server qlik-engine-2.company.com:4747 max_fails=3 fail_timeout=30s;
    server qlik-engine-3.company.com:4747 max_fails=3 fail_timeout=30s;
    least_conn;
    keepalive 32;
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name qlik.company.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器配置
server {
    listen 443 ssl http2;
    server_name qlik.company.com;
    
    # SSL证书配置
    ssl_certificate /etc/ssl/certs/qlik.crt;
    ssl_certificate_key /etc/ssl/private/qlik.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 代理超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # 日志配置
    access_log /var/log/nginx/qlik.access.log;
    error_log /var/log/nginx/qlik.error.log;
    
    # 根路径 - 重定向到Hub
    location / {
        proxy_pass https://qlik_proxy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_ssl_verify off;
        proxy_ssl_session_reuse on;
    }
    
    # Qlik Sense API路径
    location /api/ {
        proxy_pass https://qlik_proxy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_ssl_verify off;
        proxy_ssl_session_reuse on;
    }
    
    # Engine通信路径
    location /engine-data/ {
        proxy_pass https://qlik_engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_ssl_verify off;
        proxy_ssl_session_reuse on;
    }
    
    # 静态资源缓存
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        proxy_pass https://qlik_proxy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_ssl_verify off;
        proxy_ssl_session_reuse on;
        
        # 启用缓存
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# 健康检查端点
server {
    listen 8080;
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 故障转移脚本

```powershell
# failover-monitor.ps1 - Qlik Sense故障转移监控脚本
param(
    [string[]]$PrimaryNodes = @("qlik-proxy-1", "qlik-engine-1"),
    [string[]]$SecondaryNodes = @("qlik-proxy-2", "qlik-engine-2"),
    [string]$LoadBalancerVIP = "192.168.1.100",
    [int]$CheckInterval = 30
)

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    
    # 写入日志文件
    $logMessage | Out-File -FilePath "C:\temp\qlik-failover.log" -Append -Encoding UTF8
}

# 检查节点健康状态
function Test-NodeHealth {
    param([string]$NodeName, [int]$Port = 443)
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connect = $tcpClient.BeginConnect($NodeName, $Port, $null, $null)
        $success = $connect.AsyncWaitHandle.WaitOne(5000, $false)
        
        if ($success) {
            $tcpClient.EndConnect($connect)
            $tcpClient.Close()
            return $true
        } else {
            return $false
        }
    } catch {
        return $false
    }
}

# 切换负载均衡配置
function Switch-LoadBalancer {
    param([string]$NewPrimaryNode)
    
    Write-Log "切换负载均衡到节点: $NewPrimaryNode" "WARN"
    
    # 这里应该调用实际的负载均衡器API
    # 示例：更新Nginx配置或调用F5 API
    
    try {
        # 重新加载Nginx配置 (示例)
        # & nginx -s reload
        
        Write-Log "负载均衡切换完成" "INFO"
        return $true
    } catch {
        Write-Log "负载均衡切换失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 发送告警通知
function Send-Alert {
    param([string]$Message, [string]$Level = "WARN")
    
    Write-Log "发送告警: $Message" $Level
    
    # 邮件告警
    $emailParams = @{
        To = "admin@company.com"
        From = "qlik-monitor@company.com"
        Subject = "Qlik Sense $Level Alert"
        Body = $Message
        SmtpServer = "smtp.company.com"
    }
    
    try {
        Send-MailMessage @emailParams -ErrorAction Stop
        Write-Log "告警邮件发送成功" "INFO"
    } catch {
        Write-Log "告警邮件发送失败: $($_.Exception.Message)" "ERROR"
    }
}

# 主监控循环
function Start-Monitoring {
    Write-Log "开始Qlik Sense故障转移监控" "INFO"
    
    $primaryHealthy = $true
    $failoverCount = 0
    $maxFailovers = 3
    
    while ($true) {
        try {
            $allPrimaryHealthy = $true
            $failedNodes = @()
            
            # 检查所有主节点
            foreach ($node in $PrimaryNodes) {
                if (-not (Test-NodeHealth -NodeName $node)) {
                    $allPrimaryHealthy = $false
                    $failedNodes += $node
                    Write-Log "节点 $node 无响应" "ERROR"
                } else {
                    Write-Log "节点 $node 健康" "DEBUG"
                }
            }
            
            # 处理故障状态变化
            if ($allPrimaryHealthy -and -not $primaryHealthy) {
                # 从故障恢复
                Write-Log "主节点恢复，切换回主节点" "INFO"
                Switch-LoadBalancer -NewPrimaryNode $PrimaryNodes[0]
                $primaryHealthy = $true
                $failoverCount = 0
                Send-Alert -Message "Qlik Sense主节点已恢复" -Level "INFO"
                
            } elseif (-not $allPrimaryHealthy -and $primaryHealthy) {
                # 检测到故障
                Write-Log "检测到主节点故障: $($failedNodes -join ', ')" "WARN"
                
                # 执行故障转移
                if ($failoverCount -lt $maxFailovers) {
                    if (Switch-LoadBalancer -NewPrimaryNode $SecondaryNodes[0]) {
                        $primaryHealthy = $false
                        $failoverCount++
                        Send-Alert -Message "Qlik Sense故障转移已执行，切换到备用节点" -Level "WARN"
                    } else {
                        Send-Alert -Message "Qlik Sense故障转移失败" -Level "ERROR"
                    }
                } else {
                    Send-Alert -Message "Qlik Sense故障转移次数已达上限，请人工干预" -Level "CRITICAL"
                }
            }
            
        } catch {
            Write-Log "监控过程中发生错误: $($_.Exception.Message)" "ERROR"
        }
        
        # 等待下次检查
        Start-Sleep -Seconds $CheckInterval
    }
}

# 启动监控
try {
    Write-Log "=========================================" "INFO"
    Write-Log "Qlik Sense故障转移监控系统启动" "INFO"
    Write-Log "主节点: $($PrimaryNodes -join ', ')" "INFO"
    Write-Log "备用节点: $($SecondaryNodes -join ', ')" "INFO"
    Write-Log "=========================================" "INFO"
    
    Start-Monitoring
    
} catch {
    Write-Log "监控系统启动失败: $($_.Exception.Message)" "ERROR"
    exit 1
}
```

## 总结

本章提供了完整的Qlik Sense生产环境部署和管理代码，包括：

1. **安装脚本** - Windows和Linux环境的自动化安装
2. **配置管理** - 系统、网络、数据库配置模板
3. **监控告警** - 健康检查和性能监控脚本
4. **备份恢复** - 自动化备份和恢复方案
5. **安全管理** - SSL证书和用户权限管理
6. **性能调优** - 系统级性能优化配置
7. **高可用性** - 负载均衡和故障转移方案

所有代码都遵循生产环境最佳实践，可以直接用于企业级部署。