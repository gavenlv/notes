# Day 5 变量与模板演示脚本
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "🚀 Day 5: 变量与模板高级应用" -ForegroundColor Yellow  
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "版本: 2.1.0" -ForegroundColor Cyan
Write-Host "时间: $(Get-Date)" -ForegroundColor Cyan
Write-Host "主机: $env:COMPUTERNAME" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputDir = "$env:TEMP"

Write-Host "🔄 生成演示文件..." -ForegroundColor Magenta

# 生成变量报告文件
$reportContent = @"
# Ansible 变量系统演示报告

**生成时间**: $(Get-Date)
**主机**: $env:COMPUTERNAME  
**用户**: $env:USERNAME

## 系统信息
- CPU核数: $env:NUMBER_OF_PROCESSORS
- 架构: $env:PROCESSOR_ARCHITECTURE
- 操作系统: Windows

## 学习内容
### Day 5: 变量与模板高级应用

#### 已创建的文件:
1. **主要文档**: variables-templates.md
2. **Playbook演示**: 
   - 01-variables-demo.yml (基础变量演示)  
   - 02-advanced-templates.yml (高级模板演示)
3. **模板文件**: 
   - variable-report.md.j2 (变量报告模板)
   - advanced-nginx.conf.j2 (Nginx配置模板)
   - user-management.sh.j2 (用户管理脚本模板)
   - app-config.yml.j2 (应用配置模板)
   - monitoring-config.json.j2 (监控配置模板)
   - docker-compose.yml.j2 (Docker配置模板)
   - database-init.sql.j2 (数据库初始化模板)
   - deploy-script.sh.j2 (部署脚本模板)
   - generated-vars.yml.j2 (生成变量模板)
   - conditional-config.j2 (条件配置模板)

#### 核心技术要点:
- ✅ Ansible变量系统深度应用
- ✅ Jinja2模板引擎高级功能  
- ✅ 复杂条件逻辑和循环控制
- ✅ 过滤器链式使用和数据转换
- ✅ 环境特定配置管理
- ✅ 企业级最佳实践模式

#### 实际应用场景:
- 多环境配置管理(开发/测试/生产)
- 动态服务器配置生成
- 用户和权限批量管理
- 监控和告警配置自动化
- 容器化部署配置生成
- 数据库初始化和迁移

---
*此报告展示了Day 5的完整学习成果*
"@

$reportFile = "$outputDir\day5_demo_report_$timestamp.md"
$reportContent | Out-File -FilePath $reportFile -Encoding UTF8

# 生成JSON配置示例
$jsonConfig = @{
    day5_summary = @{
        title = "变量与模板高级应用"
        completion_date = (Get-Date).ToString()
        files_created = 12
        templates_created = 10
        playbooks_created = 2
        techniques_learned = @(
            "变量优先级和作用域",
            "Jinja2模板语法",
            "条件判断和循环",
            "过滤器使用",
            "环境配置管理"
        )
        next_topics = @(
            "Day 6: 条件判断与循环",
            "Day 7: 角色和Galaxy",
            "Day 8: 模块和插件"
        )
    }
    system_info = @{
        hostname = $env:COMPUTERNAME
        user = $env:USERNAME
        cpu_cores = $env:NUMBER_OF_PROCESSORS
        architecture = $env:PROCESSOR_ARCHITECTURE
    }
} | ConvertTo-Json -Depth 5

$jsonFile = "$outputDir\day5_config_$timestamp.json"
$jsonConfig | Out-File -FilePath $jsonFile -Encoding UTF8

Write-Host "✅ 演示报告已生成: $reportFile" -ForegroundColor Green
Write-Host "✅ JSON配置已生成: $jsonFile" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Day 5 学习成果统计:" -ForegroundColor Cyan
Write-Host "- 📄 主要文档: 1个 (variables-templates.md)" -ForegroundColor White
Write-Host "- 🎭 Playbook: 2个 (变量演示 + 高级模板)" -ForegroundColor White  
Write-Host "- 📋 模板文件: 10个 (覆盖多种应用场景)" -ForegroundColor White
Write-Host "- 📚 示例文档: 1个 (README.md)" -ForegroundColor White
Write-Host "- 💻 演示脚本: 3个 (PowerShell脚本)" -ForegroundColor White
Write-Host ""

Write-Host "🎯 核心技能掌握:" -ForegroundColor Yellow
Write-Host "✓ Ansible变量系统的高级用法" -ForegroundColor Green
Write-Host "✓ Jinja2模板引擎的强大功能" -ForegroundColor Green  
Write-Host "✓ 复杂配置文件的动态生成" -ForegroundColor Green
Write-Host "✓ 企业级变量管理最佳实践" -ForegroundColor Green
Write-Host "✓ 多环境配置管理策略" -ForegroundColor Green
Write-Host ""

Write-Host "📁 文件结构:" -ForegroundColor Cyan
Write-Host "day5-variables-templates/" -ForegroundColor White
Write-Host "├── variables-templates.md       # 主要学习文档" -ForegroundColor Gray
Write-Host "├── playbooks/" -ForegroundColor White  
Write-Host "│   ├── 01-variables-demo.yml    # 基础变量演示" -ForegroundColor Gray
Write-Host "│   └── 02-advanced-templates.yml # 高级模板演示" -ForegroundColor Gray
Write-Host "├── templates/                   # 模板文件目录" -ForegroundColor White
Write-Host "│   ├── variable-report.md.j2    # 变量报告模板" -ForegroundColor Gray
Write-Host "│   ├── advanced-nginx.conf.j2   # Nginx配置模板" -ForegroundColor Gray
Write-Host "│   ├── app-config.yml.j2        # 应用配置模板" -ForegroundColor Gray
Write-Host "│   └── ...                      # 其他模板文件" -ForegroundColor Gray
Write-Host "├── examples/" -ForegroundColor White
Write-Host "│   └── README.md                # 示例和练习" -ForegroundColor Gray
Write-Host "└── *.ps1                        # 演示脚本" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 准备学习 Day 6:" -ForegroundColor Yellow
Write-Host "条件判断与循环高级应用" -ForegroundColor White
Write-Host ""
Write-Host "演示完成！查看生成的文件了解详细内容。" -ForegroundColor Green 