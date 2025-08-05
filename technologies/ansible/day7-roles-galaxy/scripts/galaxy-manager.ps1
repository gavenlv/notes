# Ansible Galaxy 管理脚本

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("search", "install", "list", "remove", "info", "create", "publish", "update", "backup")]
    [string]$Action = "list",
    
    [Parameter(Position=1)]
    [string]$RoleName = "",
    
    [Parameter()]
    [string]$RequirementsFile = "requirements.yml",
    
    [Parameter()]
    [string]$RolesPath = "./galaxy-roles",
    
    [Parameter()]
    [string]$Galaxy = "https://galaxy.ansible.com",
    
    [Parameter()]
    [switch]$Force,
    
    [Parameter()]
    [switch]$Check,
    
    [Parameter()]
    [int]$MaxResults = 10
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Cyan" = [ConsoleColor]::Cyan
        "Magenta" = [ConsoleColor]::Magenta
        "White" = [ConsoleColor]::White
        "Gray" = [ConsoleColor]::Gray
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

# 显示标题
function Show-Title {
    param([string]$Title)
    
    Write-ColorOutput "`n" + "="*50 -Color "Cyan"
    Write-ColorOutput " $Title" -Color "Cyan"
    Write-ColorOutput "="*50 + "`n" -Color "Cyan"
}

# 执行 Galaxy 命令
function Invoke-GalaxyCommand {
    param(
        [string]$Command,
        [string]$Description = "",
        [switch]$ShowOutput = $true
    )
    
    if ($Description) {
        Write-ColorOutput "执行: $Description" -Color "Yellow"
    }
    
    Write-ColorOutput "命令: $Command" -Color "Gray"
    
    if ($Check) {
        Write-ColorOutput "检查模式 - 显示将要执行的命令" -Color "Blue"
        return
    }
    
    try {
        $result = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($ShowOutput) {
                Write-ColorOutput $result -Color "White"
            }
            Write-ColorOutput "✓ 命令执行成功" -Color "Green"
            return $result
        } else {
            Write-ColorOutput "✗ 命令执行失败" -Color "Red"
            Write-ColorOutput $result -Color "Red"
            return $null
        }
    }
    catch {
        Write-ColorOutput "✗ 命令执行异常: $($_.Exception.Message)" -Color "Red"
        return $null
    }
}

# 搜索角色
function Search-Roles {
    param([string]$SearchTerm)
    
    Show-Title "搜索 Galaxy 角色"
    
    if (-not $SearchTerm) {
        $SearchTerm = Read-Host "请输入搜索关键词"
    }
    
    Write-ColorOutput "搜索关键词: $SearchTerm" -Color "Cyan"
    Write-ColorOutput "最大结果数: $MaxResults" -Color "Cyan"
    
    $command = "ansible-galaxy search `"$SearchTerm`" --max $MaxResults"
    $result = Invoke-GalaxyCommand $command "搜索角色"
    
    if ($result) {
        Write-ColorOutput "`n搜索完成，找到以下角色:" -Color "Green"
        
        # 解析搜索结果并格式化显示
        $lines = $result -split "`n"
        $roleCount = 0
        
        foreach ($line in $lines) {
            if ($line -match "^\s*(\S+)\s+(.+)$") {
                $roleCount++
                $roleName = $matches[1]
                $description = $matches[2].Trim()
                
                Write-ColorOutput "  $roleCount. $roleName" -Color "Yellow"
                Write-ColorOutput "     描述: $description" -Color "White"
            }
        }
        
        if ($roleCount -eq 0) {
            Write-ColorOutput "未找到匹配的角色" -Color "Red"
        }
    }
}

# 安装角色
function Install-Role {
    param([string]$Role)
    
    Show-Title "安装 Galaxy 角色"
    
    if (-not $Role) {
        if (Test-Path $RequirementsFile) {
            Write-ColorOutput "从 requirements.yml 安装角色" -Color "Cyan"
            $command = "ansible-galaxy install -r `"$RequirementsFile`" --roles-path `"$RolesPath`""
            if ($Force) {
                $command += " --force"
            }
            Invoke-GalaxyCommand $command "从需求文件安装角色"
        } else {
            Write-ColorOutput "未指定角色名称，且 $RequirementsFile 不存在" -Color "Red"
            return
        }
    } else {
        Write-ColorOutput "安装角色: $Role" -Color "Cyan"
        Write-ColorOutput "安装路径: $RolesPath" -Color "Cyan"
        
        $command = "ansible-galaxy install `"$Role`" --roles-path `"$RolesPath`""
        if ($Force) {
            $command += " --force"
            Write-ColorOutput "强制覆盖已存在的角色" -Color "Yellow"
        }
        
        Invoke-GalaxyCommand $command "安装角色"
    }
}

