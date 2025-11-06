# SSH Key Generation Script
# Generate SSH key pair for Alibaba Cloud ClickHouse cluster deployment

param(
    [string]$KeyPath = "infrastructure\terraform\clickhouse_key",
    [string]$KeyName = "clickhouse-keypair",
    [int]$KeySize = 2048
)

$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

Write-Host "🔑 SSH Key Generation Script" -ForegroundColor $Blue
Write-Host "===========================================" -ForegroundColor $Blue

# Check if ssh-keygen is available
function Test-SshKeygen {
    try {
        ssh-keygen -h 2>$null
        return $true
    }
    catch {
        Write-Host "❌ ssh-keygen not found" -ForegroundColor $Red
        Write-Host "Please install OpenSSH client or Git for Windows" -ForegroundColor $Yellow
        return $false
    }
}

# Generate SSH key pair
function New-SshKeyPair {
    param(
        [string]$KeyPath,
        [int]$KeySize
    )
    
    Write-Host "🔐 Generating SSH key pair..." -ForegroundColor $Blue
    Write-Host "Key path: $KeyPath" -ForegroundColor $Blue
    Write-Host "Key size: $KeySize bits" -ForegroundColor $Blue
    
    # Check if key files already exist
    if (Test-Path "$KeyPath" -or Test-Path "$KeyPath.pub") {
        Write-Host "⚠️  Key files already exist" -ForegroundColor $Yellow
        $overwrite = Read-Host "Overwrite existing keys? (y/N)"
        if ($overwrite -ne "y" -and $overwrite -ne "Y") {
            Write-Host "⏭️  Skipping key generation" -ForegroundColor $Yellow
            return $true
        }
        
        # Remove existing keys
        if (Test-Path "$KeyPath") { Remove-Item "$KeyPath" -Force }
        if (Test-Path "$KeyPath.pub") { Remove-Item "$KeyPath.pub" -Force }
    }
    
    try {
        # Generate key pair (no password)
        ssh-keygen -t rsa -b $KeySize -f $KeyPath -N '""' -C "clickhouse-cluster-key"
        
        if (Test-Path "$KeyPath" -and Test-Path "$KeyPath.pub") {
            Write-Host "✅ SSH key pair generated successfully" -ForegroundColor $Green
            Write-Host "Private key: $KeyPath" -ForegroundColor $Blue
            Write-Host "Public key: $KeyPath.pub" -ForegroundColor $Blue
            return $true
        }
        else {
            Write-Host "❌ Key file generation failed" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error generating SSH key: $($_.Exception.Message)" -ForegroundColor $Red
        return $false
    }
}

# Show public key content
function Show-PublicKey {
    param([string]$KeyPath)
    
    $publicKeyPath = "$KeyPath.pub"
    if (Test-Path $publicKeyPath) {
        Write-Host "`n📋 Public key content:" -ForegroundColor $Blue
        Write-Host "========================================" -ForegroundColor $Blue
        Get-Content $publicKeyPath
        Write-Host "========================================" -ForegroundColor $Blue
    }
}

# Set file permissions (Windows)
function Set-KeyPermissions {
    param([string]$KeyPath)
    
    try {
        # Set private key file permissions (current user read/write only)
        if (Test-Path $KeyPath) {
            icacls $KeyPath /inheritance:r /grant:r "$env:USERNAME:(R,W)"
            Write-Host "✅ Private key file permissions set" -ForegroundColor $Green
        }
    }
    catch {
        Write-Host "⚠️  Warning setting file permissions: $($_.Exception.Message)" -ForegroundColor $Yellow
    }
}

# Verify key pair
function Test-KeyPair {
    param([string]$KeyPath)
    
    Write-Host "🔍 Verifying key pair..." -ForegroundColor $Blue
    
    try {
        # Generate public key from private key and compare
        $generatedPublicKey = ssh-keygen -y -f $KeyPath
        $existingPublicKey = (Get-Content "$KeyPath.pub").Split(' ')[0,1] -join ' '
        
        if ($generatedPublicKey -eq $existingPublicKey) {
            Write-Host "✅ Key pair verification successful" -ForegroundColor $Green
            return $true
        }
        else {
            Write-Host "❌ Key pair mismatch" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "⚠️  Warning during key pair verification: $($_.Exception.Message)" -ForegroundColor $Yellow
        return $true  # Don't affect main flow
    }
}

# Create usage instructions
function New-UsageInstructions {
    param([string]$KeyPath)
    
    $instructionsPath = "$(Split-Path $KeyPath)\SSH-USAGE.md"
    
    $instructions = @"
# SSH Key Usage Instructions

## Generated Files
- **Private key**: $KeyPath
- **Public key**: $KeyPath.pub

## Connecting to Servers
Use the following commands to connect to ClickHouse nodes:

``````bash
# Connect to node 1
ssh -i $KeyPath ubuntu@<node1_public_ip>

# Connect to node 2  
ssh -i $KeyPath ubuntu@<node2_public_ip>

# Connect to node 3
ssh -i $KeyPath ubuntu@<node3_public_ip>

# Connect to ZooKeeper node
ssh -i $KeyPath ubuntu@<zookeeper_public_ip>
``````

## Important Notes
1. Protect your private key file, do not share with others
2. Private key file permissions should be set to current user read-only
3. If using on Linux/macOS, set file permissions:
   ``````bash
   chmod 600 $KeyPath
   ``````

## Terraform Output
After deployment, view connection information with:
``````bash
terraform output ssh_commands
``````

## Troubleshooting
If SSH connection fails, check:
1. Public IP address is correct
2. Security group allows SSH (port 22) access
3. Private key file permissions are correct
4. Server has fully started
"@

    $instructions | Out-File -FilePath $instructionsPath -Encoding UTF8
    Write-Host "📖 Usage instructions created: $instructionsPath" -ForegroundColor $Blue
}

# Main function
function Main {
    Write-Host "Starting SSH key pair generation..." -ForegroundColor $Blue
    
    # Check ssh-keygen
    if (-not (Test-SshKeygen)) {
        Write-Host "Please install OpenSSH or run this script with Git Bash" -ForegroundColor $Yellow
        exit 1
    }
    
    # Ensure directory exists
    $keyDir = Split-Path $KeyPath -Parent
    if ($keyDir -and -not (Test-Path $keyDir)) {
        New-Item -ItemType Directory -Path $keyDir -Force | Out-Null
        Write-Host "✅ Created directory: $keyDir" -ForegroundColor $Green
    }
    
    # Generate key pair
    if (New-SshKeyPair -KeyPath $KeyPath -KeySize $KeySize) {
        # Set permissions
        Set-KeyPermissions -KeyPath $KeyPath
        
        # Verify key pair
        Test-KeyPair -KeyPath $KeyPath | Out-Null
        
        # Show public key
        Show-PublicKey -KeyPath $KeyPath
        
        # Create usage instructions
        New-UsageInstructions -KeyPath $KeyPath
        
        Write-Host "`n🎉 SSH key generation completed!" -ForegroundColor $Green
        Write-Host "You can now run Terraform deployment commands" -ForegroundColor $Blue
    }
    else {
        Write-Host "❌ SSH key generation failed" -ForegroundColor $Red
        exit 1
    }
}

# Show help information
function Show-Help {
    Write-Host "SSH Key Generation Script"
    Write-Host ""
    Write-Host "Usage: .\generate-ssh-key.ps1 [parameters]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -KeyPath    Key file path (default: infrastructure\terraform\clickhouse_key)"
    Write-Host "  -KeyName    Key pair name (default: clickhouse-keypair)"  
    Write-Host "  -KeySize    Key size (default: 2048)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\generate-ssh-key.ps1                           # Use default settings"
    Write-Host "  .\generate-ssh-key.ps1 -KeySize 4096            # Use 4096-bit key"
    Write-Host "  .\generate-ssh-key.ps1 -KeyPath my_key          # Custom key path"
}

# Script entry point
if ($args -contains "-help" -or $args -contains "--help") {
    Show-Help
}
else {
    Main
} 