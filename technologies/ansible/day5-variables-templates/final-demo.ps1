# Day 5 变量与模板演示脚本 - 最终版本

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Day 5: 变量与模板高级应用 - 演示完成" -ForegroundColor Yellow  
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "🎯 学习目标已达成:" -ForegroundColor Green
Write-Host "✓ 掌握 Ansible 变量系统的高级用法" -ForegroundColor White
Write-Host "✓ 学会 Jinja2 模板引擎的强大功能" -ForegroundColor White  
Write-Host "✓ 理解复杂配置文件的动态生成" -ForegroundColor White
Write-Host "✓ 体验企业级变量管理最佳实践" -ForegroundColor White
Write-Host ""

Write-Host "📁 已创建的文件结构:" -ForegroundColor Cyan
Write-Host "day5-variables-templates/" -ForegroundColor White
Write-Host "├── variables-templates.md (主要学习文档)" -ForegroundColor Gray
Write-Host "├── playbooks/" -ForegroundColor White  
Write-Host "│   ├── 01-variables-demo.yml" -ForegroundColor Gray
Write-Host "│   └── 02-advanced-templates.yml" -ForegroundColor Gray
Write-Host "├── templates/ (10个模板文件)" -ForegroundColor White
Write-Host "│   ├── variable-report.md.j2" -ForegroundColor Gray
Write-Host "│   ├── advanced-nginx.conf.j2" -ForegroundColor Gray
Write-Host "│   ├── user-management.sh.j2" -ForegroundColor Gray
Write-Host "│   ├── app-config.yml.j2" -ForegroundColor Gray
Write-Host "│   ├── monitoring-config.json.j2" -ForegroundColor Gray
Write-Host "│   ├── docker-compose.yml.j2" -ForegroundColor Gray
Write-Host "│   ├── database-init.sql.j2" -ForegroundColor Gray
Write-Host "│   ├── deploy-script.sh.j2" -ForegroundColor Gray
Write-Host "│   ├── generated-vars.yml.j2" -ForegroundColor Gray
Write-Host "│   └── conditional-config.j2" -ForegroundColor Gray
Write-Host "└── examples/README.md" -ForegroundColor White
Write-Host ""

Write-Host "🔧 核心技术要点:" -ForegroundColor Yellow
Write-Host "• 变量优先级和作用域管理" -ForegroundColor White
Write-Host "• Jinja2 模板语法和过滤器" -ForegroundColor White
Write-Host "• 条件判断和循环控制" -ForegroundColor White
Write-Host "• 复杂数据结构处理" -ForegroundColor White
Write-Host "• 环境特定配置生成" -ForegroundColor White
Write-Host ""

Write-Host "💼 实际应用场景:" -ForegroundColor Magenta
Write-Host "• 多环境配置管理 (开发/测试/生产)" -ForegroundColor White
Write-Host "• 动态服务器配置生成" -ForegroundColor White
Write-Host "• 用户和权限批量管理" -ForegroundColor White
Write-Host "• 监控和告警配置自动化" -ForegroundColor White
Write-Host "• 容器化部署配置生成" -ForegroundColor White
Write-Host "• 数据库初始化和迁移" -ForegroundColor White
Write-Host ""

# 生成简单的报告文件
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = "$env:TEMP\day5_completion_report_$timestamp.txt"

$report = "Ansible Day 5 学习完成报告`n" +
"===========================`n`n" +
"完成时间: $(Get-Date)`n" +
"主机: $env:COMPUTERNAME`n" +
"用户: $env:USERNAME`n`n" +
"学习内容: 变量与模板高级应用`n`n" +
"文件统计:`n" +
"主要文档: 1个`n" +
"Playbook: 2个`n" +
"模板文件: 10个`n" +
"示例文档: 1个`n" +
"演示脚本: 3个`n`n" +
"技能掌握:`n" +
"Ansible变量系统高级用法`n" +
"Jinja2模板引擎功能`n" +
"复杂配置文件动态生成`n" +
"企业级变量管理实践`n`n" +
"下一步: Day 6 条件判断与循环高级应用"

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "📊 统计信息:" -ForegroundColor Cyan
Write-Host "文档文件: 1个" -ForegroundColor White
Write-Host "Playbook: 2个" -ForegroundColor White
Write-Host "模板文件: 10个" -ForegroundColor White
Write-Host "演示脚本: 3个" -ForegroundColor White
Write-Host ""

Write-Host "✅ 报告已生成: $reportFile" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 准备学习 Day 6:" -ForegroundColor Yellow
Write-Host "条件判断与循环高级应用" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Day 5 学习完成! 恭喜!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow 