# Ansible 高级主题与最佳实践

在掌握了 Ansible 的基础知识后，我们需要深入了解其高级特性和最佳实践，以充分发挥其在复杂环境中的潜力。

## 1. 高级 Playbook 技巧

### 1.1 动态 Inventory 管理

动态 Inventory 允许我们根据外部数据源动态生成主机清单。

```python
#!/usr/bin/env python3
# dynamic_inventory.py

import json
import argparse
import boto3

def get_ec2_instances():
    ec2 = boto3.client('ec2', region_name='us-west-2')
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
    inventory = {
        '_meta': {
            'hostvars': {}
        },
        'webservers': {
            'hosts': [],
            'vars': {
                'ansible_user': 'ubuntu'
            }
        },
        'databases': {
            'hosts': [],
            'vars': {
                'ansible_user': 'ubuntu'
            }
        }
    }
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # 获取实例标签
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            
            # 根据标签分类主机
            if tags.get('Role') == 'web':
                hostname = instance['PublicIpAddress']
                inventory['webservers']['hosts'].append(hostname)
                inventory['_meta']['hostvars'][hostname] = {
                    'ansible_host': instance['PrivateIpAddress'],
                    'instance_id': instance['InstanceId'],
                    'availability_zone': instance['Placement']['AvailabilityZone']
                }
            elif tags.get('Role') == 'db':
                hostname = instance['PublicIpAddress']
                inventory['databases']['hosts'].append(hostname)
                inventory['_meta']['hostvars'][hostname] = {
                    'ansible_host': instance['PrivateIpAddress'],
                    'instance_id': instance['InstanceId'],
                    'availability_zone': instance['Placement']['AvailabilityZone']
                }
    
    return inventory

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', default=None)
    args = parser.parse_args()
    
    if args.list:
        inventory = get_ec2_instances()
        print(json.dumps(inventory, indent=2))
    elif args.host:
        # 对于特定主机，返回空的主机变量
        print(json.dumps({}))

if __name__ == '__main__':
    main()
```

使用动态 Inventory：
```bash
# 测试动态 Inventory 脚本
python3 dynamic_inventory.py --list

# 使用动态 Inventory 运行 playbook
ansible-playbook -i dynamic_inventory.py site.yml
```

### 1.2 条件执行和错误处理

使用条件语句和错误处理来增强 Playbook 的健壮性。

```yaml
---
- name: Advanced Error Handling Example
  hosts: all
  tasks:
    # 条件执行示例
    - name: Install Apache on RedHat systems
      package:
        name: httpd
        state: present
      when: ansible_os_family == "RedHat"
      
    - name: Install Nginx on Debian systems
      package:
        name: nginx
        state: present
      when: ansible_os_family == "Debian"
      
    # 错误处理示例
    - name: Attempt to start service
      service:
        name: myapp
        state: started
      register: service_result
      ignore_errors: yes
      
    - name: Handle service start failure
      debug:
        msg: "Failed to start service: {{ service_result.msg }}"
      when: service_result.failed is defined and service_result.failed
      
    - name: Try alternative approach
      command: systemctl start myapp-fallback
      when: service_result.failed is defined and service_result.failed
      
    # 重试机制
    - name: Wait for application to respond
      uri:
        url: "http://{{ ansible_default_ipv4.address }}:8080/health"
        method: GET
        status_code: 200
      register: result
      until: result.status == 200
      retries: 30
      delay: 10
```

### 1.3 循环和迭代优化

使用高级循环技巧来简化复杂任务。

