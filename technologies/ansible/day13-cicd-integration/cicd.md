# Ansible CI/CD 集成

在现代 DevOps 实践中，将 Ansible 集成到持续集成和持续部署（CI/CD）流水线中是实现基础设施即代码和自动化部署的关键。通过 CI/CD 集成，我们可以确保基础设施变更的可重复性、可靠性和安全性。

## 1. GitLab CI 集成

GitLab CI 是最流行的 CI/CD 平台之一，与 Ansible 集成非常紧密。

### 1.1 基本配置

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - deploy

variables:
  ANSIBLE_HOST_KEY_CHECKING: "false"

before_script:
  - apt-get update -qy
  - apt-get install -y python3-pip
  - pip3 install ansible
  - ansible --version

validate:
  stage: validate
  script:
    - ansible-playbook playbooks/site.yml --syntax-check

test:
  stage: test
  script:
    - ansible-playbook playbooks/site.yml --check --diff
  only:
    - merge_requests

deploy:
  stage: deploy
  script:
    - ansible-playbook playbooks/site.yml
  environment:
    name: production
  only:
    - main
```

### 1.2 使用 GitLab CI 的 Ansible 执行器

```yaml
# .gitlab-ci.yml
deploy_staging:
  stage: deploy
  image: 
    name: willhallonline/ansible:2.10-alpine
    entrypoint: [""]
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yml
  only:
    - staging

deploy_production:
  stage: deploy
  image: 
    name: willhallonline/ansible:2.10-alpine
    entrypoint: [""]
  script:
    - ansible-playbook -i inventory/production playbooks/deploy.yml
  when: manual
  only:
    - main
```

## 2. GitHub Actions 集成

GitHub Actions 提供了强大的自动化功能，可以轻松集成 Ansible。

### 2.1 基本工作流

```yaml
# .github/workflows/ansible.yml
name: Ansible Deployment
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install Ansible
      run: |
        pip install ansible
        
    - name: Validate syntax
      run: |
        ansible-playbook playbooks/site.yml --syntax-check

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install Ansible
      run: |
        pip install ansible
        
    - name: Deploy with Ansible
      run: |
        ansible-playbook playbooks/site.yml -i inventory/production
      env:
        ANSIBLE_HOST_KEY_CHECKING: false
```

### 2.2 使用 Secrets 管理凭证

```yaml
# .github/workflows/ansible-deploy.yml
deploy:
  runs-on: ubuntu-latest
  steps:
  - uses: actions/checkout@v2
  
  - name: Set up SSH key
    uses: webfactory/ssh-agent@v0.5.1
    with:
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      
  - name: Set up Python and Ansible
    run: |
      pip install ansible
      
  - name: Create vault password file
    run: |
      echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}" > ~/.vault_pass.txt
      
  - name: Deploy with Ansible Vault
    run: |
      ansible-playbook playbooks/site.yml -i inventory/production --vault-password-file ~/.vault_pass.txt
    env:
      ANSIBLE_HOST_KEY_CHECKING: false
```

## 3. Jenkins 流水线集成

Jenkins 是企业级 CI/CD 平台，支持复杂的流水线配置。

### 3.1 声明式流水线

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        ANSIBLE_HOST_KEY_CHECKING = 'false'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install ansible'
                sh 'ansible --version'
            }
        }
        
        stage('Validate') {
            steps {
                sh 'ansible-playbook playbooks/site.yml --syntax-check'
            }
        }
        
        stage('Test') {
            steps {
                sh 'ansible-playbook playbooks/site.yml --check --diff'
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        sh 'ansible-playbook playbooks/site.yml -i inventory/production'
                    } else {
                        sh 'ansible-playbook playbooks/site.yml -i inventory/staging'
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend channel: '#deployments', message: "Deployment successful: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend channel: '#deployments', message: "Deployment failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
```

