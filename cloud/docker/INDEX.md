# Docker学习课程 - 完整索引

## 📖 快速导航

### 📌 开始之前
- [主目录 README](README.md) - 课程总览
- [快速开始指南](QUICK_START.md) - 5分钟上手
- [完成总结](COMPLETION_SUMMARY.md) - 课程完成情况
- [章节大纲](CHAPTERS_OUTLINE.md) - 第6-15章概要

---

## 📚 课程章节

### 第一部分：基础入门（1-5章）⭐⭐⭐

#### [第1章：Docker简介与安装](chapter01-introduction/README.md)
**学习时间**: 1天 | **难度**: ⭐  
**核心内容**:
- Docker是什么？为什么需要它？
- 容器 vs 虚拟机详细对比
- Windows/Linux/Mac安装教程
- 运行第一个容器

**资源**:
- 📝 [详细教程](chapter01-introduction/README.md) (694行)
- 💻 [演示脚本](chapter01-introduction/code/) (PS1 + SH)
- ✏️ [10个练习题](chapter01-introduction/exercises/exercises.md)
- 🎯 [Web应用示例](chapter01-introduction/examples/simple-web-app/)

---

#### [第2章：Docker基础概念](chapter02-basic-concepts/README.md)
**学习时间**: 1-2天 | **难度**: ⭐⭐  
**核心内容**:
- 镜像的分层结构深入剖析
- 容器生命周期完整解析
- 文件系统和CoW机制
- exec vs attach对比

**资源**:
- 📝 [详细教程](chapter02-basic-concepts/README.md) (866行)
- 📂 [代码目录](chapter02-basic-concepts/code/)
- 📂 [练习目录](chapter02-basic-concepts/exercises/)
- 📂 [示例目录](chapter02-basic-concepts/examples/)

---

#### [第3章：Docker镜像管理](chapter03-image-management/README.md)
**学习时间**: 1天 | **难度**: ⭐⭐  
**核心内容**:
- 镜像搜索、拉取、推送操作
- 镜像标签管理最佳实践
- 镜像导入导出实战
- 镜像清理和优化策略

**资源**:
- 📝 [详细教程](chapter03-image-management/README.md) (519行)
- 📂 [代码目录](chapter03-image-management/code/)
- 📂 [练习目录](chapter03-image-management/exercises/)

---

#### [第4章：Docker容器高级操作](chapter04-container-operations/README.md)
**学习时间**: 1-2天 | **难度**: ⭐⭐⭐  
**核心内容**:
- 容器高级运行选项
- 资源限制（CPU/内存/磁盘）
- 重启策略和健康检查
- 环境变量管理

**资源**:
- 📝 [详细教程](chapter04-container-operations/README.md) (603行)
- 📂 [代码目录](chapter04-container-operations/code/)
- 📂 [练习目录](chapter04-container-operations/exercises/)

---

#### [第5章：Dockerfile详解](chapter05-dockerfile/README.md)
**学习时间**: 1天 | **难度**: ⭐⭐⭐  
**核心内容**:
- Dockerfile所有指令详解
- 多阶段构建技术
- 镜像优化技巧
- 实战构建示例

**资源**:
- 📝 [详细教程](chapter05-dockerfile/README.md) (767行)
- 📂 [代码目录](chapter05-dockerfile/code/)
- 📂 [示例目录](chapter05-dockerfile/examples/)

---

### 第二部分：进阶应用（6-10章）⭐⭐⭐⭐

#### [第6章：Docker数据管理](chapter06-data-management/README.md)
**学习时间**: 1天 | **难度**: ⭐⭐⭐  
**核心内容**:
- Volumes（数据卷）
- Bind Mounts（绑定挂载）
- tmpfs（内存挂载）
- 数据备份和恢复

**资源**:
- 📝 [详细教程](chapter06-data-management/README.md) (376行)
- 📂 [代码目录](chapter06-data-management/code/)
- 📂 [练习目录](chapter06-data-management/exercises/)

---

#### [第7章：Docker网络](chapter07-networking/README.md)
**学习时间**: 1-2天 | **难度**: ⭐⭐⭐  
**核心内容**:
- 5种网络模式详解
- 自定义网络创建
- 容器间通信
- 网络故障排查

