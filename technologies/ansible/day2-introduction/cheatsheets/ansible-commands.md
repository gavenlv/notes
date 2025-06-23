# Ansible 命令速查表

## 🚀 基本命令格式

```bash
ansible <pattern> -m <module> -a <arguments> [options]
ansible-playbook playbook.yml [options]
ansible-galaxy <command> [options]
ansible-config <command> [options]
ansible-doc <module>
```

## 📋 Ad-hoc 命令

### 基础语法
```bash
# 基本格式
ansible <hosts> -m <module> -a "<module_args>"

# 示例
ansible all -m ping
ansible webservers -m setup
ansible databases -m shell -a "uptime"
```

### 主机模式 (Patterns)
```bash
# 所有主机
ansible all -m ping

# 特定组
ansible webservers -m ping

# 多个组
ansible webservers:databases -m ping

# 交集 (既在 webservers 又在 production)
ansible webservers:&production -m ping

# 排除 (webservers 组但不包括 staging)
ansible webservers:!staging -m ping

# 通配符
ansible web* -m ping

# 正则表达式
ansible ~web[0-9]+ -m ping

# 范围
ansible webservers[0:2] -m ping

# 单个主机
ansible web1.example.com -m ping
```

## 🔧 常用参数

### 连接参数
```bash
-i INVENTORY          # 指定 inventory 文件
-u USER              # 远程用户名
-k                   # 提示输入 SSH 密码
-K                   # 提示输入 sudo 密码
--private-key FILE   # SSH 私钥文件
--ssh-common-args    # SSH 公共参数
```

### 权限提升
```bash
--become             # 使用 sudo
--become-user USER   # 切换到指定用户
--become-method      # 提升方法 (sudo, su, etc.)
--ask-become-pass    # 提示输入提升密码
```

### 执行参数
```bash
-f FORKS            # 并行执行数 (默认5)
-C, --check         # 检查模式 (不执行)
-D, --diff          # 显示差异
--limit PATTERN     # 限制主机
-t TAGS             # 仅执行指定标签
--skip-tags TAGS    # 跳过指定标签
```

### 输出控制
```bash
-v                  # 详细输出 (verbose)
-vv                 # 更详细
-vvv                # 极详细 (包含连接调试)
-vvvv               # 包含SSH调试
--one-line          # 单行输出
--tree DIRECTORY    # 保存输出到目录
```

## 📦 核心模块快速参考

### 系统信息
```bash
# 收集系统信息
ansible all -m setup

# 过滤信息
ansible all -m setup -a "filter=ansible_os_family"
ansible all -m setup -a "filter=ansible_memory_mb"
ansible all -m setup -a "filter=ansible_default_ipv4"

# 连接测试
ansible all -m ping
```

### 命令执行
```bash
# 执行命令 (不支持shell特性)
ansible all -m command -a "uptime"
ansible all -m command -a "ls -la /tmp"

# Shell命令 (支持管道、重定向)
ansible all -m shell -a "ps aux | grep nginx"
ansible all -m shell -a "echo hello > /tmp/test.txt"

# 执行脚本
ansible all -m script -a "/path/to/script.sh"
```

### 文件操作
```bash
# 复制文件
ansible all -m copy -a "src=/tmp/file dest=/tmp/file"
ansible all -m copy -a "content='Hello World' dest=/tmp/hello.txt"

# 文件/目录管理
ansible all -m file -a "path=/tmp/test state=directory"
ansible all -m file -a "path=/tmp/test.txt state=touch"
ansible all -m file -a "path=/tmp/test state=absent"

# 模板文件
ansible all -m template -a "src=config.j2 dest=/etc/app.conf"

# 下载文件
ansible all -m get_url -a "url=http://example.com/file dest=/tmp/"

# 获取远程文件
ansible all -m fetch -a "src=/etc/hostname dest=/tmp/hostnames/"
```

### 包管理
```bash
# 通用包管理
ansible all -m package -a "name=git state=present"

# Ubuntu/Debian
ansible all -m apt -a "name=nginx state=present update_cache=yes"
ansible all -m apt -a "name=nginx state=absent purge=yes"

# RedHat/CentOS
ansible all -m yum -a "name=nginx state=present"
ansible all -m dnf -a "name=nginx state=latest"

# Python包
ansible all -m pip -a "name=django state=present"
```

