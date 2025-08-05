# Day 8: Ansible 模块与插件开发

## 📚 学习目标

通过本天的学习，您将掌握：

- **自定义模块开发**：从零开始创建 Ansible 模块
- **插件系统理解**：深入理解 Ansible 插件架构
- **开发环境搭建**：配置模块和插件开发环境
- **测试与调试**：模块测试和调试技巧
- **发布与分享**：模块打包和分发方法
- **最佳实践**：企业级模块开发规范

## 🎯 核心概念

### 1. Ansible 扩展机制

#### 模块 vs 插件
```yaml
# 模块 (Modules)
- 任务执行的基本单元
- 在目标主机上执行
- 返回 JSON 格式结果
- 示例：copy, file, service

# 插件 (Plugins)
- 扩展 Ansible 核心功能
- 在控制节点执行
- 包含多种类型：连接、过滤器、查找等
- 示例：ssh 连接插件、jinja2 过滤器
```

#### 扩展类型
```python
# 1. 模块 (Modules)
- 操作目标主机的基本单元
- 实现具体的系统操作

# 2. 动作插件 (Action Plugins)
- 在控制节点执行的模块前处理
- 用于复杂的逻辑处理

# 3. 连接插件 (Connection Plugins)
- 定义如何连接到目标主机
- 如 SSH、WinRM、Docker 等

# 4. 过滤器插件 (Filter Plugins)
- 扩展 Jinja2 模板过滤器
- 用于数据转换和处理

# 5. 查找插件 (Lookup Plugins)
- 从外部数据源获取数据
- 如文件、数据库、API 等
```

### 2. 模块开发架构

#### 模块结构
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# 版权和许可证信息
DOCUMENTATION = '''
---
module: my_custom_module
short_description: 模块简短描述
description:
    - 模块详细描述
    - 功能说明
options:
    name:
        description:
            - 参数描述
        required: true
        type: str
    state:
        description:
            - 期望状态
        required: false
        default: present
        choices: ['present', 'absent']
        type: str
'''

EXAMPLES = '''
# 使用示例
- name: 示例任务
  my_custom_module:
    name: example
    state: present
'''

RETURN = '''
# 返回值说明
result:
    description: 操作结果
    returned: always
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule

def main():
    # 模块主逻辑
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', 
                      choices=['present', 'absent'])
        ),
        supports_check_mode=True
    )
    
    # 实现模块逻辑
    # ...
    
    module.exit_json(changed=False, msg="Success")

if __name__ == '__main__':
    main()
```

## 🛠️ 实践项目

### 项目1: 文件管理模块

#### 需求分析
```yaml
# 自定义文件管理模块
功能需求:
  - 创建/删除文件
  - 设置文件权限
  - 备份现有文件
  - 验证文件内容
  - 支持模板替换
```

#### 模块实现
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: advanced_file
short_description: 高级文件管理模块
description:
    - 提供文件创建、删除、备份等高级功能
    - 支持模板替换和内容验证
    - 集成权限管理和备份策略
options:
    path:
        description:
            - 文件路径
        required: true
        type: path
    content:
        description:
            - 文件内容
        required: false
        type: str
    template:
        description:
            - 模板文件路径
        required: false
        type: path
    backup:
        description:
            - 是否备份现有文件
        required: false
        default: false
        type: bool
    mode:
        description:
            - 文件权限模式
        required: false
        type: str
    owner:
        description:
            - 文件所有者
        required: false
        type: str
    group:
        description:
            - 文件所属组
        required: false
        type: str
    state:
        description:
            - 文件状态
        required: false
        default: present
        choices: ['present', 'absent', 'touch']
        type: str
    validate:
        description:
            - 验证命令
        required: false
        type: str
'''

EXAMPLES = '''
# 创建文件
- name: 创建配置文件
  advanced_file:
    path: /etc/myapp/config.conf
    content: |
      server_name = {{ ansible_hostname }}
      port = 8080
    mode: '0644'
    owner: root
    group: root
    backup: true

# 使用模板
- name: 使用模板创建文件
  advanced_file:
    path: /etc/nginx/sites-available/mysite
    template: templates/nginx.conf.j2
    mode: '0644'
    validate: 'nginx -t -c %s'
    backup: true

# 删除文件
- name: 删除临时文件
  advanced_file:
    path: /tmp/temp_file
    state: absent
'''

