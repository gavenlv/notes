# 第2章：NPM包管理与基本命令

## 2.1 包的安装与卸载

### 安装包的基本语法

NPM提供了多种方式来安装包，根据不同的需求可以选择合适的安装方式：

```bash
npm install <package-name>
# 或者使用简写
npm i <package-name>
```

### 安装最新版本

安装包的最新稳定版本：

```bash
npm install lodash
```

### 安装特定版本

安装包的特定版本：

```bash
npm install lodash@4.17.21
```

### 安装版本范围

安装符合特定版本范围的包：

```bash
# 安装4.x.x的最新版本
npm install lodash@4

# 安装大于等于4.17.0且小于5.0.0的版本
npm install lodash@">=4.17.0 <5.0.0"

# 安装最新的预发布版本
npm install lodash@next
```

### 安装开发依赖

将包安装为开发依赖（仅用于开发环境，不用于生产环境）：

```bash
npm install jest --save-dev
# 或者使用简写
npm install jest -D
```

### 安装生产依赖

将包安装为生产依赖（默认行为）：

```bash
npm install express --save-prod
# 或者使用简写
npm install express -P
# 或者直接使用
npm install express
```

### 安装可选依赖

安装可选依赖（包安装失败不会导致整个安装过程失败）：

```bash
npm install optional-package --save-optional
# 或者使用简写
npm install optional-package -O
```

### 安装精确版本

安装精确版本的包（忽略package.json中的版本范围）：

```bash
npm install lodash@4.17.21 --save-exact
# 或者使用简写
npm install lodash@4.17.21 -E
```

### 卸载包

从项目中卸载包：

```bash
npm uninstall lodash
# 或者使用简写
npm un lodash
npm remove lodash
npm rm lodash
```

### 卸载全局包

卸载全局安装的包：

```bash
npm uninstall -g <package-name>
```

### 卸载开发依赖

卸载开发依赖：

```bash
npm uninstall jest --save-dev
```

## 2.2 全局包与本地包

### 本地包

本地包是安装在项目`node_modules`目录中的包，只对当前项目可用。

**特点：**
- 安装在项目的`node_modules`目录
- 在`package.json`中记录依赖关系
- 项目间版本隔离
- 便于项目协作和部署

**安装本地包：**
```bash
npm install <package-name>
```

### 全局包

全局包是安装在系统全局位置的包，可以在系统的任何位置使用。

**特点：**
- 安装在全局目录
- 可以在任何项目中使用
- 通常用于命令行工具
- 所有项目共享同一版本

**查看全局安装目录：**
```bash
npm config get prefix
```

**安装全局包：**
```bash
npm install -g <package-name>
npm install --global <package-name>
```

**查看已安装的全局包：**
```bash
npm list -g --depth=0
```

### 全局包与本地包的选择

**使用全局包的场景：**
- 命令行工具（如`create-react-app`, `vue-cli`）
- 开发工具（如`nodemon`, `typescript`）
- 系统级工具（如`http-server`）

**使用本地包的场景：**
- 项目依赖库（如`react`, `express`）
- 项目特定的工具
- 需要版本控制的依赖

### 使用npx运行本地包

`npx`允许运行本地安装的包而无需全局安装：

```bash
# 运行本地安装的create-react-app
npx create-react-app my-app

# 运行特定版本的包
npx lodash@4.17.21

# 运行GitHub上的包
npx github:user/repo
```

## 2.3 包的更新与版本控制

### 检查过时的包

检查项目中哪些包有过时的版本：

```bash
npm outdated
```

输出示例：
```
Package  Current  Wanted  Latest  Location
lodash    4.16.0  4.17.21  4.17.21  my-project
express   4.16.0  4.17.1   4.18.2   my-project
```

- **Current**：当前安装的版本
- **Wanted**：符合package.json中版本范围的最新版本
- **Latest**：包的最新版本

### 更新包

更新单个包到符合版本范围的最新版本：

```bash
npm update lodash
```

更新所有包：

```bash
npm update
```

### 更新到最新版本

使用`npm-check-updates`工具更新到最新版本：

1. 安装工具：
```bash
npm install -g npm-check-updates
```

2. 检查并更新package.json：
```bash
ncu
```

3. 应用更新：
```bash
ncu -u
npm install
```

### 版本控制

