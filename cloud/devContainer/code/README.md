# DevContainer 代码示例

本目录包含DevContainer教程中使用的所有代码示例，方便读者直接运行和实验。

## 目录结构

```
code/
├── README.md                   # 本文件
├── basic-nodejs/              # 基础Node.js开发环境
├── python-data-science/       # Python数据科学环境
├── fullstack-app/             # 全栈应用开发环境
├── multi-service/             # 多服务架构环境
└── advanced-features/         # 高级特性演示
```

## 使用说明

每个子目录都是一个完整的DevContainer项目，包含：

- `.devcontainer/devcontainer.json` - 主要配置文件
- `.devcontainer/Dockerfile` - 自定义Dockerfile（如果需要）
- 示例代码和配置文件

## 如何运行

1. 打开VS Code
2. 安装"Remote - Containers"扩展
3. 打开任意子目录
4. 按`Ctrl+Shift+P`，输入"Reopen in Container"
5. 等待容器构建完成

## 实验顺序

建议按照以下顺序进行实验：

1. `basic-nodejs/` - 基础环境配置
2. `python-data-science/` - 多语言环境
3. `fullstack-app/` - 复杂项目配置
4. `multi-service/` - 多服务架构
5. `advanced-features/` - 高级特性

每个实验都包含了详细的注释和说明，帮助理解DevContainer的各个特性。