# ClickHouse Docker Installation Script - Windows Edition
# Optimized for Chinese users with mirror configurations and detailed validation steps

param(
    [string]$WorkDir = "C:\ClickHouse",
    [string]$Password = "ClickHouse@2024",
    [string]$ContainerName = "clickhouse-server",
    [switch]$UseChineseMirror = $true
)

# Set error handling
$ErrorActionPreference = "Stop"

# Color output functions
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorText "`n=== $Message ===" -Color "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorText "[SUCCESS] $Message" -Color "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorText "[WARNING] $Message" -Color "Yellow"
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-ColorText "[ERROR] $Message" -Color "Red"
}

# Main function
function Install-ClickHouse {
    Write-ColorText @"
===============================================================
              ClickHouse Docker Installation Tool           
                   Windows Chinese Users Edition            
===============================================================
"@ -Color "Magenta"

    # Step 1: Environment check
    Write-Step "Step 1: Environment Check"
    Test-Environment

    # Step 2: Create working directory
    Write-Step "Step 2: Create Working Directory"
    Create-WorkDirectory

    # Step 3: Download ClickHouse image
    Write-Step "Step 3: Download ClickHouse Image"
    Download-ClickHouseImage

    # Step 4: Generate configuration files
    Write-Step "Step 4: Generate Configuration Files"
    Generate-ConfigFiles

    # Step 5: Start ClickHouse container
    Write-Step "Step 5: Start ClickHouse Container"
    Start-ClickHouseContainer

    # Step 6: Verify installation
    Write-Step "Step 6: Verify Installation"
    Test-Installation

    # Step 7: Generate management scripts
    Write-Step "Step 7: Generate Management Scripts"
    Generate-ManagementScripts

    Write-Success "ClickHouse installation completed!"
    Show-Summary
}

# Environment check
function Test-Environment {
    Write-ColorText "Checking system environment..." -Color "Yellow"
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    Write-ColorText "PowerShell version: $psVersion" -Color "Gray"
    
    # Check if Docker is installed
    try {
        $dockerVersion = docker --version
        Write-Success "Docker installed: $dockerVersion"
    } catch {
        Write-ErrorMsg "Docker not installed or not started. Please install Docker Desktop first"
        Write-ColorText "Download URL: https://www.docker.com/products/docker-desktop/" -Color "Blue"
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Success "Docker service running normally"
    } catch {
        Write-ErrorMsg "Docker service not running. Please start Docker Desktop"
        exit 1
    }
    
    # Check port usage
    $ports = @(8123, 9000, 9004)
    foreach ($port in $ports) {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Warning "Port $port is already in use, may affect ClickHouse startup"
        } else {
            Write-ColorText "Port $port is available" -Color "Gray"
        }
    }
}

# Create working directory
function Create-WorkDirectory {
    Write-ColorText "Creating working directory: $WorkDir" -Color "Yellow"
    
    # Create main directory
    if (-not (Test-Path $WorkDir)) {
        New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
        Write-Success "Created directory: $WorkDir"
    } else {
        Write-ColorText "Directory already exists: $WorkDir" -Color "Gray"
    }
    
    # Create subdirectories
    $subDirs = @("data", "logs", "config", "backups", "scripts")
    foreach ($dir in $subDirs) {
        $fullPath = Join-Path $WorkDir $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Success "Created subdirectory: $dir"
        }
    }
    
    # Set current directory
    Set-Location $WorkDir
    Write-ColorText "Working directory set to: $WorkDir" -Color "Gray"
}

# Download ClickHouse image
function Download-ClickHouseImage {
    Write-ColorText "Downloading ClickHouse image..." -Color "Yellow"
    
    $imageName = "clickhouse/clickhouse-server:latest"
    
    if ($UseChineseMirror) {
        # Try downloading from Chinese mirror
        $chineseImage = "registry.cn-hangzhou.aliyuncs.com/clickhouse/clickhouse-server:latest"
        Write-ColorText "Trying to download from Alibaba Cloud mirror..." -Color "Gray"
        
        try {
            docker pull $chineseImage
            docker tag $chineseImage $imageName
            Write-Success "Downloaded successfully from Chinese mirror"
        } catch {
            Write-Warning "Chinese mirror download failed, trying official mirror..."
            try {
                docker pull $imageName
                Write-Success "Downloaded successfully from official mirror"
            } catch {
                Write-ErrorMsg "Failed to download ClickHouse image. Please check network connection."
                Write-ColorText "You can try configuring Docker registry mirrors manually:" -Color "Yellow"
                Write-ColorText "Docker Desktop -> Settings -> Docker Engine -> Add registry-mirrors" -Color "Gray"
                exit 1
            }
        }
    } else {
        try {
            docker pull $imageName
            Write-Success "Image download completed"
        } catch {
            Write-ErrorMsg "Failed to download ClickHouse image. Please check network connection."
            exit 1
        }
    }
    
    # Verify image
    $images = docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | Select-String "clickhouse"
    Write-ColorText "Downloaded ClickHouse images:" -Color "Gray"
    $images | ForEach-Object { Write-ColorText "  $_" -Color "White" }
}