#### 语义化版本控制（SemVer）

版本号格式：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

#### 版本范围

- `*` 或 `x`：匹配任何版本
- `1.x`：匹配1.x.x的最新版本
- `1.2.x`：匹配1.2.x的最新版本
- `~1.2.3`：匹配>=1.2.3且<1.3.0的版本
- `^1.2.3`：匹配>=1.2.3且<2.0.0的版本
- `>=1.2.3`：匹配>=1.2.3的版本
- `<=1.2.3`：匹配<=1.2.3的版本
- `>1.2.3`：匹配>1.2.3的版本
- `<1.2.3`：匹配<1.2.3的版本
- `1.2.3 - 2.3.4`：匹配>=1.2.3且<=2.3.4的版本
- `1.2.3 || 2.3.4`：匹配1.2.3或2.3.4的版本

#### package-lock.json

`package-lock.json`文件记录了每个依赖的确切版本，确保团队成员安装相同的依赖：

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "": {
      "name": "my-project",
      "version": "1.0.0",
      "dependencies": {
        "lodash": "^4.17.21"
      }
    },
    "node_modules/lodash": {
      "version": "4.17.21",
      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
      "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg=="
    }
  }
}
```

## 2.4 包的搜索与信息查看

### 搜索包

在NPM注册表中搜索包：

```bash
npm search <keyword>
# 或者使用简写
npm s <keyword>
```

搜索JavaScript相关的包：
```bash
npm search javascript
```

搜索结果包含：
- 包名
- 描述
- 作者
- 发布日期
- 关键词
- 维护者

### 查看包信息

查看包的基本信息：

```bash
npm info <package-name>
# 或者使用简写
npm view <package-name>
```

查看包的特定字段：
```bash
npm view <package-name> version
npm view <package-name> description
npm view <package-name> dependencies
npm view <package-name> homepage
npm view <package-name> repository
```

查看包的版本历史：
```bash
npm view <package-name> versions
```

查看包的发布时间：
```bash
npm view <package-name> time
```

### 查看已安装的包

查看当前项目的依赖树：
```bash
npm list
# 或者使用简写
npm ls
```

限制显示深度：
```bash
npm list --depth=0
```

查看全局安装的包：
```bash
npm list -g
npm list -g --depth=0
```

查看特定包的信息：
```bash
npm list lodash
```

### 检查包的完整性

验证已安装包的完整性：
```bash
npm verify
```

## 2.5 常用命令详解

### npm init

初始化一个新的NPM项目：

```bash
npm init          # 交互式初始化
npm init -y       # 使用默认值快速初始化
npm init --yes    # 同上
```

### npm install

安装包的多种方式：

```bash
# 安装最新版本
npm install <package>

# 安装特定版本
npm install <package>@<version>

# 安装开发依赖
npm install <package> --save-dev

# 安装全局包
npm install <package> --global

# 安装并保存精确版本
npm install <package> --save-exact

# 从GitHub安装
npm install <username>/<repository>
npm install git+https://github.com/<username>/<repository>.git

# 从本地目录安装
npm install ./local-package

