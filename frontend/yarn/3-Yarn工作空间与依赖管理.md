# 第3章：Yarn工作空间与依赖管理

## 概述

本章将深入探讨Yarn的工作空间（Workspaces）功能和高级依赖管理技巧。工作空间允许您在单一仓库中管理多个相关包，这对于大型项目、组件库和微前端架构特别有用。我们将学习如何配置和使用工作空间，以及如何解决复杂的依赖关系问题。

## 3.1 工作空间概述

### 3.1.1 什么是工作空间？

工作空间是Yarn提供的一个功能，允许您在单一仓库（Monorepo）中管理多个相关的包。每个包都有自己的`package.json`，但共享一个顶层的`yarn.lock`文件和`node_modules`目录。

### 3.1.2 工作空间的优势

1. **依赖去重**：所有工作空间共享相同的依赖，避免重复安装
2. **原子操作**：一次性更新所有工作空间的依赖
3. **简化构建**：更容易构建和测试关联的包
4. **版本一致性**：确保所有工作空间使用相同的依赖版本
5. **简化开发流程**：在本地开发多个包时无需手动链接

### 3.1.3 工作空间适用场景

- 组件库开发（如React组件库）
- 微前端架构
- 共享工具和库
- 多包项目管理
- 插件系统开发

## 3.2 工作空间设置

### 3.2.1 基本配置

在项目根目录的`package.json`中添加`workspaces`字段：

```json
{
  "private": true,
  "name": "my-monorepo",
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```

### 3.2.2 工作空间结构示例

```
my-monorepo/
├── package.json          # 根目录的package.json
├── yarn.lock            # 共享的yarn.lock文件
├── packages/            # 工作空间目录
│   ├── shared-utils/    # 第一个工作空间
│   │   ├── package.json
│   │   └── src/
│   └── ui-components/   # 第二个工作空间
│       ├── package.json
│       └── src/
└── apps/                # 应用目录
    └── web-app/         # 第三个工作空间
        ├── package.json
        └── src/
```

### 3.2.3 工作空间配置详解

#### 数组形式配置

```json
{
  "private": true,
  "name": "my-monorepo",
  "workspaces": [
    "packages/*",
    "apps/*",
    "tools/*"
  ]
}
```

#### 对象形式配置

```json
{
  "private": true,
  "name": "my-monorepo",
  "workspaces": {
    "packages": [
      "packages/*"
    ],
    "apps": [
      "apps/*"
    ]
  }
}
```

#### 带有nohoist的工作空间

```json
{
  "private": true,
  "name": "my-monorepo",
  "workspaces": {
    "packages": [
      "packages/*"
    ],
    "nohoist": [
      "react-native/**",
      "expo/**"
    ]
  }
}
```

## 3.3 工作空间操作

### 3.3.1 安装依赖

```bash
# 在根目录安装所有工作空间的依赖
yarn install

# 只安装生产依赖
yarn install --production
```

### 3.3.2 添加依赖

#### 为所有工作空间添加依赖

```bash
# 为所有工作空间添加生产依赖
yarn add lodash

# 为所有工作空间添加开发依赖
yarn add jest --dev
```

#### 为特定工作空间添加依赖

```bash
# 为特定工作空间添加依赖
yarn workspace @my-monorepo/shared-utils add lodash

# 简写形式
yarn add lodash -W @my-monorepo/shared-utils
```

#### 为多个工作空间添加依赖

```bash
# 为多个工作空间添加依赖
yarn workspaces add lodash

# 为特定模式的工作空间添加依赖
yarn workspaces add lodash --pattern "@my-monorepo/*"
```

### 3.3.3 运行脚本

#### 在特定工作空间运行脚本

```bash
# 在特定工作空间运行脚本
yarn workspace @my-monorepo/shared-utils test

# 简写形式
yarn test -W @my-monorepo/shared-utils
```

#### 在所有工作空间运行脚本

```bash
# 在所有工作空间运行同名脚本
yarn workspaces run test

# 简写形式
yarn test
```

#### 按模式运行脚本

```bash
# 在匹配模式的工作空间运行脚本
yarn workspaces run test --pattern "@my-monorepo/*-utils"
```

### 3.3.4 管理工作空间

#### 列出工作空间

```bash
# 列出所有工作空间
yarn workspaces info

# 查看特定工作空间信息
yarn workspace @my-monorepo/shared-utils info
```

#### 检查工作空间依赖

```bash
# 检查工作空间的依赖关系
yarn workspaces why lodash

# 查看哪个工作空间使用了特定依赖
yarn workspaces list | grep lodash
```

## 3.4 高级依赖管理

### 3.4.1 依赖解析策略

Yarn使用以下策略解析工作空间中的依赖：

1. **优先匹配工作空间**：如果工作空间名称与依赖名称匹配，优先使用本地工作空间
2. **依赖提升**：公共依赖被提升到根目录的`node_modules`
3. **版本冲突解决**：使用满足所有约束的最高版本

