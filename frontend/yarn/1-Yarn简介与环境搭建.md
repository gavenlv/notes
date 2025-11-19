# 第1章：Yarn简介与环境搭建

## 概述

Yarn（Yet Another Resource Navigator）是Facebook、Google、Exponent和Tilde联合开发的JavaScript包管理器，旨在解决NPM的痛点，提供更快、更可靠、更安全的依赖管理体验。本章将介绍Yarn的基本概念、优势，并详细讲解如何在不同操作系统上安装和配置Yarn。

## 1.1 Yarn简介

### 1.1.1 什么是Yarn？

Yarn是一个现代化的JavaScript包管理器，它提供了以下核心功能：

- **快速安装**：并行操作和优化的依赖缓存，显著加速安装过程
- **安全可靠**：使用校验和确保依赖的完整性和一致性
- **确定性**：`yarn.lock`文件保证依赖版本的一致性
- **兼容性**：与NPM registry完全兼容，无缝迁移现有项目

### 1.1.2 Yarn与NPM的对比

| 特性 | Yarn | NPM |
|------|------|-----|
| 安装速度 | 更快（并行下载、缓存） | 相对较慢 |
| 版本锁定 | yarn.lock文件 | package-lock.json文件 |
| 安全性 | 校验和验证 | 相对较弱 |
| 工作空间 | 原生支持 | 相对复杂 |
| 离线模式 | 原生支持 | 有限支持 |

### 1.1.3 Yarn的优势

1. **性能优势**
   - 并行下载依赖包
   - 智能缓存机制，避免重复下载
   - 更快的依赖解析算法

2. **可靠性优势**
   - 校验和验证，确保依赖完整性
   - `yarn.lock`锁定文件，保证安装一致性
   - 自动清理和优化依赖关系

3. **功能优势**
   - 原生工作空间（Workspaces）支持
   - 离线模式，无网络环境下也能安装
   - 更好的依赖管理和版本控制

4. **用户体验优势**
   - 清晰的命令行界面和进度显示
   - 更友好的错误信息提示
   - 更丰富的插件生态系统

## 1.2 Yarn的版本演进

Yarn经历了几个重要的版本迭代，了解这些版本差异有助于选择适合的Yarn版本：

### 1.2.1 Yarn 1.x（Classic Yarn）

Yarn 1.x是经典版本，与NPM保持高度的兼容性：

- 使用`yarn.lock`锁定依赖
- 基于Node.js的`node_modules`解析方式
- 支持基本的工作空间功能
- 稳定且广泛使用

### 1.2.2 Yarn 2.x/3.x（Yarn Berry）

Yarn 2.x及以后版本被称为"Yarn Berry"，引入了许多创新特性：

- 引入Plug'n'Play（PnP）机制，不再依赖`node_modules`
- 更严格的依赖隔离和解析
- 更快的启动时间和更小的磁盘占用
- 零安装（Zero-Install）模式
- 更强大的工作空间支持
- 内置TypeScript支持

### 1.2.3 版本选择建议

- **新手项目**：建议使用Yarn 1.x，学习曲线平缓
- **大型项目/企业应用**：推荐Yarn 2.x/3.x，享受性能和安全优势
- **从NPM迁移**：先从Yarn 1.x开始，后续可升级至Yarn Berry

## 1.3 环境要求

在安装Yarn之前，需要确保系统满足以下要求：

### 1.3.1 操作系统支持

Yarn支持以下操作系统：
- Windows 7及以上版本
- macOS 10.10及以上版本
- 大多数Linux发行版（Ubuntu, Debian, CentOS等）

### 1.3.2 Node.js版本

Yarn需要Node.js环境支持：
- Yarn 1.x：需要Node.js 4.0及以上版本
- Yarn 2.x/3.x：需要Node.js 12.0及以上版本

推荐使用LTS（长期支持）版本的Node.js，以确保最佳兼容性和稳定性。

### 1.3.3 网络要求

Yarn安装时需要访问NPM registry，因此需要：
- 稳定的互联网连接
- 访问https://registry.yarnpkg.com和https://registry.npmjs.org的权限
- 部分企业网络可能需要配置代理设置

## 1.4 Yarn安装方法

### 1.4.1 Windows系统安装

#### 方法一：使用MSI安装包

1. 访问Yarn官方网站：https://yarnpkg.com/
2. 下载最新的MSI安装包
3. 双击安装包，按照向导完成安装
4. 安装完成后，重启命令行工具

#### 方法二：使用Chocolatey

```powershell
# 安装Chocolatey（如果尚未安装）
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 使用Chocolatey安装Yarn
choco install yarn
```

#### 方法三：使用Scoop

```powershell
# 安装Scoop（如果尚未安装）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# 使用Scoop安装Yarn
scoop install yarn
```

### 1.4.2 macOS系统安装

#### 方法一：使用Homebrew

```bash
# 安装Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 使用Homebrew安装Yarn
brew install yarn
```

#### 方法二：使用MacPorts

```bash
# 使用MacPorts安装Yarn
sudo port install yarn
```

### 1.4.3 Linux系统安装

#### 方法一：使用包管理器

**Ubuntu/Debian:**

```bash
# 配置仓库
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

# 更新软件包列表并安装
sudo apt update
sudo apt install yarn
```

**CentOS/RHEL/Fedora:**

```bash
# 配置仓库
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | sudo tee /etc/yum.repos.d/yarn.repo

# 安装
sudo yum install yarn    # 对于CentOS/RHEL
# 或
sudo dnf install yarn    # 对于Fedora
```

#### 方法二：使用NPM