```yaml
---
- name: Advanced Loop Examples
  hosts: all
  vars:
    users:
      - name: alice
        uid: 1001
        groups: wheel
      - name: bob
        uid: 1002
        groups: users
      - name: charlie
        uid: 1003
        groups: developers
      
    packages:
      web: [nginx, php, mysql-client]
      db: [mysql-server, mysql-client]
      cache: [redis, memcached]
      
  tasks:
    # 嵌套循环
    - name: Create users with specific UIDs
      user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        groups: "{{ item.groups }}"
        state: present
      loop: "{{ users }}"
      
    # 字典循环
    - name: Install packages by category
      package:
        name: "{{ item.value }}"
        state: present
      loop: "{{ packages | dict2items }}"
      loop_control:
        label: "Installing {{ item.key }} packages"
        
    # 条件循环
    - name: Configure services based on role
      template:
        src: "{{ item }}.conf.j2"
        dest: "/etc/{{ item }}.conf"
      loop: "{{ ['nginx', 'mysql', 'redis'] }}"
      when: item in required_services
      
    # 索引循环
    - name: Create numbered directories
      file:
        path: "/opt/app/data/shard_{{ idx }}"
        state: directory
      loop: "{{ range(0, 10) | list }}"
      loop_control:
        index_var: idx
```

## 2. 自定义模块开发

### 2.1 Python 模块开发基础

创建一个简单的自定义模块来管理 Docker 容器。

```python
#!/usr/bin/python
# library/docker_container.py

from ansible.module_utils.basic import AnsibleModule
import docker

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            image=dict(type='str', required=True),
            state=dict(type='str', default='started', choices=['present', 'started', 'stopped', 'absent']),
            ports=dict(type='list', default=[]),
            env=dict(type='dict', default={}),
            volumes=dict(type='list', default=[]),
        ),
        supports_check_mode=True
    )

    name = module.params['name']
    image = module.params['image']
    state = module.params['state']
    ports = module.params['ports']
    env = module.params['env']
    volumes = module.params['volumes']

    # 初始化 Docker 客户端
    try:
        client = docker.from_env()
    except Exception as e:
        module.fail_json(msg=f"Failed to connect to Docker daemon: {str(e)}")

    # 检查容器是否存在
    try:
        container = client.containers.get(name)
        container_exists = True
    except docker.errors.NotFound:
        container_exists = False
        container = None
    except Exception as e:
        module.fail_json(msg=f"Failed to check container status: {str(e)}")

    # 根据状态执行相应操作
    if state == 'absent':
        if container_exists:
            if not module.check_mode:
                try:
                    container.remove(force=True)
                except Exception as e:
                    module.fail_json(msg=f"Failed to remove container: {str(e)}")
            module.exit_json(changed=True, msg=f"Container {name} removed")
        else:
            module.exit_json(changed=False, msg=f"Container {name} does not exist")

    elif state == 'present':
        if not container_exists:
            if not module.check_mode:
                try:
                    client.containers.create(
                        name=name,
                        image=image,
                        ports=ports,
                        environment=env,
                        volumes=volumes,
                        detach=True
                    )
                except Exception as e:
                    module.fail_json(msg=f"Failed to create container: {str(e)}")
            module.exit_json(changed=True, msg=f"Container {name} created")
        else:
            module.exit_json(changed=False, msg=f"Container {name} already exists")

    elif state == 'started':
        if not container_exists:
            if not module.check_mode:
                try:
                    container = client.containers.run(
                        name=name,
                        image=image,
                        ports=ports,
                        environment=env,
                        volumes=volumes,
                        detach=True
                    )
                except Exception as e:
                    module.fail_json(msg=f"Failed to start container: {str(e)}")
            module.exit_json(changed=True, msg=f"Container {name} started")
        else:
            if container.status != 'running':
                if not module.check_mode:
                    try:
                        container.start()
                    except Exception as e:
                        module.fail_json(msg=f"Failed to start container: {str(e)}")
                module.exit_json(changed=True, msg=f"Container {name} started")
            else:
                module.exit_json(changed=False, msg=f"Container {name} is already running")

    elif state == 'stopped':
        if container_exists and container.status == 'running':
            if not module.check_mode:
                try:
                    container.stop()
                except Exception as e:
                    module.fail_json(msg=f"Failed to stop container: {str(e)}")
            module.exit_json(changed=True, msg=f"Container {name} stopped")
        else:
            module.exit_json(changed=False, msg=f"Container {name} is not running")

if __name__ == '__main__':
    main()
```

