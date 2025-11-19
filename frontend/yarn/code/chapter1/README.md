# 第1章代码示例 - Yarn简介与环境搭建

本目录包含第1章"Yarn简介与环境搭建"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. 基础项目结构
- **basic-project/** - 基础Yarn项目结构
- **npm-migration-project/** - 从NPM迁移到Yarn的示例项目

### 2. 配置文件示例
- **.yarnrc** - Yarn配置文件示例
- **.npmrc** - NPM配置文件示例（用于迁移场景）
- **package.json** - 包配置文件示例

### 3. 环境检查脚本
- **check-environment.js** - 环境检查脚本
- **install-check.js** - 安装验证脚本

## 使用说明

1. 进入示例目录：
   ```bash
   cd chapter1
   ```

2. 初始化基础项目：
   ```bash
   cd basic-project
   yarn install
   ```

3. 检查环境：
   ```bash
   node check-environment.js
   ```

## 运行说明

1. 基础项目安装和验证：
   ```bash
   cd basic-project
   yarn install
   node install-check.js
   ```

2. NPM迁移示例：
   ```bash
   cd npm-migration-project
   yarn install
   # 观察生成的yarn.lock文件
   ```

## 环境要求

- Node.js 14.0+
- Yarn 1.22.0+（或使用Corepack）
- 基本的命令行操作知识

## 目录结构

```
chapter1/
├── README.md                          # 本文件
├── basic-project/                     # 基础Yarn项目
│   ├── package.json                  # 包配置
│   ├── .yarnrc                       # Yarn配置
│   ├── src/                          # 源代码目录
│   │   └── index.js                  # 主入口文件
│   └── dist/                         # 构建输出目录
├── npm-migration-project/            # NPM迁移项目
│   ├── package.json                  # 原始NPM项目配置
│   ├── package-lock.json             # 原始NPM锁定文件
│   └── src/                          # 源代码目录
│       └── index.js                  # 主入口文件
├── check-environment.js              # 环境检查脚本
└── install-check.js                  # 安装验证脚本
```

## 注意事项

1. 确保已正确安装Node.js和Yarn
2. 使用Node.js LTS版本以获得最佳兼容性
3. 在企业环境中可能需要配置代理或镜像源
4. 对于Yarn 2.x/3.x，项目结构会有所不同