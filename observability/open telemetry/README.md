# OpenTelemetry从入门到专家

本教程将带您从零基础开始，逐步掌握OpenTelemetry的可观测性解决方案。OpenTelemetry是一个CNCF托管的开源项目，旨在提供一套标准化的工具、API和SDK，用于生成、收集、分析和导出遥测数据（指标、日志和链路追踪）。

## 教程结构

本教程分为5个章节，从基础概念到实战应用，帮助您全面掌握OpenTelemetry：

1. **[OpenTelemetry基础入门](./1-基础入门.md)** - 介绍OpenTelemetry的基本概念、架构和核心组件
2. **[OpenTelemetry三大信号类型](./2-三大信号类型.md)** - 深入讲解追踪(Traces)、指标(Metrics)和日志(Logs)
3. **[OpenTelemetry Instrumentation与SDK](./3-Instrumentation与SDK.md)** - 详细介绍如何使用SDK进行代码插桩
4. **[OpenTelemetry Collector](./4-Collector.md)** - 讲解Collector的配置、扩展和最佳实践
5. **[OpenTelemetry实战应用](./5-实战应用.md)** - 通过实际案例展示OpenTelemetry在不同场景的应用

## 代码示例

每个章节都配有完整的代码示例，存放在[code](./code)目录中，方便您实践和学习。

## 学习路径建议

1. **零基础学习者**：按章节顺序学习，确保理解每个概念后再继续
2. **有基础的开发者**：可以跳过第1章，直接从第2章开始
3. **运维人员**：重点关注第4章和第5章的内容
4. **架构师**：全面学习，特别关注第3章和第5章

## 前置知识

- 基本的编程知识（至少熟悉一种编程语言）
- 了解微服务架构概念
- 基本的容器和Kubernetes知识（第5章需要）

## 实践环境

- 本地开发环境
- Docker和Docker Compose
- 可选：Kubernetes集群（用于第5章）

## 贡献指南

欢迎提交Issue和Pull Request来改进本教程。

## 许可证

本教程采用MIT许可证。