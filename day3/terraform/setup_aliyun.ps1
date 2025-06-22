# 阿里云ClickHouse集群部署脚本
# 作者: ClickHouse学习教程
# 版本: 1.0

param(
    [string]$AccessKeyPath = "C:\Users\mingbo\aliyun\AccessKey.csv",
    [string]$Region = "cn-beijing",
    [string]$Action = "plan"  # plan, apply, destroy
)

# 颜色定义
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

Write-Host "🚀 阿里云 ClickHouse 集群部署脚本" -ForegroundColor $Blue
Write-Host "================================================" -ForegroundColor $Blue

# 检查Terraform是否安装
function Test-Terraform {
    try {
        $version = terraform version
        Write-Host "✅ Terraform已安装: $($version[0])" -ForegroundColor $Green
        return $true
    }
    catch {
        Write-Host "❌ Terraform未安装，请先安装Terraform" -ForegroundColor $Red
        Write-Host "下载地址: https://www.terraform.io/downloads.html" -ForegroundColor $Yellow
        return $false
    }
}

# 读取阿里云AccessKey
function Read-AccessKey {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        Write-Host "❌ AccessKey文件不存在: $Path" -ForegroundColor $Red
        Write-Host "请确保阿里云AccessKey文件存在" -ForegroundColor $Yellow
        return $null
    }
    
    try {
        $content = Get-Content $Path
        $accessKeyId = ""
        $accessKeySecret = ""
        
        # 解析CSV格式
        foreach ($line in $content) {
            if ($line -match "AccessKey ID.*?([A-Za-z0-9]+)") {
                $accessKeyId = $matches[1]
            }
            elseif ($line -match "AccessKey Secret.*?([A-Za-z0-9/+=]+)") {
                $accessKeySecret = $matches[1]
            }
            elseif ($line -contains "," -and $accessKeyId -eq "") {
                # CSV格式: AccessKey ID, AccessKey Secret
                $parts = $line -split ","
                if ($parts.Length -eq 2) {
                    $accessKeyId = $parts[0].Trim()
                    $accessKeySecret = $parts[1].Trim()
                }
            }
        }
        
        if ($accessKeyId -and $accessKeySecret) {
            Write-Host "✅ 成功读取AccessKey配置" -ForegroundColor $Green
            return @{
                AccessKeyId = $accessKeyId
                AccessKeySecret = $accessKeySecret
            }
        }
        else {
            Write-Host "❌ 无法解析AccessKey文件" -ForegroundColor $Red
            return $null
        }
    }
    catch {
        Write-Host "❌ 读取AccessKey文件时出错: $($_.Exception.Message)" -ForegroundColor $Red
        return $null
    }
}

# 设置环境变量
function Set-AliyunEnvironment {
    param($AccessKey, $Region)
    
    $env:ALICLOUD_ACCESS_KEY = $AccessKey.AccessKeyId
    $env:ALICLOUD_SECRET_KEY = $AccessKey.AccessKeySecret
    $env:ALICLOUD_REGION = $Region
    
    Write-Host "✅ 环境变量已设置" -ForegroundColor $Green
    Write-Host "   Region: $Region" -ForegroundColor $Blue
    Write-Host "   AccessKey ID: $($AccessKey.AccessKeyId.Substring(0,8))****" -ForegroundColor $Blue
}

# 初始化Terraform
function Initialize-Terraform {
    Write-Host "🔧 初始化Terraform..." -ForegroundColor $Blue
    
    Set-Location "infrastructure\terraform"
    
    try {
        terraform init
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Terraform初始化成功" -ForegroundColor $Green
            return $true
        }
        else {
            Write-Host "❌ Terraform初始化失败" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Terraform初始化出错: $($_.Exception.Message)" -ForegroundColor $Red
        return $false
    }
}

# 执行Terraform命令
function Invoke-TerraformAction {
    param([string]$Action)
    
    Write-Host "🚀 执行Terraform $Action..." -ForegroundColor $Blue
    
    switch ($Action.ToLower()) {
        "plan" {
            terraform plan -out=tfplan
        }
        "apply" {
            if (Test-Path "tfplan") {
                terraform apply tfplan
            }
            else {
                terraform apply -auto-approve
            }
        }
        "destroy" {
            terraform destroy -auto-approve
        }
        default {
            Write-Host "❌ 无效的操作: $Action" -ForegroundColor $Red
            Write-Host "支持的操作: plan, apply, destroy" -ForegroundColor $Yellow
            return $false
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Terraform $Action 执行成功" -ForegroundColor $Green
        return $true
    }
    else {
        Write-Host "❌ Terraform $Action 执行失败" -ForegroundColor $Red
        return $false
    }
}

# 显示输出信息
function Show-TerraformOutput {
    Write-Host "📋 基础设施信息:" -ForegroundColor $Blue
    terraform output
}

# 主函数
function Main {
    Write-Host "开始部署阿里云ClickHouse集群..." -ForegroundColor $Blue
    
    # 检查Terraform
    if (-not (Test-Terraform)) {
        exit 1
    }
    
    # 读取AccessKey
    $accessKey = Read-AccessKey -Path $AccessKeyPath
    if (-not $accessKey) {
        exit 1
    }
    
    # 设置环境变量
    Set-AliyunEnvironment -AccessKey $accessKey -Region $Region
    
    # 初始化Terraform
    if (-not (Initialize-Terraform)) {
        exit 1
    }
    
    # 执行Terraform操作
    if (Invoke-TerraformAction -Action $Action) {
        if ($Action -eq "apply") {
            Show-TerraformOutput
        }
        Write-Host "🎉 操作完成!" -ForegroundColor $Green
    }
    else {
        exit 1
    }
}

# 显示帮助信息
function Show-Help {
    Write-Host "阿里云ClickHouse集群部署脚本"
    Write-Host ""
    Write-Host "用法: .\setup_aliyun.ps1 [参数]"
    Write-Host ""
    Write-Host "参数:"
    Write-Host "  -AccessKeyPath  AccessKey文件路径 (默认: C:\Users\mingbo\aliyun\AccessKey.csv)"
    Write-Host "  -Region         阿里云地域 (默认: cn-beijing)"
    Write-Host "  -Action         操作类型 [plan|apply|destroy] (默认: plan)"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\setup_aliyun.ps1 -Action plan     # 查看执行计划"
    Write-Host "  .\setup_aliyun.ps1 -Action apply    # 创建基础设施"
    Write-Host "  .\setup_aliyun.ps1 -Action destroy  # 销毁基础设施"
}

# 脚本入口
if ($args -contains "-help" -or $args -contains "--help") {
    Show-Help
}
else {
    Main
} 