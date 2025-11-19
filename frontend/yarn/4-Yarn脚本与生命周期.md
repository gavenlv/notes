# 第4章：Yarn脚本与生命周期

## 概述

本章将详细介绍Yarn的脚本系统和生命周期管理，包括如何定义和执行脚本、如何利用生命周期钩子自动化构建流程、以及如何组织复杂的脚本任务。通过本章学习，您将掌握如何使用Yarn脚本提高开发效率，实现项目构建、测试和部署的自动化。

## 4.1 脚本系统基础

### 4.1.1 什么是Yarn脚本？

Yarn脚本是定义在`package.json`的`scripts`字段中的命令，它们允许您将常用的命令行操作封装为简短、易记的命令。这些脚本可以用于启动开发服务器、运行测试、构建项目等各种任务。

### 4.1.2 脚本的优势

1. **命令简化**：将复杂的命令简化为简短的名称
2. **跨平台兼容**：解决Windows和Unix系统之间的命令差异
3. **环境一致性**：确保团队成员使用相同的命令
4. **文档化**：通过脚本名称传达其用途
5. **流程自动化**：实现多步骤任务的自动化

### 4.1.3 脚本类型

| 类型 | 描述 | 示例 |
|------|------|------|
| 启动脚本 | 用于启动应用程序或开发服务器 | `start`, `dev` |
| 构建脚本 | 用于构建或打包应用程序 | `build`, `compile` |
| 测试脚本 | 用于运行测试 | `test`, `test:watch` |
| 代码质量脚本 | 用于检查代码质量 | `lint`, `format` |
| 部署脚本 | 用于部署应用程序 | `deploy`, `publish` |
| 工具脚本 | 用于辅助开发任务 | `clean`, `setup` |

## 4.2 定义脚本

### 4.2.1 基本脚本定义

在`package.json`中定义脚本的基本语法：

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src/**/*.js"
  }
}
```

### 4.2.2 复杂脚本定义

#### 使用参数的脚本

```json
{
  "scripts": {
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "build:analyze": "webpack-bundle-analyzer dist/bundle.js"
  }
}
```

#### 串行执行的脚本

```json
{
  "scripts": {
    "build-and-test": "npm run build && npm run test",
    "clean-and-build": "rimraf dist && npm run build"
  }
}
```

#### 并行执行的脚本

```json
{
  "scripts": {
    "start:all": "concurrently \"npm run server\" \"npm run client\"",
    "test:all": "concurrently \"npm run test:unit\" \"npm run test:integration\""
  }
}
```

#### 条件执行的脚本

```json
{
  "scripts": {
    "deploy": "if [ \"$NODE_ENV\" = \"production\" ]; then npm run build:prod; else npm run build:dev; fi"
  }
}
```

### 4.2.3 跨平台脚本

#### 使用cross-env

```json
{
  "scripts": {
    "build": "cross-env NODE_ENV=production webpack",
    "start": "cross-env PORT=3000 node src/index.js"
  }
}
```

#### 使用rimraf

```json
{
  "scripts": {
    "clean": "rimraf dist/*",
    "reset": "rimraf node_modules dist/* && npm install"
  }
}
```

## 4.3 运行脚本

### 4.3.1 基本运行方式

```bash
# 运行特定脚本
yarn run start

# 简写形式（不包含特殊字符）
yarn start

# 运行带参数的脚本
yarn run build --env production

# 运行不存在的脚本（查找全局命令）
yarn run nodemon
```

### 4.3.2 在工作空间中运行脚本

```bash
# 在特定工作空间运行脚本
yarn workspace @my-monorepo/app start

# 在所有工作空间运行同名脚本
yarn workspaces run test

# 按模式在工作空间运行脚本
yarn workspaces run build --pattern "@my-monorepo/*"
```

### 4.3.3 传递参数

```bash
# 直接传递参数
yarn test --coverage

# 使用--分隔符
yarn build -- --config webpack.prod.js

