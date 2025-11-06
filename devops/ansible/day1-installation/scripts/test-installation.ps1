# Ansible 安装验证脚本 (PowerShell)
# 用于验证 Ansible 安装和配置的正确性

param(
    [switch]$Verbose = $false
)

Write-Host "=== Ansible 安装验证脚本 ===" -ForegroundColor Green
Write-Host ""

# 1. 检查 Python 版本
Write-Host "1. 检查 Python 版本..." -ForegroundColor Cyan
try {
    $pythonVersion = python3 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python3 未安装或不在 PATH 中" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 检查 Python 版本时出错: $_" -ForegroundColor Red
    exit 1
}

# 2. 检查 Ansible 版本
Write-Host "2. 检查 Ansible 版本..." -ForegroundColor Cyan
try {
    $ansibleVersion = ansible --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $version = ($ansibleVersion -split "`n")[0]
        Write-Host "✓ $version" -ForegroundColor Green
    } else {
        Write-Host "✗ Ansible 未安装或不在 PATH 中" -ForegroundColor Red
        Write-Host "请运行: pip install ansible" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ 检查 Ansible 版本时出错: $_" -ForegroundColor Red
    exit 1
}

# 3. 检查 Ansible 组件
Write-Host "3. 检查 Ansible 组件..." -ForegroundColor Cyan
$components = @("ansible-playbook", "ansible-galaxy", "ansible-config")
foreach ($component in $components) {
    try {
        $result = & $component --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $component 可用" -ForegroundColor Green
        } else {
            Write-Host "✗ $component 不可用" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ 检查 $component 时出错" -ForegroundColor Red
    }
}

# 4. 测试本地连接
Write-Host "4. 测试本地连接..." -ForegroundColor Cyan
try {
    $pingResult = ansible localhost -m ping 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 本地连接测试成功" -ForegroundColor Green
        if ($Verbose) {
            Write-Host $pingResult -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ 本地连接测试失败" -ForegroundColor Red
        Write-Host $pingResult -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 本地连接测试出错: $_" -ForegroundColor Red
}

# 5. 检查配置文件
Write-Host "5. 检查配置文件..." -ForegroundColor Cyan
$configLocations = @(
    "$env:ANSIBLE_CONFIG",
    ".\ansible.cfg",
    "$env:USERPROFILE\.ansible.cfg",
    "C:\ansible\ansible.cfg"
)

$foundConfig = $false
foreach ($location in $configLocations) {
    if ($location -and (Test-Path $location)) {
        Write-Host "✓ 找到配置文件: $location" -ForegroundColor Green
        $foundConfig = $true
        break
    }
}

if (-not $foundConfig) {
    Write-Host "! 未找到配置文件，将使用默认配置" -ForegroundColor Yellow
}

# 6. 检查 SSH (如果在 WSL 或有 SSH 客户端)
Write-Host "6. 检查 SSH 客户端..." -ForegroundColor Cyan
try {
    $sshVersion = ssh -V 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ SSH 客户端可用: $sshVersion" -ForegroundColor Green
    } else {
        Write-Host "! SSH 客户端不可用，请安装 OpenSSH 或使用 WSL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "! SSH 客户端检查出错" -ForegroundColor Yellow
}

# 7. 生成测试报告
Write-Host ""
Write-Host "=== 安装验证完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "建议下一步:" -ForegroundColor Cyan
Write-Host "1. 如果所有检查都通过，可以开始学习 Day 2" -ForegroundColor White
Write-Host "2. 如果有错误，请根据错误信息进行修复" -ForegroundColor White
Write-Host "3. 准备一些测试虚拟机来实践 Ansible" -ForegroundColor White
Write-Host ""

# 输出到日志文件
$logFile = "ansible-test-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$output = @"
Ansible 安装验证报告
生成时间: $(Get-Date)
Python 版本: $pythonVersion
Ansible 版本: $ansibleVersion
配置文件: $(if ($foundConfig) { "找到" } else { "未找到" })
"@

$output | Out-File -FilePath $logFile -Encoding UTF8
Write-Host "测试日志已保存到: $logFile" -ForegroundColor Gray 