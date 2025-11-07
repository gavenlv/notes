# Prometheus：从零基础到专家（完整中文教程）

## 📚 Prometheus完整学习指南

这是一套全面的、实战导向的Prometheus中文学习教程，从绝对零基础到专家级别。每个概念都通过深入讲解、实例演示和实验验证来确保理解。

**适合人群：**
- 0基础初学者（完全不了解监控系统）
- 运维工程师（DevOps/SRE）
- 后端开发人员
- 系统架构师
- 云原生技术学习者

---

## 🎯 学习路径

```
第1-2章：基础入门 (安装配置+核心概念)
    ↓
第3-4章：查询与导出 (PromQL+Exporters)
    ↓
第5-6章：服务发现与告警 (SD机制+Alertmanager)
    ↓
第7-8章：高级特性 (Recording Rules+Pushgateway)
    ↓
第9-10章：生产就绪 (高可用+性能优化)
    ↓
第11-12章：实战应用 (应用监控+完整方案)
```

---

## 📖 目录

### [第1章：Prometheus安装与环境配置](第1章-Prometheus安装与环境配置.md)
**Prometheus安装与环境配置**

学习如何在各种环境中安装和配置Prometheus。

**学习内容：**
- ✅ Prometheus简介和架构
- ✅ 核心概念：指标、标签、时间序列
- ✅ 系统要求和存储规划
- ✅ 多种安装方式（Docker、Linux、Windows、macOS）
- ✅ 配置文件详解
- ✅ Web界面使用
- ✅ 完整监控环境实验
- ✅ 故障排查和最佳实践

**代码示例：** [`code/chapter01/`](code/chapter01/)

**学习时长：** 3-4小时

---

### [第2章：Prometheus核心概念](第2章-Prometheus核心概念.md)
**指标类型、数据模型与标签系统**

深入理解Prometheus的数据模型和工作原理。

**学习内容：**
- ✅ 四种指标类型（Counter、Gauge、Histogram、Summary）
- ✅ 数据模型深度解析
- ✅ 标签系统和最佳实践
- ✅ 指标命名规范
- ✅ 时间序列唯一性
- ✅ 实战：设计监控指标体系

**代码示例：** [`code/chapter02/`](code/chapter02/)

**学习时长：** 4-5小时

---

### [第3章：PromQL查询语言](第3章-PromQL查询语言.md)
**从基础到高级的完整PromQL指南**

掌握Prometheus强大的查询语言。

**学习内容：**
- ✅ PromQL基础语法
- ✅ 选择器和过滤器
- ✅ 聚合操作（sum、avg、max、min等）
- ✅ 函数大全（rate、increase、histogram_quantile等）
- ✅ 向量匹配和运算
- ✅ 子查询和高级用法
- ✅ 查询优化技巧
- ✅ 实战：复杂查询编写

**代码示例：** [`code/chapter03/`](code/chapter03/)

**学习时长：** 6-8小时

---

### [第4章：Exporters导出器](第4章-Exporters导出器.md)
**系统、应用和自定义Exporter详解**

学习如何使用和开发Exporters收集指标。

**学习内容：**
- ✅ Exporter工作原理
- ✅ Node Exporter（系统指标）深度使用
- ✅ 常用Exporters（MySQL、Redis、Nginx等）
- ✅ 开发自定义Exporter（Go、Python）
- ✅ Textfile Collector使用
- ✅ Exporter最佳实践
- ✅ 实战：监控完整技术栈

**代码示例：** [`code/chapter04/`](code/chapter04/)

**学习时长：** 5-6小时

---

### [第5章：服务发现机制](第5章-服务发现机制.md)
**动态目标发现与配置**

掌握Prometheus的自动服务发现能力。

**学习内容：**
- ✅ 静态配置 vs 动态发现
- ✅ 文件服务发现（file_sd）
- ✅ Kubernetes服务发现
- ✅ Consul服务发现
- ✅ DNS服务发现
- ✅ 云平台服务发现（AWS、GCP、Azure）
- ✅ Relabeling配置详解
- ✅ 实战：Kubernetes集群监控

**代码示例：** [`code/chapter05/`](code/chapter05/)

**学习时长：** 5-6小时

---

### [第6章：告警规则与Alertmanager](第6章-告警规则与Alertmanager.md)
**完整的告警体系搭建**

构建生产级别的告警系统。

