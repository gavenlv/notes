# 第1章：NPM基础入门与环境搭建

## 1.1 NPM简介与历史

### 什么是NPM？

NPM（Node Package Manager）是Node.js的默认包管理器，也是世界上最大的软件注册表。它允许开发者发现、共享和使用代码包，以及管理项目依赖关系。

### NPM的历史

- **2010年**：NPM由Isaac Z. Schlueter创建，旨在解决Node.js模块管理问题
- **2011年**：NPM 1.0发布，成为Node.js的默认包管理器
- **2014年**：NPM公司成立，开始商业化运营
- **2016年**：NPM注册表中的包数量突破20万
- **2020年**：微软收购NPM，确保开源生态系统的可持续发展
- **现在**：NPM注册表包含超过200万个包，每周下载量超过数十亿次

### NPM的重要性

NPM在现代JavaScript开发中扮演着至关重要的角色：

1. **依赖管理**：自动处理项目依赖关系和版本冲突
2. **代码共享**：促进代码重用和社区协作
3. **生态系统**：构建了庞大的JavaScript生态系统
4. **自动化**：提供脚本执行和自动化工具
5. **标准化**：建立了JavaScript项目的标准结构

## 1.2 Node.js与NPM的关系

### Node.js简介

Node.js是一个基于Chrome V8引擎的JavaScript运行时环境，它使JavaScript可以在服务器端运行。Node.js的设计理念是：

- 非阻塞I/O模型
- 事件驱动架构
- 单线程但高并发

### NPM与Node.js的关系

1. **捆绑安装**：NPM随Node.js一起安装，无需单独安装
2. **默认包管理器**：NPM是Node.js的官方包管理器
3. **生态系统基础**：NPM是Node.js生态系统的核心组成部分
4. **互操作性**：NPM包可以在Node.js环境中无缝使用

### Node.js版本与NPM版本兼容性

| Node.js版本 | 推荐NPM版本 | 发布时间 |
|------------|------------|---------|
| Node.js 16.x | NPM 8.x | 2021年 |
| Node.js 17.x | NPM 8.x | 2021年 |
| Node.js 18.x | NPM 8.x | 2022年 |
| Node.js 19.x | NPM 9.x | 2022年 |
| Node.js 20.x | NPM 10.x | 2023年 |

## 1.3 NPM安装与配置

### 安装Node.js（包含NPM）

#### Windows系统

1. 访问 [Node.js官网](https://nodejs.org/)
2. 下载LTS（长期支持）版本的Windows安装程序
3. 运行安装程序，按照向导完成安装
4. 验证安装：

```bash
node -v
npm -v
```

#### macOS系统

1. 使用Homebrew安装：

```bash
brew install node
```

2. 或者从官网下载macOS安装程序

3. 验证安装：

```bash
node -v
npm -v
```

#### Linux系统

使用包管理器安装：

**Ubuntu/Debian:**

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**CentOS/RHEL/Fedora:**

```bash
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo yum install -y nodejs
```

### 使用Node版本管理器

#### nvm（Node Version Manager）

nvm允许在同一台机器上安装和管理多个Node.js版本：

1. 安装nvm：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

2. 重新加载终端配置：

```bash
source ~/.bashrc
```

3. 安装和使用Node.js：

```bash
nvm install 18.17.0  # 安装特定版本
nvm use 18.17.0     # 使用特定版本
nvm ls              # 列出已安装的版本
nvm alias default 18.17.0  # 设置默认版本
```

### NPM基本配置

#### 查看当前配置

```bash
npm config list
```

#### 设置配置项

```bash
npm config set key value
```

#### 常用配置项

1. **设置默认初始化值**：

```bash
npm config set init-author-name "Your Name"
npm config set init-author-email "your.email@example.com"
npm config set init-author-url "https://yourwebsite.com"
npm config set init-license "MIT"
npm config set init-version "1.0.0"
```

2. **设置全局安装目录**：

```bash
npm config set prefix "C:\Program Files\nodejs\npm-global"  # Windows
npm config set prefix "~/.npm-global"  # macOS/Linux
```

3. **设置缓存目录**：

```bash
npm config set cache "D:\npm-cache"  # Windows
npm config set cache "~/.npm-cache"  # macOS/Linux
```

#### 配置文件位置

- **全局配置文件**：
  - Windows: `C:\Users\[用户名]\.npmrc`
  - macOS/Linux: `~/.npmrc`

- **项目级配置文件**：项目根目录下的 `.npmrc`

## 1.4 基本命令介绍

### 查看NPM版本

```bash
npm -v
npm --version
```

### 查看NPM帮助

```bash
npm help
npm <command> --help  # 查看特定命令的帮助
```

### 初始化项目

```bash
npm init          # 交互式初始化
npm init -y       # 使用默认值快速初始化
npm init --yes    # 同上
```

### 安装包

```bash
# 安装最新版本
npm install <package>
npm i <package>

# 安装特定版本
npm install <package>@<version>

# 安装作为开发依赖
npm install <package> --save-dev
npm install <package> -D

# 安装作为全局包
npm install <package> --global
npm install <package> -g
```

### 查看已安装的包

```bash
npm list              # 查看本地包
npm list -g           # 查看全局包
npm list --depth=0    # 只显示顶级依赖
```

### 卸载包

```bash
npm uninstall <package>
npm un <package>
npm remove <package>
```

### 更新包

```bash
npm update            # 更新所有包
npm update <package>  # 更新特定包
```

### 搜索包

```bash
npm search <keyword>
npm s <keyword>
```

### 查看包信息

```bash
npm info <package>
npm view <package>
```

## 1.5 开发环境搭建

### 创建项目结构

一个标准的NPM项目结构如下：

```
my-project/
├── node_modules/     # 依赖包目录
├── src/              # 源代码目录
├── tests/            # 测试文件目录
├── docs/             # 文档目录
├── .gitignore        # Git忽略文件
├── .npmrc            # NPM配置文件
├── package.json      # 项目配置文件
└── README.md         # 项目说明文件
```

### 初始化项目

1. 创建项目目录：

```bash
mkdir my-project
cd my-project
```

2. 初始化NPM项目：

```bash
npm init -y
```

3. 创建基本目录结构：

```bash
mkdir src tests docs
```

4. 创建 `.gitignore` 文件：

```gitignore
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
```

### 配置开发环境

#### 安装常用开发依赖

```bash
# 代码格式化工具
npm install -D prettier

# 代码检查工具
npm install -D eslint

# 测试框架
npm install -D jest

# 构建工具
npm install -D webpack webpack-cli

# 开发服务器
npm install -D webpack-dev-server

# CSS预处理器
npm install -D sass

# TypeScript支持
npm install -D typescript @types/node
```

#### 配置package.json脚本

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "A sample project",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "webpack serve --mode development",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src/**/*.js",
    "format": "prettier --write src/**/*.js"
  },
  "keywords": [
    "node",
    "npm",
    "javascript"
  ],
  "author": "Your Name",
  "license": "MIT",
  "devDependencies": {
    "eslint": "^8.45.0",
    "jest": "^29.6.1",
    "prettier": "^3.0.0",
    "typescript": "^5.1.6",
    "webpack": "^5.88.2",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1"
  }
}
```

### 设置开发工具

#### VS Code扩展推荐

1. **ESLint**：代码检查
2. **Prettier**：代码格式化
3. **Auto Rename Tag**：自动重命名配对标签
4. **Bracket Pair Colorizer**：括号配对着色
5. **GitLens**：Git增强
6. **DotENV**：环境变量支持
7. **Path Intellisense**：路径自动补全
8. **npm Intellisense**：npm模块自动补全

#### VS Code工作区设置

创建 `.vscode/settings.json`：

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  },
  "files.associations": {
    "*.js": "javascriptreact"
  }
}
```

