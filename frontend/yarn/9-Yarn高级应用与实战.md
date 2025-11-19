# 第9章：Yarn高级应用与实战

## 概述

本章将通过实际案例展示Yarn在各种复杂场景下的高级应用，包括大型项目管理、CI/CD集成、企业环境部署、微前端架构等。通过这些实战案例，您将学习如何将Yarn的特性应用到真实项目中，解决实际开发中的复杂问题。

## 9.1 大型项目管理

### 9.1.1 Monorepo结构设计

大型项目通常采用Monorepo结构，Yarn工作空间是管理这类项目的理想工具。

#### 典型Monorepo结构

```
large-monorepo/
├── .yarnrc.yml                      # Yarn配置
├── .gitignore
├── package.json                     # 根package.json
├── yarn.lock                        # 全局依赖锁定
├── .yarn/                           # Yarn缓存（零安装）
│   ├── cache/
│   └── releases/
├── packages/                        # 共享包
│   ├── ui-components/              # UI组件库
│   ├── utils/                      # 工具库
│   ├── api-client/                 # API客户端
│   └── design-tokens/              # 设计令牌
├── apps/                           # 应用程序
│   ├── web-app/                    # Web应用
│   ├── mobile-app/                 # 移动应用
│   └── desktop-app/                # 桌面应用
├── tools/                          # 开发工具
│   ├── build-tools/                # 构建工具
│   ├── deploy-tools/               # 部署工具
│   └── lint-configs/               # 代码检查配置
├── docs/                           # 文档
└── scripts/                        # 构建脚本
```

#### 根目录配置

```yaml
# .yarnrc.yml

# 基本配置
nodeLinker: pnp
enableGlobalCache: false
nmMode: hardlinks-local

# 插件
plugins:
  - "@yarnpkg/plugin-version"
  - "@yarnpkg/plugin-constraints"
  - "@yarnpkg/plugin-workspace-tools"

# 工作空间配置
workspaces:
  - "packages/*"
  - "apps/*"
  - "tools/*"

# 构建配置
scripts:
  - "postinstall": "husky install"

# 依赖策略
packageExtensions:
  - "@beyond Essential": "@my-company/essential"
```

```json
// package.json
{
  "name": "@my-company/monorepo",
  "private": true,
  "version": "1.0.0",
  "packageManager": "yarn@3.2.0",
  "scripts": {
    "build": "yarn workspaces foreach run build",
    "test": "yarn workspaces foreach run test",
    "lint": "yarn workspaces foreach run lint",
    "clean": "yarn workspaces foreach run clean && rm -rf .yarn/cache",
    "dev": "yarn workspaces foreach --parallel --topological run dev",
    "bootstrap": "yarn install && husky install"
  },
  "devDependencies": {
    "@yarnpkg/plugin-version": "^2.4.0",
    "@yarnpkg/plugin-constraints": "^3.1.2",
    "@yarnpkg/plugin-workspace-tools": "^3.0.2",
    "husky": "^8.0.3",
    "lint-staged": "^13.2.0",
    "concurrently": "^7.6.0"
  }
}
```

### 9.1.2 依赖策略

#### 共享依赖管理

使用`packageExtensions`强制共享特定依赖：

```yaml
# .yarnrc.yml

packageExtensions:
  - "@beyond Essential": "@my-company/essential"
    # 强制所有工作空间使用相同版本的react
  - "react": "npm:17.0.2"
    # 强制所有工作空间使用相同版本的typescript
  - "typescript": "npm:4.9.5"
```

#### 工作空间依赖策略

```json
// packages/ui-components/package.json
{
  "name": "@my-company/ui-components",
  "dependencies": {
    "@my-company/design-tokens": "workspace:*",
    "react": "17.0.2",
    "react-dom": "17.0.2"
  },
  "peerDependencies": {
    "react": ">=16.8.0",
    "react-dom": ">=16.8.0"
  },
  "devDependencies": {
    "@my-company/build-tools": "workspace:*",
    "typescript": "4.9.5"
  }
}
```

