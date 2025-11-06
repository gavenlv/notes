# Day 6 循环演示脚本
Write-Host "======================================" -ForegroundColor Green
Write-Host "Day 6: 高级循环演示" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# 设置脚本路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$playbookPath = Join-Path $scriptPath "..\playbooks\02-advanced-loops.yml"

Write-Host "`n=== 循环演示说明 ===" -ForegroundColor Cyan
Write-Host "本演示将展示以下循环技术：" -ForegroundColor White
Write-Host "• 基础循环 (简单列表、字典、范围)" -ForegroundColor White
Write-Host "• 嵌套循环 (subelements, product)" -ForegroundColor White  
Write-Host "• 条件循环 (when + loop)" -ForegroundColor White
Write-Host "• 循环变量和索引控制" -ForegroundColor White
Write-Host "• 高级过滤和选择" -ForegroundColor White
Write-Host "• 动态循环构建" -ForegroundColor White
Write-Host "• 批量操作模拟" -ForegroundColor White
Write-Host "• 错误处理和恢复" -ForegroundColor White
Write-Host "• 性能优化技术" -ForegroundColor White
Write-Host "• 综合应用示例" -ForegroundColor White

Write-Host "`n=== 开始执行循环演示 ===" -ForegroundColor Yellow
ansible-playbook $playbookPath -v

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "循环演示完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# 显示学习要点总结
Write-Host "`n📚 循环技术学习要点：" -ForegroundColor Cyan
Write-Host "✓ loop - 基础循环，替代 with_items" -ForegroundColor White
Write-Host "✓ subelements - 嵌套列表循环" -ForegroundColor White  
Write-Host "✓ product - 笛卡尔积循环" -ForegroundColor White
Write-Host "✓ selectattr/rejectattr - 条件过滤" -ForegroundColor White
Write-Host "✓ groupby - 分组操作" -ForegroundColor White
Write-Host "✓ loop_control - 循环控制参数" -ForegroundColor White
Write-Host "✓ ansible_loop - 循环变量信息" -ForegroundColor White
Write-Host "✓ batch - 批量处理优化" -ForegroundColor White
Write-Host "✓ register - 循环结果收集" -ForegroundColor White
Write-Host "✓ 动态数据结构构建" -ForegroundColor White

Write-Host "`n🔧 性能优化建议：" -ForegroundColor Magenta
Write-Host "• 避免深度嵌套循环 (>3层)" -ForegroundColor White
Write-Host "• 使用过滤器减少循环次数" -ForegroundColor White
Write-Host "• 优先使用模块的批量功能" -ForegroundColor White
Write-Host "• 合理使用 async 和 poll" -ForegroundColor White
Write-Host "• 利用 loop_control 优化显示" -ForegroundColor White 