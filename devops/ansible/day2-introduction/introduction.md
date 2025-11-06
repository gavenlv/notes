# Day 2: Ansible 基础介绍

## 📋 学习目标

- 深入理解 Ansible 的核心概念
- 掌握 Ansible 的工作原理和架构
- 学习 Ansible 基础术语和组件
- 实践基本的 Ad-hoc 命令
- 了解 Ansible 模块系统

## 🏗️ Ansible 核心概念

### 什么是 Ansible？

Ansible 是一个开源的自动化平台，用于：
- **配置管理** (Configuration Management)
- **应用部署** (Application Deployment)  
- **任务自动化** (Task Automation)
- **多层编排** (Multi-tier Orchestration)

### 核心特性

1. **无代理架构** (Agentless)
   - 不需要在目标主机安装客户端
   - 通过 SSH (Linux) 或 WinRM (Windows) 通信

2. **声明式语法** (Declarative)
   - 描述期望的状态，而不是执行步骤
   - 使用 YAML 格式，易读易写

3. **幂等性** (Idempotency)
   - 多次执行相同操作产生相同结果
   - 避免重复配置和错误

4. **模块化设计** (Modular)
   - 丰富的内置模块库
   - 支持自定义模块开发

## 🧩 核心组件详解

### 1. Control Node (控制节点)
- 安装 Ansible 的机器
- 执行 playbook 和 ad-hoc 命令
- 存储 inventory 和配置文件

```bash
# 控制节点要求
- Python 3.6+ 
- Linux/macOS/WSL (不支持 Windows 作为控制节点)
- SSH 客户端
```

### 2. Managed Nodes (受管节点)
- 被 Ansible 管理的目标机器
- 需要 Python 解释器
- 需要 SSH 服务 (Linux) 或 WinRM (Windows)

### 3. Inventory (清单)
定义和组织受管节点的文件

**INI 格式示例**:
```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
db2.example.com

[production:children]
webservers
databases
```

**YAML 格式示例**:
```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
        web2.example.com:
    databases:
      hosts:
        db1.example.com:
        db2.example.com:
```

### 4. Modules (模块)
执行具体任务的代码单元

**常用模块分类**:
- **系统模块**: `user`, `group`, `service`, `cron`
- **文件模块**: `copy`, `file`, `template`, `fetch`
- **包管理**: `apt`, `yum`, `pip`, `npm`
- **云服务**: `ec2`, `azure_rm`, `gcp_compute`
- **网络模块**: `uri`, `get_url`, `firewall`

### 5. Playbooks (剧本)
包含一系列任务的 YAML 文件

**基本结构**:
```yaml
---
- name: Web servers setup
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        
    - name: Start nginx service
      service:
        name: nginx
        state: started
        enabled: yes
```

### 6. Tasks (任务)
调用模块执行特定操作的单元

### 7. Plays (剧目)
映射主机组到任务的部分

### 8. Handlers (处理器)
只在被通知时运行的特殊任务

```yaml
tasks:
  - name: Update nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx

handlers:
  - name: restart nginx
    service:
      name: nginx
      state: restarted
```

## 🎭 Ansible 工作流程

1. **读取 Inventory**: 确定目标主机
2. **建立连接**: 通过 SSH/WinRM 连接到目标主机
3. **传输模块**: 将 Python 模块传输到目标主机
4. **执行任务**: 在目标主机上执行模块
5. **收集结果**: 获取执行结果并返回
6. **清理环境**: 删除临时文件

## 🚀 Ad-hoc 命令实践

### 基本语法
```bash
ansible <pattern> -m <module> -a <arguments> [options]
```

### 实践练习

详细示例见：[examples/basic-commands.md](./examples/basic-commands.md)

#### 1. 信息收集
```bash
# 查看所有主机的操作系统信息
ansible all -m setup -a "filter=ansible_os_family"

# 查看内存信息
ansible all -m setup -a "filter=ansible_memory_mb"

# 查看 CPU 信息
ansible all -m setup -a "filter=ansible_processor_count"
```

