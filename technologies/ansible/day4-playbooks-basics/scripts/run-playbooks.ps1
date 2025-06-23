# Day 4 Playbooks 运行脚本
param(
    [string]$Target = "localhost",
    [string]$PlaybookName = "",
    [switch]$DryRun = $false,
    [switch]$Verbose = $false
)

Write-Host "=== Day 4: Ansible Playbooks 实践运行脚本 ===" -ForegroundColor Green

# 脚本目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PlaybooksDir = Join-Path $ScriptDir "..\playbooks"
$ConfigsDir = Join-Path $ScriptDir "..\..\day1-installation\configs"

# 检查 Ansible 是否已安装
Write-Host "`n🔍 检查 Ansible 安装状态..." -ForegroundColor Cyan
try {
    $ansibleVersion = ansible --version | Select-Object -First 1
    Write-Host "✅ Ansible 已安装: $ansibleVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Ansible 未安装或未在 PATH 中"
    Write-Host "请先安装 Ansible:" -ForegroundColor Yellow
    Write-Host "pip install ansible" -ForegroundColor Yellow
    exit 1
}

# 可用的 playbooks
$Playbooks = @{
    "1" = @{
        "Name" = "01-system-info.yml"
        "Description" = "系统信息收集"
        "Requirements" = "无特殊要求"
    }
    "2" = @{
        "Name" = "02-web-server-setup.yml"
        "Description" = "Web服务器配置 (Nginx)"
        "Requirements" = "需要 sudo 权限，建议在测试环境运行"
    }
    "3" = @{
        "Name" = "03-user-management.yml"
        "Description" = "用户和权限管理"
        "Requirements" = "需要 sudo 权限"
    }
}

# 显示可用选项
function Show-PlaybookMenu {
    Write-Host "`n📋 可用的 Playbooks:" -ForegroundColor Cyan
    foreach ($key in $Playbooks.Keys | Sort-Object) {
        $playbook = $Playbooks[$key]
        Write-Host "  $key. $($playbook.Name)" -ForegroundColor White
        Write-Host "     📝 $($playbook.Description)" -ForegroundColor Gray
        Write-Host "     ⚠️  $($playbook.Requirements)" -ForegroundColor Yellow
        Write-Host ""
    }
    Write-Host "  a. 运行所有 playbooks" -ForegroundColor Magenta
    Write-Host "  q. 退出" -ForegroundColor Red
}

# 检查 inventory 文件
function Test-InventoryFile {
    $inventoryPath = Join-Path $ConfigsDir "inventory.ini"
    if (Test-Path $inventoryPath) {
        Write-Host "✅ 找到 inventory 文件: $inventoryPath" -ForegroundColor Green
        return $inventoryPath
    } else {
        Write-Host "⚠️  未找到 inventory 文件，创建临时的..." -ForegroundColor Yellow
        $tempInventory = Join-Path $env:TEMP "ansible_inventory_temp.ini"
        @"
[local]
localhost ansible_connection=local

[web_servers]
localhost ansible_connection=local

[db_servers]
localhost ansible_connection=local

[app_servers]
localhost ansible_connection=local
"@ | Out-File -FilePath $tempInventory -Encoding UTF8
        return $tempInventory
    }
}

# 运行 playbook
function Invoke-AnsiblePlaybook {
    param(
        [string]$PlaybookPath,
        [string]$InventoryPath,
        [bool]$CheckMode = $false,
        [bool]$VerboseMode = $false
    )
    
    $playbookName = Split-Path -Leaf $PlaybookPath
    Write-Host "`n🚀 运行 Playbook: $playbookName" -ForegroundColor Green
    
    $ansibleArgs = @(
        "-i", $InventoryPath,
        $PlaybookPath
    )
    
    if ($CheckMode) {
        $ansibleArgs += "--check"
        Write-Host "   (Dry Run 模式 - 不会实际执行)" -ForegroundColor Yellow
    }
    
    if ($VerboseMode) {
        $ansibleArgs += "-v"
    }
    
    try {
        Write-Host "执行命令: ansible-playbook $($ansibleArgs -join ' ')" -ForegroundColor Gray
        Write-Host "按 Enter 继续，或 Ctrl+C 取消..." -ForegroundColor Yellow
        Read-Host
        
        & ansible-playbook @ansibleArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $playbookName 执行成功!" -ForegroundColor Green
        } else {
            Write-Host "❌ $playbookName 执行失败 (退出码: $LASTEXITCODE)" -ForegroundColor Red
        }
    } catch {
        Write-Error "执行 playbook 时出错: $_"
    }
    
    Write-Host "`n" + "="*60 + "`n"
}

