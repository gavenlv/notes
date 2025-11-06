# Day 7 示例：角色与 Galaxy 高级应用

本目录包含 Day 7 学习的各种示例和演示文件，展示 Ansible 角色开发和 Galaxy 应用的最佳实践。

## 📁 目录结构

```
examples/
├── README.md                    # 本文件
├── role-usage/                  # 角色使用示例
│   ├── simple-webserver.yml     # 简单 Web 服务器部署
│   ├── complex-stack.yml        # 复杂应用栈部署
│   └── multi-environment.yml    # 多环境部署
├── role-development/            # 角色开发示例
│   ├── basic-structure/         # 基础角色结构
│   ├── advanced-patterns/       # 高级设计模式
│   └── testing-examples/        # 角色测试示例
└── galaxy-integration/          # Galaxy 集成示例
    ├── requirements-examples/   # 需求文件示例
    ├── private-galaxy/          # 私有 Galaxy 配置
    └── ci-cd-integration/       # CI/CD 集成示例
```

## 🚀 快速开始

### 1. 基础角色使用

```bash
# 安装依赖角色
ansible-galaxy install -r requirements.yml

# 运行简单 Web 服务器部署
ansible-playbook examples/role-usage/simple-webserver.yml

# 运行复杂应用栈部署
ansible-playbook examples/role-usage/complex-stack.yml -e env=staging
```

### 2. 角色开发演示

```bash
# 创建新角色
ansible-galaxy init my-role --init-path ./roles/

# 查看基础角色结构示例
ls -la examples/role-development/basic-structure/

# 学习高级设计模式
cat examples/role-development/advanced-patterns/README.md
```

### 3. Galaxy 操作演示

```bash
# 使用管理脚本
.\scripts\galaxy-manager.ps1 search nginx
.\scripts\galaxy-manager.ps1 install geerlingguy.nginx
.\scripts\galaxy-manager.ps1 list

# 角色演示
.\scripts\role-demo.ps1 all -Environment staging
```

## 📚 学习示例

### 基础角色使用示例

#### 1. 简单 Web 服务器部署 (simple-webserver.yml)
```yaml
---
- name: 部署简单 Web 服务器
  hosts: webservers
  become: yes
  
  roles:
    - role: webserver
      webserver_type: nginx
      webserver_port: 80
      webserver_enable_ssl: false
```

#### 2. 复杂应用栈部署 (complex-stack.yml)
```yaml
---
- name: 部署完整应用栈
  hosts: all
  become: yes
  
  roles:
    # 基础设施层
    - role: geerlingguy.security
      when: "'all' in group_names"
    
    # 数据库层
    - role: database
      when: "'database' in group_names"
      vars:
        database_type: mysql
        database_databases:
          - name: app_db
            encoding: utf8mb4
    
    # Web 服务器层
    - role: webserver
      when: "'webservers' in group_names"
      vars:
        webserver_type: nginx
        webserver_upstream_servers:
          - name: app_backend
            servers: "{{ groups['app'] | map('extract', hostvars, 'ansible_default_ipv4') | map(attribute='address') | list }}"
```

#### 3. 多环境部署 (multi-environment.yml)
```yaml
---
- name: 多环境应用部署
  hosts: all
  become: yes
  
  vars:
    environment_configs:
      development:
        webserver_worker_processes: 1
        database_max_connections: 50
        enable_debug: true
      staging:
        webserver_worker_processes: 2
        database_max_connections: 100
        enable_debug: false
      production:
        webserver_worker_processes: auto
        database_max_connections: 200
        enable_debug: false
        enable_ssl: true
  
  pre_tasks:
    - name: 设置环境变量
      set_fact:
        current_env: "{{ env | default('development') }}"
        env_config: "{{ environment_configs[env | default('development')] }}"
  
  roles:
    - role: webserver
      vars:
        webserver_worker_processes: "{{ env_config.webserver_worker_processes }}"
        webserver_enable_ssl: "{{ env_config.enable_ssl | default(false) }}"
    
    - role: database
      vars:
        database_max_connections: "{{ env_config.database_max_connections }}"
        database_debug: "{{ env_config.enable_debug }}"
```

### 角色开发示例

#### 基础角色结构
```
my-role/
├── defaults/
│   └── main.yml          # 默认变量
├── vars/
│   └── main.yml          # 角色变量
├── tasks/
│   ├── main.yml          # 主任务文件
│   ├── install.yml       # 安装任务
│   ├── configure.yml     # 配置任务
│   └── service.yml       # 服务管理任务
├── handlers/
│   └── main.yml          # 处理器
├── templates/
│   ├── config.j2         # 配置模板
│   └── service.j2        # 服务模板
├── files/
│   ├── scripts/          # 脚本文件
│   └── configs/          # 静态配置文件
├── meta/
│   └── main.yml          # 角色元数据
├── tests/
│   ├── inventory         # 测试清单
│   └── test.yml          # 测试剧本
└── README.md             # 角色文档
```

