# Day 1: ClickHouse 环境搭建与配置 (Windows 国内用户专版)

## 学习目标 🎯
- 掌握Windows环境下ClickHouse的Docker安装
- 学会配置文件的实际操作和安全设置
- 理解ClickHouse的基本配置和优化
- 掌握连接测试和基本运维命令

## 为什么选择Docker？ 🤔

对于国内Windows用户，Docker是最佳选择：
- ✅ **环境隔离**: 不影响本机系统
- ✅ **快速部署**: 几分钟即可完成安装
- ✅ **版本管理**: 轻松切换不同版本
- ✅ **配置灵活**: 支持自定义配置
- ✅ **故障恢复**: 容器重建快速

## 前置准备 📋

### 系统要求
- **操作系统**: Windows 10 版本2004及以上 或 Windows 11
- **内存**: 最少4GB，推荐8GB+
- **存储**: 至少20GB可用空间
- **网络**: 稳定的互联网连接（用于下载镜像）

### 软件准备
- Docker Desktop for Windows
- PowerShell 5.1+ 或 PowerShell Core 7+
- 文本编辑器（推荐VS Code）

## 第一步：安装Docker Desktop 🐳

### 1.1 下载Docker Desktop

**国内用户推荐下载方式:**
```powershell
# Method 1: Official download (may be slow)
# Visit: https://www.docker.com/products/docker-desktop/

# Method 2: Domestic mirror site (recommended)
# Visit: https://mirrors.tuna.tsinghua.edu.cn/docker-ce/win/static/stable/x86_64/
```

### 1.2 安装Docker Desktop

1. **运行安装程序**
   ```powershell
   # Run the installer as administrator
   # Docker Desktop Installer.exe
   ```

2. **安装配置选择**
   - ✅ Enable Hyper-V Windows Features
   - ✅ Install required Windows components for WSL 2
   - ✅ Add shortcut to desktop

3. **重启系统**
   ```powershell
   # Restart computer after installation
   Restart-Computer
   ```

### 1.3 配置Docker Desktop

**启动Docker Desktop后进行以下配置:**

1. **配置国内镜像源** (重要!)
   ```json
   {
     "registry-mirrors": [
       "https://docker.xuanyuan.me"
     ],
     "insecure-registries": [],
     "debug": false,
     "experimental": false
   }
   ```

2. **资源配置**
   - Memory: 4GB (最少) / 8GB (推荐)
   - CPU: 2 cores (最少) / 4 cores (推荐)
   - Disk image size: 60GB+

### 1.4 验证Docker安装

```powershell
# Check Docker version
docker --version
# Expected output: Docker version 24.0.x, build xxx

# Check Docker running status
docker info
# Check for error messages

# Test Docker functionality
docker run hello-world
# Should display "Hello from Docker!" message
```

## 第二步：一键安装ClickHouse 🏠

### 2.1 使用自动化安装脚本 (推荐)

**下载并运行专用安装脚本:**
```powershell
# Create working directory
New-Item -ItemType Directory -Path "C:\ClickHouse" -Force
Set-Location "C:\ClickHouse"

# Download installation script (from Day1 code directory)
# Copy docker-install-windows.ps1 to current directory

# Run one-click installation script
powershell -ExecutionPolicy Bypass -File "docker-install-windows.ps1"
```

**脚本功能特性:**
- ✅ 自动检测系统环境和Docker状态
- ✅ 配置国内镜像源加速下载
- ✅ 生成安全的配置文件
- ✅ 创建加密密码和用户账户
- ✅ 启动容器并验证安装
- ✅ 生成管理脚本和文档

### 2.2 手动安装步骤详解

如果需要了解详细步骤或自定义安装，可以按以下步骤操作：

#### 2.2.1 创建工作目录

```powershell
# Create ClickHouse working directory
New-Item -ItemType Directory -Path "C:\ClickHouse" -Force
Set-Location "C:\ClickHouse"

# Create subdirectories
$dirs = @("data", "logs", "config", "backups", "scripts")
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force
}
```

#### 2.2.2 下载ClickHouse镜像

```powershell
# Pull official ClickHouse image
docker pull clickhouse/clickhouse-server:latest

# If download is slow, use domestic mirror
docker pull registry.cn-hangzhou.aliyuncs.com/clickhouse/clickhouse-server:latest
docker tag registry.cn-hangzhou.aliyuncs.com/clickhouse/clickhouse-server:latest clickhouse/clickhouse-server:latest

# Verify image
docker images | Select-String "clickhouse"
```