```json
// apps/web-app/package.json
{
  "name": "@my-company/web-app",
  "dependencies": {
    "@my-company/ui-components": "workspace:^",
    "@my-company/api-client": "workspace:*",
    "react": "17.0.2",
    "react-dom": "17.0.2",
    "react-router-dom": "^6.8.0"
  },
  "devDependencies": {
    "@my-company/build-tools": "workspace:*",
    "typescript": "4.9.5",
    "vite": "^4.2.0"
  }
}
```

### 9.1.3 构建策略

#### 拓扑构建

```bash
# 按依赖顺序构建
yarn workspaces foreach --topological run build

# 并行构建（无依赖关系）
yarn workspaces foreach --parallel run build

# 只构建变更的工作空间
yarn workspaces foreach --since HEAD~1 run build
```

#### 增量构建

```javascript
// scripts/incremental-build.js
const { execSync } = require('child_process');
const { readFileSync, writeFileSync } = require('fs');
const path = require('path');

// 获取变更的文件
const changedFiles = execSync('git diff --name-only HEAD~1', { encoding: 'utf8' }).trim().split('\n');

// 确定受影响的工作空间
const affectedWorkspaces = new Set();

for (const file of changedFiles) {
  const parts = file.split('/');
  if (parts[0] === 'packages' || parts[0] === 'apps') {
    affectedWorkspaces.add(`${parts[0]}/${parts[1]}`);
  }
}

// 构建受影响的工作空间及其依赖
for (const workspace of affectedWorkspaces) {
  try {
    console.log(`Building ${workspace}...`);
    execSync(`yarn workspace ${workspace} run build`, { stdio: 'inherit' });
  } catch (error) {
    console.error(`Failed to build ${workspace}:`, error.message);
    process.exit(1);
  }
}
```

## 9.2 CI/CD集成

