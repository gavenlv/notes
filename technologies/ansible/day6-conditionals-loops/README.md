# Day 6: 条件判断与循环高级应用

## 📚 学习概述

Day 6 专注于 Ansible 中最重要的控制流程技能 - 条件判断和循环控制。通过深入学习这些技术，您将能够构建复杂、灵活且高效的自动化系统。

## 🎯 学习目标

- **掌握复杂条件逻辑**：学会构建和应用各种条件判断
- **精通循环控制**：掌握多种循环类型的高级用法
- **组合应用技巧**：学会条件与循环的组合使用
- **错误处理机制**：理解异常管理和恢复策略
- **动态任务执行**：实现智能的任务调度策略
- **企业级应用**：应用于实际的企业场景

## 📁 目录结构

```
day6-conditionals-loops/
├── README.md                          # 本文档
├── conditionals-loops.md              # 主要学习文档
├── playbooks/                         # 演示 Playbooks
│   ├── 01-advanced-conditionals.yml   # 高级条件判断演示
│   ├── 02-advanced-loops.yml          # 高级循环技术演示
│   └── 03-error-handling.yml          # 错误处理和流程控制
├── scripts/                           # 演示脚本
│   ├── run-conditionals-demo.ps1      # 条件判断演示脚本
│   ├── run-loops-demo.ps1             # 循环演示脚本
│   ├── run-error-handling-demo.ps1    # 错误处理演示脚本
│   └── run-all-demos.ps1              # 综合演示脚本
└── examples/                          # 示例文件(待创建)
    └── README.md                      # 示例说明
```

## 🚀 快速开始

### 1. 运行单个演示

```powershell
# 条件判断演示
.\scripts\run-conditionals-demo.ps1

# 循环技术演示
.\scripts\run-loops-demo.ps1

# 错误处理演示
.\scripts\run-error-handling-demo.ps1
```

### 2. 运行综合演示

```powershell
# 运行所有演示
.\scripts\run-all-demos.ps1

# 只运行特定演示
.\scripts\run-all-demos.ps1 -Demo conditionals
.\scripts\run-all-demos.ps1 -Demo loops
.\scripts\run-all-demos.ps1 -Demo errors

# 显示进度和暂停选项
.\scripts\run-all-demos.ps1 -ShowProgress -PauseAfterEach
```

### 3. 手动执行 Playbooks

```bash
# 条件判断演示 - 不同环境
ansible-playbook playbooks/01-advanced-conditionals.yml -e "env=development"
ansible-playbook playbooks/01-advanced-conditionals.yml -e "env=staging"
ansible-playbook playbooks/01-advanced-conditionals.yml -e "env=production"

# 循环技术演示
ansible-playbook playbooks/02-advanced-loops.yml -v

# 错误处理演示 - 不同场景
ansible-playbook playbooks/03-error-handling.yml -e "env=development rollback=true"
ansible-playbook playbooks/03-error-handling.yml -e "env=production force=true"
```

## 📋 学习内容详解

### 第一部分：高级条件判断

**涵盖技术：**
- 基础条件语法 (`when`)
- 多条件组合 (`and`/`or`)
- 变量类型检查 (`is string`, `is number`, `is boolean`)
- 正则表达式匹配 (`is match`, `is search`)
- 变量存在性检查 (`is defined`, `is undefined`)
- 动态条件设置和重用

**实际应用：**
- 环境特定的配置管理
- 服务器角色自动检测
- 用户权限验证
- 服务兼容性检查

### 第二部分：高级循环技术

**涵盖技术：**
- 基础循环类型 (`loop`, `dict2items`)
- 嵌套循环 (`subelements`, `product`)
- 条件循环 (`when` + `loop`)
- 循环变量控制 (`loop_control`)
- 高级过滤 (`selectattr`, `rejectattr`, `groupby`)
- 动态循环构建
- 性能优化技术

**实际应用：**
- 批量用户管理
- 服务器-服务映射
- 多环境配置部署
- 监控指标收集

### 第三部分：错误处理和流程控制

**涵盖技术：**
- 错误处理策略 (`failed_when`, `ignore_errors`)
- 重试机制 (`until`, `retries`, `delay`)
- 结构化错误处理 (`block`/`rescue`/`always`)
- 条件性流程控制
- 循环中的错误处理
- 错误恢复和清理

**实际应用：**
- 多环境部署策略
- 自动回滚机制
- 服务健康检查
- 故障恢复流程

## 🛠️ 技术要点

### 条件判断最佳实践

```yaml
# ✅ 推荐：简洁明了的条件
- name: 安装生产环境服务
  service:
    name: nginx
    state: started
  when: environment == "production"

# ✅ 推荐：使用变量封装复杂逻辑
- name: 设置高性能模式
  set_fact:
    high_performance_mode: "{{ ansible_processor_vcpus >= 4 and ansible_memtotal_mb >= 8192 }}"

- name: 应用高性能配置
  template:
    src: nginx-performance.conf.j2
    dest: /etc/nginx/nginx.conf
  when: high_performance_mode
```

### 循环优化策略

```yaml
# ✅ 推荐：使用过滤器减少循环次数
- name: 仅处理 Web 服务器
  debug:
    msg: "配置 Web 服务器: {{ item.hostname }}"
  loop: "{{ servers | selectattr('role', 'equalto', 'web') | list }}"

# ⚠️ 避免：深度嵌套循环
# 如果需要超过3层嵌套，考虑重构为多个任务
```

### 错误处理策略

```yaml
# ✅ 推荐：结构化错误处理
- block:
    - name: 主要操作
      # 主要任务
  rescue:
    - name: 错误处理
      # 错误恢复
  always:
    - name: 清理工作
      # 必须执行的清理
```

## 📊 性能优化建议

### 1. 条件优化
- 将最可能为 `false` 的条件放在前面
- 缓存复杂计算的结果
- 使用变量避免重复计算

### 2. 循环优化
- 使用 `selectattr`/`rejectattr` 预过滤数据
- 考虑使用 `async`/`poll` 并行执行
- 利用模块的批量功能替代循环

### 3. 错误处理优化
- 为不同环境设置不同的错误阈值
- 实现智能重试策略
- 提供详细的错误日志

## 🔍 故障排除

### 常见问题

1. **条件判断不生效**
   ```bash
   # 检查变量值
   ansible-playbook playbook.yml -e "debug=true" -vvv
   ```

2. **循环性能问题**
   ```yaml
   # 添加循环控制
   loop_control:
     label: "{{ item.name }}"  # 简化输出
     pause: 1                 # 添加延迟
   ```

3. **错误处理不当**
   ```yaml
   # 使用 register 收集错误信息
   register: task_result
   failed_when: task_result.rc != 0 and item.required
   ```

## 🎓 学习验证

完成学习后，您应该能够：

- [ ] 编写复杂的条件判断逻辑
- [ ] 使用各种循环类型处理批量操作
- [ ] 实现robust的错误处理机制
- [ ] 优化循环和条件的性能
- [ ] 设计企业级的自动化流程

## 🚀 下一步学习

**Day 7: 角色与 Galaxy 高级应用**
- 学习角色的设计模式
- 掌握 Ansible Galaxy 的使用
- 构建企业级角色库
- 实现角色的版本管理

## 📞 获取帮助

如果在学习过程中遇到问题：

1. 查看 `conditionals-loops.md` 详细文档
2. 运行带 `-vvv` 参数的详细调试
3. 检查 Ansible 官方文档的条件和循环部分
4. 参考企业级最佳实践案例

---

**Happy Learning with Ansible! 🎉** 