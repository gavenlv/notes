# Day 7: 角色与 Galaxy 高级应用

## 📚 学习目标

深入掌握 Ansible 角色和 Galaxy 的高级应用，包括：
- 角色的设计模式和最佳实践
- 企业级角色库的构建和管理
- Ansible Galaxy 社区资源的使用
- 角色依赖管理和版本控制
- 角色测试和质量保证
- 角色发布和分享策略
- 复杂场景的角色组合应用

## 🎯 核心概念

### 1. Ansible 角色深度解析

#### 1.1 角色的核心概念
```yaml
# 角色是什么？
# - 可重用的 Ansible 代码组织单元
# - 标准化的目录结构和文件组织
# - 封装特定功能的完整解决方案
# - 支持参数化和定制化
# - 便于分享和协作的代码包

# 角色的优势
# ✓ 代码重用和模块化
# ✓ 标准化的组织结构
# ✓ 易于测试和维护
# ✓ 支持依赖管理
# ✓ 便于团队协作
```

**概念解析**:
- **代码组织单元**: 角色将相关的任务、变量、模板等资源组织在一起，形成功能完整的模块
- **标准化结构**: 遵循 Ansible 约定的目录结构，确保一致性和可维护性
- **功能封装**: 每个角色专注于解决特定的配置管理问题
- **参数化设计**: 通过变量系统支持灵活的配置和定制
- **协作共享**: 便于在团队内部或社区中分享和重用

**设计原则**:
- **单一职责**: 每个角色只负责一个明确的功能领域
- **高内聚**: 相关功能紧密组织在同一个角色中
- **低耦合**: 角色之间通过清晰的接口进行交互
- **可配置**: 通过变量系统支持不同环境的配置需求

#### 1.2 角色目录结构详解
```
my_role/
├── defaults/           # 默认变量 (最低优先级)
│   └── main.yml
├── vars/              # 角色变量 (高优先级)
│   └── main.yml
├── tasks/             # 主要任务定义
│   ├── main.yml
│   ├── install.yml
│   ├── configure.yml
│   └── service.yml
├── handlers/          # 处理器定义
│   └── main.yml
├── templates/         # Jinja2 模板文件
│   ├── config.j2
│   └── service.j2
├── files/             # 静态文件
│   ├── scripts/
│   └── configs/
├── meta/              # 角色元数据
│   └── main.yml
├── tests/             # 测试文件
│   ├── inventory
│   └── test.yml
└── README.md          # 角色说明文档
```

**目录结构解析**:
- **`defaults/`**: 存储角色默认变量，优先级最低，可被其他变量覆盖
- **`vars/`**: 存储角色内部变量，优先级较高，用于固定配置
- **`tasks/`**: 包含角色的主要任务定义，`main.yml` 是入口文件
- **`handlers/`**: 定义处理器，用于服务重启等响应操作
- **`templates/`**: 存放 Jinja2 模板文件，支持动态配置生成
- **`files/`**: 包含静态文件，如脚本、配置文件等
- **`meta/`**: 存储角色元数据，包括依赖关系和兼容性信息
- **`tests/`**: 包含角色测试文件和测试环境配置

**文件组织原则**:
- **模块化设计**: 将复杂任务拆分为多个文件提高可维护性
- **清晰分层**: 不同目录承担不同的功能职责
- **扩展性**: 支持通过添加新文件扩展角色功能
- **标准化**: 遵循 Ansible 社区约定的标准结构

#### 1.3 角色变量优先级
```yaml
# 变量优先级 (高 -> 低)
# 1. Extra vars (-e)
# 2. Task vars
# 3. Block vars
# 4. Role and include vars
# 5. Play vars_files
# 6. Play vars_prompt
# 7. Play vars
# 8. Set_facts / Registered vars
# 9. Host facts
# 10. Playbook host_vars
# 11. Playbook group_vars
# 12. Inventory host_vars
# 13. Inventory group_vars
# 14. Inventory vars
# 15. Role defaults

# 角色变量示例
# defaults/main.yml (默认值)
nginx_version: "1.18"
nginx_user: "nginx"
nginx_worker_processes: "auto"

# vars/main.yml (固定值)
nginx_config_dir: "/etc/nginx"
nginx_log_dir: "/var/log/nginx"
```

