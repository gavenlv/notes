# Helm 从入门到专家教程

## 📚 教程概述

本教程将带你从零开始，系统性地学习Helm，最终达到专家水平。教程采用循序渐进的方式，每个概念都通过实例和实验进行验证。

### 🎯 学习目标

- ✅ **零基础入门** - 从Helm基本概念开始
- ✅ **深入理解** - 每个知识点都深入讲解
- ✅ **实践验证** - 通过实例代码验证所有概念
- ✅ **专家进阶** - 掌握企业级最佳实践

### 📖 教程结构

| 章节 | 内容 | 难度 |
|------|------|------|
| [01-基础概念](./01-基础概念.md) | Helm核心概念、安装配置 | 🌟 |
| [02-Chart开发详解](./02-Chart开发详解.md) | Chart结构、模板语法 | 🌟🌟 |
| [03-高级特性与模板引擎](./03-高级特性与模板引擎.md) | 模板函数、流程控制 | 🌟🌟🌟 |
| [04-Helm部署策略](./04-Helm部署策略.md) | 部署管理、生命周期 | 🌟🌟🌟🌟 |
| [05-企业级最佳实践](./05-企业级最佳实践.md) | 安全、监控、CI/CD | 🌟🌟🌟🌟🌟 |

### 🚀 快速开始

#### 环境准备
1. 安装Helm：`curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`
2. 安装Kubernetes集群（如Minikube）

#### 实验环境
```bash
# 启动Minikube
minikube start

# 验证Helm安装
helm version

# 添加官方仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
```

### 📁 代码结构

```
cloud/helm/
├── README.md                    # 本文件
├── SUMMARY.md                   # 教程总结
├── 01-基础概念.md               # 第1章：基础概念
├── 02-Chart开发详解.md          # 第2章：Chart开发
├── 03-高级特性与模板引擎.md      # 第3章：高级特性
├── 04-Helm部署策略.md           # 第4章：部署策略
├── 05-企业级最佳实践.md          # 第5章：最佳实践
└── code/                        # 代码示例目录
    ├── README.md                # 代码示例说明
    ├── basic-chart/             # 基础Chart示例
    ├── advanced-chart/          # 高级Chart示例
    ├── multi-service/           # 多服务Chart
    ├── helmfile/                # Helmfile配置
    └── enterprise/              # 企业级示例
```

### 🧪 学习方法

1. **理论学习** - 阅读对应章节的文档
2. **代码实践** - 进入code目录运行示例
3. **实验验证** - 修改代码观察效果
4. **项目实战** - 应用所学知识到实际项目

### 🔧 实验环境要求

- Kubernetes集群（Minikube、Kind或云平台）
- Helm 3.8+ 版本
- kubectl命令行工具
- 文本编辑器（VS Code推荐）

### 📚 扩展资源

- [官方文档](https://helm.sh/docs/)
- [Chart模板指南](https://helm.sh/docs/chart_template_guide/)
- [最佳实践](https://helm.sh/docs/chart_best_practices/)

---

**开始你的Helm学习之旅吧！从第1章开始，循序渐进，理论与实践结合，成为Helm专家！**