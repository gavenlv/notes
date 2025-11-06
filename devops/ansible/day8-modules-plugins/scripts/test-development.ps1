# Ansible 模块和插件开发测试脚本
# 用于测试第8天开发的自定义模块和插件

param(
    [string]$TestType = "all",  # all, modules, plugins, unit
    [switch]$Verbose,
    [switch]$Debug,
    [string]$PythonPath = "python3"
)

# 设置颜色输出
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$Cyan = [System.ConsoleColor]::Cyan

function Write-ColorOutput {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White
    )
    
    $currentColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = $currentColor
}

function Test-Prerequisites {
    Write-ColorOutput "=== 检查测试前置条件 ===" -Color $Blue
    
    # 检查Python
    try {
        $pythonVersion = & $PythonPath --version 2>&1
        Write-ColorOutput "✓ Python版本: $pythonVersion" -Color $Green
    } catch {
        Write-ColorOutput "✗ Python未找到或不可用" -Color $Red
        return $false
    }
    
    # 检查Ansible
    try {
        $ansibleVersion = ansible --version 2>&1 | Select-Object -First 1
        Write-ColorOutput "✓ Ansible版本: $ansibleVersion" -Color $Green
    } catch {
        Write-ColorOutput "✗ Ansible未找到或不可用" -Color $Red
        return $false
    }
    
    # 检查必要的Python包
    $requiredPackages = @("psutil", "jinja2")
    foreach ($package in $requiredPackages) {
        try {
            & $PythonPath -c "import $package; print('$package version:', $package.__version__)" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✓ Python包 $package 已安装" -Color $Green
            } else {
                Write-ColorOutput "⚠ Python包 $package 未安装，某些功能可能不可用" -Color $Yellow
            }
        } catch {
            Write-ColorOutput "⚠ 无法检查Python包 $package" -Color $Yellow
        }
    }
    
    return $true
}

function Test-ModuleSyntax {
    Write-ColorOutput "=== 检查模块语法 ===" -Color $Blue
    
    $moduleDir = "modules"
    $modules = Get-ChildItem -Path $moduleDir -Filter "*.py" -ErrorAction SilentlyContinue
    
    if (-not $modules) {
        Write-ColorOutput "✗ 未找到模块文件" -Color $Red
        return $false
    }
    
    $allValid = $true
    foreach ($module in $modules) {
        Write-ColorOutput "检查模块: $($module.Name)" -Color $Cyan
        
        try {
            & $PythonPath -m py_compile $module.FullName
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "  ✓ 语法检查通过" -Color $Green
            } else {
                Write-ColorOutput "  ✗ 语法检查失败" -Color $Red
                $allValid = $false
            }
        } catch {
            Write-ColorOutput "  ✗ 语法检查出错: $($_.Exception.Message)" -Color $Red
            $allValid = $false
        }
        
        # 检查模块文档
        try {
            $content = Get-Content $module.FullName -Raw
            if ($content -match "DOCUMENTATION\s*=") {
                Write-ColorOutput "  ✓ 包含文档字符串" -Color $Green
            } else {
                Write-ColorOutput "  ⚠ 缺少文档字符串" -Color $Yellow
            }
            
            if ($content -match "EXAMPLES\s*=") {
                Write-ColorOutput "  ✓ 包含示例" -Color $Green
            } else {
                Write-ColorOutput "  ⚠ 缺少示例" -Color $Yellow
            }
            
            if ($content -match "RETURN\s*=") {
                Write-ColorOutput "  ✓ 包含返回值文档" -Color $Green
            } else {
                Write-ColorOutput "  ⚠ 缺少返回值文档" -Color $Yellow
            }
        } catch {
            Write-ColorOutput "  ⚠ 无法检查文档完整性" -Color $Yellow
        }
    }
    
    return $allValid
}

function Test-PluginSyntax {
    Write-ColorOutput "=== 检查插件语法 ===" -Color $Blue
    
    $pluginDirs = @("plugins/filter_plugins", "plugins/lookup_plugins")
    $allValid = $true
    
    foreach ($pluginDir in $pluginDirs) {
        if (Test-Path $pluginDir) {
            Write-ColorOutput "检查插件目录: $pluginDir" -Color $Cyan
            
            $plugins = Get-ChildItem -Path $pluginDir -Filter "*.py" -ErrorAction SilentlyContinue
            foreach ($plugin in $plugins) {
                Write-ColorOutput "  检查插件: $($plugin.Name)" -Color $Cyan
                
                try {
                    & $PythonPath -m py_compile $plugin.FullName
                    if ($LASTEXITCODE -eq 0) {
                        Write-ColorOutput "    ✓ 语法检查通过" -Color $Green
                    } else {
                        Write-ColorOutput "    ✗ 语法检查失败" -Color $Red
                        $allValid = $false
                    }
                } catch {
                    Write-ColorOutput "    ✗ 语法检查出错: $($_.Exception.Message)" -Color $Red
                    $allValid = $false
                }
            }
        } else {
            Write-ColorOutput "插件目录不存在: $pluginDir" -Color $Yellow
        }
    }
    
    return $allValid
}