RETURN = '''
path:
    description: 文件路径
    returned: always
    type: str
    sample: /etc/myapp/config.conf
changed:
    description: 是否发生变更
    returned: always
    type: bool
backup_file:
    description: 备份文件路径
    returned: when backup is true
    type: str
    sample: /etc/myapp/config.conf.backup.2023-12-01
msg:
    description: 操作消息
    returned: always
    type: str
'''

import os
import shutil
import tempfile
import subprocess
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native

def backup_file(path):
    """备份文件"""
    if os.path.exists(path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{path}.backup.{timestamp}"
        shutil.copy2(path, backup_path)
        return backup_path
    return None

def validate_file(path, validate_cmd):
    """验证文件"""
    if validate_cmd:
        cmd = validate_cmd.replace('%s', path)
        try:
            subprocess.run(cmd, shell=True, check=True, 
                         capture_output=True, text=True)
            return True, ""
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    return True, ""

def render_template(template_path, variables):
    """渲染模板"""
    try:
        from jinja2 import Template
        with open(template_path, 'r') as f:
            template_content = f.read()
        template = Template(template_content)
        return template.render(variables)
    except ImportError:
        raise Exception("Jinja2 is required for template rendering")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            content=dict(type='str'),
            template=dict(type='path'),
            backup=dict(type='bool', default=False),
            mode=dict(type='str'),
            owner=dict(type='str'),
            group=dict(type='str'),
            state=dict(type='str', default='present', 
                      choices=['present', 'absent', 'touch']),
            validate=dict(type='str')
        ),
        mutually_exclusive=[['content', 'template']],
        supports_check_mode=True
    )
    
    path = module.params['path']
    content = module.params['content']
    template = module.params['template']
    backup = module.params['backup']
    mode = module.params['mode']
    owner = module.params['owner']
    group = module.params['group']
    state = module.params['state']
    validate_cmd = module.params['validate']
    
    result = dict(
        changed=False,
        path=path
    )
    
    # 检查文件是否存在
    file_exists = os.path.exists(path)
    
    if state == 'absent':
        if file_exists:
            if not module.check_mode:
                os.remove(path)
            result['changed'] = True
            result['msg'] = f"File {path} removed"
        else:
            result['msg'] = f"File {path} does not exist"
    
    elif state == 'touch':
        if not file_exists:
            if not module.check_mode:
                open(path, 'a').close()
            result['changed'] = True
            result['msg'] = f"File {path} created"
        else:
            result['msg'] = f"File {path} already exists"
    
    elif state == 'present':
        # 备份现有文件
        backup_path = None
        if backup and file_exists:
            backup_path = backup_file(path)
            result['backup_file'] = backup_path
        
        # 准备文件内容
        if template:
            # 获取 Ansible 变量
            variables = module.params.get('variables', {})
            variables.update({
                'ansible_hostname': os.uname().nodename,
                'ansible_date_time': datetime.now().isoformat()
            })
            file_content = render_template(template, variables)
        elif content:
            file_content = content
        else:
            file_content = ""
        
        # 检查内容是否需要更新
        needs_update = True
        if file_exists:
            try:
                with open(path, 'r') as f:
                    current_content = f.read()
                needs_update = current_content != file_content
            except IOError:
                needs_update = True
        
        if needs_update:
            if not module.check_mode:
                # 写入文件
                try:
                    with open(path, 'w') as f:
                        f.write(file_content)
                except IOError as e:
                    module.fail_json(msg=f"Failed to write file: {to_native(e)}")
                
                # 验证文件
                if validate_cmd:
                    valid, error = validate_file(path, validate_cmd)
                    if not valid:
                        # 恢复备份
                        if backup_path:
                            shutil.copy2(backup_path, path)
                        module.fail_json(msg=f"Validation failed: {error}")
                
                # 设置权限
                if mode:
                    os.chmod(path, int(mode, 8))
                
                # 设置所有者和组
                if owner or group:
                    import pwd
                    import grp
                    uid = pwd.getpwnam(owner).pw_uid if owner else -1
                    gid = grp.getgrnam(group).gr_gid if group else -1
                    os.chown(path, uid, gid)
            
            result['changed'] = True
            result['msg'] = f"File {path} updated"
        else:
            result['msg'] = f"File {path} is already up to date"
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

### 项目2: 系统信息收集模块

#### 模块设计
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: system_info
short_description: 系统信息收集模块
description:
    - 收集详细的系统信息
    - 支持自定义信息类型
    - 提供性能监控数据
