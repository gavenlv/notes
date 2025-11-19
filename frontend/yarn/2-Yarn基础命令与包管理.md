# 第2章：Yarn基础命令与包管理

## 概述

本章将详细介绍Yarn的基础命令和包管理功能，包括项目初始化、依赖管理、版本控制、信息查询等核心操作。通过本章学习，您将掌握Yarn的基本使用方法，能够有效管理项目的依赖包。

## 2.1 项目初始化

### 2.1.1 yarn init - 创建新项目

`yarn init`命令用于创建一个新的Yarn项目，它会在当前目录下生成一个`package.json`文件。

#### 基本用法

```bash
# 交互式创建项目
yarn init

# 快速创建（接受默认值）
yarn init -y

# 指定项目名称
yarn init my-project

# 指定项目私有性
yarn init --private
```

#### 交互式创建示例

```bash
$ yarn init
yarn init v1.22.19
question name (yarn-tutorial): my-awesome-project
question version (1.0.0): 1.0.0
question description (My awesome project): 一个非常棒的项目
question entry point (index.js): src/index.js
question repository url (https://github.com/user/my-awesome-project): 
question author (Your Name): 张三
question license (MIT): MIT
question private (false): 

success Saved package.json
✨  Done in 12.45s.
```

#### 生成的package.json示例

```json
{
  "name": "my-awesome-project",
  "version": "1.0.0",
  "description": "一个非常棒的项目",
  "main": "src/index.js",
  "repository": "https://github.com/user/my-awesome-project",
  "author": "张三",
  "license": "MIT"
}
```

### 2.1.2 了解package.json

`package.json`是项目的核心配置文件，包含以下主要字段：

| 字段 | 描述 | 示例 |
|------|------|------|
| name | 项目名称 | "my-project" |
| version | 项目版本 | "1.0.0" |
| description | 项目描述 | "一个JavaScript项目" |
| main | 入口文件 | "src/index.js" |
| scripts | 脚本命令 | {"start": "node src/index.js"} |
| dependencies | 生产依赖 | {"lodash": "^4.17.21"} |
| devDependencies | 开发依赖 | {"nodemon": "^2.0.20"} |
| keywords | 关键词数组 | ["node", "javascript"] |
| author | 作者信息 | {"name": "张三", "email": "zhang@example.com"} |
| license | 许可证 | "MIT" |

## 2.2 依赖管理

### 2.2.1 安装依赖

Yarn提供了多种安装依赖的方式，根据不同的需求和场景选择合适的命令。

#### 安装所有依赖

```bash
# 根据package.json安装所有依赖
yarn install

# 简写形式
yarn
```

#### 添加生产依赖

```bash
# 添加最新版本
yarn add lodash

# 添加指定版本
yarn add lodash@4.17.21

# 添加版本范围
yarn add react@^17.0.0

# 添加多个依赖
yarn add lodash moment express

# 添加并保存到指定依赖类型
yarn add lodash --save    # 生产依赖（默认）
yarn add eslint --save-dev # 开发依赖
```

#### 添加开发依赖

```bash
# 添加开发依赖
yarn add nodemon --dev

# 简写形式
yarn add nodemon -D
```

#### 添加可选依赖

```bash
# 添加可选依赖（安装失败不会中断整个过程）
yarn add fsevents --optional
```

#### 添加精确版本依赖

```bash
# 添加精确版本（不使用范围符号）
yarn add react@16.14.0 --exact

# 简写形式
yarn add react@16.14.0 -E
```

### 2.2.2 更新依赖

Yarn提供了多种更新依赖的方式，可以更新单个依赖、批量更新或更新到指定版本。

#### 更新单个依赖

```bash
# 更新到最新兼容版本（遵循package.json中的版本范围）
yarn upgrade lodash

# 更新到指定版本
yarn upgrade lodash@4.17.21

# 更新到最新版本（不考虑版本范围）
yarn upgrade lodash --latest
```

#### 批量更新

