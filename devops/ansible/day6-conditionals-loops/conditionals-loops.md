# Day 6: 条件判断与循环高级应用

## 📚 学习目标

深入掌握 Ansible 中的条件判断和循环控制，包括：
- 复杂条件逻辑的构建和应用
- 多种循环类型的高级用法
- 条件与循环的组合使用技巧
- 错误处理和异常管理机制
- 动态任务执行策略
- 企业级场景的实际应用

## 🎯 核心概念

### 1. 条件判断 (Conditionals)

#### 1.1 基础条件语法
```yaml
# 简单条件判断
- name: 安装软件包 (仅在 Ubuntu 系统)
  apt:
    name: nginx
    state: present
  when: ansible_distribution == "Ubuntu"

# 多条件组合
- name: 配置服务 (生产环境且CPU核数大于4)
  service:
    name: nginx
    state: started
    enabled: yes
  when:
    - environment == "production"
    - ansible_processor_vcpus > 4
```

**语法解析**:
- **`when: ansible_distribution == "Ubuntu"`**: 使用 Ansible 事实变量 `ansible_distribution` 检查操作系统类型，仅在 Ubuntu 系统上执行任务
- **多条件列表语法**: 使用 YAML 列表格式定义多个条件，所有条件都必须满足（AND 逻辑）
- **条件表达式**: 支持比较运算符（`==`, `!=`, `>`, `<`, `>=`, `<=`）和逻辑运算符（`and`, `or`, `not`）
- **变量引用**: 可以直接引用 playbook 变量和 Ansible 事实变量

**应用场景**:
- 操作系统特定的软件包安装
- 环境特定的配置管理
- 硬件资源相关的条件执行

#### 1.2 高级条件表达式
```yaml
# 逻辑运算符
- name: 复杂逻辑条件
  debug:
    msg: "满足复杂条件"
  when: >
    (ansible_distribution == "Ubuntu" and ansible_distribution_version >= "18.04") or
    (ansible_distribution == "CentOS" and ansible_distribution_major_version >= "7")

# 正则表达式匹配
- name: 检查服务名称模式
  service:
    name: "{{ item }}"
    state: started
  when: item is match("^web.*")
  loop: "{{ services_list }}"

# 变量存在性检查
- name: 仅在变量已定义时执行
  debug:
    msg: "数据库URL: {{ database_url }}"
  when: database_url is defined

# 变量类型检查
- name: 处理字符串类型配置
  template:
    src: config.j2
    dest: /etc/app/config.yaml
  when: app_config is string

# 文件存在性检查
- name: 备份现有配置
  copy:
    src: /etc/nginx/nginx.conf
    dest: /etc/nginx/nginx.conf.backup
  when: ansible_stat.stat.exists
  vars:
    ansible_stat: "{{ ansible_stat_result }}"
```

**语法解析**:
- **多行条件表达式**: 使用 `>` YAML 折叠标量语法处理复杂的多行条件逻辑
- **正则表达式测试**: `is match("^web.*")` 使用 Jinja2 的 match 过滤器检查字符串模式匹配
- **变量检查测试**: `is defined` 检查变量是否已定义，`is string` 检查变量类型
- **文件状态检查**: 使用 `ansible_stat` 模块获取文件状态，通过 `stat.exists` 属性判断文件存在性
- **组合逻辑**: 支持复杂的 AND/OR 逻辑组合，使用括号明确优先级

**高级特性**:
- **类型安全**: 通过变量类型检查避免运行时错误
- **模式匹配**: 支持正则表达式用于灵活的字符串匹配
- **状态感知**: 结合模块结果进行条件判断
- **可读性**: 复杂条件使用多行格式提高可读性

#### 1.3 条件注册和重用
```yaml
# 注册条件结果
- name: 检查服务状态
  service_facts:
  register: service_status

- name: 根据服务状态执行操作
  debug:
    msg: "Nginx 正在运行"
  when: "'nginx' in service_status.ansible_facts.services and 
         service_status.ansible_facts.services['nginx']['state'] == 'running'"

# 条件变量设置
- name: 设置环境特定的端口
  set_fact:
    app_port: >-
      {% if environment == 'production' %}
        80
      {% elif environment == 'staging' %}
        8080
      {% else %}
        3000
      {% endif %}

- name: 使用动态端口配置
  template:
    src: app.conf.j2
    dest: /etc/app/app.conf
  notify: restart app
```