# 列出已安装角色
function List-Roles {
    Show-Title "已安装的角色"
    
    Write-ColorOutput "角色路径: $RolesPath" -Color "Cyan"
    
    $command = "ansible-galaxy list --roles-path `"$RolesPath`""
    $result = Invoke-GalaxyCommand $command "列出已安装角色"
    
    if ($result) {
        # 统计角色数量
        $lines = $result -split "`n"
        $roleCount = 0
        
        foreach ($line in $lines) {
            if ($line -match "^\s*-\s+(.+?),\s*(.+)$") {
                $roleCount++
            }
        }
        
        Write-ColorOutput "`n总计 $roleCount 个已安装角色" -Color "Green"
    }
}

# 获取角色信息
function Get-RoleInfo {
    param([string]$Role)
    
    Show-Title "角色详细信息"
    
    if (-not $Role) {
        $Role = Read-Host "请输入角色名称"
    }
    
    Write-ColorOutput "角色: $Role" -Color "Cyan"
    
    $command = "ansible-galaxy info `"$Role`""
    Invoke-GalaxyCommand $command "获取角色信息"
}

# 删除角色
function Remove-Role {
    param([string]$Role)
    
    Show-Title "删除角色"
    
    if (-not $Role) {
        $Role = Read-Host "请输入要删除的角色名称"
    }
    
    Write-ColorOutput "将要删除角色: $Role" -Color "Yellow"
    Write-ColorOutput "角色路径: $RolesPath" -Color "Cyan"
    
    if (-not $Check) {
        $confirm = Read-Host "确认删除此角色? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-ColorOutput "操作已取消" -Color "Yellow"
            return
        }
    }
    
    $command = "ansible-galaxy remove `"$Role`" --roles-path `"$RolesPath`""
    Invoke-GalaxyCommand $command "删除角色"
}

# 创建新角色
function New-Role {
    param([string]$Role)
    
    Show-Title "创建新角色"
    
    if (-not $Role) {
        $Role = Read-Host "请输入新角色名称"
    }
    
    Write-ColorOutput "创建角色: $Role" -Color "Cyan"
    Write-ColorOutput "创建路径: $RolesPath" -Color "Cyan"
    
    # 检查角色是否已存在
    $rolePath = Join-Path $RolesPath $Role
    if (Test-Path $rolePath -and -not $Force) {
        Write-ColorOutput "角色已存在: $rolePath" -Color "Red"
        Write-ColorOutput "使用 -Force 参数覆盖现有角色" -Color "Yellow"
        return
    }
    
    $command = "ansible-galaxy init `"$Role`" --init-path `"$RolesPath`""
    if ($Force -and (Test-Path $rolePath)) {
        Remove-Item $rolePath -Recurse -Force
        Write-ColorOutput "已删除现有角色目录" -Color "Yellow"
    }
    
    $result = Invoke-GalaxyCommand $command "创建角色骨架"
    
    if ($result) {
        Write-ColorOutput "`n角色创建成功，目录结构:" -Color "Green"
        if (Test-Path $rolePath) {
            Get-ChildItem $rolePath -Recurse | ForEach-Object {
                $relativePath = $_.FullName.Replace($rolePath, "").TrimStart("\")
                if ($_.PSIsContainer) {
                    Write-ColorOutput "  📁 $relativePath/" -Color "Blue"
                } else {
                    Write-ColorOutput "  📄 $relativePath" -Color "White"
                }
            }
        }
    }
}

# 更新角色
function Update-Roles {
    Show-Title "更新角色"
    
    Write-ColorOutput "检查角色更新..." -Color "Cyan"
    
    if (Test-Path $RequirementsFile) {
        Write-ColorOutput "从 $RequirementsFile 更新角色" -Color "Cyan"
        $command = "ansible-galaxy install -r `"$RequirementsFile`" --roles-path `"$RolesPath`" --force"
        Invoke-GalaxyCommand $command "更新所有角色"
    } else {
        Write-ColorOutput "未找到 $RequirementsFile 文件" -Color "Red"
        Write-ColorOutput "将尝试更新已安装的角色..." -Color "Yellow"
        
        # 获取已安装角色列表
        $listCommand = "ansible-galaxy list --roles-path `"$RolesPath`""
        $rolesList = Invoke-Expression $listCommand 2>$null
        
        if ($rolesList) {
            $lines = $rolesList -split "`n"
            foreach ($line in $lines) {
                if ($line -match "^\s*-\s+(.+?),\s*(.+)$") {
                    $roleName = $matches[1].Trim()
                    Write-ColorOutput "更新角色: $roleName" -Color "Yellow"
                    $updateCommand = "ansible-galaxy install `"$roleName`" --roles-path `"$RolesPath`" --force"
                    Invoke-GalaxyCommand $updateCommand "更新 $roleName" -ShowOutput $false
                }
            }
        }
    }
}