function Test-ModuleExecution {
    Write-ColorOutput "=== 测试模块执行 ===" -Color $Blue
    
    # 设置模块路径
    $env:ANSIBLE_LIBRARY = "$(Get-Location)/modules"
    
    # 设置插件路径
    $env:ANSIBLE_FILTER_PLUGINS = "$(Get-Location)/plugins/filter_plugins"
    $env:ANSIBLE_LOOKUP_PLUGINS = "$(Get-Location)/plugins/lookup_plugins"
    
    # 设置详细输出
    $verboseFlag = ""
    if ($Verbose) {
        $verboseFlag = "-v"
    }
    if ($Debug) {
        $verboseFlag = "-vvv"
    }
    
    # 运行模块测试
    Write-ColorOutput "运行模块测试 Playbook..." -Color $Cyan
    try {
        $result = ansible-playbook examples/test-modules.yml $verboseFlag --connection=local -i "localhost," 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 模块测试通过" -Color $Green
            if ($Verbose) {
                Write-Host $result
            }
        } else {
            Write-ColorOutput "✗ 模块测试失败" -Color $Red
            Write-Host $result
            return $false
        }
    } catch {
        Write-ColorOutput "✗ 模块测试执行出错: $($_.Exception.Message)" -Color $Red
        return $false
    }
    
    return $true
}

function Test-PluginExecution {
    Write-ColorOutput "=== 测试插件执行 ===" -Color $Blue
    
    # 设置插件路径
    $env:ANSIBLE_FILTER_PLUGINS = "$(Get-Location)/plugins/filter_plugins"
    $env:ANSIBLE_LOOKUP_PLUGINS = "$(Get-Location)/plugins/lookup_plugins"
    
    # 设置详细输出
    $verboseFlag = ""
    if ($Verbose) {
        $verboseFlag = "-v"
    }
    if ($Debug) {
        $verboseFlag = "-vvv"
    }
    
    # 运行插件测试
    Write-ColorOutput "运行插件测试 Playbook..." -Color $Cyan
    try {
        $result = ansible-playbook examples/test-plugins.yml $verboseFlag --connection=local -i "localhost," 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ 插件测试通过" -Color $Green
            if ($Verbose) {
                Write-Host $result
            }
        } else {
            Write-ColorOutput "✗ 插件测试失败" -Color $Red
            Write-Host $result
            return $false
        }
    } catch {
        Write-ColorOutput "✗ 插件测试执行出错: $($_.Exception.Message)" -Color $Red
        return $false
    }
    
    return $true
}

function Test-UnitTests {
    Write-ColorOutput "=== 运行单元测试 ===" -Color $Blue
    
    # 检查是否有单元测试文件
    if (Test-Path "tests") {
        $testFiles = Get-ChildItem -Path "tests" -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue
        
        if ($testFiles) {
            foreach ($testFile in $testFiles) {
                Write-ColorOutput "运行单元测试: $($testFile.Name)" -Color $Cyan
                
                try {
                    & $PythonPath -m pytest $testFile.FullName -v 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-ColorOutput "  ✓ 单元测试通过" -Color $Green
                    } else {
                        Write-ColorOutput "  ✗ 单元测试失败" -Color $Red
                    }
                } catch {
                    Write-ColorOutput "  ⚠ 无法运行单元测试 (pytest未安装?)" -Color $Yellow
                    # 尝试直接运行
                    try {
                        & $PythonPath $testFile.FullName
                        if ($LASTEXITCODE -eq 0) {
                            Write-ColorOutput "  ✓ 单元测试通过 (直接运行)" -Color $Green
                        } else {
                            Write-ColorOutput "  ✗ 单元测试失败 (直接运行)" -Color $Red
                        }
                    } catch {
                        Write-ColorOutput "  ✗ 单元测试执行出错: $($_.Exception.Message)" -Color $Red
                    }
                }
            }
        } else {
            Write-ColorOutput "未找到单元测试文件" -Color $Yellow
        }
    } else {
        Write-ColorOutput "未找到测试目录" -Color $Yellow
    }
}