#### 2. 文件管理
```bash
# 创建目录
ansible webservers -m file -a "path=/opt/app state=directory mode=0755" --become

# 复制文件
ansible all -m copy -a "src=./configs/test.conf dest=/tmp/test.conf owner=root group=root mode=0644" --become

# 下载文件
ansible all -m get_url -a "url=https://example.com/file.tar.gz dest=/tmp/file.tar.gz"
```

#### 3. 软件管理
```bash
# 安装软件包
ansible ubuntu -m apt -a "name=htop state=present update_cache=yes" --become

# 安装多个软件包
ansible centos -m yum -a "name=htop,git,curl state=present" --become

# 升级所有软件包
ansible all -m package -a "name=* state=latest" --become
```

## 📊 模块详解

### 核心模块示例

**详细配置见**: [configs/modules-reference.yml](./configs/modules-reference.yml)

#### 1. command vs shell
```bash
# command: 不支持管道、重定向
ansible all -m command -a "ls -la /tmp"

# shell: 支持 shell 特性
ansible all -m shell -a "ps aux | grep nginx | wc -l"
```

#### 2. copy vs template
```bash
# copy: 直接复制文件
ansible all -m copy -a "src=static.conf dest=/etc/app.conf"

# template: 支持变量替换
ansible all -m template -a "src=dynamic.conf.j2 dest=/etc/app.conf"
```

#### 3. service vs systemd
```bash
# service: 通用服务管理
ansible all -m service -a "name=nginx state=started"

# systemd: 专用于 systemd 系统
ansible all -m systemd -a "name=nginx state=started daemon_reload=yes"
```

## 🔧 配置最佳实践

### 1. Inventory 组织
```ini
# 按环境分组
[production]
prod-web[01:03].example.com

[staging] 
stage-web[01:02].example.com

# 按功能分组
[webservers]
web[01:05].example.com

[databases]
db[01:02].example.com

# 按地域分组
[us-east]
us-east-web[01:03].example.com

[us-west]
us-west-web[01:03].example.com
```

### 2. 变量优先级
```
1. Extra vars (-e)
2. Task vars
3. Block vars
4. Role and include vars
5. Play vars
6. Host facts
7. Host vars
8. Group vars
9. Default vars
```

### 3. 命令行技巧
```bash
# 并行执行 (默认 5 个)
ansible all -m ping -f 10

# 限制主机
ansible webservers[0:2] -m ping

# 使用正则表达式
ansible ~web.* -m ping

# 排除主机
ansible all:!staging -m ping

# 交集
ansible webservers:&production -m ping
```

## 📝 实验练习

### 练习 1: 环境探索
```bash
# 1. 收集所有主机信息
ansible all -m setup > inventory_facts.json

# 2. 查看网络配置
ansible all -m setup -a "filter=ansible_default_ipv4"

# 3. 检查磁盘空间
ansible all -m shell -a "df -h"
```

### 练习 2: 批量配置
```bash
# 1. 创建用户
ansible all -m user -a "name=ansible_user shell=/bin/bash" --become

# 2. 安装基础软件
ansible all -m package -a "name=vim,curl,wget state=present" --become

# 3. 配置时区
ansible all -m timezone -a "name=Asia/Shanghai" --become
```

### 练习 3: 服务管理
```bash
# 1. 安装并启动 nginx
ansible webservers -m package -a "name=nginx state=present" --become
ansible webservers -m service -a "name=nginx state=started enabled=yes" --become

# 2. 检查服务状态
ansible webservers -m shell -a "systemctl status nginx"
```

## 📚 参考资源

- [Ansible 模块索引](https://docs.ansible.com/ansible/latest/modules/modules_by_category.html)
- [最佳实践指南](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible 命令行工具](https://docs.ansible.com/ansible/latest/user_guide/command_line_tools.html)

## ✅ 检查清单

- [ ] 理解 Ansible 核心概念和架构
- [ ] 掌握 Ad-hoc 命令基本语法
- [ ] 熟悉常用模块的使用
- [ ] 完成基础实验练习
- [ ] 理解 Inventory 的组织方式
- [ ] 掌握命令行参数和选项

---

**下一步**: [Day 3 - Inventory 管理](../day3-inventory-management/inventory-management.md) 