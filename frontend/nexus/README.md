# Nexus配置专题

本专题介绍如何配置NPM使用内部Nexus仓库，实现根据不同的包访问不同的Nexus仓库，同时确保密码安全不泄露。

## 目录

1. [Nexus基础概念与架构](./1-Nexus基础概念与架构.md)
2. [多Nexus仓库配置指南](./2-多Nexus仓库配置指南.md)
3. [安全密码管理方案](./3-安全密码管理方案.md)
4. [代码示例](./code/)

## 内容概述

### 1. Nexus基础概念与架构

- Nexus的核心价值和优势
- Nexus架构概述
- 安装与配置指南
- 与NPM的集成方式
- 安全模型和权限控制
- 性能优化和监控
- 最佳实践

### 2. 多Nexus仓库配置指南

- NPM配置基础
- 多仓库配置方案
  - 作用域配置
  - .npmrc文件切换
  - 条件配置
- 安全密码管理方案
- 高级配置技巧
- 实战案例
- 常见问题与解决方案
- 最佳实践

### 3. 安全密码管理方案

- 安全风险分析
- 密码管理方案
  - 环境变量管理
  - .npm-auth文件
  - npm-login命令
  - 密钥管理系统
  - Docker Secrets
- CI/CD集成
- 安全最佳实践
- 常见问题解决方案

### 4. 代码示例

- 基本的多仓库配置示例
- 环境变量配置示例
- 生成认证Token的脚本
- 环境变量设置脚本
- .npmrc文件切换脚本
- Vault集成脚本
- AWS Secrets Manager集成
- Docker Secrets集成
- CI/CD配置示例

## 快速开始

1. 了解Nexus基础概念和架构
2. 学习多Nexus仓库配置方法
3. 选择适合的安全密码管理方案
4. 参考代码示例进行实际配置

## 适用场景

- 企业内部需要管理多个NPM仓库
- 不同项目需要访问不同的Nexus仓库
- 需要确保仓库密码安全不泄露
- 需要在CI/CD环境中安全使用Nexus仓库

## 前置知识

- 基础的NPM使用经验
- 了解企业级仓库管理的基本概念
- 基本的Linux/Windows命令行操作

## 相关资源

- [Nexus Repository Manager官方文档](https://help.sonatype.com/repomanager3)
- [NPM官方文档](https://docs.npmjs.com/)
- [企业级NPM仓库管理最佳实践](https://www.npmjs.com/package/enterprise-registry)

## 贡献指南

欢迎提交问题和改进建议，帮助完善本专题内容。

## 许可证

本专题内容采用MIT许可证。