# Generate configuration files
function Generate-ConfigFiles {
    Write-ColorText "Generating ClickHouse configuration files..." -Color "Yellow"
    
    # Generate config.xml
    Generate-ConfigXml
    
    # Generate users.xml
    Generate-UsersXml
    
    Write-Success "Configuration files generated successfully"
}

# Generate main configuration file
function Generate-ConfigXml {
    $configContent = @"
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
"@
    
    $configPath = Join-Path $WorkDir "config/config.xml"
    $configContent | Out-File -FilePath $configPath -Encoding UTF8
    Write-Success "Generated configuration file: config/config.xml"
}

# Generate user configuration file
function Generate-UsersXml {
    # Generate password hash
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Password))
    $passwordHash = [System.BitConverter]::ToString($hashBytes).Replace('-', '').ToLower()
    
    $usersContent = @"
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
        <!-- Default user -->
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
        
        <!-- Readonly user -->
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
"@
    
    $usersPath = Join-Path $WorkDir "config/users.xml"
    $usersContent | Out-File -FilePath $usersPath -Encoding UTF8
    Write-Success "Generated user configuration file: config/users.xml"
    
    # Save password information
    $passwordInfo = @"
ClickHouse User Password Information
====================================
Admin User: admin
Original Password: $Password
SHA256 Hash: $passwordHash

Readonly User: readonly_user  
Password: ReadOnly@2024

Default User: default
Password: (empty)
"@
    
    $passwordPath = Join-Path $WorkDir "config/passwords.txt"
    $passwordInfo | Out-File -FilePath $passwordPath -Encoding UTF8
    Write-Success "Password information saved to: config/passwords.txt"
}

# Start ClickHouse container
function Start-ClickHouseContainer {
    Write-ColorText "Starting ClickHouse container..." -Color "Yellow"
    
    # Check if container with same name already exists
    $existingContainer = docker ps -a --format "{{.Names}}" | Select-String "^$ContainerName$"
    if ($existingContainer) {
        Write-Warning "Found existing container: $ContainerName"
        $choice = Read-Host "Do you want to remove and recreate it? (y/N)"
        if ($choice -eq 'y' -or $choice -eq 'Y') {
            docker stop $ContainerName 2>$null
            docker rm $ContainerName 2>$null
            Write-Success "Removed old container"
        } else {
            Write-ErrorMsg "Container name conflict, please choose a different name"
            return
        }
    }
    
    # Start container
    $configPath = Join-Path $WorkDir "config/config.xml"
    $usersPath = Join-Path $WorkDir "config/users.xml"
    $dataPath = Join-Path $WorkDir "data"
    $logsPath = Join-Path $WorkDir "logs"
    
    docker run -d `
        --name $ContainerName `
        --hostname $ContainerName `
        -p 8123:8123 `
        -p 9000:9000 `
        -p 9004:9004 `
        -v "${dataPath}:/var/lib/clickhouse" `
        -v "${logsPath}:/var/log/clickhouse-server" `
        -v "${configPath}:/etc/clickhouse-server/config.d/custom-config.xml" `
        -v "${usersPath}:/etc/clickhouse-server/users.d/custom-users.xml" `
        --ulimit nofile=262144:262144 `
        clickhouse/clickhouse-server:latest
    
    Write-Success "Container start command executed successfully"
    
    # Wait for container to start
    Write-ColorText "Waiting for ClickHouse service to start..." -Color "Yellow"
    $maxWait = 60
    $waited = 0
    
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 2
        $waited += 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8123" -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "ClickHouse service started successfully (wait time: ${waited}s)"
                break
            }
        } catch {
            # Continue waiting
        }
        
        if ($waited % 10 -eq 0) {
            Write-ColorText "Waiting... (${waited}/${maxWait}s)" -Color "Gray"
        }
    }
    
    if ($waited -ge $maxWait) {
        Write-ErrorMsg "ClickHouse service startup timeout"
        Write-ColorText "Check container logs:" -Color "Yellow"
        docker logs $ContainerName --tail 20
    }
}

# Verify installation
function Test-Installation {
    Write-ColorText "Verifying ClickHouse installation..." -Color "Yellow"
    
    # 1. Check container status
    Write-ColorText "1. Check container status" -Color "Gray"
    $containerStatus = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String $ContainerName
    if ($containerStatus) {
        Write-Success "Container running status normal"
    } else {
        Write-ErrorMsg "Container not running"
        return
    }
    
    # 2. Test HTTP interface
    Write-ColorText "2. Test HTTP interface" -Color "Gray"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8123" -Method GET -TimeoutSec 10
        Write-Success "HTTP interface response normal: $($response.StatusCode)"
    } catch {
        Write-ErrorMsg "HTTP interface test failed"
    }
    
    # 3. Test version query
    Write-ColorText "3. Test version query" -Color "Gray"
    try {
        $version = Invoke-RestMethod -Uri "http://localhost:8123" -Method POST -Body "SELECT version()" -TimeoutSec 10
        Write-Success "Version query successful: $version"
    } catch {
        Write-ErrorMsg "Version query failed"
    }
    
    # 4. Test admin user connection
    Write-ColorText "4. Test admin user connection" -Color "Gray"
    try {
        $result = docker exec $ContainerName clickhouse-client --user admin --password $Password --query "SELECT 'Admin connection test passed'" 2>$null
        if ($result -match "Admin connection test passed") {
            Write-Success "Admin user connection normal"
        } else {
            Write-Warning "Admin user connection abnormal"
        }
    } catch {
        Write-Warning "Unable to test admin user connection"
    }
}

# Generate management scripts
function Generate-ManagementScripts {
    Write-ColorText "Generating management scripts..." -Color "Yellow"
    
    $managerScript = @"
# ClickHouse Container Manager
# Usage: ./clickhouse-manager.ps1 [start|stop|restart|status|logs|backup]

param([string]`$Action = "status")

