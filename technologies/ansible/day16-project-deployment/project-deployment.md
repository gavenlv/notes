# 项目部署实战详解

## 部署架构设计

### 应用架构
```
                    +------------------+
                    |   Load Balancer  |
                    +------------------+
                             |
        +--------------------+--------------------+
        |                                         |
+-------v--------+                     +----------v-------+
|  Web Server 1  |                     |  Web Server 2    |
| (10.0.1.10)    |                     | (10.0.1.11)      |
+-------+--------+                     +----------+-------+
        |                                         |
        +-------------------+---------------------+
                            |
                    +-------v-------+
                    |   Database    |
                    | (10.0.2.20)   |
                    +---------------+
```

### 部署流程
1. 预检检查
2. 备份当前版本
3. 部署新版本应用
4. 运行数据库迁移
5. 健康检查
6. 切换流量
7. 清理旧版本

## 多环境配置管理

### Inventory 结构
```ini
# inventory/production
[webservers]
web1.example.com ansible_host=10.0.1.10
web2.example.com ansible_host=10.0.1.11

[databases]
db1.example.com ansible_host=10.0.2.20

[monitoring]
monitor.example.com ansible_host=10.0.3.30

[all:vars]
env=production
app_version=1.2.3
```

### 环境变量配置
```yaml
# group_vars/production
app_name: "myapp"
app_port: 8080
db_host: "db1.example.com"
db_port: 5432
db_name: "myapp_prod"
db_user: "myapp_user"
```

## 滚动更新策略

### Playbook 示例
```yaml
---
- name: 滚动更新应用
  hosts: webservers
  serial: 1
  vars:
    backup_dir: "/var/backups/{{ app_name }}_{{ ansible_date_time.iso8601 }}"
  
  pre_tasks:
    - name: 创建备份目录
      file:
        path: "{{ backup_dir }}"
        state: directory
        mode: '0755'
        
    - name: 备份当前应用
      copy:
        src: "/var/www/{{ app_name }}/"
        dest: "{{ backup_dir }}/"
        remote_src: yes
  
  tasks:
    - name: 停止应用服务
      service:
        name: "{{ app_name }}"
        state: stopped
        
    - name: 部署新版本应用
      unarchive:
        src: "files/{{ app_name }}-{{ app_version }}.tar.gz"
        dest: "/var/www/"
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        
    - name: 应用配置文件
      template:
        src: "app.conf.j2"
        dest: "/etc/{{ app_name }}/app.conf"
      notify: reload app
        
    - name: 运行数据库迁移
      command: "/var/www/{{ app_name }}/bin/migrate.sh"
      when: inventory_hostname == groups['webservers'][0]
      
    - name: 启动应用服务
      service:
        name: "{{ app_name }}"
        state: started
        
    - name: 健康检查
      uri:
        url: "http://localhost:{{ app_port }}/health"
        method: GET
        status_code: 200
      retries: 10
      delay: 5
      
  handlers:
    - name: reload app
      service:
        name: "{{ app_name }}"
        state: reloaded
```

## 蓝绿部署策略

### 部署脚本
```bash
#!/bin/bash
# scripts/deploy.sh

ENV=${1:-staging}
VERSION=${2:-latest}

# 部署到绿色环境
ansible-playbook -i inventory/$ENV playbooks/deploy-green.yml \
  -e "app_version=$VERSION"

# 健康检查
ansible-playbook -i inventory/$ENV playbooks/health-check.yml \
  -e "target_environment=green"

# 如果健康检查通过，切换流量到绿色环境
if [ $? -eq 0 ]; then
  ansible-playbook -i inventory/$ENV playbooks/switch-traffic.yml \
    -e "target_environment=green"
    
  # 清理蓝色环境
  ansible-playbook -i inventory/$ENV playbooks/cleanup-blue.yml
else
  echo "Health check failed, rolling back"
  ansible-playbook -i inventory/$ENV playbooks/rollback.yml
fi
```

## 数据库迁移管理