使用自定义模块：
```yaml
---
- name: Use Custom Docker Module
  hosts: docker_hosts
  tasks:
    - name: Start web application container
      docker_container:
        name: webapp
        image: nginx:latest
        state: started
        ports:
          - "80:80"
          - "443:443"
        env:
          ENV: production
        volumes:
          - "/var/www:/usr/share/nginx/html"
          
    - name: Stop database container
      docker_container:
        name: database
        image: mysql:8.0
        state: stopped
```

## 3. 角色最佳实践

### 3.1 角色设计模式

创建一个可重用的 Web 服务器角色。

```
roles/webserver/
├── defaults/
│   └── main.yml
├── files/
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   ├── install.yml
│   ├── configure.yml
│   └── secure.yml
├── templates/
├── vars/
│   └── main.yml
└── README.md
```

角色元数据 (meta/main.yml)：
```yaml
galaxy_info:
  author: Your Name
  description: A comprehensive web server role
  company: Your Company
  
  license: MIT
  
  min_ansible_version: 2.9
  
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
    - name: CentOS
      versions:
        - 7
        - 8
        
  galaxy_tags:
    - web
    - nginx
    - apache
    - security

dependencies: []
```

角色默认变量 (defaults/main.yml)：
```yaml
---
# Web server configuration
webserver_package: nginx
webserver_service: nginx
webserver_port: 80
webserver_ssl_port: 443
webserver_user: www-data
webserver_group: www-data

# Security settings
webserver_enable_security_headers: true
webserver_enable_hsts: true
webserver_hsts_max_age: 31536000

# SSL configuration
webserver_ssl_certificate: /etc/ssl/certs/nginx.crt
webserver_ssl_certificate_key: /etc/ssl/private/nginx.key
```

角色主任务 (tasks/main.yml)：
```yaml
---
- name: Include installation tasks
  include_tasks: install.yml

- name: Include configuration tasks
  include_tasks: configure.yml

- name: Include security tasks
  include_tasks: secure.yml
  when: webserver_enable_security_headers

- name: Ensure web server is running
  service:
    name: "{{ webserver_service }}"
    state: started
    enabled: yes
```

安装任务 (tasks/install.yml)：
```yaml
---
- name: Install web server package
  package:
    name: "{{ webserver_package }}"
    state: present
    
- name: Create web root directory
  file:
    path: /var/www/html
    state: directory
    owner: "{{ webserver_user }}"
    group: "{{ webserver_group }}"
    mode: '0755'
```

配置任务 (tasks/configure.yml)：
```yaml
---
- name: Configure web server
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
  notify: restart webserver

- name: Create site configuration
  template:
    src: site.conf.j2
    dest: "/etc/nginx/sites-available/{{ inventory_hostname }}"
    mode: '0644'
  notify: reload webserver

- name: Enable site
  file:
    src: "/etc/nginx/sites-available/{{ inventory_hostname }}"
    dest: "/etc/nginx/sites-enabled/{{ inventory_hostname }}"
    state: link
  notify: reload webserver
```

安全任务 (tasks/secure.yml)：
```yaml
---
- name: Configure security headers
  lineinfile:
    path: /etc/nginx/nginx.conf
    regexp: "{{ item.regexp }}"
    line: "{{ item.line }}"
    insertafter: "{{ item.insertafter | default(omit) }}"
  loop:
    - { regexp: '^.*add_header X-Frame-Options', line: 'add_header X-Frame-Options "SAMEORIGIN";', insertafter: 'http {' }
    - { regexp: '^.*add_header X-Content-Type-Options', line: 'add_header X-Content-Type-Options "nosniff";' }
    - { regexp: '^.*add_header X-XSS-Protection', line: 'add_header X-XSS-Protection "1; mode=block";' }
  notify: reload webserver

- name: Configure HSTS
  lineinfile:
    path: /etc/nginx/nginx.conf
    regexp: '^.*add_header Strict-Transport-Security'
    line: 'add_header Strict-Transport-Security "max-age={{ webserver_hsts_max_age }}; includeSubDomains" always;'
  when: webserver_enable_hsts
  notify: reload webserver
```

