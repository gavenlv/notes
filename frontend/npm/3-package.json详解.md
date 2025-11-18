# 第3章：package.json详解

## 3.1 package.json概述

### 3.1.1 什么是package.json

`package.json`是Node.js项目的核心配置文件，它定义了项目的基本信息、依赖关系、脚本命令等关键配置。每个Node.js项目都应该包含一个`package.json`文件，它是项目的"身份证"。

### 3.1.2 package.json的重要性

1. **项目标识**：定义项目的基本信息，如名称、版本、描述等
2. **依赖管理**：记录项目所需的依赖包及其版本
3. **脚本定义**：定义可执行的命令脚本
4. **项目配置**：包含项目的各种配置选项
5. **发布信息**：当发布到NPM时使用的元数据

### 3.1.3 package.json的生成

#### 使用npm init生成

```bash
# 交互式创建package.json
npm init

# 使用默认值创建package.json
npm init -y
# 或
npm init --yes
```

#### 自定义初始化

```bash
# 使用自定义配置
npm config set init-author-name "Your Name"
npm config set init-author-email "your.email@example.com"
npm config set init-license "MIT"
npm config set init-version "1.0.0"

# 然后使用npm init -y会使用这些默认值
```

## 3.2 package.json核心字段详解

### 3.2.1 必需字段

#### name字段

`name`字段定义包的名称，必须满足以下规则：
- 长度必须小于等于214个字符
- 不能以点(.)或下划线(_)开头
- 不能包含大写字母
- 不能包含非URL安全字符
- 不能是Node.js核心模块名称

```json
{
  "name": "my-awesome-project"
}
```

#### version字段

`version`字段遵循语义化版本(SemVer)规范：`主版本号.次版本号.修订号`

```json
{
  "version": "1.2.3"
}
```

版本号规则：
- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 3.2.2 信息描述字段

#### description字段

简短描述项目功能

```json
{
  "description": "一个用于处理用户数据的Node.js库"
}
```

#### keywords字段

帮助用户在NPM上搜索到你的包

```json
{
  "keywords": ["data", "processing", "user", "nodejs", "library"]
}
```

#### homepage字段

项目主页URL

```json
{
  "homepage": "https://github.com/username/my-awesome-project#readme"
}
```

#### bugs字段

问题反馈地址

```json
{
  "bugs": {
    "url": "https://github.com/username/my-awesome-project/issues",
    "email": "issues@example.com"
  }
}
```

### 3.2.3 人员相关字段

#### author字段

```json
{
  "author": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "url": "https://johndoe.com"
  }
}

// 或者简写形式
{
  "author": "John Doe <john.doe@example.com> (https://johndoe.com)"
}
```

#### contributors字段

```json
{
  "contributors": [
    {
      "name": "Jane Smith",
      "email": "jane.smith@example.com"
    },
    {
      "name": "Bob Johnson",
      "email": "bob.johnson@example.com",
      "url": "https://bobjohnson.com"
    }
  ]
}
```

### 3.2.4 文件相关字段

#### main字段

指定模块的入口文件

```json
{
  "main": "src/index.js"
}
```

#### files字段

指定包含在NPM包中的文件或目录

```json
{
  "files": [
    "src/",
    "dist/",
    "README.md",
    "LICENSE"
  ]
}
```

#### bin字段

指定可执行文件

```json
{
  "bin": {
    "my-cli": "./bin/cli.js"
  }
}

// 或者简写形式
{
  "bin": "./bin/cli.js"
}
```

#### man字段

指定手册文件

```json
{
  "man": [
    "./man/my-project.1",
    "./man/my-project.2"
  ]
}
```

### 3.2.5 依赖管理字段

#### dependencies字段