```bash
# 更新所有依赖到最新兼容版本
yarn upgrade

# 更新所有依赖到最新版本（不考虑版本范围）
yarn upgrade --latest
```

#### 交互式更新

```bash
# 交互式选择要更新的依赖
yarn upgrade-interactive --latest
```

### 2.2.3 移除依赖

```bash
# 移除依赖
yarn remove lodash

# 同时移除多个依赖
yarn remove lodash moment
```

移除依赖时，Yarn会：
- 从`node_modules`中删除包
- 从`package.json`中移除相应的条目
- 更新`yarn.lock`文件
- 如果包被其他依赖引用，则会保留

## 2.3 全局操作

### 2.3.1 全局安装包

```bash
# 全局安装包
yarn global add create-react-app

# 全局安装指定版本
yarn global add typescript@4.9.5

# 列出全局安装的包
yarn global list
```

全局安装的包通常用作命令行工具，安装位置：
- macOS/Linux: `~/.config/yarn/global/node_modules/.bin`
- Windows: `%LOCALAPPDATA%\Yarn\Data\global\node_modules\.bin`

### 2.3.2 全局移除包

```bash
# 全局移除包
yarn global remove create-react-app
```

### 2.3.3 查看全局包信息

```bash
# 查看全局安装的包列表
yarn global list

# 查看全局安装的特定包信息
yarn global info create-react-app
```

## 2.4 信息查询

### 2.4.1 查看包信息

```bash
# 查看包的基本信息
yarn info react

# 查看包的特定字段
yarn info react version
yarn info react dependencies
yarn info react homepage

# 查看包的所有信息
yarn info react --json
```

#### 信息字段示例

```bash
$ yarn info react
{ name: 'react',
  description: 'React is a JavaScript library for building user interfaces.',
  version: '18.2.0',
  author: { name: 'Jordan Walke', email: 'jordan.walke@gmail.com' },
  homepage: 'https://reactjs.org/',
  dependencies: { 'loose-envify': '^1.1.0', 'object-assign': '^4.1.1' },
  devDependencies: { 'jest': '26.6.2', 'rollup': '^2.4.1' } }
```

### 2.4.2 列出依赖

```bash
# 列出所有依赖
yarn list

# 列出生产依赖
yarn list --production

# 列出开发依赖
yarn list --dev

# 列出特定模式的依赖
yarn list --pattern "react*"

# 以JSON格式输出
yarn list --json
```

#### 列出依赖示例

```bash
$ yarn list
yarn list v1.22.19
├─ lodash@4.17.21
├─ moment@2.29.4
├─ react@18.2.0
│  └─ loose-envify@1.4.0
│     └─ js-tokens@4.0.0
└─ typescript@4.9.5
✨  Done in 2.67s.
```

### 2.4.3 检查过时依赖

```bash
# 检查过时的依赖
yarn outdated

# 检查特定依赖
yarn outdated react
```

#### 检查过时依赖示例

```bash
$ yarn outdated
yarn list v1.22.19
Info Color legend :
<red>    - major update</red><yellow>    - minor update</yellow><green>    - patch update</green>

Package  Current  Wanted   Latest   Location  Type
react    17.0.2   ^17.0.2  18.2.0   my-app    dependencies
typescript 4.8.3   4.8.3   4.9.5   my-app    devDependencies

✨  Done in 2.67s.
```

## 2.5 缓存管理

Yarn使用缓存机制加速包的安装，了解缓存管理有助于解决安装问题。

### 2.5.1 查看缓存

```bash
# 查看缓存目录
yarn cache dir

# 查看缓存中的包
yarn cache list
```

### 2.5.2 清理缓存

```bash
# 清理缓存
yarn cache clean

# 清理特定包的缓存
yarn cache clean lodash
```

### 2.5.3 验证缓存

```bash
# 验证缓存完整性
yarn cache verify
```

## 2.6 运行脚本

### 2.6.1 运行脚本命令

```bash
# 运行package.json中定义的脚本
yarn run start

# 简写形式
yarn start

# 运行不存在的脚本（会查找全局安装的命令）
yarn run nodemon

# 运行脚本并传递参数
yarn run build --production
```

