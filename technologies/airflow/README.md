# Apache Airflow 学习路径：从零基础到精通

## 📋 学习概述

本学习路径将带您从 Airflow 零基础开始，逐步掌握 Airflow 的核心概念、高级特性和企业级应用，最终成为 Airflow 专家。通过 16 天的系统学习，您将能够设计、实施和维护复杂的数据管道和工作流管理系统。

## 🎯 学习目标

- 掌握 Airflow 核心概念和架构
- 能够设计和实现复杂的数据管道
- 熟练使用 Airflow 高级特性和扩展
- 具备企业级 Airflow 部署和运维能力
- 能够解决复杂的数据工作流问题

## 📚 学习路径

### 第一阶段：基础入门 (Day 1-4)
- **Day 1: [安装与环境配置](day1-installation/)** - 搭建 Airflow 开发环境
- **Day 2: [核心概念与架构](day2-concepts-architecture/)** - 理解 Airflow 核心组件
- **Day 3: [DAG 基础与任务定义](day3-dag-basics/)** - 创建第一个工作流
- **Day 4: [操作符与 Hook](day4-operators-hooks/)** - 掌握任务执行机制

### 第二阶段：核心功能 (Day 5-8)
- **Day 5: [依赖管理与调度](day5-dependencies-scheduling/)** - 控制任务执行顺序
- **Day 6: [模板与 Jinja2](day6-templating-jinja2/)** - 动态任务配置
- **Day 7: [变量与连接](day7-variables-connections/)** - 管理配置和凭据
- **Day 8: [监控与日志](day8-monitoring-logging/)** - 跟踪工作流执行

### 第三阶段：高级特性 (Day 9-12)
- **Day 9: [XComs 与任务间通信](day9-xcoms-communication/)** - 任务数据传递
- **Day 10: [动态 DAG 生成](day10-dynamic-dags/)** - 程序化工作流创建
- **Day 11: [自定义操作符与插件](day11-custom-operators-plugins/)** - 扩展 Airflow 功能
- **Day 12: [传感器与触发器](day12-sensors-triggers/)** - 响应外部事件

### 第四阶段：企业应用 (Day 13-16)
- **Day 13: [安全与权限](day13-security-permissions/)** - 企业级安全配置
- **Day 14: [性能优化与扩展](day14-performance-scaling/)** - 大规模部署优化
- **Day 15: [CI/CD 集成与测试](day15-cicd-testing/)** - 自动化部署与测试
- **Day 16: [项目实战](day16-project-implementation/)** - 完整企业级项目实施

## 🔧 环境要求

### 基础环境
- **操作系统**: Windows 10/11, macOS 10.15+, 或 Linux (Ubuntu 18.04+)
- **Python**: 3.8+ (推荐 3.9 或 3.10)
- **内存**: 最少 4GB RAM (推荐 8GB+)
- **存储**: 最少 10GB 可用空间

### 开发工具
- **IDE**: PyCharm, VS Code 或其他 Python IDE
- **版本控制**: Git
- **容器**: Docker 和 Docker Compose (可选，但推荐)
- **数据库**: PostgreSQL 或 MySQL (用于生产环境元数据)

### 依赖软件
- **Apache Airflow**: 2.3+ (最新稳定版)
- **数据库客户端**: DBeaver 或 pgAdmin
- **消息队列**: Redis 或 RabbitMQ (可选，用于 Celery 执行器)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd technologies/airflow
```

### 2. 设置环境
```bash
# 创建虚拟环境
python -m venv airflow-env
source airflow-env/bin/activate  # Linux/macOS
# 或
airflow-env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 第一天学习
```bash
cd day1-installation
# 按照指南完成环境搭建
```

### 4. 验证安装
```bash
# 启动 Airflow
airflow standalone

# 访问 Web UI
http://localhost:8080
```

## 📁 目录结构

```
airflow/
├── README.md                     # 本文件
├── requirements.txt               # Python 依赖
├── docker-compose.yml            # Docker 环境配置
├── .gitignore                    # Git 忽略文件
├── day1-installation/            # Day 1: 安装与环境配置
├── day2-concepts-architecture/   # Day 2: 核心概念与架构
├── day3-dag-basics/              # Day 3: DAG 基础与任务定义
├── day4-operators-hooks/         # Day 4: 操作符与 Hook
├── day5-dependencies-scheduling/ # Day 5: 依赖管理与调度
├── day6-templating-jinja2/       # Day 6: 模板与 Jinja2
├── day7-variables-connections/   # Day 7: 变量与连接
├── day8-monitoring-logging/       # Day 8: 监控与日志
├── day9-xcoms-communication/     # Day 9: XComs 与任务间通信
├── day10-dynamic-dags/            # Day 10: 动态 DAG 生成
├── day11-custom-operators-plugins/ # Day 11: 自定义操作符与插件
├── day12-sensors-triggers/        # Day 12: 传感器与触发器
├── day13-security-permissions/    # Day 13: 安全与权限
├── day14-performance-scaling/     # Day 14: 性能优化与扩展
├── day15-cicd-testing/            # Day 15: CI/CD 集成与测试
├── day16-project-implementation/  # Day 16: 项目实战
├── configs/                       # 配置文件和模板
├── examples/                      # 示例 DAG 和代码
├── scripts/                       # 辅助脚本
└── docs/                          # 补充文档和参考资料
```

## 📖 学习资源

### 官方资源
- [Apache Airflow 官方文档](https://airflow.apache.org/docs/apache-airflow/stable/)
- [Airflow GitHub 仓库](https://github.com/apache/airflow)
- [Airflow 官方博客](https://airflow.apache.org/blog/)

### 推荐书籍
- "Data Pipelines with Apache Airflow" - Bas Harenslak & Julian de Ruiter
- "Working with Apache Airflow" - Krishna Puttamparthi

### 社区资源
- [Airflow Slack 社区](https://apache-airflow.slack.com/)
- [Stack Overflow Airflow 标签](https://stackoverflow.com/questions/tagged/apache-airflow)
- [Airflow 用户邮件列表](https://lists.apache.org/list.html?users@airflow.apache.org)

## 🎓 学习成果

完成本学习路径后，您将能够：

1. **设计复杂工作流**：创建多步骤、多依赖的数据管道
2. **优化性能**：配置和调优大规模 Airflow 部署
3. **扩展功能**：开发自定义操作符和插件
4. **确保安全**：实施企业级安全策略
5. **自动化运维**：集成 CI/CD 流程和监控

## 📊 学习进度跟踪

使用 [PROGRESS.md](PROGRESS.md) 文件跟踪您的学习进度，记录完成的任务和掌握的技能。

## 🤝 贡献指南

欢迎贡献内容、报告问题或提出改进建议！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

---

祝您学习愉快！如有任何问题，请随时通过 Issues 或社区渠道联系我们。