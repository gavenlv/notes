# Day 6 条件判断演示脚本
Write-Host "======================================" -ForegroundColor Green
Write-Host "Day 6: 条件判断演示" -ForegroundColor Green  
Write-Host "======================================" -ForegroundColor Green

# 设置脚本路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$playbookPath = Join-Path $scriptPath "..\playbooks\01-advanced-conditionals.yml"

Write-Host "`n=== 演示1: 开发环境条件判断 ===" -ForegroundColor Yellow
Write-Host "运行环境: development"
ansible-playbook $playbookPath -e "env=development" -v

Write-Host "`n=== 演示2: 生产环境条件判断 ===" -ForegroundColor Yellow  
Write-Host "运行环境: production"
ansible-playbook $playbookPath -e "env=production deploy_type=blue_green" -v

Write-Host "`n=== 演示3: 暂存环境条件判断 ===" -ForegroundColor Yellow
Write-Host "运行环境: staging"
ansible-playbook $playbookPath -e "env=staging deploy_type=rolling" -v

Write-Host "`n=== 演示4: 测试环境条件判断 ===" -ForegroundColor Yellow
Write-Host "运行环境: development (测试部署)"
ansible-playbook $playbookPath -e "env=development deploy_type=testing" -v

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "条件判断演示完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# 显示学习要点
Write-Host "`n📚 本演示展示了以下条件判断技术：" -ForegroundColor Cyan
Write-Host "✓ 基础条件判断 (when)" -ForegroundColor White
Write-Host "✓ 多条件组合 (and/or)" -ForegroundColor White
Write-Host "✓ 变量类型检查" -ForegroundColor White
Write-Host "✓ 正则表达式匹配" -ForegroundColor White
Write-Host "✓ 动态条件设置" -ForegroundColor White
Write-Host "✓ 服务兼容性检查" -ForegroundColor White
Write-Host "✓ 用户权限验证" -ForegroundColor White
Write-Host "✓ 条件性配置生成" -ForegroundColor White 