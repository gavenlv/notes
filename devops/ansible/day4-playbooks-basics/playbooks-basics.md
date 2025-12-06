# Day 4: Ansible Playbooks 基础

## 学习目标

- 深入理解 Playbook 的结构和语法
- 掌握 Tasks、Plays 和 Playbooks 的关系
- 学习常用模块的实际应用
- 通过实际例子掌握 Playbook 编写技巧
- 理解变量、facts 和条件判断的使用

## 什么是 Playbook

Playbook 是 Ansible 的核心功能，它是一个 YAML 文件，包含了要在远程主机上执行的任务列表。

### Playbook 的基本结构

```yaml
---
- name: "Play 的描述"
  hosts: target_hosts
  become: yes
  gather_facts: yes
  vars:
    variable_name: value
  tasks:
    - name: "任务描述"
      module_name:
        parameter: value
```

**语法解析:**
- `---`: YAML 文件的开头标记，表示这是一个 YAML 文档
- `- name: "Play 的描述"`: Play 的名称，用于描述这个 Play 的作用
- `hosts: target_hosts`: 指定目标主机或主机组，可以是 inventory 中定义的主机组名或单个主机
- `become: yes`: 表示使用特权提升（sudo 权限）执行任务
- `gather_facts: yes`: 收集目标主机的系统信息（facts）
- `vars:`: 定义变量部分
- `tasks:`: 任务列表，包含要执行的具体操作

### 核心概念

1. **Play**: 一个 playbook 中的一个执行单元，包含一组相关的任务
2. **Task**: Play 中的具体操作，每个任务调用一个 Ansible 模块
3. **Module**: 执行具体操作的模块，如 file、copy、service 等
4. **Handler**: 响应通知的特殊任务，通常用于服务重启等操作

## 实践练习 1: 基础 Playbook

### 示例 1.1: 简单的系统信息收集

```yaml
---
- name: "收集系统信息"
  hosts: all
  gather_facts: yes
  tasks:
    - name: "显示操作系统信息"
      debug:
        msg: "主机 {{ inventory_hostname }} 运行的是 {{ ansible_os_family }} {{ ansible_distribution_version }}"
    
    - name: "显示内存信息"
      debug:
        msg: "总内存: {{ ansible_memtotal_mb }}MB, 可用内存: {{ ansible_memfree_mb }}MB"
```

**模块解析:**
- **debug 模块**: 用于调试和显示信息
  - `msg`: 参数，显示自定义消息
  - 使用 Jinja2 模板语法 `{{ }}` 引用变量

**变量解析:**
- `{{ inventory_hostname }}`: 当前主机的 inventory 名称
- `{{ ansible_os_family }}`: 操作系统家族（如 Debian、RedHat）
- `{{ ansible_distribution_version }}`: 操作系统版本
- `{{ ansible_memtotal_mb }}`: 总内存大小（MB）
- `{{ ansible_memfree_mb }}`: 可用内存大小（MB）

**语法说明:**
- `gather_facts: yes`: 启用事实收集，自动获取系统信息
- `hosts: all`: 对所有主机执行
- 每个任务都有 `name` 字段，用于描述任务作用

### 示例 1.2: 文件和目录操作

```yaml
---
- name: "文件和目录管理示例"
  hosts: web_servers
  become: yes
  tasks:
    - name: "创建应用目录"
      file:
        path: /opt/myapp
        state: directory
        owner: root
        group: root
        mode: '0755'
    
    - name: "创建配置文件"
      copy:
        content: |
          # 应用配置文件
          app_name=MyApplication
          version=1.0.0
          debug=false
        dest: /opt/myapp/config.conf
        owner: root
        group: root
        mode: '0644'
    
    - name: "创建日志目录"
      file:
        path: /var/log/myapp
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'
```

**模块解析:**
- **file 模块**: 用于文件和目录管理
  - `path`: 文件或目录的路径
  - `state`: 状态，`directory` 表示创建目录，`absent` 表示删除
  - `owner`: 文件所有者
  - `group`: 文件所属组
  - `mode`: 文件权限，八进制格式

- **copy 模块**: 用于复制文件或创建文件内容
  - `content: |`: YAML 多行字符串语法，`|` 表示保留换行符
  - `dest`: 目标文件路径
  - `owner`, `group`, `mode`: 文件权限设置

