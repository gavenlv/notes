# Day 5 变量与模板演示脚本
# PowerShell script for Windows users

param(
    [string]$Demo = "all",
    [switch]$Help,
    [switch]$Verbose
)

# 颜色输出函数
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Success { param([string]$Text) Write-ColorText "✅ $Text" "Green" }
function Write-Info { param([string]$Text) Write-ColorText "ℹ️  $Text" "Cyan" }
function Write-Warning { param([string]$Text) Write-ColorText "⚠️  $Text" "Yellow" }
function Write-Error { param([string]$Text) Write-ColorText "❌ $Text" "Red" }
function Write-Step { param([string]$Text) Write-ColorText "🔄 $Text" "Magenta" }

# 显示帮助信息
function Show-Help {
    Write-Host @"
Day 5: 变量与模板高级应用 - 演示脚本

用法: .\run-demos.ps1 [选项]

选项:
  -Demo <demo_name>   运行特定演示 (variables, templates, all)
  -Verbose           显示详细输出
  -Help              显示此帮助信息

演示说明:
  variables          基础变量演示 (01-variables-demo.yml)
  templates          高级模板演示 (02-advanced-templates.yml)  
  all               运行所有演示 (默认)

示例:
  .\run-demos.ps1
  .\run-demos.ps1 -Demo variables -Verbose
  .\run-demos.ps1 -Demo templates

注意: 如果 Ansible 未安装，脚本将模拟运行并生成示例文件。
"@
}

# 检查 Ansible 安装
function Test-AnsibleInstallation {
    try {
        $null = Get-Command ansible-playbook -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# 模拟变量演示
function Invoke-VariablesDemo {
    Write-Step "运行变量演示..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outputDir = "$env:TEMP"
    
    # 模拟生成变量报告
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
    Write-Success "变量报告已生成: $reportFile"
    
    # 模拟生成 JSON 导出
    $jsonContent = @{
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
    } | ConvertTo-Json -Depth 5
    
    $jsonFile = "$outputDir\variables_export_$timestamp.json"
    $jsonContent | Out-File -FilePath $jsonFile -Encoding UTF8
    Write-Success "JSON 导出已生成: $jsonFile"
    
    Write-Info @"
🎉 变量演示完成！

生成的文件:
- 变量报告: $reportFile
- JSON 导出: $jsonFile

学习要点:
✓ 基本变量定义和使用
✓ 列表和字典变量操作
✓ 嵌套变量访问
✓ 变量过滤器应用
✓ 条件变量设置
✓ Facts 变量收集
✓ 模板文件生成
"@
}

# 模拟高级模板演示
function Invoke-TemplatesDemo {
    Write-Step "运行高级模板演示..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outputDir = "$env:TEMP"
    
    # 生成 Nginx 配置示例
    $nginxConfig = @"
# Advanced Nginx Configuration
# Generated by PowerShell Demo on $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
# Target host: $env:COMPUTERNAME

user www-data;
worker_processes $env:NUMBER_OF_PROCESSORS;
worker_rlimit_nofile $($env:NUMBER_OF_PROCESSORS * 2048);
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
    accept_mutex off;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Logging Configuration
    log_format main '`$remote_addr - `$remote_user [`$time_local] "`$request" '
                    '`$status `$body_bytes_sent "`$http_referer" '
                    '"`$http_user_agent" "`$http_x_forwarded_for" '
                    '`$request_time `$upstream_response_time';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip Configuration
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1000;
    
    # Rate Limiting
    limit_req_zone `$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone `$binary_remote_addr zone=login:10m rate=1r/s;
    limit_conn_zone `$binary_remote_addr zone=addr:10m;
    
    # Main Virtual Hosts
    server {
        listen 80;
        server_name www.company.com;
        
        # Connection limiting
        limit_conn addr 10;
        
        location / {
            try_files `$uri `$uri/ /index.php?`$query_string;
            expires 1h;
        }
        
        location /api/ {
            # API specific rate limiting
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api-backend;
            proxy_set_header Host `$host;
        }
        
        # Static files caching
        location ~* \.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)`$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
        
        # Logging
        access_log /var/log/nginx/www.company.com.access.log main;
        error_log /var/log/nginx/www.company.com.error.log;
    }
}
"@
    
    $nginxFile = "$outputDir\nginx_advanced_$timestamp.conf"
    $nginxConfig | Out-File -FilePath $nginxFile -Encoding UTF8
    Write-Success "Nginx 配置已生成: $nginxFile"
    
    # 生成应用配置示例
    $appConfig = @"
# AdvancedWebApp Application Configuration
# Generated by PowerShell Demo on $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
# Environment: production
# Version: 2.1.0

application:
  name: "AdvancedWebApp"
  version: "2.1.0"
  environment: "production"
  debug: false
  
  # Server configuration
  server:
    host: "0.0.0.0"
    port: 8080
    workers: $($env:NUMBER_OF_PROCESSORS * 2)
    timeout: 30
    keepalive: 2
    max_requests: 1000
    
  # Database configuration
  database:
    host: "192.168.1.30"
    port: 3306
    name: "advancedwebapp_production"
    user: "advancedwebapp_user"
    password: "advancedwebapp_password_production"
    
    # Connection pool settings
    pool_size: 20
    max_overflow: 30
    pool_timeout: 30
    pool_recycle: 3600
    
  # Redis/Cache configuration
  cache:
    enabled: true
    type: "redis"
    host: "192.168.1.20"
    port: 6379
    db: 0
    default_timeout: 3600
    key_prefix: "AdvancedWebApp_prod_"
    
  # Logging configuration
  logging:
    level: "WARNING"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file:
      enabled: true
      path: "/var/log/advancedwebapp/application.log"
      max_bytes: 10485760
      backup_count: 5
    json_format: true
    
  # Feature flags
  features:
    new_dashboard: true
    experimental_api: false
    debug_toolbar: false
    rate_limiting: true
    metrics_collection: true
    error_reporting: true

# Infrastructure settings
infrastructure:
  load_balancer:
    enabled: true
    algorithm: "round_robin"
    health_check:
      enabled: true
      path: "/health"
      interval: 30
      timeout: 5
      retries: 3
      
  monitoring:
    enabled: true
    prometheus:
      enabled: true
      endpoint: "/metrics"
      scrape_interval: "15s"
      labels:
        environment: "production"
        application: "advancedwebapp"
        version: "2.1.0"

# Configuration validation
validation:
  config_version: "1.0"
  generated_by: "PowerShell Demo"
  generated_on: "$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")"
  target_host: "$env:COMPUTERNAME"
  checksum: "demo_$(Get-Random)"