**资源**:
- 📝 [详细教程](chapter07-networking/README.md) (364行)
- 📂 [代码目录](chapter07-networking/code/)
- 📂 [练习目录](chapter07-networking/exercises/)

---

#### [第8章：Docker Compose](chapter08-docker-compose/README.md)
**学习时间**: 2天 | **难度**: ⭐⭐⭐⭐  
**核心内容**:
- docker-compose.yml完整语法
- 多容器应用编排
- 环境变量管理
- 完整项目示例

**资源**:
- 📝 [详细教程](chapter08-docker-compose/README.md) (818行)
- 📂 [代码目录](chapter08-docker-compose/code/)
- 📂 [示例目录](chapter08-docker-compose/examples/)

---

#### [第9章：Docker私有仓库](chapter09-registry/README.md)
**学习时间**: 1-2天 | **难度**: ⭐⭐⭐  
**核心内容**:
- Docker Hub使用
- 搭建私有Registry
- Harbor企业级仓库
- 镜像推送拉取

**资源**:
- 📂 [章节目录](chapter09-registry/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第9章docker私有仓库)

---

#### [第10章：容器监控与日志](chapter10-monitoring-logging/README.md)
**学习时间**: 2天 | **难度**: ⭐⭐⭐⭐  
**核心内容**:
- 容器监控方案
- Prometheus + Grafana
- ELK日志收集
- 告警机制

**资源**:
- 📂 [章节目录](chapter10-monitoring-logging/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第10章容器监控与日志)

---

### 第三部分：高级特性（11-15章）⭐⭐⭐⭐⭐

#### [第11章：Docker安全](chapter11-security/README.md)
**学习时间**: 2天 | **难度**: ⭐⭐⭐⭐  
**核心内容**:
- 安全最佳实践
- 镜像扫描和漏洞检测
- Secrets管理
- 安全加固

**资源**:
- 📂 [章节目录](chapter11-security/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第11章docker安全)

---

#### [第12章：Docker Swarm集群](chapter12-swarm/README.md)
**学习时间**: 2天 | **难度**: ⭐⭐⭐⭐⭐  
**核心内容**:
- Swarm架构
- 集群初始化和管理
- 服务部署和滚动更新
- 负载均衡

**资源**:
- 📂 [章节目录](chapter12-swarm/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第12章docker-swarm集群)

---

#### [第13章：Docker与CI/CD](chapter13-cicd/README.md)
**学习时间**: 2-3天 | **难度**: ⭐⭐⭐⭐⭐  
**核心内容**:
- CI/CD流程
- Jenkins/GitLab CI集成
- GitHub Actions
- 部署策略

**资源**:
- 📂 [章节目录](chapter13-cicd/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第13章docker与cicd)

---

#### [第14章：Docker性能优化](chapter14-performance/README.md)
**学习时间**: 1-2天 | **难度**: ⭐⭐⭐⭐  
**核心内容**:
- 镜像优化技巧
- 容器性能调优
- 存储驱动选择
- 性能监控

**资源**:
- 📂 [章节目录](chapter14-performance/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第14章docker性能优化)

---

#### [第15章：企业级实战案例](chapter15-enterprise-cases/README.md)
**学习时间**: 2-3天 | **难度**: ⭐⭐⭐⭐⭐  
**核心内容**:
- 微服务架构
- 完整项目部署
- 生产环境最佳实践
- 故障排查和运维