**语法说明:**
- `become: yes`: 使用 sudo 权限执行任务
- `hosts: web_servers`: 只对 web_servers 主机组执行
- `content: |` 语法：`|` 表示保留所有换行符，`>` 表示折叠换行符
- 权限模式：`0755` 表示 rwxr-xr-x，`0644` 表示 rw-r--r--

## 实践练习 2: 软件包管理

### 示例 2.1: 多系统软件包安装

```yaml
---
- name: "跨平台软件包安装"
  hosts: all
  become: yes
  tasks:
    - name: "安装基础软件包 (Ubuntu/Debian)"
      apt:
        name:
          - nginx
          - git
          - curl
          - vim
        state: present
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: "安装基础软件包 (CentOS/RHEL)"
      yum:
        name:
          - nginx
          - git
          - curl
          - vim
        state: present
      when: ansible_os_family == "RedHat"
    
    - name: "启动并启用 nginx 服务"
      service:
        name: nginx
        state: started
        enabled: yes
```

**模块解析:**
- **apt 模块**: Debian/Ubuntu 系统的包管理器
  - `name`: 包名，可以是单个包或列表
  - `state: present`: 确保包已安装
  - `update_cache: yes`: 更新包缓存（相当于 apt update）

- **yum 模块**: RedHat/CentOS 系统的包管理器
  - `name`: 包名列表
  - `state: present`: 确保包已安装

- **service 模块**: 服务管理
  - `name`: 服务名称
  - `state: started`: 确保服务正在运行
  - `enabled: yes`: 设置服务开机自启

**语法说明:**
- `when: ansible_os_family == "Debian"`: 条件判断，只在 Debian 系统上执行
- `name:` 后跟列表语法，使用 `-` 表示列表项
- 条件判断使用 Jinja2 表达式语法
- 跨平台兼容性：通过条件判断实现不同系统的适配

### 示例 2.2: 从源码编译安装

```yaml
---
- name: "从源码编译安装软件"
  hosts: build_servers
  become: yes
  vars:
    app_version: "1.2.3"
    build_dir: "/tmp/myapp-build"
  tasks:
    - name: "安装编译依赖"
      apt:
        name:
          - build-essential
          - cmake
          - libssl-dev
        state: present
      when: ansible_os_family == "Debian"
    
    - name: "创建构建目录"
      file:
        path: "{{ build_dir }}"
        state: directory
    
    - name: "下载源代码"
      get_url:
        url: "https://github.com/example/myapp/archive/v{{ app_version }}.tar.gz"
        dest: "{{ build_dir }}/myapp-{{ app_version }}.tar.gz"
    
    - name: "解压源代码"
      unarchive:
        src: "{{ build_dir }}/myapp-{{ app_version }}.tar.gz"
        dest: "{{ build_dir }}"
        remote_src: yes
    
    - name: "配置构建"
      command: cmake .
      args:
        chdir: "{{ build_dir }}/myapp-{{ app_version }}"
    
    - name: "编译"
      command: make -j4
      args:
        chdir: "{{ build_dir }}/myapp-{{ app_version }}"
    
    - name: "安装"
      command: make install
      args:
        chdir: "{{ build_dir }}/myapp-{{ app_version }}"
      become: yes
```

**模块解析:**
- **get_url 模块**: 下载文件
  - `url`: 下载链接，支持变量插值
  - `dest`: 本地保存路径

- **unarchive 模块**: 解压文件
  - `src`: 源文件路径
  - `dest`: 解压目标目录
  - `remote_src: yes`: 表示源文件在远程主机上

- **command 模块**: 执行 shell 命令
  - 直接写命令名称和参数
  - `args`: 额外参数，如 `chdir` 指定工作目录

**语法说明:**
- `vars:`: 定义 playbook 级别的变量
- `{{ build_dir }}`: 引用变量，使用 Jinja2 模板语法
- `args:` 参数块：用于指定命令的额外参数
- `chdir`: 在执行命令前切换到指定目录
- `become: yes` 在任务级别：仅在该任务使用特权提升
- `-j4`: make 命令参数，使用 4 个线程并行编译

## 实践练习 3: 服务配置和管理

### 示例 3.1: Web 服务器配置