#### 高级设计模式

**1. 参数化角色设计**
```yaml
# defaults/main.yml
---
app_name: "myapp"
app_version: "latest"
app_environment: "production"

# 支持多种部署策略
deployment_strategy: "standard"  # standard, ha, cluster

# 环境特定配置
environments:
  development:
    debug_mode: true
    log_level: debug
    replicas: 1
  production:
    debug_mode: false
    log_level: warn
    replicas: 3
```

**2. 条件化任务执行**
```yaml
# tasks/main.yml
---
- name: 包含操作系统特定任务
  include_tasks: "{{ ansible_os_family | lower }}.yml"

- name: 包含环境特定配置
  include_tasks: "{{ app_environment }}.yml"
  when: app_environment in ['staging', 'production']

- name: 包含部署策略特定任务
  include_tasks: "deploy_{{ deployment_strategy }}.yml"
```

**3. 角色依赖管理**
```yaml
# meta/main.yml
---
dependencies:
  - role: common.base
    vars:
      base_packages:
        - curl
        - wget
        - git
  
  - role: security.hardening
    when: enable_security_hardening | default(true)
  
  - role: monitoring.agent
    vars:
      monitoring_enabled: "{{ enable_monitoring | default(false) }}"
```

### Galaxy 集成示例

#### Requirements.yml 高级配置
```yaml
---
# 从不同源安装角色

# 1. 从 Galaxy 安装指定版本
- name: geerlingguy.nginx
  version: "3.1.4"

# 2. 从 Git 仓库安装
- src: https://github.com/company/custom-role.git
  scm: git
  version: main
  name: company.custom

# 3. 从本地路径安装
- src: ../shared-roles/common
  name: shared.common

# 4. 从压缩包安装
- src: https://releases.company.com/roles/app-role.tar.gz
  name: company.app
  version: "1.2.0"
```

#### 私有 Galaxy 配置
```ini
# ansible.cfg
[galaxy]
server_list = company_galaxy, public_galaxy

[galaxy_server.company_galaxy]
url = https://galaxy.company.com/
username = your_username
password = your_password

[galaxy_server.public_galaxy]
url = https://galaxy.ansible.com/
```

## 🧪 测试和验证

### 角色测试
```bash
# 使用 Molecule 测试角色
pip install molecule[docker]
cd roles/webserver
molecule test

# 语法检查
ansible-playbook playbooks/webserver-deployment.yml --syntax-check

# 干运行
ansible-playbook playbooks/webserver-deployment.yml --check --diff
```

### 角色验证
```bash
# 验证角色结构
.\scripts\role-demo.ps1 test

# 验证角色功能
ansible-playbook examples/role-usage/simple-webserver.yml --check
```

## 📖 最佳实践

### 1. 角色设计原则
- **单一职责**: 每个角色专注于一个特定功能
- **参数化**: 提供足够的配置选项
- **幂等性**: 确保重复执行的安全性
- **文档化**: 提供清晰的使用说明

### 2. 变量管理
- 使用 `defaults/main.yml` 提供默认值
- 使用 `vars/main.yml` 存储固定值
- 利用环境特定变量进行配置覆盖
- 遵循变量优先级规则

### 3. 任务组织
- 将复杂任务拆分为独立文件
- 使用条件和标签控制执行流程
- 实现合理的错误处理
- 提供详细的任务描述

### 4. Galaxy 管理
- 维护 requirements.yml 文件
- 锁定生产环境的角色版本
- 定期更新角色依赖
- 建立角色测试流程

## 🔧 故障排除

### 常见问题

**1. 角色安装失败**
```bash
# 检查网络连接
curl -I https://galaxy.ansible.com

# 使用详细输出
ansible-galaxy install geerlingguy.nginx -vvv

# 强制重新安装
ansible-galaxy install geerlingguy.nginx --force
```

**2. 角色依赖冲突**
```bash
# 清理旧版本
ansible-galaxy remove old-role

# 重新安装依赖
ansible-galaxy install -r requirements.yml --force
```

**3. 变量优先级问题**
```bash
# 检查变量值
ansible-playbook playbook.yml -e debug_vars=true

# 使用额外变量覆盖
ansible-playbook playbook.yml -e "app_debug=true"
```

## 📚 参考资源

- [Ansible Roles 官方文档](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)
- [Ansible Galaxy 官方文档](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html)
- [角色最佳实践指南](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Molecule 测试框架](https://molecule.readthedocs.io/)

## 💡 学习建议

1. **从简单开始**: 先掌握基础角色使用，再学习复杂设计模式
2. **实践为主**: 多动手创建和修改角色
3. **社区学习**: 研究优秀的开源角色实现
4. **测试驱动**: 为角色编写测试用例
5. **文档完善**: 为自己的角色编写详细文档

---

*通过这些示例，您可以深入理解 Ansible 角色的设计原理和 Galaxy 的强大功能，为构建企业级自动化解决方案打下坚实基础。* 