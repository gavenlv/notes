# 第5章：Yarn配置与优化

## 概述

本章将详细介绍Yarn的配置系统和性能优化技巧，包括全局配置、项目级配置、网络优化、缓存管理、以及针对不同环境的优化策略。通过本章学习，您将掌握如何根据项目需求调整Yarn的行为，提高安装速度和开发效率。

## 5.1 Yarn配置系统

### 5.1.1 配置层级

Yarn配置遵循以下优先级（从高到低）：

1. **命令行参数**：通过命令行传递的参数
2. **环境变量**：以`YARN_`开头的环境变量
3. **项目配置**：`.yarnrc`和`.yarnrc.yml`文件
4. **用户配置**：`~/.yarnrc`文件
5. **全局配置**：通过`yarn config set`设置的配置

### 5.1.2 配置文件格式

Yarn支持多种配置文件格式：

- **.yarnrc**：INI格式，传统配置文件
- **.yarnrc.yml**：YAML格式，更现代的配置文件
- **.yarnrc.json**：JSON格式，程序友好的配置文件

### 5.1.3 配置管理命令

```bash
# 查看所有配置
yarn config list

# 查看特定配置
yarn config get registry

# 设置配置
yarn config set registry https://registry.npm.taobao.org

# 删除配置
yarn config delete registry

# 编辑配置文件
yarn config edit
```

## 5.2 常用配置选项

### 5.2.1 网络配置

```bash
# 设置registry镜像
yarn config set registry https://registry.npm.taobao.org

# 设置代理
yarn config set proxy http://proxy-server:port
yarn config set https-proxy https://proxy-server:port

# 设置网络超时时间（毫秒）
yarn config set network-timeout 60000

# 设置网络重试次数
yarn config set network-concurrency 10

# 设置最大网络请求数
yarn config set maxsockets 50
```

### 5.2.2 缓存配置

```bash
# 设置缓存目录
yarn config set cache-folder ~/.yarn-cache

# 设置缓存最大大小（MB）
yarn config set cache-max-megabytes 5000

# 启用/禁用缓存
yarn config set enable-offline-mirror true
yarn config set enable-offline-mirror-pruning true
```

### 5.2.3 全局目录配置

```bash
# 设置全局模块目录
yarn config set prefix ~/.yarn-global

# 设置链接前缀
yarn config set link-folder ~/.yarn-links
```

### 5.2.4 安全配置

```bash
# 启用严格SSL验证
yarn config set strict-ssl true

# 设置CA证书路径
yarn config set cafile /path/to/ca.pem
```

### 5.2.5 日志配置

```bash
# 设置日志级别（0=无, 1=错误, 2=警告, 3=信息, 4=调试）
yarn config set loglevel info

# 启用进度条
yarn config set progress-bar-style "bar"

# 启用版本检查
yarn config set version-check-enabled true
```

## 5.3 项目级配置

### 5.3.1 .yarnrc文件

在项目根目录创建`.yarnrc`文件：

```ini
# .yarnrc

# 设置registry镜像
registry "https://registry.npm.taobao.org"

# 设置缓存目录
cache-folder ".yarn-cache"

# 启用严格SSL
strict-ssl true

# 设置网络超时
network-timeout 60000

# 设置用户代理
user-agent "yarn/1.22.19 npm/? node/v16.14.0"
```

### 5.3.2 .yarnrc.yml文件

使用YAML格式的配置文件：

```yaml
# .yarnrc.yml

registry: "https://registry.npm.taobao.org"
cacheFolder: ".yarn-cache"
strictSsl: true
networkTimeout: 60000
loglevel: "info"
enableOfflineMirror: true
```

### 5.3.3 .npmrc文件

Yarn也支持`.npmrc`文件：

```ini
# .npmrc

registry=https://registry.npm.taobao.org
cache=.npm-cache
strict-ssl=true
timeout=60000
```

## 5.4 网络优化

### 5.4.1 使用国内镜像

对于国内用户，使用国内镜像可以显著提高下载速度：

```bash
# 淘宝镜像
yarn config set registry https://registry.npm.taobao.org

# 腾讯云镜像
yarn config set registry https://mirrors.cloud.tencent.com/npm/

# 华为云镜像
yarn config set registry https://mirrors.huaweicloud.com/repository/npm/
```

