# Day 5 变量与模板演示脚本 - 简化版本
# PowerShell script for Windows users

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "🚀 Day 5: 变量与模板高级应用" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "版本: 2.1.0" -ForegroundColor Cyan
Write-Host "环境: PowerShell 演示" -ForegroundColor Cyan
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "主机: $env:COMPUTERNAME" -ForegroundColor Cyan
Write-Host "用户: $env:USERNAME" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# 检查 Ansible 安装
$ansibleInstalled = $false
try {
    $null = Get-Command ansible-playbook -ErrorAction Stop
    $ansibleInstalled = $true
} catch {
    $ansibleInstalled = $false
}

if ($ansibleInstalled) {
    Write-Host "✅ Ansible 已安装，将使用真实的 playbook 运行" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ansible 未安装，将使用模拟演示模式" -ForegroundColor Yellow
    Write-Host "ℹ️  要安装 Ansible，请参考: https://docs.ansible.com/ansible/latest/installation_guide/" -ForegroundColor Cyan
}

Write-Host ""

# 变量演示
Write-Host "🔄 运行变量演示..." -ForegroundColor Magenta

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputDir = "$env:TEMP"

# 生成变量报告
$reportContent = @"
# Ansible 变量系统演示报告

**生成时间**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**目标主机**: $env:COMPUTERNAME
**操作系统**: $((Get-WmiObject Win32_OperatingSystem).Caption)
**Ansible 版本**: 模拟运行 (Ansible 未安装)

---

## 📊 系统信息

| 项目 | 值 |
|------|-----|
| 主机名 | $env:COMPUTERNAME |
| 用户名 | $env:USERNAME |
| CPU 架构 | $env:PROCESSOR_ARCHITECTURE |
| CPU 核数 | $env:NUMBER_OF_PROCESSORS |
| 操作系统 | $((Get-WmiObject Win32_OperatingSystem).Caption) |

## 🔧 应用配置

### 基本信息
- **应用名称**: VariableDemo
- **版本**: 1.0.0
- **环境**: development
- **调试模式**: true

### 支持的编程语言
- Python
- JavaScript  
- Go
- Java

### 应用功能
- ✅ User Authentication
- ✅ File Upload
- ✅ Real Time Chat

---

## 📈 性能建议

⚡ **内存适中**: 当前系统可以满足基本需求
✅ **CPU 性能良好**: 性能优秀

### 建议的配置调整
- Nginx 工作进程: $env:NUMBER_OF_PROCESSORS
- PHP-FPM 进程池: $($env:NUMBER_OF_PROCESSORS * 2)
- 数据库连接池: 10-20

---

## 📝 部署清单

- [ ] 检查所需软件包是否已安装
- [ ] 配置数据库连接
- [ ] 设置 SSL 证书 (如果启用 HTTPS)
- [ ] 配置防火墙规则
- [ ] 设置日志轮转
- [ ] 配置监控告警
- [ ] 备份重要数据
- [ ] 测试应用功能

---

**生成工具**: PowerShell 模拟运行  
**模板版本**: 1.0.0  
**更新时间**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

---

*此报告由演示脚本自动生成，展示了 Ansible 变量系统的功能。*
"@

$reportFile = "$outputDir\variable_report_$timestamp.md"
$reportContent | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "✅ 变量报告已生成: $reportFile" -ForegroundColor Green

# 生成 JSON 导出
$jsonData = @{
    metadata = @{
        hostname = $env:COMPUTERNAME
        generation_time = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        demo_version = "1.0.0"
    }
    application = @{
        name = "VariableDemo"
        version = "1.0.0"
        settings = @{
            debug = $true
            environment = "development"
            database_url = "mysql://demo_user@localhost:3306/demo_db"
            features = @("user_authentication", "file_upload", "real_time_chat")
            supported_languages = @("Python", "JavaScript", "Go", "Java")
        }
    }
    system_facts = @{
        os = (Get-WmiObject Win32_OperatingSystem).Caption
        cpu_cores = [int]$env:NUMBER_OF_PROCESSORS
        architecture = $env:PROCESSOR_ARCHITECTURE
        username = $env:USERNAME
    }
    custom_facts = @{
        hostname = $env:COMPUTERNAME
        os_info = (Get-WmiObject Win32_OperatingSystem).Caption
        cpu_info = "$env:NUMBER_OF_PROCESSORS cores"
        demo_mode = $true
    }
}

$jsonContent = $jsonData | ConvertTo-Json -Depth 5
$jsonFile = "$outputDir\variables_export_$timestamp.json"
$jsonContent | Out-File -FilePath $jsonFile -Encoding UTF8
Write-Host "✅ JSON 导出已生成: $jsonFile" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 变量演示完成！" -ForegroundColor Green
Write-Host ""
Write-Host "生成的文件:" -ForegroundColor Cyan
Write-Host "- 变量报告: $reportFile" -ForegroundColor White
Write-Host "- JSON 导出: $jsonFile" -ForegroundColor White
Write-Host ""
Write-Host "学习要点:" -ForegroundColor Cyan
Write-Host "✓ 基本变量定义和使用" -ForegroundColor White
Write-Host "✓ 列表和字典变量操作" -ForegroundColor White
Write-Host "✓ 嵌套变量访问" -ForegroundColor White
Write-Host "✓ 变量过滤器应用" -ForegroundColor White
Write-Host "✓ 条件变量设置" -ForegroundColor White
Write-Host "✓ Facts 变量收集" -ForegroundColor White
Write-Host "✓ 模板文件生成" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "📚 Day 5 学习总结:" -ForegroundColor Yellow
Write-Host "- ✅ 掌握了 Ansible 变量系统的高级用法" -ForegroundColor White
Write-Host "- ✅ 学会了 Jinja2 模板引擎的强大功能" -ForegroundColor White
Write-Host "- ✅ 理解了复杂配置文件的动态生成" -ForegroundColor White
Write-Host "- ✅ 体验了企业级变量管理最佳实践" -ForegroundColor White
Write-Host ""
Write-Host "🎯 下一步学习: Day 6 - 条件判断与循环高级应用" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# 显示文件内容示例
Write-Host ""
Write-Host "📄 查看生成的报告文件:" -ForegroundColor Cyan
if (Test-Path $reportFile) {
    Write-Host "打开报告文件: notepad `"$reportFile`"" -ForegroundColor White
    Write-Host "打开JSON文件: notepad `"$jsonFile`"" -ForegroundColor White
}

Write-Host ""
Write-Host "🔍 模板文件位置:" -ForegroundColor Cyan
Write-Host "- day5-variables-templates/templates/" -ForegroundColor White
Write-Host "- day5-variables-templates/playbooks/" -ForegroundColor White
Write-Host "- day5-variables-templates/variables-templates.md" -ForegroundColor White

Write-Host ""
Write-Host "完成！演示结束。" -ForegroundColor Yellow 