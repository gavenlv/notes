# Ansible Vault 安全加密管理

## 概述

Ansible Vault 是 Ansible 的核心安全功能，用于加密敏感数据，如密码、API 密钥、证书等。它确保敏感信息在版本控制系统中安全存储。

## 1. Vault 基础

### 1.1 Vault 工作原理

Ansible Vault 使用 AES-256 对称加密算法来加密数据。加密后的数据可以安全地存储在版本控制系统中，只有拥有密码的人才能解密。

### 1.2 创建加密文件

```bash
# 创建新的加密文件
ansible-vault create secrets.yml

# 加密现有文件
ansible-vault encrypt secrets.yml

# 查看加密文件内容
ansible-vault view secrets.yml

# 编辑加密文件
ansible-vault edit secrets.yml

# 解密文件
ansible-vault decrypt secrets.yml
```

### 1.3 密码管理方式

#### 密码文件方式

```bash
# 创建密码文件
echo "myvaultpassword" > .vault_pass
chmod 600 .vault_pass

# 使用密码文件
ansible-vault view secrets.yml --vault-password-file .vault_pass
```

#### 环境变量方式

```bash
# 设置环境变量
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass

# 或直接设置密码
export ANSIBLE_VAULT_PASSWORD="myvaultpassword"
```

## 2. Vault 实战应用

### 2.1 加密变量文件

创建 `group_vars/all/vault.yml`：

```yaml
---
# 数据库凭据
database_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          313233343536373839306162636465663738393061626364656637383930616263646566
          373839306162636465663738393061626364656637383930616263646566373839306162
          636465663738393061626364656637383930616263646566373839306162636465663738
          393061626364656637383930616263646566373839306162636465663738393061626364
          6566

# API 密钥
api_key: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          616263646566373839306162636465663738393061626364656637383930616263646566
          373839306162636465663738393061626364656637383930616263646566373839306162
          636465663738393061626364656637383930616263646566373839306162636465663738
          393061626364656637383930616263646566373839306162636465663738393061626364
          6566

# SSL 证书私钥
ssl_private_key: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          373839306162636465663738393061626364656637383930616263646566373839306162
          636465663738393061626364656637383930616263646566373839306162636465663738
          393061626364656637383930616263646566373839306162636465663738393061626364
          656637383930616263646566373839306162636465663738393061626364656637383930
          6162
```

### 2.2 在 Playbook 中使用加密变量

```yaml
---
- name: Deploy Application with Encrypted Secrets
  hosts: app_servers
  vars_files:
    - group_vars/all/vault.yml
  
  tasks:
    - name: Create database configuration
      template:
        src: database.conf.j2
        dest: /etc/app/database.conf
        mode: '0600'
      no_log: true  # 防止密码在日志中显示
      
    - name: Configure API credentials
      template:
        src: api_config.j2
        dest: /etc/app/api.conf
        mode: '0600'
      no_log: true
      
    - name: Install SSL certificate
      copy:
        content: "{{ ssl_private_key }}"
        dest: /etc/ssl/private/app.key
        mode: '0600'
      no_log: true
```

### 2.3 模板中使用加密变量

创建 `templates/database.conf.j2`：

```jinja2
# {{ ansible_managed }}

[database]
host = {{ db_host }}
port = {{ db_port }}
name = {{ db_name }}
username = {{ db_user }}
password = {{ database_password }}

# 连接字符串
connection_string = postgresql://{{ db_user }}:{{ database_password }}@{{ db_host }}:{{ db_port }}/{{ db_name }}
```

## 3. 高级 Vault 功能

### 3.1 多密码 Vault

对于不同环境使用不同的密码：

```bash
# 创建开发环境密码文件
echo "dev_password" > .vault_pass_dev

# 创建生产环境密码文件  
echo "prod_password" > .vault_pass_prod

# 使用特定密码文件
ansible-playbook site.yml --vault-password-file .vault_pass_dev -e "env=development"
ansible-playbook site.yml --vault-password-file .vault_pass_prod -e "env=production"
```

