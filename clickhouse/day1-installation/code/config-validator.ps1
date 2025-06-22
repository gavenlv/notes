# ClickHouse Configuration File Validation and Hands-on Practice Script
# For validating configuration file correctness and demonstrating configuration operations

param(
    [string]$WorkDir = "C:\ClickHouse",
    [string]$ContainerName = "clickhouse-server"
)

# Color output functions
function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Section {
    param([string]$Title)
    Write-ColorText "`n" + "="*60 -Color "Cyan"
    Write-ColorText "  $Title" -Color "Cyan"
    Write-ColorText "="*60 -Color "Cyan"
}

function Write-Step {
    param([string]$Message)
    Write-ColorText "`n>>> $Message" -Color "Yellow"
}

function Write-Success {
    param([string]$Message)
    Write-ColorText "[SUCCESS] $Message" -Color "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorText "[WARNING] $Message" -Color "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorText "[ERROR] $Message" -Color "Red"
}

# Main function
function Start-ConfigValidation {
    Write-ColorText @"
===============================================================
       ClickHouse Configuration Validation and Practice Tool 
                Windows Chinese Users Edition               
===============================================================
"@ -Color "Magenta"

    # 1. Environment check
    Write-Section "Environment Check"
    Test-Environment

    # 2. Configuration file syntax validation
    Write-Section "Configuration File Syntax Validation"
    Test-ConfigSyntax

    # 3. User configuration validation
    Write-Section "User Configuration Validation"
    Test-UserConfig

    # 4. Password encryption demonstration
    Write-Section "Password Encryption Demonstration"
    Demo-PasswordEncryption

    # 5. Network configuration validation
    Write-Section "Network Configuration Validation"
    Test-NetworkConfig

    # 6. Performance configuration validation
    Write-Section "Performance Configuration Validation"
    Test-PerformanceConfig

    # 7. Log configuration validation
    Write-Section "Log Configuration Validation"
    Test-LogConfig

    # 8. Real-time configuration modification demonstration
    Write-Section "Real-time Configuration Modification Demo"
    Demo-ConfigModification

    Write-Success "Configuration validation and demonstration completed!"
}

# Environment check
function Test-Environment {
    Write-Step "Check working directory"
    if (Test-Path $WorkDir) {
        Write-Success "Working directory exists: $WorkDir"
    } else {
        Write-Error "Working directory does not exist: $WorkDir"
        return
    }

    Write-Step "Check configuration files"
    $configFiles = @("config/config.xml", "config/users.xml")
    foreach ($file in $configFiles) {
        $fullPath = Join-Path $WorkDir $file
        if (Test-Path $fullPath) {
            Write-Success "Configuration file exists: $file"
        } else {
            Write-Error "Configuration file missing: $file"
        }
    }

    Write-Step "Check container status"
    try {
        $containerStatus = docker ps --format "{{.Names}}\t{{.Status}}" | Select-String $ContainerName
        if ($containerStatus) {
            Write-Success "Container running normally: $containerStatus"
        } else {
            Write-Warning "Container not running, some tests will not be executable"
        }
    } catch {
        Write-Warning "Unable to check container status"
    }
}

# Configuration file syntax validation
function Test-ConfigSyntax {
    Write-Step "Validate config.xml syntax"
    $configPath = Join-Path $WorkDir "config/config.xml"
    
    if (Test-Path $configPath) {
        try {
            [xml]$configXml = Get-Content $configPath -Encoding UTF8
            Write-Success "config.xml syntax is correct"
            
            # Check key configuration items
            $httpPort = $configXml.yandex.http_port
            $tcpPort = $configXml.yandex.tcp_port
            $listenHost = $configXml.yandex.listen_host
            
            Write-ColorText "  - HTTP Port: $httpPort" -Color "Gray"
            Write-ColorText "  - TCP Port: $tcpPort" -Color "Gray"
            Write-ColorText "  - Listen Address: $listenHost" -Color "Gray"
            
        } catch {
            Write-Error "config.xml syntax error: $_"
        }
    }

    Write-Step "Validate users.xml syntax"
    $usersPath = Join-Path $WorkDir "config/users.xml"
    
    if (Test-Path $usersPath) {
        try {
            [xml]$usersXml = Get-Content $usersPath -Encoding UTF8
            Write-Success "users.xml syntax is correct"
            
            # Check user configuration
            $users = $usersXml.yandex.users.ChildNodes | Where-Object { $_.NodeType -eq "Element" }
            Write-ColorText "  - Number of configured users: $($users.Count)" -Color "Gray"
            foreach ($user in $users) {
                Write-ColorText "    * $($user.Name)" -Color "White"
            }
            
        } catch {
            Write-Error "users.xml syntax error: $_"
        }
    }
}