function Show-TestSummary {
    param(
        [bool]$PrereqsOk,
        [bool]$ModuleSyntaxOk,
        [bool]$PluginSyntaxOk,
        [bool]$ModuleExecOk,
        [bool]$PluginExecOk
    )
    
    Write-ColorOutput "`n=== 测试总结 ===" -Color $Blue
    
    Write-ColorOutput "前置条件检查: $(if ($PrereqsOk) { '✓ 通过' } else { '✗ 失败' })" -Color $(if ($PrereqsOk) { $Green } else { $Red })
    Write-ColorOutput "模块语法检查: $(if ($ModuleSyntaxOk) { '✓ 通过' } else { '✗ 失败' })" -Color $(if ($ModuleSyntaxOk) { $Green } else { $Red })
    Write-ColorOutput "插件语法检查: $(if ($PluginSyntaxOk) { '✓ 通过' } else { '✗ 失败' })" -Color $(if ($PluginSyntaxOk) { $Green } else { $Red })
    Write-ColorOutput "模块执行测试: $(if ($ModuleExecOk) { '✓ 通过' } else { '✗ 失败' })" -Color $(if ($ModuleExecOk) { $Green } else { $Red })
    Write-ColorOutput "插件执行测试: $(if ($PluginExecOk) { '✓ 通过' } else { '✗ 失败' })" -Color $(if ($PluginExecOk) { $Green } else { $Red })
    
    $overallSuccess = $PrereqsOk -and $ModuleSyntaxOk -and $PluginSyntaxOk -and $ModuleExecOk -and $PluginExecOk
    Write-ColorOutput "`n总体结果: $(if ($overallSuccess) { '✓ 所有测试通过' } else { '✗ 存在失败的测试' })" -Color $(if ($overallSuccess) { $Green } else { $Red })
    
    if (-not $overallSuccess) {
        Write-ColorOutput "`n建议:" -Color $Yellow
        Write-ColorOutput "1. 检查错误信息并修复代码问题" -Color $Yellow
        Write-ColorOutput "2. 确保所有依赖包已正确安装" -Color $Yellow
        Write-ColorOutput "3. 验证Ansible环境配置" -Color $Yellow
        Write-ColorOutput "4. 使用 -Verbose 或 -Debug 参数获取更多信息" -Color $Yellow
    }
}

# 主执行流程
Write-ColorOutput "Ansible 模块和插件开发测试" -Color $Blue
Write-ColorOutput "测试类型: $TestType" -Color $Cyan
Write-ColorOutput "当前目录: $(Get-Location)" -Color $Cyan

# 切换到脚本目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

Write-ColorOutput "项目目录: $(Get-Location)" -Color $Cyan

# 初始化测试结果
$prereqsOk = $false
$moduleSyntaxOk = $false
$pluginSyntaxOk = $false
$moduleExecOk = $false
$pluginExecOk = $false

# 执行测试
try {
    # 检查前置条件
    $prereqsOk = Test-Prerequisites
    
    if ($prereqsOk) {
        # 根据测试类型执行相应测试
        switch ($TestType.ToLower()) {
            "all" {
                $moduleSyntaxOk = Test-ModuleSyntax
                $pluginSyntaxOk = Test-PluginSyntax
                if ($moduleSyntaxOk) {
                    $moduleExecOk = Test-ModuleExecution
                }
                if ($pluginSyntaxOk) {
                    $pluginExecOk = Test-PluginExecution
                }
                Test-UnitTests
            }
            "modules" {
                $moduleSyntaxOk = Test-ModuleSyntax
                if ($moduleSyntaxOk) {
                    $moduleExecOk = Test-ModuleExecution
                }
                $pluginSyntaxOk = $true  # 跳过插件测试
                $pluginExecOk = $true
            }
            "plugins" {
                $pluginSyntaxOk = Test-PluginSyntax
                if ($pluginSyntaxOk) {
                    $pluginExecOk = Test-PluginExecution
                }
                $moduleSyntaxOk = $true  # 跳过模块测试
                $moduleExecOk = $true
            }
            "unit" {
                Test-UnitTests
                $moduleSyntaxOk = $true
                $pluginSyntaxOk = $true
                $moduleExecOk = $true
                $pluginExecOk = $true
            }
            default {
                Write-ColorOutput "无效的测试类型: $TestType" -Color $Red
                Write-ColorOutput "支持的类型: all, modules, plugins, unit" -Color $Yellow
                exit 1
            }
        }
    } else {
        Write-ColorOutput "前置条件检查失败，跳过其他测试" -Color $Red
    }
    
    # 显示测试总结
    Show-TestSummary -PrereqsOk $prereqsOk -ModuleSyntaxOk $moduleSyntaxOk -PluginSyntaxOk $pluginSyntaxOk -ModuleExecOk $moduleExecOk -PluginExecOk $pluginExecOk
    
} catch {
    Write-ColorOutput "测试执行过程中出现错误: $($_.Exception.Message)" -Color $Red
    exit 1
}

Write-ColorOutput "`n测试完成!" -Color $Blue 