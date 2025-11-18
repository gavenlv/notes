# 第6章：NPM高级配置与优化

## 目录
1. [NPM配置文件详解](#npm配置文件详解)
2. [NPM缓存管理](#npm缓存管理)
3. [NPM镜像与代理配置](#npm镜像与代理配置)
4. [NPM性能优化](#npm性能优化)
5. [NPM工作区(Workspaces)](#npm工作区workspaces)
6. [NPM高级脚本技巧](#npm高级脚本技巧)
7. [NPM私有仓库配置](#npm私有仓库配置)
8. [NPM与CI/CD集成](#npm与cicd集成)
9. [实践练习](#实践练习)
10. [常见问题与解决方案](#常见问题与解决方案)

## NPM配置文件详解

### .npmrc配置文件

NPM使用`.npmrc`文件来存储配置设置，这些文件可以存在于多个位置，具有不同的优先级：

1. **全局配置文件**：`$PREFIX/etc/npmrc` (Windows上通常是`C:\Program Files\nodejs\node_modules\npm\npmrc`)
2. **用户级配置文件**：`~/.npmrc` (Windows上通常是`C:\Users\[用户名]\.npmrc`)
3. **项目级配置文件**：`.npmrc` (项目根目录)
4. **环境变量**：以`NPM_CONFIG_`开头的环境变量

配置的优先级从高到低为：命令行参数 > 项目级配置 > 用户级配置 > 全局配置 > 环境变量

### 常用配置项

```bash
# 设置默认作者
npm config set init-author-name "Your Name"
npm config set init-author-email "your.email@example.com"
npm config set init-author-url "https://yourwebsite.com"

# 设置默认许可证
npm config set init-license "MIT"

# 设置默认仓库
npm config set registry "https://registry.npmjs.org/"

# 设置代理
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080

# 设置CA证书
npm config set ca /path/to/cert.pem

# 设置日志级别
npm config set loglevel "warn"

# 设置保存前缀（--save或--save-dev）
npm config set save-prefix "^"

# 设置是否精确安装版本
npm config set save-exact false

# 设置包安装位置
npm config set prefix "C:\\Program Files\\nodejs"

# 设置缓存目录
npm config set cache "C:\\Users\\[用户名]\\AppData\\Roaming\\npm-cache"
```

### 查看和修改配置

```bash
# 查看所有配置
npm config list

# 查看特定配置
npm config get registry

# 设置配置
npm config set registry https://registry.npm.taobao.org/

# 删除配置
npm config delete registry

# 编辑配置文件
npm config edit
```

## NPM缓存管理

### 缓存机制

NPM使用缓存来加速包的安装过程。当您安装一个包时，NPM会将其下载并存储在缓存目录中。下次需要相同版本的包时，NPM会直接从缓存中获取，而不必重新下载。

### 查看缓存信息

```bash
# 查看缓存目录
npm config get cache

# 查看缓存内容
npm cache verify

# 查看缓存统计信息
npm cache ls
```

### 清理缓存

```bash
# 清理缓存
npm cache clean --force

# 验证缓存完整性
npm cache verify
```

### 缓存优化

```bash
# 设置缓存大小限制（以字节为单位）
npm config set cache-max 1073741824  # 1GB

# 设置缓存最小保留时间（以秒为单位）
npm config set cache-min 3600  # 1小时

# 禁用缓存（不推荐）
npm config set cache false
```

## NPM镜像与代理配置

### 使用国内镜像

```bash
# 临时使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 永久设置淘宝镜像
npm config set registry https://registry.npmmirror.com

# 恢复官方镜像
npm config set registry https://registry.npmjs.org/
```

### 使用nrm管理镜像源

nrm是一个NPM镜像源管理工具，可以帮助您快速切换不同的镜像源：

```bash
# 安装nrm
npm install -g nrm

# 查看所有镜像源
nrm ls

# 添加自定义镜像源
nrm add company http://npm.company.com/

# 切换镜像源
nrm use taobao

# 测试镜像源速度
nrm test

# 查看当前使用的镜像源
nrm current
```

### 代理配置

```bash
# 设置HTTP代理
npm config set proxy http://proxy.company.com:8080

# 设置HTTPS代理
npm config set https-proxy http://proxy.company.com:8080

# 设置不使用代理的域名
npm config set noproxy "localhost,127.0.0.1,.company.com"

# 删除代理设置
npm config delete proxy
npm config delete https-proxy
npm config delete noproxy
```

## NPM性能优化

### 并行安装

NPM 6及更高版本支持并行安装包，可以显著提高安装速度：

```bash
# 设置最大并行下载数（默认为3）
npm config set maxsockets 5

# 设置最大并行安装数（默认为5）
npm config set workers 5
```

### 离线安装

```bash
# 打包依赖
npm pack

# 离线安装
npm install ./package-name-version.tgz
```

### 使用yarn替代npm

yarn是Facebook开发的包管理器，具有更快的安装速度和更好的依赖管理：

```bash
# 安装yarn
npm install -g yarn

# 安装依赖
yarn install

# 添加依赖
yarn add [package-name]

# 运行脚本
yarn run [script-name]
```

### 使用pnpm替代npm

pnpm是高效的包管理器，通过硬链接和符号链接节省磁盘空间：

```bash
# 安装pnpm
npm install -g pnpm

# 安装依赖
pnpm install

# 添加依赖
pnpm add [package-name]

# 运行脚本
pnpm run [script-name]
```

## NPM工作区(Workspaces)

### 工作区概述

NPM工作区允许您在单个仓库中管理多个相关的包，这对于开发monorepo项目非常有用。

### 配置工作区

在根目录的`package.json`中添加工作区配置：

```json
{
  "name": "my-monorepo",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "install:all": "npm install --workspaces",
    "test": "npm run test --workspaces",
    "build": "npm run build --workspaces"
  }
}
```

### 工作区常用命令

```bash
# 安装所有工作区的依赖
npm install

# 在特定工作区中安装依赖
npm install lodash --workspace=packages/utils

# 在所有工作区中安装依赖
npm install lodash --workspaces

# 运行特定工作区的脚本
npm run test --workspace=packages/utils

# 运行所有工作区的脚本
npm run test --workspaces

# 列出所有工作区
npm ls --workspaces

# 在特定工作区中运行命令
npm run build --workspace=packages/utils
```

### 工作区实践

假设有以下项目结构：

```
my-monorepo/
├── package.json
├── packages/
│   ├── utils/
│   │   ├── package.json
│   │   └── index.js
│   └── app/
│       ├── package.json
│       └── index.js
```

根目录`package.json`：

```json
{
  "name": "my-monorepo",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "install:all": "npm install --workspaces",
    "test": "npm run test --workspaces",
    "build": "npm run build --workspaces",
    "dev": "npm run dev --workspace=packages/app"
  }
}
```

`packages/utils/package.json`：

```json
{
  "name": "@my-monorepo/utils",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "test": "echo 'Testing utils'"
  }
}
```

`packages/app/package.json`：

```json
{
  "name": "@my-monorepo/app",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "@my-monorepo/utils": "^1.0.0"
  },
  "scripts": {
    "test": "echo 'Testing app'",
    "dev": "echo 'Starting app in dev mode'"
  }
}
```

## NPM高级脚本技巧

### 条件执行

使用`&&`和`||`实现条件执行：

```json
{
  "scripts": {
    "build": "npm run clean && npm run compile",
    "test": "npm run lint || echo 'Linting failed but continuing'",
    "deploy": "npm run test && npm run build && npm run upload"
  }
}
```

### 并行执行

使用`&`和`concurrently`实现并行执行：

```json
{
  "scripts": {
    "dev": "concurrently \"npm run watch:css\" \"npm run watch:js\"",
    "start": "npm run serve & npm run watch",
    "test:parallel": "npm run test:unit & npm run test:integration"
  },
  "devDependencies": {
    "concurrently": "^7.0.0"
  }
}
```

### 环境变量

在脚本中使用环境变量：

```json
{
  "scripts": {
    "dev": "NODE_ENV=development npm run start",
    "prod": "NODE_ENV=production npm run start",
    "test": "NODE_ENV=test npm run jest",
    "build:dev": "NODE_ENV=development webpack --mode=development",
    "build:prod": "NODE_ENV=production webpack --mode=production"
  }
}
```

### 跨平台脚本

使用`cross-env`实现跨平台环境变量设置：

```json
{
  "scripts": {
    "build": "cross-env NODE_ENV=production webpack --mode=production",
    "start": "cross-env PORT=3000 node server.js"
  },
  "devDependencies": {
    "cross-env": "^7.0.3"
  }
}
```

### 参数传递

向脚本传递参数：

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:single": "jest --testNamePattern",
    "build": "webpack",
    "build:analyze": "webpack --analyze"
  }
}
```

使用方式：
```bash
npm run test:single -- "should return true"
npm run build:analyze
```

### 预提交钩子

使用`husky`和`lint-staged`设置预提交钩子：

```json
{
  "scripts": {
    "prepare": "husky install",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "format": "prettier --write ."
  },
  "devDependencies": {
    "husky": "^7.0.0",
    "lint-staged": "^12.0.0",
    "eslint": "^8.0.0",
    "prettier": "^2.0.0"
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

## NPM私有仓库配置

### 使用Verdaccio搭建私有仓库

Verdaccio是一个简单的轻量级私有NPM代理注册表：

```bash
# 安装Verdaccio
npm install -g verdaccio

# 启动Verdaccio
verdaccio

# 配置Verdaccio（默认配置文件位置：~/.config/verdaccio/config.yaml）
```

### 配置私有仓库

在`.npmrc`中配置私有仓库：

```bash
# 设置私有仓库
npm config set registry http://localhost:4873/

# 登录私有仓库
npm login --registry=http://localhost:4873

# 发布到私有仓库
npm publish --registry=http://localhost:4873
```

### 使用.npmrc文件管理多个仓库

在项目根目录创建`.npmrc`文件：

```
# 私有包使用私有仓库
@mycompany:registry=http://npm.mycompany.com/

# 其他包使用公共仓库
registry=https://registry.npmjs.org/
```

### 配置作用域包

```bash
# 安装作用域包
npm install @mycompany/mypackage

# 发布作用域包
npm publish --access public  # 公开包
npm publish --access restricted  # 私有包（需要付费账户）
```

## NPM与CI/CD集成

### GitHub Actions示例

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [14.x, 16.x, 18.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build project
      run: npm run build
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'
        registry-url: 'https://registry.npmjs.org'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build project
      run: npm run build
    
    - name: Publish to NPM
      run: npm publish
      env:
        NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Jenkins Pipeline示例

```groovy
pipeline {
    agent any
    
    tools {
        nodejs 'NodeJS-18'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'coverage',
                        reportFiles: 'lcov-report/index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Publish') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([string(credentialsId: 'npm-token', variable: 'NPM_TOKEN')]) {
                    sh 'npm publish'
                }
            }
        }
    }
}
```

### 使用.npmrc管理CI/CD中的配置

在CI/CD环境中使用项目级`.npmrc`文件：

```
# .npmrc
@mycompany:registry=https://npm.mycompany.com/
//npm.mycompany.com/:_authToken=${NPM_TOKEN}
```

在CI/CD中设置环境变量：
```bash
export NPM_TOKEN=your-token-here
```

## 实践练习

### 练习1：配置NPM镜像源

1. 查看当前使用的NPM镜像源
2. 切换到淘宝镜像源
3. 安装一个包，观察安装速度
4. 切换回官方镜像源

### 练习2：管理NPM缓存

1. 查看当前缓存目录和大小
2. 清理NPM缓存
3. 重新安装一个包，观察缓存重建过程
4. 设置缓存大小限制

### 练习3：设置NPM工作区

1. 创建一个monorepo项目结构
2. 配置工作区
3. 在工作区中安装依赖
4. 在工作区之间共享代码

### 练习4：配置私有仓库

1. 使用Verdaccio搭建本地私有仓库
2. 发布一个包到私有仓库
3. 从私有仓库安装包
4. 配置作用域包

### 练习5：配置CI/CD

1. 创建一个GitHub Actions工作流
2. 配置自动化测试
3. 配置自动化发布
4. 测试整个CI/CD流程

## 常见问题与解决方案

### 问题1：NPM安装速度慢

**解决方案：**
1. 切换到国内镜像源
2. 使用yarn或pnpm替代npm
3. 配置代理
4. 清理缓存

```bash
# 切换到淘宝镜像
npm config set registry https://registry.npmmirror.com

# 使用yarn
npm install -g yarn
yarn install

# 配置代理
npm config set proxy http://proxy.company.com:8080

# 清理缓存
npm cache clean --force
```

### 问题2：NPM安装依赖失败

**解决方案：**
1. 检查网络连接
2. 清理缓存
3. 删除node_modules和package-lock.json
4. 使用npm ci替代npm install

```bash
# 清理缓存
npm cache clean --force

# 删除node_modules和package-lock.json
rm -rf node_modules package-lock.json

# 使用npm ci
npm ci
```

### 问题3：NPM权限问题

**解决方案：**
1. 使用nvm管理Node.js版本
2. 修改NPM全局目录
3. 使用sudo（Linux/macOS）

```bash
# 使用nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install node

# 修改NPM全局目录
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 问题4：NPM脚本跨平台问题

**解决方案：**
1. 使用cross-env处理环境变量
2. 使用rimraf替代rm -rf
3. 使用concurrently处理并行执行

```json
{
  "scripts": {
    "clean": "rimraf dist",
    "build": "cross-env NODE_ENV=production webpack",
    "dev": "concurrently \"npm run watch:css\" \"npm run watch:js\""
  },
  "devDependencies": {
    "cross-env": "^7.0.3",
    "rimraf": "^3.0.2",
    "concurrently": "^7.0.0"
  }
}
```

### 问题5：私有仓库认证问题

**解决方案：**
1. 使用.npmrc文件存储认证信息
2. 使用环境变量存储token
3. 配置作用域包

```
# .npmrc
@mycompany:registry=https://npm.mycompany.com/
//npm.mycompany.com/:_authToken=${NPM_TOKEN}
```

```bash
# 设置环境变量
export NPM_TOKEN=your-token-here
```

## 总结

本章深入探讨了NPM的高级配置与优化技术，包括：

1. **NPM配置文件详解**：了解了不同级别的配置文件及其优先级
2. **NPM缓存管理**：学习了如何管理和优化NPM缓存
3. **NPM镜像与代理配置**：掌握了如何配置镜像源和代理
4. **NPM性能优化**：探索了提高NPM性能的各种方法
5. **NPM工作区**：学习了如何使用工作区管理monorepo项目
6. **NPM高级脚本技巧**：掌握了编写复杂脚本的技巧
7. **NPM私有仓库配置**：了解了如何搭建和配置私有仓库
8. **NPM与CI/CD集成**：学习了如何在CI/CD流程中使用NPM

通过这些高级配置和优化技术，您可以更高效地使用NPM，提高开发效率，并解决实际项目中的复杂问题。在下一章中，我们将探讨NPM的安全性和最佳实践。