### 3.2 Vault ID 管理

使用 Vault ID 来管理多个加密文件：

```bash
# 使用不同的 Vault ID 加密文件
ansible-vault encrypt --vault-id dev@prompt dev_secrets.yml
ansible-vault encrypt --vault-id prod@prompt prod_secrets.yml

# 运行 Playbook 时指定 Vault ID
ansible-playbook site.yml --vault-id dev@prompt --vault-id prod@prompt
```

### 3.3 重新加密和轮换密码

```bash
# 重新加密所有文件（密码轮换）
ansible-vault rekey group_vars/all/vault.yml

# 批量重新加密
find . -name "*vault*" -type f | xargs -I {} ansible-vault rekey {}

# 创建新的密码文件并重新加密
echo "new_password" > .vault_pass_new
ansible-vault rekey --new-vault-password-file .vault_pass_new secrets.yml
```

## 4. Vault 与 CI/CD 集成

### 4.1 Jenkins 集成

在 Jenkins Pipeline 中使用 Vault：

```groovy
pipeline {
    agent any
    
    environment {
        VAULT_PASSWORD = credentials('ansible-vault-password')
    }
    
    stages {
        stage('Deploy') {
            steps {
                sh '''
                    echo "$VAULT_PASSWORD" > .vault_pass
                    chmod 600 .vault_pass
                    ansible-playbook -i inventory site.yml --vault-password-file .vault_pass
                    rm -f .vault_pass
                '''
            }
        }
    }
}
```

### 4.2 GitLab CI 集成

```yaml
# .gitlab-ci.yml

stages:
  - deploy

deploy:
  stage: deploy
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - chmod 600 .vault_pass
    - ansible-playbook -i inventory site.yml --vault-password-file .vault_pass
    - rm -f .vault_pass
  only:
    - main
  variables:
    ANSIBLE_VAULT_PASSWORD: $ANSIBLE_VAULT_PASSWORD
```

### 4.3 GitHub Actions 集成

```yaml
# .github/workflows/deploy.yml

name: Deploy with Ansible Vault

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    
    - name: Install Ansible
      run: pip install ansible
    
    - name: Deploy with Vault
      run: |
        echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}" > .vault_pass
        chmod 600 .vault_pass
        ansible-playbook -i inventory site.yml --vault-password-file .vault_pass
        rm -f .vault_pass
      env:
        ANSIBLE_VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
```

## 5. 企业级 Vault 实践

### 5.1 分层加密策略

```yaml
# 目录结构
inventory/
├── group_vars/
│   ├── all/
│   │   ├── vars.yml          # 非敏感变量
│   │   └── vault.yml         # 加密变量
│   ├── production/
│   │   ├── vars.yml
│   │   └── vault.yml
│   └── development/
│       ├── vars.yml
│       └── vault.yml
├── host_vars/
│   ├── server1.example.com/
│   │   ├── vars.yml
│   │   └── vault.yml
│   └── server2.example.com/
│       ├── vars.yml
│       └── vault.yml
```

### 5.2 密钥管理系统集成

与 HashiCorp Vault 集成：

```yaml
---
- name: Get secrets from HashiCorp Vault
  hosts: localhost
  tasks:
    - name: Retrieve database password
      set_fact:
        db_password: "{{ lookup('hashi_vault', 'secret=databases/production/postgres token={{ vault_token }}')['data']['password'] }}"
    
    - name: Create encrypted variable file
      copy:
        content: |
          database_password: !vault |
            $ANSIBLE_VAULT;1.1;AES256
            {{ db_password | ansible.builtin.vault | b64encode }}
        dest: /tmp/encrypted_db_password.yml
        mode: '0600'
```

### 5.3 审计和合规性