### 2. Galaxy 基础操作

#### 2.1 Galaxy 命令详解
```bash
# 搜索角色
ansible-galaxy search nginx
ansible-galaxy search --platforms=EL --galaxy-tags=web

# 安装角色
ansible-galaxy install geerlingguy.nginx
ansible-galaxy install -r requirements.yml

# 列出已安装角色
ansible-galaxy list

# 角色信息查看
ansible-galaxy info geerlingguy.nginx

# 删除角色
ansible-galaxy remove geerlingguy.nginx

# 创建角色骨架
ansible-galaxy init my_new_role
```

**命令解析**:
- **`ansible-galaxy search`**: 在 Ansible Galaxy 社区中搜索可用的角色，支持按名称、平台、标签等条件过滤
- **`ansible-galaxy install`**: 安装指定角色，支持从 Galaxy 仓库、Git 仓库、本地路径等多种来源安装
- **`ansible-galaxy list`**: 显示当前环境中已安装的所有角色及其版本信息
- **`ansible-galaxy info`**: 查看角色的详细信息，包括作者、描述、依赖关系等
- **`ansible-galaxy remove`**: 删除已安装的角色，清理相关文件
- **`ansible-galaxy init`**: 创建新的角色骨架，自动生成标准的目录结构和基础文件

**Galaxy 生态系统**:
- **社区资源**: Ansible Galaxy 提供数千个社区维护的角色，覆盖各种常见应用场景
- **质量保证**: 官方认证的角色经过质量审查，确保可靠性和安全性
- **版本管理**: 支持角色版本控制，便于依赖管理和升级
- **依赖解析**: 自动处理角色间的依赖关系，确保正确安装

#### 2.2 requirements.yml 管理
```yaml
# requirements.yml - 角色依赖文件
---
# 从 Galaxy 安装
- name: geerlingguy.nginx
  version: "3.1.4"

- name: community.mysql
  version: ">=3.0.0"

# 从 Git 仓库安装
- src: https://github.com/company/custom-role.git
  scm: git
  version: main
  name: custom.app

# 从本地路径安装
- src: ../local-roles/monitoring
  name: local.monitoring

# 从压缩包安装
- src: https://releases.example.com/roles/app-role.tar.gz
  name: company.app
```

### 3. 角色设计模式

#### 3.1 参数化设计模式
```yaml
# defaults/main.yml - 提供灵活的配置选项
app_name: "myapp"
app_version: "latest"
app_port: 8080
app_environment: "production"

# 支持不同的部署模式
deployment_mode: "standard"  # standard, ha, cluster

# 环境特定配置
environments:
  development:
    debug: true
    log_level: "debug"
  production:
    debug: false
    log_level: "warn"
```

**参数化设计解析**:
- **基础参数**: 定义应用名称、版本、端口等核心配置参数，提供合理的默认值
- **部署模式**: 支持多种部署架构（标准、高可用、集群），适应不同规模的需求
- **环境配置**: 使用嵌套字典结构管理不同环境的特定配置，实现配置分离
- **默认值策略**: 在 `defaults/` 目录中定义可被覆盖的参数，确保角色灵活性

**设计优势**:
- **可配置性**: 用户无需修改角色代码即可适应不同场景
- **环境适配**: 通过变量系统支持开发、测试、生产等多环境部署
- **扩展性**: 新的部署模式或环境只需添加相应配置，无需修改核心逻辑
- **一致性**: 统一的参数命名和结构确保配置的可读性和可维护性

#### 3.2 条件化任务模式
```yaml
# tasks/main.yml
- name: 包含操作系统特定任务
  include_tasks: "{{ ansible_os_family | lower }}.yml"

- name: 包含环境特定任务
  include_tasks: "{{ app_environment }}.yml"
  when: app_environment in ['staging', 'production']

- name: 包含部署模式特定任务
  include_tasks: "deploy_{{ deployment_mode }}.yml"
```

### 4. 企业级角色开发