```yaml
---
- name: "配置 Nginx Web 服务器"
  hosts: web_servers
  become: yes
  vars:
    server_name: "example.com"
    document_root: "/var/www/html"
  tasks:
    - name: "安装 Nginx"
      apt:
        name: nginx
        state: present
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: "创建网站目录"
      file:
        path: "{{ document_root }}"
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'
    
    - name: "创建网站配置文件"
      copy:
        content: |
          server {
              listen 80;
              server_name {{ server_name }};
              root {{ document_root }};
              index index.html index.htm;
              
              location / {
                  try_files $uri $uri/ =404;
              }
              
              access_log /var/log/nginx/{{ server_name }}.access.log;
              error_log /var/log/nginx/{{ server_name }}.error.log;
          }
        dest: "/etc/nginx/sites-available/{{ server_name }}"
        owner: root
        group: root
        mode: '0644'
      notify: reload nginx
    
    - name: "启用网站"
      file:
        src: "/etc/nginx/sites-available/{{ server_name }}"
        dest: "/etc/nginx/sites-enabled/{{ server_name }}"
        state: link
      notify: reload nginx
    
    - name: "创建测试页面"
      copy:
        content: |
          <!DOCTYPE html>
          <html>
          <head>
              <title>欢迎来到 {{ server_name }}</title>
          </head>
          <body>
              <h1>Hello from {{ inventory_hostname }}</h1>
              <p>当前时间: {{ ansible_date_time.iso8601 }}</p>
              <p>系统信息: {{ ansible_distribution }} {{ ansible_distribution_version }}</p>
          </body>
          </html>
        dest: "{{ document_root }}/index.html"
        owner: www-data
        group: www-data
        mode: '0644'
    
    - name: "启动并启用 Nginx"
      service:
        name: nginx
        state: started
        enabled: yes
  
  handlers:
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
```

**模块解析:**
- **file 模块（链接创建）**: 创建符号链接
  - `src`: 源文件路径
  - `dest`: 链接文件路径
  - `state: link`: 创建符号链接

- **copy 模块（模板内容）**: 创建包含变量的配置文件
  - `content: |`: 多行内容，支持变量插值
  - 在 Nginx 配置中使用 `{{ server_name }}` 等变量

**Handlers 机制:**
- `notify: reload nginx`: 当任务状态改变时通知 handler
- `handlers:`: 定义处理器，在 play 结束时执行
- `state: reloaded`: 重新加载服务而不中断连接

**语法说明:**
- 变量在配置文件中使用：`{{ server_name }}`、`{{ document_root }}`
- Nginx 站点配置：`sites-available` 存放配置，`sites-enabled` 启用配置
- `notify` 触发机制：只有在任务实际改变状态时才执行 handler
- HTML 页面中也使用变量：`{{ inventory_hostname }}`、`{{ ansible_date_time.iso8601 }}`

### 示例 3.2: 数据库配置

```yaml
---
- name: "配置 MySQL 数据库"
  hosts: db_servers
  become: yes
  vars:
    mysql_root_password: "SecurePassword123!"
    mysql_database: "myapp_db"
    mysql_user: "myapp_user"
    mysql_password: "AppPassword456!"
  tasks:
    - name: "安装 MySQL 服务器"
      apt:
        name:
          - mysql-server
          - python3-pymysql
        state: present
        update_cache: yes
    
    - name: "启动 MySQL 服务"
      service:
        name: mysql
        state: started
        enabled: yes
    
    - name: "设置 MySQL root 密码"
      mysql_user:
        name: root
        password: "{{ mysql_root_password }}"
        login_unix_socket: /var/run/mysqld/mysqld.sock
    
    - name: "创建数据库"
      mysql_db:
        name: "{{ mysql_database }}"
        state: present
        login_user: root
        login_password: "{{ mysql_root_password }}"
    
    - name: "创建数据库用户"
      mysql_user:
        name: "{{ mysql_user }}"
        password: "{{ mysql_password }}"
        priv: "{{ mysql_database }}.*:ALL"
        state: present
        login_user: root
        login_password: "{{ mysql_root_password }}"
    
    - name: "删除匿名用户"
      mysql_user:
        name: ""
        host_all: yes
        state: absent
        login_user: root
        login_password: "{{ mysql_root_password }}"
```