```bash
# 检查加密文件状态
ansible-vault check group_vars/all/vault.yml

# 验证加密完整性
ansible-vault verify group_vars/all/vault.yml

# 审计加密文件访问
#!/bin/bash
# audit_vault_access.sh

LOG_FILE="/var/log/ansible-vault-audit.log"

# 记录 Vault 访问
echo "$(date): User $(whoami) accessed vault file $1" >> $LOG_FILE

# 执行实际命令
ansible-vault "$@"
```

## 6. 故障排除和最佳实践

### 6.1 常见问题解决

```bash
# 忘记密码时的恢复流程
# 1. 检查是否有备份的密码文件
ls -la ~/.vault_pass*

# 2. 检查环境变量
echo $ANSIBLE_VAULT_PASSWORD_FILE
echo $ANSIBLE_VAULT_PASSWORD

# 3. 尝试使用提示输入
ansible-vault view secrets.yml --ask-vault-pass

# 4. 如果所有方法都失败，需要重新创建加密文件
```

### 6.2 安全最佳实践

1. **密码强度**：使用强密码（至少16个字符，包含大小写字母、数字和特殊字符）
2. **密码存储**：不要将密码存储在版本控制中
3. **访问控制**：限制对密码文件的访问权限
4. **定期轮换**：定期更换 Vault 密码
5. **备份策略**：确保有密码的备份机制
6. **审计日志**：记录所有 Vault 访问操作

### 6.3 性能优化

```ini
# ansible.cfg
[defaults]
# 启用 Vault 缓存
vault_password_file = .vault_pass

# 优化 Vault 解密性能
vault_identity_list = dev@.vault_pass_dev,prod@.vault_pass_prod

# 设置 Vault 超时
vault_read_timeout = 30
vault_connect_timeout = 5
```

## 7. 实际案例研究

### 7.1 多团队协作场景

```yaml
# 团队特定的 Vault 文件结构
inventory/
├── team_a/
│   ├── group_vars/
│   │   └── vault.yml
│   └── host_vars/
├── team_b/
│   ├── group_vars/
│   │   └── vault.yml
│   └── host_vars/
└── shared/
    ├── group_vars/
    │   └── vault.yml
    └── host_vars/

# 每个团队使用不同的密码
ansible-playbook -i inventory/team_a site.yml --vault-password-file .vault_pass_team_a
ansible-playbook -i inventory/team_b site.yml --vault-password-file .vault_pass_team_b
```

### 7.2 零信任架构集成

```yaml
---
- name: Zero Trust Security with Ansible Vault
  hosts: all
  vars:
    # 从零信任平台获取临时令牌
    zero_trust_token: "{{ lookup('url', 'https://zero-trust-platform/api/token', username=api_user, password=api_password) }}"
    
  tasks:
    - name: Get dynamic secrets
      uri:
        url: "https://secrets-manager/api/secrets"
        method: GET
        headers:
          Authorization: "Bearer {{ zero_trust_token }}"
        return_content: yes
      register: secrets_response
      
    - name: Create temporary Vault file
      copy:
        content: |
          temporary_secret: !vault |
            $ANSIBLE_VAULT;1.1;AES256
            {{ secrets_response.json.secret | ansible.builtin.vault | b64encode }}
        dest: /tmp/temp_vault.yml
        mode: '0600'
      
    - name: Use temporary secret
      include_vars:
        file: /tmp/temp_vault.yml
      
    - name: Cleanup temporary file
      file:
        path: /tmp/temp_vault.yml
        state: absent
```

## 总结

Ansible Vault 是企业级自动化部署的关键安全组件。通过合理使用 Vault，您可以：

- 安全地管理敏感数据
- 实现合规性要求
- 支持多团队协作
- 集成到现代 CI/CD 流程
- 构建零信任安全架构

记住安全最佳实践，定期审计和更新您的 Vault 策略，确保自动化流程的安全性和可靠性。