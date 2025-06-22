# ClickHouse Day 14: 项目实战管理脚本
# 实时数据分析平台部署和运维工具

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "start", "stop", "status", "monitor", "backup", "restore", "test", "cleanup", "scale", "update")]
    [string]$Action,
    
    [string]$Environment = "production",
    [string]$ConfigPath = "./configs/project-config.xml",
    [string]$LogPath = "./logs",
    [string]$BackupPath = "./backups",
    [int]$ShardCount = 3,
    [int]$ReplicaCount = 2,
    [switch]$Force,
    [switch]$Verbose
)

# 全局配置
$Global:ProjectConfig = @{
    Name = "ClickHouse Analytics Platform"
    Version = "1.0.0"
    Environment = $Environment
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    LogFile = Join-Path $LogPath "project-manager-$(Get-Date -Format 'yyyy-MM-dd').log"
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
    
    # 控制台输出
    switch ($Level) {
        "INFO" { Write-Host $logMessage -ForegroundColor Green }
        "WARN" { Write-Host $logMessage -ForegroundColor Yellow }
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "DEBUG" { if ($Verbose) { Write-Host $logMessage -ForegroundColor Gray } }
    }
    
    # 文件输出
    if (-not (Test-Path $LogPath)) {
        New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
    }
    Add-Content -Path $Global:ProjectConfig.LogFile -Value $logMessage
}

# 错误处理
function Handle-Error {
    param([string]$ErrorMessage, [bool]$Exit = $true)
    
    Write-Log "Error: $ErrorMessage" -Level "ERROR"
    if ($Exit) {
        exit 1
    }
}