### 5.4.2 企业网络配置

对于企业网络环境，可能需要配置代理：

```bash
# HTTP代理
yarn config set proxy http://proxy-server:port

# HTTPS代理
yarn config set https-proxy https://proxy-server:port

# 绕过代理的地址
yarn config set no-proxy "localhost,127.0.0.1,.local"
```

### 5.4.3 私有registry配置

对于企业内部私有registry：

```bash
# 配置私有registry
yarn config set @my-company:registry https://npm.my-company.com

# 设置认证
yarn config set //npm.my-company.com/:_authToken ${NPM_TOKEN}

# 设置CA证书
yarn config set //npm.my-company.com/:_authToken ${NPM_TOKEN}
```

## 5.5 缓存优化

### 5.5.1 缓存策略

```bash
# 设置缓存目录到高速存储
yarn config set cache-folder /path/to/fast/storage

# 设置缓存大小限制
yarn config set cache-max-megabytes 5000

# 启用缓存压缩
yarn config set cache-compression true
```

### 5.5.2 缓存管理

```bash
# 查看缓存目录
yarn cache dir

# 查看缓存内容
yarn cache list

# 清理缓存
yarn cache clean

# 验证缓存完整性
yarn cache verify
```

### 5.5.3 离线安装优化

```bash
# 启用离线模式
yarn install --offline

# 优先使用离线缓存
yarn install --prefer-offline

# 严格使用离线缓存（网络不可用时不会失败）
yarn install --frozen-lockfile
```

## 5.6 并发优化

### 5.6.1 并行下载

```bash
# 设置最大网络并发数
yarn config set network-concurrency 20

# 设置最大socket数
yarn config set maxsockets 100
```

### 5.6.2 并行安装

```bash
# 启用并行安装（默认启用）
yarn install --network-concurrency 20
```

### 5.6.3 工作空间并发

```bash
# 并行运行所有工作空间的脚本
yarn workspaces run build --parallel

# 并行运行特定数量的工作空间
yarn workspaces run build --parallel --max-parallel 4
```

## 5.7 磁盘优化

### 5.7.1 符号链接优化

```bash
# 启用符号链接
yarn config set link-folder ~/.yarn-links

# 全局链接模式
yarn config set global-folder ~/.yarn-global
```

### 5.7.2 node_modules优化

```bash
# 使用平铺node_modules
yarn install --flat

# 启用模块链接
yarn config module-folder ~/.yarn-modules
```

## 5.8 环境特定配置

### 5.8.1 开发环境配置

```yaml
# .yarnrc.dev.yml

registry: "https://registry.npm.taobao.org"
loglevel: "debug"
progress-bar-style: "bar"
network-timeout: 30000
```

### 5.8.2 生产环境配置

```yaml
# .yarnrc.prod.yml

registry: "https://registry.npmjs.org"
loglevel: "error"
strict-ssl: true
enable-offline-mirror: true
```

### 5.8.3 CI环境配置

```yaml
# .yarnrc.ci.yml

cache-folder: ".yarn-cache"
network-timeout: 120000
enable-offline-mirror: true
```

## 5.9 性能监控

### 5.9.1 安装性能分析

```bash
# 显示详细安装信息
yarn install --verbose

# 显示网络活动
yarn install --network-timeout

# 分析依赖解析时间
yarn install --verbose | grep "Resolution"
```

### 5.9.2 性能基准测试

```bash
# 清理缓存和node_modules
yarn cache clean && rm -rf node_modules

# 测试安装时间
time yarn install

# 记录安装日志
yarn install --verbose > install.log 2>&1
```

## 5.10 企业环境优化

### 5.10.1 私有registry配置

```bash
# 配置作用域私有registry
yarn config set @my-company:registry https://npm.my-company.com

# 配置认证
yarn config set //npm.my-company.com/:_authToken ${NPM_TOKEN}

# 配置CA证书
yarn config set //npm.my-company.com/:_authToken ${NPM_TOKEN}
```

### 5.10.2 离线安装

```bash
# 准备离线包
yarn pack --filename my-package-1.0.0.tgz

# 安装离线包
yarn add file:./my-package-1.0.0.tgz

# 完全离线安装
yarn install --offline --frozen-lockfile
```

### 5.10.3 代理配置

