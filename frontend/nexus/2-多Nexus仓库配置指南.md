# 多Nexus仓库配置指南

## 概述

在企业环境中，通常需要配置多个Nexus仓库来管理不同类型的包，例如：
- 内部开发的私有包
- 第三方依赖包
- 特定项目的专用包
- 不同安全级别的包

本指南将详细介绍如何配置NPM以根据不同的包访问不同的Nexus仓库，同时确保各仓库的账号密码安全。

## NPM配置基础

### NPM配置文件位置

NPM配置文件可以存在于多个位置，按优先级排序：

1. 项目级配置：项目根目录下的 `.npmrc`
2. 用户级配置：`~/.npmrc`
3. 全局配置：`$PREFIX/etc/npmrc`
4. 内置配置：NPM内置的默认配置

### 基本配置命令

```bash
# 查看当前配置
npm config list

# 设置配置项
npm config set key value

# 删除配置项
npm config delete key

# 编辑配置文件
npm config edit
```

## 多仓库配置方案

### 方案一：使用.npmrc作用域配置

这是最推荐的方法，可以为不同的作用域（scope）配置不同的仓库。

#### 1. 创建项目级.npmrc文件

在项目根目录创建 `.npmrc` 文件：

```ini
# 默认仓库配置
registry=https://registry.npmjs.org/

# 公司内部包配置
@company:registry=https://nexus.company.com/repository/npm-private/
@company:always-auth=true

# 特定项目包配置
@project:registry=https://nexus.company.com/repository/npm-project/
@project:always-auth=true

# 第三方镜像配置
@thirdparty:registry=https://nexus.company.com/repository/npm-proxy/
```

#### 2. 配置认证信息

为了安全起见，不建议在 `.npmrc` 文件中直接存储密码。推荐使用以下方法：

**方法A：使用环境变量**

```ini
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${NEXUS_COMPANY_AUTH_TOKEN}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${NEXUS_PROJECT_AUTH_TOKEN}
```

**方法B：使用.npmrc作用域认证**

```bash
# 为特定作用域设置认证
npm config set @company:registry https://nexus.company.com/repository/npm-private/
npm config set @company:_authToken <base64-encoded-credentials>
```

#### 3. 生成认证Token

```bash
# 生成Base64编码的认证信息
echo -n 'username:password' | base64
```

### 方案二：使用npmrc文件切换

通过脚本切换不同的 `.npmrc` 文件来适应不同环境。

#### 1. 创建多个.npmrc文件

```
project/
├── .npmrc.dev
├── .npmrc.staging
├── .npmrc.prod
└── switch-npmrc.sh
```

#### 2. 创建切换脚本

**switch-npmrc.sh:**
```bash
#!/bin/bash

ENV=$1
if [ -z "$ENV" ]; then
  echo "Usage: ./switch-npmrc.sh [dev|staging|prod]"
  exit 1
fi

case $ENV in
  dev)
    cp .npmrc.dev .npmrc
    echo "Switched to development npmrc"
    ;;
  staging)
    cp .npmrc.staging .npmrc
    echo "Switched to staging npmrc"
    ;;
  prod)
    cp .npmrc.prod .npmrc
    echo "Switched to production npmrc"
    ;;
  *)
    echo "Unknown environment: $ENV"
    exit 1
    ;;
esac
```

### 方案三：使用.npmrc条件配置

通过条件语句在单个 `.npmrc` 文件中实现多环境配置。

#### .npmrc 示例

```ini
# 基础配置
registry=https://registry.npmjs.org/
progress=false

# 环境变量条件配置
${NODE_ENV}_registry=https://nexus.company.com/repository/npm-${NODE_ENV}/
${NODE_ENV}_always-auth=true

# 作用域配置
@company:registry=${COMPANY_REGISTRY}
@company:always-auth=true
@company:_authToken=${COMPANY_AUTH_TOKEN}

@project:registry=${PROJECT_REGISTRY}
@project:always-auth=true
@project:_authToken=${PROJECT_AUTH_TOKEN}
```

## 安全密码管理方案

### 方案一：使用环境变量

这是最简单且安全的方法，适用于大多数场景。

#### 1. 设置环境变量