# 检查依赖
function Test-Dependencies {
    Write-Log "检查系统依赖..." -Level "INFO"
    
    $dependencies = @(
        @{Name="Docker"; Command="docker --version"},
        @{Name="Docker Compose"; Command="docker-compose --version"},
        @{Name="ClickHouse Client"; Command="clickhouse-client --version"}
    )
    
    $missing = @()
    foreach ($dep in $dependencies) {
        try {
            $result = Invoke-Expression $dep.Command 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "$($dep.Name) 已安装: $($result.Split("`n")[0])" -Level "DEBUG"
            } else {
                $missing += $dep.Name
            }
        } catch {
            $missing += $dep.Name
        }
    }
    
    if ($missing.Count -gt 0) {
        Handle-Error "缺少依赖: $($missing -join ', ')"
    }
    
    Write-Log "所有依赖检查通过" -Level "INFO"
}

# 生成Docker Compose配置
function New-DockerComposeConfig {
    Write-Log "生成Docker Compose配置..." -Level "INFO"
    
    $composeContent = @"
version: '3.8'

services:
  # ZooKeeper集群
  zookeeper-1:
    image: zookeeper:3.7
    container_name: zk-1
    hostname: zk-1.analytics.local
    ports:
      - "2181:2181"
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=0.0.0.0:2888:3888;2181 server.2=zk-2:2888:3888;2181 server.3=zk-3:2888:3888;2181
    volumes:
      - zk1-data:/data
      - zk1-logs:/datalog
    networks:
      - clickhouse-net
    restart: unless-stopped

  zookeeper-2:
    image: zookeeper:3.7
    container_name: zk-2
    hostname: zk-2.analytics.local
    ports:
      - "2182:2181"
    environment:
      ZOO_MY_ID: 2
      ZOO_SERVERS: server.1=zk-1:2888:3888;2181 server.2=0.0.0.0:2888:3888;2181 server.3=zk-3:2888:3888;2181
    volumes:
      - zk2-data:/data
      - zk2-logs:/datalog
    networks:
      - clickhouse-net
    restart: unless-stopped

  zookeeper-3:
    image: zookeeper:3.7
    container_name: zk-3
    hostname: zk-3.analytics.local
    ports:
      - "2183:2181"
    environment:
      ZOO_MY_ID: 3
      ZOO_SERVERS: server.1=zk-1:2888:3888;2181 server.2=zk-2:2888:3888;2181 server.3=0.0.0.0:2888:3888;2181
    volumes:
      - zk3-data:/data
      - zk3-logs:/datalog
    networks:
      - clickhouse-net
    restart: unless-stopped

"@

    # 生成ClickHouse节点配置
    for ($shard = 1; $shard -le $ShardCount; $shard++) {
        for ($replica = 1; $replica -le $ReplicaCount; $replica++) {
            $nodeName = "ch-shard$shard-replica$replica"
            $httpPort = 8120 + ($shard - 1) * 10 + $replica
            $tcpPort = 9000 + ($shard - 1) * 10 + $replica
            
            $composeContent += @"
  $nodeName`:
    image: clickhouse/clickhouse-server:latest
    container_name: $nodeName
    hostname: $nodeName
    ports:
      - "$httpPort`:8123"
      - "$tcpPort`:9000"
    environment:
      CLICKHOUSE_DB: analytics
      CLICKHOUSE_USER: analytics_user
      CLICKHOUSE_PASSWORD: Analytics@2024
    volumes:
      - ./configs/project-config.xml:/etc/clickhouse-server/config.d/project-config.xml
      - ./configs/macros-shard$shard-replica$replica.xml:/etc/clickhouse-server/config.d/macros.xml
      - $nodeName-data:/var/lib/clickhouse
      - $nodeName-logs:/var/log/clickhouse-server
    depends_on:
      - zookeeper-1
      - zookeeper-2  
      - zookeeper-3
    networks:
      - clickhouse-net
    restart: unless-stopped
    ulimits:
      nofile:
        soft: 262144
        hard: 262144

"@
        }
    }

    # 添加Kafka集群
    $composeContent += @"
  # Kafka集群
  kafka-1:
    image: confluentinc/cp-kafka:latest
    container_name: kafka-1
    hostname: kafka1
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zk-1:2181,zk-2:2181,zk-3:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_METRIC_REPORTERS: io.confluent.metrics.reporter.ConfluentMetricsReporter
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_CONFLUENT_METRICS_REPORTER_BOOTSTRAP_SERVERS: kafka1:29092
      KAFKA_CONFLUENT_METRICS_REPORTER_TOPIC_REPLICAS: 3
      KAFKA_CONFLUENT_METRICS_ENABLE: 'true'
      KAFKA_CONFLUENT_SUPPORT_CUSTOMER_ID: anonymous
    volumes:
      - kafka1-data:/var/lib/kafka/data
    networks:
      - clickhouse-net
    restart: unless-stopped

  kafka-2:
    image: confluentinc/cp-kafka:latest
    container_name: kafka-2
    hostname: kafka2
    ports:
      - "9093:9092"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zk-1:2181,zk-2:2181,zk-3:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:29092,PLAINTEXT_HOST://localhost:9093
      KAFKA_METRIC_REPORTERS: io.confluent.metrics.reporter.ConfluentMetricsReporter
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_CONFLUENT_METRICS_REPORTER_BOOTSTRAP_SERVERS: kafka2:29092
      KAFKA_CONFLUENT_METRICS_REPORTER_TOPIC_REPLICAS: 3
      KAFKA_CONFLUENT_METRICS_ENABLE: 'true'
      KAFKA_CONFLUENT_SUPPORT_CUSTOMER_ID: anonymous
    volumes:
      - kafka2-data:/var/lib/kafka/data
    networks:
      - clickhouse-net
    restart: unless-stopped

  kafka-3:
    image: confluentinc/cp-kafka:latest
    container_name: kafka-3
    hostname: kafka3
    ports:
      - "9094:9092"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zk-1:2181,zk-2:2181,zk-3:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:29092,PLAINTEXT_HOST://localhost:9094
      KAFKA_METRIC_REPORTERS: io.confluent.metrics.reporter.ConfluentMetricsReporter
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_CONFLUENT_METRICS_REPORTER_BOOTSTRAP_SERVERS: kafka3:29092
      KAFKA_CONFLUENT_METRICS_REPORTER_TOPIC_REPLICAS: 3
      KAFKA_CONFLUENT_METRICS_ENABLE: 'true'
      KAFKA_CONFLUENT_SUPPORT_CUSTOMER_ID: anonymous
    volumes:
      - kafka3-data:/var/lib/kafka/data
    networks:
      - clickhouse-net
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: redis-cache
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass Redis@2024
    volumes:
      - redis-data:/data
    networks:
      - clickhouse-net
    restart: unless-stopped

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - clickhouse-net
    restart: unless-stopped

  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: Grafana@2024
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - clickhouse-net
    restart: unless-stopped

volumes:
"@

    # 添加数据卷配置
    $volumes = @("zk1-data", "zk1-logs", "zk2-data", "zk2-logs", "zk3-data", "zk3-logs")
    $volumes += @("kafka1-data", "kafka2-data", "kafka3-data", "redis-data", "prometheus-data", "grafana-data")
    
    for ($shard = 1; $shard -le $ShardCount; $shard++) {
        for ($replica = 1; $replica -le $ReplicaCount; $replica++) {
            $nodeName = "ch-shard$shard-replica$replica"
            $volumes += @("$nodeName-data", "$nodeName-logs")
        }
    }
    
    foreach ($volume in $volumes) {
        $composeContent += "`n  $volume`:"
    }

    $composeContent += @"

networks:
  clickhouse-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
"@

    # 保存配置文件
    $composeFile = "docker-compose.yml"
    Set-Content -Path $composeFile -Value $composeContent
    Write-Log "Docker Compose配置已生成: $composeFile" -Level "INFO"
}

