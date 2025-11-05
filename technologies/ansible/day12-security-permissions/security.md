# Ansible 安全与权限管理

在企业环境中，安全性是基础设施自动化的关键考虑因素。Ansible 提供了多种机制来确保安全性和适当的权限控制。

## 1. Ansible Vault

Ansible Vault 是用于加密敏感数据的内置功能。

### 1.1 创建加密文件

```bash
# 创建新的加密文件
ansible-vault create secrets.yml

# 编辑现有加密文件
ansible-vault edit secrets.yml
```

### 1.2 加密现有文件

```bash
# 加密现有文件
ansible-vault encrypt secrets.yml
```

### 1.3 解密文件

```bash
# 解密文件
ansible-vault decrypt secrets.yml
```

### 1.4 查看加密文件

```bash
# 查看加密文件内容
ansible-vault view secrets.yml
```

### 1.5 使用加密文件

```yaml
# playbook.yml
---
- hosts: all
  vars_files:
    - secrets.yml
  tasks:
    - name: Use secret variable
      debug:
        msg: "Password is {{ db_password }}"
```

运行加密的 playbook：
```bash
ansible-playbook playbook.yml --ask-vault-pass
```

## 2. 多重 Vault 密码

### 2.1 使用不同的 Vault ID

```bash
# 创建带有特定 ID 的加密文件
ansible-vault create --vault-id dev@prompt dev_secrets.yml
ansible-vault create --vault-id prod@prompt prod_secrets.yml
```

### 2.2 使用多个 Vault ID 运行 Playbook

```bash
# 使用多个 vault ID
ansible-playbook playbook.yml --vault-id dev@prompt --vault-id prod@prompt
```

## 3. 权限控制

### 3.1 文件权限

确保 Ansible 文件具有适当的操作系统级别权限：

```bash
# 设置适当的文件权限
chmod 600 inventory
chmod 644 playbook.yml
chmod 600 group_vars/all/vault.yml
```

### 3.2 用户和组管理

```yaml
# 创建系统用户和组
- name: Create ansible user
  user:
    name: ansible
    system: yes
    shell: /bin/bash
    home: /home/ansible
    groups: wheel
```

## 4. 安全加固

### 4.1 SSH 配置

```yaml
# 安全 SSH 配置
- name: Configure SSH security
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: "{{ item.regexp }}"
    line: "{{ item.line }}"
    backup: yes
  loop:
    - { regexp: '^#?PermitRootLogin', line: 'PermitRootLogin no' }
    - { regexp: '^#?PasswordAuthentication', line: 'PasswordAuthentication no' }
    - { regexp: '^#?PubkeyAuthentication', line: 'PubkeyAuthentication yes' }
  notify: Restart sshd
```

### 4.2 防火墙配置

```yaml
# UFW 防火墙配置
- name: Configure UFW firewall
  ufw:
    rule: allow
    port: "{{ item.port }}"
    proto: "{{ item.proto | default('tcp') }}"
  loop:
    - { port: '22' }      # SSH
    - { port: '80' }      # HTTP
    - { port: '443' }     # HTTPS
    - { port: '3306' }    # MySQL

- name: Enable UFW
  ufw:
    state: enabled
    policy: deny
```

## 5. 合规性检查

### 5.1 系统基线检查

```yaml
# CIS 基线检查示例
- name: Check password complexity
  command: grep "^password.*pam_pwquality.so" /etc/pam.d/common-password
  register: password_policy
  failed_when: password_policy.stdout == ""

- name: Check account lockout policy
  command: grep "auth.*pam_tally2.so" /etc/pam.d/login
  register: lockout_policy
  failed_when: lockout_policy.stdout == ""
```

### 5.2 安全扫描

```yaml
# 使用 OpenSCAP 进行安全扫描
- name: Install OpenSCAP
  package:
    name: openscap-scanner
    state: present

- name: Run security scan
  command: oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_standard /usr/share/xml/scap/ssg/content/ssg-ubuntu1804-ds.xml
  register: scan_results

- name: Save scan results
  copy:
    content: "{{ scan_results.stdout }}"
    dest: /var/log/security_scan_{{ ansible_date_time.iso8601 }}.txt
```

## 6. 审计和日志

### 6.1 配置审计日志

```yaml
# 配置审计规则
- name: Add audit rules
  lineinfile:
    path: /etc/audit/rules.d/ansible.rules
    line: "{{ item }}"
    create: yes
  loop:
    - "-w /etc/passwd -p wa -k identity"
    - "-w /etc/shadow -p wa -k identity"
    - "-w /etc/group -p wa -k identity"
    - "-w /var/log/ansible -p wa -k ansible"

- name: Reload audit rules
  command: augenrules --load
```

### 6.2 日志转发

```yaml
# 配置日志转发到集中式日志服务器
- name: Configure rsyslog for remote logging
  lineinfile:
    path: /etc/rsyslog.conf
    line: "*.* @logs.example.com:514"
    backup: yes

- name: Restart rsyslog
  service:
    name: rsyslog
    state: restarted
```

## 7. 最佳实践

### 7.1 密钥管理

```yaml
# 使用 Ansible Vault 和外部密钥管理系统
- name: Retrieve secret from external system
  uri:
    url: https://secrets.example.com/api/v1/secrets/{{ secret_name }}
    headers:
      Authorization: "Bearer {{ vault_token }}"
    return_content: yes
  register: secret_data
  no_log: true

- name: Use retrieved secret
  set_fact:
    db_password: "{{ secret_data.json.value }}"
```

### 7.2 安全的 Playbook 编写

```yaml
# 安全的 Playbook 示例
---
- name: Secure system configuration
  hosts: all
  become: yes
  vars:
    # 不要在 playbook 中硬编码敏感信息
    # 使用 vault 加密的变量文件
    ansible_become_password: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      66386439653...
  tasks:
    - name: Ensure secure permissions
      file:
        path: "{{ item.path }}"
        mode: "{{ item.mode }}"
      loop:
        - { path: "/etc/ssh/sshd_config", mode: "0600" }
        - { path: "/etc/passwd", mode: "0644" }
        - { path: "/etc/shadow", mode: "0640" }
      no_log: true  # 避免在日志中泄露敏感信息
```

## 8. 实际应用示例

### 8.1 完整的安全加固 Playbook

```yaml
# security_hardening.yml
---
- name: System Security Hardening
  hosts: all
  become: yes
  vars_files:
    - vault.yml
  tasks:
    # SSH 安全配置
    - name: Secure SSH configuration
      include_tasks: tasks/ssh_security.yml
    
    # 防火墙配置
    - name: Configure firewall
      include_tasks: tasks/firewall.yml
    
    # 用户和权限管理
    - name: Manage users and permissions
      include_tasks: tasks/users.yml
    
    # 日志和审计配置
    - name: Configure logging and auditing
      include_tasks: tasks/logging.yml
      
  handlers:
    - name: Restart sshd
      service:
        name: sshd
        state: restarted
        
    - name: Reload firewall
      command: ufw reload
```

通过本日的学习，您已经掌握了 Ansible 中的安全和权限管理技术，包括 Vault 加密、权限控制、安全加固和合规性检查等方面的知识。这些技能对于在企业环境中安全地实施 Ansible 自动化至关重要。