### 2.6.2 列出可用脚本

```bash
# 列出package.json中定义的所有脚本
yarn run

# 列出全局安装的可执行脚本
yarn global bin
```

### 2.6.3 脚本示例

在`package.json`中定义的脚本示例：

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "clean": "rimraf dist"
  }
}
```

## 2.7 语义化版本控制

Yarn遵循语义化版本控制（Semantic Versioning, SemVer）规范，理解版本控制有助于管理依赖版本。

### 2.7.1 版本格式

版本号格式为：`主版本号.次版本号.修订号`（例如：1.2.3）

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 2.7.2 版本范围

Yarn支持多种版本范围表达式：

| 范围表达式 | 含义 | 示例 |
|-----------|------|------|
| `^1.2.3` | 兼容版本，允许次版本和修订版本更新 | ^1.2.3 允许 >=1.2.3 <2.0.0 |
| `~1.2.3` | 允许修订版本更新 | ~1.2.3 允许 >=1.2.3 <1.3.0 |
| `*` | 匹配任何版本 | * 匹配任何版本 |
| `1.x` | 通配符，匹配次版本 | 1.x 匹配 >=1.0.0 <2.0.0 |
| `1.2.*` | 通配符，匹配修订版本 | 1.2.* 匹配 >=1.2.0 <1.3.0 |
| `>=1.2.3` | 大于等于指定版本 | >=1.2.3 允许 >=1.2.3 |
| `<=1.2.3` | 小于等于指定版本 | <=1.2.3 允许 <=1.2.3 |
| `>=1.2.3 <2.0.0` | 版本范围 | 允许 >=1.2.3 <2.0.0 |
| `1.2.3 - 2.3.4` | 包含范围的版本 | 允许 >=1.2.3 <=2.3.4 |
| `||` | 或 | `^2.0.0 || ^3.0.0` 允任选其一 |

### 2.7.3 版本锁定

Yarn使用`yarn.lock`文件锁定依赖的确切版本，确保不同环境中安装的依赖版本一致。

#### yarn.lock示例

```lockfile
# THIS IS AN AUTOGENERATED FILE. DO NOT EDIT THIS FILE DIRECTLY.
# yarn lockfile v1

lodash@^4.17.21:
  version "4.17.21"
  resolved "https://registry.yarnpkg.com/lodash/-/lodash-4.17.21.tgz#679591c564c3bffaae8454cf0b3df370c3d6911f"
  integrity sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg==

react@^18.2.0:
  version "18.2.0"
  resolved "https://registry.yarnpkg.com/react/-/react-18.2.0.tgz#2e8a2ad3a58473a3b75692366e487cb6fe99e8a"
  integrity sha512-/3IjMdb2L9QbBd9WEGt/x9MvKWLAFdu69t+vwi8I2McMWidZYIIpcg9hRrrihy1sYQklxLBAAPI1qgkygKXOw==
  dependencies:
    loose-envify "^1.1.0"
    object-assign "^4.1.1"
```

## 2.8 高级包管理技巧

### 2.8.1 选择性安装

```bash
# 只安装生产依赖
yarn install --production

# 只安装开发依赖
yarn install --dev

# 强制重新安装
yarn install --force
```

### 2.8.2 离线安装

```bash
# 离线模式（只从缓存安装）
yarn install --offline

# 如果缓存中没有，则从网络下载
yarn install --prefer-offline

# 如果缓存中没有，则跳过该依赖
yarn install --frozen-lockfile
```

### 2.8.3 解决依赖冲突

当依赖冲突发生时，可以采取以下策略：

1. **使用resolutions字段强制解析**

在`package.json`中添加`resolutions`字段：

```json
{
  "dependencies": {
    "package-a": "^1.0.0",
    "package-b": "^2.0.0"
  },
  "resolutions": {
    "package-c": "^1.2.3"
  }
}
```

2. **使用npm别名安装不同版本**

```bash
# 安装不同版本
yarn add react@17.0.2
yarn add react@18.2.0 --alias react18

