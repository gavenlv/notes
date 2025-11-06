# Day 6 综合演示脚本 - 条件判断与循环高级应用
param(
    [string]$Demo = "all",  # all, conditionals, loops, errors
    [switch]$ShowProgress,
    [switch]$PauseAfterEach
)

# 颜色定义
$Colors = @{
    Title = "Green"
    Section = "Yellow"
    Info = "Cyan"
    Success = "Green"
    Warning = "Magenta"
    Error = "Red"
    Gray = "Gray"
}

function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Show-Banner {
    param([string]$Title)
    Write-ColorText "==========================================" $Colors.Title
    Write-ColorText "  $Title" $Colors.Title
    Write-ColorText "==========================================" $Colors.Title
}

function Show-Progress {
    param([int]$Current, [int]$Total, [string]$Activity)
    if ($ShowProgress) {
        $percent = [math]::Round(($Current / $Total) * 100)
        Write-Progress -Activity $Activity -Status "$Current of $Total completed" -PercentComplete $percent
    }
}

function Wait-ForUser {
    if ($PauseAfterEach) {
        Write-ColorText "`n按任意键继续..." $Colors.Info
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# 设置脚本路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 显示欢迎信息
Show-Banner "Day 6: 条件判断与循环高级应用 - 综合演示"

Write-ColorText "`n📚 学习目标概览：" $Colors.Info
Write-ColorText "• 掌握复杂条件逻辑的构建和应用" -ForegroundColor White
Write-ColorText "• 精通多种循环类型的高级用法" -ForegroundColor White
Write-ColorText "• 学会条件与循环的组合使用技巧" -ForegroundColor White
Write-ColorText "• 理解错误处理和异常管理机制" -ForegroundColor White
Write-ColorText "• 实现动态任务执行策略" -ForegroundColor White
Write-ColorText "• 应用企业级场景的实际案例" -ForegroundColor White

# 演示配置
$demos = @(
    @{
        Name = "conditionals"
        Title = "高级条件判断演示"
        Script = "run-conditionals-demo.ps1"
        Description = "展示各种条件判断技术和逻辑控制"
        EstimatedTime = "5-8分钟"
    },
    @{
        Name = "loops"
        Title = "高级循环技术演示"
        Script = "run-loops-demo.ps1"
        Description = "演示复杂循环、嵌套循环和批量操作"
        EstimatedTime = "8-12分钟"
    },
    @{
        Name = "errors"
        Title = "错误处理和流程控制演示"
        Script = "run-error-handling-demo.ps1"
        Description = "展示错误处理、重试机制和流程控制"
        EstimatedTime = "10-15分钟"
    }
)

# 根据参数决定运行哪些演示
$demosToRun = switch ($Demo) {
    "conditionals" { $demos | Where-Object { $_.Name -eq "conditionals" } }
    "loops" { $demos | Where-Object { $_.Name -eq "loops" } }
    "errors" { $demos | Where-Object { $_.Name -eq "errors" } }
    default { $demos }
}

Write-ColorText "`n🎯 将要运行的演示：" $Colors.Section
foreach ($demo in $demosToRun) {
    Write-ColorText "✓ $($demo.Title)" -ForegroundColor White
    Write-ColorText "  📝 $($demo.Description)" $Colors.Gray
    Write-ColorText "  ⏱️ 预计时间: $($demo.EstimatedTime)" $Colors.Gray
}

$totalTime = switch ($demosToRun.Count) {
    1 { "5-15分钟" }
    2 { "15-25分钟" }
    3 { "25-35分钟" }
    default { "未知" }
}

Write-ColorText "`n⏱️ 总预计时间: $totalTime" $Colors.Warning

# 确认是否继续
Write-ColorText "`n继续执行演示吗? (y/N): " $Colors.Info -NoNewline
$response = Read-Host
if ($response -notmatch "^[yY]") {
    Write-ColorText "演示取消。" $Colors.Warning
    exit 0
}

# 记录开始时间
$startTime = Get-Date

# 执行演示
$currentDemo = 0
foreach ($demo in $demosToRun) {
    $currentDemo++
    Show-Progress $currentDemo $demosToRun.Count "执行 Day 6 演示"
    
    Write-ColorText "`n" 
    Show-Banner "演示 $currentDemo/$($demosToRun.Count): $($demo.Title)"
    
    Write-ColorText "📄 演示说明: $($demo.Description)" $Colors.Info
    Write-ColorText "⏱️ 预计时间: $($demo.EstimatedTime)" $Colors.Info
    Write-ColorText "🚀 开始执行..." $Colors.Success
    
    $demoStartTime = Get-Date
    
    try {
        # 执行演示脚本
        $scriptFullPath = Join-Path $scriptPath $demo.Script
        if (Test-Path $scriptFullPath) {
            & $scriptFullPath
            $demoEndTime = Get-Date
            $demoElapsed = $demoEndTime - $demoStartTime
            
            Write-ColorText "`n✅ 演示 '$($demo.Title)' 完成！" $Colors.Success
            Write-ColorText "   实际耗时: $($demoElapsed.Minutes)分$($demoElapsed.Seconds)秒" $Colors.Gray
        } else {
            Write-ColorText "❌ 演示脚本未找到: $scriptFullPath" $Colors.Error
        }
    } catch {
        Write-ColorText "❌ 演示执行出错: $_" $Colors.Error
    }
    
    Wait-ForUser
}

# 显示完成信息
$endTime = Get-Date
$totalElapsed = $endTime - $startTime

Write-ColorText "`n"
Show-Banner "所有演示完成！"

Write-ColorText "📊 执行统计：" $Colors.Info
Write-ColorText "• 执行演示数量: $($demosToRun.Count)" -ForegroundColor White
Write-ColorText "• 开始时间: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
Write-ColorText "• 结束时间: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
Write-ColorText "• 总耗时: $($totalElapsed.Minutes)分$($totalElapsed.Seconds)秒" -ForegroundColor White

Write-ColorText "`n🎓 Day 6 学习成果总结：" $Colors.Success
Write-ColorText "✅ 掌握了高级条件判断技术" -ForegroundColor White
Write-ColorText "✅ 精通了各种循环控制方法" -ForegroundColor White
Write-ColorText "✅ 学会了错误处理和流程控制" -ForegroundColor White
Write-ColorText "✅ 理解了性能优化最佳实践" -ForegroundColor White
Write-ColorText "✅ 具备了企业级应用开发能力" -ForegroundColor White

Write-ColorText "`n🚀 下一步学习建议：" $Colors.Info
Write-ColorText "• Day 7: 角色与 Galaxy 高级应用" -ForegroundColor White
Write-ColorText "• 深入学习 Ansible 角色设计模式" -ForegroundColor White  
Write-ColorText "• 探索 Ansible Galaxy 社区资源" -ForegroundColor White
Write-ColorText "• 实践企业级角色库构建" -ForegroundColor White

Write-ColorText "`n💡 实用技巧提醒：" $Colors.Warning
Write-ColorText "• 保存重要的条件判断模式作为模板" -ForegroundColor White
Write-ColorText "• 建立循环性能优化的检查清单" -ForegroundColor White
Write-ColorText "• 为不同环境设计错误处理策略" -ForegroundColor White
Write-ColorText "• 定期回顾和重构复杂的逻辑代码" -ForegroundColor White

# 可选的文档生成
Write-ColorText "`n📄 是否生成学习报告? (y/N): " $Colors.Info -NoNewline
$generateReport = Read-Host
if ($generateReport -match "^[yY]") {
    $reportPath = Join-Path $scriptPath "..\Day6-学习报告-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    
    $reportContent = @"
# Day 6 学习报告 - 条件判断与循环高级应用

## 执行信息
- **执行时间**: $($startTime.ToString('yyyy-MM-dd HH:mm:ss')) - $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))
- **总耗时**: $($totalElapsed.Minutes)分$($totalElapsed.Seconds)秒
- **演示数量**: $($demosToRun.Count)

## 完成的演示

$($demosToRun | ForEach-Object { "### $($_.Title)`n$($_.Description)`n" })

## 学习成果
- ✅ 掌握了高级条件判断技术
- ✅ 精通了各种循环控制方法  
- ✅ 学会了错误处理和流程控制
- ✅ 理解了性能优化最佳实践
- ✅ 具备了企业级应用开发能力

## 下一步学习
- Day 7: 角色与 Galaxy 高级应用
- 深入学习 Ansible 角色设计模式
- 探索 Ansible Galaxy 社区资源
- 实践企业级角色库构建

---
*报告生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*
"@

    try {
        $reportContent | Out-File -FilePath $reportPath -Encoding UTF8
        Write-ColorText "📄 学习报告已生成: $reportPath" $Colors.Success
    } catch {
        Write-ColorText "❌ 报告生成失败: $_" $Colors.Error
    }
}

Write-ColorText "`n感谢使用 Ansible Day 6 学习系统！" $Colors.Success 