**学习内容：**
- ✅ 告警规则编写
- ✅ Alertmanager架构
- ✅ 告警路由和分组
- ✅ 通知渠道配置（Email、Slack、钉钉、企业微信）
- ✅ 抑制和静默
- ✅ 告警模板定制
- ✅ 高可用Alertmanager
- ✅ 实战：完整告警方案

**代码示例：** [`code/chapter06/`](code/chapter06/)

**学习时长：** 5-6小时

---

### [第7章：Recording Rules记录规则](第7章-Recording-Rules记录规则.md)
**性能优化的利器**

使用Recording Rules优化复杂查询性能。

**学习内容：**
- ✅ Recording Rules原理
- ✅ 规则编写和组织
- ✅ 预聚合策略
- ✅ 性能对比测试
- ✅ 最佳实践和常见模式
- ✅ 实战：大规模指标预聚合

**代码示例：** [`code/chapter07/`](code/chapter07/)

**学习时长：** 3-4小时

---

### [第8章：Pushgateway推送网关](第8章-Pushgateway推送网关.md)
**短期任务和批处理作业监控**

学习监控批处理任务和定时作业。

**学习内容：**
- ✅ Pushgateway使用场景
- ✅ 推送指标的方法
- ✅ 标签处理和分组
- ✅ 与定时任务集成
- ✅ 最佳实践和注意事项
- ✅ 实战：监控批处理作业

**代码示例：** [`code/chapter08/`](code/chapter08/)

**学习时长：** 3-4小时

---

### [第9章：高可用与联邦集群](第9章-高可用与联邦集群.md)
**生产环境部署架构**

构建高可用和可扩展的Prometheus架构。

**学习内容：**
- ✅ 高可用架构设计
- ✅ Prometheus联邦
- ✅ 远程存储（Thanos、Cortex、M3DB）
- ✅ 数据分片策略
- ✅ 多集群管理
- ✅ 实战：企业级Prometheus架构

**代码示例：** [`code/chapter09/`](code/chapter09/)

**学习时长：** 6-8小时

---

### [第10章：性能优化与最佳实践](第10章-性能优化与最佳实践.md)
**生产环境调优指南**

优化Prometheus性能和资源使用。

**学习内容：**
- ✅ 存储优化和数据保留
- ✅ 查询性能优化
- ✅ 标签设计最佳实践
- ✅ 资源规划和容量评估
- ✅ 监控Prometheus自身
- ✅ 常见性能问题排查
- ✅ 实战：大规模Prometheus调优

**代码示例：** [`code/chapter10/`](code/chapter10/)

**学习时长：** 4-5小时

---

### [第11章：应用程序监控](第11章-应用程序监控.md)
**应用级别的监控实践**

为应用程序添加Prometheus监控。

**学习内容：**
- ✅ 客户端库使用（Go、Python、Java、Node.js）
- ✅ 自定义指标设计
- ✅ 业务指标监控
- ✅ HTTP中间件集成
- ✅ 分布式追踪集成
- ✅ 实战：微服务监控完整方案

**代码示例：** [`code/chapter11/`](code/chapter11/)

**学习时长：** 6-8小时

---

### [第12章：实战项目](第12章-实战项目.md)
**完整的生产级监控方案**

将所学知识应用到真实项目中。

**学习内容：**
- ✅ Kubernetes集群完整监控
- ✅ 微服务架构监控方案
- ✅ 数据库监控（MySQL、PostgreSQL、Redis、MongoDB）
- ✅ 中间件监控（Kafka、RabbitMQ、Nginx）
- ✅ 业务监控Dashboard设计
- ✅ SLI/SLO/SLA监控
- ✅ 实战：从零搭建企业级监控平台

**代码示例：** [`code/chapter12/`](code/chapter12/)

**学习时长：** 10-12小时

---

## 🚀 快速开始

### 前置要求
- Docker和Docker Compose已安装
- 基本的Linux命令行知识
- 4GB+内存推荐

### 5分钟快速体验

```bash
# 克隆代码仓库（或直接使用）
cd observability/prometheus

# 启动基础Prometheus
cd code/chapter01/01-docker-basic
docker run -d --name prometheus -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest

# 访问Prometheus
# http://localhost:9090
```

### 完整监控栈

```bash
# 启动完整监控环境（Prometheus + Exporters + Grafana + Alertmanager）
cd code/chapter01/02-docker-compose
docker-compose up -d

# 访问服务
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin123)
# Alertmanager: http://localhost:9093
```

---

## 📁 代码结构

所有代码示例按章节组织：