### 9.2.1 GitHub Actions工作流

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  install-and-cache:
    runs-on: ubuntu-latest
    outputs:
      cache-key: ${{ steps.cache-key.outputs.key }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'yarn'

      - name: Get cache key
        id: cache-key
        run: |
          KEY="${{ runner.os }}-yarn-$(hashFiles('yarn.lock'))"
          echo "::set-output name=key::$KEY"
          echo "Cache key: $KEY"

      - name: Cache Yarn dependencies
        uses: actions/cache@v3
        with:
          path: |
            .yarn/cache
            .yarn/unplugged
          key: ${{ steps.cache-key.outputs.key }}

  test:
    needs: install-and-cache
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Restore Yarn dependencies
        uses: actions/cache@v3
        with:
          path: |
            .yarn/cache
            .yarn/unplugged
          key: ${{ needs.install-and-cache.outputs.cache-key }}

      - name: Install dependencies
        run: yarn install --immutable

      - name: Run tests
        run: yarn test

      - name: Run linting
        run: yarn lint

      - name: Run type checking
        run: yarn type-check

  build:
    needs: [install-and-cache, test]
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Restore Yarn dependencies
        uses: actions/cache@v3
        with:
          path: |
            .yarn/cache
            .yarn/unplugged
          key: ${{ needs.install-and-cache.outputs.cache-key }}

      - name: Install dependencies
        run: yarn install --immutable

      - name: Build packages
        run: yarn build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: |
            packages/*/dist
            apps/*/dist
```

### 9.2.2 部署策略

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  workflow_run:
    workflows: ["CI"]
    types:
      - completed
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success'
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts

      - name: Deploy to staging
        run: |
          echo "${{ secrets.STAGING_DEPLOY_KEY }}" > deploy_key
          chmod 600 deploy_key
          scp -r -i deploy_key apps/web-app/dist/* user@staging:/var/www/staging
          ssh -i deploy_key user@staging "systemctl reload nginx"
        env:
          STAGING_DEPLOY_KEY: ${{ secrets.STAGING_DEPLOY_KEY }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts

      - name: Deploy to production
        run: |
          echo "${{ secrets.PRODUCTION_DEPLOY_KEY }}" > deploy_key
          chmod 600 deploy_key
          scp -r -i deploy_key apps/web-app/dist/* user@production:/var/www/production
          ssh -i deploy_key user@production "systemctl reload nginx"
        env:
          PRODUCTION_DEPLOY_KEY: ${{ secrets.PRODUCTION_DEPLOY_KEY }}
```

## 9.3 企业环境部署

### 9.3.1 私有Registry配置

#### Nexus/Artifactory配置

```yaml
# .yarnrc.yml

# 主registry（公共包）
registry: "https://registry.yarnpkg.com"

# 私有作用域registry
"@my-company:registry": "https://npm.my-company.com/repository/npm-private/"

# 认证配置
"//npm.my-company.com/repository/npm-private/:_authToken": "${NPM_TOKEN}"

# 镜像配置
"//npm.my-company.com/repository/npm-public/": "https://registry.yarnpkg.com"
```

#### 认证脚本

```javascript
// scripts/setup-auth.js
const { writeFileSync } = require('fs');
const { resolve } = require('path');
const { execSync } = require('child_process');

// 获取认证token
const npmToken = process.env.NPM_TOKEN;
if (!npmToken) {
  console.error('NPM_TOKEN environment variable is required');
  process.exit(1);
}

// 更新.yarnrc.yml
const yarnrcPath = resolve(__dirname, '../.yarnrc.yml');
const yarnrcContent = `
registry: "https://registry.yarnpkg.com"

"@my-company:registry": "https://npm.my-company.com/repository/npm-private/"
"//npm.my-company.com/repository/npm-private/:_authToken": "${npmToken}"

networkTimeout: 120000
networkConcurrency: 5
`;

writeFileSync(yarnrcPath, yarnrcContent.trim());
console.log('Updated .yarnrc.yml with authentication token');
```

### 9.3.2 企业网络配置

```yaml
# .yarnrc.yml

# 代理配置
proxy: "http://proxy.my-company.com:8080"
httpsProxy: "https://proxy.my-company.com:8080"
noProxy: "localhost,127.0.0.1,.my-company.com"

# 网络配置
networkTimeout: 120000
networkConcurrency: 5

# 缓存配置
enableGlobalCache: false
cacheFolder: ".yarn/cache"
```

### 9.3.3 安全策略

#### 约束检查配置

```prolog
# constraints.pro

# 限制包的版本
gen_enforced_pkg("react", "17.0.2", EXACT).
gen_enforced_pkg("react-dom", "17.0.2", EXACT).

# 禁止使用有已知漏洞的包
gen_forbidden_pkg("request").
gen_forbidden_pkg("hoek").

# 强制使用公司的内部包
gen_enforced_pkg("@my-company/ui-components", "workspace:^").
gen_enforced_pkg("@my-company/utils", "workspace:*").

# 确保安全相关包存在
gen_enforced_pkg("helmet", "npm:*").
gen_enforced_pkg("express-rate-limit", "npm:*").

# 限制开发依赖
gen_dep_constraint(@my-company/*, "nodemon", dev_dependency).
gen_dep_constraint(@my-company/*, "jest", dev_dependency).
```

#### 安全检查脚本

```javascript
// scripts/security-check.js
const { execSync } = require('child_process');
const { readFileSync } = require('fs');

// 运行yarn audit
function runAudit() {
  console.log('Running security audit...');
  try {
    const result = execSync('yarn audit --json', { encoding: 'utf8' });
    const audit = JSON.parse(result);
    
    // 检查高危漏洞
    const highVulns = audit.advisories.filter(a => 
      a.severity === 'high' || a.severity === 'critical'
    );
    
    if (highVulns.length > 0) {
      console.error(`Found ${highVulns.length} high/critical vulnerabilities:`);
      highVulns.forEach(vuln => {
        console.error(`- ${vuln.module_name}: ${vuln.title}`);
        console.error(`  URL: ${vuln.url}`);
      });
      process.exit(1);
    }
    
    console.log('No high/critical vulnerabilities found');
  } catch (error) {
    console.error('Error running security audit:', error.message);
    process.exit(1);
  }
}

// 运行约束检查
function runConstraints() {
  console.log('Running constraint checks...');
  try {
    execSync('yarn constraints check', { stdio: 'inherit' });
    console.log('All constraints passed');
  } catch (error) {
    console.error('Constraint checks failed');
    process.exit(1);
  }
}

// 主函数
function main() {
  console.log('Running security checks...');
  runAudit();
  runConstraints();
  console.log('All security checks passed!');
}

main();
```

## 9.4 微前端架构

### 9.4.1 微前端Monorepo结构

```
micro-frontend-monorepo/
├── .yarnrc.yml
├── package.json
├── yarn.lock
├── .yarn/
├── packages/
│   ├── shell-app/                    # 主应用（Shell应用）
│   ├── user-profile/                 # 用户配置模块
│   ├── dashboard/                    # 仪表盘模块
│   ├── shared-components/           # 共享组件库
│   ├── routing/                      # 路由管理
│   └── state-management/             # 状态管理
├── tools/
│   ├── build-tools/
│   └── dev-server/
└── docs/
```

### 9.4.2 Shell应用配置

```json
// packages/shell-app/package.json
{
  "name": "@my-micro-frontend/shell-app",
  "version": "1.0.0",
  "dependencies": {
    "@my-micro-frontend/shared-components": "workspace:*",
    "@my-micro-frontend/routing": "workspace:*",
    "@my-micro-frontend/state-management": "workspace:*",
    "react": "17.0.2",
    "react-dom": "17.0.2",
    "react-router-dom": "6.8.0",
    "qiankun": "^2.8.7"
  },
  "devDependencies": {
    "@my-micro-frontend/build-tools": "workspace:*",
    "typescript": "4.9.5",
    "webpack": "^5.76.0"
  }
}
```

```javascript
// packages/shell-app/src/App.js
import React from 'react';
import { ConfigProvider } from 'antd';
import { registerMicroApps, start } from 'qiankun';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Button } from '@my-micro-frontend/shared-components';

// 注册微应用
registerMicroApps([
  {
    name: 'user-profile',
    entry: '//localhost:3001',
    container: '#user-profile-container',
    activeRule: '/user-profile',
  },
  {
    name: 'dashboard',
    entry: '//localhost:3002',
    container: '#dashboard-container',
    activeRule: '/dashboard',
  },
]);

function App() {
  return (
    <ConfigProvider>
      <Router>
        <div>
          <nav>
            <Link to="/">Home</Link> | 
            <Link to="/user-profile">User Profile</Link> | 
            <Link to="/dashboard">Dashboard</Link>
          </nav>
          
          <Routes>
            <Route path="/" element={<div>Home Page</div>} />
            <Route path="/user-profile" element={<div id="user-profile-container" />} />
            <Route path="/dashboard" element={<div id="dashboard-container" />} />
          </Routes>
        </div>
      </Router>
    </ConfigProvider>
  );
}

// 启动微应用
start();

export default App;
```

### 9.4.3 微应用配置

```json
// packages/user-profile/package.json
{
  "name": "@my-micro-frontend/user-profile",
  "version": "1.0.0",
  "dependencies": {
    "@my-micro-frontend/shared-components": "workspace:*",
    "@my-micro-frontend/routing": "workspace:*",
    "@my-micro-frontend/state-management": "workspace:*",
    "react": "17.0.2",
    "react-dom": "17.0.2",
    "react-router-dom": "6.8.0"
  },
  "devDependencies": {
    "@my-micro-frontend/build-tools": "workspace:*",
    "typescript": "4.9.5",
    "webpack": "^5.76.0"
  }
}
```

```javascript
// packages/user-profile/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Button } from '@my-micro-frontend/shared-components';

let root = null;
let render = () => {};

// 生命周期钩子
export async function bootstrap() {
  console.log('react app bootstraped');
}

export async function mount(props) {
  const { container } = props;
  root = ReactDOM.createRoot(container);
  render = () => root.render(
    <BrowserRouter>
      <div>
        <h1>User Profile Micro App</h1>
        <Button type="primary">Click Me</Button>
        <p>This is rendered inside the Shell App</p>
      </div>
    </BrowserRouter>
  );
  render();
}

export async function unmount(props) {
  root.unmount();
  root = null;
  render = () => {};
}

// 独立运行
if (!window.__POWERED_BY_QIANKUN__) {
  render();
}
```

### 9.4.4 微前端开发脚本

```json
// package.json (root)
{
  "scripts": {
    "dev:shell": "yarn workspace @my-micro-frontend/shell-app dev",
    "dev:user-profile": "yarn workspace @my-micro-frontend/user-profile dev",
    "dev:dashboard": "yarn workspace @my-micro-frontend/dashboard dev",
    "dev": "concurrently \"yarn dev:shell\" \"yarn dev:user-profile\" \"yarn dev:dashboard\"",
    "build": "yarn workspaces foreach --topological run build",
    "test": "yarn workspaces foreach run test"
  }
}
```

## 9.5 性能优化

### 9.5.1 依赖优化

#### 依赖分析脚本

```javascript
// scripts/analyze-deps.js
const { readFileSync } = require('fs');
const path = require('path');

// 分析依赖
function analyzeDependencies() {
  const packageJson = JSON.parse(readFileSync('package.json', 'utf8'));
  const { dependencies = {}, devDependencies = {} } = packageJson;
  
  // 依赖分析结果
  const analysis = {
    total: Object.keys(dependencies).length + Object.keys(devDependencies).length,
    production: Object.keys(dependencies).length,
    development: Object.keys(devDependencies).length,
    size: 0,
    duplicates: [],
    securityIssues: []
  };
  
  // 计算依赖大小
  console.log('Analyzing dependency sizes...');
  
  // 检查重复依赖
  console.log('Checking for duplicate dependencies...');
  
  // 安全审计
  console.log('Running security audit...');
  
  // 输出分析结果
  console.log('Dependency Analysis:');
  console.log(`- Total dependencies: ${analysis.total}`);
  console.log(`- Production dependencies: ${analysis.production}`);
  console.log(`- Development dependencies: ${analysis.development}`);
  console.log(`- Estimated size: ${analysis.size} MB`);
  console.log(`- Duplicate dependencies: ${analysis.duplicates.length}`);
  console.log(`- Security issues: ${analysis.securityIssues.length}`);
  
  return analysis;
}

// 优化建议
function optimizeDependencies(analysis) {
  console.log('\nOptimization Recommendations:');
  
  // 检查大体积依赖
  if (analysis.size > 100) {
    console.log('- Consider using tree-shaking to reduce bundle size');
    console.log('- Remove unused dependencies');
  }
  
  // 检查重复依赖
  if (analysis.duplicates.length > 0) {
    console.log('- Use yarn dedupe to eliminate duplicate dependencies');
  }
  
  // 检查安全漏洞
  if (analysis.securityIssues.length > 0) {
    console.log('- Update packages to fix security vulnerabilities');
  }
  
  // 检查开发依赖
  if (analysis.development > analysis.production * 2) {
    console.log('- Review development dependencies and remove unused ones');
  }
}

// 主函数
function main() {
  console.log('Analyzing project dependencies...');
  const analysis = analyzeDependencies();
  optimizeDependencies(analysis);
}

main();
```

### 9.5.2 构建优化

#### 增量构建策略

```javascript
// scripts/incremental-build.js
const { execSync } = require('child_process');
const { readFileSync, existsSync } = require('fs');
const path = require('path');
const crypto = require('crypto');

// 计算文件哈希
function getFileHash(filePath) {
  if (!existsSync(filePath)) return null;
  
  const content = readFileSync(filePath);
  return crypto.createHash('md5').update(content).digest('hex');
}

// 获取变更的包
function getChangedPackages() {
  try {
    // 获取上一次构建的哈希
    const lastBuildHash = getFileHash('.last-build');
    
    // 获取当前哈希
    const currentHash = execSync('git rev-parse HEAD', { encoding: 'utf8' }).trim();
    
    if (lastBuildHash === currentHash) {
      console.log('No changes since last build');
      return [];
    }
    
    // 获取变更的文件
    const changedFiles = execSync(
      `git diff --name-only ${lastBuildHash || 'HEAD~1'} HEAD`, 
      { encoding: 'utf8' }
    ).trim().split('\n');
    
    // 确定受影响的包
    const affectedPackages = new Set();
    
    for (const file of changedFiles) {
      if (file.startsWith('packages/') || file.startsWith('apps/')) {
        const parts = file.split('/');
        const packageName = `${parts[0]}/${parts[1]}`;
        affectedPackages.add(packageName);
      }
    }
    
    return Array.from(affectedPackages);
  } catch (error) {
    console.error('Error determining changed packages:', error.message);
    return ['packages/*', 'apps/*']; // 构建所有包作为fallback
  }
}

// 构建包
function buildPackage(packagePath) {
  console.log(`Building ${packagePath}...`);
  
  try {
    execSync(`yarn workspace ${packagePath} run build`, { stdio: 'inherit' });
    console.log(`Successfully built ${packagePath}`);
    return true;
  } catch (error) {
    console.error(`Failed to build ${packagePath}:`, error.message);
    return false;
  }
}

// 主函数
function main() {
  console.log('Starting incremental build...');
  
  // 获取变更的包
  const changedPackages = getChangedPackages();
  
  if (changedPackages.length === 0) {
    console.log('No packages to build');
    return;
  }
  
  console.log(`Building ${changedPackages.length} changed packages:`, changedPackages);
  
  // 构建每个包
  let successCount = 0;
  for (const packagePath of changedPackages) {
    if (buildPackage(packagePath)) {
      successCount++;
    }
  }
  
  // 更新构建状态
  const currentHash = execSync('git rev-parse HEAD', { encoding: 'utf8' }).trim();
  require('fs').writeFileSync('.last-build', currentHash);
  
  console.log(`Incremental build completed: ${successCount}/${changedPackages.length} packages built successfully`);
}

main();
```

## 9.6 故障排除

### 9.6.1 常见问题诊断

#### 依赖冲突诊断

```javascript
// scripts/diagnose-conflicts.js
const { execSync } = require('child_process');
const { readFileSync } = require('fs');

// 诊断依赖冲突
function diagnoseConflicts() {
  console.log('Diagnosing dependency conflicts...');
  
  try {
    // 检查yarn.lock是否存在
    try {
      readFileSync('yarn.lock');
      console.log('✓ yarn.lock exists');
    } catch (error) {
      console.error('✗ yarn.lock is missing. Run `yarn install` to generate it.');
      return;
    }
    
    // 检查工作空间配置
    const packageJson = JSON.parse(readFileSync('package.json', 'utf8'));
    if (packageJson.workspaces) {
      console.log('✓ Workspaces configured:', packageJson.workspaces);
    } else {
      console.log('ℹ No workspaces configured');
    }
    
    // 检查约束
    try {
      execSync('yarn constraints check', { stdio: 'inherit' });
      console.log('✓ All constraints satisfied');
    } catch (error) {
      console.error('✗ Constraint violations detected');
    }
    
    // 检查PnP配置
    try {
      const yarnrc = readFileSync('.yarnrc.yml', 'utf8');
      if (yarnrc.includes('nodeLinker: pnp')) {
        console.log('✓ PnP enabled');
        
        // 检查.pnp.cjs是否存在
        try {
          readFileSync('.pnp.cjs');
          console.log('✓ .pnp.cjs exists');
        } catch (error) {
          console.error('✗ .pnp.cjs is missing. Run `yarn install` to generate it.');
        }
      } else {
        console.log('ℹ PnP not enabled');
      }
    } catch (error) {
      console.log('ℹ No .yarnrc.yml found');
    }
    
    // 检查安全漏洞
    try {
      execSync('yarn audit --level moderate', { stdio: 'inherit' });
      console.log('✓ No moderate or higher security vulnerabilities');
    } catch (error) {
      console.error('✗ Security vulnerabilities detected');
    }
    
  } catch (error) {
    console.error('Error during diagnosis:', error.message);
  }
}

// 主函数
function main() {
  diagnoseConflicts();
}

main();
```

### 9.6.2 性能监控

```javascript
// scripts/performance-monitor.js
const { execSync } = require('child_process');
const { performance } = require('perf_hooks');

// 监控安装性能
function monitorInstallPerformance() {
  console.log('Monitoring Yarn install performance...');
  
  const startTime = performance.now();
  
  try {
    execSync('yarn install', { stdio: 'inherit' });
    
    const endTime = performance.now();
    const duration = (endTime - startTime) / 1000; // 转换为秒
    
    console.log(`Yarn install completed in ${duration.toFixed(2)} seconds`);
    
    // 获取缓存统计
    const cacheStats = execSync('yarn cache list', { encoding: 'utf8' });
    console.log('Cache statistics:');
    console.log(cacheStats);
    
    return { duration, cacheStats };
  } catch (error) {
    const endTime = performance.now();
    const duration = (endTime - startTime) / 1000;
    
    console.error(`Yarn install failed after ${duration.toFixed(2)} seconds:`, error.message);
    return { duration: -1, error: error.message };
  }
}

// 主函数
function main() {
  const result = monitorInstallPerformance();
  
  if (result.duration > 0) {
    // 性能基准
    if (result.duration > 60) {
      console.log('⚠ Slow installation detected. Consider:');
      console.log('  - Using a registry mirror');
      console.log('  - Increasing network concurrency');
      console.log('  - Enabling offline mode for subsequent installs');
    } else if (result.duration < 30) {
      console.log('✓ Fast installation performance');
    } else {
      console.log('ℹ Average installation performance');
    }
  }
}

main();
```

## 9.7 实践练习

### 练习1：创建大型Monorepo

1. 创建一个新的Monorepo项目：
   ```bash
   mkdir large-monorepo
   cd large-monorepo
   yarn init
   ```

2. 配置工作空间和插件
3. 创建多个包并设置依赖关系
4. 实现拓扑构建和增量构建

### 练习2：设置CI/CD流程

1. 在练习1的项目中添加GitHub Actions配置
2. 实现缓存策略和并行构建
3. 设置部署流水线

## 9.8 总结

本章通过实际案例展示了Yarn在各种复杂场景下的高级应用，包括大型项目管理、CI/CD集成、企业环境部署、微前端架构等。这些实战案例展示了如何将Yarn的特性应用到真实项目中，解决实际开发中的复杂问题。

关键要点：
- Monorepo结构适合大型项目，Yarn工作空间提供了强大的支持
- 零安装和PnP可以显著提高CI/CD效率
- 企业环境需要特殊配置，如私有registry和代理设置
- 微前端架构可以利用Yarn的工作空间和依赖管理能力
- 性能监控和优化对于大型项目至关重要
- 故障排除工具可以帮助诊断和解决常见问题
- 增量构建和缓存策略可以显著提高构建效率

下一章将总结Yarn的最佳实践与性能优化技巧，帮助您掌握Yarn的高级用法，并在实际项目中应用这些经验。