### 服务管理
```bash
# 服务控制
ansible all -m service -a "name=nginx state=started"
ansible all -m service -a "name=nginx state=stopped"
ansible all -m service -a "name=nginx state=restarted"
ansible all -m service -a "name=nginx state=reloaded"

# 启用/禁用服务
ansible all -m service -a "name=nginx enabled=yes"
ansible all -m service -a "name=nginx enabled=no"

# Systemd 专用
ansible all -m systemd -a "name=nginx state=started daemon_reload=yes"
```

### 用户管理
```bash
# 用户操作
ansible all -m user -a "name=testuser state=present"
ansible all -m user -a "name=testuser state=absent remove=yes"
ansible all -m user -a "name=testuser groups=sudo append=yes"

# 组操作
ansible all -m group -a "name=developers state=present"
```

## 📚 Playbook 命令

### 基本执行
```bash
# 执行 playbook
ansible-playbook playbook.yml

# 检查语法
ansible-playbook --syntax-check playbook.yml

# 检查模式
ansible-playbook --check playbook.yml

# 显示差异
ansible-playbook --diff playbook.yml

# 指定 inventory
ansible-playbook -i inventory.ini playbook.yml
```

### 高级选项
```bash
# 限制主机
ansible-playbook --limit webservers playbook.yml

# 指定标签
ansible-playbook --tags deploy playbook.yml
ansible-playbook --skip-tags config playbook.yml

# 从特定任务开始
ansible-playbook --start-at-task "Install packages" playbook.yml

# 变量传递
ansible-playbook -e "env=production" playbook.yml
ansible-playbook -e "@vars.yml" playbook.yml

# 并发控制
ansible-playbook -f 20 playbook.yml

# 详细输出
ansible-playbook -vv playbook.yml
```

## 🌟 Ansible Galaxy

### Role 管理
```bash
# 搜索 role
ansible-galaxy search apache

# 安装 role
ansible-galaxy install geerlingguy.apache

# 安装到指定目录
ansible-galaxy install -p roles/ geerlingguy.apache

# 列出已安装的 roles
ansible-galaxy list

# 删除 role
ansible-galaxy remove geerlingguy.apache

# 从文件安装
ansible-galaxy install -r requirements.yml
```

### Collection 管理
```bash
# 安装 collection
ansible-galaxy collection install community.general

# 列出 collections
ansible-galaxy collection list

# 安装指定版本
ansible-galaxy collection install community.general:1.3.0
```

## 🔍 信息查询

### 配置查询
```bash
# 查看配置
ansible-config list
ansible-config dump
ansible-config view

# 查看当前配置
ansible-config dump --only-changed
```

### 模块文档
```bash
# 查看模块文档
ansible-doc copy
ansible-doc -l                 # 列出所有模块
ansible-doc -l | grep file     # 搜索相关模块
ansible-doc -s copy            # 简短语法
```

### Inventory 查询
```bash
# 列出主机
ansible-inventory --list
ansible-inventory --host web1.example.com

# 图形化显示
ansible-inventory --graph
```

## 💡 实用技巧

### 调试技巧
```bash
# 查看将要执行的主机
ansible all --list-hosts

# 检查连接
ansible all -m ping -o

# 并行执行
ansible all -m shell -a "hostname" -f 20

# 超时控制
ansible all -m shell -a "sleep 10" -T 5
```

### 过滤和格式化
```bash
# JSON 输出
ansible all -m setup | jq '.'

# 保存输出
ansible all -m setup --tree /tmp/facts

# 单行输出
ansible all -m ping -o
```

### 变量使用
```bash
# 设置变量
ansible all -m debug -a "var=ansible_os_family"

# 使用额外变量
ansible all -m debug -a "msg='Hello {{ name }}'" -e "name=World"
```

## 🚨 常见问题

### 连接问题
```bash
# SSH 连接问题
ansible all -m ping -vvv

# 跳过主机密钥检查
ansible all -m ping -e "ansible_ssh_common_args='-o StrictHostKeyChecking=no'"

# 使用密码连接
ansible all -m ping -k

# 使用不同端口
ansible all -m ping -e "ansible_port=2222"
```

### 权限问题
```bash
# 使用 sudo
ansible all -m shell -a "whoami" --become

# 指定 sudo 用户
ansible all -m shell -a "whoami" --become --become-user=root

# 提示输入密码
ansible all -m shell -a "whoami" --become -K
```

---

💡 **提示**: 使用 `ansible-doc <module>` 查看详细的模块文档和示例！ 