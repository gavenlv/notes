# 第5章：NPM版本管理与发布

## 5.1 语义化版本控制

### 5.1.1 什么是语义化版本控制

语义化版本控制（Semantic Versioning，简称SemVer）是一种版本编号规范，它使用三段式版本号格式：`主版本号.次版本号.修订号`（MAJOR.MINOR.PATCH）。

- **主版本号（MAJOR）**：当做了不兼容的API修改时增加
- **次版本号（MINOR）**：当做了向下兼容的功能性新增时增加
- **修订号（PATCH）**：当做了向下兼容的问题修正时增加

例如：`1.2.3` 表示主版本1，次版本2，修订3。

### 5.1.2 版本号格式详解

#### 基本格式

```
主版本号.次版本号.修订号
```

#### 预发布版本

预发布版本在基本版本号后添加连字符和预发布标识符：

```
主版本号.次版本号.修订号-预发布标识符.预发布版本号
```

例如：
- `1.0.0-alpha.1`（第一个alpha版本）
- `1.0.0-beta.2`（第二个beta版本）
- `1.0.0-rc.1`（第一个候选发布版本）

#### 构建元数据

构建元数据在基本版本号或预发布版本后添加加号和构建信息：

```
主版本号.次版本号.修订号+构建信息
主版本号.次版本号.修订号-预发布标识符+构建信息
```

例如：
- `1.0.0+20130313144700`
- `1.0.0-beta+exp.sha.5114f85`

### 5.1.3 版本范围表示法

在`package.json`中，依赖版本可以使用多种范围表示法：

#### 精确版本

```json
{
  "dependencies": {
    "package": "1.2.3"
  }
}
```

#### 波浪号范围（~）

允许修订号变化，但不允许次版本号变化：

```json
{
  "dependencies": {
    "package": "~1.2.3"  // 匹配 >=1.2.3 且 <1.3.0
  }
}
```

#### 插入号范围（^）

允许次版本号和修订号变化，但不允许主版本号变化：

```json
{
  "dependencies": {
    "package": "^1.2.3"  // 匹配 >=1.2.3 且 <2.0.0
  }
}
```

#### 大于/小于范围

```json
{
  "dependencies": {
    "package": ">1.2.3",    // 大于1.2.3
    "package": ">=1.2.3",   // 大于等于1.2.3
    "package": "<2.0.0",    // 小于2.0.0
    "package": "<=2.0.0"    // 小于等于2.0.0
  }
}
```

#### 连字符范围

```json
{
  "dependencies": {
    "package": "1.2.3 - 2.3.4"  // 匹配 >=1.2.3 且 <=2.3.4
  }
}
```

#### 或范围

```json
{
  "dependencies": {
    "package": "1.2.3 || 2.3.4"  // 匹配1.2.3或2.3.4
  }
}
```

#### 通配符

```json
{
  "dependencies": {
    "package": "1.2.*",  // 匹配1.2.x
    "package": "1.*",    // 匹配1.x.x
    "package": "*"      // 匹配任意版本
  }
}
```

## 5.2 NPM版本管理命令

### 5.2.1 查看当前版本

```bash
# 查看当前项目的版本
npm version

# 查看特定包的版本
npm view package-name version

# 查看包的所有版本
npm view package-name versions

# 查看包的版本历史
npm view package-name time
```

### 5.2.2 更新版本号

```bash
# 更新修订号（1.0.0 -> 1.0.1）
npm version patch

# 更新次版本号（1.0.0 -> 1.1.0）
npm version minor

# 更新主版本号（1.0.0 -> 2.0.0）
npm version major

# 更新为预发布版本（1.0.0 -> 1.0.1-0）
npm version prerelease

# 更新为指定的预发布标识符（1.0.0 -> 1.0.1-alpha.0）
npm version prerelease --preid=alpha

# 更新为指定版本号
npm version 1.2.3

# 查看版本更新后的变化
git diff
```

### 5.2.3 版本生命周期脚本

NPM在版本更新过程中会执行一系列生命周期脚本：

```json
{
  "scripts": {
    "preversion": "npm run test && npm run lint",
    "version": "npm run build && git add -A dist",
    "postversion": "git push && git push --tags && npm publish"
  }
}
```

执行顺序：
1. `preversion` - 版本更新前执行
2. `version` - 版本更新后执行
3. `postversion` - 版本更新完成后执行

## 5.3 NPM发布流程

### 5.3.1 注册NPM账号

