# Grafana教程配套代码示例

本目录包含Grafana教程各章节的配套可运行代码示例。

## 目录结构

```
code/
├── chapter1/          # 第1章：基础概念和安装
│   ├── docker-compose.yml
│   ├── grafana.ini
│   └── README.md
├── chapter2/          # 第2章：数据源配置和连接
│   ├── prometheus/
│   ├── influxdb/
│   ├── mysql/
│   └── README.md
├── chapter3/          # 第3章：仪表板创建和面板配置
│   ├── dashboards/
│   ├── panel-examples/
│   └── README.md
├── chapter4/          # 第4章：查询语言和数据处理
│   ├── promql-examples/
│   ├── flux-examples/
│   ├── sql-examples/
│   └── README.md
├── chapter5/          # 第5章：告警和通知配置
│   ├── alert-rules/
│   ├── notification-templates/
│   └── README.md
├── chapter6/          # 第6章：高级功能和最佳实践
│   ├── plugins/
│   ├── automation/
│   └── README.md
└── shared/            # 共享配置和工具
    ├── scripts/
    ├── configs/
    └── README.md
```

## 使用说明

### 环境要求

- Docker 和 Docker Compose
- 至少4GB可用内存
- Linux/macOS/Windows WSL2

### 快速开始

1. 进入对应章节目录
2. 运行 `docker-compose up -d`
3. 访问 http://localhost:3000 (Grafana)
4. 默认用户名/密码: admin/admin

### 章节说明

每个章节包含：
- 完整的Docker Compose配置
- 预配置的数据源和仪表板
- 示例数据和查询
- 详细的README说明

## 注意事项

- 所有代码示例都经过测试，确保可运行
- 生产环境使用时请修改默认密码和配置
- 建议在隔离的测试环境中运行
- 定期备份重要配置和数据