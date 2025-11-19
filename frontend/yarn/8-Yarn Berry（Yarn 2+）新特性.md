# 第8章：Yarn Berry（Yarn 2+）新特性

## 概述

本章将详细介绍Yarn Berry（Yarn 2.0及以上版本）的新特性和改进，包括插件系统、约束检查、增强的工作空间支持、零安装模式和更多创新功能。通过本章学习，您将掌握Yarn Berry的核心特性，了解它与Yarn 1.x的主要区别，以及如何充分利用这些新特性。

## 8.1 Yarn Berry概述

### 8.1.1 什么是Yarn Berry？

Yarn Berry是Yarn的2.0及以后版本的代号，它引入了许多革命性的变化和改进。与Yarn 1.x（Classic Yarn）相比，Yarn Berry提供了更快的性能、更强大的功能和更好的开发体验。

### 8.1.2 主要变化

| 特性 | Yarn 1.x (Classic) | Yarn Berry (2.0+) |
|------|-------------------|-------------------|
| 依赖解析 | node_modules | Plug'n'Play (可选) |
| 插件系统 | 无 | 内置支持 |
| 约束检查 | 无 | 内置支持 |
| 零安装 | 无 | 支持 |
| 工作空间 | 基础支持 | 增强支持 |
| 配置文件 | .yarnrc | .yarnrc.yml |
| 命令行界面 | 基础 | 增强 |

### 8.1.3 迁移原因

1. **性能提升**：更快的安装速度和更少的磁盘占用
2. **依赖确定性**：Plug'n'Play提供严格的依赖隔离
3. **开发体验**：更好的CLI和更丰富的功能
4. **未来兼容性**：Yarn团队的重点发展方向

## 8.2 升级到Yarn Berry

### 8.2.1 升级方法

#### 方法一：使用yarn policies命令

```bash
# 升级到最新稳定版本
yarn policies set-version berry

# 升级到特定版本
yarn policies set-version 3.2.0
```

#### 方法二：手动升级

```bash
# 卸载全局Yarn
npm uninstall -g yarn

# 使用Corepack启用
corepack enable

# 安装Yarn Berry
corepack prepare yarn@stable --activate
```

#### 方法三：项目级升级

```json
// package.json
{
  "packageManager": "yarn@3.2.0"
}
```

然后运行：
```bash
corepack enable
yarn install
```

### 8.2.2 迁移检查清单

- [ ] 检查工具兼容性（ESLint、TypeScript等）
- [ ] 更新CI/CD脚本
- [ ] 测试开发环境
- [ ] 更新团队文档
- [ ] 备份项目

## 8.3 插件系统

### 8.3.1 插件系统概述

Yarn Berry引入了内置的插件系统，允许扩展Yarn的功能。插件可以添加新命令、修改现有行为或集成外部工具。

### 8.3.2 使用插件

#### 安装官方插件

```bash
# 安装版本管理插件
yarn plugin import @yarnpkg/plugin-version

# 安装约束检查插件
yarn plugin import @yarnpkg/plugin-constraints

# 安装工作空间工具插件
yarn plugin import @yarnpkg/plugin-workspace-tools
```

#### 使用插件

```bash
# 使用版本插件
yarn version patch

# 使用约束检查
yarn constraints check

# 使用工作空间工具
yarn workspaces focus @my-project/app
```

### 8.3.3 常用官方插件

| 插件 | 功能 | 安装命令 |
|------|------|---------|
| @yarnpkg/plugin-version | 版本管理 | `yarn plugin import @yarnpkg/plugin-version` |
| @yarnpkg/plugin-constraints | 约束检查 | `yarn plugin import @yarnpkg/plugin-constraints` |
| @yarnpkg/plugin-workspace-tools | 工作空间工具 | `yarn plugin import @yarnpkg/plugin-workspace-tools` |
| @yarnpkg/plugin-exec | 执行本地命令 | `yarn plugin import @yarnpkg/plugin-exec` |
| @yarnpkg/plugin-interactive-tools | 交互式工具 | `yarn plugin import @yarnpkg/plugin-interactive-tools` |

