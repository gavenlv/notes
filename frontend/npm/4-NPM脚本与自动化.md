# 第4章：NPM脚本与自动化

## 4.1 NPM脚本基础

### 4.1.1 什么是NPM脚本

NPM脚本是定义在`package.json`文件中的可执行命令，通过`scripts`字段来配置。这些脚本可以自动化执行常见的开发任务，如启动服务器、运行测试、构建代码等。

### 4.1.2 为什么使用NPM脚本

1. **标准化**：提供统一的命令接口，团队成员无需了解具体实现细节
2. **自动化**：简化重复性任务，提高开发效率
3. **跨平台**：NPM脚本可以在不同操作系统上运行
4. **可组合**：脚本可以相互调用，形成复杂的工作流
5. **环境变量**：自动设置有用的环境变量

### 4.1.3 基本语法

```json
{
  "scripts": {
    "脚本名": "命令",
    "start": "node index.js",
    "test": "jest"
  }
}
```

### 4.1.4 运行NPM脚本

```bash
# 运行特定脚本
npm run <脚本名>

# 运行start脚本（特殊命令，可以省略run）
npm start

# 运行stop脚本（特殊命令，可以省略run）
npm stop

# 运行test脚本（特殊命令，可以省略run）
npm test

# 运行restart脚本（特殊命令，可以省略run）
npm restart
```

## 4.2 NPM脚本类型

### 4.2.1 预定义脚本

NPM有一些预定义的脚本名称和生命周期：

```json
{
  "scripts": {
    "preinstall": "echo 'Installing dependencies...'",
    "install": "node scripts/install.js",
    "postinstall": "echo 'Dependencies installed!'",
    "prepublish": "npm run build",
    "prepare": "npm run build",
    "prepublishOnly": "npm test",
    "prepack": "npm test",
    "postpack": "echo 'Package packed!'",
    "publish": "node scripts/publish.js",
    "postpublish": "echo 'Package published!'",
    "preuninstall": "echo 'Uninstalling...'",
    "uninstall": "node scripts/uninstall.js",
    "postuninstall": "echo 'Uninstalled!'",
    "prestart": "echo 'Starting application...'",
    "start": "node index.js",
    "poststart": "echo 'Application started!'",
    "prestop": "echo 'Stopping application...'",
    "stop": "pkill -f 'node index.js'",
    "poststop": "echo 'Application stopped!'",
    "prerestart": "npm run stop",
    "restart": "npm run start",
    "postrestart": "echo 'Application restarted!'",
    "pretest": "npm run lint",
    "test": "jest",
    "posttest": "echo 'Tests completed!'",
    "preversion": "npm run test",
    "version": "node scripts/version.js",
    "postversion": "npm publish && git push --follow-tags"
  }
}
```

### 4.2.2 自定义脚本

除了预定义脚本，你还可以定义任意名称的自定义脚本：

```json
{
  "scripts": {
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.{js,css,html}",
    "clean": "rimraf dist",
    "deploy": "npm run build && npm run upload",
    "docs": "jsdoc -c jsdoc.conf.json",
    "coverage": "jest --coverage",
    "test:watch": "jest --watch",
    "test:debug": "node --inspect-brk node_modules/.bin/jest --runInBand"
  }
}
```

## 4.3 NPM脚本高级用法

### 4.3.1 脚本参数传递

```bash
# 在命令行中传递参数
npm run script -- --param value

# 在package.json中定义
{
  "scripts": {
    "build": "webpack --mode production",
    "build:dev": "npm run build -- --mode development",
    "serve": "webpack serve --mode development",
    "serve:prod": "npm run serve -- --mode production"
  }
}
```

### 4.3.2 脚本组合

```json
{
  "scripts": {
    "lint": "eslint src/**/*.js",
    "test": "jest",
    "check": "npm run lint && npm run test",
    "precommit": "npm run check",
    "build": "webpack --mode production",
    "build:analyze": "npm run build -- --analyze",
    "deploy": "npm run test && npm run build && npm run upload",
    "start": "npm run build && node dist/index.js"
  }
}
```

### 4.3.3 并行执行脚本

使用`&`符号（Unix/Linux/macOS）或`concurrently`包（跨平台）：