"@
    
    $appFile = "$outputDir\app_config_$timestamp.yml"
    $appConfig | Out-File -FilePath $appFile -Encoding UTF8
    Write-Success "应用配置已生成: $appFile"
    
    # 生成监控配置示例
    $monitoringConfig = @{
        monitoring = @{
            version = "1.0"
            generated_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
            generated_by = $env:COMPUTERNAME
            application = @{
                name = "AdvancedWebApp"
                version = "2.1.0"
                environment = "production"
            }
            global_settings = @{
                scrape_interval = "15s"
                evaluation_interval = "15s"
                external_labels = @{
                    environment = "production"
                    application = "advancedwebapp"
                    region = "demo"
                }
            }
            targets = @{
                servers = @(
                    @{
                        hostname = "web01"
                        ip = "192.168.1.10"
                        role = "frontend"
                        services = @("nginx", "php-fpm")
                        specs = @{
                            cpu_cores = 4
                            memory_mb = 8192
                            disk_gb = 500
                        }
                    },
                    @{
                        hostname = "api01"
                        ip = "192.168.1.20"
                        role = "api"
                        services = @("nodejs", "redis")
                        specs = @{
                            cpu_cores = 8
                            memory_mb = 16384
                            disk_gb = 1000
                        }
                    }
                )
            }
            health_checks = @{
                enabled = $true
                endpoints = @(
                    @{
                        name = "health"
                        path = "/health"
                        check_interval = "30s"
                        timeout = "5s"
                        expected_status = 200
                    }
                )
            }
        }
    } | ConvertTo-Json -Depth 10
    
    $monitoringFile = "$outputDir\monitoring_config_$timestamp.json"
    $monitoringConfig | Out-File -FilePath $monitoringFile -Encoding UTF8
    Write-Success "监控配置已生成: $monitoringFile"
    
    Write-Info @"
🎉 高级模板演示完成！