**语法解析**:
- **注册变量机制**: `register: service_status` 将模块执行结果保存到变量中供后续任务使用
- **嵌套属性访问**: `service_status.ansible_facts.services['nginx']['state']` 访问注册变量的深层嵌套属性
- **Jinja2 条件表达式**: 在 `set_fact` 中使用 `{% if %}` 条件块进行动态变量赋值
- **多行字符串**: 使用 `>-` YAML 折叠标量语法处理多行 Jinja2 模板

**设计模式**:
- **状态驱动**: 基于前一个任务的结果决定后续任务执行
- **动态配置**: 根据环境变量动态生成配置参数
- **条件复用**: 将复杂条件逻辑封装在变量中提高可维护性
- **通知机制**: 配置变更后自动触发处理程序重启服务

### 2. 循环控制 (Loops)

#### 2.1 基础循环类型

**简单列表循环**
```yaml
# 基础 loop
- name: 安装多个软件包
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql-server
    - redis-server
    - git

# 使用变量列表
- name: 创建多个用户
  user:
    name: "{{ item }}"
    shell: /bin/bash
    create_home: yes
  loop: "{{ user_list }}"
```

**语法解析**:
- **`loop` 指令**: 替代传统的 `with_items`，是 Ansible 2.5+ 推荐的循环语法
- **内联列表**: 直接在 `loop` 中定义 YAML 列表进行循环
- **变量引用**: `loop: "{{ user_list }}"` 引用外部定义的列表变量
- **`item` 变量**: 在每次循环迭代中自动设置为当前列表项

**循环特性**:
- **顺序执行**: 循环项按列表顺序依次执行
- **独立上下文**: 每次循环都是独立的，不会相互影响
- **错误处理**: 默认情况下，单个循环项失败会停止整个 playbook
- **变量作用域**: `item` 变量仅在当前任务内有效

**字典循环**
```yaml
# 循环字典
- name: 配置多个虚拟主机
  template:
    src: vhost.conf.j2
    dest: "/etc/nginx/sites-available/{{ item.key }}"
  loop: "{{ vhosts | dict2items }}"
  vars:
    vhosts:
      site1:
        server_name: example.com
        document_root: /var/www/site1
      site2:
        server_name: test.example.com
        document_root: /var/www/site2

# 循环复杂字典结构
- name: 配置数据库用户
  mysql_user:
    name: "{{ item.username }}"
    password: "{{ item.password }}"
    priv: "{{ item.privileges }}"
    host: "{{ item.host | default('localhost') }}"
  loop:
    - username: app_user
      password: "{{ app_user_password }}"
      privileges: "app_db.*:ALL"
      host: "%"
    - username: readonly_user
      password: "{{ readonly_password }}"
      privileges: "app_db.*:SELECT"
```

**语法解析**:
- **字典转列表**: `dict2items` 过滤器将字典转换为 `{key: key, value: value}` 结构的列表
- **复杂数据结构**: 循环项可以是包含多个属性的字典对象
- **属性访问**: `item.username`、`item.password` 访问字典对象的属性
- **默认值处理**: `default('localhost')` 过滤器为可选属性提供默认值

**数据结构设计**:
- **键值对映射**: 使用字典结构表示配置对象集合
- **嵌套属性**: 支持多层嵌套的复杂数据结构
- **模板化配置**: 结合模板引擎实现动态配置生成
- **参数化设计**: 将配置参数与执行逻辑分离

#### 2.2 高级循环技术

**嵌套循环**
```yaml
# 多层嵌套循环
- name: 为每个用户在每个服务器上创建SSH密钥
  authorized_key:
    user: "{{ item.0.username }}"
    key: "{{ item.1 }}"
  loop: "{{ users | product(ssh_keys) | list }}"
  vars:
    users:
      - username: alice
      - username: bob
    ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... alice@workstation"
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... bob@workstation"

# 服务器和服务的组合循环
- name: 在每个服务器上配置每个服务
  template:
    src: "{{ item.1 }}.conf.j2"
    dest: "/etc/{{ item.1 }}/{{ item.0.hostname }}.conf"
  loop: "{{ servers | product(services) | list }}"
  when: item.1 in item.0.required_services
```

**条件循环**
```yaml
# 带条件的循环
- name: 安装环境特定的软件包
  package:
    name: "{{ item.name }}"
    state: present
  loop:
    - name: nginx
      environments: ["production", "staging"]
    - name: redis
      environments: ["production"]
    - name: nodejs
      environments: ["development", "staging"]
  when: environment in item.environments

# 循环中的复杂条件
- name: 配置服务 (基于服务器角色和环境)
  service:
    name: "{{ item }}"
    state: started
    enabled: yes
  loop: "{{ services_by_role[server_role] | default([]) }}"
  when:
    - server_role is defined
    - item not in disabled_services | default([])
    - environment in ['production', 'staging'] or item in development_services | default([])
```

