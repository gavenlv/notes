# Day 8: Ansible 模块与插件开发

## 📚 学习概述

第8天的学习重点是 **Ansible 模块与插件开发**，这是一个高级主题，将帮助您掌握扩展 Ansible 功能的能力。通过本天的学习，您将从零开始创建自定义模块和插件，掌握企业级开发规范。

## 🎯 学习目标

- ✅ **自定义模块开发**：从零开始创建 Ansible 模块
- ✅ **插件系统理解**：深入理解 Ansible 插件架构
- ✅ **开发环境搭建**：配置模块和插件开发环境
- ✅ **测试与调试**：模块测试和调试技巧
- ✅ **最佳实践**：企业级模块开发规范

## 📁 项目结构

```
day8-modules-plugins/
├── modules/                    # 自定义模块
│   ├── advanced_file.py       # 高级文件管理模块
│   └── system_info.py         # 系统信息收集模块
├── plugins/                   # 自定义插件
│   ├── filter_plugins/
│   │   └── custom_filters.py  # 自定义过滤器插件
│   └── lookup_plugins/
│       └── database_lookup.py # 数据库查找插件
├── examples/                  # 示例和测试
│   ├── test-modules.yml       # 模块测试 Playbook
│   └── test-plugins.yml       # 插件测试 Playbook
├── scripts/                   # 测试脚本
│   └── test-development.ps1   # 开发测试脚本
├── modules-plugins.md         # 详细学习文档
└── README.md                  # 本文件
```

## 🛠️ 开发的模块和插件

### 自定义模块

#### 1. advanced_file 模块
**功能**：高级文件管理模块，提供比内置 `file` 模块更强大的功能

**特性**：
- 支持内容和模板渲染
- 自动备份功能
- 文件验证机制
- 完整的权限管理
- 支持 check mode

**使用示例**：
```yaml
- name: 创建配置文件
  advanced_file:
    path: /etc/myapp/config.conf
    content: |
      server_name = {{ ansible_hostname }}
      port = 8080
    mode: '0644'
    backup: true
    validate: 'myapp --check-config %s'
```

#### 2. system_info 模块
**功能**：全面的系统信息收集模块

**特性**：
- 硬件信息收集（CPU、内存、存储）
- 网络信息统计
- 进程信息分析
- 服务状态查询
- 多种输出格式支持

**使用示例**：
```yaml
- name: 收集系统信息
  system_info:
    info_type: all
    top_processes: 10
    include_services: true
  register: system_data
```

### 自定义插件

#### 1. 过滤器插件 (custom_filters.py)
**功能**：扩展 Jinja2 模板过滤器

**包含的过滤器**：
- `to_title_case`: 转换为标题格式
- `extract_domain`: 从邮箱提取域名
- `format_bytes`: 格式化字节大小
- `mask_sensitive`: 遮盖敏感信息
- `flatten_dict`/`unflatten_dict`: 字典扁平化操作
- `group_by_key`/`sort_by_key`: 列表操作
- `validate_email`/`validate_ip`: 数据验证
- `generate_password`: 密码生成
- `calculate_age`/`add_days`: 日期操作

**使用示例**：
```yaml
- debug:
    msg: |
      格式化大小: {{ 1048576 | format_bytes }}
      域名: {{ "user@example.com" | extract_domain }}
      遮盖密码: {{ "password123" | mask_sensitive }}
```

#### 2. 查找插件 (database_lookup.py)
**功能**：数据库查询插件，支持多种数据库类型

**支持的数据库**：
- PostgreSQL
- MySQL
- SQLite
- MongoDB

**使用示例**：
```yaml
- name: 查询数据库
  debug:
    msg: "{{ lookup('database', 'SELECT * FROM users', 
                    type='postgresql', host='localhost', 
                    database='myapp', username='reader') }}"
```

## 🧪 测试和验证

### 运行测试

使用提供的测试脚本来验证开发的模块和插件：

```powershell
# 运行所有测试
.\scripts\test-development.ps1

# 仅测试模块
.\scripts\test-development.ps1 -TestType modules

# 仅测试插件
.\scripts\test-development.ps1 -TestType plugins

# 详细输出
.\scripts\test-development.ps1 -Verbose

# 调试模式
.\scripts\test-development.ps1 -Debug
```

### 手动测试

```bash
# 设置模块路径
export ANSIBLE_LIBRARY="$(pwd)/modules"
export ANSIBLE_FILTER_PLUGINS="$(pwd)/plugins/filter_plugins"
export ANSIBLE_LOOKUP_PLUGINS="$(pwd)/plugins/lookup_plugins"

# 运行模块测试
ansible-playbook examples/test-modules.yml -v

# 运行插件测试
ansible-playbook examples/test-plugins.yml -v
```

## 📋 开发规范

### 模块开发规范

1. **文档完整性**
   - 必须包含 `DOCUMENTATION`、`EXAMPLES`、`RETURN` 字符串
   - 详细的参数说明和使用示例
   - 完整的返回值文档

2. **代码质量**
   - 遵循 PEP 8 代码风格
   - 使用类型提示
   - 完善的错误处理
   - 支持 check mode