### 3.4.2 跨工作空间引用

#### 使用相对路径引用

```json
{
  "name": "@my-monorepo/web-app",
  "dependencies": {
    "@my-monorepo/shared-utils": "file:../shared-utils"
  }
}
```

#### 使用协议引用（推荐）

```json
{
  "name": "@my-monorepo/web-app",
  "dependencies": {
    "@my-monorepo/shared-utils": "^1.0.0"
  }
}
```

#### 使用workspace协议

```json
{
  "name": "@my-monorepo/web-app",
  "dependencies": {
    "@my-monorepo/shared-utils": "workspace:*"
  }
}
```

### 3.4.3 发布策略

#### 发布单个工作空间

```bash
# 发布特定工作空间
yarn workspace @my-monorepo/shared-utils npm publish
```

#### 批量发布

```bash
# 发布所有已更新的工作空间
yarn workspaces each --parallel npm publish
```

#### 使用changesets管理发布

```bash
# 安装changesets
yarn add @changesets/cli -W

# 初始化changesets
yarn changeset init

# 添加变更集
yarn changeset

# 更新版本并发布
yarn changeset version
yarn changeset publish
```

## 3.5 依赖冲突解决

### 3.5.1 常见冲突类型

1. **版本不兼容**：不同工作空间依赖同一包的不同版本
2. **循环依赖**：工作空间之间存在循环引用
3. **Peer依赖冲突**：对等依赖版本要求不一致

### 3.5.2 冲突解决策略

#### 使用resolutions字段

在根目录的`package.json`中添加`resolutions`字段：

```json
{
  "private": true,
  "name": "my-monorepo",
  "workspaces": [
    "packages/*"
  ],
  "resolutions": {
    "react": "^17.0.0",
    "react-dom": "^17.0.0",
    "@babel/core": "^7.0.0"
  }
}
```

#### 使用选择性依赖解析

```json
{
  "resolutions": {
    "react": "workspace:*",
    "react-dom": "workspace:*"
  }
}
```

#### 使用peer依赖

```json
{
  "name": "@my-monorepo/shared-utils",
  "peerDependencies": {
    "react": "^16.8.0 || ^17.0.0",
    "react-dom": "^16.8.0 || ^17.0.0"
  }
}
```

### 3.5.3 调试依赖关系

#### 查看依赖树

```bash
# 查看整个项目的依赖树
yarn list

# 查看特定工作空间的依赖树
yarn workspace @my-monorepo/shared-utils list
```

#### 使用why命令

```bash
# 查看为什么安装了某个依赖
yarn why react

# 在特定工作空间查看
yarn workspace @my-monorepo/web-app why react
```

#### 使用依赖分析工具

```bash
# 安装依赖分析工具
yarn add -W depcheck

# 检查未使用的依赖
yarn depcheck
```

## 3.6 实际应用案例

### 3.6.1 组件库项目

#### 项目结构

```
component-library/
├── package.json
├── yarn.lock
├── packages/
│   ├── button/
│   │   ├── package.json
│   │   └── src/
│   ├── input/
│   │   ├── package.json
│   │   └── src/
│   └── theme/
│       ├── package.json
│       └── src/
└── apps/
    └── storybook/
        ├── package.json
        └── .storybook/
```

#### 根目录package.json

```json
{
  "private": true,
  "name": "component-library",
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "scripts": {
    "build": "yarn workspaces run build",
    "test": "yarn workspaces run test",
    "storybook": "yarn workspace @component-library/storybook storybook",
    "lint": "yarn workspaces run lint",
    "clean": "yarn workspaces run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "@storybook/react": "^6.5.10",
    "@storybook/addon-actions": "^6.5.10",
    "@storybook/addon-links": "^6.5.10",
    "eslint": "^8.28.0",
    "prettier": "^2.8.0"
  }
}
```

#### 组件package.json示例

```json
{
  "name": "@component-library/button",
  "version": "1.0.0",
  "main": "dist/index.js",
  "scripts": {
    "build": "babel src --out-dir dist",
    "test": "jest",
    "lint": "eslint src/**/*.js"
  },
  "dependencies": {
    "@component-library/theme": "workspace:*"
  },
  "devDependencies": {
    "@babel/cli": "^7.19.3",
    "@babel/core": "^7.20.5",
    "@babel/preset-react": "^7.18.6"
  },
  "peerDependencies": {
    "react": "^16.8.0 || ^17.0.0",
    "react-dom": "^16.8.0 || ^17.0.0"
  }
}
```

### 3.6.2 微前端项目

#### 项目结构

```
micro-frontends/
├── package.json
├── yarn.lock
├── packages/
│   ├── shared-components/
│   │   ├── package.json
│   │   └── src/
│   └── shared-utils/
│       ├── package.json
│       └── src/
└── apps/
    ├── shell-app/
    │   ├── package.json
    │   └── src/
    └── product-app/
        ├── package.json
        └── src/
```

