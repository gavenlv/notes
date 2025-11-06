# Day 9: Ansible 高级特性应用

## 📚 学习目标

通过本天的学习，您将掌握：

- **异步任务处理**：async 和 poll 机制的应用
- **委托执行机制**：delegate_to 和 local_action 的使用
- **策略控制**：执行策略和并发控制技术
- **高级循环**：复杂的循环和批处理技术
- **动态任务**：运行时任务生成和执行
- **条件执行**：复杂条件逻辑和流程控制
- **性能优化**：大规模环境下的执行优化
- **错误处理**：高级错误处理和恢复机制

## 🎯 核心概念

### 1. 异步任务处理

#### async 和 poll 机制
```yaml
# 基本异步任务
- name: 长时间运行的任务
  command: /usr/bin/long_running_script
  async: 600  # 最大运行时间（秒）
  poll: 10    # 检查间隔（秒）

# 后台任务
- name: 后台启动服务
  command: /usr/bin/start_service
  async: 300
  poll: 0     # 不等待完成，立即返回

# 带条件的异步任务
- name: 条件异步任务
  command: /usr/bin/conditional_script
  async: 120
  poll: 5
  when: inventory_hostname in groups['servers']
```

#### 异步任务的最佳实践
```yaml
# 1. 合理设置超时时间
- name: 数据库备份
  command: /usr/bin/db_backup.sh
  async: 3600  # 1小时超时
  poll: 30     # 30秒检查一次

# 2. 错误处理
- name: 异步任务带错误处理
  command: /usr/bin/risky_operation
  async: 300
  poll: 10
  register: async_result
  failed_when: async_result.rc != 0

# 3. 任务状态检查
- name: 检查异步任务状态
  async_status:
    jid: "{{ async_result.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 30
  delay: 10
```

### 2. 委托执行机制

#### delegate_to 的使用
```yaml
# 在特定主机上执行任务
- name: 在负载均衡器上更新配置
  template:
    src: haproxy.cfg.j2
    dest: /etc/haproxy/haproxy.cfg
  delegate_to: "{{ groups['loadbalancers'][0] }}"
  notify: restart haproxy

# 在控制节点执行
- name: 在控制节点生成报告
  template:
    src: report.j2
    dest: /tmp/{{ inventory_hostname }}_report.html
  delegate_to: localhost
  run_once: true

# 条件委托
- name: 条件委托执行
  command: /usr/bin/update_config
  delegate_to: "{{ item }}"
  loop: "{{ groups['config_servers'] }}"
  when: inventory_hostname in groups['target_servers']
```

#### local_action 的使用
```yaml
# 本地操作
- name: 本地文件操作
  local_action:
    module: copy
    src: /local/path/file
    dest: /remote/path/file

# 简化的本地操作
- name: 简化的本地操作
  copy:
    src: /local/path/file
    dest: /remote/path/file
  delegate_to: localhost

# 本地命令执行
- name: 在控制节点执行命令
  local_action:
    module: shell
    cmd: "echo '{{ inventory_hostname }}' >> /tmp/hosts.log"
```

### 3. 策略控制

#### 执行策略
```yaml
# 线性执行策略
- name: 线性部署
  hosts: webservers
  strategy: linear
  serial: 2  # 每次2台服务器
  tasks:
    - name: 部署应用
      copy:
        src: app.war
        dest: /opt/app/

# 自由执行策略
- name: 并行部署
  hosts: webservers
  strategy: free
  tasks:
    - name: 并行部署
      copy:
        src: app.war
        dest: /opt/app/

# 调试策略
- name: 调试模式
  hosts: webservers
  strategy: debug
  tasks:
    - name: 调试任务
      debug:
        msg: "当前主机: {{ inventory_hostname }}"
```

#### 并发控制
```yaml
# 批量执行
- name: 批量更新
  hosts: all
  serial: "25%"  # 每次25%的主机
  tasks:
    - name: 系统更新
      yum:
        name: "*"
        state: latest

# 滚动更新
- name: 滚动更新
  hosts: webservers
  serial:
    - 1
    - 50%
    - 100%
  tasks:
    - name: 重启服务
      service:
        name: nginx
        state: restarted
```

### 4. 高级循环技术

