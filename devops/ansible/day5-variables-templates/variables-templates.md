# Ansible 变量与模板 - Day 5

## 概述

Ansible 变量和模板是自动化配置管理的核心功能。变量允许您参数化配置，而模板则提供了动态生成配置文件的能力。

## 1. 变量基础

### 1.1 变量的定义与优先级

Ansible 变量可以从多个来源定义，优先级从高到低：

1. **命令行变量** (`-e` 或 `--extra-vars`)
2. **Playbook 中的变量**
3. **Inventory 变量** (主机变量、组变量)
4. **Facts 变量** (自动收集的系统信息)
5. **Role 默认变量**

### 1.2 变量定义方式

#### 在 Playbook 中定义变量

```yaml
---
- name: 变量定义示例
  hosts: webservers
  vars:
    http_port: 80
    max_clients: 200
    server_name: "web.example.com"
  
  tasks:
    - name: 显示变量值
      debug:
        msg: "服务器 {{ server_name }} 端口 {{ http_port }}"
```

#### 在 Inventory 中定义变量

```ini
[webservers]
web1.example.com http_port=8080 max_clients=300
web2.example.com http_port=9090 max_clients=400

[webservers:vars]
nginx_version=1.18
cache_size=512m
```

### 1.3 特殊变量

#### Facts 变量

```yaml
- name: 显示系统信息
  debug:
    msg: "主机名: {{ ansible_hostname }}, 操作系统: {{ ansible_os_family }}"
```

#### 魔法变量

```yaml
- name: 显示魔法变量
  debug:
    msg: |
      主机组: {{ group_names }}
      当前主机: {{ inventory_hostname }}
      Playbook 路径: {{ playbook_dir }}
```

## 2. 变量高级用法

### 2.1 变量注册与使用

```yaml
- name: 获取系统信息
  command: uname -r
  register: kernel_version

- name: 使用注册的变量
  debug:
    msg: "内核版本: {{ kernel_version.stdout }}"
```

### 2.2 变量文件

创建 `vars/main.yml`：

```yaml
---
app_name: "myapp"
app_version: "1.0.0"
database:
  host: "localhost"
  port: 5432
  name: "myapp_db"
```

在 Playbook 中使用：

```yaml
- name: 使用变量文件
  hosts: all
  vars_files:
    - vars/main.yml
  
  tasks:
    - name: 显示应用信息
      debug:
        msg: "应用 {{ app_name }} 版本 {{ app_version }}"
```

### 2.3 字典变量

```yaml
vars:
  users:
    alice:
      name: "Alice Smith"
      uid: 1001
      groups: "wheel"
    bob:
      name: "Bob Johnson"
      uid: 1002
      groups: "users"

tasks:
  - name: 创建用户
    user:
      name: "{{ item.key }}"
      comment: "{{ item.value.name }}"
      uid: "{{ item.value.uid }}"
      groups: "{{ item.value.groups }}"
    loop: "{{ users | dict2items }}"
```

## 3. Jinja2 模板基础

### 3.1 模板语法

Jinja2 是 Ansible 使用的模板引擎，支持：

- **变量插值**: `{{ variable }}`
- **控制结构**: `{% for %}`、`{% if %}`
- **过滤器**: `{{ variable | upper }}`

### 3.2 基本模板示例

创建 `templates/nginx.conf.j2`：

```jinja2
# {{ ansible_managed }}

server {
    listen {{ http_port }};
    server_name {{ server_name }};
    
    # 访问日志
    access_log /var/log/nginx/{{ app_name }}_access.log;
    error_log /var/log/nginx/{{ app_name }}_error.log;
    
    location / {
        root /var/www/{{ app_name }};
        index index.html index.htm;
    }
    
    # Gzip 压缩
    {% if enable_gzip %}
    gzip on;
    gzip_types text/plain text/css application/json;
    {% endif %}
    
    # SSL 配置
    {% if enable_ssl %}
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/{{ server_name }}.crt;
    ssl_certificate_key /etc/ssl/private/{{ server_name }}.key;
    {% endif %}
}
```

### 3.3 使用模板

```yaml
- name: 配置 Nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/sites-available/{{ app_name }}
    owner: root
    group: root
    mode: '0644'
  notify: restart nginx
```

## 4. 高级模板功能

### 4.1 条件语句

```jinja2
{% if ansible_os_family == "Debian" %}
# Debian 特定配置
apt-get update
{% elif ansible_os_family == "RedHat" %}
# RedHat 特定配置
yum update
{% else %}
# 其他系统
echo "Unsupported OS"
{% endif %}
```

### 4.2 循环语句

```jinja2
# 配置防火墙规则
{% for port in firewall_ports %}
-A INPUT -p tcp --dport {{ port }} -j ACCEPT
{% endfor %}

# 配置虚拟主机
{% for vhost in virtual_hosts %}
<VirtualHost *:80>
    ServerName {{ vhost.name }}
    DocumentRoot {{ vhost.docroot }}
</VirtualHost>
{% endfor %}
```