#### 2.2.3 创建ClickHouse配置文件

**创建主配置文件 config.xml:**
```powershell
# Create config.xml
@"
<?xml version="1.0"?>
<yandex>
    <!-- Network configuration -->
    <listen_host>0.0.0.0</listen_host>
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    <mysql_port>9004</mysql_port>
    
    <!-- Data path configuration -->
    <path>/var/lib/clickhouse/</path>
    <tmp_path>/var/lib/clickhouse/tmp/</tmp_path>
    <user_files_path>/var/lib/clickhouse/user_files/</user_files_path>
    
    <!-- Log configuration -->
    <logger>
        <level>information</level>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>10</count>
    </logger>
    
    <!-- Memory configuration -->
    <max_server_memory_usage>0</max_server_memory_usage>
    <max_server_memory_usage_to_ram_ratio>0.8</max_server_memory_usage_to_ram_ratio>
    
    <!-- Performance configuration -->
    <max_concurrent_queries>100</max_concurrent_queries>
    <max_connections>4096</max_connections>
    <keep_alive_timeout>3</keep_alive_timeout>
    <max_session_timeout>3600</max_session_timeout>
    
    <!-- Timezone configuration -->
    <timezone>Asia/Shanghai</timezone>
</yandex>
"@ | Out-File -FilePath "config\config.xml" -Encoding UTF8
```

**配置文件详解:**
- `listen_host`: 监听地址，0.0.0.0表示监听所有网卡
- `http_port`: HTTP接口端口，用于REST API
- `tcp_port`: 原生客户端端口，用于clickhouse-client连接
- `mysql_port`: MySQL兼容协议端口
- `max_server_memory_usage_to_ram_ratio`: 限制服务器内存使用比例
- `timezone`: 设置时区为中国标准时间

#### 2.2.4 创建用户配置文件 (重要安全配置)

**生成密码哈希:**
```powershell
# Generate encrypted password
$plainPassword = "ClickHouse@2024"

# Calculate SHA256 hash
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($plainPassword))
$passwordHash = [System.BitConverter]::ToString($hashBytes).Replace('-', '').ToLower()

Write-Host "Original password: $plainPassword" -ForegroundColor Yellow
Write-Host "SHA256 hash: $passwordHash" -ForegroundColor Green
```

**创建users.xml:**
```powershell
# Create users.xml (using the hash generated above)
@"
<?xml version="1.0"?>
<yandex>
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <max_execution_time>300</max_execution_time>
            <readonly>0</readonly>
        </default>
        
        <readonly>
            <readonly>1</readonly>
            <max_memory_usage>5000000000</max_memory_usage>
            <max_execution_time>60</max_execution_time>
        </readonly>
    </profiles>

    <users>
        <!-- Default user (for development environment) -->
        <default>
            <password></password>
            <networks>
                <ip>::/0</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>
        
        <!-- Admin user -->
        <admin>
            <!-- Use SHA256 encrypted password -->
            <password_sha256_hex>$passwordHash</password_sha256_hex>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
                <ip>172.17.0.0/16</ip>
                <ip>192.168.0.0/16</ip>
                <ip>10.0.0.0/8</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </admin>
        
        <!-- Read-only user -->
        <readonly_user>
            <password>ReadOnly@2024</password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>readonly</profile>
            <quota>default</quota>
        </readonly_user>
    </users>

    <quotas>
        <default>
            <interval>
                <duration>3600</duration>
                <queries>0</queries>
                <errors>0</errors>
                <result_rows>0</result_rows>
                <read_rows>0</read_rows>
                <execution_time>0</execution_time>
            </interval>
        </default>
    </quotas>
</yandex>
"@ | Out-File -FilePath "config\users.xml" -Encoding UTF8
```