```
code/
├── chapter01/           # 安装与配置
│   ├── 01-docker-basic/         # 基础Docker运行
│   ├── 02-docker-compose/       # 完整监控栈
│   ├── 03-complete-lab/         # 综合实验环境
│   └── 04-exercises/            # 练习题答案
│
├── chapter02/           # 核心概念
│   ├── 01-metric-types/         # 指标类型示例
│   ├── 02-labels-demo/          # 标签系统演示
│   └── 03-data-model/           # 数据模型实验
│
├── chapter03/           # PromQL
│   ├── 01-basic-queries/        # 基础查询
│   ├── 02-functions/            # 函数使用
│   ├── 03-aggregations/         # 聚合操作
│   └── 04-advanced/             # 高级查询
│
├── chapter04/           # Exporters
│   ├── 01-node-exporter/        # Node Exporter配置
│   ├── 02-common-exporters/     # 常用Exporters
│   ├── 03-custom-exporter/      # 自定义Exporter开发
│   │   ├── go/                  # Go语言实现
│   │   └── python/              # Python实现
│   └── 04-textfile-collector/   # Textfile Collector
│
├── chapter05/           # 服务发现
│   ├── 01-file-sd/              # 文件服务发现
│   ├── 02-kubernetes/           # K8s服务发现
│   ├── 03-consul/               # Consul集成
│   └── 04-relabeling/           # Relabeling配置
│
├── chapter06/           # 告警
│   ├── 01-alert-rules/          # 告警规则示例
│   ├── 02-alertmanager/         # Alertmanager配置
│   ├── 03-notification/         # 通知渠道配置
│   └── 04-templates/            # 告警模板
│
├── chapter07/           # Recording Rules
│   ├── 01-basic-rules/          # 基础规则
│   ├── 02-performance/          # 性能对比
│   └── 03-patterns/             # 常见模式
│
├── chapter08/           # Pushgateway
│   ├── 01-basic-usage/          # 基础使用
│   ├── 02-cron-jobs/            # 定时任务集成
│   └── 03-batch-jobs/           # 批处理作业
│
├── chapter09/           # 高可用
│   ├── 01-ha-setup/             # HA配置
│   ├── 02-federation/           # 联邦集群
│   └── 03-remote-storage/       # 远程存储（Thanos）
│
├── chapter10/          # 性能优化
│   ├── 01-storage-tuning/       # 存储优化
│   ├── 02-query-optimization/   # 查询优化
│   └── 03-resource-planning/    # 资源规划
│
├── chapter11/          # 应用监控
│   ├── 01-go-client/            # Go客户端
│   ├── 02-python-client/        # Python客户端
│   ├── 03-java-client/          # Java客户端
│   └── 04-nodejs-client/        # Node.js客户端
│
└── chapter12/          # 实战项目
    ├── 01-kubernetes/           # K8s完整监控
    ├── 02-microservices/        # 微服务监控
    ├── 03-databases/            # 数据库监控
    └── 04-complete-solution/    # 完整企业方案
```

---

## 🎓 学习方法

### 零基础学习者

**推荐路径：**
1. 按章节顺序学习
2. 完成每章的实验和练习
3. 运行所有代码示例
4. 搭建自己的监控环境
5. 监控实际应用

**学习时间：**
- **快速学习**：40-50小时（2周密集学习）
- **推荐节奏**：2-3个月（每周5-8小时）
- **深度掌握**：6个月（包含实战项目）

### 有经验的用户

跳转到相关章节：
- **DevOps工程师**：重点学习第6、9、10、12章
- **SRE团队**：重点学习第6、7、9、10、12章
- **后端开发**：重点学习第3、4、11章
- **架构师**：重点学习第5、9、10、12章

---

## 💡 核心特色

### ✅ 深入浅出
- 每个概念都从零开始讲解
- 复杂原理用图表和类比说明
- 循序渐进的知识体系

### ✅ 实战导向
- 所有概念都有代码验证
- 完整的Docker Compose环境
- 真实场景的实战项目

### ✅ 生产级别
- 生产环境最佳实践
- 性能优化技巧
- 故障排查指南

### ✅ 代码齐全
- 所有示例都在`code/`目录
- 即拷即用的配置
- 经过测试验证

---

## 🛠️ 涵盖技术

### 监控组件
- **Prometheus** (最新版本)
- **Alertmanager** (告警管理)
- **Pushgateway** (推送网关)
- **Grafana** (可视化)