#### 2.3 循环控制和优化

**循环变量和索引**
```yaml
# 使用循环变量
- name: 创建配置文件 (带索引)
  template:
    src: config.j2
    dest: "/etc/app/config_{{ ansible_loop.index }}.yaml"
  loop: "{{ config_templates }}"
  loop_control:
    index_var: config_index
    loop_var: config_item

# 扩展循环信息
- name: 显示循环进度
  debug:
    msg: >
      处理第 {{ ansible_loop.index }} 项 (共 {{ ansible_loop.length }} 项):
      {{ item.name }}
      {% if ansible_loop.first %}这是第一项{% endif %}
      {% if ansible_loop.last %}这是最后一项{% endif %}
  loop: "{{ deployment_items }}"
```

**循环性能优化**
```yaml
# 并行循环执行
- name: 并行下载文件
  get_url:
    url: "{{ item.url }}"
    dest: "{{ item.dest }}"
    mode: '0644'
  loop: "{{ download_files }}"
  async: 300
  poll: 0
  register: download_jobs

- name: 等待所有下载完成
  async_status:
    jid: "{{ item.ansible_job_id }}"
  loop: "{{ download_jobs.results }}"
  register: download_results
  until: download_results.finished
  retries: 30
  delay: 10

# 批量处理优化
- name: 批量创建用户 (使用模块的批量功能)
  user:
    name: "{{ item }}"
    shell: /bin/bash
  loop: "{{ user_list }}"
  # 替换为更高效的方法:
  when: false

- name: 高效批量用户创建
  script: batch_create_users.sh
  args:
    stdin: "{{ user_list | join('\n') }}"
```

### 3. 错误处理和流程控制

#### 3.1 错误处理策略
```yaml
# 基础错误处理
- name: 尝试启动服务
  service:
    name: "{{ item }}"
    state: started
  loop: "{{ services }}"
  ignore_errors: yes
  register: service_results

- name: 报告失败的服务
  debug:
    msg: "服务 {{ item.item }} 启动失败: {{ item.msg }}"
  loop: "{{ service_results.results }}"
  when: item.failed | default(false)

# 条件性错误处理
- name: 安装软件包 (允许部分失败)
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ required_packages + optional_packages }}"
  failed_when: >
    item in required_packages and 
    ansible_failed_result.rc != 0
  ignore_errors: "{{ item in optional_packages }}"
```

**语法解析**:
- **`ignore_errors: yes`**: 忽略任务执行过程中的错误，继续执行后续任务
- **循环结果注册**: `register: service_results` 保存循环执行的所有结果
- **失败项过滤**: `when: item.failed | default(false)` 仅处理失败的循环项
- **动态错误忽略**: `ignore_errors: "{{ item in optional_packages }}"` 根据条件动态决定是否忽略错误
- **自定义失败条件**: `failed_when` 定义任务失败的自定义条件

**错误处理策略**:
- **优雅降级**: 允许非关键任务失败而不中断整个流程
- **结果分析**: 收集所有执行结果进行事后分析
- **条件性容错**: 根据任务重要性决定错误处理策略
- **失败报告**: 提供详细的错误信息用于问题诊断

#### 3.2 流程控制机制
```yaml
# 早期退出策略
- name: 检查系统兼容性
  fail:
    msg: "不支持的操作系统: {{ ansible_distribution }}"
  when: ansible_distribution not in supported_os_list

# 条件性任务块
- block:
    - name: 配置生产环境服务
      service:
        name: "{{ item }}"
        state: started
        enabled: yes
      loop: "{{ production_services }}"
    
    - name: 配置生产环境监控
      template:
        src: monitoring.conf.j2
        dest: /etc/monitoring/config.conf
  
  rescue:
    - name: 生产环境配置失败，回滚
      service:
        name: "{{ item }}"
        state: stopped
      loop: "{{ production_services }}"
      ignore_errors: yes
    
    - name: 发送告警通知
      mail:
        to: admin@company.com
        subject: "生产环境部署失败"
        body: "服务器 {{ inventory_hostname }} 的生产环境配置失败"
  
  always:
    - name: 记录部署日志
      lineinfile:
        path: /var/log/deployment.log
        line: "{{ ansible_date_time.iso8601 }}: 生产环境部署尝试完成"
  
  when: environment == "production"
```

### 4. 动态任务生成