```bash
# 使用NPM全局安装Yarn
npm install -g yarn
```

### 1.4.4 通过Corepack使用Yarn（推荐）

Node.js 16.10+ 版本内置了Corepack，这是管理包管理器的官方工具：

```bash
# 启用Corepack（Node.js 16.10+）
corepack enable

# 安装最新稳定版的Yarn
corepack prepare yarn@stable --activate

# 安装特定版本的Yarn
corepack prepare yarn@1.22.19 --activate
```

使用Corepack的优势：
- 无需单独安装Yarn
- 自动管理Yarn版本
- 与Node.js版本紧密集成

## 1.5 验证安装

### 1.5.1 检查Yarn版本

```bash
yarn --version
```

命令执行后，应显示Yarn的版本号，例如：
```
1.22.19
```

### 1.5.2 查看Yarn帮助信息

```bash
yarn --help
```

### 1.5.3 查看Yarn基本信息

```bash
yarn -v --verbose
```

## 1.6 Yarn基础配置

### 1.6.1 查看配置

```bash
# 查看当前配置
yarn config list

# 查看特定配置项
yarn config get <key>
```

### 1.6.2 设置配置

```bash
# 设置registry为淘宝镜像（提高国内下载速度）
yarn config set registry https://registry.npm.taobao.org

# 设置代理
yarn config set proxy http://your-proxy-server:port
yarn config set https-proxy http://your-proxy-server:port

# 设置默认的前缀
yarn config set prefix /usr/local
```

### 1.6.3 删除配置

```bash
# 删除特定配置项
yarn config delete <key>
```

## 1.7 升级Yarn

### 1.7.1 自升级（仅限Yarn 1.x）

```bash
# 升级到最新稳定版
yarn self upgrade

# 升级到特定版本
yarn self upgrade <version>
```

### 1.7.2 使用包管理器升级

#### npm方式

```bash
npm install -g yarn@latest
```

#### Corepack方式

```bash
# 升级到最新版本
corepack prepare yarn@latest --activate
```

## 1.8 Yarn基本概念

### 1.8.1 package.json

每个使用Yarn的项目都需要一个`package.json`文件，它定义了项目的元信息、依赖关系和脚本。

创建一个简单的`package.json`：

```bash
# 交互式创建
yarn init

# 快速创建（接受默认值）
yarn init -y
```

### 1.8.2 yarn.lock

`yarn.lock`文件是Yarn的核心特性之一，它锁定了项目中每个依赖包的确切版本，确保在不同环境中安装的依赖完全一致。这个文件应该提交到版本控制系统中。

### 1.8.3 依赖类型

Yarn支持多种依赖类型，每种类型都有特定的用途：

- `dependencies`：生产环境必需的依赖
- `devDependencies`：开发环境所需的依赖
- `peerDependencies`：对等依赖，宿主项目需要提供
- `optionalDependencies`：可选依赖，安装失败不会导致安装中止
- `bundledDependencies`：打包依赖，发布时会包含在包中

## 1.9 Yarn与现有项目的集成

### 1.9.1 从NPM迁移到Yarn

1. 保留现有的`package.json`和`package-lock.json`文件
2. 运行`yarn install`，Yarn会：
   - 读取`package.json`
   - 忽略`package-lock.json`
   - 生成新的`yarn.lock`文件
3. 将`yarn.lock`添加到版本控制
4. 删除`package-lock.json`和`node_modules`（可选）
5. 更新团队文档，指示使用Yarn命令

### 1.9.2 团队协作建议

1. 在项目README中明确指定使用的包管理器
2. 添加`.npmrc`或`.yarnrc`配置文件，锁定团队配置
3. 在CI/CD中指定使用Yarn
4. 考虑添加一个`preinstall`脚本，检查是否使用了正确的包管理器

## 1.10 常见问题与解决方案

### 1.10.1 权限问题（Linux/macOS）

```bash
# 如果遇到EACCES错误，配置npm全局目录
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 1.10.2 网络问题

```bash
# 使用代理
yarn config set proxy http://proxy-server:port
yarn config set https-proxy https://proxy-server:port

# 使用国内镜像
yarn config set registry https://registry.npm.taobao.org
```

### 1.10.3 版本冲突

如果系统中有多个Node.js版本，考虑使用版本管理器：

```bash
# 安装nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装并使用特定Node.js版本
nvm install 16
nvm use 16
```

## 1.11 实践练习

### 练习1：安装和配置Yarn

1. 根据您的操作系统安装Yarn
2. 验证安装是否成功
3. 配置适合您环境的Yarn设置
4. 升级到最新版本

### 练习2：创建第一个Yarn项目

1. 创建一个新目录
2. 初始化一个新的Yarn项目
3. 添加一个简单的依赖
4. 验证`yarn.lock`文件的生成

## 1.12 总结

本章介绍了Yarn的基本概念、优势、版本演进以及详细的安装和配置方法。Yarn作为JavaScript生态系统的现代化包管理器，通过并行下载、智能缓存和确定性依赖管理，显著提升了开发体验和项目可靠性。

关键要点：
- Yarn是NPM的替代品，提供更快、更可靠的包管理体验
- Yarn 1.x（Classic）和Yarn 2.x/3.x（Berry）有不同的特性集
- 安装Yarn有多种方式，Corepack是推荐的现代方法
- `yarn.lock`文件确保了依赖的一致性，应加入版本控制
- 从NPM迁移到Yarn相对简单，但需要团队协作

下一章将深入探讨Yarn的基础命令和包管理功能，帮助您掌握日常开发中常用的Yarn操作。