**模块解析:**
- **mysql_user 模块**: MySQL 用户管理
  - `name`: 用户名，`""` 表示匿名用户
  - `password`: 用户密码
  - `login_unix_socket`: 通过 Unix socket 连接 MySQL
  - `priv`: 权限设置，格式：`数据库.表:权限`
  - `state: present/absent`: 创建或删除用户
  - `host_all: yes`: 对所有主机生效

- **mysql_db 模块**: MySQL 数据库管理
  - `name`: 数据库名称
  - `state: present`: 确保数据库存在
  - `login_user`, `login_password`: 连接认证信息

**语法说明:**
- 密码变量：使用变量存储敏感信息，避免硬编码
- `python3-pymysql`: 安装 MySQL Python 客户端，Ansible 需要它来连接 MySQL
- 权限语法：`{{ mysql_database }}.*:ALL` 表示对指定数据库的所有表有所有权限
- 安全实践：删除匿名用户，提高安全性
- 连接方式：`login_unix_socket` 用于初始连接，之后使用用户名密码

## 实践练习 4: 用户和权限管理

### 示例 4.1: 用户管理

```yaml
---
- name: "用户和组管理"
  hosts: all
  become: yes
  vars:
    app_users:
      - name: "developer1"
        groups: ["sudo", "docker"]
        shell: "/bin/bash"
      - name: "developer2"
        groups: ["docker"]
        shell: "/bin/bash"
      - name: "deploy"
        groups: ["www-data"]
        shell: "/bin/bash"
        system: yes
  tasks:
    - name: "创建开发组"
      group:
        name: developers
        state: present
    
    - name: "创建用户"
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups | default([]) + ['developers'] }}"
        shell: "{{ item.shell | default('/bin/bash') }}"
        system: "{{ item.system | default(false) }}"
        create_home: yes
        state: present
      loop: "{{ app_users }}"
    
    - name: "设置 SSH 密钥"
      authorized_key:
        user: "{{ item.name }}"
        key: "{{ lookup('file', 'keys/' + item.name + '.pub') }}"
        state: present
      loop: "{{ app_users }}"
      when: item.name != "deploy"
    
    - name: "配置 sudo 权限"
      copy:
        content: |
          # 开发人员 sudo 权限
          %developers ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx
          %developers ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx
          %developers ALL=(ALL) NOPASSWD: /usr/bin/tail -f /var/log/*
        dest: /etc/sudoers.d/developers
        mode: '0440'
        validate: 'visudo -cf %s'
```

**模块解析:**
- **group 模块**: 用户组管理
  - `name`: 组名
  - `state: present`: 确保组存在

- **user 模块**: 用户管理
  - `name`: 用户名
  - `groups`: 用户所属组，支持列表和默认值
  - `shell`: 用户默认 shell
  - `system: yes`: 创建系统用户
  - `create_home: yes`: 创建用户家目录

- **authorized_key 模块**: SSH 密钥管理
  - `user`: 目标用户
  - `key`: 公钥内容，使用 `lookup` 插件从文件读取
  - `lookup('file', 'path')`: 从本地文件读取内容

**语法说明:**
- **列表变量定义**: 使用 YAML 列表语法定义多个用户
- **循环 (loop)**: 对列表中的每个元素执行任务
- **过滤器 (filter)**: `default([])` 设置默认值
- **条件判断**: `when: item.name != "deploy"` 排除特定用户
- **sudoers 文件**: 使用 `validate` 参数检查语法正确性
- **权限模式**: `0440` 表示只有 root 和所属组可读

### 示例 4.2: 文件权限和安全

```yaml
---
- name: "文件权限和安全配置"
  hosts: web_servers
  become: yes
  tasks:
    - name: "设置应用目录权限"
      file:
        path: /opt/myapp
        owner: root
        group: www-data
        mode: '0750'
        recurse: yes
    
    - name: "设置配置文件权限"
      file:
        path: /opt/myapp/config
        owner: root
        group: www-data
        mode: '0640'
        recurse: yes
    
    - name: "设置日志目录权限"
      file:
        path: /var/log/myapp
        owner: www-data
        group: www-data
        mode: '0755'
        state: directory
    
    - name: "配置 logrotate"
      copy:
        content: |
          /var/log/myapp/*.log {
              daily
              missingok
              rotate 30
              compress
              delaycompress
              notifempty
              create 0644 www-data www-data
              postrotate
                  systemctl reload nginx > /dev/null 2>&1 || true
              endscript
          }
        dest: /etc/logrotate.d/myapp
        mode: '0644'
```

