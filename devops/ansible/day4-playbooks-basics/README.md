# Day 4: Ansible Playbooks 基础

## 🎯 今日学习目标

通过实际例子和动手实践，掌握 Ansible Playbooks 的核心概念和编写技巧。

## 📁 目录结构

```
day4-playbooks-basics/
├── playbooks-basics.md          # 详细学习文档
├── README.md                     # 快速开始指南 (本文件)
├── playbooks/                    # 实际可运行的 playbooks
│   ├── 01-system-info.yml       # 系统信息收集
│   ├── 02-web-server-setup.yml  # Web 服务器配置
│   └── 03-user-management.yml   # 用户和权限管理
├── examples/                     # 学习示例
│   └── basic-commands.md         # 基础命令参考
└── scripts/                      # 实用脚本
    └── run-playbooks.ps1         # PowerShell 运行脚本
```

## 🚀 快速开始

### 1. 环境检查

确保已完成前三天的学习并安装了 Ansible：

```bash
# 检查 Ansible 安装
ansible --version

# 检查 inventory 文件
ls ../day1-installation/configs/inventory.ini
```

### 2. 运行第一个 Playbook

最简单的系统信息收集：

```bash
# 进入 day4 目录
cd day4-playbooks-basics

# 运行系统信息收集 (安全，只读操作)
ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local -v
```

### 3. 使用 PowerShell 脚本 (Windows)

```powershell
# 运行交互式脚本
.\scripts\run-playbooks.ps1

# 或直接运行特定 playbook
.\scripts\run-playbooks.ps1 -PlaybookName "01-system-info.yml"
```

## 📚 学习路径

### 阶段 1: 基础理解 (30分钟)
1. 阅读 [`playbooks-basics.md`](playbooks-basics.md) 了解核心概念
2. 运行 `01-system-info.yml` 理解 playbook 结构
3. 查看 [`examples/basic-commands.md`](examples/basic-commands.md) 学习常用命令

### 阶段 2: 实际配置 (45分钟)
1. **检查模式运行** Web 服务器配置：
   ```bash
   ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --check
   ```
2. **实际运行** (需要管理员权限):
   ```bash
   ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --become
   ```
3. 访问 `http://localhost` 验证结果

### 阶段 3: 高级管理 (30分钟)
1. 运行用户管理 playbook (检查模式):
   ```bash
   ansible-playbook -i localhost, playbooks/03-user-management.yml --connection=local --check --become
   ```
2. 理解变量使用和循环操作
3. 学习错误处理和调试技巧

## 🛠️ 实践练习

### 练习 1: 修改和运行
修改 Web 服务器 playbook 中的变量，创建自己的配置：

```bash
ansible-playbook -i localhost, playbooks/02-web-server-setup.yml --connection=local --become \
  -e "server_name=mycompany.local document_root=/var/www/mycompany"
```

### 练习 2: 调试技能
练习使用调试命令：

```bash
# 语法检查
ansible-playbook playbooks/01-system-info.yml --syntax-check

# 列出所有任务
ansible-playbook playbooks/01-system-info.yml --list-tasks

# 步进模式
ansible-playbook -i localhost, playbooks/01-system-info.yml --connection=local --step
```

### 练习 3: 创建自己的 Playbook
基于学到的知识，创建一个简单的 playbook：

```yaml
---
- name: "我的第一个 Playbook"
  hosts: localhost
  connection: local
  tasks:
    - name: "创建测试目录"
      file:
        path: /tmp/my-ansible-test
        state: directory
        mode: '0755'
    
    - name: "创建测试文件"
      copy:
        content: "Hello Ansible!"
        dest: /tmp/my-ansible-test/hello.txt
```

## 📋 检查清单

完成 Day 4 学习后，你应该能够：

- [ ] 理解 Playbook 的基本结构 (Play, Task, Module, Handler)
- [ ] 编写基础的 Ansible Tasks
- [ ] 使用变量和 facts
- [ ] 处理条件判断和循环
- [ ] 运行和调试 playbooks
- [ ] 理解幂等性的概念
- [ ] 使用 handlers 处理服务重启
- [ ] 进行基本的错误处理

## 🔧 故障排除

### 常见问题

1. **权限错误**: 确保使用 `--become` 参数
2. **连接错误**: 检查 inventory 配置或使用 `--connection=local`
3. **模块不存在**: 确保 Ansible 版本支持所用模块
4. **语法错误**: 使用 `--syntax-check` 检查 YAML 语法

### 获取帮助

```bash
# 查看模块文档
ansible-doc file
ansible-doc copy
ansible-doc service

# 查看 playbook 帮助
ansible-playbook --help
```

## 📖 相关资源

- [Ansible 官方文档](https://docs.ansible.com/)
- [YAML 语法指南](https://yaml.org/spec/1.2/spec.html)
- [Jinja2 模板语法](https://jinja.palletsprojects.com/en/3.0.x/templates/)

## ➡️ 下一步

完成 Day 4 学习后，继续 Day 5: **变量和模板**，学习更高级的 Ansible 功能。

---

💡 **提示**: 始终在测试环境中实验新的 playbooks，生产环境部署前要充分测试！ 