#### 4.1 角色模板结构
```yaml
# meta/main.yml - 完整的元数据示例
---
galaxy_info:
  author: "Company DevOps Team"
  company: "Your Company"
  description: "Enterprise web application deployment role"
  license: "MIT"
  min_ansible_version: "2.9"
  
  platforms:
    - name: EL
      versions:
        - 7
        - 8
    - name: Ubuntu
      versions:
        - 18.04
        - 20.04
  
  galaxy_tags:
    - web
    - application
    - deployment
    - enterprise

dependencies:
  - role: common.base
  - role: security.hardening
    when: enable_security_hardening | default(true)

# 角色变量声明
argument_specs:
  main:
    description: "Main entry point for the role"
    options:
      app_name:
        description: "Application name"
        type: str
        required: true
      app_version:
        description: "Application version"
        type: str
        default: "latest"
```

#### 4.2 任务组织策略
```yaml
# tasks/main.yml - 主任务文件
---
- name: 验证角色参数
  include_tasks: validate.yml
  tags: [validate, always]

- name: 安装系统依赖
  include_tasks: install.yml
  tags: [install]

- name: 配置应用
  include_tasks: configure.yml
  tags: [configure]

- name: 部署应用
  include_tasks: deploy.yml
  tags: [deploy]
  when: perform_deployment | default(true)

- name: 配置服务
  include_tasks: service.yml
  tags: [service]

- name: 验证部署
  include_tasks: verify.yml
  tags: [verify]
  when: run_verification | default(true)
```

#### 4.3 模板化配置管理
```jinja2
{# templates/app.conf.j2 #}
# {{ ansible_managed }}
# Application Configuration for {{ app_name }}
# Generated on {{ ansible_date_time.iso8601 }}

[application]
name = {{ app_name }}
version = {{ app_version }}
environment = {{ app_environment | default('production') }}
debug = {{ app_debug | default(false) | lower }}

[server]
host = {{ app_host | default('0.0.0.0') }}
port = {{ app_port | default(8080) }}
workers = {{ app_workers | default(ansible_processor_vcpus) }}

{% if app_ssl_enabled | default(false) %}
[ssl]
enabled = true
certificate = {{ app_ssl_cert_path }}
private_key = {{ app_ssl_key_path }}
{% endif %}

[database]
{% for db in app_databases %}
[database.{{ db.name }}]
host = {{ db.host }}
port = {{ db.port | default(5432) }}
name = {{ db.database }}
user = {{ db.user }}
password = {{ db.password }}
{% endfor %}

[logging]
level = {{ app_log_level | default('INFO') }}
file = {{ app_log_file | default('/var/log/' + app_name + '/app.log') }}
max_size = {{ app_log_max_size | default('100MB') }}
backup_count = {{ app_log_backup_count | default(5) }}

{% if app_monitoring_enabled | default(true) %}
[monitoring]
enabled = true
endpoint = {{ app_monitoring_endpoint | default('/metrics') }}
port = {{ app_monitoring_port | default(9090) }}
{% endif %}
```

#### 4.4 处理器设计
```yaml
# handlers/main.yml
---
- name: restart application
  service:
    name: "{{ app_service_name }}"
    state: restarted
  listen: "restart app"

- name: reload application
  service:
    name: "{{ app_service_name }}"
    state: reloaded
  listen: "reload app"

- name: restart nginx
  service:
    name: nginx
    state: restarted
  when: nginx_installed | default(false)

- name: update application cache
  command: "{{ app_cache_update_command }}"
  when: app_cache_update_command is defined
  listen: "update cache"

- name: notify monitoring
  uri:
    url: "{{ monitoring_webhook_url }}"
    method: POST
    body_format: json
    body:
      service: "{{ app_name }}"
      status: "deployed"
      version: "{{ app_version }}"
      timestamp: "{{ ansible_date_time.iso8601 }}"
  when: monitoring_webhook_url is defined
  listen: "notify deployment"
```

### 5. 角色测试和质量保证

#### 5.1 Molecule 测试框架
```yaml
# molecule/default/molecule.yml
---
dependency:
  name: galaxy
  options:
    requirements-file: requirements.yml

driver:
  name: docker

platforms:
  - name: instance-ubuntu20
    image: ubuntu:20.04
    pre_build_image: true
    command: /lib/systemd/systemd
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    privileged: true

  - name: instance-centos8
    image: centos:8
    pre_build_image: true
    command: /usr/sbin/init
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    privileged: true

provisioner:
  name: ansible
  config_options:
    defaults:
      callbacks_enabled: timer,profile_tasks
  inventory:
    host_vars:
      instance-ubuntu20:
        app_environment: "testing"
      instance-centos8:
        app_environment: "staging"

verifier:
  name: ansible

scenario:
  test_sequence:
    - dependency
    - lint
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - side_effect
    - verify
    - cleanup
    - destroy
```

