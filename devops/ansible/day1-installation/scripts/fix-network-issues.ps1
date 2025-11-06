# Ansible Day 1 Network Issues Fix Script

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("china", "global", "offline")]
    [string]$Mode = "china",
    
    [Parameter()]
    [switch]$Clean,
    
    [Parameter()]
    [switch]$Test
)

Write-Host "=== Ansible Day 1 Network Issues Fix ===" -ForegroundColor Cyan

function Test-NetworkConnectivity {
    Write-Host "`nTesting network connectivity..." -ForegroundColor Yellow
    
    $testUrls = @(
        "mirrors.aliyun.com",
        "archive.ubuntu.com", 
        "quay.io",
        "docker.io"
    )
    
    foreach ($url in $testUrls) {
        try {
            $result = Test-NetConnection $url -Port 80 -WarningAction SilentlyContinue
            if ($result.TcpTestSucceeded) {
                Write-Host "OK $url - Connection successful" -ForegroundColor Green
            } else {
                Write-Host "FAIL $url - Connection failed" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "ERROR $url - Connection error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Clean-Environment {
    Write-Host "`nCleaning environment..." -ForegroundColor Yellow
    
    # Stop and remove containers
    docker-compose -f ../configs/docker-compose.yml down 2>$null
    docker-compose -f ../configs/docker-compose-china.yml down 2>$null
    
    # Remove related images
    $images = docker images --format "table {{.Repository}}:{{.Tag}}" | Select-String "ansible|ubuntu:22.04|centos|alpine:3.18"
    if ($images) {
        Write-Host "Removing related images..." -ForegroundColor Gray
        $images | ForEach-Object {
            docker rmi $_.ToString().Trim() -f 2>$null
        }
    }
    
    # Clean Docker cache
    docker system prune -f 2>$null
    
    Write-Host "Environment cleaned" -ForegroundColor Green
}

function Start-Environment {
    param([string]$ConfigFile)
    
    Write-Host "`nStarting environment..." -ForegroundColor Yellow
    Write-Host "Using config file: $ConfigFile" -ForegroundColor Cyan
    
    try {
        # Build and start containers
        Set-Location ../configs
        docker-compose -f $ConfigFile up -d --build
        
        # Wait for containers to start
        Write-Host "Waiting for containers to start..." -ForegroundColor Gray
        Start-Sleep -Seconds 15
        
        # Check container status
        $containers = docker-compose -f $ConfigFile ps
        Write-Host "`nContainer status:" -ForegroundColor Cyan
        Write-Host $containers
        
        # Test SSH connections
        Write-Host "`nTesting SSH connections..." -ForegroundColor Yellow
        $nodes = @("ansible-node1", "ansible-node2", "ansible-node3")
        
        foreach ($node in $nodes) {
            try {
                $result = docker exec $node which sshd 2>$null
                if ($result) {
                    Write-Host "OK $node SSH service available" -ForegroundColor Green
                } else {
                    Write-Host "WARN $node SSH service not found" -ForegroundColor Yellow
                }
            }
            catch {
                Write-Host "ERROR $node cannot connect" -ForegroundColor Red
            }
        }
        
        Write-Host "`nEnvironment started successfully!" -ForegroundColor Green
        Write-Host "Use this command to enter control node:" -ForegroundColor Cyan
        Write-Host "docker exec -it ansible-control bash" -ForegroundColor White
        
        Set-Location ../scripts
        
    }
    catch {
        Write-Host "Failed to start: $($_.Exception.Message)" -ForegroundColor Red
        Set-Location ../scripts
        return $false
    }
    
    return $true
}

function Show-Diagnosis {
    Write-Host "`nNetwork diagnosis suggestions:" -ForegroundColor Cyan
    
    Write-Host "`n1. Check network connection:" -ForegroundColor Yellow
    Write-Host "   - Ensure internet connection is working" -ForegroundColor White
    Write-Host "   - Check for proxy or firewall restrictions" -ForegroundColor White
    
    Write-Host "`n2. Docker configuration:" -ForegroundColor Yellow
    Write-Host "   - Check if Docker Desktop is running" -ForegroundColor White
    Write-Host "   - Ensure Docker has sufficient resources" -ForegroundColor White
    
    Write-Host "`n3. DNS settings:" -ForegroundColor Yellow
    Write-Host "   - Try using public DNS (8.8.8.8, 114.114.114.114)" -ForegroundColor White
    Write-Host "   - Check corporate network DNS settings" -ForegroundColor White
    
    Write-Host "`n4. Mirror selection:" -ForegroundColor Yellow
    Write-Host "   - For China users: -Mode china" -ForegroundColor White
    Write-Host "   - For global users: -Mode global" -ForegroundColor White
    
    Write-Host "`n5. Solutions:" -ForegroundColor Yellow
    Write-Host "   ./fix-network-issues.ps1 -Mode china   # Use China mirrors" -ForegroundColor White
    Write-Host "   ./fix-network-issues.ps1 -Clean        # Clean and retry" -ForegroundColor White
    Write-Host "   ./fix-network-issues.ps1 -Test         # Test network only" -ForegroundColor White
}

# Main logic
try {
    # Check if Docker is running
    $dockerStatus = docker version 2>$null
    if (-not $dockerStatus) {
        Write-Host "Docker is not running or not installed" -ForegroundColor Red
        Write-Host "Please ensure Docker Desktop is started" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Docker status OK" -ForegroundColor Green
    
    # Test only mode
    if ($Test) {
        Test-NetworkConnectivity
        Show-Diagnosis
        exit 0
    }
    
    # Clean mode
    if ($Clean) {
        Clean-Environment
        Write-Host "Cleanup complete, please run the script again to start environment" -ForegroundColor Green
        exit 0
    }
    
    # Test network connectivity
    Test-NetworkConnectivity
    
    # Select config file
    $configFile = switch ($Mode) {
        "china" { "docker-compose-china.yml" }
        "global" { "docker-compose.yml" }
        "offline" { "docker-compose-offline.yml" }
    }
    
    if (-not (Test-Path "../configs/$configFile")) {
        Write-Host "Config file does not exist: $configFile" -ForegroundColor Red
        exit 1
    }
    
    # Clean old environment
    Write-Host "`nCleaning old environment..." -ForegroundColor Yellow
    docker-compose -f ../configs/docker-compose.yml down 2>$null
    docker-compose -f ../configs/docker-compose-china.yml down 2>$null
    
    # Start new environment
    $success = Start-Environment -ConfigFile $configFile
    
    if ($success) {
        Write-Host "`nAnsible environment started successfully!" -ForegroundColor Green
        Write-Host "Now you can start Day 1 learning!" -ForegroundColor Cyan
    } else {
        Write-Host "`nIf you still have issues, please try:" -ForegroundColor Yellow
        Write-Host "1. Run: ./fix-network-issues.ps1 -Clean" -ForegroundColor White
        Write-Host "2. Then: ./fix-network-issues.ps1 -Mode china" -ForegroundColor White
        Show-Diagnosis
    }
    
}
catch {
    Write-Host "Script execution failed: $($_.Exception.Message)" -ForegroundColor Red
    Show-Diagnosis
    exit 1
} 