### 数据库角色
```yaml
# roles/database/tasks/main.yml
---
- name: 备份数据库
  mysql_db:
    name: "{{ db_name }}"
    state: dump
    target: "/var/backups/{{ db_name }}_{{ ansible_date_time.iso8601 }}.sql"
  when: backup_before_migrate

- name: 应用数据库迁移
  mysql_db:
    name: "{{ db_name }}"
    state: import
    target: "files/migrations/{{ migration_version }}.sql"
    
- name: 验证数据库状态
  command: "mysql -u {{ db_user }} -p{{ db_password }} -e 'SHOW TABLES;' {{ db_name }}"
  register: db_tables
  changed_when: false
  
- name: 显示数据库表
  debug:
    msg: "Database tables: {{ db_tables.stdout_lines }}"
```

## 健康检查与监控

### 健康检查Playbook
```yaml
---
- name: 应用健康检查
  hosts: webservers
  tasks:
    - name: 检查HTTP服务
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:{{ app_port }}/health"
        method: GET
        status_code: 200
        timeout: 30
      register: health_check
      
    - name: 检查数据库连接
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:{{ app_port }}/db-health"
        method: GET
        status_code: 200
      register: db_check
      
    - name: 检查外部服务依赖
      uri:
        url: "{{ item }}"
        method: GET
        status_code: 200
        timeout: 10
      loop:
        - "https://api.payment.com/health"
        - "https://api.email.com/health"
      register: service_check
      ignore_errors: yes
      
    - name: 报告健康状态
      debug:
        msg: |
          Health Check Results:
          HTTP Service: {{ health_check.status }} 
          Database: {{ db_check.status }}
          External Services: {{ service_check.results | map(attribute='status') | list }}
```

## 自动回滚机制

### 回滚Playbook
```yaml
---
- name: 应用回滚
  hosts: webservers
  vars:
    rollback_version: "{{ rollback_to_version | default('previous') }}"
    
  tasks:
    - name: 确定回滚版本
      set_fact:
        target_version: "{{ hostvars[inventory_hostname]['previous_version'] }}"
      when: rollback_version == 'previous'
      
    - name: 停止当前应用
      service:
        name: "{{ app_name }}"
        state: stopped
        
    - name: 恢复备份的应用版本
      unarchive:
        src: "/var/backups/{{ app_name }}_{{ target_version }}.tar.gz"
        dest: "/var/www/"
        owner: "{{ app_user }}"
        group: "{{ app_group }}"
        
    - name: 恢复数据库备份
      mysql_db:
        name: "{{ db_name }}"
        state: import
        target: "/var/backups/{{ db_name }}_{{ target_version }}.sql"
      when: rollback_database
        
    - name: 启动应用服务
      service:
        name: "{{ app_name }}"
        state: started
        
    - name: 验证回滚结果
      uri:
        url: "http://localhost:{{ app_port }}/health"
        method: GET
        status_code: 200
```

## 部署监控与日志

### 监控集成
```yaml
---
- name: 部署监控代理
  hosts: all
  tasks:
    - name: 安装Prometheus Node Exporter
      package:
        name: prometheus-node-exporter
        state: present
        
    - name: 配置Node Exporter
      template:
        src: node-exporter.service.j2
        dest: /etc/systemd/system/node-exporter.service
        
    - name: 启动Node Exporter
      systemd:
        name: node-exporter
        state: started
        enabled: yes
        
    - name: 配置应用日志收集
      template:
        src: fluentd.conf.j2
        dest: /etc/fluentd/app.conf
        
    - name: 重启Fluentd
      service:
        name: fluentd
        state: restarted
```

## 最佳实践总结

1. **版本控制**: 所有配置和Playbook都应纳入版本控制
2. **测试环境**: 在生产环境部署前，先在测试环境验证
3. **备份策略**: 部署前务必备份应用和数据
4. **健康检查**: 部署后进行充分的健康检查
5. **回滚计划**: 始终准备好回滚方案
6. **监控告警**: 部署后持续监控应用状态
7. **文档记录**: 记录部署过程和遇到的问题