处理器 (handlers/main.yml)：
```yaml
---
- name: restart webserver
  service:
    name: "{{ webserver_service }}"
    state: restarted

- name: reload webserver
  service:
    name: "{{ webserver_service }}"
    state: reloaded
```

## 4. 性能优化

### 4.1 并行执行优化

优化 Ansible 配置以提高执行性能。

```ini
# ansible.cfg
[defaults]
# 增加并行执行数量
forks = 50

# 启用事实缓存
gathering = smart
fact_caching = redis
fact_caching_timeout = 86400

# 启用内部重试
retry_files_enabled = False

# 优化连接
host_key_checking = False
timeout = 30

[inventory]
# 启用 inventory 缓存
cache = True
cache_plugin = redis
cache_timeout = 3600

[ssh_connection]
# SSH 连接优化
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
control_path = %(directory)s/%%h-%%r
```

### 4.2 大规模环境管理

使用策略来管理大规模环境。

```yaml
---
- name: Large Scale Deployment Strategy
  hosts: all
  serial: 
    - 10%
    - 20%
    - "remainder"
  max_fail_percentage: 5
  
  pre_tasks:
    - name: Gather facts selectively
      setup:
        gather_subset:
          - network
          - virtual
      when: gather_facts | default(true)
      
  tasks:
    - name: Deploy application in batches
      include_role:
        name: application_deploy
      delegate_to: "{{ item }}"
      loop: "{{ play_hosts }}"
      
  post_tasks:
    - name: Verify deployment
      uri:
        url: "http://{{ ansible_default_ipv4.address }}/health"
        status_code: 200
      retries: 10
      delay: 5
```

## 5. 安全最佳实践

### 5.1 凭证管理

安全地管理凭证和敏感信息。

```yaml
---
- name: Secure Credential Management
  hosts: all
  vars:
    # 使用 Ansible Vault 加密敏感变量
    database_password: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      313233343536373839306162636465663738393061626364656637383930616263646566
      373839306162636465663738393061626364656637383930616263646566373839306162
      636465663738393061626364656637383930616263646566373839306162636465663738
      393061626364656637383930616263646566373839306162636465663738393061626364
      6566
      
  tasks:
    - name: Create configuration with encrypted variables
      template:
        src: app_config.j2
        dest: /etc/app/config.ini
        mode: '0600'
        
    - name: Use lookup plugin for external secrets
      set_fact:
        api_key: "{{ lookup('hashi_vault', 'secret=kv/api-keys:myapp token={{ vault_token }} url={{ vault_url }}') }}"
        
    - name: Configure application with secrets
      template:
        src: app_secrets.j2
        dest: /etc/app/secrets.ini
        mode: '0600'
      no_log: true
```

### 5.3 Ansible Vault 高级应用

#### 5.3.1 多环境 Vault 管理

```yaml
# inventory/group_vars/all/vault.yml
---
# 开发环境变量
dev_secrets: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  # 开发环境加密内容
  
# 生产环境变量
prod_secrets: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  # 生产环境加密内容

# 根据环境动态选择变量
secrets: "{{ dev_secrets if env == 'development' else prod_secrets }}"

# Playbook 中使用
- name: Deploy with environment-specific secrets
  hosts: all
  vars_files:
    - group_vars/all/vault.yml
  tasks:
    - name: Configure application
      template:
        src: config.j2
        dest: /etc/app/config.yaml
        mode: '0600'
      vars:
        db_password: "{{ secrets.database_password }}"
        api_key: "{{ secrets.api_key }}"
```

#### 5.3.2 Vault ID 和分层加密

```bash
# 使用不同的 Vault ID 管理不同级别的机密
ansible-vault encrypt --vault-id dev@prompt dev_secrets.yml
ansible-vault encrypt --vault-id prod@prompt prod_secrets.yml
ansible-vault encrypt --vault-id infra@prompt infrastructure_secrets.yml

# 运行 Playbook 时指定多个 Vault ID
ansible-playbook deploy.yml --vault-id dev@prompt --vault-id prod@prompt --vault-id infra@prompt

# 使用密码文件
ansible-playbook deploy.yml --vault-id dev@.vault_pass_dev --vault-id prod@.vault_pass_prod
```

