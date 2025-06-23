# Ansible 学习路径 - 从入门到精通

这是一个完整的 Ansible 学习路径，包含 15 天的学习内容，从基础安装到高级项目实施。每天的内容都包含理论知识、实践示例和可运行的代码。

## 📚 学习路径

### 基础入门 (Day 1-4)
- **Day 1**: [安装与环境配置](./day1-installation/installation.md)
- **Day 2**: [Ansible 基础介绍](./day2-introduction/introduction.md)  
- **Day 3**: [Inventory 管理](./day3-inventory-management/inventory-management.md)
- **Day 4**: [Playbooks 基础](./day4-playbooks-basics/playbooks-basics.md)

### 核心功能 (Day 5-8)
- **Day 5**: [变量与模板](./day5-variables-templates/variables-templates.md)
- **Day 6**: [条件判断与循环](./day6-conditionals-loops/conditionals-loops.md)
- **Day 7**: [Roles 和 Galaxy](./day7-roles-galaxy/roles-galaxy.md)
- **Day 8**: [模块与插件开发](./day8-modules-plugins/modules-plugins.md)

### 高级特性 (Day 9-12)
- **Day 9**: [高级功能](./day9-advanced-features/advanced-features.md)
- **Day 10**: [错误处理](./day10-error-handling/error-handling.md)
- **Day 11**: [性能优化](./day11-performance-optimization/performance-optimization.md)
- **Day 12**: [安全与 Vault](./day12-security-vault/security-vault.md)

### 企业应用 (Day 13-15)
- **Day 13**: [CI/CD 集成](./day13-cicd-integration/cicd-integration.md)
- **Day 14**: [监控与日志](./day14-monitoring-logging/monitoring-logging.md)
- **Day 15**: [项目实战](./day15-project-implementation/project-implementation.md)

## 🛠️ 环境要求

- **操作系统**: Linux/macOS/Windows (WSL)
- **Python**: 3.6+
- **Ansible**: 2.9+ (推荐最新版本)
- **虚拟机**: VirtualBox/VMware (用于测试)

## 🚀 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd ansible-learning
```

2. **开始第一天学习**
```bash
cd day1-installation
# 按照 installation.md 的指引进行安装
```

3. **验证安装**
```bash
ansible --version
ansible localhost -m ping
```

## 📁 目录结构

每个学习日期的目录包含：
- **文档**: 详细的学习指南和理论知识
- **configs/**: 配置文件示例
- **examples/**: 实践示例
- **scripts/**: 自动化脚本
- **playbooks/**: Playbook 示例 (适用时)

## 🎯 学习目标

完成本学习路径后，你将能够：

- ✅ 熟练安装和配置 Ansible 环境
- ✅ 编写和管理 Ansible Playbooks
- ✅ 使用 Ansible 管理大规模基础设施
- ✅ 开发自定义模块和插件
- ✅ 在企业环境中应用 Ansible 最佳实践
- ✅ 集成 Ansible 到 CI/CD 流水线
- ✅ 实施安全和监控策略

## 💡 学习建议

1. **循序渐进**: 按照天数顺序学习，不要跳跃
2. **动手实践**: 每个示例都要亲自运行
3. **环境搭建**: 准备测试环境，避免在生产环境练习
4. **文档记录**: 记录学习笔记和遇到的问题
5. **社区参与**: 积极参与 Ansible 社区讨论

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个学习路径！

## 📖 参考资源

- [Ansible 官方文档](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Ansible GitHub](https://github.com/ansible/ansible)
- [Red Hat Ansible](https://www.redhat.com/en/technologies/management/ansible)

---
**开始你的 Ansible 学习之旅吧！** 🚀 