**用户配置详解:**
- `default`: 默认用户，无密码，适合开发环境
- `admin`: 管理员用户，使用SHA256加密密码，具有完全权限
- `readonly_user`: 只读用户，只能执行查询操作
- `networks`: 限制用户可以从哪些IP地址连接
- `profile`: 指定用户使用的配置文件
- `quota`: 指定用户的资源配额
            <readonly>0</readonly>
        </default>
        
        <readonly>
            <readonly>1</readonly>
            <max_memory_usage>5000000000</max_memory_usage>
            <max_execution_time>60</max_execution_time>
        </readonly>
    </profiles>

    <users>
        <!-- 默认用户 (生产环境应该禁用) -->
        <default>
            <password></password>
            <networks incl="networks_config">
                <ip>::/0</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>
        
        <!-- 管理员用户 -->
        <admin>
            <!-- 使用明文密码 (仅用于学习，生产环境请使用SHA256) -->
            <password>ClickHouse@2024</password>
            <!-- 生产环境推荐使用SHA256加密: -->
            <!-- <password_sha256_hex>SHA256加密后的密码</password_sha256_hex> -->
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
                <ip>172.17.0.0/16</ip>
                <ip>192.168.0.0/16</ip>
                <ip>10.0.0.0/8</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </admin>
        
        <!-- 只读用户 -->
        <readonly_user>
            <password>ReadOnly@2024</password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>readonly</profile>
            <quota>default</quota>
        </readonly_user>
    </users>

    <quotas>
        <default>
            <interval>
                <duration>3600</duration>
                <queries>0</queries>
                <errors>0</errors>
                <result_rows>0</result_rows>
                <read_rows>0</read_rows>
                <execution_time>0</execution_time>
            </interval>
        </default>
    </quotas>