#### 5.3.3 Vault 与 CI/CD 集成

```yaml
# .gitlab-ci.yml
stages:
  - deploy

deploy_production:
  stage: deploy
  script:
    - echo "$PROD_VAULT_PASSWORD" > .vault_pass_prod
    - chmod 600 .vault_pass_prod
    - ansible-playbook -i production deploy.yml --vault-id prod@.vault_pass_prod
    - rm -f .vault_pass_prod
  only:
    - main
  variables:
    PROD_VAULT_PASSWORD: $PROD_VAULT_PASSWORD

deploy_staging:
  stage: deploy
  script:
    - echo "$STAGING_VAULT_PASSWORD" > .vault_pass_staging
    - chmod 600 .vault_pass_staging
    - ansible-playbook -i staging deploy.yml --vault-id staging@.vault_pass_staging
    - rm -f .vault_pass_staging
  only:
    - develop
  variables:
    STAGING_VAULT_PASSWORD: $STAGING_VAULT_PASSWORD
```

#### 5.3.4 企业级 Vault 策略

```yaml
# ansible.cfg
[defaults]
vault_password_file = .vault_pass
vault_identity_list = dev@.vault_pass_dev,prod@.vault_pass_prod,infra@.vault_pass_infra

# 启用 Vault 缓存以提高性能
vault_caching_enabled = True
vault_caching_ttl = 3600

# 安全配置
vault_password_prompt = True
vault_ask_vault_pass = False
```

### 5.4 零信任安全架构

```yaml
---
- name: Zero Trust Security Implementation
  hosts: all
  vars:
    # 从零信任平台获取临时令牌
    zero_trust_token: "{{ lookup('url', 'https://zero-trust-platform/api/token', username=api_user, password=api_password) }}"
    
  tasks:
    - name: Get dynamic secrets from zero trust platform
      uri:
        url: "https://secrets-manager/api/secrets"
        method: GET
        headers:
          Authorization: "Bearer {{ zero_trust_token }}"
        return_content: yes
      register: secrets_response
      
    - name: Create temporary encrypted configuration
      template:
        src: zero_trust_config.j2
        dest: /tmp/zero_trust_config.yml
        mode: '0600'
      vars:
        dynamic_secrets: "{{ secrets_response.json }}"
      
    - name: Apply zero trust configuration
      include_vars:
        file: /tmp/zero_trust_config.yml
      
    - name: Cleanup temporary files
      file:
        path: /tmp/zero_trust_config.yml
        state: absent
      
    - name: Configure application with zero trust principles
      template:
        src: app_config.j2
        dest: /etc/app/config.yaml
        mode: '0600'
      vars:
        # 使用动态获取的凭据
        db_credentials: "{{ dynamic_secrets.database }}"
        api_credentials: "{{ dynamic_secrets.api }}"
```

### 5.2 最小权限原则

实施最小权限原则以增强安全性。

```yaml
---
- name: Implement Least Privilege Principle
  hosts: all
  become: yes
  become_user: "{{ item.user }}"
  become_method: sudo
  loop:
    - { user: "webuser", tasks: ["deploy_web_content"] }
    - { user: "dbuser", tasks: ["manage_database"] }
    - { user: "monitoring", tasks: ["collect_metrics"] }
    
  tasks:
    - name: Deploy web content (limited privileges)
      copy:
        src: files/{{ item.tasks[0] }}/
        dest: /var/www/html/
        owner: webuser
        group: webuser
        mode: '0644'
      when: "'deploy_web_content' in item.tasks"
      
    - name: Manage database (limited privileges)
      mysql_query:
        login_user: dbuser
        login_password: "{{ db_password }}"
        query: "{{ item.query }}"
      when: "'manage_database' in item.tasks"
      
    - name: Collect metrics (read-only)
      command: "/usr/local/bin/collect_metrics.sh"
      when: "'collect_metrics' in item.tasks"
```

通过掌握这些高级主题和最佳实践，您可以更有效地使用 Ansible 来管理复杂的基础设施，并确保其安全性、性能和可维护性。