#### 复杂循环
```yaml
# 嵌套循环
- name: 嵌套循环示例
  debug:
    msg: "服务器 {{ item[0] }} 上的服务 {{ item[1] }}"
  loop: "{{ groups['servers'] | product(groups['services']) }}"

# 条件循环
- name: 条件循环
  debug:
    msg: "处理 {{ item.name }}"
  loop: "{{ users }}"
  when: item.active and item.role == 'admin'

# 动态循环
- name: 动态循环
  debug:
    msg: "文件: {{ item }}"
  loop: "{{ lookup('fileglob', '/tmp/*.log') }}"
```

#### 循环控制
```yaml
# 循环标签
- name: 带标签的循环
  debug:
    msg: "处理用户 {{ item }}"
  loop: "{{ users }}"
  loop_control:
    label: "用户: {{ item }}"
    pause: 1  # 每次循环暂停1秒

# 循环变量
- name: 循环变量使用
  debug:
    msg: "{{ item }} - 索引: {{ index }}"
  loop: "{{ items }}"
  loop_control:
    index_var: index
    extended: yes
```

### 5. 动态任务生成

#### 运行时任务生成
```yaml
# 基于变量生成任务
- name: 动态任务生成
  include_tasks: dynamic_tasks.yml
  vars:
    task_list: "{{ dynamic_tasks }}"

# 条件任务包含
- name: 条件任务包含
  include_tasks: "{{ item }}.yml"
  loop:
    - "web_tasks"
    - "db_tasks"
    - "monitoring_tasks"
  when: item in enabled_modules
```

#### 模板任务
```yaml
# 使用模板生成任务
- name: 模板任务
  template:
    src: task_template.yml.j2
    dest: /tmp/generated_task.yml
  delegate_to: localhost

- name: 执行生成的任务
  include_tasks: /tmp/generated_task.yml
```

## 🛠️ 实践项目

### 项目1: 大规模部署系统

#### 需求分析
```yaml
# 大规模部署需求
部署目标:
  - 100+ 服务器
  - 多环境支持 (dev, test, prod)
  - 滚动更新策略
  - 健康检查机制
  - 回滚能力
  - 监控集成
```

#### 实现方案
```yaml
# 大规模部署 Playbook
---
- name: 大规模应用部署
  hosts: all
  strategy: linear
  serial: "{{ deployment_batch_size | default(5) }}"
  vars:
    deployment_batch_size: 10
    health_check_timeout: 300
    rollback_enabled: true
  
  pre_tasks:
    - name: 部署前检查
      include_tasks: pre_deployment_checks.yml
      
  tasks:
    - name: 备份当前版本
      include_tasks: backup_current_version.yml
      when: rollback_enabled
      
    - name: 停止服务
      include_tasks: stop_services.yml
      
    - name: 部署新版本
      include_tasks: deploy_new_version.yml
      
    - name: 健康检查
      include_tasks: health_check.yml
      
    - name: 启动服务
      include_tasks: start_services.yml
      
  post_tasks:
    - name: 部署后清理
      include_tasks: post_deployment_cleanup.yml
      
  handlers:
    - name: 回滚部署
      include_tasks: rollback_deployment.yml
```

### 项目2: 智能监控系统

#### 监控系统架构
```yaml
# 监控系统组件
监控组件:
  - 数据收集器 (异步任务)
  - 数据处理引擎 (委托执行)
  - 告警系统 (策略控制)
  - 报告生成器 (动态任务)
  - 仪表板更新 (高级循环)
```

#### 实现代码
```yaml
# 智能监控系统
---
- name: 数据收集阶段
  hosts: monitored_servers
  gather_facts: no
  
  tasks:
    - name: 异步收集系统指标
      include_tasks: collect_metrics.yml
      async: 300
      poll: 0
      
    - name: 异步收集应用指标
      include_tasks: collect_app_metrics.yml
      async: 600
      poll: 0
      
- name: 数据处理阶段
  hosts: monitoring_servers
  gather_facts: no
  
  tasks:
    - name: 处理收集的数据
      include_tasks: process_metrics.yml
      delegate_to: "{{ groups['data_processors'][0] }}"
      
    - name: 生成告警
      include_tasks: generate_alerts.yml
      delegate_to: "{{ groups['alert_servers'] }}"
      
- name: 报告生成阶段
  hosts: reporting_servers
  gather_facts: no
  
  tasks:
    - name: 生成日报
      include_tasks: generate_daily_report.yml
      delegate_to: localhost
      run_once: true
      
    - name: 更新仪表板
      include_tasks: update_dashboard.yml
      loop: "{{ dashboard_configs }}"
      loop_control:
        label: "更新仪表板: {{ item.name }}"
```

