# Day 3: Inventory 管理

## 📋 学习目标

- 深入理解 Ansible Inventory 的概念和作用
- 掌握多种 Inventory 格式 (INI, YAML, JSON)
- 学习主机组织和分组策略
- 掌握变量定义和优先级
- 实践动态 Inventory 和脚本
- 了解 Inventory 插件系统

## 🗂️ Inventory 概述

### 什么是 Inventory？

Inventory (清单) 是 Ansible 中定义和组织受管节点的核心组件：

- **主机列表**: 定义 Ansible 可以管理的所有主机
- **组织结构**: 将主机按逻辑分组
- **变量存储**: 为主机和组定义变量
- **连接信息**: 指定如何连接到各个主机

### Inventory 的重要性

1. **目标定位**: 确定任务执行的目标主机
2. **逻辑分组**: 便于批量管理相似主机
3. **环境隔离**: 区分开发、测试、生产环境
4. **配置管理**: 为不同主机提供不同配置

## 📁 Inventory 格式

### 1. INI 格式 (传统格式)

**基本语法**:
```ini
# 单个主机
web1.example.com

# 带连接信息的主机
web2.example.com ansible_host=192.168.1.10 ansible_user=ubuntu

# 主机组
[webservers]
web1.example.com
web2.example.com
web3.example.com

# 主机范围
[databases]
db[01:03].example.com

# 组变量
[webservers:vars]
http_port=80
nginx_version=1.18

# 组嵌套
[production:children]
webservers
databases
```

### 2. YAML 格式 (推荐格式)

**基本结构**:
```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 192.168.1.10
        web2.example.com:
          ansible_host: 192.168.1.11
      vars:
        http_port: 80
        nginx_version: "1.18"
    databases:
      hosts:
        db[01:03].example.com:
      vars:
        mysql_port: 3306
    production:
      children:
        webservers:
        databases:
      vars:
        environment: prod
```

### 3. JSON 格式

```json
{
  "all": {
    "hosts": ["localhost"],
    "children": {
      "webservers": {
        "hosts": ["web1.example.com", "web2.example.com"],
        "vars": {
          "http_port": 80
        }
      },
      "databases": {
        "hosts": ["db1.example.com", "db2.example.com"]
      }
    }
  }
}
```

## 🏗️ 主机组织策略

### 1. 按功能分组

```ini
[webservers]
web[01:05].example.com

[databases]
db[01:02].example.com

[loadbalancers]
lb[01:02].example.com

[cache]
redis[01:03].example.com
```

### 2. 按环境分组

```ini
[development]
dev-web[01:02].example.com
dev-db01.example.com

[staging]
stage-web[01:02].example.com
stage-db01.example.com

[production]
prod-web[01:05].example.com
prod-db[01:02].example.com
```

### 3. 按地域分组

```ini
[us-east]
us-east-web[01:03].example.com

[us-west]
us-west-web[01:03].example.com

[asia-pacific]
ap-web[01:02].example.com
```

### 4. 混合分组策略

详细示例见：[configs/inventory-advanced.yml](./configs/inventory-advanced.yml)

## 🔧 主机和组变量

### 1. 内置连接变量

```yaml
all:
  hosts:
    web1.example.com:
      ansible_host: 192.168.1.10          # 实际IP地址
      ansible_port: 22                     # SSH端口
      ansible_user: ubuntu                 # 远程用户名
      ansible_ssh_private_key_file: ~/.ssh/web.key  # 私钥文件
      ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
      ansible_python_interpreter: /usr/bin/python3   # Python解释器路径
      
    windows-host:
      ansible_host: 192.168.1.20
      ansible_connection: winrm            # Windows连接方式
      ansible_winrm_transport: basic
      ansible_port: 5985
```

### 2. 自定义变量

```yaml
webservers:
  hosts:
    web1.example.com:
      server_id: web01
      max_connections: 1000
    web2.example.com:
      server_id: web02
      max_connections: 2000
  vars:
    http_port: 80
    https_port: 443
    nginx_version: "1.18"
    app_name: "myapp"
    environment: "production"
```

### 3. 变量优先级

从高到低的优先级：
1. Extra vars (`-e` 命令行变量)
2. Task vars (任务变量)
3. Block vars (块变量)
4. Role and include vars
5. Play vars
6. Host facts
7. Host vars (主机变量)
8. Group vars (组变量)
9. Default vars (默认变量)

## 📊 Inventory 插件

### 1. 静态插件

```ini
# 启用插件
[inventory]
enable_plugins = host_list, script, auto, yaml, ini, toml
```

### 2. 动态插件示例

云平台插件配置见：[configs/aws-inventory.yml](./configs/aws-inventory.yml)

## 🚀 实践示例

### 示例 1: 企业级 Inventory 结构

详细配置见：[examples/enterprise-inventory.yml](./examples/enterprise-inventory.yml)

### 示例 2: 多环境管理

```bash
# 目录结构
inventories/
├── production/
│   ├── hosts.yml
│   └── group_vars/
│       ├── all.yml
│       ├── webservers.yml
│       └── databases.yml
├── staging/
│   ├── hosts.yml
│   └── group_vars/
│       ├── all.yml
│       ├── webservers.yml
│       └── databases.yml
└── development/
    ├── hosts.yml
    └── group_vars/
        ├── all.yml
        ├── webservers.yml
        └── databases.yml

# 使用方式
ansible-playbook -i inventories/production/hosts.yml site.yml
ansible-playbook -i inventories/staging/hosts.yml site.yml
```