# User configuration validation
function Test-UserConfig {
    Write-Step "Test default user connection"
    try {
        $result = docker exec $ContainerName clickhouse-client --query "SELECT 'Default user test passed'" 2>$null
        if ($result -match "Default user test passed") {
            Write-Success "Default user connection normal"
        } else {
            Write-Warning "Default user connection abnormal"
        }
    } catch {
        Write-Warning "Unable to test default user connection"
    }

    Write-Step "Test admin user connection"
    $adminPassword = Get-AdminPassword
    if ($adminPassword) {
        try {
            $result = docker exec $ContainerName clickhouse-client --user admin --password $adminPassword --query "SELECT 'Admin user test passed'" 2>$null
            if ($result -match "Admin user test passed") {
                Write-Success "Admin user connection normal"
            } else {
                Write-Warning "Admin user connection abnormal"
            }
        } catch {
            Write-Warning "Unable to test admin user connection"
        }
    }

    Write-Step "Test readonly user connection"
    try {
        $result = docker exec $ContainerName clickhouse-client --user readonly_user --password "ReadOnly@2024" --query "SELECT 'Readonly user test passed'" 2>$null
        if ($result -match "Readonly user test passed") {
            Write-Success "Readonly user connection normal"
            
            # Test readonly restrictions
            try {
                $createResult = docker exec $ContainerName clickhouse-client --user readonly_user --password "ReadOnly@2024" --query "CREATE TABLE test (id UInt32) ENGINE = Memory" 2>&1
                if ($createResult -match "readonly") {
                    Write-Success "Readonly restrictions working properly"
                } else {
                    Write-Warning "Readonly restrictions may not be working"
                }
            } catch {
                Write-Success "Readonly restrictions working properly (CREATE blocked)"
            }
        } else {
            Write-Warning "Readonly user connection abnormal"
        }
    } catch {
        Write-Warning "Unable to test readonly user connection"
    }
}

# Password encryption demonstration
function Demo-PasswordEncryption {
    Write-Step "Generate strong password"
    $strongPassword = Generate-StrongPassword
    Write-ColorText "Generated strong password: $strongPassword" -Color "White"
    
    Write-Step "SHA256 encryption demonstration"
    $sha256Hash = Get-SHA256Hash $strongPassword
    Write-ColorText "Original password: $strongPassword" -Color "Gray"
    Write-ColorText "SHA256 hash: $sha256Hash" -Color "Yellow"
    
    Write-Step "Create user configuration with encrypted password"
    $userConfig = @"
<new_user>
    <password_sha256_hex>$sha256Hash</password_sha256_hex>
    <networks>
        <ip>127.0.0.1</ip>
        <ip>::1</ip>
    </networks>
    <profile>default</profile>
    <quota>default</quota>
</new_user>
"@
    Write-ColorText "User configuration example:" -Color "Cyan"
    Write-ColorText $userConfig -Color "White"
    
    Write-Step "Password security best practices"
    Write-ColorText "[BEST PRACTICE] Use SHA256 hash instead of plaintext" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Password length >= 12 characters" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Include uppercase, lowercase, numbers, and special characters" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Restrict network access with IP whitelist" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Use different passwords for different users" -Color "Green"
}

# Network configuration validation
function Test-NetworkConfig {
    Write-Step "Test HTTP port connectivity"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8123" -Method GET -TimeoutSec 5
        Write-Success "HTTP port 8123 accessible, status: $($response.StatusCode)"
    } catch {
        Write-Error "HTTP port 8123 not accessible"
    }
    
    Write-Step "Test TCP port connectivity"
    try {
        $tcpTest = Test-NetConnection -ComputerName localhost -Port 9000 -WarningAction SilentlyContinue
        if ($tcpTest.TcpTestSucceeded) {
            Write-Success "TCP port 9000 accessible"
        } else {
            Write-Error "TCP port 9000 not accessible"
        }
    } catch {
        Write-Warning "Unable to test TCP port connectivity"
    }
    
    Write-Step "Test MySQL compatibility port"
    try {
        $mysqlTest = Test-NetConnection -ComputerName localhost -Port 9004 -WarningAction SilentlyContinue
        if ($mysqlTest.TcpTestSucceeded) {
            Write-Success "MySQL port 9004 accessible"
        } else {
            Write-Error "MySQL port 9004 not accessible"
        }
    } catch {
        Write-Warning "Unable to test MySQL port connectivity"
    }
}

