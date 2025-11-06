# Day 6 错误处理演示脚本
Write-Host "======================================" -ForegroundColor Green
Write-Host "Day 6: 错误处理和流程控制演示" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# 设置脚本路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$playbookPath = Join-Path $scriptPath "..\playbooks\03-error-handling.yml"

Write-Host "`n=== 错误处理演示说明 ===" -ForegroundColor Cyan
Write-Host "本演示将展示以下错误处理技术：" -ForegroundColor White
Write-Host "• failed_when - 自定义失败条件" -ForegroundColor White
Write-Host "• ignore_errors - 错误忽略策略" -ForegroundColor White
Write-Host "• until/retries - 重试机制" -ForegroundColor White
Write-Host "• block/rescue/always - 结构化错误处理" -ForegroundColor White
Write-Host "• 条件性流程控制" -ForegroundColor White
Write-Host "• 循环中的错误处理" -ForegroundColor White
Write-Host "• 错误恢复和清理" -ForegroundColor White
Write-Host "• 最终状态验证" -ForegroundColor White

Write-Host "`n=== 演示1: 开发环境部署 (基础错误处理) ===" -ForegroundColor Yellow
Write-Host "环境: development (容错较松)"
ansible-playbook $playbookPath -e "env=development rollback=true" -v

Write-Host "`n=== 演示2: 暂存环境部署 (标准错误处理) ===" -ForegroundColor Yellow
Write-Host "环境: staging (标准流程)"
ansible-playbook $playbookPath -e "env=staging rollback=true skip_tests=false" -v

Write-Host "`n=== 演示3: 生产环境部署 (严格错误处理) ===" -ForegroundColor Yellow
Write-Host "环境: production (需要强制参数)"
Write-Host "⚠️ 第一次运行会失败，展示生产环境安全检查" -ForegroundColor Red
ansible-playbook $playbookPath -e "env=production rollback=true" -v

Write-Host "`n=== 演示4: 生产环境强制部署 ===" -ForegroundColor Yellow
Write-Host "环境: production (启用强制部署)"
ansible-playbook $playbookPath -e "env=production force=true rollback=true" -v

Write-Host "`n=== 演示5: 跳过测试的部署 ===" -ForegroundColor Yellow
Write-Host "环境: staging (跳过性能测试)"
ansible-playbook $playbookPath -e "env=staging skip_tests=true rollback=true" -v

Write-Host "`n=== 演示6: 禁用回滚的部署 ===" -ForegroundColor Yellow
Write-Host "环境: development (禁用回滚机制)"
ansible-playbook $playbookPath -e "env=development rollback=false" -v

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "错误处理演示完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# 显示学习要点总结
Write-Host "`n📚 错误处理技术要点：" -ForegroundColor Cyan
Write-Host "✓ failed_when - 自定义失败条件" -ForegroundColor White
Write-Host "✓ ignore_errors - 忽略非关键错误" -ForegroundColor White
Write-Host "✓ until/retries - 重试机制" -ForegroundColor White
Write-Host "✓ block/rescue/always - 结构化错误处理" -ForegroundColor White
Write-Host "✓ register - 结果收集和检查" -ForegroundColor White
Write-Host "✓ when - 条件性执行" -ForegroundColor White
Write-Host "✓ fail - 主动失败控制" -ForegroundColor White
Write-Host "✓ set_fact - 状态标志管理" -ForegroundColor White

Write-Host "`n🎯 最佳实践建议：" -ForegroundColor Magenta
Write-Host "• 预期可能的失败点并准备处理策略" -ForegroundColor White
Write-Host "• 区分关键错误和非关键错误" -ForegroundColor White
Write-Host "• 为生产环境设置更严格的检查" -ForegroundColor White
Write-Host "• 实现自动回滚和恢复机制" -ForegroundColor White
Write-Host "• 记录详细的错误日志和状态" -ForegroundColor White
Write-Host "• 为不同环境设置不同的错误策略" -ForegroundColor White

Write-Host "`n⚡ 可用的命令行参数：" -ForegroundColor Green
Write-Host "-e env=<environment>     设置部署环境 (development/staging/production)" -ForegroundColor Gray
Write-Host "-e force=true            启用强制部署 (生产环境必需)" -ForegroundColor Gray
Write-Host "-e rollback=false        禁用自动回滚" -ForegroundColor Gray  
Write-Host "-e skip_tests=true       跳过性能测试" -ForegroundColor Gray 