# 生成宏配置文件
function New-MacroConfigs {
    Write-Log "生成宏配置文件..." -Level "INFO"
    
    if (-not (Test-Path "configs")) {
        New-Item -ItemType Directory -Path "configs" -Force | Out-Null
    }
    
    for ($shard = 1; $shard -le $ShardCount; $shard++) {
        for ($replica = 1; $replica -le $ReplicaCount; $replica++) {
            $macroContent = @"
<?xml version="1.0"?>
<yandex>
    <macros>
        <cluster>analytics_cluster</cluster>
        <shard>$('{0:D2}' -f $shard)</shard>
        <replica>replica-$replica</replica>
        <layer>$Environment</layer>
    </macros>
</yandex>
"@
            $macroFile = "configs/macros-shard$shard-replica$replica.xml"
            Set-Content -Path $macroFile -Value $macroContent
            Write-Log "生成宏配置: $macroFile" -Level "DEBUG"
        }
    }
}

# 生成Prometheus配置
function New-PrometheusConfig {
    Write-Log "生成Prometheus配置..." -Level "INFO"
    
    $prometheusContent = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'clickhouse'
    static_configs:
"@

    for ($shard = 1; $shard -le $ShardCount; $shard++) {
        for ($replica = 1; $replica -le $ReplicaCount; $replica++) {
            $httpPort = 8120 + ($shard - 1) * 10 + $replica
            $prometheusContent += "`n      - targets: ['localhost:$httpPort']"
        }
    }

    $prometheusContent += @"

  - job_name: 'kafka'
    static_configs:
      - targets: ['localhost:9092', 'localhost:9093', 'localhost:9094']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
"@

    Set-Content -Path "configs/prometheus.yml" -Value $prometheusContent
    Write-Log "Prometheus配置已生成" -Level "INFO"
}

# 部署项目
function Deploy-Project {
    Write-Log "开始部署 $($Global:ProjectConfig.Name)..." -Level "INFO"
    
    try {
        # 检查依赖
        Test-Dependencies
        
        # 生成配置文件
        New-DockerComposeConfig
        New-MacroConfigs
        New-PrometheusConfig
        
        # 启动服务
        Write-Log "启动Docker服务..." -Level "INFO"
        $result = docker-compose up -d 2>&1
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Docker服务启动失败: $result"
        }
        
        # 等待服务启动
        Write-Log "等待服务启动..." -Level "INFO"
        Start-Sleep -Seconds 30
        
        # 初始化数据库
        Initialize-Database
        
        # 验证部署
        Test-Deployment
        
        Write-Log "项目部署完成!" -Level "INFO"
        
    } catch {
        Handle-Error "部署失败: $($_.Exception.Message)"
    }
}

# 初始化数据库
function Initialize-Database {
    Write-Log "初始化数据库..." -Level "INFO"
    
    # 等待ClickHouse启动
    $maxRetries = 30
    $retryCount = 0
    
    do {
        try {
            $result = clickhouse-client --host localhost --port 9001 --query "SELECT 1" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "ClickHouse连接成功" -Level "INFO"
                break
            }
        } catch {
            # 忽略连接错误
        }
        
        $retryCount++
        Write-Log "等待ClickHouse启动... ($retryCount/$maxRetries)" -Level "DEBUG"
        Start-Sleep -Seconds 10
    } while ($retryCount -lt $maxRetries)
    
    if ($retryCount -ge $maxRetries) {
        Handle-Error "ClickHouse启动超时"
    }
    
    # 执行初始化SQL
    $sqlFile = "./examples/project-demo.sql"
    if (Test-Path $sqlFile) {
        Write-Log "执行初始化SQL..." -Level "INFO"
        $result = clickhouse-client --host localhost --port 9001 --multiquery --queries-file $sqlFile 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "SQL执行警告: $result" -Level "WARN"
        } else {
            Write-Log "数据库初始化完成" -Level "INFO"
        }
    }
}

# 测试部署
function Test-Deployment {
    Write-Log "验证部署状态..." -Level "INFO"
    
    # 检查容器状态
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String -Pattern "(zk-|ch-|kafka-|redis|prometheus|grafana)"
    Write-Log "运行中的容器:" -Level "INFO"
    $containers | ForEach-Object { Write-Log $_.Line -Level "INFO" }
    
    # 检查ClickHouse集群状态
    try {
        $clusterStatus = clickhouse-client --host localhost --port 9001 --query "SELECT * FROM system.clusters WHERE cluster = 'analytics_cluster'" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "ClickHouse集群状态正常" -Level "INFO"
        } else {
            Write-Log "ClickHouse集群状态检查失败" -Level "WARN"
        }
    } catch {
        Write-Log "无法检查ClickHouse集群状态" -Level "WARN"
    }
    
    # 检查Kafka主题
    try {
        $topics = docker exec kafka-1 kafka-topics --bootstrap-server localhost:9092 --list 2>$null
        Write-Log "Kafka主题: $topics" -Level "DEBUG"
    } catch {
        Write-Log "无法检查Kafka主题" -Level "WARN"
    }
}

# 启动服务
function Start-Services {
    Write-Log "启动所有服务..." -Level "INFO"
    
    try {
        $result = docker-compose start 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "服务启动成功" -Level "INFO"
            Get-ServiceStatus
        } else {
            Handle-Error "服务启动失败: $result"
        }
    } catch {
        Handle-Error "启动服务时发生错误: $($_.Exception.Message)"
    }
}

# 停止服务
function Stop-Services {
    Write-Log "停止所有服务..." -Level "INFO"
    
    try {
        $result = docker-compose stop 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "服务停止成功" -Level "INFO"
        } else {
            Handle-Error "服务停止失败: $result" -Exit $false
        }
    } catch {
        Handle-Error "停止服务时发生错误: $($_.Exception.Message)" -Exit $false
    }
}