# 环境变量
NODE_ENV=production yarn build
```

## 4.4 生命周期脚本

### 4.4.1 生命周期钩子

Yarn提供了一系列生命周期脚本，它们在特定操作前后自动运行：

| 脚本名称 | 触发时机 | 描述 |
|---------|---------|------|
| `preinstall` | 安装依赖前 | 在执行`yarn install`前运行 |
| `install` | 安装依赖后 | 在执行`yarn install`后运行 |
| `postinstall` | 安装依赖后 | 在执行`yarn install`后运行 |
| `prepublish` | 发布前 | 在执行`yarn publish`前运行 |
| `prepublishOnly` | 发布前 | 仅在`yarn publish`前运行 |
| `prepack` | 打包前 | 在打包tarball前运行 |
| `postpack` | 打包后 | 在打包tarball后运行 |
| `publish` | 发布后 | 在执行`yarn publish`后运行 |
| `preversion` | 版本更新前 | 在更新版本号前运行 |
| `version` | 版本更新后 | 在更新版本号后运行 |
| `postversion` | 版本更新后 | 在更新版本号后运行 |

### 4.4.2 生命周期脚本示例

```json
{
  "scripts": {
    "preinstall": "echo '即将安装依赖...' && node check-node-version.js",
    "postinstall": "echo '依赖安装完成' && npm run build",
    "prepublishOnly": "npm run test && npm run build",
    "preversion": "npm run test",
    "version": "npm run build && git add -A dist",
    "postversion": "git push && git push --tags"
  }
}
```

### 4.4.3 install生命周期详解

`install`生命周期是最常用的，它包含三个阶段：

1. **preinstall**：安装依赖前
2. **install**：安装依赖后
3. **postinstall**：安装依赖后

```json
{
  "scripts": {
    "preinstall": "node scripts/check-platform.js",
    "postinstall": "opencollective postinstall"
  }
}
```

## 4.5 常用脚本模式

### 4.5.1 开发服务器模式

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "dev:debug": "nodemon --inspect server.js"
  }
}
```

### 4.5.2 构建模式

```json
{
  "scripts": {
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "build:watch": "webpack --mode development --watch",
    "build:analyze": "webpack-bundle-analyzer dist/bundle.js"
  }
}
```

### 4.5.3 测试模式

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:debug": "node --inspect-brk node_modules/.bin/jest --runInBand"
  }
}
```

### 4.5.4 代码质量模式

```json
{
  "scripts": {
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.{js,jsx,ts,tsx,json,css,md}",
    "type-check": "tsc --noEmit"
  }
}
```

### 4.5.5 部署模式

```json
{
  "scripts": {
    "build:prod": "npm run build && npm run test",
    "deploy:staging": "npm run build:prod && scp -r dist/* user@staging:/var/www",
    "deploy:prod": "npm run build:prod && scp -r dist/* user@production:/var/www"
  }
}
```

## 4.6 脚本组织策略

### 4.6.1 按功能组织

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src/**/*.js"
  }
}
```

### 4.6.2 使用命名空间

```json
{
  "scripts": {
    "app:start": "node server.js",
    "app:dev": "nodemon server.js",
    "build:prod": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "lint:check": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix"
  }
}
```

### 4.6.3 使用脚本文件

对于复杂的脚本，可以将其放在单独的文件中：

```json
{
  "scripts": {
    "build": "node scripts/build.js",
    "deploy": "node scripts/deploy.js",
    "setup": "node scripts/setup.js"
  }
}
```

## 4.7 脚本工具库

### 4.7.1 常用工具

| 工具 | 用途 | 安装命令 |
|------|------|---------|
| concurrently | 并行运行多个命令 | `yarn add concurrently --dev` |
| cross-env | 跨平台环境变量设置 | `yarn add cross-env --dev` |
| rimraf | 跨平台文件删除 | `yarn add rimraf --dev` |
| nodemon | 自动重启开发服务器 | `yarn add nodemon --dev` |
| chalk | 终端颜色输出 | `yarn add chalk --dev` |
| ora | 加载动画 | `yarn add ora --dev` |
| inquirer | 交互式命令行界面 | `yarn add inquirer --dev` |

### 4.7.2 示例脚本文件

#### scripts/build.js

```javascript
#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');

const spinner = ora('构建项目...').start();

try {
  // 清理构建目录
  spinner.text = '清理构建目录...';
  execSync('rimraf dist', { stdio: 'inherit' });
  
  // 运行TypeScript编译
  spinner.text = '编译TypeScript...';
  execSync('tsc', { stdio: 'inherit' });
  
  // 运行Webpack打包
  spinner.text = 'Webpack打包...';
  execSync('webpack --mode production', { stdio: 'inherit' });
  
  spinner.succeed(chalk.green('构建完成！'));
} catch (error) {
  spinner.fail(chalk.red('构建失败：' + error.message));
  process.exit(1);
}
```

#### scripts/deploy.js

```javascript
#!/usr/bin/env node

const inquirer = require('inquirer');
const { execSync } = require('child_process');
const chalk = require('chalk');

inquirer
  .prompt([
    {
      type: 'list',
      name: 'environment',
      message: '选择部署环境:',
      choices: ['staging', 'production']
    },
    {
      type: 'confirm',
      name: 'confirm',
      message: '确认部署？',
      default: false
    }
  ])
  .then((answers) => {
    if (!answers.confirm) {
      console.log(chalk.yellow('部署已取消'));
      return;
    }
    
    try {
      console.log(chalk.blue(`部署到 ${answers.environment} 环境...`));
      execSync(`yarn build && yarn deploy:${answers.environment}`, {
        stdio: 'inherit'
      });
      console.log(chalk.green('部署成功！'));
    } catch (error) {
      console.error(chalk.red('部署失败：' + error.message));
      process.exit(1);
    }
  });
```

## 4.8 高级技巧