3. **安全考虑**
   - 输入验证
   - 权限检查
   - 敏感信息保护

### 插件开发规范

1. **过滤器插件**
   - 明确的功能定义
   - 完善的错误处理
   - 类型检查和验证

2. **查找插件**
   - 支持多种数据源
   - 连接池管理
   - 错误恢复机制

## 🔧 开发环境设置

### 前置条件

```bash
# Python 依赖
pip install ansible psutil jinja2

# 可选依赖（用于特定功能）
pip install jmespath          # JSON 查询
pip install psycopg2-binary   # PostgreSQL 支持
pip install mysql-connector-python  # MySQL 支持
pip install pymongo           # MongoDB 支持
```

### 开发工具

```bash
# 代码质量检查
pip install flake8 black

# 测试工具
pip install pytest pytest-cov

# 文档生成
pip install sphinx
```

## 📊 性能考虑

### 模块性能优化

1. **缓存机制**
   - 缓存昂贵的操作结果
   - 避免重复计算

2. **异步操作**
   - 使用异步 I/O
   - 并行处理多个任务

3. **资源管理**
   - 及时释放资源
   - 内存使用优化

### 插件性能优化

1. **过滤器优化**
   - 避免在循环中使用复杂过滤器
   - 预编译正则表达式

2. **查找插件优化**
   - 连接池复用
   - 查询结果缓存

## 🚀 高级特性

### 动作插件开发

```python
# action_plugins/advanced_action.py
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        # 在控制节点执行的逻辑
        result = super().run(tmp, task_vars)
        # 自定义处理逻辑
        return result
```

### 连接插件开发

```python
# connection_plugins/custom_connection.py
from ansible.plugins.connection import ConnectionBase

class Connection(ConnectionBase):
    transport = 'custom'
    
    def _connect(self):
        # 自定义连接逻辑
        pass
    
    def exec_command(self, cmd, in_data=None, sudoable=True):
        # 自定义命令执行逻辑
        pass
```

## 🔍 故障排除

### 常见问题

1. **模块无法找到**
   ```bash
   # 检查模块路径
   echo $ANSIBLE_LIBRARY
   
   # 设置模块路径
   export ANSIBLE_LIBRARY="/path/to/modules"
   ```

2. **插件无法加载**
   ```bash
   # 检查插件路径
   echo $ANSIBLE_FILTER_PLUGINS
   echo $ANSIBLE_LOOKUP_PLUGINS
   
   # 设置插件路径
   export ANSIBLE_FILTER_PLUGINS="/path/to/filter_plugins"
   export ANSIBLE_LOOKUP_PLUGINS="/path/to/lookup_plugins"
   ```

3. **依赖包缺失**
   ```bash
   # 检查 Python 包
   python -c "import psutil; print(psutil.__version__)"
   
   # 安装缺失的包
   pip install psutil jinja2
   ```

### 调试技巧

1. **模块调试**
   ```bash
   # 使用 -vvv 参数获取详细输出
   ansible-playbook playbook.yml -vvv
   
   # 使用 debug 模块输出变量
   - debug: var=result
   ```

2. **插件调试**
   ```python
   # 在插件中添加调试输出
   from ansible.utils.display import Display
   display = Display()
   display.vvv("Debug message")
   ```

## 📚 扩展学习

### 推荐资源

1. **官方文档**
   - [Ansible 模块开发指南](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules.html)
   - [插件开发指南](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html)

2. **社区资源**
   - [Ansible Galaxy](https://galaxy.ansible.com/)
   - [GitHub 示例](https://github.com/ansible/ansible/tree/devel/lib/ansible/modules)

3. **开发工具**
   - [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing.html)
   - [molecule](https://molecule.readthedocs.io/)

### 下一步学习

1. **集合开发**
   - 学习 Ansible 集合的创建和发布
   - 掌握集合的版本管理和依赖处理

2. **企业级开发**
   - 建立 CI/CD 流水线
   - 实施代码质量检查
   - 自动化测试和部署

3. **高级插件类型**
   - 回调插件开发
   - 清单插件开发
   - 策略插件开发

## 🎓 学习成果

通过第8天的学习，您已经掌握了：

- ✅ 自定义模块的完整开发流程
- ✅ 多种类型插件的开发技巧
- ✅ 企业级开发规范和最佳实践
- ✅ 完整的测试和调试方法
- ✅ 性能优化和故障排除技能

这些技能将帮助您：
- 扩展 Ansible 功能以满足特定需求
- 开发可重用的模块和插件
- 构建企业级的 Ansible 解决方案
- 为 Ansible 社区贡献代码

## 🔄 与其他天数的关联

- **Day 1-7**: 前期学习为模块开发提供了基础知识
- **Day 9**: 将学习高级特性，进一步扩展开发能力
- **Day 10-11**: 错误处理和性能优化将应用到模块开发中
- **Day 15**: 项目实战将综合运用自定义模块和插件

---

**继续学习 Day 9: 高级特性应用！** 🚀

> 💡 **提示**: 模块和插件开发是 Ansible 的高级技能，需要持续练习和改进。建议在实际项目中应用这些技能，并积极参与社区贡献。 