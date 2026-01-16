# 第1章代码示例：Thanos基础概念和架构

## 目录结构

```
chapter1/
├── README.md                 # 本章说明文档
├── architecture-diagrams/    # 架构图文件
│   ├── thanos-architecture.drawio
│   └── thanos-architecture.png
├── config-templates/         # 配置模板
│   ├── sidecar-config.yaml
│   └── query-config.yaml
└── scripts/                  # 实用脚本
    ├── check-dependencies.sh
    └── generate-config.sh
```

## 代码示例说明

### 1. 架构图文件
- **thanos-architecture.drawio**: Draw.io格式的Thanos架构图源文件
- **thanos-architecture.png**: 导出的架构图PNG文件

### 2. 配置模板
- **sidecar-config.yaml**: Sidecar组件的基础配置模板
- **query-config.yaml**: Query组件的基础配置模板

### 3. 实用脚本
- **check-dependencies.sh**: 环境依赖检查脚本
- **generate-config.sh**: 配置文件生成脚本

## 使用说明

1. 查看架构图了解Thanos整体设计
2. 使用配置模板作为实际部署的参考
3. 运行脚本检查环境依赖和生成配置

## 注意事项

- 所有配置文件需要根据实际环境修改
- 脚本需要执行权限：`chmod +x scripts/*.sh`
- 架构图可以使用Draw.io在线工具编辑