生产环境依赖

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "~4.17.21",
    "moment": "2.29.4"
  }
}
```

#### devDependencies字段

开发环境依赖

```json
{
  "devDependencies": {
    "jest": "^29.6.1",
    "eslint": "^8.45.0",
    "webpack": "^5.88.2"
  }
}
```

#### peerDependencies字段

对等依赖

```json
{
  "peerDependencies": {
    "react": ">=16.8.0",
    "react-dom": ">=16.8.0"
  }
}
```

#### optionalDependencies字段

可选依赖

```json
{
  "optionalDependencies": {
    "fsevents": "^2.3.2"
  }
}
```

#### bundledDependencies字段

打包依赖

```json
{
  "bundledDependencies": [
    "lodash",
    "moment"
  ]
}
```

### 3.2.6 脚本字段

#### scripts字段

定义可执行的脚本命令

```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "test": "jest",
    "lint": "eslint src/**/*.js",
    "format": "prettier --write src/**/*.js"
  }
}
```

#### 生命周期脚本

```json
{
  "scripts": {
    "preinstall": "echo 'Installing dependencies...'",
    "install": "node scripts/install.js",
    "postinstall": "echo 'Dependencies installed!'",
    "prepublish": "npm run build",
    "publish": "node scripts/publish.js",
    "postpublish": "echo 'Package published!'",
    "preuninstall": "echo 'Uninstalling...'",
    "uninstall": "node scripts/uninstall.js",
    "postuninstall": "echo 'Uninstalled!'",
    "prestart": "echo 'Starting application...'",
    "start": "node src/index.js",
    "poststart": "echo 'Application started!'",
    "pretest": "npm run lint",
    "test": "jest",
    "posttest": "echo 'Tests completed!'",
    "prestop": "echo 'Stopping application...'",
    "stop": "pkill -f 'node src/index.js'",
    "poststop": "echo 'Application stopped!'",
    "prerestart": "npm run stop",
    "restart": "npm run start",
    "postrestart": "echo 'Application restarted!'"
  }
}
```

### 3.2.7 配置字段

#### config字段

```json
{
  "config": {
    "port": "8080",
    "database_url": "mongodb://localhost:27017/myapp"
  }
}
```

#### engines字段

指定Node.js和NPM版本要求

```json
{
  "engines": {
    "node": ">=14.0.0",
    "npm": ">=6.0.0"
  }
}
```

#### engineStrict字段

严格引擎检查

```json
{
  "engineStrict": true
}
```

#### os字段

指定支持的操作系统

```json
{
  "os": ["darwin", "linux"]
}
```

#### cpu字段

指定支持的CPU架构

```json
{
  "cpu": ["x64", "arm64"]
}
```

### 3.2.8 发布相关字段

#### private字段

防止意外发布

```json
{
  "private": true
}
```

#### publishConfig字段

发布配置

```json
{
  "publishConfig": {
    "registry": "https://registry.npmjs.org/",
    "access": "public",
    "tag": "latest"
  }
}
```

#### repository字段

代码仓库信息

```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/username/my-awesome-project.git"
  }
}

// 或者简写形式
{
  "repository": "username/my-awesome-project"
}
```

#### license字段

许可证信息

```json
{
  "license": "MIT"
}

// 或者使用SPDX表达式
{
  "license": "(MIT OR Apache-2.0)"
}
```

## 3.3 package.json高级配置

### 3.3.1 工作区配置

#### workspaces字段

```json
{
  "private": true,
  "workspaces": [
    "packages/*"
  ]
}
```

#### 工作区示例结构

```
my-monorepo/
├── package.json
├── packages/
│   ├── package-a/
│   │   └── package.json
│   ├── package-b/
│   │   └── package.json
│   └── package-c/
│       └── package.json
```

### 3.3.2 导入映射

#### imports字段

```json
{
  "imports": {
    "#app/*": "./src/*",
    "#utils/*": "./src/utils/*",
    "#config": "./src/config/index.js"
  }
}
```

### 3.3.3 条件导出

#### exports字段

```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./package.json": "./package.json"
  }
}
```

### 3.3.4 浏览器字段

#### browser字段

```json
{
  "browser": {
    "./lib/index.js": "./lib/browser.js",
    "util": false
  }
}
```

### 3.3.5 模块字段

#### module字段

```json
{
  "module": "./dist/index.esm.js"
}
```

#### type字段

```json
{
  "type": "module"
}
```

## 3.4 package.json最佳实践

### 3.4.1 版本管理最佳实践

#### 使用语义化版本

```json
{
  "version": "1.2.3"
}
```

#### 精确控制依赖版本

```json
{
  "dependencies": {
    "express": "4.18.2",           // 精确版本
    "lodash": "^4.17.21",          // 兼容补丁和次版本
    "moment": "~2.29.4",           // 仅兼容补丁
    "react": ">=16.8.0 <18.0.0"    // 版本范围
  }
}
```

### 3.4.2 脚本命名最佳实践

#### 使用有意义的脚本名称

```json
{
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.js",
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "postbuild": "npm run test"
  }
}
```

### 3.4.3 依赖分类最佳实践

#### 合理分类依赖

```json
{
  "dependencies": {
    "express": "^4.18.2",      // 运行时依赖
    "lodash": "^4.17.21"       // 应用代码中使用的库
  },
  "devDependencies": {
    "jest": "^29.6.1",         // 测试框架
    "eslint": "^8.45.0",       // 代码检查工具
    "webpack": "^5.88.2",      // 构建工具
    "nodemon": "^3.0.1"        // 开发工具
  },
  "peerDependencies": {
    "react": ">=16.8.0"        // 插件宿主
  },
  "optionalDependencies": {
    "fsevents": "^2.3.2"       // 平台特定依赖
  }
}
```

### 3.4.4 安全最佳实践

#### 使用private字段防止意外发布

```json
{
  "private": true
}
```

#### 设置engines字段

```json
{
  "engines": {
    "node": ">=14.0.0",
    "npm": ">=6.0.0"
  }
}
```

## 3.5 package.json常见问题与解决方案

### 3.5.1 版本冲突问题

#### 问题场景

```json
{
  "dependencies": {
    "package-a": "^1.0.0",
    "package-b": "^2.0.0"
  }
}