```json
{
  "scripts": {
    "watch:js": "webpack --watch",
    "watch:css": "sass --watch src/scss:dist/css",
    "watch": "npm run watch:js & npm run watch:css",
    "watch:parallel": "concurrently \"npm run watch:js\" \"npm run watch:css\""
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

### 4.3.4 顺序执行脚本

使用`&&`连接符或`npm-run-all`包：

```json
{
  "scripts": {
    "clean": "rimraf dist",
    "build:js": "webpack",
    "build:css": "sass src/scss:dist/css",
    "build": "npm run clean && npm run build:js && npm run build:css",
    "build:sequential": "npm-run-all clean build:js build:css"
  },
  "devDependencies": {
    "npm-run-all": "^4.1.5"
  }
}
```

### 4.3.5 条件执行脚本

```json
{
  "scripts": {
    "build": "webpack --mode production",
    "build:dev": "cross-env NODE_ENV=development npm run build",
    "build:prod": "cross-env NODE_ENV=production npm run build",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "precommit": "lint-staged",
    "deploy:staging": "if [ \"$NODE_ENV\" = \"staging\" ]; then npm run build && npm run upload:staging; fi",
    "deploy:prod": "if [ \"$NODE_ENV\" = \"production\" ]; then npm run build && npm run upload:prod; fi"
  },
  "devDependencies": {
    "cross-env": "^7.0.3",
    "lint-staged": "^13.2.3"
  }
}
```

## 4.4 NPM脚本环境变量

### 4.4.1 内置环境变量

NPM在运行脚本时会自动设置一些环境变量：

```json
{
  "scripts": {
    "print-env": "echo 'npm_config_root: $npm_config_root'",
    "print-package": "echo 'npm_package_name: $npm_package_name'",
    "print-version": "echo 'npm_package_version: $npm_package_version'",
    "print-script": "echo 'npm_lifecycle_event: $npm_lifecycle_event'"
  }
}
```

### 4.4.2 自定义环境变量

```json
{
  "scripts": {
    "start": "cross-env NODE_ENV=production node index.js",
    "dev": "cross-env NODE_ENV=development PORT=3000 node index.js",
    "build": "cross-env NODE_ENV=production webpack --mode production",
    "test": "cross-env NODE_ENV=test jest"
  },
  "devDependencies": {
    "cross-env": "^7.0.3"
  }
}
```

### 4.4.3 使用.env文件

```json
{
  "scripts": {
    "start": "dotenv -e .env.production node index.js",
    "dev": "dotenv -e .env.development node index.js",
    "test": "dotenv -e .env.test jest"
  },
  "devDependencies": {
    "dotenv": "^16.3.1",
    "dotenv-cli": "^7.2.1"
  }
}
```

## 4.5 常用NPM脚本模式

### 4.5.1 开发环境脚本

```json
{
  "scripts": {
    "dev": "nodemon src/index.js",
    "dev:debug": "nodemon --inspect src/index.js",
    "dev:verbose": "nodemon --verbose src/index.js",
    "serve": "webpack serve --mode development",
    "serve:https": "webpack serve --mode development --https",
    "watch": "webpack --watch --mode development"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "webpack": "^5.88.2",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1"
  }
}
```

### 4.5.2 构建脚本

```json
{
  "scripts": {
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "build": "webpack --mode production",
    "build:analyze": "npm run build -- --analyze",
    "build:profile": "npm run build -- --profile",
    "build:report": "npm run build:analyze > build-report.txt",
    "postbuild": "npm run size-limit"
  },
  "devDependencies": {
    "webpack": "^5.88.2",
    "webpack-bundle-analyzer": "^4.9.0",
    "rimraf": "^5.0.1",
    "size-limit": "^8.2.4"
  }
}
```

### 4.5.3 测试脚本

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:debug": "node --inspect-brk node_modules/.bin/jest --runInBand",
    "test:ci": "jest --ci --coverage --watchAll=false",
    "pretest": "npm run lint",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "jest": "^29.6.1",
    "playwright": "^1.36.2"
  }
}
```

### 4.5.4 代码质量脚本

```json
{
  "scripts": {
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "lint:css": "stylelint src/**/*.css",
    "lint:html": "htmlhint src/**/*.html",
    "format": "prettier --write src/**/*.{js,css,html,json,md}",
    "format:check": "prettier --check src/**/*.{js,css,html,json,md}",
    "check": "npm run lint && npm run format:check",
    "precommit": "lint-staged"
  },
  "devDependencies": {
    "eslint": "^8.45.0",
    "stylelint": "^15.10.2",
    "htmlhint": "^1.1.4",
    "prettier": "^3.0.0",
    "lint-staged": "^13.2.3",
    "husky": "^8.0.3"
  }
}
```