#### 根目录package.json

```json
{
  "private": true,
  "name": "micro-frontends",
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "scripts": {
    "start:shell": "yarn workspace @micro-frontends/shell-app start",
    "start:product": "yarn workspace @micro-frontends/product-app start",
    "build": "yarn workspaces run build",
    "start:all": "concurrently \"yarn start:shell\" \"yarn start:product\"",
    "test": "yarn workspaces run test"
  },
  "devDependencies": {
    "concurrently": "^7.6.0",
    "webpack": "^5.75.0",
    "webpack-cli": "^5.0.1"
  }
}
```

## 3.7 最佳实践

### 3.7.1 组织工作空间

1. **清晰的目录结构**：使用有意义的目录名称和层次结构
2. **命名规范**：使用一致的命名空间（如@my-org/package-name）
3. **依赖关系**：明确工作空间之间的依赖关系

### 3.7.2 版本管理

1. **语义化版本**：遵循SemVer规范
2. **自动化版本**：使用工具自动管理版本号
3. **变更日志**：维护详细的变更日志

### 3.7.3 构建和发布

1. **构建顺序**：确保依赖项在依赖它们之前构建
2. **CI/CD集成**：在CI/CD流水线中集成工作空间构建
3. **增量发布**：只发布变更的包

### 3.7.4 开发体验

1. **IDE支持**：配置IDE以支持工作空间
2. **热重载**：实现跨工作空间的热重载
3. **调试配置**：配置调试器以处理工作空间

## 3.8 性能优化

### 3.8.1 依赖优化

1. **依赖去重**：确保相同依赖只安装一次
2. **按需安装**：只安装当前开发所需的依赖
3. **缓存策略**：优化Yarn缓存使用

### 3.8.2 构建优化

1. **并行构建**：并行构建不相关的工作空间
2. **增量构建**：只构建变更的包
3. **构建缓存**：使用构建工具的缓存功能

### 3.8.3 开发环境优化

1. **监视模式**：使用文件监视实现自动重建
2. **TypeScript项目引用**：使用TypeScript项目引用加速编译
3. **Webpack优化**：优化Webpack配置以提高构建速度

## 3.9 常见问题与解决方案

### 3.9.1 依赖冲突

**问题**：不同工作空间依赖同一包的不同版本导致冲突。

**解决方案**：
1. 使用`resolutions`字段强制统一版本
2. 使用peer依赖解决版本兼容问题
3. 分析依赖关系，消除不必要的依赖

### 3.9.2 工作空间无法识别

**问题**：Yarn无法识别某些工作空间。

**解决方案**：
1. 检查`workspaces`配置是否正确
2. 确保每个工作空间都有有效的`package.json`
3. 验证目录路径匹配模式

### 3.9.3 构建顺序问题

**问题**：构建顺序不正确导致构建失败。

**解决方案**：
1. 使用拓扑排序确定构建顺序
2. 明确指定依赖关系
3. 使用`workspaces run`的`--include`参数控制构建顺序

### 3.9.4 发布问题

**问题**：工作空间发布时遇到问题。

**解决方案**：
1. 确保工作空间名称与npm包名一致
2. 检查版本号是否符合npm规范
3. 验证发布配置和权限

## 3.10 实践练习

### 练习1：创建工作空间项目

1. 创建一个新的工作空间项目：
   ```bash
   mkdir my-workspace
   cd my-workspace
   yarn init -y
   ```

2. 配置工作空间：
   ```json
   {
     "private": true,
     "name": "my-workspace",
     "workspaces": ["packages/*"]
   }
   ```

3. 创建两个工作空间包：
   ```bash
   mkdir -p packages/{utils,app}
   cd packages/utils
   yarn init -y
   cd ../app
   yarn init -y
   ```

4. 配置包依赖关系并测试安装

### 练习2：工作空间操作

1. 在练习1创建的项目中：
   ```bash
   # 添加共享依赖
   yarn add lodash
   
   # 为特定工作空间添加依赖
   yarn workspace utils add moment
   
   # 运行工作空间脚本
   yarn workspaces run test
   ```

2. 创建跨工作空间引用
3. 测试依赖解析和版本控制

## 3.11 总结

本章深入探讨了Yarn的工作空间功能和高级依赖管理技巧。工作空间是管理大型JavaScript项目的强大工具，它提供了依赖去重、原子操作和简化构建等优势。

关键要点：
- 工作空间允许在单一仓库中管理多个相关包
- 使用workspace协议可以实现灵活的工作空间引用
- `resolutions`字段可以帮助解决依赖冲突
- 适当的目录结构和命名规范有助于项目管理
- 构建顺序和发布策略是工作空间项目的关键考虑因素
- 依赖优化和构建优化可以显著提高开发效率

下一章将介绍Yarn的脚本系统和生命周期管理，帮助您自动化项目构建和部署流程。