# 备份角色
function Backup-Roles {
    Show-Title "备份角色"
    
    $backupDir = "./roles-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    Write-ColorOutput "创建角色备份..." -Color "Cyan"
    Write-ColorOutput "源路径: $RolesPath" -Color "White"
    Write-ColorOutput "备份路径: $backupDir" -Color "White"
    
    if (Test-Path $RolesPath) {
        try {
            Copy-Item $RolesPath $backupDir -Recurse -Force
            Write-ColorOutput "✓ 角色备份完成" -Color "Green"
            
            # 创建备份信息文件
            $backupInfo = @{
                "backup_time" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                "source_path" = $RolesPath
                "backup_path" = $backupDir
                "roles_count" = (Get-ChildItem $RolesPath -Directory).Count
            }
            
            $backupInfo | ConvertTo-Json -Depth 2 | Out-File "$backupDir/backup-info.json" -Encoding UTF8
            
            Write-ColorOutput "备份信息已保存到: $backupDir/backup-info.json" -Color "Cyan"
        }
        catch {
            Write-ColorOutput "✗ 备份失败: $($_.Exception.Message)" -Color "Red"
        }
    } else {
        Write-ColorOutput "源路径不存在: $RolesPath" -Color "Red"
    }
}

# 生成 requirements.yml
function New-RequirementsFile {
    Show-Title "生成 requirements.yml"
    
    if (Test-Path $RolesPath) {
        $roles = Get-ChildItem $RolesPath -Directory
        
        if ($roles.Count -eq 0) {
            Write-ColorOutput "未找到已安装的角色" -Color "Red"
            return
        }
        
        Write-ColorOutput "找到 $($roles.Count) 个角色，生成需求文件..." -Color "Cyan"
        
        $requirements = @"
---
# Ansible Galaxy Requirements
# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

"@
        
        foreach ($role in $roles) {
            $requirements += @"

# Role: $($role.Name)
- name: $($role.Name)
  version: latest
"@
        }
        
        $requirements | Out-File $RequirementsFile -Encoding UTF8
        Write-ColorOutput "✓ Requirements 文件已生成: $RequirementsFile" -Color "Green"
        
        # 显示文件内容
        Write-ColorOutput "`n文件内容预览:" -Color "Cyan"
        Get-Content $RequirementsFile | ForEach-Object {
            Write-ColorOutput "  $_" -Color "White"
        }
    } else {
        Write-ColorOutput "角色目录不存在: $RolesPath" -Color "Red"
    }
}

# 显示帮助信息
function Show-Help {
    Show-Title "Galaxy 管理器帮助"
    
    Write-ColorOutput "可用操作:" -Color "Cyan"
    Write-ColorOutput "  search    - 搜索角色" -Color "White"
    Write-ColorOutput "  install   - 安装角色" -Color "White"
    Write-ColorOutput "  list      - 列出已安装角色" -Color "White"
    Write-ColorOutput "  info      - 显示角色信息" -Color "White"
    Write-ColorOutput "  remove    - 删除角色" -Color "White"
    Write-ColorOutput "  create    - 创建新角色" -Color "White"
    Write-ColorOutput "  update    - 更新角色" -Color "White"
    Write-ColorOutput "  backup    - 备份角色" -Color "White"
    
    Write-ColorOutput "`n参数选项:" -Color "Cyan"
    Write-ColorOutput "  -RoleName         : 角色名称" -Color "White"
    Write-ColorOutput "  -RequirementsFile : 需求文件路径 (默认: requirements.yml)" -Color "White"
    Write-ColorOutput "  -RolesPath        : 角色安装路径 (默认: ./galaxy-roles)" -Color "White"
    Write-ColorOutput "  -Force            : 强制执行操作" -Color "White"
    Write-ColorOutput "  -Check            : 检查模式，不执行实际操作" -Color "White"
    Write-ColorOutput "  -MaxResults       : 搜索结果最大数量 (默认: 10)" -Color "White"
    
    Write-ColorOutput "`n使用示例:" -Color "Cyan"
    Write-ColorOutput "  .\galaxy-manager.ps1 search nginx" -Color "Gray"
    Write-ColorOutput "  .\galaxy-manager.ps1 install geerlingguy.nginx" -Color "Gray"
    Write-ColorOutput "  .\galaxy-manager.ps1 create my-custom-role -Force" -Color "Gray"
    Write-ColorOutput "  .\galaxy-manager.ps1 list" -Color "Gray"
}

# 主函数
function Main {
    try {
        Write-ColorOutput "Ansible Galaxy 管理器" -Color "Cyan"
        Write-ColorOutput "执行时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Color "Gray"
        
        # 确保角色目录存在
        if (-not (Test-Path $RolesPath)) {
            New-Item -ItemType Directory -Path $RolesPath -Force | Out-Null
            Write-ColorOutput "已创建角色目录: $RolesPath" -Color "Yellow"
        }
        
        switch ($Action) {
            "search" {
                Search-Roles $RoleName
            }
            "install" {
                Install-Role $RoleName
            }
            "list" {
                List-Roles
            }
            "info" {
                Get-RoleInfo $RoleName
            }
            "remove" {
                Remove-Role $RoleName
            }
            "create" {
                New-Role $RoleName
            }
            "update" {
                Update-Roles
            }
            "backup" {
                Backup-Roles
            }
            default {
                Show-Help
            }
        }
        
        Write-ColorOutput "`n操作完成!" -Color "Green"
        
    }
    catch {
        Write-ColorOutput "执行出错: $($_.Exception.Message)" -Color "Red"
        exit 1
    }
}

# 运行主函数
Main 