## 8.4 约束检查

### 8.4.1 什么是约束检查？

约束检查允许您定义一系列规则，确保项目遵循特定的依赖模式、代码结构或其他约定。

### 8.4.2 定义约束

创建`constraints.pro`文件：

```prolog
# constraints.pro

# 限制特定包的版本
gen_enforced_pkg("react", "17.0.0", EXACT).

# 限制包的范围
gen_enforced_pkg("react", "^16.0.0", GT).

# 禁止使用特定包
gen_forbidden_pkg("deprecated-package").

# 限制工作空间依赖
workspace_type(@my-project/*, workspace_type(app)).
workspace_type(@my-project/*, workspace_type(library)).

# 依赖关系约束
gen_dep_constraint(@my-project/*, @my-project/*, dev_dependency).
gen_dep_constraint(@my-project/*, "react", peer_dependency).
```

### 8.4.3 检查约束

```bash
# 检查约束
yarn constraints check

# 自动修复简单约束
yarn constraints fix
```

### 8.4.4 实用约束示例

```prolog
# 限制生产依赖不能有调试工具
gen_dep_constraint(@my-project/*, "debug", forbidden_dependency).

# 确保所有工作空间有相同的devDependencies
gen_same_dev_deps(@my-project/*).

# 禁止特定包的直接依赖
gen_forbidden_dep(@my-project/*, "moment").
gen_allowed_dep(@my-project/*, "dayjs").

# 确保TypeScript项目有一致的配置
has_field(@my-project/typescript-*, "devDependencies.typescript").
has_field(@my-project/typescript-*, "devDependencies.@types/node").
```

## 8.5 增强的工作空间支持

### 8.5.1 工作空间聚焦

聚焦特定工作空间，减少安装和构建时间：

```bash
# 聚焦特定工作空间
yarn workspaces focus @my-project/app

# 聚焦多个工作空间
yarn workspaces focus @my-project/app @my-project/ui

# 聚焦所有工作空间
yarn workspaces focus --all

# 重置聚焦
yarn workspaces focus
```

### 8.5.2 工作空间互依赖

Yarn Berry改进了工作空间之间的依赖关系处理：

```json
// packages/app/package.json
{
  "dependencies": {
    "@my-project/ui": "workspace:*",
    "@my-project/utils": "workspace:^"
  }
}
```

### 8.5.3 工作空间工具插件

使用工作空间工具插件：

```bash
# 列出工作空间
yarn workspaces list

# 显示工作空间信息
yarn workspaces info

# 检查工作空间依赖关系
yarn workspaces why @my-project/utils

# 在工作空间间运行命令
yarn workspaces each build
```

## 8.6 零安装模式

### 8.6.1 什么是零安装？

零安装模式允许将所有依赖存储在版本控制中，使项目能够在不运行`yarn install`的情况下运行。

### 8.6.2 配置零安装

```yaml
# .yarnrc.yml

nodeLinker: pnp
nmMode: hardlinks-local
enableGlobalCache: false
```

### 8.6.3 提交依赖到版本控制

```bash
# 添加yarn缓存
git add .yarn/cache

# 提交
git commit -m "Add dependencies for zero-install"
```

### 8.6.4 零安装的优势

1. **即时启动**：克隆项目后即可运行
2. **环境一致性**：所有开发者使用相同的依赖
3. **CI/CD简化**：无需安装步骤
4. **依赖审计**：依赖变更可见且可审计

### 8.6.5 零安装的注意事项

1. **仓库大小**：会增加仓库大小
2. **存储成本**：增加存储需求
3. **合并冲突**：更新依赖时可能产生冲突

## 8.7 增强的CLI

### 8.7.1 新命令