</yandex>
"@ | Out-File -FilePath "config\users.xml" -Encoding UTF8
```

### 2.5 生成密码加密 (生产环境必须)

**密码加密工具脚本:**
```powershell
# 创建密码加密脚本
@"
# ClickHouse Password Encryption Tool
param([string]`$Password)

if (-not `$Password) {
    `$Password = Read-Host "Please enter the password to encrypt" -AsSecureString
    `$Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR(`$Password))
}

# Calculate SHA256 hash
`$sha256 = [System.Security.Cryptography.SHA256]::Create()
`$hashBytes = `$sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes(`$Password))
`$hashString = [System.BitConverter]::ToString(`$hashBytes).Replace('-', '').ToLower()

Write-Host "Original password: `$Password" -ForegroundColor Yellow
Write-Host "SHA256 hash: `$hashString" -ForegroundColor Green
Write-Host ""
Write-Host "Use in users.xml:" -ForegroundColor Cyan
Write-Host "<password_sha256_hex>`$hashString</password_sha256_hex>" -ForegroundColor White

# Save to file
`$hashString | Out-File -FilePath "password_hash.txt" -Encoding UTF8
Write-Host "Hash value saved to password_hash.txt"
"@ | Out-File -FilePath "generate-password.ps1" -Encoding UTF8

# Run password encryption
powershell -File "generate-password.ps1" -Password "ClickHouse@2024"
```

### 2.6 启动ClickHouse容器

```powershell
# Create and start ClickHouse container
docker run -d `
  --name clickhouse-server `
  --hostname clickhouse-server `
  -p 8123:8123 `
  -p 9000:9000 `
  -p 9004:9004 `
  -v "${PWD}\data:/var/lib/clickhouse" `
  -v "${PWD}\logs:/var/log/clickhouse-server" `
  -v "${PWD}\config\config.xml:/etc/clickhouse-server/config.d/custom-config.xml" `
  -v "${PWD}\config\users.xml:/etc/clickhouse-server/users.d/custom-users.xml" `
  --ulimit nofile=262144:262144 `
  clickhouse/clickhouse-server:latest

Write-Host "ClickHouse container starting..." -ForegroundColor Green
```

## 第三步：启动容器和验证安装 ✅

### 3.1 启动ClickHouse容器

```powershell
# Start container
docker run -d `
    --name clickhouse-server `
    --hostname clickhouse-server `
    -p 8123:8123 `
    -p 9000:9000 `
    -p 9004:9004 `
    -v "${PWD}\data:/var/lib/clickhouse" `
    -v "${PWD}\logs:/var/log/clickhouse-server" `
    -v "${PWD}\config\config.xml:/etc/clickhouse-server/config.d/custom-config.xml" `
    -v "${PWD}\config\users.xml:/etc/clickhouse-server/users.d/custom-users.xml" `
    --ulimit nofile=262144:262144 `
    clickhouse/clickhouse-server:latest

# Wait for service startup
Write-Host "Waiting for ClickHouse service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
```

### 3.2 基础验证测试

#### 3.2.1 检查容器状态

```powershell
# Check container running status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "clickhouse"

# View container logs
docker logs clickhouse-server --tail 20

# Check container resource usage
docker stats clickhouse-server --no-stream
```

#### 3.2.2 网络连接测试

```powershell
# Test HTTP interface
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8123" -Method GET -TimeoutSec 10
    Write-Host "✅ HTTP interface status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ HTTP interface test failed: $_" -ForegroundColor Red
}

# Test version query
try {
    $query = "SELECT version()"
    $result = Invoke-WebRequest -Uri "http://localhost:8123" -Method POST -Body $query -TimeoutSec 10
    Write-Host "✅ ClickHouse version: $($result.Content.Trim())" -ForegroundColor Green
} catch {
    Write-Host "❌ Version query failed: $_" -ForegroundColor Red
}

# Test port connectivity
$ports = @(8123, 9000, 9004)
foreach ($port in $ports) {
    $tcpTest = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    if ($tcpTest.TcpTestSucceeded) {
        Write-Host "✅ Port $port accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Port $port not accessible" -ForegroundColor Red
    }
}
```

#### 3.2.3 用户连接测试

```powershell
# Test default user connection
Write-Host "`nTesting default user connection:" -ForegroundColor Yellow
try {
    $result = docker exec clickhouse-server clickhouse-client --query "SELECT 'Default user test passed'"
    Write-Host "✅ Default user connection normal: $result" -ForegroundColor Green
} catch {
    Write-Host "❌ Default user connection failed" -ForegroundColor Red
}

# Test admin user connection
Write-Host "`nTesting admin user connection:" -ForegroundColor Yellow
try {
    $result = docker exec clickhouse-server clickhouse-client --user admin --password ClickHouse@2024 --query "SELECT 'Admin user test passed'"
    Write-Host "✅ Admin user connection normal: $result" -ForegroundColor Green
} catch {
    Write-Host "❌ Admin user connection failed" -ForegroundColor Red
}

# Test readonly user connection
Write-Host "`nTesting readonly user connection:" -ForegroundColor Yellow
try {
    $result = docker exec clickhouse-server clickhouse-client --user readonly_user --password ReadOnly@2024 --query "SELECT 'Readonly user test passed'"
    Write-Host "✅ Readonly user connection normal: $result" -ForegroundColor Green
    
    # Test readonly restrictions
    Write-Host "Testing readonly user permission restrictions:" -ForegroundColor Gray
    $createResult = docker exec clickhouse-server clickhouse-client --user readonly_user --password ReadOnly@2024 --query "CREATE DATABASE test_readonly" 2>&1
    if ($createResult -match "readonly" -or $createResult -match "permission") {
        Write-Host "✅ Readonly user permission restrictions normal" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Readonly user permission restrictions may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Readonly user connection failed" -ForegroundColor Red
}
```

#### 3.2.4 配置文件验证

```powershell
# Check system users
Write-Host "`nChecking system users:" -ForegroundColor Yellow
docker exec clickhouse-server clickhouse-client --query "SELECT name FROM system.users"

# Check memory configuration
Write-Host "`nChecking memory configuration:" -ForegroundColor Yellow
docker exec clickhouse-server clickhouse-client --query "SELECT name, value FROM system.settings WHERE name LIKE '%memory%' LIMIT 5"

# Check network configuration
Write-Host "`nChecking network configuration:" -ForegroundColor Yellow
docker exec clickhouse-server clickhouse-client --query "SELECT interface, port FROM system.servers"

# Check database list
Write-Host "`nChecking database list:" -ForegroundColor Yellow
docker exec clickhouse-server clickhouse-client --user admin --password ClickHouse@2024 --query "SHOW DATABASES"
```

## 第四步：配置文件深度实操 🔧

### 4.1 运行配置验证脚本

**使用专用配置验证工具:**
```powershell
# Run configuration validation script
powershell -ExecutionPolicy Bypass -File "config-validator.ps1"
```

这个脚本会执行以下验证：
- ✅ 环境检查和配置文件语法验证
- ✅ 用户配置和权限测试
- ✅ 密码加密演示和强密码生成
- ✅ 网络配置和端口连通性测试
- ✅ 性能配置和资源使用检查
- ✅ 日志配置和日志文件检查
- ✅ 实时配置修改演示

### 4.2 密码安全实操

#### 4.2.1 生成强密码

```powershell
# Generate strong password function
function Generate-StrongPassword {
    param([int]$Length = 16)
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

# Generate 3 strong password examples
1..3 | ForEach-Object {
    $strongPassword = Generate-StrongPassword
    Write-Host "Strong password $_`: $strongPassword" -ForegroundColor Yellow
    
    # Calculate SHA256 hash
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($strongPassword))
    $hashString = [System.BitConverter]::ToString($hashBytes).Replace('-', '').ToLower()
    Write-Host "  SHA256: $hashString" -ForegroundColor Green
    Write-Host ""
}
```

#### 4.2.2 密码加密配置实践

```powershell
# 创建新用户配置示例
$newUserPassword = "MySecurePassword@2024"
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($newUserPassword))
$passwordHash = [System.BitConverter]::ToString($hashBytes).Replace('-', '').ToLower()

Write-Host "New user configuration example:" -ForegroundColor Cyan
Write-Host @"
<new_user>
    <password_sha256_hex>$passwordHash</password_sha256_hex>
    <networks>
        <ip>127.0.0.1</ip>
        <ip>192.168.1.0/24</ip>
    </networks>
    <profile>default</profile>
    <quota>default</quota>
</new_user>
"@ -ForegroundColor White
```

### 4.3 网络安全配置实操

#### 4.3.1 IP访问限制配置

```powershell
Write-Host "Network access restriction configuration example:" -ForegroundColor Cyan

# Local access only
Write-Host "`n1. Local access only:" -ForegroundColor Yellow
Write-Host @"
<networks>
    <ip>::1</ip>
    <ip>127.0.0.1</ip>
</networks>
"@ -ForegroundColor White

# LAN access
Write-Host "`n2. LAN access:" -ForegroundColor Yellow
Write-Host @"
<networks>
    <ip>192.168.0.0/16</ip>
    <ip>10.0.0.0/8</ip>
    <ip>172.16.0.0/12</ip>
</networks>
"@ -ForegroundColor White

# Specific IP access
Write-Host "`n3. Specific IP access:" -ForegroundColor Yellow
Write-Host @"
<networks>
    <ip>192.168.1.100</ip>
    <ip>192.168.1.101</ip>
</networks>
"@ -ForegroundColor White
```

#### 4.3.2 端口配置优化

```powershell
Write-Host "`nPort configuration description:" -ForegroundColor Cyan
Write-Host "HTTP port (8123): REST API and web interface access" -ForegroundColor Gray
Write-Host "TCP port (9000): Native client connection" -ForegroundColor Gray
Write-Host "MySQL port (9004): MySQL protocol compatibility" -ForegroundColor Gray
Write-Host "PostgreSQL port (9005): PostgreSQL protocol compatibility" -ForegroundColor Gray

# Test current port configuration
Write-Host "`nCurrent port status:" -ForegroundColor Yellow
$ports = @(8123, 9000, 9004)
foreach ($port in $ports) {
    try {
        $test = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if ($test.TcpTestSucceeded) {
            Write-Host "✅ Port $port accessible" -ForegroundColor Green
        } else {
            Write-Host "❌ Port $port not accessible" -ForegroundColor Red
        }
    } catch {
        Write-Host "⚠️  Port $port test failed" -ForegroundColor Yellow
    }
}
```

### 4.4 性能配置优化实操

#### 4.4.1 内存配置调优

```powershell
Write-Host "`nMemory configuration optimization:" -ForegroundColor Cyan

# Get system memory information
$totalMemory = Get-CimInstance -ClassName Win32_ComputerSystem
$memoryGB = [math]::Round($totalMemory.TotalPhysicalMemory / 1GB, 2)
Write-Host "Total system memory: ${memoryGB}GB" -ForegroundColor Gray

# Recommended memory configuration
$recommendedMemory = [math]::Floor($memoryGB * 0.6) * 1000000000  # 60% of system memory
Write-Host "Recommended ClickHouse memory limit: $([math]::Round($recommendedMemory / 1000000000, 1))GB" -ForegroundColor Yellow

Write-Host "`nMemory configuration example:" -ForegroundColor Yellow
Write-Host @"
<!-- 限制服务器内存使用为系统内存的60% -->
<max_server_memory_usage_to_ram_ratio>0.6</max_server_memory_usage_to_ram_ratio>

<!-- 或者设置固定内存限制 -->
<max_server_memory_usage>$recommendedMemory</max_server_memory_usage>

<!-- 单个查询内存限制 -->
<max_memory_usage>5000000000</max_memory_usage>  <!-- 5GB -->
"@ -ForegroundColor White
```

#### 4.4.2 并发配置调优

```powershell
Write-Host "`nConcurrency configuration optimization:" -ForegroundColor Cyan

# Get CPU core count
$cpuCores = (Get-CimInstance -ClassName Win32_Processor).NumberOfCores
Write-Host "CPU cores: $cpuCores" -ForegroundColor Gray

# Recommended concurrency configuration
$recommendedQueries = $cpuCores * 4
$recommendedConnections = $cpuCores * 128

Write-Host "`nRecommended concurrency configuration:" -ForegroundColor Yellow
Write-Host @"
<!-- 最大并发查询数 -->
<max_concurrent_queries>$recommendedQueries</max_concurrent_queries>

<!-- 最大连接数 -->
<max_connections>$recommendedConnections</max_connections>

<!-- 后台处理线程数 -->
<background_pool_size>$cpuCores</background_pool_size>
<background_schedule_pool_size>$([math]::Max($cpuCores / 2, 2))</background_schedule_pool_size>
"@ -ForegroundColor White
```

### 4.5 配置修改和重启实操

#### 4.5.1 安全备份配置

```powershell
# Backup current configuration
Write-Host "Backing up current configuration files..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$backupDir = "config\backup-$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Copy-Item "config\config.xml" "$backupDir\config.xml" -Force
Copy-Item "config\users.xml" "$backupDir\users.xml" -Force
Write-Host "✅ Configuration files backed up to: $backupDir" -ForegroundColor Green
```

#### 4.5.2 配置修改示例

```powershell
Write-Host "`nConfiguration modification example - Adjust log level:" -ForegroundColor Cyan

# Read current configuration
$configPath = "config\config.xml"
$configContent = Get-Content $configPath -Raw -Encoding UTF8

# Display current log level
if ($configContent -match '<level>([^<]+)</level>') {
    $currentLevel = $matches[1]
    Write-Host "Current log level: $currentLevel" -ForegroundColor Yellow
}

Write-Host "`nAvailable log levels:" -ForegroundColor Gray
@("trace", "debug", "information", "warning", "error") | ForEach-Object {
    Write-Host "  - $_ $(if($_ -eq $currentLevel){'(current)'})" -ForegroundColor White
}

Write-Host "`nCommand to change log level to debug:" -ForegroundColor Cyan
Write-Host @'
$configContent = $configContent -replace '<level>information</level>', '<level>debug</level>'
$configContent | Out-File -FilePath "config\config.xml" -Encoding UTF8
'@ -ForegroundColor White
```

#### 4.5.3 容器重启和验证

```powershell
Write-Host "`nContainer restart steps:" -ForegroundColor Cyan
Write-Host @"
# 1. 停止容器
docker stop clickhouse-server

# 2. 重新启动容器 (配置会自动重新加载)
docker start clickhouse-server

# 3. 等待服务启动
Start-Sleep -Seconds 10

# 4. 验证服务状态
docker exec clickhouse-server clickhouse-client --query "SELECT 1"

# 5. 检查新配置是否生效
docker exec clickhouse-server clickhouse-client --query "SELECT value FROM system.server_settings WHERE name = 'logger.level'"
"@ -ForegroundColor White
```

## 第五步：故障排查和运维管理 🔧

### 5.1 常见问题诊断和解决

#### 5.1.0 Docker网络连接问题

**问题症状:**
```
docker: Error response from daemon: Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers).
```

**解决方案:**

**方法1: 配置Docker镜像源**
```powershell
# 1. 打开Docker Desktop设置
# 2. 进入 Settings -> Docker Engine
# 3. 添加以下配置:
{
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}

# 4. 点击 Apply & Restart
```

**方法2: 使用代理或VPN**
```powershell
# 如果有代理，在Docker Desktop中配置:
# Settings -> Resources -> Proxies
# 配置HTTP/HTTPS代理地址
```

**方法3: 手动下载镜像**
```powershell
# 使用国内镜像源
docker pull registry.cn-hangzhou.aliyuncs.com/clickhouse/clickhouse-server:latest
docker tag registry.cn-hangzhou.aliyuncs.com/clickhouse/clickhouse-server:latest clickhouse/clickhouse-server:latest

# 或者使用其他镜像源
docker pull uhub.service.ucloud.cn/clickhouse/clickhouse-server:latest
docker tag uhub.service.ucloud.cn/clickhouse/clickhouse-server:latest clickhouse/clickhouse-server:latest
```

**方法4: 网络诊断和修复**
```powershell
# 重置Docker网络
docker network prune -f

# 重启Docker Desktop
# 在系统托盘右键Docker图标 -> Restart Docker Desktop

# 检查DNS设置
nslookup registry-1.docker.io
nslookup docker.mirrors.ustc.edu.cn

# 刷新DNS缓存
ipconfig /flushdns
```

#### 5.1.1 容器启动失败

**问题诊断:**
```powershell
Write-Host "=== 容器启动问题诊断 ===" -ForegroundColor Cyan

# 1. 检查容器状态
Write-Host "`n1. 检查容器状态:" -ForegroundColor Yellow
docker ps -a --filter "name=clickhouse-server"

# 2. 查看详细错误日志
Write-Host "`n2. 查看容器启动日志:" -ForegroundColor Yellow
docker logs clickhouse-server --tail 50

# 3. 检查端口占用
Write-Host "`n3. 检查端口占用情况:" -ForegroundColor Yellow
$ports = @(8123, 9000, 9004)
foreach ($port in $ports) {
    $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($processes) {
        Write-Host "❌ 端口 $port 被占用:" -ForegroundColor Red
        $processes | ForEach-Object {
            $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  进程: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor White
            }
        }
    } else {
        Write-Host "✅ 端口 $port 可用" -ForegroundColor Green
    }
}

# 4. 检查Docker服务
Write-Host "`n4. 检查Docker服务状态:" -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker服务异常: $_" -ForegroundColor Red
}
```

**解决方案:**
```powershell
Write-Host "`n=== 解决方案 ===" -ForegroundColor Cyan

# 清理并重新创建容器
Write-Host "1. 清理并重新创建容器:" -ForegroundColor Yellow
Write-Host @"
# 停止并删除容器
docker stop clickhouse-server 2>$null
docker rm clickhouse-server 2>$null

# 清理Docker缓存
docker system prune -f

# 重新运行安装脚本
powershell -ExecutionPolicy Bypass -File "docker-install-windows.ps1"
"@ -ForegroundColor White

# 端口冲突解决
Write-Host "`n2. 端口冲突解决:" -ForegroundColor Yellow
Write-Host @"
# 查找占用端口的进程
Get-NetTCPConnection -LocalPort 8123 | ForEach-Object {
    Get-Process -Id $_.OwningProcess
}

# 终止占用进程 (谨慎操作)
Stop-Process -Id <进程ID> -Force

# 或者修改ClickHouse端口配置
# 在config.xml中修改端口号
"@ -ForegroundColor White
```

#### 5.1.2 连接被拒绝问题

**问题诊断:**
```powershell
Write-Host "`n=== 连接问题诊断 ===" -ForegroundColor Cyan

# 1. 测试网络连接
Write-Host "`n1. 测试网络连接:" -ForegroundColor Yellow
$endpoints = @(
    @{Host="localhost"; Port=8123; Protocol="HTTP"},
    @{Host="localhost"; Port=9000; Protocol="TCP"},
    @{Host="127.0.0.1"; Port=8123; Protocol="HTTP"}
)

foreach ($endpoint in $endpoints) {
    try {
        $test = Test-NetConnection -ComputerName $endpoint.Host -Port $endpoint.Port -WarningAction SilentlyContinue
        $status = if ($test.TcpTestSucceeded) { "✅ 成功" } else { "❌ 失败" }
        Write-Host "  $($endpoint.Protocol) $($endpoint.Host):$($endpoint.Port) - $status" -ForegroundColor $(if ($test.TcpTestSucceeded) { "Green" } else { "Red" })
    } catch {
        Write-Host "  $($endpoint.Protocol) $($endpoint.Host):$($endpoint.Port) - ❌ 异常: $_" -ForegroundColor Red
    }
}

# 2. 检查防火墙设置
Write-Host "`n2. 检查Windows防火墙:" -ForegroundColor Yellow
try {
    $firewallProfiles = Get-NetFirewallProfile
    foreach ($profile in $firewallProfiles) {
        $status = if ($profile.Enabled) { "启用" } else { "禁用" }
        Write-Host "  $($profile.Name): $status" -ForegroundColor $(if ($profile.Enabled) { "Yellow" } else { "Green" })
    }
} catch {
    Write-Host "  无法检查防火墙状态" -ForegroundColor Red
}
```

### 5.2 日常运维管理

#### 5.2.1 生成运维脚本

```powershell
Write-Host "=== 生成运维管理脚本 ===" -ForegroundColor Cyan

# 创建综合管理脚本
$managementScript = @"
# ClickHouse 综合管理脚本
param(
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs', 'backup', 'monitor', 'cleanup')]
    [string]`$Action = 'status'
)

`$ContainerName = "clickhouse-server"
`$WorkDir = "$PWD"

switch (`$Action) {
    'start' {
        Write-Host "启动ClickHouse容器..." -ForegroundColor Yellow
        docker start `$ContainerName
        Start-Sleep -Seconds 5
        docker exec `$ContainerName clickhouse-client --query "SELECT 'ClickHouse已启动'"
    }
    
    'stop' {
        Write-Host "停止ClickHouse容器..." -ForegroundColor Yellow
        docker stop `$ContainerName
    }
    
    'restart' {
        Write-Host "重启ClickHouse容器..." -ForegroundColor Yellow
        docker restart `$ContainerName
        Start-Sleep -Seconds 10
        docker exec `$ContainerName clickhouse-client --query "SELECT 'ClickHouse已重启'"
    }
    
    'status' {
        Write-Host "=== ClickHouse状态检查 ===" -ForegroundColor Cyan
        docker ps --filter "name=`$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        docker exec `$ContainerName clickhouse-client --query "SELECT version(), uptime()"
    }
    
    'logs' {
        Write-Host "=== ClickHouse日志 ===" -ForegroundColor Cyan
        docker logs `$ContainerName --tail 50
    }
    
    'backup' {
        `$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
        `$backupDir = "backup-`$timestamp"
        Write-Host "创建备份: `$backupDir" -ForegroundColor Yellow
        
        New-Item -ItemType Directory -Path `$backupDir -Force | Out-Null
        docker cp `$ContainerName`:/var/lib/clickhouse `$backupDir\data
        Copy-Item -Path "config" -Destination "`$backupDir\config" -Recurse -Force
        
        Write-Host "✅ 备份完成: `$backupDir" -ForegroundColor Green
    }
    
    'monitor' {
        Write-Host "=== ClickHouse监控信息 ===" -ForegroundColor Cyan
        docker stats `$ContainerName --no-stream
    }
    
    'cleanup' {
        Write-Host "清理Docker资源..." -ForegroundColor Yellow
        docker system prune -f
        Write-Host "✅ 清理完成" -ForegroundColor Green
    }
}
"@

$managementScript | Out-File -FilePath "scripts\clickhouse-manager.ps1" -Encoding UTF8
Write-Host "✅ 综合管理脚本已生成: scripts\clickhouse-manager.ps1" -ForegroundColor Green

Write-Host "`n使用方法:" -ForegroundColor Yellow
Write-Host @"
  .\scripts\clickhouse-manager.ps1 -Action start     # 启动服务
  .\scripts\clickhouse-manager.ps1 -Action stop      # 停止服务
  .\scripts\clickhouse-manager.ps1 -Action restart   # 重启服务
  .\scripts\clickhouse-manager.ps1 -Action status    # 查看状态
  .\scripts\clickhouse-manager.ps1 -Action logs      # 查看日志
  .\scripts\clickhouse-manager.ps1 -Action backup    # 创建备份
  .\scripts\clickhouse-manager.ps1 -Action monitor   # 监控信息
  .\scripts\clickhouse-manager.ps1 -Action cleanup   # 清理资源
"@ -ForegroundColor White
```

## 学习总结 🎯

### 完成的学习内容

通过Day 1的学习，您已经掌握：

1. **环境搭建**: ✅ Windows Docker环境下的ClickHouse安装
2. **配置管理**: ✅ 配置文件的创建、修改和验证
3. **安全配置**: ✅ 用户管理、密码加密、网络限制
4. **运维技能**: ✅ 容器管理、监控、备份、故障排查
5. **实操能力**: ✅ 通过脚本自动化完成各种配置任务

### 生成的工具和脚本

- 📦 `docker-install-windows.ps1` - 一键安装脚本
- 🔧 `config-validator.ps1` - 配置验证工具
- 🛠️ `clickhouse-manager.ps1` - 综合管理脚本
- 📊 `performance-monitor.ps1` - 性能监控脚本
- 🔐 `generate-password.ps1` - 密码加密工具

### 重要文件结构

```
C:\ClickHouse\
├── config\
│   ├── config.xml          # 主配置文件
│   ├── users.xml           # 用户配置文件
│   ├── passwords.txt       # 密码信息
│   └── backup-*\           # 配置备份
├── data\                   # 数据目录
├── logs\                   # 日志目录
├── scripts\                # 管理脚本
│   ├── clickhouse-manager.ps1
│   ├── config-validator.ps1
│   └── performance-monitor.ps1
└── backups\               # 数据备份
```

### 下一步学习建议

✅ **Day 1 完成** - 环境搭建与配置实操

🔜 **Day 2 准备** - ClickHouse基础概念和架构
- 数据类型和存储引擎
- 基本SQL语法和查询
- 表结构设计基础

🎉 **恭喜您完成了ClickHouse学习的第一步！**

现在您已经拥有了一个完全配置好的ClickHouse环境，可以开始深入学习ClickHouse的核心功能了。 