# 在代码中使用
import React from 'react';
import React18 from 'react18';
```

3. **检查依赖树**

```bash
# 检查为什么安装了某个依赖
yarn why react

# 检查依赖关系
yarn info react@17.0.2 --json
```

## 2.9 实用技巧与最佳实践

### 2.9.1 命令简写

| 完整命令 | 简写 | 功能 |
|---------|------|------|
| yarn install | yarn | 安装依赖 |
| yarn add package | yarn add package | 添加依赖 |
| yarn remove package | yarn remove package | 移除依赖 |
| yarn upgrade package | yarn upgrade package | 更新依赖 |
| yarn run script | yarn script | 运行脚本 |

### 2.9.2 安全实践

1. **定期更新依赖**
   ```bash
   # 检查过时依赖
   yarn outdated
   ```

2. **审计安全漏洞**
   ```bash
   # 审计依赖的安全漏洞
   yarn audit
   ```

3. **使用精确版本**
   ```bash
   # 安装精确版本
   yarn add lodash --exact
   ```

### 2.9.3 性能优化

1. **使用缓存**
   ```bash
   # 启用缓存（默认启用）
   yarn config set cache-folder ./yarn-cache
   ```

2. **并行安装**
   ```bash
   # 设置网络并发数（默认是50）
   yarn config set maxsockets 100
   ```

3. **使用镜像源**
   ```bash
   # 使用国内镜像
   yarn config set registry https://registry.npm.taobao.org
   ```

### 2.9.4 团队协作

1. **提交yarn.lock**
   - 确保`yarn.lock`文件被提交到版本控制系统
   - 这保证所有团队成员使用相同的依赖版本

2. **使用.npmrc或.yarnrc**
   - 创建统一的配置文件
   - 确保团队成员使用相同的registry和其他设置

3. **文档化依赖决策**
   - 在README或文档中记录重要的依赖选择
   - 说明某些依赖的特殊版本要求

## 2.10 实践练习

### 练习1：创建和管理一个项目

1. 创建一个新项目：
   ```bash
   mkdir my-yarn-project
   cd my-yarn-project
   yarn init -y
   ```

2. 添加生产依赖：
   ```bash
   yarn add express
   yarn add lodash moment
   ```

3. 添加开发依赖：
   ```bash
   yarn add nodemon --dev
   yarn add jest --dev
   ```

4. 更新依赖：
   ```bash
   yarn upgrade express
   ```

5. 检查过时依赖：
   ```bash
   yarn outdated
   ```

### 练习2：管理项目依赖

1. 创建一个package.json文件，包含以下内容：
   ```json
   {
     "name": "dependency-practice",
     "version": "1.0.0",
     "description": "Yarn依赖管理练习",
     "main": "index.js",
     "scripts": {
       "start": "node index.js",
       "dev": "nodemon index.js",
       "test": "jest"
     },
     "dependencies": {
       "axios": "^0.26.0"
     },
     "devDependencies": {
       "jest": "^27.5.1",
       "nodemon": "^2.0.15"
     }
   }
   ```

2. 安装依赖并创建一个简单的应用程序

3. 尝试使用本章学习的命令管理这个项目的依赖

## 2.11 总结

本章详细介绍了Yarn的基础命令和包管理功能，包括项目初始化、依赖管理、版本控制、信息查询等核心操作。掌握这些基础知识是有效使用Yarn进行项目依赖管理的关键。

关键要点：
- `yarn init`用于创建新项目并生成package.json
- `yarn add/remove/upgrade`用于管理依赖
- `yarn.lock`文件确保依赖版本的一致性
- Yarn提供了丰富的信息查询命令
- 语义化版本控制有助于管理依赖版本
- 缓存机制可以显著提高安装速度
- 适当使用高级功能可以提高开发效率

下一章将深入探讨Yarn的工作空间和依赖管理高级特性，帮助您在更复杂的项目中有效使用Yarn。