**模块解析:**
- **file 模块（递归权限）**: 递归设置权限
  - `recurse: yes`: 递归应用到所有子目录和文件
  - 权限设置原则：目录 `0750`，配置文件 `0640`

- **copy 模块（logrotate 配置）**: 创建系统服务配置文件
  - `content: |`: 多行配置内容
  - `dest`: 系统配置文件目录

**语法说明:**
- **权限模式含义**:
  - `0750`: root 用户可读写执行，www-data 组可读执行，其他用户无权限
  - `0640`: root 用户可读写，www-data 组可读，其他用户无权限
  - `0755`: 所有用户可读执行，所有者可写

- **logrotate 配置语法**:
  - `daily`: 每天轮转日志
  - `rotate 30`: 保留 30 个旧日志文件
  - `compress`: 压缩旧日志
  - `postrotate`: 轮转后执行的命令

- **安全最佳实践**:
  - 配置文件权限设置为 `0640`，避免其他用户读取
  - 日志目录权限设置为 `0755`，确保日志可写入
  - 使用适当的用户组权限分离

## 实践练习 5: 复杂的部署场景

### 示例 5.1: 应用部署流水线

```yaml
---
- name: "应用部署流水线"
  hosts: app_servers
  become: yes
  vars:
    app_name: "mywebapp"
    app_version: "{{ version | default('latest') }}"
    app_user: "webapp"
    app_path: "/opt/{{ app_name }}"
    backup_path: "/backup/{{ app_name }}"
  tasks:
    - name: "创建应用用户"
      user:
        name: "{{ app_user }}"
        system: yes
        shell: /bin/false
        home: "{{ app_path }}"
        create_home: no
    
    - name: "创建应用目录结构"
      file:
        path: "{{ item }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'
      loop:
        - "{{ app_path }}"
        - "{{ app_path }}/current"
        - "{{ app_path }}/releases"
        - "{{ app_path }}/shared"
        - "{{ app_path }}/shared/logs"
        - "{{ app_path }}/shared/config"
        - "{{ backup_path }}"
    
    - name: "获取当前时间戳"
      set_fact:
        timestamp: "{{ ansible_date_time.epoch }}"
    
    - name: "创建新版本目录"
      file:
        path: "{{ app_path }}/releases/{{ timestamp }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'
    
    - name: "备份当前版本"
      archive:
        path: "{{ app_path }}/current"
        dest: "{{ backup_path }}/backup-{{ ansible_date_time.iso8601_basic_short }}.tar.gz"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0644'
      when: app_path + '/current' is exists
    
    - name: "下载新版本"
      get_url:
        url: "https://releases.example.com/{{ app_name }}/{{ app_version }}/{{ app_name }}.tar.gz"
        dest: "/tmp/{{ app_name }}-{{ app_version }}.tar.gz"
        mode: '0644'
    
    - name: "解压新版本"
      unarchive:
        src: "/tmp/{{ app_name }}-{{ app_version }}.tar.gz"
        dest: "{{ app_path }}/releases/{{ timestamp }}"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        remote_src: yes
    
    - name: "创建共享文件链接"
      file:
        src: "{{ app_path }}/shared/{{ item }}"
        dest: "{{ app_path }}/releases/{{ timestamp }}/{{ item }}"
        state: link
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
      loop:
        - logs
        - config
    
    - name: "更新当前版本链接"
      file:
        src: "{{ app_path }}/releases/{{ timestamp }}"
        dest: "{{ app_path }}/current"
        state: link
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        force: yes
      notify:
        - restart application
        - cleanup old releases
    
    - name: "设置应用权限"
      file:
        path: "{{ app_path }}/current"
        owner: "{{ app_user }}"
        group: "{{ app_user }}"
        mode: '0755'
        recurse: yes
  
  handlers:
    - name: restart application
      systemd:
        name: "{{ app_name }}"
        state: restarted
    
    - name: cleanup old releases
      shell: |
        cd {{ app_path }}/releases
        ls -t | tail -n +6 | xargs rm -rf
      become_user: "{{ app_user }}"
```