生成的文件:
📄 Nginx 配置: $nginxFile
⚙️ 应用配置: $appFile
📊 监控配置: $monitoringFile

高级模板技术展示:
✓ 复杂变量处理和嵌套访问
✓ 条件判断和循环控制
✓ 过滤器链式使用
✓ 动态配置生成
✓ 多格式文件生成 (YAML, JSON, Conf)
✓ 环境特定配置

建议下一步:
1. 查看生成的配置文件
2. 理解模板中的逻辑
3. 尝试修改变量重新生成
4. 学习更多 Jinja2 过滤器
"@
}

# 显示模板文件内容
function Show-TemplateContent {
    param([string]$TemplatePath)
    
    if (Test-Path $TemplatePath) {
        Write-Info "模板文件内容: $TemplatePath"
        Write-Host "=" * 50 -ForegroundColor Yellow
        Get-Content $TemplatePath | ForEach-Object {
            if ($_ -match "{{.*}}") {
                Write-Host $_ -ForegroundColor Cyan
            } elseif ($_ -match "{%.*%}") {
                Write-Host $_ -ForegroundColor Magenta
            } elseif ($_ -match "^#.*") {
                Write-Host $_ -ForegroundColor Green
            } else {
                Write-Host $_
            }
        }
        Write-Host "=" * 50 -ForegroundColor Yellow
    } else {
        Write-Warning "模板文件不存在: $TemplatePath"
    }
}

# 主函数
function Main {
    Clear-Host
    Write-ColorText @"
========================================
🚀 Day 5: 变量与模板高级应用
========================================
版本: 2.1.0
环境: PowerShell 演示
时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
主机: $env:COMPUTERNAME
用户: $env:USERNAME
========================================
"@ "Yellow"
    
    if ($Help) {
        Show-Help
        return
    }
    
    # 检查 Ansible 安装
    $ansibleInstalled = Test-AnsibleInstallation
    if ($ansibleInstalled) {
        Write-Success "Ansible 已安装，将使用真实的 playbook 运行"
    } else {
        Write-Warning "Ansible 未安装，将使用模拟演示模式"
        Write-Info "要安装 Ansible，请参考: https://docs.ansible.com/ansible/latest/installation_guide/"
    }
    
    Write-Host ""
    
    switch ($Demo.ToLower()) {
        "variables" {
            if ($ansibleInstalled) {
                Write-Step "运行 Ansible 变量演示..."
                & ansible-playbook "day5-variables-templates/playbooks/01-variables-demo.yml" $(if ($Verbose) { "-v" })
            } else {
                Invoke-VariablesDemo
            }
        }
        "templates" {
            if ($ansibleInstalled) {
                Write-Step "运行 Ansible 高级模板演示..."
                & ansible-playbook "day5-variables-templates/playbooks/02-advanced-templates.yml" $(if ($Verbose) { "-v" })
            } else {
                Invoke-TemplatesDemo
            }
        }
        "all" {
            Write-Step "运行所有演示..."
            if ($ansibleInstalled) {
                Write-Step "运行变量演示..."
                & ansible-playbook "day5-variables-templates/playbooks/01-variables-demo.yml" $(if ($Verbose) { "-v" })
                Write-Host ""
                Write-Step "运行高级模板演示..."
                & ansible-playbook "day5-variables-templates/playbooks/02-advanced-templates.yml" $(if ($Verbose) { "-v" })
            } else {
                Invoke-VariablesDemo
                Write-Host ""
                Invoke-TemplatesDemo
            }
        }
        default {
            Write-Error "未知的演示类型: $Demo"
            Write-Info "支持的演示类型: variables, templates, all"
            Show-Help
            return
        }
    }
    
    Write-Host ""
    Write-Success "Day 5 演示完成！"
    Write-Info @"
📚 学习总结:
- ✅ 掌握了 Ansible 变量系统的高级用法
- ✅ 学会了 Jinja2 模板引擎的强大功能
- ✅ 理解了复杂配置文件的动态生成
- ✅ 体验了企业级变量管理最佳实践

🎯 下一步学习: Day 6 - 条件判断与循环高级应用
"@
    
    if ($Verbose) {
        Write-Host ""
        Write-Info "显示模板文件内容示例:"
        Show-TemplateContent "day5-variables-templates/templates/variable-report.md.j2"
    }
}

# 运行主函数
Main 