switch (`$Action.ToLower()) {
    "start" {
        Write-Host "Starting ClickHouse container..." -ForegroundColor Yellow
        docker start $ContainerName
        Write-Host "Container started" -ForegroundColor Green
    }
    "stop" {
        Write-Host "Stopping ClickHouse container..." -ForegroundColor Yellow
        docker stop $ContainerName
        Write-Host "Container stopped" -ForegroundColor Green
    }
    "restart" {
        Write-Host "Restarting ClickHouse container..." -ForegroundColor Yellow
        docker restart $ContainerName
        Write-Host "Container restarted" -ForegroundColor Green
    }
    "status" {
        Write-Host "ClickHouse container status:" -ForegroundColor Cyan
        docker ps -a --filter name=$ContainerName --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    }
    "logs" {
        Write-Host "ClickHouse container logs:" -ForegroundColor Cyan
        docker logs $ContainerName --tail 50 -f
    }
    "backup" {
        Write-Host "Creating backup..." -ForegroundColor Yellow
        `$backupDir = "backups/backup-`$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        New-Item -ItemType Directory -Path `$backupDir -Force
        Copy-Item -Path "data/*" -Destination `$backupDir -Recurse -Force
        Copy-Item -Path "config/*" -Destination `$backupDir -Recurse -Force
        Write-Host "Backup created: `$backupDir" -ForegroundColor Green
    }
    default {
        Write-Host "Usage: ./clickhouse-manager.ps1 [start|stop|restart|status|logs|backup]" -ForegroundColor Yellow
    }
}
"@
    
    $managerPath = Join-Path $WorkDir "scripts/clickhouse-manager.ps1"
    $managerScript | Out-File -FilePath $managerPath -Encoding UTF8
    Write-Success "Generated management script: scripts/clickhouse-manager.ps1"
}

# Show installation summary
function Show-Summary {
    Write-ColorText @"

===============================================================
                 Installation Summary                      
===============================================================

Working Directory: $WorkDir
Container Name: $ContainerName
HTTP Port: http://localhost:8123
TCP Port: localhost:9000
MySQL Port: localhost:9004

User Accounts:
   - default (no password)
   - admin (password: $Password)
   - readonly_user (password: ReadOnly@2024)

Management Commands:
   - Start:   ./scripts/clickhouse-manager.ps1 start
   - Stop:    ./scripts/clickhouse-manager.ps1 stop
   - Status:  ./scripts/clickhouse-manager.ps1 status
   - Logs:    ./scripts/clickhouse-manager.ps1 logs
   - Backup:  ./scripts/clickhouse-manager.ps1 backup

Configuration Files:
   - Main config: config/config.xml
   - Users config: config/users.xml
   - Passwords: config/passwords.txt

ClickHouse is ready to use!
"@ -Color "Green"
}

# Run installation
Install-ClickHouse 