## 4.6 NPM脚本最佳实践

### 4.6.1 脚本命名规范

1. **使用描述性名称**：脚本名称应该清楚地表达其功能
2. **使用冒号分隔类别**：如`test:unit`、`test:integration`
3. **保持一致性**：在整个项目中使用一致的命名约定

```json
{
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon src/index.js",
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "test": "jest",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:e2e": "playwright test",
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.{js,css,html}",
    "clean": "rimraf dist",
    "deploy": "npm run build && npm run upload"
  }
}
```

### 4.6.2 脚本组织

1. **按功能分组**：将相关脚本放在一起
2. **使用生命周期脚本**：利用pre和post钩子
3. **避免重复**：通过组合脚本减少重复代码

```json
{
  "scripts": {
    // 开发相关
    "start": "node index.js",
    "dev": "nodemon src/index.js",
    "serve": "webpack serve --mode development",
    
    // 构建相关
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    
    // 测试相关
    "pretest": "npm run lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    
    // 代码质量
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.{js,css,html}",
    
    // 部署相关
    "predeploy": "npm run test && npm run build",
    "deploy": "npm run upload"
  }
}
```

### 4.6.3 错误处理

1. **使用`&&`连接符**：确保前一个命令成功后才执行下一个
2. **设置退出码**：确保脚本在失败时返回非零退出码
3. **使用`set -e`**：在Shell脚本中遇到错误立即退出

```json
{
  "scripts": {
    "deploy": "npm run test && npm run build && npm run upload",
    "ci": "npm run lint && npm run test:coverage && npm run build",
    "check": "npm run lint && npm run test && npm run build",
    "safe-script": "set -e && npm run lint && npm run test && npm run build"
  }
}
```

## 4.7 NPM脚本工具与库

### 4.7.1 并行与顺序执行

#### npm-run-all

```json
{
  "scripts": {
    "build:js": "webpack",
    "build:css": "sass src/scss:dist/css",
    "build:img": "imagemin src/img/* --out-dir=dist/img",
    "build": "npm-run-all build:js build:css build:img",
    "build:parallel": "npm-run-all --parallel build:js build:css build:img",
    "watch:js": "webpack --watch",
    "watch:css": "sass --watch src/scss:dist/css",
    "watch": "npm-run-all --parallel watch:js watch:css"
  },
  "devDependencies": {
    "npm-run-all": "^4.1.5"
  }
}
```

#### concurrently