#### 4.1 基于条件的任务动态生成
```yaml
# 动态包含任务
- name: 根据操作系统包含相应任务
  include_tasks: "{{ ansible_distribution | lower }}.yml"
  when: ansible_distribution | lower + '.yml' in available_os_tasks

# 动态角色分配
- name: 应用服务器角色配置
  include_role:
    name: "{{ item }}"
  loop: "{{ server_roles }}"
  when: 
    - item in available_roles
    - hostvars[inventory_hostname]['role_' + item + '_enabled'] | default(false)

# 条件性变量设置
- name: 设置环境特定变量
  set_fact:
    "{{ item.key }}": "{{ item.value }}"
  loop: "{{ environment_configs[environment] | dict2items }}"
  when: item.key not in ansible_facts
```

#### 4.2 复杂场景应用
```yaml
# 多环境部署策略
- name: 确定部署策略
  set_fact:
    deployment_strategy: >-
      {% if environment == 'production' %}
        {% if deployment_type == 'rolling' %}
          rolling_update
        {% elif deployment_type == 'blue_green' %}
          blue_green
        {% else %}
          standard
        {% endif %}
      {% elif environment == 'staging' %}
        quick_deploy
      {% else %}
        development
      {% endif %}

- name: 执行相应的部署策略
  include_tasks: "deploy_{{ deployment_strategy }}.yml"

# 基于负载的资源分配
- name: 动态调整服务配置
  template:
    src: "{{ item.template }}"
    dest: "{{ item.dest }}"
  loop:
    - template: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
      condition: "'web' in server_roles"
    - template: mysql.cnf.j2
      dest: /etc/mysql/mysql.conf.d/custom.cnf
      condition: "'database' in server_roles"
    - template: redis.conf.j2
      dest: /etc/redis/redis.conf
      condition: "'cache' in server_roles"
  when: item.condition | bool
  notify: "restart {{ item.template | regex_replace('\\.conf\\.j2$', '') }}"
```

## 🔧 实际应用场景

### 场景1: 多环境自动化部署
```yaml
---
- name: 智能部署系统
  hosts: all
  vars:
    environments:
      development:
        deploy_method: direct
        health_check: false
        backup: false
        rollback_enabled: false
      staging:
        deploy_method: rolling
        health_check: true
        backup: true
        rollback_enabled: true
      production:
        deploy_method: blue_green
        health_check: true
        backup: true
        rollback_enabled: true
        approval_required: true

  tasks:
    - name: 验证部署前置条件
      block:
        - name: 检查环境配置
          fail:
            msg: "环境 {{ environment }} 不在支持列表中"
          when: environment not in environments.keys()

        - name: 生产环境需要审批
          pause:
            prompt: "确认部署到生产环境? (yes/no)"
          register: approval
          when: environments[environment].approval_required | default(false)

        - name: 验证审批结果
          fail:
            msg: "部署被取消"
          when: 
            - environments[environment].approval_required | default(false)
            - approval.user_input | lower != 'yes'

    - name: 执行部署前备份
      block:
        - name: 备份当前版本
          archive:
            path: "{{ app_directory }}"
            dest: "{{ backup_directory }}/{{ ansible_date_time.epoch }}_{{ app_version }}.tar.gz"
          register: backup_result

        - name: 记录备份信息
          lineinfile:
            path: "{{ backup_directory }}/backup_history.log"
            line: "{{ ansible_date_time.iso8601 }}: {{ backup_result.dest }}"
      when: environments[environment].backup | default(false)

    - name: 根据环境选择部署方法
      include_tasks: "deploy_{{ environments[environment].deploy_method }}.yml"

    - name: 执行健康检查
      uri:
        url: "http://{{ inventory_hostname }}:{{ app_port }}/health"
        method: GET
        status_code: 200
      register: health_check
      retries: 5
      delay: 10
      when: environments[environment].health_check | default(false)

    - name: 部署后清理
      block:
        - name: 清理旧版本
          file:
            path: "{{ item }}"
            state: absent
          loop: "{{ old_versions.files | map(attribute='path') | list }}"
          vars:
            old_versions: "{{ ansible_find_result }}"

        - name: 重启相关服务
          service:
            name: "{{ item }}"
            state: restarted
          loop: "{{ services_to_restart }}"
          when: deployment_requires_restart | default(true)
      when: health_check is not failed
```