### 示例 3: 动态 Inventory 脚本

脚本示例见：[scripts/dynamic-inventory.py](./scripts/dynamic-inventory.py)

## 🔍 Inventory 验证和调试

### 1. 基本验证命令

```bash
# 列出所有主机
ansible-inventory --list

# 列出特定主机信息
ansible-inventory --host web1.example.com

# 图形化显示组结构
ansible-inventory --graph

# 验证 inventory 语法
ansible-inventory --list --check

# 导出为 JSON
ansible-inventory --list --output /tmp/inventory.json
```

### 2. 调试技巧

```bash
# 查看主机变量
ansible-inventory --host web1.example.com --vars

# 测试主机连接
ansible all -m ping -i inventory.yml

# 查看将要执行的主机
ansible webservers --list-hosts -i inventory.yml

# 验证组成员
ansible production --list-hosts -i inventory.yml
```

## 🛠️ 高级功能

### 1. 主机模式 (Host Patterns)

```bash
# 所有主机
ansible all -m ping

# 特定组
ansible webservers -m ping

# 多个组 (并集)
ansible webservers:databases -m ping

# 交集
ansible webservers:&production -m ping

# 排除
ansible all:!staging -m ping

# 通配符
ansible web* -m ping

# 正则表达式
ansible ~web[0-9]+ -m ping

# 范围
ansible webservers[0:2] -m ping

# 复合模式
ansible 'webservers:!web3*:&production' -m ping
```

### 2. 变量文件组织

```bash
# group_vars 目录结构
group_vars/
├── all.yml                 # 所有主机的变量
├── webservers.yml         # webservers 组变量
├── databases.yml          # databases 组变量
└── production/            # production 组的多文件变量
    ├── vars.yml
    ├── secrets.yml
    └── database.yml

# host_vars 目录结构
host_vars/
├── web1.example.com.yml   # 单个主机变量
├── db1.example.com.yml
└── web2.example.com/      # 单个主机的多文件变量
    ├── vars.yml
    └── secrets.yml
```

### 3. 条件主机包含

```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
        web2.example.com:
          # 只有在生产环境才包含
          ansible_host: "{{ '192.168.1.11' if environment == 'production' else '10.0.1.11' }}"
```

## 📝 实验练习

### 练习 1: 基础 Inventory 创建

```bash
# 1. 创建 INI 格式的 inventory
# 2. 转换为 YAML 格式
# 3. 验证语法和连接性
# 4. 测试不同的主机模式
```

### 练习 2: 多环境 Inventory 管理

```bash
# 1. 设计三套环境的 inventory 结构
# 2. 创建对应的 group_vars
# 3. 实现环境间的变量差异化
# 4. 测试环境隔离效果
```

### 练习 3: 动态 Inventory 开发

```bash
# 1. 编写简单的动态 inventory 脚本
# 2. 集成外部数据源 (如数据库、API)
# 3. 实现缓存机制
# 4. 测试动态发现功能
```

## 📚 最佳实践

### 1. 命名规范

```bash
# 主机命名
web01.prod.example.com
db01.staging.example.com
cache01.dev.example.com

# 组命名
webservers_production
databases_staging
loadbalancers_development
```

### 2. 目录结构

```bash
ansible-project/
├── inventories/
│   ├── production/
│   ├── staging/
│   └── development/
├── group_vars/
├── host_vars/
├── playbooks/
└── roles/
```

### 3. 安全考虑

- 使用 Ansible Vault 加密敏感变量
- 限制 inventory 文件的访问权限
- 避免在 inventory 中硬编码密码
- 使用 SSH 密钥而非密码认证

## 🔧 故障排除

### 常见问题

1. **主机连接失败**
   ```bash
   # 检查 SSH 连接
   ansible web1.example.com -m ping -vvv
   
   # 验证 inventory 配置
   ansible-inventory --host web1.example.com
   ```

2. **变量未生效**
   ```bash
   # 检查变量优先级
   ansible-inventory --host web1.example.com --vars
   
   # 验证变量文件语法
   ansible-playbook --syntax-check playbook.yml
   ```

3. **组嵌套问题**
   ```bash
   # 查看组结构
   ansible-inventory --graph
   
   # 验证组成员
   ansible production --list-hosts
   ```

## 📖 参考资源

- [Ansible Inventory Guide](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
- [Inventory Plugins](https://docs.ansible.com/ansible/latest/plugins/inventory.html)
- [Working with Patterns](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html)

## ✅ 检查清单

- [ ] 理解 Inventory 的基本概念和作用
- [ ] 掌握 INI 和 YAML 格式的 Inventory 编写
- [ ] 熟悉主机组织和分组策略
- [ ] 了解变量定义和优先级规则
- [ ] 完成基础和高级实验练习
- [ ] 掌握 Inventory 验证和调试方法
- [ ] 理解动态 Inventory 的原理和应用

---

**下一步**: [Day 4 - Playbooks 基础](../day4-playbooks-basics/playbooks-basics.md) 