# 获取服务状态
function Get-ServiceStatus {
    Write-Log "检查服务状态..." -Level "INFO"
    
    # Docker容器状态
    Write-Host "`n=== Docker容器状态 ===" -ForegroundColor Cyan
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # ClickHouse集群状态
    Write-Host "`n=== ClickHouse集群状态 ===" -ForegroundColor Cyan
    try {
        clickhouse-client --host localhost --port 9001 --query "
        SELECT 
            hostname() as node,
            database,
            table,
            active,
            is_leader,
            absolute_delay,
            log_max_index - log_pointer as replication_lag
        FROM system.replicas 
        WHERE database = 'analytics'
        FORMAT PrettyCompact
        " 2>$null
    } catch {
        Write-Log "无法获取ClickHouse集群状态" -Level "WARN"
    }
    
    # 系统资源使用
    Write-Host "`n=== 系统资源使用 ===" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# 监控服务
function Monitor-Services {
    Write-Log "启动服务监控..." -Level "INFO"
    
    while ($true) {
        Clear-Host
        Write-Host "=== $($Global:ProjectConfig.Name) 监控面板 ===" -ForegroundColor Green
        Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
        Write-Host "环境: $Environment" -ForegroundColor Gray
        Write-Host ""
        
        # 获取服务状态
        Get-ServiceStatus
        
        # 检查告警
        Write-Host "`n=== 系统告警 ===" -ForegroundColor Yellow
        try {
            $alerts = clickhouse-client --host localhost --port 9001 --query "
            SELECT 
                alert_time,
                alert_type,
                severity,
                service_name,
                message
            FROM analytics.alerts 
            WHERE alert_time >= now() - INTERVAL 5 MINUTE 
                AND resolved = 0
            ORDER BY alert_time DESC
            LIMIT 10
            FORMAT PrettyCompact
            " 2>$null
            
            if ($alerts) {
                Write-Host $alerts
            } else {
                Write-Host "无活跃告警" -ForegroundColor Green
            }
        } catch {
            Write-Host "无法获取告警信息" -ForegroundColor Red
        }
        
        Write-Host "`n按 Ctrl+C 退出监控..." -ForegroundColor Gray
        Start-Sleep -Seconds 30
    }
}

# 备份数据
function Backup-Data {
    Write-Log "开始数据备份..." -Level "INFO"
    
    try {
        $backupDir = Join-Path $BackupPath "backup-$(Get-Date -Format 'yyyy-MM-dd-HH-mm-ss')"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        # 备份ClickHouse数据
        Write-Log "备份ClickHouse数据..." -Level "INFO"
        $tables = @("user_events", "app_metrics", "error_logs", "alerts")
        
        foreach ($table in $tables) {
            $backupFile = Join-Path $backupDir "$table.sql"
            $query = "SELECT * FROM analytics.$table FORMAT TabSeparated"
            
            clickhouse-client --host localhost --port 9001 --query $query > $backupFile 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "表 $table 备份完成: $backupFile" -Level "DEBUG"
            } else {
                Write-Log "表 $table 备份失败" -Level "WARN"
            }
        }
        
        # 备份配置文件
        Write-Log "备份配置文件..." -Level "INFO"
        Copy-Item -Path "configs" -Destination (Join-Path $backupDir "configs") -Recurse -Force
        Copy-Item -Path "docker-compose.yml" -Destination $backupDir -Force
        
        # 创建备份信息文件
        $backupInfo = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Environment = $Environment
            Version = $Global:ProjectConfig.Version
            Tables = $tables
            ConfigFiles = @("project-config.xml", "prometheus.yml")
        } | ConvertTo-Json -Depth 3
        
        Set-Content -Path (Join-Path $backupDir "backup-info.json") -Value $backupInfo
        
        # 压缩备份
        $zipFile = "$backupDir.zip"
        Compress-Archive -Path $backupDir -DestinationPath $zipFile -Force
        Remove-Item -Path $backupDir -Recurse -Force
        
        Write-Log "数据备份完成: $zipFile" -Level "INFO"
        
    } catch {
        Handle-Error "备份失败: $($_.Exception.Message)" -Exit $false
    }
}

# 恢复数据
function Restore-Data {
    param([string]$BackupFile)
    
    if (-not $BackupFile) {
        # 列出可用备份
        $backups = Get-ChildItem -Path $BackupPath -Filter "backup-*.zip" | Sort-Object LastWriteTime -Descending
        if ($backups.Count -eq 0) {
            Handle-Error "未找到备份文件"
        }
        
        Write-Host "可用备份文件:" -ForegroundColor Cyan
        for ($i = 0; $i -lt $backups.Count; $i++) {
            Write-Host "$($i + 1). $($backups[$i].Name) - $($backups[$i].LastWriteTime)" -ForegroundColor White
        }
        
        $selection = Read-Host "请选择要恢复的备份 (1-$($backups.Count))"
        if ($selection -match '^\d+$' -and [int]$selection -ge 1 -and [int]$selection -le $backups.Count) {
            $BackupFile = $backups[[int]$selection - 1].FullName
        } else {
            Handle-Error "无效选择"
        }
    }
    
    Write-Log "开始数据恢复: $BackupFile" -Level "INFO"
    
    try {
        # 解压备份文件
        $tempDir = Join-Path $env:TEMP "clickhouse-restore-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Expand-Archive -Path $BackupFile -DestinationPath $tempDir -Force
        
        # 读取备份信息
        $backupInfoFile = Join-Path $tempDir "backup-info.json"
        if (Test-Path $backupInfoFile) {
            $backupInfo = Get-Content $backupInfoFile | ConvertFrom-Json
            Write-Log "备份信息: 时间=$($backupInfo.Timestamp), 环境=$($backupInfo.Environment)" -Level "INFO"
        }
        
        # 恢复表数据
        $sqlFiles = Get-ChildItem -Path $tempDir -Filter "*.sql"
        foreach ($sqlFile in $sqlFiles) {
            $tableName = [System.IO.Path]::GetFileNameWithoutExtension($sqlFile.Name)
            Write-Log "恢复表: $tableName" -Level "INFO"
            
            # 清空现有数据
            clickhouse-client --host localhost --port 9001 --query "TRUNCATE TABLE analytics.$tableName" 2>$null
            
            # 导入数据
            $importQuery = "INSERT INTO analytics.$tableName FORMAT TabSeparated"
            Get-Content $sqlFile.FullName | clickhouse-client --host localhost --port 9001 --query $importQuery 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "表 $tableName 恢复完成" -Level "DEBUG"
            } else {
                Write-Log "表 $tableName 恢复失败" -Level "WARN"
            }
        }
        
        # 清理临时文件
        Remove-Item -Path $tempDir -Recurse -Force
        
        Write-Log "数据恢复完成" -Level "INFO"
        
    } catch {
        Handle-Error "恢复失败: $($_.Exception.Message)" -Exit $false
    }
}