**资源**:
- 📂 [章节目录](chapter15-enterprise-cases/)
- 📋 [内容大纲](CHAPTERS_OUTLINE.md#第15章企业级实战案例)

---

## 🎯 学习路径推荐

### 路径1: 快速入门（1周）
适合：需要快速上手Docker的开发者
```
第1章 → 第2章 → 第3章 → 第5章 → 第8章
```

### 路径2: 全面学习（4周）
适合：系统学习Docker的学习者
```
第1-15章按顺序学习
```

### 路径3: 运维专精（3周）
适合：运维工程师
```
第1-7章 → 第9-12章 → 第14章 → 第15章
```

### 路径4: 开发专精（2周）
适合：应用开发者
```
第1-8章 → 第13章
```

---

## 📊 学习进度追踪

复制以下清单到你的笔记中，完成一章打勾：

```markdown
## 我的学习进度

### 基础入门
- [ ] 第1章：Docker简介与安装
- [ ] 第2章：Docker基础概念
- [ ] 第3章：Docker镜像管理
- [ ] 第4章：Docker容器操作
- [ ] 第5章：Dockerfile详解

### 进阶应用
- [ ] 第6章：Docker数据管理
- [ ] 第7章：Docker网络
- [ ] 第8章：Docker Compose
- [ ] 第9章：Docker私有仓库
- [ ] 第10章：容器监控与日志

### 高级特性
- [ ] 第11章：Docker安全
- [ ] 第12章：Docker Swarm集群
- [ ] 第13章：Docker与CI/CD
- [ ] 第14章：Docker性能优化
- [ ] 第15章：企业级实战案例

### 实践项目
- [ ] 容器化第一个应用
- [ ] 编写第一个Dockerfile
- [ ] 部署多容器应用
- [ ] 搭建私有仓库
- [ ] 实施监控系统
- [ ] 完成企业级项目
```

---

## 🔍 快速查找

### 按主题查找

**容器基础**
- [运行容器](chapter01-introduction/README.md#15-验证安装)
- [容器生命周期](chapter02-basic-concepts/README.md#22-容器深入理解)
- [容器操作](chapter04-container-operations/README.md)

**镜像管理**
- [镜像操作](chapter03-image-management/README.md)
- [Dockerfile](chapter05-dockerfile/README.md)
- [镜像优化](chapter05-dockerfile/README.md#55-镜像优化技巧)

**数据和网络**
- [数据卷](chapter06-data-management/README.md#62-数据卷-volumes)
- [网络配置](chapter07-networking/README.md)
- [端口映射](chapter07-networking/README.md#76-端口映射)

**应用编排**
- [Docker Compose](chapter08-docker-compose/README.md)
- [多容器应用](chapter08-docker-compose/README.md#83-完整示例)

**运维监控**
- [监控](CHAPTERS_OUTLINE.md#第10章容器监控与日志)
- [日志](CHAPTERS_OUTLINE.md#第10章容器监控与日志)
- [安全](CHAPTERS_OUTLINE.md#第11章docker安全)

**集群和CI/CD**
- [Swarm](CHAPTERS_OUTLINE.md#第12章docker-swarm集群)
- [CI/CD](CHAPTERS_OUTLINE.md#第13章docker与cicd)

---

## 💻 代码示例索引

### 第1章
- [运行hello-world](chapter01-introduction/README.md#153-运行第一个容器)
- [运行Nginx](chapter01-introduction/README.md#练习1运行nginx-web服务器)
- [交互式Ubuntu](chapter01-introduction/README.md#练习2交互式运行ubuntu容器)

### 第5章
- [Flask应用](chapter05-dockerfile/README.md#561-flask-web应用)
- [Node.js应用](chapter05-dockerfile/README.md#562-nodejs应用)
- [Go应用](chapter05-dockerfile/README.md#563-go应用)

### 第8章
- [WordPress](chapter08-docker-compose/README.md#831-wordpress--mysql)
- [微服务架构](chapter08-docker-compose/README.md#833-微服务架构示例)
- [LNMP环境](chapter08-docker-compose/README.md#练习1-lnmp环境)

---

## 📖 相关资源

### 官方资源
- [Docker官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker GitHub](https://github.com/docker)

### 在线实践
- [Play with Docker](https://labs.play-with-docker.com/)
- [Katacoda Docker教程](https://www.katacoda.com/courses/docker)

### 推荐阅读
- Docker最佳实践
- 容器化设计模式
- 微服务架构

---

## 🆘 获取帮助

### 遇到问题时
1. 查看本章节的FAQ
2. 查看[官方文档](https://docs.docker.com/)
3. 搜索[Stack Overflow](https://stackoverflow.com/questions/tagged/docker)
4. 查看[Docker论坛](https://forums.docker.com/)

### 学习建议
- 按顺序学习，不跳章
- 每个命令都要亲自运行
- 完成所有练习题
- 尝试实际项目

---

**祝你学习愉快！成为Docker专家！** 🐳🚀
