# 第2章代码示例 - Yarn基础命令与包管理

本目录包含第2章"Yarn基础命令与包管理"的代码示例，涵盖以下内容：

## 代码示例说明

### 1. 基础命令示例
- **basic-project/** - 基础项目结构
- **dependency-demo/** - 依赖管理示例
- **script-demo/** - 脚本管理示例

### 2. 依赖管理示例
- **version-control/** - 版本控制示例
- **cache-demo/** - 缓存管理示例
- **global-packages/** - 全局包管理示例

### 3. 配置文件示例
- **.yarnrc** - Yarn配置文件示例
- **package-examples/** - 不同类型的package.json示例

### 4. 工具脚本
- **dependency-checker.js** - 依赖检查工具
- **version-analyzer.js** - 版本分析工具

## 使用说明

1. 进入示例目录：
   ```bash
   cd chapter2
   ```

2. 选择一个示例项目：
   ```bash
   cd basic-project
   ```

3. 安装依赖：
   ```bash
   yarn install
   ```

4. 运行示例：
   ```bash
   yarn start
   ```

## 运行说明

1. 基础命令示例：
   ```bash
   cd basic-project
   yarn install
   yarn start
   ```

2. 依赖管理示例：
   ```bash
   cd dependency-demo
   yarn add lodash
   yarn list
   yarn remove lodash
   ```

3. 脚本管理示例：
   ```bash
   cd script-demo
   yarn run
   yarn dev
   ```

## 环境要求

- Node.js 14.0+
- Yarn 1.22.0+
- 基本的命令行操作知识

## 目录结构

```
chapter2/
├── README.md                          # 本文件
├── basic-project/                     # 基础项目示例
│   ├── package.json                  # 包配置
│   ├── src/                          # 源代码
│   │   └── index.js                  # 主入口文件
│   └── dist/                         # 构建输出目录
├── dependency-demo/                   # 依赖管理示例
│   ├── package.json                  # 包配置
│   └── src/                          # 源代码
├── script-demo/                       # 脚本管理示例
│   ├── package.json                  # 包配置
│   └── scripts/                       # 脚本目录
├── version-control/                   # 版本控制示例
│   ├── package.json                  # 包配置
│   └── .yarnrc                        # Yarn配置
├── cache-demo/                        # 缓存管理示例
│   ├── package.json                  # 包配置
│   └── cache-info.js                  # 缓存信息脚本
├── global-packages/                   # 全局包管理示例
│   ├── global-cli/                    # 全局CLI工具
│   │   ├── package.json              # 包配置
│   │   └── bin/                       # 可执行文件
│   └── install-global.sh              # 全局安装脚本
├── .yarnrc                            # Yarn全局配置
├── dependency-checker.js              # 依赖检查工具
└── version-analyzer.js                # 版本分析工具
```

## 注意事项

1. 确保已正确安装Node.js和Yarn
2. 部分示例可能需要网络连接以下载依赖
3. 全局包示例可能需要管理员权限
4. 缓存管理示例会修改本地Yarn缓存，请谨慎使用
5. 版本控制示例会修改package.json文件，建议先备份