**模块解析:**
- **archive 模块**: 创建压缩归档文件
  - `path`: 要归档的路径
  - `dest`: 归档文件路径
  - 支持多种格式：tar.gz、zip 等

- **set_fact 模块**: 设置临时变量（facts）
  - `timestamp: "{{ ansible_date_time.epoch }}"`: 使用系统时间戳
  - 这些变量只在当前 playbook 执行期间有效

- **shell 模块**: 执行复杂的 shell 命令
  - `|`: 多行命令语法
  - `become_user`: 以指定用户身份执行命令

**语法说明:**
- **部署策略**: 使用 Capistrano 风格的部署目录结构
  - `releases/`: 存放所有版本
  - `current/`: 指向当前版本的符号链接
  - `shared/`: 共享文件（日志、配置）

- **变量默认值**: `{{ version | default('latest') }}` 设置默认值
- **条件判断**: `when: app_path + '/current' is exists` 检查文件是否存在
- **多 handler 通知**: `notify:` 可以触发多个 handler
- **时间戳格式**: `ansible_date_time.iso8601_basic_short` 生成文件名友好的时间戳

- **清理策略**: 保留最近 5 个版本，删除旧版本
- **符号链接更新**: `force: yes` 强制覆盖现有链接

## 调试和测试技巧

### 1. 使用 debug 模块

```yaml
- name: "调试变量值"
  debug:
    var: ansible_all_ipv4_addresses

- name: "调试消息"
  debug:
    msg: "主机 {{ inventory_hostname }} 的 IP 是 {{ ansible_default_ipv4.address }}"
```

**语法解析:**
- **debug 模块的两种用法**:
  - `var:`: 直接输出变量值
  - `msg:`: 输出自定义消息，支持变量插值
- **变量引用**: 使用 `{{ }}` 语法引用系统变量或自定义变量

### 2. 条件执行

```yaml
- name: "仅在 Ubuntu 上执行"
  apt:
    name: package_name
    state: present
  when: ansible_distribution == "Ubuntu"

- name: "检查文件是否存在"
  stat:
    path: /etc/myapp/config.yml
  register: config_file

- name: "仅在配置文件不存在时执行"
  template:
    src: config.yml.j2
    dest: /etc/myapp/config.yml
  when: not config_file.stat.exists
```

**语法解析:**
- **条件判断语法**: `when:` 后跟布尔表达式
- **stat 模块**: 获取文件状态信息
- **register 关键字**: 将任务结果保存到变量中
- **条件表达式**: `not config_file.stat.exists` 检查文件不存在
- **Jinja2 表达式**: 支持复杂的逻辑运算

### 3. 错误处理

```yaml
- name: "尝试启动服务"
  service:
    name: myapp
    state: started
  ignore_errors: yes
  register: service_result

- name: "服务启动失败时的处理"
  debug:
    msg: "服务启动失败: {{ service_result.msg }}"
  when: service_result is failed
```

**语法解析:**
- **ignore_errors: yes**: 忽略任务失败，继续执行后续任务
- **register**: 保存任务执行结果，包括成功/失败状态
- **状态检查**: `when: service_result is failed` 检查任务是否失败
- **错误信息**: `{{ service_result.msg }}` 获取错误消息
- **优雅的错误处理**: 允许 playbook 继续执行，同时记录错误

## 最佳实践

1. **使用有意义的任务名称**: 每个任务都应该有清晰的描述
2. **合理使用变量**: 避免硬编码，提高可重用性
3. **错误处理**: 使用 `ignore_errors`、`failed_when` 等处理异常
4. **幂等性**: 确保多次执行相同结果
5. **模块化**: 将复杂逻辑拆分为多个 playbook

## 下一步学习

完成这些练习后，你应该能够：
- 编写基础的 Ansible Playbooks
- 使用常见模块进行系统管理
- 理解变量和条件判断的使用
- 处理复杂的部署场景

下一天我们将学习变量和模板的高级用法。

## 实践作业

1. 编写一个 playbook 部署 LAMP/LEMP 环境
2. 创建一个用户管理的 playbook
3. 设计一个应用备份恢复的 playbook
4. 实现一个多环境配置管理方案 