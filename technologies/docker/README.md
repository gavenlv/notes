# Docker 从零基础到专家 - 完整学习路径

## 📚 课程概述

本课程专为零基础学习者设计，通过15个章节系统学习Docker技术栈，从基础概念到企业级应用，每个知识点都配有详细的实例和可执行代码。

## 🎯 学习目标

- 掌握Docker核心概念和工作原理
- 熟练使用Docker命令和最佳实践
- 构建和优化Docker镜像
- 掌握Docker网络和存储
- 使用Docker Compose编排多容器应用
- 理解容器安全和生产环境部署
- 掌握Docker在CI/CD中的应用

## 📖 课程目录

### 第一部分：基础入门（第1-5章）

- **[第1章：Docker简介与安装](chapter01-introduction/README.md)**
  - Docker是什么
  - 容器vs虚拟机
  - Docker架构
  - 安装配置（Windows/Linux/Mac）
  - 验证安装
  
- **[第2章：Docker基础概念](chapter02-basic-concepts/README.md)**
  - 镜像（Image）
  - 容器（Container）
  - 仓库（Registry）
  - Docker工作流程
  - 第一个容器实验

- **[第3章：Docker镜像管理](chapter03-image-management/README.md)**
  - 镜像搜索和拉取
  - 镜像查看和删除
  - 镜像导入导出
  - 镜像标签管理
  - 镜像分层原理

- **[第4章：Docker容器操作](chapter04-container-operations/README.md)**
  - 容器创建和启动
  - 容器停止和删除
  - 容器进入和退出
  - 容器日志查看
  - 容器资源限制

- **[第5章：Dockerfile详解](chapter05-dockerfile/README.md)**
  - Dockerfile语法
  - 常用指令详解
  - 构建上下文
  - 多阶段构建
  - 构建优化技巧

### 第二部分：进阶应用（第6-10章）

- **[第6章：Docker数据管理](chapter06-data-management/README.md)**
  - 数据卷（Volumes）
  - 绑定挂载（Bind Mounts）
  - tmpfs挂载
  - 数据备份和恢复
  - 数据共享

- **[第7章：Docker网络](chapter07-networking/README.md)**
  - 网络模式详解
  - 自定义网络
  - 容器间通信
  - 端口映射
  - 网络故障排查

- **[第8章：Docker Compose](chapter08-docker-compose/README.md)**
  - Compose简介和安装
  - docker-compose.yml语法
  - 服务编排
  - 多容器应用
  - 环境变量管理

- **[第9章：Docker私有仓库](chapter09-registry/README.md)**
  - Docker Hub使用
  - 搭建私有Registry
  - Harbor安装配置
  - 镜像推送拉取
  - 仓库管理

- **[第10章：容器监控与日志](chapter10-monitoring-logging/README.md)**
  - 容器监控方案
  - Docker stats命令
  - 日志驱动
  - ELK日志收集
  - Prometheus监控

### 第三部分：高级特性（第11-15章）

- **[第11章：Docker安全](chapter11-security/README.md)**
  - 安全最佳实践
  - 用户和权限
  - 镜像扫描
  - 安全加固
  - Secrets管理

- **[第12章：Docker Swarm集群](chapter12-swarm/README.md)**
  - Swarm架构
  - 集群初始化
  - 服务部署
  - 滚动更新
  - 负载均衡

- **[第13章：Docker与CI/CD](chapter13-cicd/README.md)**
  - CI/CD流程
  - Jenkins集成
  - GitLab CI/CD
  - 自动化构建
  - 部署策略

- **[第14章：Docker性能优化](chapter14-performance/README.md)**
  - 镜像优化
  - 容器性能调优
  - 资源限制
  - 存储驱动选择
  - 性能监控

- **[第15章：企业级实战案例](chapter15-enterprise-cases/README.md)**
  - 微服务架构
  - 完整项目部署
  - 生产环境最佳实践
  - 故障排查
  - 运维自动化

## 🔧 代码目录说明

每个章节都包含：
- `README.md` - 详细的理论讲解
- `code/` - 可执行的示例代码
- `exercises/` - 实践练习题
- `examples/` - 完整示例项目

## 🚀 快速开始

### 前置要求
- 操作系统：Windows 10/11, Linux, macOS
- 硬件：至少4GB RAM，20GB可用磁盘空间
- 基础知识：命令行基础操作

### 开始学习

1. **克隆或下载本仓库**
2. **从第1章开始按顺序学习**
3. **每章都运行代码示例**
4. **完成章节练习**
5. **记录学习笔记**

### 代码运行方式

```bash
# Windows PowerShell
cd technologies\docker\chapter01-introduction\code
.\run-examples.ps1

# Linux/Mac
cd technologies/docker/chapter01-introduction/code
./run-examples.sh
```

## 📝 学习建议

1. **循序渐进**：不要跳章，每个章节都有前置知识依赖
2. **动手实践**：每个命令都要亲自运行，每个代码都要测试
3. **理解原理**：不仅知道怎么做，更要知道为什么
4. **记录笔记**：记录遇到的问题和解决方案
5. **项目实战**：学完基础后立即应用到实际项目

## 🎓 学习进度跟踪

- [ ] 第1章：Docker简介与安装
- [ ] 第2章：Docker基础概念
- [ ] 第3章：Docker镜像管理
- [ ] 第4章：Docker容器操作
- [ ] 第5章：Dockerfile详解
- [ ] 第6章：Docker数据管理
- [ ] 第7章：Docker网络
- [ ] 第8章：Docker Compose
- [ ] 第9章：Docker私有仓库
- [ ] 第10章：容器监控与日志
- [ ] 第11章：Docker安全
- [ ] 第12章：Docker Swarm集群
- [ ] 第13章：Docker与CI/CD
- [ ] 第14章：Docker性能优化
- [ ] 第15章：企业级实战案例

## 📚 参考资源

- [Docker官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker GitHub](https://github.com/docker)

## 💡 常见问题

详见各章节的FAQ部分

## 🤝 贡献

欢迎提交问题和改进建议

---

**开始你的Docker学习之旅！** 🐳
