# Ansible Inventory 测试脚本 (PowerShell)
# 用于测试各种 inventory 功能和验证配置

param(
    [string]$InventoryFile = "../configs/inventory-advanced.yml",
    [switch]$Verbose = $false
)

Write-Host "=== Ansible Inventory 测试脚本 ===" -ForegroundColor Green
Write-Host ""

# 检查 ansible-inventory 命令是否可用
Write-Host "1. 检查 ansible-inventory 命令..." -ForegroundColor Cyan
try {
    $version = ansible-inventory --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ ansible-inventory 可用" -ForegroundColor Green
        if ($Verbose) {
            Write-Host $version -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ ansible-inventory 不可用" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ ansible-inventory 命令不存在" -ForegroundColor Red
    exit 1
}

# 检查 inventory 文件是否存在
Write-Host "2. 检查 inventory 文件..." -ForegroundColor Cyan
if (Test-Path $InventoryFile) {
    Write-Host "✓ 找到 inventory 文件: $InventoryFile" -ForegroundColor Green
} else {
    Write-Host "✗ inventory 文件不存在: $InventoryFile" -ForegroundColor Red
    exit 1
}

# 验证 inventory 语法
Write-Host "3. 验证 inventory 语法..." -ForegroundColor Cyan
try {
    $syntaxCheck = ansible-inventory -i $InventoryFile --list 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ inventory 语法正确" -ForegroundColor Green
    } else {
        Write-Host "✗ inventory 语法错误" -ForegroundColor Red
        Write-Host $syntaxCheck -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 语法检查失败" -ForegroundColor Red
    exit 1
}

# 列出所有主机
Write-Host "4. 列出所有主机..." -ForegroundColor Cyan
try {
    $hosts = ansible-inventory -i $InventoryFile --list-hosts all 2>&1
    if ($LASTEXITCODE -eq 0) {
        $hostCount = ($hosts | Measure-Object -Line).Lines - 1  # 减去标题行
        Write-Host "✓ 找到 $hostCount 个主机" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "主机列表:" -ForegroundColor White
            $hosts | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        }
    } else {
        Write-Host "✗ 获取主机列表失败" -ForegroundColor Red
        Write-Host $hosts -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 列出主机时出错" -ForegroundColor Red
}

# 显示组结构
Write-Host "5. 显示组结构..." -ForegroundColor Cyan
try {
    $graph = ansible-inventory -i $InventoryFile --graph 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 组结构获取成功" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "组结构:" -ForegroundColor White
            $graph | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        }
    } else {
        Write-Host "✗ 获取组结构失败" -ForegroundColor Red
        Write-Host $graph -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 显示组结构时出错" -ForegroundColor Red
}

# 测试特定组
$testGroups = @("webservers", "databases", "production", "development")
Write-Host "6. 测试特定组..." -ForegroundColor Cyan
foreach ($group in $testGroups) {
    try {
        $groupHosts = ansible-inventory -i $InventoryFile --list-hosts $group 2>&1
        if ($LASTEXITCODE -eq 0) {
            $count = ($groupHosts | Measure-Object -Line).Lines - 1
            Write-Host "  ✓ $group 组: $count 个主机" -ForegroundColor Green
        } else {
            Write-Host "  ! $group 组: 不存在或为空" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ✗ $group 组: 查询失败" -ForegroundColor Red
    }
}

# 导出 JSON 格式
Write-Host "7. 导出 JSON 格式..." -ForegroundColor Cyan
try {
    $outputFile = "inventory-export-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $jsonOutput = ansible-inventory -i $InventoryFile --list --output $outputFile 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ JSON 导出成功: $outputFile" -ForegroundColor Green
    } else {
        # 尝试不使用 --output 参数
        $jsonData = ansible-inventory -i $InventoryFile --list 2>&1
        if ($LASTEXITCODE -eq 0) {
            $jsonData | Out-File -FilePath $outputFile -Encoding UTF8
            Write-Host "✓ JSON 导出成功: $outputFile" -ForegroundColor Green
        } else {
            Write-Host "✗ JSON 导出失败" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "✗ 导出 JSON 时出错" -ForegroundColor Red
}

# 测试主机模式
Write-Host "8. 测试主机模式..." -ForegroundColor Cyan
$patterns = @(
    "all",
    "webservers",
    "webservers:databases",
    "production:&webservers",
    "all:!development"
)

foreach ($pattern in $patterns) {
    try {
        $patternHosts = ansible-inventory -i $InventoryFile --list-hosts $pattern 2>&1
        if ($LASTEXITCODE -eq 0) {
            $count = ($patternHosts | Measure-Object -Line).Lines - 1
            Write-Host "  ✓ '$pattern': $count 个主机" -ForegroundColor Green
        } else {
            Write-Host "  ✗ '$pattern': 模式无效" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ '$pattern': 查询失败" -ForegroundColor Red
    }
}

# 测试动态 inventory (如果存在)
Write-Host "9. 测试动态 inventory..." -ForegroundColor Cyan
$dynamicScript = "./dynamic-inventory.py"
if (Test-Path $dynamicScript) {
    try {
        $dynamicOutput = python $dynamicScript --list 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 动态 inventory 脚本运行成功" -ForegroundColor Green
            if ($Verbose) {
                Write-Host "动态 inventory 输出 (前10行):" -ForegroundColor White
                ($dynamicOutput -split "`n")[0..9] | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
            }
        } else {
            Write-Host "✗ 动态 inventory 脚本运行失败" -ForegroundColor Red
            Write-Host $dynamicOutput -ForegroundColor Red
        }
    } catch {
        Write-Host "! 动态 inventory 脚本无法执行 (可能缺少 Python)" -ForegroundColor Yellow
    }
} else {
    Write-Host "! 动态 inventory 脚本不存在: $dynamicScript" -ForegroundColor Yellow
}

# 生成测试报告
Write-Host ""
Write-Host "=== 测试完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "建议下一步:" -ForegroundColor Cyan
Write-Host "1. 检查所有测试结果，修复任何错误" -ForegroundColor White
Write-Host "2. 尝试编辑 inventory 文件，添加自己的主机" -ForegroundColor White  
Write-Host "3. 测试更复杂的主机模式" -ForegroundColor White
Write-Host "4. 开始学习 Day 4 - Playbooks 基础" -ForegroundColor White
Write-Host ""

# 输出总结信息
$summary = @"
Ansible Inventory 测试总结
测试时间: $(Get-Date)
Inventory 文件: $InventoryFile
测试结果: 查看上方详细输出
"@

$logFile = "inventory-test-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$summary | Out-File -FilePath $logFile -Encoding UTF8
Write-Host "测试日志已保存到: $logFile" -ForegroundColor Gray 