### 场景2: 动态服务器配置管理
```yaml
---
- name: 动态服务器配置管理
  hosts: all
  vars:
    server_configs:
      web:
        packages:
          - nginx
          - php-fpm
        services:
          - nginx
          - php7.4-fpm
        ports:
          - 80
          - 443
        config_templates:
          - nginx.conf.j2
          - php.ini.j2
      database:
        packages:
          - mysql-server
          - mysql-client
        services:
          - mysql
        ports:
          - 3306
        config_templates:
          - my.cnf.j2
      cache:
        packages:
          - redis-server
        services:
          - redis
        ports:
          - 6379
        config_templates:
          - redis.conf.j2

  tasks:
    - name: 检测服务器角色
      set_fact:
        detected_roles: []

    - name: 基于主机名检测角色
      set_fact:
        detected_roles: "{{ detected_roles + [item] }}"
      loop:
        - web
        - database
        - cache
      when: item in inventory_hostname

    - name: 基于服务检测角色
      set_fact:
        detected_roles: "{{ detected_roles + [item.key] }}"
      loop: "{{ server_configs | dict2items }}"
      when: 
        - item.value.services is defined
        - item.value.services | intersect(ansible_facts.services.keys()) | length > 0

    - name: 显示检测到的角色
      debug:
        msg: "检测到服务器角色: {{ detected_roles | unique }}"

    - name: 安装角色相关软件包
      package:
        name: "{{ item.1 }}"
        state: present
      loop: "{{ detected_roles | unique | product(item_packages) | list }}"
      vars:
        item_packages: "{{ server_configs[item.0].packages | default([]) }}"
      when: detected_roles | length > 0

    - name: 配置服务
      service:
        name: "{{ item.1 }}"
        state: started
        enabled: yes
      loop: "{{ detected_roles | unique | product(item_services) | list }}"
      vars:
        item_services: "{{ server_configs[item.0].services | default([]) }}"
      when: detected_roles | length > 0

    - name: 生成配置文件
      template:
        src: "{{ item.1 }}"
        dest: "/etc/{{ item.0 }}/{{ item.1 | regex_replace('\\.j2$', '') }}"
      loop: "{{ detected_roles | unique | product(item_templates) | list }}"
      vars:
        item_templates: "{{ server_configs[item.0].config_templates | default([]) }}"
      when: detected_roles | length > 0
      notify: "restart {{ item.0 }} services"

    - name: 配置防火墙
      ufw:
        rule: allow
        port: "{{ item.1 }}"
        proto: tcp
      loop: "{{ detected_roles | unique | product(item_ports) | list }}"
      vars:
        item_ports: "{{ server_configs[item.0].ports | default([]) }}"
      when: 
        - detected_roles | length > 0
        - ansible_distribution == "Ubuntu"
```

## 🎨 最佳实践

### 1. 条件判断最佳实践
- **保持条件简洁**: 避免过于复杂的条件表达式
- **使用变量**: 将复杂条件逻辑封装在变量中
- **文档化条件**: 为复杂条件添加注释说明
- **测试边界情况**: 确保条件在各种边界情况下都能正确工作

### 2. 循环优化策略
- **避免嵌套过深**: 超过3层的嵌套循环应该重构
- **使用批量操作**: 优先使用模块的批量功能而非循环
- **异步处理**: 对于耗时操作使用异步执行
- **合理使用索引**: 仅在必要时使用循环索引

### 3. 错误处理准则
- **预期失败**: 为可能失败的操作准备错误处理
- **优雅降级**: 设计系统在部分功能失败时仍能运行
- **详细日志**: 记录足够的信息用于问题诊断
- **清理机制**: 确保失败后能够正确清理资源

### 4. 性能优化建议
- **条件前置**: 将最可能为false的条件放在前面
- **缓存结果**: 对于重复计算的条件结果进行缓存
- **并行执行**: 利用异步和并行特性提高执行效率
- **资源管理**: 合理管理内存和连接资源

## 📝 学习总结

通过 Day 6 的学习，您应该掌握：

1. **条件判断高级技巧**
   - 复杂逻辑表达式构建
   - 条件变量和动态判断
   - 错误处理和异常管理

2. **循环控制精通**
   - 多种循环类型的灵活应用
   - 嵌套循环和条件循环
   - 循环性能优化技术

3. **企业级应用能力**
   - 多环境部署策略
   - 动态配置管理
   - 智能任务调度

4. **最佳实践应用**
   - 代码可读性和可维护性
   - 性能优化和资源管理
   - 错误处理和恢复机制

## 🚀 下一步学习

**Day 7: 角色与 Galaxy 高级应用** - 学习如何创建可重用的角色，使用 Ansible Galaxy，以及构建企业级角色库。

---

*Day 6 的学习为您提供了 Ansible 中最重要的控制流程技能，这些技能是构建复杂自动化系统的基础。* 