# Performance configuration validation
function Test-PerformanceConfig {
    Write-Step "Check memory configuration"
    try {
        $memorySettings = docker exec $ContainerName clickhouse-client --query "SELECT name, value FROM system.settings WHERE name LIKE '%memory%' ORDER BY name" 2>$null
        if ($memorySettings) {
            Write-Success "Memory configuration retrieved"
            Write-ColorText "Key memory settings:" -Color "Gray"
            $memorySettings -split "`n" | ForEach-Object {
                if ($_ -match "max_memory_usage|max_server_memory") {
                    Write-ColorText "  $_" -Color "White"
                }
            }
        }
    } catch {
        Write-Warning "Unable to retrieve memory configuration"
    }
    
    Write-Step "Check concurrent query limits"
    try {
        $querySettings = docker exec $ContainerName clickhouse-client --query "SELECT name, value FROM system.settings WHERE name LIKE '%concurrent%' OR name LIKE '%connection%' ORDER BY name" 2>$null
        if ($querySettings) {
            Write-Success "Query and connection limits retrieved"
            Write-ColorText "Concurrent settings:" -Color "Gray"
            $querySettings -split "`n" | ForEach-Object {
                if ($_ -and $_ -notmatch "^\s*$") {
                    Write-ColorText "  $_" -Color "White"
                }
            }
        }
    } catch {
        Write-Warning "Unable to retrieve query settings"
    }
}

# Log configuration validation
function Test-LogConfig {
    Write-Step "Check log file existence"
    $logPath = Join-Path $WorkDir "logs"
    if (Test-Path $logPath) {
        $logFiles = Get-ChildItem $logPath -Filter "*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            Write-Success "Log files found: $($logFiles.Count) files"
            foreach ($logFile in $logFiles) {
                Write-ColorText "  - $($logFile.Name) ($([math]::Round($logFile.Length/1KB, 2)) KB)" -Color "Gray"
            }
        } else {
            Write-Warning "No log files found in $logPath"
        }
    } else {
        Write-Error "Log directory not found: $logPath"
    }
    
    Write-Step "Check log level configuration"
    try {
        $logLevel = docker exec $ContainerName clickhouse-client --query "SELECT value FROM system.server_settings WHERE name = 'logger.level'" 2>$null
        if ($logLevel) {
            Write-Success "Current log level: $logLevel"
        }
    } catch {
        Write-Warning "Unable to retrieve log level"
    }
}

# Real-time configuration modification demonstration
function Demo-ConfigModification {
    Write-Step "Backup current configuration"
    $backupDir = Join-Path $WorkDir "config/backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Copy-Item -Path (Join-Path $WorkDir "config/*.xml") -Destination $backupDir -Force
    Write-Success "Configuration backed up to: $backupDir"
    
    Write-Step "Demonstrate configuration modification"
    Write-ColorText "Example: Modify log level to 'debug'" -Color "Cyan"
    Write-ColorText "1. Edit config/config.xml" -Color "Gray"
    Write-ColorText "2. Change <level>information</level> to <level>debug</level>" -Color "Gray"
    Write-ColorText "3. Restart container to apply changes" -Color "Gray"
    Write-ColorText "4. Verify changes with: docker exec $ContainerName clickhouse-client --query `"SELECT value FROM system.server_settings WHERE name = 'logger.level'`"" -Color "Gray"
    
    Write-Step "Configuration modification best practices"
    Write-ColorText "[BEST PRACTICE] Always backup before modification" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Validate XML syntax before applying" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Test changes in development environment first" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Monitor logs after changes" -Color "Green"
    Write-ColorText "[BEST PRACTICE] Have rollback plan ready" -Color "Green"
}

# Helper functions
function Get-AdminPassword {
    $passwordFile = Join-Path $WorkDir "config/passwords.txt"
    if (Test-Path $passwordFile) {
        $content = Get-Content $passwordFile -Encoding UTF8
        $passwordLine = $content | Where-Object { $_ -match "Original Password:" }
        if ($passwordLine) {
            return $passwordLine -replace ".*Original Password:\s*", ""
        }
    }
    return "ClickHouse@2024"  # Default password
}

function Generate-StrongPassword {
    $length = 16
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    $random = New-Object System.Random
    
    for ($i = 0; $i -lt $length; $i++) {
        $password += $chars[$random.Next($chars.Length)]
    }
    
    return $password
}

function Get-SHA256Hash {
    param([string]$InputString)
    
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($InputString))
    $hash = [System.BitConverter]::ToString($hashBytes).Replace('-', '').ToLower()
    $sha256.Dispose()
    
    return $hash
}

# Run validation
Start-ConfigValidation 