// package-a依赖lodash@^4.17.0
// package-b依赖lodash@^3.10.0
```

#### 解决方案

1. 使用npm ls检查依赖树
2. 使用resolutions字段强制统一版本（Yarn）
3. 使用npm-force-resolutions（NPM）

### 3.5.2 循环依赖问题

#### 问题场景

```
package-a -> package-b -> package-a
```

#### 解决方案

1. 重构代码消除循环依赖
2. 使用依赖注入
3. 提取共同依赖到新模块

### 3.5.3 依赖安装缓慢问题

#### 解决方案

1. 使用.npmrc配置国内镜像
2. 使用yarn或pnpm替代npm
3. 使用缓存策略

### 3.5.4 package.json格式问题

#### 常见错误

1. JSON语法错误（逗号、引号等）
2. 字段拼写错误
3. 不符合规范的字段值

#### 解决方案

1. 使用JSON验证工具
2. 使用IDE的JSON支持
3. 使用npm init重新生成

## 3.6 package.json扩展工具

### 3.6.1 验证工具

#### npm-package-json-lint

```bash
# 安装
npm install -g npm-package-json-lint

# 使用
npmpackagejsonlint
```

#### 配置文件.npm-package-json-lint.json

```json
{
  "rules": {
    "require-name": "error",
    "require-version": "error",
    "require-license": "warning",
    "valid-values-license": ["error", ["MIT", "Apache-2.0"]]
  }
}
```

### 3.6.2 格式化工具

#### prettier

```json
{
  "scripts": {
    "format:package": "prettier --write package.json"
  }
}
```

### 3.6.3 依赖分析工具

#### npm-check

```bash
# 安装
npm install -g npm-check

# 使用
npm-check
```

#### depcheck

```bash
# 安装
npm install -g depcheck

