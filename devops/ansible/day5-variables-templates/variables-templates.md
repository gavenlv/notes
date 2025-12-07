# Ansible 变量与模板 - Day 5

## 概述

Ansible 变量和模板是自动化配置管理的核心功能。变量允许您参数化配置，而模板则提供了动态生成配置文件的能力。

**对于新手来说，理解变量和模板的概念很重要：**
- **变量**：就像编程中的变量，用于存储和重用值
- **模板**：就像带有占位符的文档，Ansible会用实际值替换这些占位符
- **Jinja2**：这是Ansible使用的模板引擎，类似于HTML模板但更强大

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

**代码解析（新手必读）：**
- `vars:` 关键字用于定义变量块
- `http_port: 80` 定义了一个名为 `http_port` 的变量，值为 80
- `server_name: "web.example.com"` 定义字符串变量，需要用引号包围
- `{{ server_name }}` 是变量引用语法，Ansible会将其替换为实际值
- `debug` 模块用于在运行时显示信息，非常适合调试

#### 在 Inventory 中定义变量

```ini
[webservers]
web1.example.com http_port=8080 max_clients=300
web2.example.com http_port=9090 max_clients=400

[webservers:vars]
nginx_version=1.18
cache_size=512m
```

**代码解析（新手必读）：**
- `[webservers]` 定义了一个主机组
- `web1.example.com http_port=8080` 为特定主机定义变量（主机变量）
- `[webservers:vars]` 为整个主机组定义变量（组变量）
- **优先级**：主机变量 > 组变量 > 默认变量
- **注意**：Inventory 变量适用于所有 Playbook，而 Playbook 变量只在该 Playbook 中有效

### 1.3 特殊变量

#### Facts 变量

```yaml
- name: 显示系统信息
  debug:
    msg: "主机名: {{ ansible_hostname }}, 操作系统: {{ ansible_os_family }}"
```

**代码解析（新手必读）：**
- **Facts** 是 Ansible 自动收集的系统信息
- `ansible_hostname` 是预定义变量，包含目标主机的主机名
- `ansible_os_family` 包含操作系统家族（如 Debian、RedHat）
- **使用场景**：根据不同的操作系统执行不同的任务
- **查看所有 Facts**：运行 `ansible hostname -m setup` 命令

#### 魔法变量

```yaml
- name: 显示魔法变量
  debug:
    msg: |
      主机组: {{ group_names }}
      当前主机: {{ inventory_hostname }}
      Playbook 路径: {{ playbook_dir }}
```

**代码解析（新手必读）：**
- **魔法变量** 是 Ansible 内部提供的特殊变量
- `group_names`：当前主机所属的所有组名列表
- `inventory_hostname`：Inventory 中定义的主机名
- `playbook_dir`：当前 Playbook 所在的目录路径
- **重要**：这些变量不需要定义，Ansible 会自动提供

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

**代码解析（新手必读）：**
- `register` 关键字用于将命令的输出保存到变量中
- `kernel_version` 是自定义的变量名，可以任意命名
- `kernel_version.stdout` 访问命令的标准输出
- **其他常用属性**：
  - `.stderr`：错误输出
  - `.rc`：返回代码（0表示成功）
  - `.changed`：任务是否改变了系统状态
- **重要**：注册的变量只在当前 Playbook 中有效

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

**代码解析（新手必读）：**
- 变量文件使用 YAML 格式，以 `---` 开头
- 支持嵌套结构：`database.host` 访问嵌套变量
- **文件位置**：通常放在 `vars/` 目录下
- **命名规范**：使用有意义的文件名，如 `main.yml`、`database.yml`

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

**代码解析（新手必读）：**
- `vars_files:` 关键字用于引入外部变量文件
- 可以引入多个文件：`- vars/main.yml`、`- vars/database.yml`
- **路径**：相对路径相对于 Playbook 文件位置
- **优点**：
  - 分离配置和数据
  - 便于版本控制
  - 支持环境特定的变量文件

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

**新手理解模板的关键点：**
- **模板文件**：以 `.j2` 结尾的文件，如 `nginx.conf.j2`
- **变量插值**：`{{ 变量名 }}` 会被替换为实际值
- **控制结构**：用于条件判断和循环
- **过滤器**：对变量值进行格式化处理
- **注释**：`{# 注释内容 #}` 不会被渲染到最终文件

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

**代码解析（新手必读）：**

**1. 变量插值部分：**
- `{{ http_port }}`：会被替换为实际的端口号（如 80 或 8080）
- `{{ server_name }}`：会被替换为实际的域名
- `{{ app_name }}`：会被替换为应用名称

**2. 条件语句部分：**
- `{% if enable_gzip %}`：如果 `enable_gzip` 变量为 true，则包含 Gzip 配置
- `{% if enable_ssl %}`：如果 `enable_ssl` 变量为 true，则包含 SSL 配置
- `{% endif %}`：结束条件块

**3. 特殊变量：**
- `{{ ansible_managed }}`：自动添加注释，说明文件由 Ansible 管理

**4. 模板工作原理：**
1. Ansible 读取模板文件
2. 替换所有 `{{ 变量 }}` 为实际值
3. 根据条件语句决定是否包含某些配置块
4. 生成最终的配置文件

**5. 变量定义示例：**
```yaml
vars:
  http_port: 80
  server_name: "example.com"
  app_name: "myapp"
  enable_gzip: true
  enable_ssl: false
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

**代码解析（新手必读）：**

**template 模块参数详解：**
- `src:` 模板文件路径（相对于 `templates/` 目录）
- `dest:` 生成的配置文件的目标路径
- `owner:` 文件所有者
- `group:` 文件所属组
- `mode:` 文件权限（0644 表示所有者可读写，其他用户只读）

**重要注意事项：**
1. **文件位置**：模板文件必须放在 `templates/` 目录下
2. **路径引用**：`src` 只需要文件名，Ansible 会自动在 `templates/` 目录中查找
3. **变量使用**：`dest` 路径中也可以使用变量
4. **通知机制**：`notify` 用于在文件改变时触发处理程序（handler）

**模板文件目录结构示例：**
```
project/
├── playbook.yml
├── templates/
│   └── nginx.conf.j2
└── vars/
    └── main.yml
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