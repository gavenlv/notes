# Day 4: Playbooks 基础命令示例

## 1. 基本运行命令

### 运行单个 playbook
```bash
# 基础运行
ansible-playbook -i inventory.ini playbook.yml

# 检查模式 (不实际执行)
ansible-playbook -i inventory.ini playbook.yml --check

# 详细输出
ansible-playbook -i inventory.ini playbook.yml -v

# 极详细输出
ansible-playbook -i inventory.ini playbook.yml -vvv

# 指定特定主机组
ansible-playbook -i inventory.ini playbook.yml --limit web_servers

# 从特定任务开始执行
ansible-playbook -i inventory.ini playbook.yml --start-at-task "任务名称"
```

### 变量传递
```bash
# 通过命令行传递变量
ansible-playbook -i inventory.ini playbook.yml -e "server_name=myapp.example.com"

# 传递多个变量
ansible-playbook -i inventory.ini playbook.yml -e "server_name=myapp.com app_port=8080"

# 从文件传递变量
ansible-playbook -i inventory.ini playbook.yml -e "@vars.yml"

# JSON 格式变量
ansible-playbook -i inventory.ini playbook.yml -e '{"users":["alice","bob"]}'
```

## 2. 实践练习命令

### 练习 1: 系统信息收集
```bash
# 运行系统信息收集
cd day4-playbooks-basics
ansible-playbook -i ../day1-installation/configs/inventory.ini playbooks/01-system-info.yml

# 只对本地主机运行
ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local

# 详细模式查看更多信息
ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local -v
```

### 练习 2: Web 服务器配置
```bash
# 检查模式 (推荐先运行)
ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --check

# 实际运行 (需要 sudo 权限)
ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --become

# 自定义变量运行
ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --become \
  -e "server_name=mytest.local app_port=8080"

# 只运行特定标签的任务
ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --become \
  --tags "install,config"
```

### 练习 3: 用户管理
```bash
# 检查模式
ansible-playbook -i localhost, playbooks/03-user-management.yml --connection=local --check --become

# 实际运行
ansible-playbook -i localhost, playbooks/03-user-management.yml --connection=local --become

# 跳过 SSH 密钥配置
ansible-playbook -i localhost, playbooks/03-user-management.yml --connection=local --become \
  --skip-tags "ssh_keys"
```

## 3. 调试和故障排除

### 调试命令
```bash
# 语法检查
ansible-playbook playbook.yml --syntax-check

# 列出所有任务
ansible-playbook -i inventory.ini playbook.yml --list-tasks

# 列出所有主机
ansible-playbook -i inventory.ini playbook.yml --list-hosts

# 列出所有标签
ansible-playbook -i inventory.ini playbook.yml --list-tags

# 步进模式 (逐个任务确认)
ansible-playbook -i inventory.ini playbook.yml --step
```

### 常见错误处理
```bash
# 连接错误时增加详细输出
ansible-playbook -i inventory.ini playbook.yml -vvv

# 忽略错误继续执行
ansible-playbook -i inventory.ini playbook.yml --ignore-errors

# 设置连接超时
ansible-playbook -i inventory.ini playbook.yml --timeout 30

# 设置最大并发
ansible-playbook -i inventory.ini playbook.yml --forks 5
```

## 4. 高级用法

### 条件执行
```bash
# 只在特定条件下运行
ansible-playbook -i inventory.ini playbook.yml --extra-vars "run_tests=true"

# 限制到特定操作系统
ansible-playbook -i inventory.ini playbook.yml --limit "ubuntu"
```

### 标签使用
```bash
# 只运行特定标签
ansible-playbook -i inventory.ini playbook.yml --tags "install,config"

# 跳过特定标签
ansible-playbook -i inventory.ini playbook.yml --skip-tags "debug,test"

# 运行除了指定标签外的所有任务
ansible-playbook -i inventory.ini playbook.yml --skip-tags "slow_tasks"
```

## 5. Windows 环境特殊命令

### PowerShell 运行方式
```powershell
# 设置执行策略 (如果需要)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 使用 PowerShell 运行脚本
.\scripts\run-playbooks.ps1

# 指定特定 playbook
.\scripts\run-playbooks.ps1 -PlaybookName "01-system-info.yml"

# Dry run 模式
.\scripts\run-playbooks.ps1 -DryRun

# 详细输出
.\scripts\run-playbooks.ps1 -Verbose

# 组合参数
.\scripts\run-playbooks.ps1 -PlaybookName "02-web-server-setup.yml" -DryRun -Verbose
```

## 6. 实践建议

### 学习步骤
1. **先检查语法**: `ansible-playbook playbook.yml --syntax-check`
2. **dry run 测试**: `ansible-playbook -i inventory.ini playbook.yml --check`
3. **详细模式运行**: `ansible-playbook -i inventory.ini playbook.yml -v`
4. **正式执行**: `ansible-playbook -i inventory.ini playbook.yml`

### 安全实践
```bash
# 在生产环境前先在测试环境验证
ansible-playbook -i test_inventory.ini playbook.yml --check

# 限制到单个主机测试
ansible-playbook -i inventory.ini playbook.yml --limit "test_host"

# 备份重要配置
ansible-playbook -i inventory.ini backup_playbook.yml

# 分步骤执行复杂 playbook
ansible-playbook -i inventory.ini playbook.yml --step
```

### 性能优化
```bash
# 增加并发数
ansible-playbook -i inventory.ini playbook.yml --forks 10

# 使用 SSH 连接复用
export ANSIBLE_SSH_PIPELINING=True
ansible-playbook -i inventory.ini playbook.yml

# 收集最少的 facts
ansible-playbook -i inventory.ini playbook.yml --extra-vars "gather_facts=False"
```

## 7. 实际练习任务

### 任务 1: 运行并理解输出
运行系统信息收集 playbook，理解每个任务的输出：
```bash
ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local -v
```

### 任务 2: 修改变量重新运行
修改 Web 服务器配置的变量：
```bash
ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --become \
  -e "server_name=mycompany.local document_root=/var/www/mycompany"
```

### 任务 3: 故障排除练习
故意在 playbook 中制造错误，练习调试：
```bash
# 运行有语法错误的 playbook
ansible-playbook broken_playbook.yml --syntax-check

# 运行有逻辑错误的 playbook
ansible-playbook -i localhost, problematic_playbook.yml --connection=local --check -v
```

### 任务 4: 性能对比
对比不同执行方式的性能：
```bash
# 记录执行时间
time ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local

# 禁用 fact gathering 的执行时间
time ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local \
  --extra-vars "gather_facts=False"
```

这些命令示例覆盖了 Ansible playbook 的基本到高级用法。通过实际运行这些命令，你将快速掌握 Ansible 的核心功能和最佳实践。 