options:
    info_type:
        description:
            - 信息类型
        required: false
        default: all
        choices: ['all', 'hardware', 'network', 'storage', 'processes']
        type: str
    format:
        description:
            - 输出格式
        required: false
        default: json
        choices: ['json', 'yaml', 'table']
        type: str
'''

import platform
import psutil
import json
from ansible.module_utils.basic import AnsibleModule

def get_hardware_info():
    """获取硬件信息"""
    return {
        'cpu_count': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': {
            partition.mountpoint: {
                'total': psutil.disk_usage(partition.mountpoint).total,
                'used': psutil.disk_usage(partition.mountpoint).used,
                'free': psutil.disk_usage(partition.mountpoint).free
            }
            for partition in psutil.disk_partitions()
        }
    }

def get_network_info():
    """获取网络信息"""
    return {
        'interfaces': dict(psutil.net_if_addrs()),
        'connections': len(psutil.net_connections()),
        'io_counters': dict(psutil.net_io_counters(pernic=True))
    }

def get_process_info():
    """获取进程信息"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return {'processes': processes[:10]}  # 返回前10个进程

def main():
    module = AnsibleModule(
        argument_spec=dict(
            info_type=dict(type='str', default='all', 
                          choices=['all', 'hardware', 'network', 'storage', 'processes']),
            format=dict(type='str', default='json', 
                       choices=['json', 'yaml', 'table'])
        ),
        supports_check_mode=True
    )
    
    info_type = module.params['info_type']
    output_format = module.params['format']
    
    result = {
        'changed': False,
        'system_info': {}
    }
    
    # 收集基本系统信息
    result['system_info']['basic'] = {
        'hostname': platform.node(),
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'uptime': psutil.boot_time()
    }
    
    # 根据类型收集特定信息
    if info_type in ['all', 'hardware']:
        result['system_info']['hardware'] = get_hardware_info()
    
    if info_type in ['all', 'network']:
        result['system_info']['network'] = get_network_info()
    
    if info_type in ['all', 'processes']:
        result['system_info']['processes'] = get_process_info()
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

## 🔌 插件开发

### 1. 过滤器插件

#### 自定义过滤器
```python
# filter_plugins/custom_filters.py

def to_title_case(value):
    """转换为标题格式"""
    return value.title()

def extract_domain(email):
    """从邮箱提取域名"""
    if '@' in email:
        return email.split('@')[1]
    return ''

def format_bytes(bytes_value):
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def json_query_extended(data, query):
    """扩展的 JSON 查询"""
    try:
        import jmespath
        return jmespath.search(query, data)
    except ImportError:
        return None

class FilterModule(object):
    """自定义过滤器模块"""
    
    def filters(self):
        return {
            'to_title_case': to_title_case,
            'extract_domain': extract_domain,
            'format_bytes': format_bytes,
            'json_query_extended': json_query_extended
        }
```

#### 使用示例
```yaml
# 使用自定义过滤器
- name: 使用自定义过滤器
  debug:
    msg: |
      标题格式: {{ "hello world" | to_title_case }}
      域名: {{ "user@example.com" | extract_domain }}
      文件大小: {{ 1048576 | format_bytes }}
      JSON查询: {{ complex_data | json_query_extended('users[?active].name') }}
```

### 2. 查找插件

#### 数据库查找插件
```python
# lookup_plugins/database_lookup.py

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

class LookupModule(LookupBase):
    """数据库查找插件"""
    
    def run(self, terms, variables=None, **kwargs):
        """执行查找"""
        results = []
        
        # 获取数据库连接参数
        db_host = kwargs.get('host', 'localhost')
        db_port = kwargs.get('port', 5432)
        db_name = kwargs.get('database', 'postgres')
        db_user = kwargs.get('user', 'postgres')
        db_password = kwargs.get('password', '')
        
        try:
            import psycopg2
            
            # 连接数据库
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            cursor = conn.cursor()
            
            # 执行查询
            for term in terms:
                cursor.execute(term)
                rows = cursor.fetchall()
                results.extend(rows)
            
            conn.close()
            
        except ImportError:
            raise AnsibleError("psycopg2 is required for database lookup")
        except Exception as e:
            raise AnsibleError(f"Database lookup failed: {str(e)}")
        
        return results
```

#### 使用示例
```yaml
# 使用数据库查找插件
- name: 查询用户信息
  debug:
    msg: "{{ lookup('database', 'SELECT * FROM users WHERE active = true', 
                    host='localhost', database='myapp', 
                    user='readonly', password='secret') }}"
```

### 3. 连接插件

#### 自定义连接插件
```python
# connection_plugins/custom_ssh.py

from ansible.plugins.connection import ConnectionBase
from ansible.errors import AnsibleConnectionFailure
import subprocess

class Connection(ConnectionBase):
    """自定义SSH连接插件"""
    
    transport = 'custom_ssh'
    
    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        self.host = self._play_context.remote_addr
        self.port = self._play_context.port or 22
        self.user = self._play_context.remote_user
        
    def _connect(self):
        """建立连接"""
        self._display.vvv(f"Connecting to {self.host}:{self.port} as {self.user}")
        # 实现连接逻辑
        
    def exec_command(self, cmd, in_data=None, sudoable=True):
        """执行命令"""
        ssh_cmd = [
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-p', str(self.port),
            f'{self.user}@{self.host}',
            cmd
        ]
        
        try:
            process = subprocess.Popen(
                ssh_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=in_data)
            return_code = process.returncode
            
            return return_code, stdout, stderr
            
        except Exception as e:
            raise AnsibleConnectionFailure(f"SSH execution failed: {str(e)}")
    
    def put_file(self, in_path, out_path):
        """上传文件"""
        scp_cmd = [
            'scp',
            '-P', str(self.port),
            in_path,
            f'{self.user}@{self.host}:{out_path}'
        ]
        
        try:
            subprocess.run(scp_cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise AnsibleConnectionFailure(f"SCP upload failed: {str(e)}")
    
    def fetch_file(self, in_path, out_path):
        """下载文件"""
        scp_cmd = [
            'scp',
            '-P', str(self.port),
            f'{self.user}@{self.host}:{in_path}',
            out_path
        ]
        
        try:
            subprocess.run(scp_cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise AnsibleConnectionFailure(f"SCP download failed: {str(e)}")
    
    def close(self):
        """关闭连接"""
        pass
```

## 🧪 测试与调试

### 1. 模块测试

#### 单元测试
```python
# tests/test_advanced_file.py

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

# 导入模块
import sys
sys.path.insert(0, '../modules')
from advanced_file import main, backup_file, validate_file

class TestAdvancedFile(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.txt')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_backup_file(self):
        """测试文件备份功能"""
        # 创建测试文件
        with open(self.test_file, 'w') as f:
            f.write('test content')
        
        # 测试备份
        backup_path = backup_file(self.test_file)
        self.assertTrue(os.path.exists(backup_path))
        
        # 验证备份内容
        with open(backup_path, 'r') as f:
            self.assertEqual(f.read(), 'test content')
    
    def test_validate_file(self):
        """测试文件验证功能"""
        # 创建测试文件
        with open(self.test_file, 'w') as f:
            f.write('test content')
        
        # 测试验证成功
        valid, error = validate_file(self.test_file, 'test -f %s')
        self.assertTrue(valid)
        self.assertEqual(error, '')
        
        # 测试验证失败
        valid, error = validate_file(self.test_file, 'test -d %s')
        self.assertFalse(valid)
    
    @patch('advanced_file.AnsibleModule')
    def test_module_present(self, mock_module):
        """测试模块 present 状态"""
        # 模拟模块参数
        mock_module.return_value.params = {
            'path': self.test_file,
            'content': 'test content',
            'template': None,
            'backup': False,
            'mode': None,
            'owner': None,
            'group': None,
            'state': 'present',
            'validate': None
        }
        mock_module.return_value.check_mode = False
        
        # 运行模块
        main()
        
        # 验证结果
        mock_module.return_value.exit_json.assert_called_once()
        call_args = mock_module.return_value.exit_json.call_args[1]
        self.assertTrue(call_args['changed'])

if __name__ == '__main__':
    unittest.main()
```

#### 集成测试
```yaml
# tests/integration/test_advanced_file.yml

- name: 测试高级文件模块
  hosts: localhost
  gather_facts: no
  
  tasks:
    - name: 创建测试文件
      advanced_file:
        path: /tmp/test_file.txt
        content: |
          This is a test file
          Created by advanced_file module
        mode: '0644'
        backup: true
      register: result
    
    - name: 验证文件创建
      assert:
        that:
          - result.changed
          - result.path == '/tmp/test_file.txt'
    
    - name: 验证文件内容
      slurp:
        src: /tmp/test_file.txt
      register: file_content
    
    - name: 检查内容正确性
      assert:
        that:
          - "'This is a test file' in (file_content.content | b64decode)"
    
    - name: 删除测试文件
      advanced_file:
        path: /tmp/test_file.txt
        state: absent
      register: delete_result
    
    - name: 验证文件删除
      assert:
        that:
          - delete_result.changed
    
    - name: 确认文件不存在
      stat:
        path: /tmp/test_file.txt
      register: file_stat
    
    - name: 验证文件已删除
      assert:
        that:
          - not file_stat.stat.exists
```

### 2. 调试技巧

#### 调试模块
```python
# 在模块中添加调试信息
def debug_log(module, message):
    """调试日志"""
    if module.params.get('debug', False):
        module.warn(f"DEBUG: {message}")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            # ... 其他参数
            debug=dict(type='bool', default=False)
        )
    )
    
    debug_log(module, "Module started")
    debug_log(module, f"Parameters: {module.params}")
    
    # ... 模块逻辑
```

#### 使用 ansible-test
```bash
# 运行模块测试
ansible-test units tests/test_advanced_file.py

# 运行集成测试
ansible-test integration tests/integration/

# 代码质量检查
ansible-test sanity --python 3.8

# 覆盖率测试
ansible-test coverage --python 3.8
```

## 📦 打包与发布

### 1. 模块打包

#### 目录结构
```
my_ansible_collection/
├── galaxy.yml
├── plugins/
│   ├── modules/
│   │   ├── advanced_file.py
│   │   └── system_info.py
│   ├── filter_plugins/
│   │   └── custom_filters.py
│   ├── lookup_plugins/
│   │   └── database_lookup.py
│   └── connection_plugins/
│       └── custom_ssh.py
├── roles/
├── playbooks/
├── tests/
├── docs/
└── README.md
```

#### galaxy.yml 配置
```yaml
# galaxy.yml
namespace: mycompany
name: utilities
version: 1.0.0
readme: README.md
authors:
  - "Your Name <your.email@example.com>"
description: >
  Advanced utilities collection for Ansible
  including custom modules and plugins
license:
  - MIT
tags:
  - utilities
  - modules
  - plugins
dependencies: {}
repository: https://github.com/mycompany/ansible-utilities
documentation: https://docs.mycompany.com/ansible-utilities
homepage: https://mycompany.com/ansible-utilities
issues: https://github.com/mycompany/ansible-utilities/issues
```

### 2. 发布流程

#### 构建集合
```bash
# 构建集合
ansible-galaxy collection build

# 安装本地集合
ansible-galaxy collection install mycompany-utilities-1.0.0.tar.gz

# 发布到 Galaxy
ansible-galaxy collection publish mycompany-utilities-1.0.0.tar.gz
```

#### 私有仓库
```bash
# 配置私有仓库
# ansible.cfg
[galaxy]
server_list = private_galaxy

[galaxy_server.private_galaxy]
url = https://galaxy.mycompany.com/
token = your_token_here

# 发布到私有仓库
ansible-galaxy collection publish mycompany-utilities-1.0.0.tar.gz --server private_galaxy
```

## 🎯 最佳实践

### 1. 开发规范

#### 代码质量
```python
# 1. 遵循 PEP 8 代码风格
# 2. 使用类型提示
def process_data(data: dict) -> dict:
    """处理数据"""
    return data

# 3. 完善的文档字符串
def my_function(param1: str, param2: int) -> bool:
    """
    函数描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
    
    Returns:
        返回值描述
    
    Raises:
        ValueError: 错误描述
    """
    pass

# 4. 错误处理
try:
    result = risky_operation()
except SpecificException as e:
    module.fail_json(msg=f"Operation failed: {str(e)}")
```

#### 性能优化
```python
# 1. 避免重复操作
def main():
    # 缓存昂贵的操作结果
    cache = {}
    
    def expensive_operation(key):
        if key not in cache:
            cache[key] = perform_calculation(key)
        return cache[key]

# 2. 使用生成器处理大数据
def process_large_dataset(data):
    for item in data:
        yield process_item(item)

# 3. 异步操作
import asyncio

async def async_operation():
    tasks = [async_task(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 安全考虑

#### 输入验证
```python
def validate_input(module, param_name, value):
    """验证输入参数"""
    if param_name == 'path':
        if not os.path.isabs(value):
            module.fail_json(msg=f"Path must be absolute: {value}")
        if '..' in value:
            module.fail_json(msg=f"Path traversal not allowed: {value}")
    
    elif param_name == 'command':
        dangerous_commands = ['rm -rf', 'dd if=', 'mkfs']
        if any(cmd in value for cmd in dangerous_commands):
            module.fail_json(msg=f"Dangerous command detected: {value}")

def main():
    module = AnsibleModule(...)
    
    # 验证所有输入
    for param, value in module.params.items():
        if value is not None:
            validate_input(module, param, value)
```

#### 权限控制
```python
def check_permissions(path, required_perms):
    """检查文件权限"""
    import stat
    
    if not os.path.exists(path):
        return False
    
    file_stat = os.stat(path)
    file_perms = stat.filemode(file_stat.st_mode)
    
    # 检查权限逻辑
    return True  # 简化示例
```

### 3. 文档规范

#### 模块文档
```python
DOCUMENTATION = '''
---
module: my_module
short_description: 简短描述（一行）
description:
    - 详细描述第一段
    - 详细描述第二段
    - 支持的功能说明