# 主执行逻辑
function Main {
    $inventoryPath = Test-InventoryFile
    
    if ($PlaybookName) {
        # 直接运行指定的 playbook
        $playbookPath = Join-Path $PlaybooksDir $PlaybookName
        if (Test-Path $playbookPath) {
            Invoke-AnsiblePlaybook -PlaybookPath $playbookPath -InventoryPath $inventoryPath -CheckMode $DryRun -VerboseMode $Verbose
        } else {
            Write-Error "Playbook 文件不存在: $playbookPath"
        }
        return
    }
    
    # 交互式菜单
    do {
        Show-PlaybookMenu
        $choice = Read-Host "`n请选择要运行的 playbook (1-3, a, q)"
        
        switch ($choice.ToLower()) {
            "q" { 
                Write-Host "退出脚本" -ForegroundColor Yellow
                return 
            }
            "a" {
                Write-Host "`n🔄 运行所有 playbooks..." -ForegroundColor Magenta
                foreach ($key in $Playbooks.Keys | Sort-Object) {
                    $playbookFile = $Playbooks[$key].Name
                    $playbookPath = Join-Path $PlaybooksDir $playbookFile
                    if (Test-Path $playbookPath) {
                        Invoke-AnsiblePlaybook -PlaybookPath $playbookPath -InventoryPath $inventoryPath -CheckMode $DryRun -VerboseMode $Verbose
                    }
                }
            }
            default {
                if ($Playbooks.ContainsKey($choice)) {
                    $playbookFile = $Playbooks[$choice].Name
                    $playbookPath = Join-Path $PlaybooksDir $playbookFile
                    if (Test-Path $playbookPath) {
                        Invoke-AnsiblePlaybook -PlaybookPath $playbookPath -InventoryPath $inventoryPath -CheckMode $DryRun -VerboseMode $Verbose
                    } else {
                        Write-Host "❌ Playbook 文件不存在: $playbookPath" -ForegroundColor Red
                    }
                } else {
                    Write-Host "❌ 无效选择: $choice" -ForegroundColor Red
                }
            }
        }
        
        if ($choice -ne "q") {
            Write-Host "按 Enter 返回菜单..." -ForegroundColor Gray
            Read-Host
        }
        
    } while ($choice.ToLower() -ne "q")
}

# 显示使用说明
Write-Host "`n📖 使用说明:" -ForegroundColor Cyan
Write-Host "  直接运行: .\run-playbooks.ps1" -ForegroundColor White
Write-Host "  指定文件: .\run-playbooks.ps1 -PlaybookName '01-system-info.yml'" -ForegroundColor White
Write-Host "  Dry Run:  .\run-playbooks.ps1 -DryRun" -ForegroundColor White
Write-Host "  详细输出: .\run-playbooks.ps1 -Verbose" -ForegroundColor White

# 安全提醒
Write-Host "`n⚠️  重要提醒:" -ForegroundColor Yellow
Write-Host "  - Web服务器和用户管理 playbooks 需要 sudo 权限" -ForegroundColor Yellow
Write-Host "  - 建议先在测试环境中运行" -ForegroundColor Yellow
Write-Host "  - 使用 -DryRun 参数可以预览将要执行的操作" -ForegroundColor Yellow

# 执行主函数
Main 