```bash
# 版本管理
yarn version patch
yarn version minor
yarn version major

# 约束检查
yarn constraints check
yarn constraints fix

# 工作空间聚焦
yarn workspaces focus @my-project/app

# 执行本地命令
yarn exec my-script.js

# 交互式依赖添加
yarn add --interactive

# 管理缓存
yarn cache clean --pattern "lodash*"
```

### 8.7.2 增强的现有命令

```bash
# 改进的依赖添加
yarn add lodash@^4.0.0 --exact

# 增强的依赖列表
yarn list --depth=2 --pattern="react*"

# 改进的信息查询
yarn info react --json --reason

# 增强的全局包管理
yarn global list --depth=1
```

### 8.7.3 交互式模式

```bash
# 交互式依赖添加
yarn add --interactive

# 交互式版本更新
yarn upgrade-interactive --latest

# 交互式依赖删除
yarn remove --interactive
```

## 8.8 配置系统改进

### 8.8.1 .yarnrc.yml格式

Yarn Berry引入了更现代的YAML配置格式：

```yaml
# .yarnrc.yml

# 插件
plugins:
  - "@yarnpkg/plugin-version"
  - "@yarnpkg/plugin-constraints"

# 基本配置
nodeLinker: pnp
enableGlobalCache: false
enableImmutableInstalls: false

# 网络配置
networkTimeout: 60000
networkConcurrency: 10

# 缓存配置
cacheFolder: ".yarn/cache"

# 工作空间配置
workspaces:
  - "packages/*"
  - "apps/*"

# 约束配置
constraintsPath: "constraints.pro"
```

### 8.8.2 环境特定配置

```yaml
# .yarnrc.yml (开发环境)
nodeLinker: node-modules
loglevel: "debug"

# .yarnrc.yml (生产环境)
nodeLinker: pnp
enableImmutableInstalls: true
loglevel: "error"
```

### 8.8.3 条件配置

```yaml
# .yarnrc.yml

# 默认配置
nodeLinker: "pnp"
loglevel: "info"

# 环境特定配置
when:
  - condition: "process.env.NODE_ENV === 'development'"
    settings:
      nodeLinker: "node-modules"
      loglevel: "debug"
  - condition: "process.env.NODE_ENV === 'production'"
    settings:
      enableImmutableInstalls: true
      loglevel: "error"
```

## 8.9 性能改进

### 8.9.1 更快的依赖解析

Yarn Berry引入了更高效的依赖解析算法：

```bash
# 测试解析速度
time yarn install
```

### 8.9.2 并行安装

增加并行度以提高安装速度：

```yaml
# .yarnrc.yml
networkConcurrency: 20
```

### 8.9.3 增量安装

只安装变更的依赖：

```bash
# 默认行为，无需额外命令
yarn install
```

## 8.10 安全增强

### 8.10.1 校验和验证

Yarn Berry增强了对依赖完整性的验证：

```bash
# 验证缓存完整性
yarn cache verify

# 强制校验和检查
yarn install --checksums
```

### 8.10.2 不可变安装

防止意外修改`node_modules`：

```yaml
# .yarnrc.yml
enableImmutableInstalls: true
```

### 8.10.3 依赖审计

```bash
# 审计安全漏洞
yarn audit

# 审计特定包
yarn audit --group dependencies --level moderate
```

## 8.11 迁移指南

### 8.11.1 常见迁移问题

#### PnP兼容性问题

```bash
# 使用pnpify适配工具
yarn add -D @yarnpkg/pnpify
yarn pnpify eslint

# 或使用fallback模式
echo "pnpFallbackMode: all" >> .yarnrc.yml
```

#### 工具集成问题

```bash
# 安装TypeScript适配器
yarn add -D typescript

# 配置tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "node",
    "baseUrl": "."
  }
}
```

#### 脚本兼容性问题

```bash
# 使用yarn exec替代直接调用
yarn exec node my-script.js

# 或使用交互式模式
yarn node
```