### 项目3: 自动化测试框架

#### 测试框架设计
```yaml
# 测试框架特性
框架特性:
  - 并行测试执行
  - 动态测试用例生成
  - 测试结果聚合
  - 失败重试机制
  - 性能基准测试
```

#### 实现示例
```yaml
# 自动化测试框架
---
- name: 准备测试环境
  hosts: test_servers
  gather_facts: no
  
  tasks:
    - name: 清理测试环境
      include_tasks: cleanup_test_env.yml
      
    - name: 准备测试数据
      include_tasks: prepare_test_data.yml
      
- name: 执行测试
  hosts: test_servers
  strategy: free
  gather_facts: no
  
  tasks:
    - name: 动态生成测试用例
      include_tasks: generate_test_cases.yml
      
    - name: 并行执行测试
      include_tasks: execute_tests.yml
      async: 1800  # 30分钟超时
      poll: 30
      
    - name: 收集测试结果
      include_tasks: collect_test_results.yml
      delegate_to: "{{ groups['test_coordinators'][0] }}"
      
- name: 生成测试报告
  hosts: reporting_servers
  gather_facts: no
  
  tasks:
    - name: 聚合测试结果
      include_tasks: aggregate_results.yml
      delegate_to: localhost
      
    - name: 生成测试报告
      include_tasks: generate_test_report.yml
      delegate_to: localhost
      run_once: true
```

## 🔧 高级技巧

### 1. 性能优化技巧

#### 并发优化
```yaml
# 优化并发执行
- name: 优化并发
  hosts: all
  strategy: free
  serial: "{{ ansible_play_hosts | length }}"
  
  tasks:
    - name: 并行任务
      command: /usr/bin/heavy_task
      async: 600
      poll: 0
```

#### 资源管理
```yaml
# 资源限制
- name: 资源限制任务
  hosts: all
  
  tasks:
    - name: 限制CPU使用
      command: /usr/bin/cpu_intensive_task
      environment:
        OMP_NUM_THREADS: "{{ ansible_processor_cores }}"
        
    - name: 限制内存使用
      command: /usr/bin/memory_intensive_task
      environment:
        JAVA_OPTS: "-Xmx2g -Xms1g"
```

### 2. 错误处理高级技巧

#### 复杂错误处理
```yaml
# 复杂错误处理
- name: 复杂错误处理
  hosts: all
  
  tasks:
    - name: 尝试主要操作
      block:
        - name: 主要任务
          command: /usr/bin/primary_task
        - name: 验证结果
          command: /usr/bin/verify_result
      rescue:
        - name: 记录错误
          debug:
            msg: "主要操作失败: {{ ansible_hostname }}"
        - name: 尝试备用方案
          command: /usr/bin/fallback_task
        - name: 验证备用方案
          command: /usr/bin/verify_fallback
      always:
        - name: 清理资源
          command: /usr/bin/cleanup
```

#### 重试机制
```yaml
# 智能重试
- name: 智能重试
  hosts: all
  
  tasks:
    - name: 重试任务
      command: /usr/bin/unreliable_task
      register: result
      until: result.rc == 0
      retries: 5
      delay: 10
      backoff: 2
```

### 3. 条件执行高级技巧

#### 复杂条件逻辑
```yaml
# 复杂条件
- name: 复杂条件执行
  hosts: all
  
  tasks:
    - name: 多条件任务
      command: /usr/bin/conditional_task
      when: >
        inventory_hostname in groups['webservers'] and
        ansible_os_family == "RedHat" and
        ansible_memtotal_mb > 4096 and
        custom_variable is defined
```

#### 动态条件
```yaml
# 动态条件
- name: 动态条件
  hosts: all
  
  tasks:
    - name: 基于变量条件
      command: /usr/bin/dynamic_task
      when: "{{ item }} in enabled_features"
      loop: "{{ available_features }}"
```

## 📊 性能监控

