# Day 1: Ansible 安装与环境配置

## 📋 学习目标

- 了解 Ansible 的基本概念和架构
- 在不同操作系统上安装 Ansible
- 配置 Ansible 控制节点和受管节点
- 验证安装和配置的正确性

## 🏗️ Ansible 架构概述

### 核心组件
- **Control Node (控制节点)**: 运行 Ansible 的机器
- **Managed Nodes (受管节点)**: 被 Ansible 管理的目标机器
- **Inventory (清单)**: 定义受管节点的文件
- **Playbooks (剧本)**: 定义任务的 YAML 文件
- **Modules (模块)**: 执行具体任务的代码单元

### 通信方式
- 默认使用 SSH 协议 (Linux/Unix)
- Windows 系统使用 WinRM
- 无需在受管节点安装客户端软件

## 🚀 安装 Ansible

### 方法 1: 使用 pip 安装 (推荐)

```bash
# 更新 pip
python3 -m pip install --upgrade pip

# 安装 Ansible
python3 -m pip install ansible

# 验证安装
ansible --version
```

#### 语法解析
- **`python3 -m pip install --upgrade pip`**: 使用 Python 模块方式运行 pip 工具，`-m` 参数表示运行模块，`--upgrade` 确保 pip 是最新版本
- **`python3 -m pip install ansible`**: 安装 Ansible 核心包，包含所有基础模块和工具
- **`ansible --version`**: 验证安装成功，显示 Ansible 版本、Python 版本和可执行文件路径

#### 安装说明
- **pip 安装优势**: 可以安装最新版本，支持虚拟环境隔离
- **Python 版本要求**: Ansible 需要 Python 3.6 或更高版本
- **依赖管理**: pip 会自动处理 Ansible 的依赖关系

### 方法 2: 使用系统包管理器

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible
```

#### 语法解析
- **`software-properties-common`**: 提供 `add-apt-repository` 命令，用于管理软件仓库
- **`ppa:ansible/ansible`**: Ansible 官方 PPA (Personal Package Archive) 仓库
- **`--yes --update`**: 自动确认并更新软件包列表

#### CentOS/RHEL/Rocky Linux
```bash
# 安装 EPEL 仓库
sudo dnf install epel-release
sudo dnf install ansible
```

#### 语法解析
- **`epel-release`**: Extra Packages for Enterprise Linux 仓库，提供额外的软件包
- **`dnf`**: Dandified YUM，新一代的包管理器，替代 yum

#### macOS
```bash
# 使用 Homebrew
brew install ansible
```

#### 语法解析
- **Homebrew**: macOS 的包管理器，自动处理依赖和路径配置

### 方法 3: 使用 Conda
```bash
conda install -c conda-forge ansible
```

#### 语法解析
- **`conda`**: Python 包和环境管理器，支持虚拟环境隔离
- **`-c conda-forge`**: 指定使用 conda-forge 社区仓库
- **优势**: 环境隔离，避免系统 Python 冲突

## ⚙️ 基础配置

### 1. 创建配置文件

Ansible 会按以下顺序查找配置文件：
1. `ANSIBLE_CONFIG` 环境变量指定的文件
2. 当前目录的 `ansible.cfg`
3. 用户主目录的 `.ansible.cfg`
4. `/etc/ansible/ansible.cfg`

### 2. 配置 SSH 密钥认证

```bash
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 复制公钥到目标主机
ssh-copy-id user@target_host

# 测试 SSH 连接
ssh user@target_host
```

#### 语法解析
- **`ssh-keygen -t rsa -b 4096`**: 生成 RSA 类型、4096 位长度的密钥对，`-t` 指定密钥类型，`-b` 指定密钥长度
- **`-C "your_email@example.com"`**: 添加注释信息，通常使用邮箱作为标识
- **`ssh-copy-id`**: 自动将公钥复制到目标主机的 `~/.ssh/authorized_keys` 文件
- **SSH 密钥认证优势**: 比密码认证更安全，支持自动化操作

#### 安全最佳实践
- 使用强密码保护私钥（可选）
- 定期轮换密钥对
- 限制公钥的使用范围

### 3. 配置文件示例

详细配置见：[configs/ansible.cfg](./configs/ansible.cfg)

## 🧪 环境验证

### 1. 版本检查
```bash
ansible --version
ansible-playbook --version
ansible-galaxy --version
```

#### 语法解析
- **`ansible --version`**: 显示 Ansible 核心版本、Python 版本和配置路径
- **`ansible-playbook --version`**: 验证 playbook 执行器可用性
- **`ansible-galaxy --version`**: 检查角色管理工具状态
- **输出信息**: 包含版本号、Python 路径、模块搜索路径等关键信息

### 2. 连接测试
```bash
# 测试本地连接
ansible localhost -m ping

# 测试远程主机连接
ansible all -m ping -i inventory.ini
```

#### 语法解析
- **`ansible localhost -m ping`**: 测试本地连接，`-m ping` 使用 ping 模块
- **`ansible all -m ping -i inventory.ini`**: 测试所有主机连接，`-i` 指定 inventory 文件
- **ping 模块**: 返回 `pong` 表示连接成功，是最基础的连接测试
- **localhost**: 特殊主机名，指向当前控制节点

### 3. 运行测试脚本

```bash
# Windows PowerShell
.\scripts\test-installation.ps1

# Linux/macOS
./scripts/test-installation.sh
```

#### 语法解析
- **PowerShell 脚本**: 适用于 Windows 环境，包含完整的安装验证流程
- **Shell 脚本**: 适用于 Linux/macOS，包含依赖检查和连接测试
- **脚本功能**: 自动化验证安装完整性，减少手动检查步骤

## 🐳 Docker 环境 (可选)

如果你想在容器中测试 Ansible：

```bash
# 构建测试环境
docker-compose -f configs/docker-compose.yml up -d

# 进入 Ansible 控制容器
docker exec -it ansible-control bash
```

## 🔧 故障排除

### 常见问题

1. **Python 版本不兼容**
   ```bash
   # 检查 Python 版本
   python3 --version
   # Ansible 需要 Python 3.6+
   ```

2. **SSH 连接失败**
   ```bash
   # 检查 SSH 配置
   ssh -vvv user@target_host
   
   # 检查防火墙设置
   sudo ufw status
   ```

3. **权限问题**
   ```bash
   # 检查用户权限
   sudo -l
   
   # 配置 sudo 免密码
   echo "username ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/username
   ```

## 📝 实践练习

1. **基础安装练习**
   - 在本地安装 Ansible
   - 创建基本配置文件
   - 测试 localhost 连接

2. **多节点环境练习**
   - 设置至少 2 个虚拟机
   - 配置 SSH 密钥认证
   - 创建 inventory 文件
   - 测试所有节点连接

## 📚 参考资源

- [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html)
- [Ansible Configuration Settings](https://docs.ansible.com/ansible/latest/reference_appendices/config.html)
- [SSH Connection Plugin](https://docs.ansible.com/ansible/latest/plugins/connection/ssh.html)

## ✅ 检查清单

- [ ] Ansible 成功安装
- [ ] 配置文件创建并生效
- [ ] SSH 密钥认证配置完成
- [ ] 本地 ping 测试成功
- [ ] 远程主机 ping 测试成功
- [ ] 理解 Ansible 基本架构

---

**下一步**: [Day 2 - Ansible 基础介绍](../day2-introduction/introduction.md) 