```bash
# 配置HTTP代理
yarn config set proxy http://proxy.my-company.com:8080

# 配置HTTPS代理
yarn config set https-proxy https://proxy.my-company.com:8080

# 配置不使用代理的地址
yarn config set no-proxy "localhost,127.0.0.1,.my-company.com"
```

## 5.11 故障排除

### 5.11.1 网络问题

**问题**：下载包时网络超时

**解决方案**：
```bash
# 增加超时时间
yarn config set network-timeout 120000

# 使用镜像
yarn config set registry https://registry.npm.taobao.org

# 减少并发数
yarn config set network-concurrency 5
```

### 5.11.2 SSL问题

**问题**：SSL证书验证失败

**解决方案**：
```bash
# 禁用严格SSL（临时解决方案）
yarn config set strict-ssl false

# 添加CA证书
yarn config set cafile /path/to/ca.pem

# 配置私有证书
yarn config set //npm.my-company.com/:cafile /path/to/ca.pem
```

### 5.11.3 权限问题

**问题**：全局安装包时权限不足

**解决方案**：
```bash
# 更改全局目录
yarn config set prefix ~/.yarn-global

# 添加到PATH
echo 'export PATH=~/.yarn-global/bin:$PATH' >> ~/.bashrc

# 使用nvm管理Node.js版本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

## 5.12 实际应用案例

### 5.12.1 大型企业项目配置

```yaml
# .yarnrc.yml

# 企业私有registry
registry: "https://npm.my-company.com"

# 作用域registry
"@my-company:registry": "https://npm.my-company.com"

# 认证
"//npm.my-company.com/:_authToken": "${NPM_TOKEN}"

# 网络配置
networkTimeout: 120000
networkConcurrency: 10

# 缓存配置
cacheFolder: ".yarn-cache"
enableOfflineMirror: true

# 安全配置
strictSsl: true

# 日志配置
loglevel: "warn"

# 代理配置（如需要）
proxy: "http://proxy.my-company.com:8080"
httpsProxy: "https://proxy.my-company.com:8080"
```

### 5.12.2 开源项目配置

```yaml
# .yarnrc.yml

# 公共registry
registry: "https://registry.npmjs.org"

# 缓存配置
cacheFolder: ".yarn-cache"

# 网络配置
networkTimeout: 60000
networkConcurrency: 20

# 安全配置
strictSsl: true

# 日志配置
loglevel: "info"
versionCheckEnabled: true

# 性能配置
enableOfflineMirror: true
```

### 5.12.3 个人开发环境配置

```yaml
# ~/.yarnrc.yml

# 国内镜像（国内用户）
registry: "https://registry.npm.taobao.org"

# 全局安装目录
prefix: "~/.yarn-global"

# 缓存配置
cacheFolder: "~/.yarn-cache"

# 日志配置
loglevel: "info"
progressBarStyle: "bar"

# 版本检查
versionCheckEnabled: true
```

## 5.13 实践练习

### 练习1：基本配置

1. 创建一个新项目并配置基本设置：
   ```bash
   mkdir yarn-config-demo
   cd yarn-config-demo
   yarn init -y
   ```

2. 创建`.yarnrc.yml`文件并配置registry和缓存

3. 测试配置是否生效：
   ```bash
   yarn config list
   yarn install
   ```

### 练习2：性能优化

1. 测试不同配置对安装速度的影响：
   ```bash
   # 默认配置
   time yarn install
   
   # 优化配置
   yarn config set network-concurrency 20
   time yarn install
   ```

2. 比较缓存大小和安装时间

## 5.14 总结

本章详细介绍了Yarn的配置系统和性能优化技巧，包括全局配置、项目级配置、网络优化、缓存管理、以及针对不同环境的优化策略。通过合理配置Yarn，可以显著提高安装速度和开发效率。

关键要点：
- Yarn配置遵循多层优先级，命令行参数优先级最高
- 使用国内镜像可以显著提高国内用户的下载速度
- 合理配置缓存和网络参数可以优化安装性能
- 企业环境需要特殊配置，如私有registry和代理设置
- 针对不同环境（开发、测试、生产）使用不同的配置
- 监控和分析安装性能有助于进一步优化

下一章将介绍Yarn的插件系统和扩展功能，帮助您扩展Yarn的功能以满足特定需求。