# Ansible项目部署快速入门指南

本指南将帮助您快速开始使用Ansible进行项目部署。

## 前置条件

- 已安装Ansible 2.9或更高版本
- 已安装Python 3.6或更高版本
- 具有SSH访问目标服务器的权限
- 已配置SSH密钥认证

## 快速部署步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd day16-project-deployment
```

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Ansible角色
ansible-galaxy install -r roles/requirements.yml
```

### 3. 配置环境

#### 3.1 编辑inventory文件

根据您的环境修改`inventory/`目录下的主机清单文件：

```bash
# 开发环境
vim inventory/development

# 测试环境
vim inventory/staging

# 生产环境
vim inventory/production
```

#### 3.2 配置环境变量

根据需要修改`group_vars/`目录下的环境变量文件：

```bash
# 开发环境变量
vim group_vars/development

# 测试环境变量
vim group_vars/staging

# 生产环境变量
vim group_vars/production
```

#### 3.3 配置敏感信息

加密敏感信息：

```bash
# 编辑vault文件
ansible-vault edit group_vars/vault

# 或者创建新的加密文件
ansible-vault create group_vars/vault
```

### 4. 部署应用

#### 4.1 使用Ansible命令

```bash
# 部署到开发环境
ansible-playbook -i inventory/development playbooks/site.yml

# 部署到测试环境
ansible-playbook -i inventory/staging playbooks/site.yml

# 部署到生产环境
ansible-playbook -i inventory/production playbooks/site.yml
```

#### 4.2 使用部署脚本

```bash
# Linux/Mac
./scripts/deploy.sh --environment development

# Windows
powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1 -Environment development
```

#### 4.3 使用Makefile

```bash
# 部署到开发环境
make deploy-dev

# 部署到测试环境
make deploy-stg

# 部署到生产环境
make deploy-prod
```

### 5. 验证部署

```bash
# 检查主机连接
ansible -i inventory/development all -m ping

# 运行健康检查
ansible-playbook -i inventory/development playbooks/health-check.yml
```

## 常用命令

### 选择性部署

```bash
# 只部署应用层
ansible-playbook -i inventory/production playbooks/site.yml --tags application

# 只部署数据库层
ansible-playbook -i inventory/production playbooks/site.yml --tags database

# 跳过监控组件部署
ansible-playbook -i inventory/production playbooks/site.yml --skip-tags monitoring
```

### 调试和故障排除

```bash
# 详细输出
ansible-playbook -i inventory/development playbooks/site.yml -v

# 更详细的输出
ansible-playbook -i inventory/development playbooks/site.yml -vvv

# 干运行（不执行实际更改）
ansible-playbook -i inventory/development playbooks/site.yml --check

# 从指定任务开始执行
ansible-playbook -i inventory/development playbooks/site.yml --start-at-task="Install application"
```

### 回滚操作

```bash
# 使用回滚脚本
./scripts/rollback.sh --environment production --version previous_version

# 或者手动回滚
ansible-playbook -i inventory/production playbooks/rollback.yml
```

## 常见问题

### 1. SSH连接问题

确保：
- SSH密钥已正确配置
- 目标主机SSH服务正在运行
- 防火墙规则允许SSH连接

### 2. 权限问题

确保：
- Ansible用户具有足够的权限
- sudo配置正确（如果使用become）
- 目标目录具有适当的权限

### 3. 变量未定义错误

检查：
- 变量是否在正确的变量文件中定义
- 变量名拼写是否正确
- 变量作用域是否正确

### 4. Vault密码问题

确保：
- Vault密码文件存在且可读
- Vault密码正确
- 使用了正确的密码脚本

## 下一步

- 阅读[项目文档](README.md)了解更多详细信息
- 查看[角色文档](roles/)了解各个角色的功能
- 探索[Playbook示例](playbooks/)学习更多部署模式

## 获取帮助

如果遇到问题，可以：
- 查看Ansible官方文档
- 检查项目日志文件（`logs/`目录）
- 运行`ansible-playbook --help`获取命令帮助