## 1.6 实践练习

### 练习1：验证NPM安装

1. 打开终端或命令提示符
2. 运行以下命令验证NPM是否正确安装：

```bash
node -v
npm -v
npm config list
```

3. 记录你的Node.js和NPM版本号

### 练习2：创建第一个NPM项目

1. 创建一个名为`hello-npm`的目录
2. 进入该目录并初始化NPM项目
3. 安装`lodash`包
4. 创建一个简单的JavaScript文件，使用lodash的功能
5. 运行该文件

**步骤：**

```bash
mkdir hello-npm
cd hello-npm
npm init -y
npm install lodash
```

创建`index.js`文件：

```javascript
const _ = require('lodash');

const numbers = [1, 2, 3, 4, 5];
const shuffled = _.shuffle(numbers);

console.log('Original array:', numbers);
console.log('Shuffled array:', shuffled);
```

运行文件：

```bash
node index.js
```

### 练习3：探索NPM命令

1. 使用`npm search`搜索你感兴趣的包
2. 使用`npm info`查看某个包的详细信息
3. 使用`npm view`查看包的特定字段信息
4. 使用`npm ls`查看当前项目的依赖树

## 1.7 常见问题与解决方案

### 问题1：NPM安装速度慢

**解决方案：**

1. 使用国内镜像源：

```bash
npm config set registry https://registry.npmmirror.com
```

2. 使用cnpm：

```bash
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install <package>
```

3. 使用yarn（替代包管理器）：

```bash
npm install -g yarn
yarn install
```

### 问题2：权限错误（Linux/macOS）

**解决方案：**

1. 使用nvm管理Node.js版本（推荐）
2. 修改npm全局目录权限：

```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 问题3：node-gyp编译错误

**解决方案：**

1. 安装编译工具：

**Windows:**

```bash
npm install -g windows-build-tools
```

**macOS:**

```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install build-essential
```

### 问题4：依赖冲突

**解决方案：**

1. 删除`node_modules`和`package-lock.json`
2. 清除NPM缓存：

```bash
npm cache clean --force
```

3. 重新安装依赖：

```bash
npm install
```

## 1.8 总结

本章介绍了NPM的基础知识和环境搭建，包括：

1. NPM的定义、历史和重要性
2. Node.js与NPM的关系
3. NPM的安装和配置方法
4. 基本命令的使用
5. 开发环境的搭建
6. 常见问题的解决方案

通过本章的学习，你应该能够：

- 理解NPM在JavaScript生态系统中的角色
- 成功安装和配置NPM环境
- 使用基本的NPM命令
- 创建和管理NPM项目
- 解决常见的NPM安装和配置问题

在下一章中，我们将深入学习NPM的包管理和基本命令，包括包的安装、更新、卸载等操作。