# 从tarball安装
npm install ./package.tgz
```

### npm uninstall

卸载包：

```bash
npm uninstall <package>
npm uninstall <package> --save-dev
npm uninstall -g <package>
```

### npm update

更新包：

```bash
npm update          # 更新所有包
npm update <package>  # 更新特定包
npm update -g       # 更新全局包
```

### npm run

运行package.json中定义的脚本：

```bash
npm run <script-name>
npm run start       # 运行start脚本
npm run test        # 运行test脚本
npm run build       # 运行build脚本
```

### npm test

运行测试脚本（等同于`npm run test`）：

```bash
npm test
```

### npm start

启动应用程序（等同于`npm run start`）：

```bash
npm start
```

### npm stop

停止应用程序（等同于`npm run stop`）：

```bash
npm stop
```

### npm restart

重启应用程序（等同于`npm run restart`）：

```bash
npm restart
```

### npm config

配置NPM设置：

```bash
npm config list                    # 查看所有配置
npm config get <key>               # 获取特定配置
npm config set <key> <value>       # 设置配置
npm config delete <key>            # 删除配置
npm config edit                    # 编辑配置文件
```

### npm cache

管理NPM缓存：

```bash
npm cache verify                   # 验证缓存
npm cache clean                    # 清除缓存
npm cache add <tarball-url>        # 添加包到缓存
```

### npm doctor

检查NPM环境的常见问题：

```bash
npm doctor
```

### npm audit

检查安全漏洞：

```bash
npm audit                          # 检查安全漏洞
npm audit fix                      # 自动修复漏洞
npm audit fix --force              # 强制修复漏洞（可能破坏性更改）
```

### npm publish

发布包到NPM注册表：

```bash
npm publish                        # 发布包
npm publish --tag beta             # 发布为beta版本
npm publish --access public        # 发布为公共包
npm publish --access restricted    # 发布为受限包
```

### npm deprecate

弃用包的特定版本：

```bash
npm deprecate <package>@<version> "<message>"
```

### npm star

为包添加星标：

```bash
npm star <package>
```

### npm stars

查看你加星标的包：

```bash
npm stars
```

### npm access

管理包的访问权限：

```bash
npm access list packages           # 列出你有权限访问的包
npm access list collaborators      # 列出协作者
npm access add <user>             # 添加协作者
npm access rm <user>              # 移除协作者
```

### npm team

管理团队：

```bash
npm team create <scope:team>       # 创建团队
npm team add <scope:team> <user>   # 添加用户到团队
npm team rm <scope:team> <user>    # 从团队移除用户
```

## 2.6 实践练习

### 练习1：包的安装与管理

1. 创建一个新项目并初始化
2. 安装lodash作为生产依赖
3. 安装jest作为开发依赖
4. 查看已安装的包
5. 卸载lodash
6. 重新安装lodash的特定版本

**步骤：**

```bash
mkdir package-management-practice
cd package-management-practice
npm init -y
npm install lodash
npm install jest --save-dev
npm list --depth=0
npm uninstall lodash
npm install lodash@4.17.21
```

### 练习2：版本控制

1. 检查项目中过时的包
2. 更新所有包到最新兼容版本
3. 查看package-lock.json文件
4. 理解版本范围符号

**步骤：**

```bash
npm outdated
npm update
cat package-lock.json
```

### 练习3：全局包管理

1. 安装一个全局包（如http-server）
2. 使用全局包启动一个简单的HTTP服务器
3. 查看已安装的全局包
4. 卸载全局包

**步骤：**

```bash
npm install -g http-server
http-server
npm list -g --depth=0
npm uninstall -g http-server
```

### 练习4：包搜索与信息查看

1. 搜索与"date"相关的包
2. 查看moment包的详细信息
3. 查看moment包的版本历史
4. 查看moment包的依赖关系

**步骤：**

```bash
npm search date
npm view moment
npm view moment versions
npm view moment dependencies
```

## 2.7 常见问题与解决方案

### 问题1：安装速度慢

**解决方案：**

1. 使用国内镜像源：

```bash
npm config set registry https://registry.npmmirror.com
```

2. 使用cnpm：

```bash
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install <package>
```

3. 使用yarn：

```bash
npm install -g yarn
yarn install
```

### 问题2：权限错误（Linux/macOS）

**解决方案：**

1. 使用nvm管理Node.js版本
2. 修改npm全局目录权限：

```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 问题3：依赖冲突

**解决方案：**

1. 删除`node_modules`和`package-lock.json`
2. 清除NPM缓存：

```bash
npm cache clean --force
```

3. 重新安装依赖：

```bash
npm install
```

### 问题4：node-gyp编译错误

**解决方案：**

1. 安装编译工具：

**Windows:**

```bash
npm install -g windows-build-tools
```

**macOS:**

```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install build-essential
```

2. 使用预编译的二进制文件：

```bash
npm install <package> --ignore-scripts
```

## 2.8 总结

本章详细介绍了NPM的包管理和基本命令，包括：

1. 包的安装与卸载方法
2. 全局包与本地包的区别和使用场景
3. 包的更新与版本控制
4. 包的搜索与信息查看
5. 常用NPM命令的详细说明
6. 实践练习和常见问题解决

通过本章的学习，你应该能够：

- 熟练安装、更新和卸载NPM包
- 理解全局包与本地包的区别
- 掌握版本控制和语义化版本
- 使用NPM命令搜索和查看包信息
- 解决常见的包管理问题

在下一章中，我们将深入学习`package.json`文件的详细配置和最佳实践。