### 8.11.2 迁移检查清单

- [ ] 安装Yarn Berry
- [ ] 更新.yarnrc.yml配置
- [ ] 测试现有工具兼容性
- [ ] 安装必要的适配器
- [ ] 更新CI/CD脚本
- [ ] 测试工作空间功能
- [ ] 更新团队文档
- [ ] 培训团队成员

## 8.12 实际应用案例

### 8.12.1 大型React应用

```yaml
# .yarnrc.yml
plugins:
  - "@yarnpkg/plugin-version"
  - "@yarnpkg/plugin-constraints"
  - "@yarnpkg/plugin-workspace-tools"

nodeLinker: pnp
workspaces:
  - "packages/*"
  - "apps/*"

enableGlobalCache: false
```

```prolog
# constraints.pro
gen_enforced_pkg("react", "17.0.2", EXACT).
gen_dep_constraint(@my-project/*, "react", peer_dependency).
```

### 8.12.2 微前端项目

```yaml
# .yarnrc.yml
nodeLinker: pnp
nmMode: hardlinks-local
enableGlobalCache: false

workspaces:
  - "shared/*"
  - "apps/*"
```

### 8.12.3 组件库项目

```yaml
# .yarnrc.yml
nodeLinker: pnp
enableImmutableInstalls: true

workspaces:
  - "packages/*"

# 构建脚本
scripts:
  build: "yarn workspaces each build"
  test: "yarn workspaces each test"
  publish: "changeset publish"
```

## 8.13 最佳实践

### 8.13.1 升级策略

1. **逐步升级**：先在小项目中试用
2. **充分测试**：确保所有功能正常
3. **团队培训**：确保团队了解新功能
4. **文档更新**：更新项目文档和流程

### 8.13.2 配置建议

1. **使用YAML配置**：更现代、更易读
2. **启用PnP**：提高性能和安全性
3. **使用约束**：确保项目一致性
4. **零安装**：考虑团队规模和项目需求

### 8.13.3 工具选择

1. **官方插件优先**：更稳定、更可靠
2. **社区插件评估**：检查活跃度和维护状态
3. **适配器选择**：确保工具兼容性

## 8.14 实践练习

### 练习1：升级到Yarn Berry

1. 创建一个新项目：
   ```bash
   mkdir yarn-berry-demo
   cd yarn-berry-demo
   yarn init
   ```

2. 升级到Yarn Berry：
   ```bash
   yarn policies set-version berry
   ```

3. 测试新功能：
   ```bash
   yarn plugin import @yarnpkg/plugin-version
   yarn version --help
   ```

### 练习2：设置约束检查

1. 在练习1的项目中创建约束文件：
   ```prolog
   # constraints.pro
   gen_enforced_pkg("lodash", "^4.0.0", GT).
   ```

2. 添加测试依赖并验证约束：
   ```bash
   yarn add lodash@3.10.1
   yarn constraints check
   ```

## 8.15 总结

本章详细介绍了Yarn Berry（Yarn 2.0+）的新特性和改进，包括插件系统、约束检查、增强的工作空间支持、零安装模式和更多创新功能。Yarn Berry代表了JavaScript包管理的重大进步，提供了更快的性能、更强大的功能和更好的开发体验。

关键要点：
- Yarn Berry引入了插件系统、约束检查和零安装等革命性功能
- 插件系统使Yarn具有高度的可扩展性
- 约束检查确保项目遵循特定的依赖模式和约定
- 零安装模式提供了无需安装依赖即可运行项目的能力
- 增强的工作空间支持使Monorepo管理更加高效
- 迁移到Yarn Berry需要考虑工具兼容性和团队培训
- 适当的配置和最佳实践可以最大化Yarn Berry的优势

下一章将介绍Yarn的高级应用与实战，通过实际案例展示如何在不同场景下有效使用Yarn。