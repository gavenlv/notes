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

### 核心概念

1. **Play**: 一个 playbook 中的一个执行单元
2. **Task**: Play 中的具体操作
3. **Module**: 执行具体操作的模块
4. **Handler**: 响应通知的特殊任务

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