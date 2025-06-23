# Ansible 基础命令示例

## Ad-hoc 命令示例

### 1. Ping 测试
```bash
# 测试本地主机
ansible localhost -m ping

# 测试所有主机
ansible all -m ping

# 测试特定组
ansible webservers -m ping

# 使用指定的 inventory 文件
ansible all -i inventory.ini -m ping
```

### 2. 命令执行
```bash
# 执行简单命令
ansible all -m command -a "uptime"

# 使用 shell 模块 (支持管道、重定向等)
ansible all -m shell -a "ps aux | grep nginx"

# 在指定用户权限下执行
ansible all -m command -a "whoami" --become
```

### 3. 文件操作
```bash
# 复制文件
ansible all -m copy -a "src=/tmp/test.txt dest=/tmp/test.txt"

# 创建目录
ansible all -m file -a "path=/tmp/testdir state=directory"

# 删除文件
ansible all -m file -a "path=/tmp/test.txt state=absent"

# 修改文件权限
ansible all -m file -a "path=/tmp/test.txt mode=0644"
```

### 4. 包管理
```bash
# 安装软件包 (Ubuntu/Debian)
ansible all -m apt -a "name=nginx state=present" --become

# 安装软件包 (CentOS/RHEL)
ansible all -m yum -a "name=nginx state=present" --become

# 更新包缓存
ansible all -m apt -a "update_cache=yes" --become
```

### 5. 服务管理
```bash
# 启动服务
ansible all -m service -a "name=nginx state=started" --become

# 停止服务
ansible all -m service -a "name=nginx state=stopped" --become

# 重启服务
ansible all -m service -a "name=nginx state=restarted" --become

# 启用开机自启
ansible all -m service -a "name=nginx enabled=yes" --become
```

### 6. 用户管理
```bash
# 创建用户
ansible all -m user -a "name=testuser state=present" --become

# 删除用户
ansible all -m user -a "name=testuser state=absent" --become

# 修改用户密码 (加密后的密码)
ansible all -m user -a "name=testuser password=encrypted_password" --become
```

### 7. 收集信息
```bash
# 收集系统信息
ansible all -m setup

# 收集特定信息
ansible all -m setup -a "filter=ansible_os_family"

# 收集网络信息
ansible all -m setup -a "filter=ansible_default_ipv4"
```

## 常用参数

- `-i inventory`: 指定 inventory 文件
- `-m module`: 指定要使用的模块
- `-a args`: 模块参数
- `--become`: 使用权限提升 (sudo)
- `--become-user`: 指定提升到的用户
- `-u user`: 指定远程用户
- `-k`: 提示输入 SSH 密码
- `-K`: 提示输入 sudo 密码
- `-v, -vv, -vvv`: 详细输出级别
- `--check`: 检查模式 (不执行实际操作)
- `--diff`: 显示文件差异

## 使用示例

### 场景 1: 快速检查服务器状态
```bash
# 检查所有服务器是否在线
ansible all -m ping

# 检查系统负载
ansible all -m shell -a "uptime"

# 检查磁盘使用情况
ansible all -m shell -a "df -h"
```

### 场景 2: 批量配置管理
```bash
# 批量创建用户
ansible webservers -m user -a "name=deploy state=present shell=/bin/bash" --become

# 批量安装软件
ansible all -m package -a "name=git state=present" --become

# 批量更新系统
ansible all -m package -a "name=* state=latest" --become
```

### 场景 3: 紧急操作
```bash
# 紧急重启服务
ansible webservers -m service -a "name=apache2 state=restarted" --become

# 快速部署配置文件
ansible all -m copy -a "src=emergency.conf dest=/etc/app/emergency.conf backup=yes" --become

# 检查安全补丁
ansible all -m shell -a "apt list --upgradable | grep security" --become
```

## 最佳实践

1. **总是先测试**: 使用 `--check` 参数进行干跑
2. **使用 inventory 组**: 避免对所有主机执行操作
3. **备份重要文件**: 使用 `backup=yes` 参数
4. **记录操作**: 保存命令历史和输出日志
5. **权限最小化**: 只在必要时使用 `--become` 