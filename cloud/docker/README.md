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

- **[第1章：Docker简介与安装](chapter01-introduction/README.md)** ✅
  - Docker是什么
  - 容器vs虚拟机
  - Docker架构
  - 安装配置（Windows/Linux/Mac）
  - 验证安装
  
- **[第2章：Docker基础概念](chapter02-basic-concepts/README.md)** ✅
  - 镜像（Image）
  - 容器（Container）
  - 仓库（Registry）
  - Docker工作流程
  - 第一个容器实验

- **[第3章：Docker镜像管理](chapter03-image-management/README.md)** ✅
  - 镜像搜索和拉取
  - 镜像查看和删除
  - 镜像导入导出
  - 镜像标签管理
  - 镜像分层原理

- **[第4章：Docker容器操作](chapter04-container-operations/README.md)** ✅
  - 容器创建和启动
  - 容器停止和删除
  - 容器进入和退出
  - 容器日志查看
  - 容器资源限制

- **[第5章：Dockerfile详解](chapter05-dockerfile/README.md)** ✅
  - Dockerfile语法
  - 常用指令详解
  - 构建上下文
  - 多阶段构建
  - 构建优化技巧

### 第二部分：进阶应用（第6-8章）

- **[第6章：Docker数据管理](chapter06-data-management/README.md)** ✅
  - 数据卷（Volumes）
  - 绑定挂载（Bind Mounts）
  - tmpfs挂载
  - 数据备份和恢复
  - 数据共享

- **[第7章：Docker网络](chapter07-networking/README.md)** ✅
  - 网络模式详解
  - 自定义网络
  - 容器间通信
  - 端口映射
  - 网络故障排查

- **[第8章：Docker Compose](chapter08-docker-compose/README.md)** ✅
  - Compose简介和安装
  - docker-compose.yml语法
  - 服务编排
  - 多容器应用
  - 环境变量管理

### 进阶学习资源

完成以上8章核心内容后，可参考 [CHAPTERS_OUTLINE.md](CHAPTERS_OUTLINE.md) 了解更多进阶主题：
- Docker私有仓库
- 容器监控与日志
- Docker安全
- Docker Swarm集群
- Docker与CI/CD
- Docker性能优化
- 企业级实战案例

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

### 核心课程（完整教程）
- [ ] 第1章：Docker简介与安装 ✅
- [ ] 第2章：Docker基础概念 ✅
- [ ] 第3章：Docker镜像管理 ✅
- [ ] 第4章：Docker容器操作 ✅
- [ ] 第5章：Dockerfile详解 ✅
- [ ] 第6章：Docker数据管理 ✅
- [ ] 第7章：Docker网络 ✅
- [ ] 第8章：Docker Compose ✅

### 进阶主题（参考大纲）
详见 [CHAPTERS_OUTLINE.md](CHAPTERS_OUTLINE.md)：
- Docker私有仓库
- 容器监控与日志
- Docker安全
- Docker Swarm集群
- Docker与CI/CD
- Docker性能优化
- 企业级实战案例

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