### 3.2 使用凭据绑定插件

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        ANSIBLE_VAULT_PASSWORD = credentials('ansible-vault-password')
        SSH_PRIVATE_KEY = credentials('ssh-private-key')
    }
    
    stages {
        stage('Deploy') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh '''
                        echo "$ANSIBLE_VAULT_PASSWORD" > ~/.vault_pass.txt
                        chmod 600 ~/.vault_pass.txt
                        ansible-playbook playbooks/site.yml --vault-password-file ~/.vault_pass.txt
                    '''
                }
            }
        }
    }
}
```

## 4. 凭证和安全管理

在 CI/CD 环境中安全地管理凭证至关重要。

### 4.1 使用 Ansible Vault

```yaml
# vault_secrets.yml
---
database_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  31323334353637383930616263646566

api_key: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  66656463626160595857565554535251
```

### 4.2 在 CI/CD 中使用 Vault

```bash
# 在 CI/CD 环境中安全传递 Vault 密码
echo "$VAULT_PASSWORD" > ~/.vault_pass.txt
ansible-playbook site.yml --vault-password-file ~/.vault_pass.txt
```

## 5. 测试和验证

确保基础设施变更的质量是 CI/CD 流水线的重要组成部分。

### 5.1 语法检查

```bash
# 检查 Playbook 语法
ansible-playbook site.yml --syntax-check
```

### 5.2 干运行测试

```bash
# 使用 --check 模式进行干运行
ansible-playbook site.yml --check --diff
```

### 5.3 使用 Molecule 进行测试

```yaml
# molecule/default/converge.yml
---
- name: Converge
  hosts: all
  tasks:
    - name: "Include site"
      include: "../../../playbooks/site.yml"
```

```yaml
# molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: geerlingguy/docker-ubuntu2004-ansible
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```

## 6. 监控和日志

在 CI/CD 环境中监控 Ansible 执行非常重要。

### 6.1 集中日志记录

```yaml
# logging_config.yml
---
- name: Configure centralized logging
  hosts: all
  tasks:
    - name: Install rsyslog
      package:
        name: rsyslog
        state: present
        
    - name: Configure remote logging
      lineinfile:
        path: /etc/rsyslog.conf
        line: "*.* @logserver.example.com:514"
        
    - name: Restart rsyslog
      service:
        name: rsyslog
        state: restarted
```

### 6.2 执行结果报告

```yaml
# reporting.yml
---
- name: Generate deployment report
  hosts: localhost
  tasks:
    - name: Create deployment report
      template:
        src: deployment_report.j2
        dest: /var/reports/deployment_{{ ansible_date_time.iso8601 }}.html
        
    - name: Send notification
      uri:
        url: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
        method: POST
        body: |
          {
            "text": "Deployment completed successfully",
            "attachments": [
              {
                "color": "good",
                "fields": [
                  {
                    "title": "Environment",
                    "value": "{{ target_environment }}",
                    "short": true
                  },
                  {
                    "title": "Timestamp",
                    "value": "{{ ansible_date_time.iso8601 }}",
                    "short": true
                  }
                ]
              }
            ]
          }
        body_format: json
```

## 7. 最佳实践

### 7.1 流水线设计

1. **分阶段执行**：将验证、测试和部署分为不同阶段
2. **环境分离**：为不同环境使用不同的 inventory
3. **手动审批**：在生产环境部署前添加手动审批步骤
4. **回滚机制**：实现快速回滚方案

### 7.2 安全实践

1. **凭据管理**：使用 CI/CD 平台的凭据管理功能
2. **最小权限**：为 CI/CD 用户分配最小必要权限
3. **审计日志**：记录所有自动化操作
4. **定期轮换**：定期轮换凭据和密钥

### 7.3 性能优化

1. **并行执行**：利用 Ansible 的并行执行能力
2. **缓存策略**：缓存依赖项以加快构建速度
3. **资源管理**：合理分配 CI/CD 执行器资源
4. **增量部署**：只部署变更的部分

通过本日的学习，您已经掌握了在主流 CI/CD 平台中集成 Ansible 的技术，包括 GitLab CI、GitHub Actions 和 Jenkins。这些技能将帮助您实现基础设施的自动化部署和管理，提高部署效率和可靠性。