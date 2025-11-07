# Loki 从入门到专家

本教程将带领您从零基础开始，逐步掌握Loki的各项功能，最终成为Loki专家。教程包含以下章节：

## 📚 教程目录

- [第1章：Loki基础入门](./chapter1/1.1-introduction.md) - 了解Loki的基本概念、安装与初始配置
- [第2章：Loki架构与组件](./chapter2/2.1-architecture.md) - 掌握Loki的架构和核心组件
- [第3章：Loki日志收集](./chapter3/3.1-log-collection.md) - 学习如何收集和传输日志
- [第4章：Loki日志查询](./chapter4/4.1-log-querying.md) - 掌握Loki查询语言和技巧
- [第5章：Loki高级功能](./chapter5/5.1-advanced-features.md) - 探索Loki的高级功能和优化
- [第6章：Loki生产环境部署](./chapter6/6.1-production-deployment.md) - 企业级部署和最佳实践

## 📋 学习路径

本教程专为零基础学习者设计，每章包含：
- 📖 概念讲解 - 清晰的理论说明
- 💡 实例演示 - 详细的操作步骤
- 🧪 实验验证 - 可运行的代码和配置
- 📝 练习题目 - 巩固所学知识
- 🎯 最佳实践 - 专业技巧与建议

## 📁 文件结构

```
observability/loki/
├── README.md               # 本文件
├── chapter1/               # 第1章：Loki基础入门
│   ├── 1.1-introduction.md
│   ├── 1.2-installation.md
│   └── 1.3-first-steps.md
├── chapter2/               # 第2章：Loki架构与组件
│   ├── 2.1-architecture.md
│   ├── 2.2-components.md
│   └── 2.3-data-model.md
├── chapter3/               # 第3章：Loki日志收集
│   ├── 3.1-log-collection.md
│   ├── 3.2-promtail.md
│   └── 3.3-fluent-bit.md
├── chapter4/               # 第4章：Loki日志查询
│   ├── 4.1-log-querying.md
│   ├── 4.2-logql.md
│   └── 4.3-advanced-queries.md
├── chapter5/               # 第5章：Loki高级功能
│   ├── 5.1-advanced-features.md
│   ├── 5.2-alerting.md
│   └── 5.3-performance.md
├── chapter6/               # 第6章：Loki生产环境部署
│   ├── 6.1-production-deployment.md
│   ├── 6.2-scalability.md
│   └── 6.3-best-practices.md
└── code/                   # 所有示例代码
    ├── chapter1/
    ├── chapter2/
    ├── chapter3/
    ├── chapter4/
    ├── chapter5/
    └── chapter6/
```

## 🚀 快速开始

1. 首先阅读[第1章](./chapter1/1.1-introduction.md)了解Loki基本概念
2. 按照[第1章](./chapter1/1.2-installation.md)的指引安装Loki
3. 完成第一次日志收集，完成[第1章](./chapter1/1.3-first-steps.md)的实验
4. 逐步学习后续章节，每个章节都包含理论与实践

## 📋 前置知识

本教程为零基础学习者设计，不需要任何Loki经验。但如果您具备以下知识，学习过程会更加轻松：
- 基本的计算机操作能力
- 了解日志的基本概念
- 有容器化基础（Docker）
- 了解JSON和YAML格式（非必需，但有助于理解配置）

## 💻 环境准备

学习本教程需要准备：
- 一台现代计算机（Windows 10+, macOS 10.14+, 或Linux）
- 至少4GB内存，推荐8GB+
- 至少10GB可用磁盘空间
- 管理员权限（用于安装软件）
- 稳定的网络连接
- Docker（推荐）或Go 1.19+环境

## 📞 获取帮助

如果在学习过程中遇到问题，可以：
- 查看每个章节的"常见问题"部分
- 参考[Loki官方文档](https://grafana.com/docs/loki/latest/)
- 在[Loki社区](https://community.grafana.com/c/loki/loki)提问

## 🔗 相关技术栈

Loki通常与以下技术一起使用：

- **Grafana**: 用于日志可视化和查询
- **Promtail**: 日志收集代理
- **Fluent Bit**: 另一个日志收集代理
- **Prometheus**: 指标收集系统

本教程将涵盖这些工具与Loki的集成方法。

## 🆚 Loki与传统日志系统

Loki与传统日志系统（如ELK Stack）的主要区别：

| 特性 | Loki | ELK Stack |
|------|------|-----------|
| 设计哲学 | "像Prometheus，但用于日志" | 全文搜索 |
| 存储方式 | 只索引标签，不索引内容 | 索引内容和元数据 |
| 资源消耗 | 较低 | 较高 |
| 查询语言 | LogQL（类似PromQL） | Lucene查询语法 |
| 集成度 | 与Grafana原生集成 | 需要额外配置 |
| 水平扩展 | 设计为水平扩展 | 可水平扩展但配置复杂 |

现在，让我们开始Loki的学习之旅！