1. 访问 [NPM官网](https://www.npmjs.com/) 注册账号
2. 或使用命令行注册：

```bash
npm adduser
# 或
npm login
```

### 5.3.2 准备发布

#### 检查包名是否可用

```bash
npm view package-name
```

如果返回404错误，说明包名可用。

#### 配置package.json

确保`package.json`包含必要字段：

```json
{
  "name": "your-package-name",
  "version": "1.0.0",
  "description": "A brief description of your package",
  "main": "index.js",
  "scripts": {
    "test": "jest"
  },
  "keywords": ["keyword1", "keyword2"],
  "author": "Your Name <your.email@example.com>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/your-repo.git"
  },
  "bugs": {
    "url": "https://github.com/yourusername/your-repo/issues"
  },
  "homepage": "https://github.com/yourusername/your-repo#readme",
  "files": [
    "lib/",
    "README.md",
    "LICENSE"
  ],
  "engines": {
    "node": ">=12.0.0"
  }
}
```

#### 创建.npmignore文件

`.npmignore`文件用于指定不需要发布的文件和目录：

```
# 测试文件
test/
tests/
*.test.js
*.spec.js

# 开发配置
.eslintrc
.travis.yml
.github/

# 依赖目录
node_modules/

# 构建工具配置
webpack.config.js
gulpfile.js
.babelrc

# 文档
docs/
*.md
!README.md

# IDE配置
.vscode/
.idea/

# 日志文件
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 临时文件
.tmp/
.temp/
```

### 5.3.3 发布包

#### 发布到公共注册表

```bash
# 登录NPM
npm login

# 发布包
npm publish

# 发布带标签的版本
npm publish --tag beta

# 发布到特定注册表
npm publish --registry https://registry.npmjs.org/
```

#### 发布到私有注册表

```bash
# 配置私有注册表
npm config set registry https://your-private-registry.com/

# 发布到私有注册表
npm publish

# 或使用--registry参数
npm publish --registry https://your-private-registry.com/
```

### 5.3.4 发布预发布版本

```bash
# 更新为预发布版本
npm version prerelease --preid=alpha

# 发布预发布版本
npm publish --tag alpha

# 安装预发布版本
npm install your-package@alpha
npm install your-package@1.0.0-alpha.1
```

### 5.3.5 更新已发布的包

```bash
# 更新版本号
npm version patch  # 或 minor, major

# 重新发布
npm publish
```

## 5.4 版本标签管理

### 5.4.1 查看版本标签

```bash
# 查看所有标签
npm dist-tag ls your-package-name

# 查看特定标签指向的版本
npm view your-package-name@latest version
npm view your-package-name@beta version
```

### 5.4.2 添加和修改标签

```bash
# 添加标签
npm dist-tag add your-package@1.2.3 stable

# 修改标签
npm dist-tag add your-package@1.3.0 latest

# 删除标签
npm dist-tag rm your-package-name beta
```

### 5.4.3 常用标签

- `latest`：默认标签，指向最新的稳定版本
- `next`：指向下一个即将发布的版本
- `beta`：指向beta版本
- `alpha`：指向alpha版本
- `stable`：指向长期稳定版本

### 5.4.4 使用标签安装特定版本

```bash
# 安装最新稳定版
npm install your-package

# 安装特定标签版本
npm install your-package@beta
npm install your-package@next

# 安装特定版本
npm install your-package@1.2.3
```

## 5.5 版本回退与撤销

### 5.5.1 版本回退

```bash
# 回退到指定版本
npm version 1.2.3

# 发布回退后的版本
npm publish
```

### 5.5.2 撤销发布

```bash
# 撤销24小时内发布的版本
npm unpublish your-package@1.0.0

# 撤销整个包（24小时内）
npm unpublish your-package

# 强制撤销（不推荐）
npm unpublish your-package@1.0.0 --force
```

### 5.5.3 弃用版本

```bash
# 弃用特定版本
npm deprecate your-package@1.0.0 "This version is deprecated, please use 2.0.0 or later"

# 弃用所有版本
npm deprecate your-package@* "This package is deprecated, please use new-package instead"
```

## 5.6 多环境版本管理

### 5.6.1 开发环境

```bash
# 安装开发依赖
npm install --save-dev jest eslint

# 安装特定版本
npm install --save-dev jest@29.0.0

# 安装预发布版本
npm install --save-dev jest@beta
```

### 5.6.2 测试环境

```json
{
  "scripts": {
    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --watchAll=false"
  }
}
```

### 5.6.3 生产环境

```bash
# 只安装生产依赖
npm install --production

# 安装特定生产依赖版本
npm install --save react@18.2.0

# 锁定依赖版本
npm shrinkwrap
```

## 5.7 版本管理最佳实践

### 5.7.1 遵循语义化版本控制

1. **主版本号**：当进行不兼容的API修改时增加
2. **次版本号**：当添加向下兼容的功能时增加
3. **修订号**：当进行向下兼容的问题修复时增加

### 5.7.2 使用适当的版本范围

```json
{
  "dependencies": {
    "react": "^18.2.0",      // 允许自动更新到18.x.x
    "express": "~4.18.0",     // 只允许自动更新到4.18.x
    "lodash": "4.17.21"       // 锁定特定版本
  }
}
```

### 5.7.3 使用package-lock.json

1. 提交`package-lock.json`到版本控制系统
2. 确保团队成员使用相同的依赖版本
3. 提高构建的可重现性

### 5.7.4 定期更新依赖

```bash
# 检查过时的依赖
npm outdated

# 更新到最新兼容版本
npm update

# 更新到最新版本（可能不兼容）
npm install package@latest
```

### 5.7.5 使用自动化工具

#### 使用semantic-release

```bash
# 安装semantic-release
npm install --save-dev semantic-release

# 配置package.json
{
  "scripts": {
    "release": "semantic-release"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/your-repo.git"
  }
}
```

#### 使用commitizen和commitlint

```bash
# 安装commitizen和commitlint
npm install --save-dev commitizen @commitlint/cli @commitlint/config-conventional

# 配置commitlint
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js

# 配置commitizen
echo '{"path": "cz-conventional-changelog"}' > .czrc
```

## 5.8 实战案例

### 5.8.1 完整的发布流程

```bash
# 1. 初始化项目
npm init -y

# 2. 安装依赖
npm install express
npm install --save-dev jest eslint

# 3. 编写代码和测试
# ... (编写代码和测试)

# 4. 运行测试
npm test

# 5. 运行代码检查
npm run lint

# 6. 构建项目
npm run build

# 7. 更新版本号
npm version patch

# 8. 发布包
npm publish
```

### 5.8.2 自动化发布脚本

```json
{
  "scripts": {
    "preversion": "npm run test && npm run lint",
    "version": "npm run build && git add -A dist",
    "postversion": "git push && git push --tags && npm publish",
    "release:major": "npm version major -m 'chore(release): bump major version to %s'",
    "release:minor": "npm version minor -m 'chore(release): bump minor version to %s'",
    "release:patch": "npm version patch -m 'chore(release): bump patch version to %s'",
    "release:beta": "npm version prerelease --preid=beta -m 'chore(release): bump beta version to %s'",
    "publish:beta": "npm publish --tag beta"
  }
}
```

### 5.8.3 多环境配置

```json
{
  "scripts": {
    "dev": "cross-env NODE_ENV=development nodemon src/index.js",
    "build": "cross-env NODE_ENV=production webpack --mode production",
    "test": "cross-env NODE_ENV=test jest",
    "start": "cross-env NODE_ENV=production node dist/index.js",
    "deploy:staging": "npm run build && npm run upload:staging",
    "deploy:prod": "npm run build && npm run upload:prod"
  },
  "devDependencies": {
    "cross-env": "^7.0.3"
  }
}
```

## 5.9 常见问题与解决方案

### 5.9.1 发布失败

**问题**：发布时提示权限错误

**解决方案**：
```bash
# 检查是否已登录
npm whoami

# 重新登录
npm login

# 检查包名是否已被占用
npm view your-package-name
```

**问题**：发布时提示文件过大

**解决方案**：
```bash
# 检查.npmignore文件
cat .npmignore

# 检查package.json中的files字段
cat package.json | grep -A 10 '"files"'

# 使用npm pack检查打包内容
npm pack
tar -tzf your-package-name-1.0.0.tgz
```

### 5.9.2 版本冲突

**问题**：依赖版本冲突

**解决方案**：
```bash
# 检查依赖树
npm ls

# 使用npm dedupe消除重复依赖
npm dedupe

# 使用resolutions解决冲突（yarn）
# 或使用npm-force-resolutions（npm）
```

### 5.9.3 版本回退

**问题**：需要回退到之前的版本

**解决方案**：
```bash
# 查看版本历史
npm view your-package-name time

# 回退到指定版本
npm version 1.2.3

# 发布回退后的版本
npm publish
```

## 5.10 总结

本章详细介绍了NPM版本管理与发布的各个方面，包括：

1. **语义化版本控制**：版本号格式、预发布版本和版本范围表示法
2. **NPM版本管理命令**：查看版本、更新版本号和版本生命周期脚本
3. **NPM发布流程**：注册账号、准备发布、发布包和发布预发布版本
4. **版本标签管理**：查看、添加、修改和使用版本标签
5. **版本回退与撤销**：版本回退、撤销发布和弃用版本
6. **多环境版本管理**：开发、测试和生产环境的版本管理策略
7. **版本管理最佳实践**：遵循语义化版本控制、使用适当版本范围和自动化工具
8. **实战案例**：完整发布流程、自动化发布脚本和多环境配置
9. **常见问题与解决方案**：发布失败、版本冲突和版本回退的解决方法

通过合理管理版本和发布流程，可以确保包的稳定性和可维护性，同时提高开发效率和团队协作效果。在实际项目中，应根据具体需求选择合适的版本管理策略，并遵循最佳实践来维护版本和发布流程。