#### 5.2 角色验证任务
```yaml
# molecule/default/verify.yml
---
- name: 验证角色部署结果
  hosts: all
  gather_facts: false
  tasks:
    - name: 检查应用服务状态
      service_facts:
      
    - name: 验证服务正在运行
      assert:
        that:
          - "'{{ app_service_name }}' in ansible_facts.services"
          - "ansible_facts.services['{{ app_service_name }}']['state'] == 'running'"
        fail_msg: "应用服务 {{ app_service_name }} 未正确启动"

    - name: 检查配置文件存在
      stat:
        path: "{{ app_config_file }}"
      register: config_file_stat

    - name: 验证配置文件存在
      assert:
        that:
          - config_file_stat.stat.exists
        fail_msg: "配置文件 {{ app_config_file }} 不存在"

    - name: 检查应用端口监听
      wait_for:
        port: "{{ app_port }}"
        host: "{{ app_host | default('localhost') }}"
        timeout: 30
      register: port_check

    - name: 验证应用响应
      uri:
        url: "http://{{ app_host | default('localhost') }}:{{ app_port }}/health"
        method: GET
        status_code: 200
      register: health_check
      ignore_errors: true

    - name: 显示健康检查结果
      debug:
        msg: "应用健康检查: {{ health_check.status if health_check.status is defined else '失败' }}"
```

#### 5.3 CI/CD 集成
```yaml
# .github/workflows/test.yml
name: Role Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
          
      - name: Install dependencies
        run: |
          pip install ansible ansible-lint yamllint
          
      - name: Lint Ansible role
        run: |
          ansible-lint .
          yamllint .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        distro: [ubuntu2004, centos8, debian10]
        
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
          
      - name: Install dependencies
        run: |
          pip install molecule[docker] docker
          
      - name: Test with molecule
        run: |
          molecule test
        env:
          PY_COLORS: '1'
          ANSIBLE_FORCE_COLOR: '1'
          MOLECULE_DISTRO: ${{ matrix.distro }}
```

### 6. 高级角色模式

#### 6.1 多层角色架构
```yaml
# 基础设施层角色
roles/
├── infrastructure/
│   ├── common/          # 基础系统配置
│   ├── security/        # 安全加固
│   └── monitoring/      # 基础监控

# 平台层角色
├── platform/
│   ├── web/            # Web 服务器平台
│   ├── database/       # 数据库平台
│   └── cache/          # 缓存平台

# 应用层角色
└── applications/
    ├── frontend/       # 前端应用
    ├── backend/        # 后端服务
    └── microservices/  # 微服务应用
```

#### 6.2 角色组合模式
```yaml
# playbooks/deploy-stack.yml
---
- name: 部署完整应用栈
  hosts: all
  vars:
    stack_environment: "{{ env | default('staging') }}"
    
  roles:
    # 基础设施层
    - role: infrastructure.common
      tags: [infra, common]
      
    - role: infrastructure.security
      tags: [infra, security]
      when: enable_security | default(true)
      
    - role: infrastructure.monitoring
      tags: [infra, monitoring]

    # 平台层 - 根据服务器角色应用
    - role: platform.web
      tags: [platform, web]
      when: "'web' in group_names"
      
    - role: platform.database
      tags: [platform, database]
      when: "'database' in group_names"
      
    - role: platform.cache
      tags: [platform, cache]
      when: "'cache' in group_names"

    # 应用层
    - role: applications.frontend
      tags: [app, frontend]
      when: "'web' in group_names"
      vars:
        app_environment: "{{ stack_environment }}"
        
    - role: applications.backend
      tags: [app, backend]
      when: "'app' in group_names"
      vars:
        app_environment: "{{ stack_environment }}"
```