### 4.3 过滤器

```jinja2
# 字符串处理
应用名称: {{ app_name | upper }}
数据库连接: postgresql://{{ db_user }}:{{ db_password | urlencode }}@{{ db_host }}/{{ db_name }}

# 列表处理
允许的IP: {{ allowed_ips | join(",") }}

# 默认值
端口: {{ http_port | default(80) }}
```

## 5. 实战示例

### 5.1 应用部署配置

创建 `templates/app-config.yml.j2`：

```jinja2
# {{ ansible_managed }}

app:
  name: "{{ app_name }}"
  version: "{{ app_version }}"
  
server:
  host: "{{ server_host | default('0.0.0.0') }}"
  port: {{ server_port | default(8080) }}
  
database:
  host: "{{ db_host }}"
  port: {{ db_port | default(5432) }}
  name: "{{ db_name }}"
  username: "{{ db_user }}"
  password: "{{ db_password }}"
  
logging:
  level: "{{ log_level | default('INFO') }}"
  file: "/var/log/{{ app_name }}/app.log"
  
{% if enable_metrics %}
metrics:
  enabled: true
  port: {{ metrics_port | default(9090) }}
{% endif %}
```

### 5.2 数据库初始化脚本

创建 `templates/database-init.sql.j2`：

```jinja2
-- {{ ansible_managed }}

-- 创建数据库
CREATE DATABASE IF NOT EXISTS {{ db_name }};

-- 创建用户
CREATE USER IF NOT EXISTS '{{ db_user }}'@'%' IDENTIFIED BY '{{ db_password }}';

-- 授予权限
GRANT ALL PRIVILEGES ON {{ db_name }}.* TO '{{ db_user }}'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 使用数据库
USE {{ db_name }};

-- 创建表
{% for table in database_tables %}
CREATE TABLE IF NOT EXISTS {{ table.name }} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    {% for column in table.columns %}
    {{ column.name }} {{ column.type }}{% if not loop.last %},{% endif %}
    {% endfor %}
);
{% endfor %}
```

### 5.3 部署脚本模板

创建 `templates/deploy-script.sh.j2`：

```jinja2
#!/bin/bash
# {{ ansible_managed }}

set -e

# 变量定义
APP_NAME="{{ app_name }}"
APP_VERSION="{{ app_version }}"
DEPLOY_DIR="/opt/{{ app_name }}"
BACKUP_DIR="/var/backups/{{ app_name }}"

# 创建目录
mkdir -p $DEPLOY_DIR $BACKUP_DIR

# 备份现有版本
if [ -d "$DEPLOY_DIR/current" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp -r $DEPLOY_DIR/current $BACKUP_DIR/$TIMESTAMP
fi

# 部署新版本
cp -r /tmp/{{ app_name }}-{{ app_version }} $DEPLOY_DIR/
ln -sfn $DEPLOY_DIR/{{ app_name }}-{{ app_version }} $DEPLOY_DIR/current

# 配置权限
chown -R {{ app_user }}:{{ app_group }} $DEPLOY_DIR

# 重启服务
systemctl restart {{ app_name }}

echo "部署完成: $APP_NAME $APP_VERSION"
```

## 6. 最佳实践

### 6.1 变量组织

- 使用 `group_vars/` 和 `host_vars/` 目录组织变量
- 为不同环境创建不同的变量文件
- 使用 `vault` 加密敏感变量

### 6.2 模板管理

- 在模板开头使用 `{{ ansible_managed }}` 注释
- 为模板文件添加 `.j2` 扩展名
- 使用有意义的模板文件名

### 6.3 错误处理

```jinja2
{% if required_variable is defined %}
使用变量: {{ required_variable }}
{% else %}
{# 错误处理 #}
ERROR: required_variable 未定义
{% endif %}
```

## 7. 实用技巧

### 7.1 调试模板

```yaml
- name: 调试模板
  template:
    src: config.j2
    dest: /tmp/debug-config
    backup: yes
  
- name: 显示生成的配置
  debug:
    msg: "{{ lookup('file', '/tmp/debug-config') }}"
```

### 7.2 模板验证

```yaml
- name: 验证模板语法
  command: ansible -m template -a "src=config.j2 dest=/tmp/test" localhost
  changed_when: false
```

### 7.3 动态包含

```jinja2
{% for config_file in config_files %}
{% include config_file %}
{% endfor %}
```

## 总结

Ansible 变量和模板是自动化配置的强大工具。通过合理使用变量优先级、Jinja2 模板功能和最佳实践，您可以创建灵活、可维护的自动化解决方案。

记住：
- 保持变量组织有序
- 使用模板实现配置的动态生成
- 始终测试模板输出
- 遵循安全最佳实践