# 运行测试
function Run-Tests {
    Write-Log "运行系统测试..." -Level "INFO"
    
    $testResults = @()
    
    # 连接测试
    Write-Log "测试ClickHouse连接..." -Level "DEBUG"
    try {
        $result = clickhouse-client --host localhost --port 9001 --query "SELECT 1" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $testResults += @{Test="ClickHouse连接"; Status="PASS"; Message="连接正常"}
        } else {
            $testResults += @{Test="ClickHouse连接"; Status="FAIL"; Message="连接失败"}
        }
    } catch {
        $testResults += @{Test="ClickHouse连接"; Status="FAIL"; Message=$_.Exception.Message}
    }
    
    # 集群测试
    Write-Log "测试集群状态..." -Level "DEBUG"
    try {
        $clusterNodes = clickhouse-client --host localhost --port 9001 --query "SELECT count() FROM system.clusters WHERE cluster = 'analytics_cluster'" 2>$null
        if ($LASTEXITCODE -eq 0 -and [int]$clusterNodes -gt 0) {
            $testResults += @{Test="集群状态"; Status="PASS"; Message="集群节点数: $clusterNodes"}
        } else {
            $testResults += @{Test="集群状态"; Status="FAIL"; Message="集群配置异常"}
        }
    } catch {
        $testResults += @{Test="集群状态"; Status="FAIL"; Message=$_.Exception.Message}
    }
    
    # 数据写入测试
    Write-Log "测试数据写入..." -Level "DEBUG"
    try {
        $testQuery = @"
INSERT INTO analytics.user_events_local VALUES 
(now(), 999999, 'test_session', 'test_event', '/test', '', 'Test Agent', '127.0.0.1', 'Test', 'Test', 'desktop', 'Chrome', 'Windows', '1920x1080', map('test', 'value'))
"@
        clickhouse-client --host localhost --port 9001 --query $testQuery 2>$null
        if ($LASTEXITCODE -eq 0) {
            $testResults += @{Test="数据写入"; Status="PASS"; Message="写入成功"}
        } else {
            $testResults += @{Test="数据写入"; Status="FAIL"; Message="写入失败"}
        }
    } catch {
        $testResults += @{Test="数据写入"; Status="FAIL"; Message=$_.Exception.Message}
    }
    
    # 数据查询测试
    Write-Log "测试数据查询..." -Level "DEBUG"
    try {
        $count = clickhouse-client --host localhost --port 9001 --query "SELECT count() FROM analytics.user_events WHERE user_id = 999999" 2>$null
        if ($LASTEXITCODE -eq 0 -and [int]$count -gt 0) {
            $testResults += @{Test="数据查询"; Status="PASS"; Message="查询到 $count 条记录"}
        } else {
            $testResults += @{Test="数据查询"; Status="FAIL"; Message="查询失败或无数据"}
        }
    } catch {
        $testResults += @{Test="数据查询"; Status="FAIL"; Message=$_.Exception.Message}
    }
    
    # 清理测试数据
    try {
        clickhouse-client --host localhost --port 9001 --query "DELETE FROM analytics.user_events_local WHERE user_id = 999999" 2>$null
    } catch {
        # 忽略清理错误
    }
    
    # 输出测试结果
    Write-Host "`n=== 测试结果 ===" -ForegroundColor Cyan
    foreach ($result in $testResults) {
        $color = if ($result.Status -eq "PASS") { "Green" } else { "Red" }
        Write-Host "$($result.Test): $($result.Status) - $($result.Message)" -ForegroundColor $color
    }
    
    $passCount = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
    $totalCount = $testResults.Count
    Write-Host "`n测试完成: $passCount/$totalCount 通过" -ForegroundColor $(if ($passCount -eq $totalCount) { "Green" } else { "Yellow" })
}