### 4.8.1 动态脚本

使用Node.js脚本生成动态命令：

```json
{
  "scripts": {
    "start": "node scripts/start.js",
    "build": "node scripts/build.js"
  }
}
```

#### scripts/start.js

```javascript
#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 读取配置
const configPath = path.join(__dirname, '../config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 构建命令
const args = ['server.js'];
if (config.port) {
  args.push('--port', config.port);
}
if (config.debug) {
  args.push('--debug');
}

// 启动进程
const child = spawn('node', args, {
  stdio: 'inherit'
});

child.on('error', (error) => {
  console.error('启动失败:', error);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code);
});
```

### 4.8.2 条件脚本

根据条件执行不同的命令：

```json
{
  "scripts": {
    "test": "node scripts/test.js"
  }
}
```

#### scripts/test.js

```javascript
#!/usr/bin/env node

const { execSync } = require('child_process');

const testType = process.env.TEST_TYPE || 'unit';

switch (testType) {
  case 'unit':
    execSync('jest --testPathPattern=unit', { stdio: 'inherit' });
    break;
  case 'integration':
    execSync('jest --testPathPattern=integration', { stdio: 'inherit' });
    break;
  case 'e2e':
    execSync('cypress run', { stdio: 'inherit' });
    break;
  default:
    execSync('jest', { stdio: 'inherit' });
}
```

### 4.8.3 使用变量和环境

```json
{
  "scripts": {
    "start": "cross-env NODE_ENV=$NODE_ENV PORT=$PORT node server.js",
    "build": "cross-env NODE_ENV=production webpack --mode $NODE_ENV"
  }
}
```

## 4.9 调试和故障排除

### 4.9.1 常见问题

1. **脚本找不到**：检查脚本名称和路径是否正确
2. **权限问题**：确保脚本文件有执行权限（使用`chmod +x`）
3. **路径问题**：使用相对路径时注意当前工作目录
4. **环境变量**：使用cross-env确保跨平台兼容性

### 4.9.2 调试技巧

1. **查看详细输出**：在脚本后添加`--verbose`参数
2. **逐步执行**：将复杂脚本分解为多个简单脚本
3. **使用`npm run`**：查看所有可用脚本
4. **检查退出码**：确保脚本正确处理错误情况

## 4.10 实际应用案例

### 4.10.1 React应用项目

```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "lint": "eslint src/**/*.js",
    "format": "prettier --write src/**/*.{js,jsx}",
    "analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js",
    "storybook": "start-storybook -p 6006",
    "build-storybook": "build-storybook"
  }
}
```

### 4.10.2 Node.js API项目

```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon --inspect src/index.js",
    "build": "babel src -d dist",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "docs": "jsdoc -c jsdoc.conf.json src/**/*.js",
    "db:migrate": "node scripts/migrate.js",
    "db:seed": "node scripts/seed.js"
  }
}
```

### 4.10.3 全栈应用项目

```json
{
  "scripts": {
    "client:start": "yarn workspace client start",
    "server:start": "yarn workspace server dev",
    "start": "concurrently \"npm run server:start\" \"npm run client:start\"",
    "client:build": "yarn workspace client build",
    "server:build": "yarn workspace server build",
    "build": "npm run client:build && npm run server:build",
    "test:client": "yarn workspace client test",
    "test:server": "yarn workspace server test",
    "test": "npm run test:client && npm run test:server",
    "deploy": "npm run build && npm run server:deploy"
  }
}
```

## 4.11 实践练习

### 练习1：创建基本脚本

1. 创建一个新项目并添加基本脚本：
   ```json
   {
     "scripts": {
       "start": "node index.js",
       "dev": "nodemon index.js",
       "test": "jest",
       "build": "echo 'Building project...'",
       "lint": "eslint ."
     }
   }
   ```

2. 创建简单的index.js和测试文件
3. 尝试运行每个脚本

### 练习2：创建复杂脚本

1. 创建一个使用cross-env的脚本
2. 创建一个并行执行多个任务的脚本
3. 创建一个带条件逻辑的脚本文件

## 4.12 总结

本章详细介绍了Yarn的脚本系统和生命周期管理，包括如何定义和执行脚本、如何利用生命周期钩子自动化构建流程、以及如何组织复杂的脚本任务。通过合理使用脚本，可以显著提高开发效率，实现项目构建、测试和部署的自动化。

关键要点：
- 脚本是将常用命令封装为简短、易记命令的有效方式
- 生命周期钩子允许在特定操作前后自动执行任务
- 使用命名空间可以更好地组织大量脚本
- 复杂脚本可以放在单独的文件中，提高可维护性
- 跨平台工具（如cross-env、rimraf）可以解决平台差异问题
- 条件执行和并行执行可以创建更复杂的自动化流程

下一章将介绍Yarn的配置与优化，帮助您根据项目需求调整Yarn的行为，提高安装速度和开发效率。