version_added: "2.9"
author:
    - "Your Name (@github_username)"
options:
    parameter_name:
        description:
            - 参数详细描述
            - 支持多行描述
        type: str
        required: true
        default: null
        choices: ['option1', 'option2']
        aliases: ['param_alias']
        version_added: "2.10"
requirements:
    - python >= 3.6
    - requests >= 2.20.0
notes:
    - 重要注意事项
    - 使用限制说明
seealso:
    - module: related_module
    - name: External documentation
      description: Description of external docs
      link: https://example.com/docs
'''

EXAMPLES = '''
# 基本使用
- name: 基本示例
  my_module:
    parameter_name: value

# 高级使用
- name: 高级示例
  my_module:
    parameter_name: value
    optional_param: optional_value
  register: result

# 条件使用
- name: 条件示例
  my_module:
    parameter_name: "{{ item }}"
  loop:
    - value1
    - value2
  when: condition
'''

RETURN = '''
result:
    description: 操作结果
    type: dict
    returned: always
    sample: {
        "key": "value",
        "nested": {
            "key": "value"
        }
    }
changed:
    description: 是否发生变更
    type: bool
    returned: always
    sample: true
msg:
    description: 操作消息
    type: str
    returned: always
    sample: "Operation completed successfully"
'''
```

## 🔍 故障排除

### 1. 常见问题

#### 模块导入问题
```python
# 问题：模块无法导入
# 解决：检查模块路径和 PYTHONPATH

import sys
import os

# 添加模块路径
module_path = os.path.join(os.path.dirname(__file__), 'library')
if module_path not in sys.path:
    sys.path.insert(0, module_path)
```

#### 参数验证问题
```python
# 问题：参数验证失败
# 解决：详细的错误信息

def validate_parameters(module):
    """验证参数"""
    errors = []
    
    if not module.params['required_param']:
        errors.append("required_param is mandatory")
    
    if module.params['numeric_param'] < 0:
        errors.append("numeric_param must be non-negative")
    
    if errors:
        module.fail_json(msg=f"Parameter validation failed: {'; '.join(errors)}")
```

### 2. 调试工具

#### 日志记录
```python
import logging

def setup_logging(module):
    """设置日志记录"""
    log_level = logging.DEBUG if module.params.get('debug') else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    module = AnsibleModule(...)
    logger = setup_logging(module)
    
    logger.info("Module execution started")
    logger.debug(f"Parameters: {module.params}")
    
    # ... 模块逻辑
    
    logger.info("Module execution completed")
```

## 📚 学习资源

### 1. 官方文档
- [Ansible 模块开发指南](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules.html)
- [插件开发指南](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html)
- [集合开发指南](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)

### 2. 社区资源
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [GitHub 示例](https://github.com/ansible/ansible/tree/devel/lib/ansible/modules)
- [社区论坛](https://forum.ansible.com/)

### 3. 开发工具
- [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
- [molecule](https://molecule.readthedocs.io/)
- [ansible-lint](https://ansible-lint.readthedocs.io/)

## 🎓 总结

通过本天的学习，您已经掌握了：

1. **模块开发**：从基础结构到复杂功能实现
2. **插件系统**：过滤器、查找、连接插件开发
3. **测试调试**：单元测试、集成测试、调试技巧
4. **打包发布**：集合构建、发布流程
5. **最佳实践**：代码质量、安全考虑、文档规范

这些技能将帮助您：
- 扩展 Ansible 功能以满足特定需求
- 开发可重用的模块和插件
- 构建企业级的 Ansible 解决方案
- 为 Ansible 社区贡献代码

下一步建议：
1. 实践开发自己的模块
2. 贡献开源项目
3. 学习高级特性应用
4. 参与社区讨论和交流

**继续学习 Day 9: 高级特性应用！** 🚀 