```json
{
  "scripts": {
    "start": "concurrently \"npm run server\" \"npm run client\"",
    "server": "nodemon server/index.js",
    "client": "webpack serve --mode development",
    "test": "concurrently \"npm run test:unit\" \"npm run test:integration\"",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

### 4.7.2 跨平台兼容性

#### cross-env

```json
{
  "scripts": {
    "build": "cross-env NODE_ENV=production webpack --mode production",
    "dev": "cross-env NODE_ENV=development PORT=3000 node index.js",
    "test": "cross-env NODE_ENV=test jest"
  },
  "devDependencies": {
    "cross-env": "^7.0.3"
  }
}
```

#### rimraf

```json
{
  "scripts": {
    "clean": "rimraf dist",
    "clean:cache": "rimraf .cache",
    "prebuild": "npm run clean"
  },
  "devDependencies": {
    "rimraf": "^5.0.1"
  }
}
```

### 4.7.3 Git钩子

#### husky

```json
{
  "scripts": {
    "prepare": "husky install",
    "precommit": "lint-staged",
    "commitmsg": "commitlint -E HUSKY_GIT_PARAMS"
  },
  "devDependencies": {
    "husky": "^8.0.3",
    "lint-staged": "^13.2.3",
    "commitlint": "^17.7.0"
  }
}
```

#### lint-staged

```json
{
  "scripts": {
    "precommit": "lint-staged"
  },
  "lint-staged": {
    "*.{js,jsx}": [
      "eslint --fix",
      "prettier --write",
      "git add"
    ],
    "*.{css,scss}": [
      "stylelint --fix",
      "prettier --write",
      "git add"
    ],
    "*.{html,json,md}": [
      "prettier --write",
      "git add"
    ]
  },
  "devDependencies": {
    "lint-staged": "^13.2.3",
    "eslint": "^8.45.0",
    "stylelint": "^15.10.2",
    "prettier": "^3.0.0"
  }
}
```

## 4.8 高级自动化场景

### 4.8.1 CI/CD集成

```json
{
  "scripts": {
    "ci": "npm ci && npm run lint && npm run test:coverage && npm run build",
    "ci:install": "npm ci",
    "ci:lint": "npm run lint",
    "ci:test": "npm run test:coverage",
    "ci:build": "npm run build",
    "ci:deploy": "npm run build && npm run upload:artifacts"
  }
}
```

### 4.8.2 版本管理自动化

```json
{
  "scripts": {
    "version": "npm run test && npm run build && git add -A dist",
    "postversion": "git push && git push --tags && npm publish",
    "release:major": "npm version major -m 'chore(release): bump major version to %s'",
    "release:minor": "npm version minor -m 'chore(release): bump minor version to %s'",
    "release:patch": "npm version patch -m 'chore(release): bump patch version to %s'",
    "release:pre": "npm version prerelease --preid=beta -m 'chore(release): bump prerelease version to %s'"
  }
}
```

### 4.8.3 多环境部署

```json
{
  "scripts": {
    "build": "webpack --mode production",
    "build:staging": "cross-env NODE_ENV=staging npm run build",
    "build:prod": "cross-env NODE_ENV=production npm run build",
    "deploy:staging": "npm run build:staging && npm run upload:staging",
    "deploy:prod": "npm run build:prod && npm run upload:prod",
    "upload:staging": "s3-cli sync ./dist/ s3://staging-bucket/ --delete",
    "upload:prod": "s3-cli sync ./dist/ s3://prod-bucket/ --delete"
  },
  "devDependencies": {
    "cross-env": "^7.0.3",
    "s3-cli": "^0.14.0"
  }
}
```

## 4.9 实战案例

### 4.9.1 完整的前端项目脚本配置

```json
{
  "name": "my-frontend-app",
  "version": "1.0.0",
  "description": "一个现代化的前端应用",
  "scripts": {
    // 开发脚本
    "start": "webpack serve --mode development",
    "dev": "npm run start",
    "dev:https": "webpack serve --mode development --https",
    
    // 构建脚本
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "build": "webpack --mode production",
    "build:analyze": "npm run build -- --analyze",
    "build:staging": "cross-env NODE_ENV=staging npm run build",
    
    // 测试脚本
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "pretest": "npm run lint",
    
    // 代码质量
    "lint": "eslint src/**/*.{js,jsx,ts,tsx}",
    "lint:fix": "eslint src/**/*.{js,jsx,ts,tsx} --fix",
    "lint:css": "stylelint src/**/*.{css,scss}",
    "format": "prettier --write src/**/*.{js,jsx,ts,tsx,css,scss,json,md}",
    "format:check": "prettier --check src/**/*.{js,jsx,ts,tsx,css,scss,json,md}",
    
    // Git钩子
    "prepare": "husky install",
    "precommit": "lint-staged",
    "commitmsg": "commitlint -E HUSKY_GIT_PARAMS",
    
    // 部署脚本
    "deploy:staging": "npm run build:staging && npm run upload:staging",
    "deploy:prod": "npm run build && npm run upload:prod",
    "upload:staging": "aws s3 sync ./dist/ s3://staging-bucket/ --delete",
    "upload:prod": "aws s3 sync ./dist/ s3://prod-bucket/ --delete",
    
    // 版本管理
    "version": "npm run test && npm run build && git add -A dist",
    "postversion": "git push && git push --tags",
    "release:major": "npm version major -m 'chore(release): bump major version to %s'",
    "release:minor": "npm version minor -m 'chore(release): bump minor version to %s'",
    "release:patch": "npm version patch -m 'chore(release): bump patch version to %s'",
    
    // 工具脚本
    "storybook": "start-storybook -p 6006",
    "build-storybook": "build-storybook",
    "docs": "jsdoc -c jsdoc.conf.json",
    "bundle-analyzer": "webpack-bundle-analyzer dist/static/js/*.js"
  },
  "devDependencies": {
    "@babel/core": "^7.22.9",
    "@babel/preset-env": "^7.22.9",
    "@babel/preset-react": "^7.22.5",
    "@commitlint/cli": "^17.7.0",
    "@commitlint/config-conventional": "^17.7.0",
    "@storybook/addon-actions": "^6.5.16",
    "@storybook/addon-essentials": "^6.5.16",
    "@storybook/addon-links": "^6.5.16",
    "@storybook/builder-webpack5": "^6.5.16",
    "@storybook/manager-webpack5": "^6.5.16",
    "@storybook/react": "^6.5.16",
    "aws-cli": "^0.0.1",
    "babel-loader": "^9.1.3",
    "concurrently": "^8.2.0",
    "cross-env": "^7.0.3",
    "css-loader": "^6.8.1",
    "eslint": "^8.45.0",
    "eslint-config-prettier": "^8.9.0",
    "eslint-plugin-react": "^7.33.1",
    "eslint-plugin-react-hooks": "^4.6.0",
    "html-webpack-plugin": "^5.5.3",
    "husky": "^8.0.3",
    "jest": "^29.6.1",
    "jsdoc": "^4.0.2",
    "lint-staged": "^13.2.3",
    "playwright": "^1.36.2",
    "prettier": "^3.0.0",
    "rimraf": "^5.0.1",
    "sass": "^1.64.2",
    "sass-loader": "^13.3.2",
    "style-loader": "^3.3.3",
    "stylelint": "^15.10.2",
    "webpack": "^5.88.2",
    "webpack-bundle-analyzer": "^4.9.0",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1"
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{css,scss}": [
      "stylelint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

### 4.9.2 Node.js后端项目脚本配置

```json
{
  "name": "my-backend-api",
  "version": "1.0.0",
  "description": "一个Node.js RESTful API",
  "scripts": {
    // 开发脚本
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "dev:debug": "nodemon --inspect src/index.js",
    
    // 构建脚本
    "clean": "rimraf dist",
    "prebuild": "npm run clean",
    "build": "babel src -d dist",
    "build:watch": "babel src -d dist --watch",
    
    // 测试脚本
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:integration": "jest --testPathPattern=integration",
    "pretest": "npm run lint",
    
    // 代码质量
    "lint": "eslint src/**/*.js",
    "lint:fix": "eslint src/**/*.js --fix",
    "format": "prettier --write src/**/*.js",
    "format:check": "prettier --check src/**/*.js",
    
    // 数据库脚本
    "db:migrate": "knex migrate:latest",
    "db:rollback": "knex migrate:rollback",
    "db:seed": "knex seed:run",
    "db:reset": "npm run db:rollback && npm run db:migrate && npm run db:seed",
    
    // Git钩子
    "prepare": "husky install",
    "precommit": "lint-staged",
    
    // 部署脚本
    "deploy:staging": "npm run build && npm run db:migrate && pm2 restart staging-app",
    "deploy:prod": "npm run build && npm run db:migrate && pm2 restart prod-app",
    
    // 版本管理
    "version": "npm run test && npm run build && git add -A dist",
    "postversion": "git push && git push --tags",
    
    // 监控脚本
    "monitor": "pm2 monit",
    "logs": "pm2 logs",
    "logs:prod": "pm2 logs prod-app",
    "logs:staging": "pm2 logs staging-app"
  },
  "devDependencies": {
    "@babel/cli": "^7.22.9",
    "@babel/core": "^7.22.9",
    "@babel/preset-env": "^7.22.9",
    "eslint": "^8.45.0",
    "eslint-config-prettier": "^8.9.0",
    "husky": "^8.0.3",
    "jest": "^29.6.1",
    "knex": "^2.5.1",
    "lint-staged": "^13.2.3",
    "nodemon": "^3.0.1",
    "prettier": "^3.0.0",
    "rimraf": "^5.0.1",
    "supertest": "^6.3.3"
  },
  "dependencies": {
    "express": "^4.18.2",
    "knex": "^2.5.1",
    "pg": "^8.11.2"
  },
  "lint-staged": {
    "*.js": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

## 4.10 总结

本章详细介绍了NPM脚本与自动化的各个方面，包括：

1. **NPM脚本基础**：基本概念、语法和运行方式
2. **脚本类型**：预定义脚本和自定义脚本的使用
3. **高级用法**：参数传递、脚本组合、并行和顺序执行
4. **环境变量**：内置环境变量和自定义环境变量的使用
5. **常用模式**：开发、构建、测试和代码质量相关的脚本模式
6. **最佳实践**：命名规范、脚本组织和错误处理
7. **工具与库**：npm-run-all、concurrently、cross-env等工具的使用
8. **高级场景**：CI/CD集成、版本管理和多环境部署
9. **实战案例**：前端和后端项目的完整脚本配置

通过合理配置NPM脚本，可以大大提高开发效率，减少重复性工作，并确保团队协作的一致性。在实际项目中，应根据具体需求选择合适的脚本模式和工具，并遵循最佳实践来组织和维护脚本。