### 1. 执行时间监控
```yaml
# 执行时间监控
- name: 监控执行时间
  hosts: all
  
  tasks:
    - name: 记录开始时间
      set_fact:
        start_time: "{{ ansible_date_time.epoch }}"
        
    - name: 执行任务
      command: /usr/bin/task_to_monitor
      register: task_result
      
    - name: 计算执行时间
      set_fact:
        execution_time: "{{ (ansible_date_time.epoch | int) - (start_time | int) }}"
        
    - name: 报告执行时间
      debug:
        msg: "任务执行时间: {{ execution_time }} 秒"
```

### 2. 资源使用监控
```yaml
# 资源使用监控
- name: 监控资源使用
  hosts: all
  
  tasks:
    - name: 收集系统资源
      include_tasks: collect_resources.yml
      async: 300
      poll: 30
      
    - name: 分析资源使用
      include_tasks: analyze_resources.yml
      delegate_to: "{{ groups['monitoring_servers'][0] }}"
```

## 🧪 测试和验证

### 1. 高级特性测试
```yaml
# 测试异步任务
- name: 测试异步任务
  hosts: localhost
  gather_facts: no
  
  tasks:
    - name: 启动异步任务
      command: sleep 30
      async: 60
      poll: 5
      register: async_result
      
    - name: 检查任务状态
      async_status:
        jid: "{{ async_result.ansible_job_id }}"
      register: job_result
      until: job_result.finished
      retries: 10
      delay: 5
```

### 2. 性能基准测试
```yaml
# 性能基准测试
- name: 性能基准测试
  hosts: all
  
  tasks:
    - name: 基准测试
      include_tasks: benchmark_tests.yml
      async: 1800
      poll: 60
      
    - name: 收集基准结果
      include_tasks: collect_benchmark_results.yml
      delegate_to: localhost
```

## 🔍 故障排除

### 1. 常见问题解决

#### 异步任务问题
```yaml
# 异步任务故障排除
- name: 异步任务故障排除
  hosts: all
  
  tasks:
    - name: 检查异步任务状态
      async_status:
        jid: "{{ job_id }}"
      register: status_result
      
    - name: 处理失败的任务
      command: /usr/bin/recover_task
      when: status_result.failed
```

#### 委托执行问题
```yaml
# 委托执行故障排除
- name: 委托执行故障排除
  hosts: all
  
  tasks:
    - name: 检查目标主机连接
      ping:
      delegate_to: "{{ target_host }}"
      
    - name: 验证委托权限
      command: whoami
      delegate_to: "{{ target_host }}"
      register: user_result
```

### 2. 调试技巧
```yaml
# 高级调试
- name: 高级调试
  hosts: all
  
  tasks:
    - name: 启用详细输出
      debug:
        msg: "当前主机: {{ inventory_hostname }}"
        verbosity: 2
        
    - name: 检查变量
      debug:
        var: hostvars[inventory_hostname]
        verbosity: 1
```

## 📚 学习资源

### 1. 官方文档
- [Ansible 异步任务文档](https://docs.ansible.com/ansible/latest/user_guide/playbooks_async.html)
- [委托执行文档](https://docs.ansible.com/ansible/latest/user_guide/playbooks_delegation.html)
- [执行策略文档](https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html)

### 2. 最佳实践
- 合理使用异步任务避免长时间阻塞
- 谨慎使用委托执行确保安全性
- 根据环境选择合适的执行策略
- 建立完善的错误处理和监控机制

### 3. 扩展学习
- 学习 Ansible Tower/AWX 的高级特性
- 研究大规模部署的最佳实践
- 探索与其他工具的集成方案

## 🎓 总结

通过本天的学习，您已经掌握了：

1. **异步任务处理**：async 和 poll 机制的应用
2. **委托执行机制**：delegate_to 和 local_action 的使用
3. **策略控制**：执行策略和并发控制技术
4. **高级循环**：复杂的循环和批处理技术
5. **动态任务**：运行时任务生成和执行
6. **性能优化**：大规模环境下的执行优化
7. **错误处理**：高级错误处理和恢复机制

这些技能将帮助您：
- 处理大规模部署场景
- 优化 Ansible 执行性能
- 构建复杂的自动化流程
- 解决企业级应用中的复杂问题

**继续学习 Day 10: 错误处理与调试！** 🚀 