### Exporters
- Node Exporter (系统指标)
- cAdvisor (容器指标)
- MySQL Exporter
- Redis Exporter
- Nginx Exporter
- Blackbox Exporter (黑盒监控)

### 集成
- Kubernetes
- Docker & Docker Compose
- 主流编程语言客户端
- 云平台（AWS、Azure、GCP）

---

## 📝 学习前提

### 必需
- Linux基础命令
- YAML语法基础
- Docker基础概念

### 推荐
- HTTP协议了解
- 监控系统基本概念
- 正则表达式基础

### 不需要
- 无需Prometheus使用经验
- 无需编程基础（第11章除外）
- 无需高级运维知识

---

## 🎯 学习目标

学完本教程后，你将能够：

✅ 独立安装和配置Prometheus  
✅ 编写复杂的PromQL查询  
✅ 部署和管理各种Exporters  
✅ 设计完整的告警体系  
✅ 搭建高可用Prometheus集群  
✅ 优化Prometheus性能  
✅ 为应用程序添加监控  
✅ 构建企业级监控解决方案  
✅ 排查常见问题  
✅ 集成Prometheus到现有基础设施  

---

## 🔧 环境要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 磁盘: 20GB
- 操作系统: Windows 10+, macOS 10.14+, Linux

### 推荐配置
- CPU: 4+核
- 内存: 8GB+
- 磁盘: 50GB+ (用于数据保留)
- 操作系统: Linux (Ubuntu 20.04+)

---

## 📚 补充资源

### 官方文档
- [Prometheus官方文档](https://prometheus.io/docs/)
- [PromQL查询语言](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [最佳实践](https://prometheus.io/docs/practices/)

### 社区
- [Prometheus GitHub](https://github.com/prometheus/prometheus)
- [CNCF Prometheus](https://www.cncf.io/projects/prometheus/)
- [中文社区](https://prometheus.fuckcloudnative.io/)

### 在线工具
- [PromLens](https://promlens.com/) - PromQL查询构建器
- [Prometheus Demo](https://demo.promlabs.com/) - 在线演示

---

## 🤝 如何使用本教程

### 学习建议

1. **按顺序学习**：章节之间有依赖关系
2. **运行所有代码**：不要只阅读，要动手实践
3. **做实验**：修改配置看效果
4. **完成练习**：巩固所学知识
5. **搭建项目**：应用到实际场景
6. **记录笔记**：记录遇到的问题和解决方案

### 时间规划

**推荐学习计划：**
- **第1-2周**：第1-2章（基础安装和核心概念）
- **第3-4周**：第3-4章（PromQL和Exporters）
- **第5-6周**：第5-6章（服务发现和告警）
- **第7-8周**：第7-8章（Recording Rules和Pushgateway）
- **第9-10周**：第9-10章（高可用和性能优化）
- **第11-12周**：第11-12章（应用监控和实战项目）

---

## 🎓 认证与职业发展

### 获得的能力
- Prometheus架构设计
- PromQL精通
- 监控策略制定
- 可观测性最佳实践

### 职业方向
- **DevOps工程师**：搭建监控基础设施
- **SRE工程师**：实现SLI/SLO监控
- **平台工程师**：管理可观测性平台
- **系统架构师**：设计监控架构

---

## 🌟 下一步

完成本教程后：

1. **构建作品集**：创建独特的监控Dashboard
2. **贡献社区**：分享Dashboard和Exporter
3. **探索集成**：学习Thanos、Cortex等扩展
4. **持续学习**：关注Prometheus新版本特性
5. **分享知识**：教授他人Prometheus

---

## 📞 支持

**文档问题：**
- 查看具体章节
- 检查`code/`目录中的示例
- 查看故障排查部分

**技术问题：**
- 搜索[Prometheus官方文档](https://prometheus.io/docs/)
- 查看[GitHub Issues](https://github.com/prometheus/prometheus/issues)
- 访问[中文社区](https://prometheus.fuckcloudnative.io/)

**仍然卡住？**
- 在社区论坛发帖，包含：
  - Prometheus版本
  - 系统信息
  - 错误信息
  - 重现步骤

---

## 🎉 开始学习！

准备好成为Prometheus专家了吗？

**👉 从 [第1章：Prometheus安装与环境配置](第1章-Prometheus安装与环境配置.md) 开始学习**

**祝学习顺利！监控愉快！ 📊📈**

---

**最后更新**：2024-11-06  
**Prometheus版本**：2.45+  
**难度级别**：零基础到专家  
**总学时**：50-70小时  
**语言**：简体中文