**Windows (PowerShell):**
```powershell
$env:NEXUS_COMPANY_USERNAME = "company-user"
$env:NEXUS_COMPANY_PASSWORD = "secure-password"
$env:NEXUS_PROJECT_USERNAME = "project-user"
$env:NEXUS_PROJECT_PASSWORD = "another-secure-password"

# 生成认证Token
$env:NEXUS_COMPANY_AUTH_TOKEN = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($env:NEXUS_COMPANY_USERNAME):$($env:NEXUS_COMPANY_PASSWORD)"))
$env:NEXUS_PROJECT_AUTH_TOKEN = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($env:NEXUS_PROJECT_USERNAME):$($env:NEXUS_PROJECT_PASSWORD)"))
```

**Linux/macOS:**
```bash
export NEXUS_COMPANY_USERNAME="company-user"
export NEXUS_COMPANY_PASSWORD="secure-password"
export NEXUS_PROJECT_USERNAME="project-user"
export NEXUS_PROJECT_PASSWORD="another-secure-password"

# 生成认证Token
export NEXUS_COMPANY_AUTH_TOKEN=$(echo -n "${NEXUS_COMPANY_USERNAME}:${NEXUS_COMPANY_PASSWORD}" | base64)
export NEXUS_PROJECT_AUTH_TOKEN=$(echo -n "${NEXUS_PROJECT_USERNAME}:${NEXUS_PROJECT_PASSWORD}" | base64)
```

#### 2. 在.npmrc中使用环境变量

```ini
@company:registry=https://nexus.company.com/repository/npm-private/
@company:_authToken=${NEXUS_COMPANY_AUTH_TOKEN}

@project:registry=https://nexus.company.com/repository/npm-project/
@project:_authToken=${NEXUS_PROJECT_AUTH_TOKEN}
```

### 方案二：使用.npm-auth文件

NPM支持将认证信息存储在单独的文件中。

#### 1. 创建.npm-auth文件

在用户主目录创建 `.npmrc` 和 `.npm-auth` 文件：

**~/.npmrc:**
```ini
@company:registry=https://nexus.company.com/repository/npm-private/
@project:registry=https://nexus.company.com/repository/npm-project/
```

**~/.npm-auth:**
```ini
//nexus.company.com/repository/npm-private/:username=company-user
//nexus.company.com/repository/npm-private/:_password=base64-encoded-password
//nexus.company.com/repository/npm-project/:username=project-user
//nexus.company.com/repository/npm-project/:_password=base64-encoded-password
```

#### 2. 设置文件权限

```bash
chmod 600 ~/.npm-auth
```

### 方案三：使用npm-login命令

使用NPM内置的登录命令安全地存储认证信息。

```bash
# 为特定作用域登录
npm login --scope=@company --registry=https://nexus.company.com/repository/npm-private/

# 输入用户名、密码和邮箱
```

### 方案四：使用密钥管理系统

对于企业级应用，推荐使用专业的密钥管理系统。

#### 1. 使用Vault

```bash
# 安装Vault CLI
npm install -g @hashicorp/vault-cli

# 从Vault获取认证信息
export NEXUS_COMPANY_AUTH_TOKEN=$(vault read -field=token secret/nexus/company)
export NEXUS_PROJECT_AUTH_TOKEN=$(vault read -field=token secret/nexus/project)
```

#### 2. 使用AWS Secrets Manager

```javascript
// 使用AWS SDK获取密钥
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();

async function getNexusCredentials(secretName) {
  const data = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
  return JSON.parse(data.SecretString);
}

// 使用示例
const companyCreds = await getNexusCredentials('nexus/company');
const projectCreds = await getNexusCredentials('nexus/project');
```

## 高级配置技巧

### 1. 使用.npmrc条件语句

```ini
# 根据操作系统设置不同的配置
; ${os}-linux
cache=/tmp/npm-cache

; ${os}-darwin
cache=/Users/${user}/Library/Caches/npm

; ${os}-win32
cache=${APPDATA}/npm-cache
```

### 2. 使用.npmrc变量替换

```ini
# 定义变量
company_domain=company.com
nexus_base_url=https://nexus.${company_domain}/repository

# 使用变量
@company:registry=${nexus_base_url}/npm-private/
@project:registry=${nexus_base_url}/npm-project/
```

### 3. 使用.npmrc包含语句

```ini
# 包含公共配置
; include=./common.npmrc

# 项目特定配置
@project:registry=https://nexus.company.com/repository/npm-project/
```

