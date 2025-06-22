# SSH密钥生成脚本
# 为阿里云ClickHouse集群部署生成SSH密钥对

param(
    [string]$KeyPath = "infrastructure\terraform\clickhouse_key",
    [string]$KeyName = "clickhouse-keypair",
    [int]$KeySize = 2048
)

$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

Write-Host "🔑 SSH密钥生成脚本" -ForegroundColor $Blue
Write-Host "===========================================" -ForegroundColor $Blue

# 检查ssh-keygen是否可用
function Test-SshKeygen {
    try {
        ssh-keygen -h 2>$null
        return $true
    }
    catch {
        Write-Host "❌ ssh-keygen未找到" -ForegroundColor $Red
        Write-Host "请安装OpenSSH客户端或Git for Windows" -ForegroundColor $Yellow
        return $false
    }
}

# 生成SSH密钥对
function New-SshKeyPair {
    param(
        [string]$KeyPath,
        [int]$KeySize
    )
    
    Write-Host "🔐 生成SSH密钥对..." -ForegroundColor $Blue
    Write-Host "密钥路径: $KeyPath" -ForegroundColor $Blue
    Write-Host "密钥大小: $KeySize bits" -ForegroundColor $Blue
    
    # 检查是否已存在密钥文件
    if (Test-Path "$KeyPath" -or Test-Path "$KeyPath.pub") {
        Write-Host "⚠️  密钥文件已存在" -ForegroundColor $Yellow
        $overwrite = Read-Host "是否覆盖现有密钥? (y/N)"
        if ($overwrite -ne "y" -and $overwrite -ne "Y") {
            Write-Host "⏭️  跳过密钥生成" -ForegroundColor $Yellow
            return $true
        }
        
        # 删除现有密钥
        if (Test-Path "$KeyPath") { Remove-Item "$KeyPath" -Force }
        if (Test-Path "$KeyPath.pub") { Remove-Item "$KeyPath.pub" -Force }
    }
    
    try {
        # 生成密钥对（无密码）
        ssh-keygen -t rsa -b $KeySize -f $KeyPath -N '""' -C "clickhouse-cluster-key"
        
        if (Test-Path "$KeyPath" -and Test-Path "$KeyPath.pub") {
            Write-Host "✅ SSH密钥对生成成功" -ForegroundColor $Green
            Write-Host "私钥: $KeyPath" -ForegroundColor $Blue
            Write-Host "公钥: $KeyPath.pub" -ForegroundColor $Blue
            return $true
        }
        else {
            Write-Host "❌ 密钥文件生成失败" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "❌ 生成SSH密钥时出错: $($_.Exception.Message)" -ForegroundColor $Red
        return $false
    }
}

# 显示公钥内容
function Show-PublicKey {
    param([string]$KeyPath)
    
    $publicKeyPath = "$KeyPath.pub"
    if (Test-Path $publicKeyPath) {
        Write-Host "`n📋 公钥内容:" -ForegroundColor $Blue
        Write-Host "========================================" -ForegroundColor $Blue
        Get-Content $publicKeyPath
        Write-Host "========================================" -ForegroundColor $Blue
    }
}

# 设置文件权限（Windows）
function Set-KeyPermissions {
    param([string]$KeyPath)
    
    try {
        # 设置私钥文件权限（仅当前用户可读写）
        if (Test-Path $KeyPath) {
            icacls $KeyPath /inheritance:r /grant:r "$env:USERNAME:(R,W)"
            Write-Host "✅ 私钥文件权限已设置" -ForegroundColor $Green
        }
    }
    catch {
        Write-Host "⚠️  设置文件权限时出现警告: $($_.Exception.Message)" -ForegroundColor $Yellow
    }
}

# 验证密钥对
function Test-KeyPair {
    param([string]$KeyPath)
    
    Write-Host "🔍 验证密钥对..." -ForegroundColor $Blue
    
    try {
        # 从私钥生成公钥并比较
        $generatedPublicKey = ssh-keygen -y -f $KeyPath
        $existingPublicKey = (Get-Content "$KeyPath.pub").Split(' ')[0,1] -join ' '
        
        if ($generatedPublicKey -eq $existingPublicKey) {
            Write-Host "✅ 密钥对验证成功" -ForegroundColor $Green
            return $true
        }
        else {
            Write-Host "❌ 密钥对不匹配" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "⚠️  密钥对验证出现警告: $($_.Exception.Message)" -ForegroundColor $Yellow
        return $true  # 不影响主流程
    }
}

# 创建使用说明
function New-UsageInstructions {
    param([string]$KeyPath)
    
    $instructionsPath = "$(Split-Path $KeyPath)\SSH-USAGE.md"
    
    $instructions = @"
# SSH密钥使用说明

## 生成的文件
- **私钥**: $KeyPath
- **公钥**: $KeyPath.pub

## 连接服务器
使用以下命令连接到ClickHouse节点：

``````bash
# 连接到节点1
ssh -i $KeyPath ubuntu@<node1_public_ip>

# 连接到节点2  
ssh -i $KeyPath ubuntu@<node2_public_ip>

# 连接到节点3
ssh -i $KeyPath ubuntu@<node3_public_ip>

# 连接到ZooKeeper节点
ssh -i $KeyPath ubuntu@<zookeeper_public_ip>
``````

## 注意事项
1. 保护好私钥文件，不要泄露给他人
2. 私钥文件权限应设置为仅当前用户可读
3. 如果在Linux/macOS上使用，需要设置文件权限：
   ``````bash
   chmod 600 $KeyPath
   ``````

## Terraform输出
部署完成后，可以通过以下命令查看连接信息：
``````bash
terraform output ssh_commands
``````

## 故障排除
如果SSH连接失败，请检查：
1. 公网IP地址是否正确
2. 安全组是否允许SSH(22端口)访问
3. 私钥文件权限是否正确
4. 服务器是否已完全启动
"@

    $instructions | Out-File -FilePath $instructionsPath -Encoding UTF8
    Write-Host "📖 使用说明已创建: $instructionsPath" -ForegroundColor $Blue
}

# 主函数
function Main {
    Write-Host "开始生成SSH密钥对..." -ForegroundColor $Blue
    
    # 检查ssh-keygen
    if (-not (Test-SshKeygen)) {
        Write-Host "请安装OpenSSH或使用Git Bash运行此脚本" -ForegroundColor $Yellow
        exit 1
    }
    
    # 确保目录存在
    $keyDir = Split-Path $KeyPath -Parent
    if ($keyDir -and -not (Test-Path $keyDir)) {
        New-Item -ItemType Directory -Path $keyDir -Force | Out-Null
        Write-Host "✅ 创建目录: $keyDir" -ForegroundColor $Green
    }
    
    # 生成密钥对
    if (New-SshKeyPair -KeyPath $KeyPath -KeySize $KeySize) {
        # 设置权限
        Set-KeyPermissions -KeyPath $KeyPath
        
        # 验证密钥对
        Test-KeyPair -KeyPath $KeyPath | Out-Null
        
        # 显示公钥
        Show-PublicKey -KeyPath $KeyPath
        
        # 创建使用说明
        New-UsageInstructions -KeyPath $KeyPath
        
        Write-Host "`n🎉 SSH密钥生成完成!" -ForegroundColor $Green
        Write-Host "现在可以运行Terraform部署命令了" -ForegroundColor $Blue
    }
    else {
        Write-Host "❌ SSH密钥生成失败" -ForegroundColor $Red
        exit 1
    }
}

# 显示帮助信息
function Show-Help {
    Write-Host "SSH密钥生成脚本"
    Write-Host ""
    Write-Host "用法: .\generate-ssh-key.ps1 [参数]"
    Write-Host ""
    Write-Host "参数:"
    Write-Host "  -KeyPath    密钥文件路径 (默认: infrastructure\terraform\clickhouse_key)"
    Write-Host "  -KeyName    密钥对名称 (默认: clickhouse-keypair)"  
    Write-Host "  -KeySize    密钥大小 (默认: 2048)"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\generate-ssh-key.ps1                           # 使用默认设置"
    Write-Host "  .\generate-ssh-key.ps1 -KeySize 4096            # 使用4096位密钥"
    Write-Host "  .\generate-ssh-key.ps1 -KeyPath my_key          # 自定义密钥路径"
}

# 脚本入口
if ($args -contains "-help" -or $args -contains "--help") {
    Show-Help
}
else {
    Main
} 