# 清理环境
function Clean-Environment {
    Write-Log "清理环境..." -Level "INFO"
    
    if (-not $Force) {
        $confirm = Read-Host "确定要清理所有数据吗? 这将删除所有容器和数据卷 (y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-Log "操作已取消" -Level "INFO"
            return
        }
    }
    
    try {
        # 停止并删除容器
        Write-Log "停止并删除容器..." -Level "INFO"
        docker-compose down -v 2>&1 | Out-Null
        
        # 删除未使用的网络
        Write-Log "清理Docker网络..." -Level "INFO"
        docker network prune -f 2>&1 | Out-Null
        
        # 删除未使用的镜像
        if ($Force) {
            Write-Log "清理Docker镜像..." -Level "INFO"
            docker image prune -f 2>&1 | Out-Null
        }
        
        Write-Log "环境清理完成" -Level "INFO"
        
    } catch {
        Handle-Error "清理失败: $($_.Exception.Message)" -Exit $false
    }
}

# 扩展集群
function Scale-Cluster {
    param([int]$NewShardCount, [int]$NewReplicaCount)
    
    if (-not $NewShardCount) { $NewShardCount = $ShardCount }
    if (-not $NewReplicaCount) { $NewReplicaCount = $ReplicaCount }
    
    Write-Log "扩展集群: 分片=$NewShardCount, 副本=$NewReplicaCount" -Level "INFO"
    
    # 更新全局配置
    $Global:ShardCount = $NewShardCount
    $Global:ReplicaCount = $NewReplicaCount
    
    # 重新生成配置
    New-DockerComposeConfig
    New-MacroConfigs
    
    # 重启服务
    Write-Log "重启服务以应用新配置..." -Level "INFO"
    docker-compose up -d --scale 2>&1 | Out-Null
    
    Write-Log "集群扩展完成" -Level "INFO"
}

# 更新系统
function Update-System {
    Write-Log "更新系统..." -Level "INFO"
    
    try {
        # 拉取最新镜像
        Write-Log "拉取最新Docker镜像..." -Level "INFO"
        docker-compose pull 2>&1 | Out-Null
        
        # 重启服务
        Write-Log "重启服务..." -Level "INFO"
        docker-compose up -d 2>&1 | Out-Null
        
        # 验证更新
        Write-Log "验证更新..." -Level "INFO"
        Start-Sleep -Seconds 10
        Test-Deployment
        
        Write-Log "系统更新完成" -Level "INFO"
        
    } catch {
        Handle-Error "更新失败: $($_.Exception.Message)" -Exit $false
    }
}

# 主函数
function Main {
    Write-Host "=== $($Global:ProjectConfig.Name) v$($Global:ProjectConfig.Version) ===" -ForegroundColor Green
    Write-Host "操作: $Action" -ForegroundColor Cyan
    Write-Host "环境: $Environment" -ForegroundColor Cyan
    Write-Host "时间: $($Global:ProjectConfig.Timestamp)" -ForegroundColor Gray
    Write-Host ""
    
    switch ($Action.ToLower()) {
        "deploy" { Deploy-Project }
        "start" { Start-Services }
        "stop" { Stop-Services }
        "status" { Get-ServiceStatus }
        "monitor" { Monitor-Services }
        "backup" { Backup-Data }
        "restore" { Restore-Data }
        "test" { Run-Tests }
        "cleanup" { Clean-Environment }
        "scale" { Scale-Cluster -NewShardCount $ShardCount -NewReplicaCount $ReplicaCount }
        "update" { Update-System }
        default { Handle-Error "未知操作: $Action" }
    }
}

# 执行主函数
try {
    Main
} catch {
    Handle-Error "脚本执行失败: $($_.Exception.Message)"
} finally {
    Write-Log "脚本执行完成" -Level "INFO"
} 