## 实战案例

### 案例1：大型企业多团队配置

假设有一个大型企业，有多个开发团队，每个团队有自己的私有包：

```ini
# .npmrc
registry=https://registry.npmjs.org/

# 基础架构团队
@infra:registry=https://nexus.company.com/repository/npm-infra/
@infra:always-auth=true
@infra:_authToken=${NEXUS_INFRA_AUTH_TOKEN}

# 前端团队
@frontend:registry=https://nexus.company.com/repository/npm-frontend/
@frontend:always-auth=true
@frontend:_authToken=${NEXUS_FRONTEND_AUTH_TOKEN}

# 后端团队
@backend:registry=https://nexus.company.com/repository/npm-backend/
@backend:always-auth=true
@backend:_authToken=${NEXUS_BACKEND_AUTH_TOKEN}

# 数据团队
@data:registry=https://nexus.company.com/repository/npm-data/
@data:always-auth=true
@data:_authToken=${NEXUS_DATA_AUTH_TOKEN}
```

### 案例2：多环境配置

```ini
# .npmrc
registry=https://registry.npmjs.org/

# 开发环境
@company:registry=${DEV_REGISTRY}
@company:_authToken=${DEV_AUTH_TOKEN}

# 测试环境
@company:test-registry=${TEST_REGISTRY}
@company:test-_authToken=${TEST_AUTH_TOKEN}

# 生产环境
@company:prod-registry=${PROD_REGISTRY}
@company:prod-_authToken=${PROD_AUTH_TOKEN}
```

### 案例3：CI/CD集成

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
          
      - name: Configure NPM
        run: |
          echo "@company:registry=https://nexus.company.com/repository/npm-private/" >> ~/.npmrc
          echo "@company:_authToken=${{ secrets.NEXUS_COMPANY_AUTH_TOKEN }}" >> ~/.npmrc
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test
```

## 常见问题与解决方案

### 1. 认证失败

**问题：** 即使配置了正确的认证信息，仍然收到401未授权错误。

**解决方案：**
- 检查用户名和密码是否正确
- 确认Base64编码是否正确
- 验证仓库URL是否正确
- 检查用户是否有访问该仓库的权限

### 2. 包解析缓慢

**问题：** 从Nexus仓库下载包速度很慢。

**解决方案：**
- 配置Nexus使用更快的上游仓库
- 启用Nexus缓存
- 使用更近的Nexus实例
- 配置NPM并行下载

```ini
maxsockets=10
fetch-retry-mintimeout=20000
fetch-retry-maxtimeout=120000
```

### 3. 包版本冲突

**问题：** 不同仓库中有相同名称但不同版本的包。

**解决方案：**
- 使用作用域区分不同仓库的包
- 明确指定包版本
- 使用npm shrinkwrap锁定依赖版本

### 4. 配置不生效

**问题：** 修改了.npmrc文件但配置不生效。

**解决方案：**
- 检查.npmrc文件位置和优先级
- 使用`npm config list`查看当前配置
- 清除NPM缓存：`npm cache clean --force`
- 检查文件语法是否正确

## 最佳实践

1. **不要在代码仓库中提交敏感信息**
   - 使用环境变量存储认证信息
   - 将包含敏感信息的.npmrc文件添加到.gitignore

2. **使用作用域区分不同仓库的包**
   - 为不同团队或项目使用不同的作用域
   - 避免包名冲突

3. **定期轮换认证信息**
   - 定期更新Nexus仓库的密码
   - 使用短期有效的认证Token

4. **使用最小权限原则**
   - 为每个仓库配置最小必要权限
   - 不同仓库使用不同的认证信息

5. **监控和审计**
   - 监控仓库访问日志
   - 定期审计包的使用情况

6. **文档化配置**
   - 记录每个仓库的用途和配置方法
   - 为团队成员提供清晰的配置指南

## 总结

通过合理配置NPM和Nexus仓库，可以有效地管理企业内部的包分发，同时确保安全性。关键点包括：

1. 使用作用域区分不同仓库
2. 安全地管理认证信息
3. 根据环境使用不同的配置策略
4. 遵循安全最佳实践

这些配置方法可以根据企业的具体需求和安全策略进行调整和组合，以实现最适合的包管理解决方案。