# 使用
depcheck
```

## 3.7 实战案例

### 3.7.1 创建一个完整的Web应用package.json

```json
{
  "name": "my-web-app",
  "version": "1.0.0",
  "description": "一个现代化的Web应用程序",
  "main": "src/index.js",
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "serve": "webpack serve --mode development",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.{js,css,html}",
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "postbuild": "npm run test"
  },
  "keywords": [
    "web",
    "application",
    "modern",
    "javascript"
  ],
  "author": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "url": "https://johndoe.com"
  },
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/johndoe/my-web-app.git"
  },
  "bugs": {
    "url": "https://github.com/johndoe/my-web-app/issues"
  },
  "homepage": "https://github.com/johndoe/my-web-app#readme",
  "engines": {
    "node": ">=14.0.0",
    "npm": ">=6.0.0"
  },
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21",
    "moment": "^2.29.4",
    "axios": "^1.4.0"
  },
  "devDependencies": {
    "jest": "^29.6.1",
    "eslint": "^8.45.0",
    "prettier": "^3.0.0",
    "webpack": "^5.88.2",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1",
    "nodemon": "^3.0.1",
    "rimraf": "^5.0.1"
  },
  "browserslist": [
    "> 1%",
    "last 2 versions",
    "not dead"
  ]
}
```

### 3.7.2 创建一个库的package.json

```json
{
  "name": "my-awesome-library",
  "version": "1.2.3",
  "description": "一个用于处理数据的JavaScript库",
  "main": "dist/index.js",
  "module": "dist/index.esm.js",
  "types": "dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.esm.js",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./package.json": "./package.json"
  },
  "files": [
    "dist/",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "rollup -c",
    "build:watch": "rollup -c -w",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.ts",
    "lint:fix": "eslint src/**/*.ts --fix",
    "format": "prettier --write src/**/*.ts",
    "prepublishOnly": "npm run build && npm test",
    "docs": "typedoc src/index.ts"
  },
  "keywords": [
    "data",
    "processing",
    "javascript",
    "library",
    "typescript"
  ],
  "author": {
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "url": "https://janesmith.com"
  },
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/janesmith/my-awesome-library.git"
  },
  "bugs": {
    "url": "https://github.com/janesmith/my-awesome-library/issues"
  },
  "homepage": "https://github.com/janesmith/my-awesome-library#readme",
  "engines": {
    "node": ">=12.0.0"
  },
  "peerDependencies": {
    "typescript": ">=4.0.0"
  },
  "devDependencies": {
    "@types/jest": "^29.5.3",
    "@typescript-eslint/eslint-plugin": "^6.2.0",
    "@typescript-eslint/parser": "^6.2.0",
    "eslint": "^8.45.0",
    "jest": "^29.6.1",
    "prettier": "^3.0.0",
    "rollup": "^3.26.3",
    "rollup-plugin-typescript2": "^0.35.0",
    "ts-jest": "^29.1.1",
    "typedoc": "^0.24.8",
    "typescript": "^5.1.6"
  },
  "publishConfig": {
    "registry": "https://registry.npmjs.org/",
    "access": "public"
  }
}
```

### 3.7.3 创建一个CLI工具的package.json

```json
{
  "name": "my-awesome-cli",
  "version": "2.0.0",
  "description": "一个强大的命令行工具",
  "main": "src/index.js",
  "bin": {
    "my-cli": "./bin/cli.js"
  },
  "files": [
    "bin/",
    "src/",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.js bin/**/*.js",
    "lint:fix": "eslint src/**/*.js bin/**/*.js --fix",
    "format": "prettier --write src/**/*.js bin/**/*.js",
    "prepare": "husky install",
    "prepublishOnly": "npm test && npm run lint"
  },
  "keywords": [
    "cli",
    "command-line",
    "tool",
    "automation"
  ],
  "author": {
    "name": "Bob Johnson",
    "email": "bob.johnson@example.com",
    "url": "https://bobjohnson.com"
  },
  "license": "Apache-2.0",
  "repository": {
    "type": "git",
    "url": "https://github.com/bobjohnson/my-awesome-cli.git"
  },
  "bugs": {
    "url": "https://github.com/bobjohnson/my-awesome-cli/issues"
  },
  "homepage": "https://github.com/bobjohnson/my-awesome-cli#readme",
  "engines": {
    "node": ">=14.0.0"
  },
  "dependencies": {
    "commander": "^11.0.0",
    "chalk": "^5.3.0",
    "inquirer": "^9.2.8",
    "ora": "^7.0.1"
  },
  "devDependencies": {
    "eslint": "^8.45.0",
    "eslint-config-standard": "^17.1.0",
    "eslint-plugin-import": "^2.27.5",
    "eslint-plugin-n": "^16.0.1",
    "eslint-plugin-promise": "^6.1.1",
    "husky": "^8.0.3",
    "jest": "^29.6.1",
    "lint-staged": "^13.2.3",
    "prettier": "^3.0.0"
  },
  "lint-staged": {
    "*.{js,jsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

## 3.8 总结

本章详细介绍了`package.json`文件的各个方面，包括：

1. **核心字段**：name、version、description等必需和常用字段
2. **依赖管理**：dependencies、devDependencies、peerDependencies等不同类型的依赖
3. **脚本配置**：scripts字段和生命周期脚本的使用
4. **高级配置**：workspaces、exports、imports等高级特性
5. **最佳实践**：版本管理、脚本命名、依赖分类等最佳实践
6. **常见问题**：版本冲突、循环依赖等问题的解决方案
7. **扩展工具**：验证、格式化、依赖分析等工具
8. **实战案例**：Web应用、库、CLI工具的package.json示例

掌握`package.json`的配置是Node.js开发的基础技能，合理配置`package.json`可以提高项目的可维护性和开发效率。在实际开发中，应根据项目需求选择合适的字段和配置，并遵循最佳实践。