#### 6.3 条件化角色应用
```yaml
# 根据变量动态选择角色
- name: 应用数据库角色
  include_role:
    name: "database.{{ database_type }}"
  vars:
    db_version: "{{ database_version }}"
  when: database_type in ['mysql', 'postgresql', 'mongodb']

# 循环应用多个角色
- name: 安装多个监控组件
  include_role:
    name: "monitoring.{{ item }}"
  loop:
    - prometheus
    - grafana
    - alertmanager
  when: monitoring_components is defined

# 基于条件的角色依赖
- name: 配置负载均衡器
  include_role:
    name: loadbalancer.nginx
  when: 
    - inventory_hostname in groups['web']
    - groups['web'] | length > 1
```

### 7. 企业级角色库管理

#### 7.1 角色版本管理
```yaml
# galaxy.yml - Galaxy 发布配置
---
namespace: company
name: webserver
version: 1.2.3
readme: README.md
authors:
  - DevOps Team <devops@company.com>
description: Enterprise web server configuration role
license:
  - MIT
license_file: LICENSE
tags:
  - web
  - nginx
  - enterprise
  - production

dependencies:
  company.common: ">=1.0.0"
  community.general: "*"

repository: https://github.com/company/ansible-role-webserver
documentation: https://docs.company.com/ansible-roles/webserver
homepage: https://github.com/company/ansible-role-webserver
issues: https://github.com/company/ansible-role-webserver/issues

build_ignore:
  - molecule/
  - .github/
  - tests/
  - "*.pyc"
  - .git/
```

#### 7.2 私有 Galaxy 服务器
```yaml
# ansible.cfg - 配置私有 Galaxy
[galaxy]
server_list = company_galaxy, public_galaxy

[galaxy_server.company_galaxy]
url = https://galaxy.company.com/
username = ansible_user
password = secure_password

[galaxy_server.public_galaxy]
url = https://galaxy.ansible.com/

# 使用私有服务器安装角色
ansible-galaxy install company.webserver --server company_galaxy
```

#### 7.3 角色发布流程
```bash
# 1. 开发和测试角色
molecule test

# 2. 更新版本和文档
vim galaxy.yml
vim CHANGELOG.md

# 3. 创建发布包
ansible-galaxy collection build

# 4. 发布到私有 Galaxy
ansible-galaxy collection publish company-webserver-1.2.3.tar.gz --server company_galaxy

# 5. 标记 Git 版本
git tag v1.2.3
git push origin v1.2.3
```

## 🔧 实际应用场景

### 场景1: Web 服务器角色设计
复杂的 Web 服务器配置，支持多种服务器类型和环境

### 场景2: 数据库管理角色
包含数据库安装、配置、备份和监控的完整解决方案

### 场景3: 应用部署角色
支持多环境、多版本的应用部署自动化

## 🎨 最佳实践

### 1. 角色设计原则
- **单一职责**：每个角色只负责一个特定功能
- **参数化**：提供足够的配置选项以适应不同环境
- **幂等性**：确保多次执行产生相同结果
- **文档化**：提供清晰的使用说明和示例
- **测试驱动**：使用自动化测试确保质量

### 2. 代码组织策略
- **模块化任务**：将复杂任务拆分为独立的文件
- **条件化执行**：使用条件和标签控制执行流程
- **变量管理**：合理使用默认值和环境特定变量
- **模板管理**：创建灵活且可维护的模板
- **处理器设计**：设计高效的服务管理处理器

## 📝 学习总结

通过 Day 7 的学习，您应该掌握：

1. **角色设计精通**
   - 理解角色的核心概念和架构
   - 掌握角色目录结构和最佳实践
   - 学会参数化和条件化设计

2. **Galaxy 应用能力**
   - 熟练使用 Ansible Galaxy 命令
   - 管理角色依赖和版本
   - 发布和分享自定义角色

3. **企业级开发技能**
   - 设计可重用的企业级角色
   - 实现复杂的角色组合和依赖
   - 建立角色测试和质量保证体系

4. **高级管理技巧**
   - 构建私有角色库
   - 实现角色版本管理
   - 建立 CI/CD 集成流程

## 🚀 下一步学习

**Day 8: 模块与插件开发** - 学习如何开发自定义 Ansible 模块和插件，扩展 Ansible 的功能以满足特定需求。

---

*Day 7 的学习为您提供了构建可重用、可维护、可扩展的 Ansible 代码的能力，这是企业级 Ansible 应用的关键技能。* 