# 第1章：Vite基础入门及环境搭建

## 1.1 Vite简介与优势

### 1.1.1 什么是Vite？

Vite（发音为"veet"，意为快速的）是一种现代前端构建工具，由Vue.js的创始人尤雨溪开发，旨在提供极速的开发体验。它通过利用浏览器原生的ES模块支持，实现了近乎即时的开发服务器启动和热模块替换（HMR）。

### 1.1.2 Vite与传统构建工具的对比

**传统构建工具（如Webpack）的工作流程**：
1. 启动开发服务器时，需要先构建整个应用，将所有模块打包
2. 即使只修改了一个文件，也需要重新构建或进行复杂的缓存策略
3. 随着项目规模增长，启动时间和热更新时间会显著增加

**Vite的创新工作流程**：
1. **开发环境**：利用浏览器对ES模块的原生支持，在请求时才按需编译模块
2. **生产环境**：使用Rollup进行高效的构建优化
3. **依赖预构建**：在启动时预构建第三方依赖，提高开发性能

### 1.1.3 Vite的核心优势

1. **极速的开发服务器启动**：无需等待打包，即时启动
2. **极速的热模块替换（HMR）**：几乎实时的代码更新反馈
3. **按需编译**：只有在请求时才编译代码，提高开发效率
4. **优化的构建输出**：利用Rollup生成优化的生产构建
5. **原生ESM支持**：使用现代浏览器特性
6. **丰富的插件生态**：与Rollup插件兼容，同时有Vite专用插件
7. **TypeScript支持**：开箱即用的TypeScript集成
8. **CSS处理**：支持CSS Modules、PostCSS等

## 1.2 环境要求与安装

### 1.2.1 系统要求

在开始使用Vite之前，你需要确保系统满足以下要求：

- **Node.js版本**：18.0或更高版本
- **包管理器**：npm、yarn或pnpm

### 1.2.2 检查Node.js版本

首先，让我们检查你的Node.js版本：

```bash
# 检查Node.js版本
node -v

# 检查npm版本
npm -v
```

如果你的Node.js版本低于18.0，建议升级到最新的LTS版本。你可以使用[nvm（Node Version Manager）](https://github.com/nvm-sh/nvm)来管理多个Node.js版本。

### 1.2.3 安装Vite

Vite本身不需要全局安装，因为我们通常通过项目模板来创建Vite项目。但如果你想全局安装Vite CLI工具，可以使用以下命令：

```bash
# 使用npm全局安装
npm install -g vite

# 使用yarn全局安装
yarn global add vite

# 使用pnpm全局安装
pnpm add -g vite
```

## 1.3 创建第一个Vite项目

### 1.3.1 使用npm创建项目

Vite提供了多种方式来创建新项目，最简单的方法是使用npm的`create vite`命令：

```bash
# 在当前目录创建项目
npm create vite@latest . -- --template vue

# 创建到指定目录
npm create vite@latest my-vite-project -- --template vue
```

### 1.3.2 支持的模板

Vite支持多种框架模板，包括：

- **vanilla**：纯JavaScript项目
- **vanilla-ts**：TypeScript项目
- **vue**：Vue.js项目
- **vue-ts**：Vue.js + TypeScript项目
- **react**：React项目
- **react-ts**：React + TypeScript项目
- **preact**：Preact项目
- **preact-ts**：Preact + TypeScript项目
- **lit**：Lit项目
- **lit-ts**：Lit + TypeScript项目
- **svelte**：Svelte项目
- **svelte-ts**：Svelte + TypeScript项目

### 1.3.3 交互式创建

如果你不想在命令行中指定模板，可以使用交互式方式创建：

```bash
# 交互式创建项目
npm create vite@latest
```

然后按照提示选择：
1. 项目名称
2. 框架选择
3. 变体（如是否使用TypeScript）

### 1.3.4 安装依赖并启动开发服务器

创建项目后，进入项目目录，安装依赖并启动开发服务器：

```bash
# 进入项目目录
cd my-vite-project

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动后，你可以在浏览器中访问`http://localhost:5173/`查看你的项目。

## 1.4 项目结构解析

### 1.4.1 基本项目结构

创建一个Vue项目后，典型的Vite项目结构如下：

```
my-vite-project/
├── node_modules/       # 依赖包
├── public/             # 静态资源目录
│   └── vite.svg        # Vite默认Logo
├── src/                # 源代码目录
│   ├── assets/         # 项目资源文件
│   │   └── vue.svg     # Vue Logo
│   ├── components/     # Vue组件
│   │   └── HelloWorld.vue
│   ├── App.vue         # 根组件
│   ├── main.js         # 入口文件
│   └── style.css       # 全局样式
├── .gitignore          # Git忽略配置
├── index.html          # HTML入口
├── package.json        # 项目配置和依赖
├── README.md           # 项目说明
└── vite.config.js      # Vite配置文件
```

### 1.4.2 关键文件说明

1. **index.html**：HTML入口文件
   - 与传统构建工具不同，Vite将`index.html`放在项目根目录，而不是`public`文件夹中
   - Vite将`index.html`视为源码和模块图的一部分
   - 可以在HTML中直接引用源码模块

2. **src/main.js**：JavaScript入口文件
   - 负责初始化应用并挂载到DOM
   - 导入全局样式和主要组件

3. **vite.config.js**：Vite配置文件
   - 使用JavaScript配置Vite的行为
   - 可以配置插件、代理、构建选项等

4. **package.json**：项目配置文件
   - 定义项目依赖、脚本命令等

5. **public/**：静态资源目录
   - 放置不需要经过Vite处理的静态资源
   - 这些文件会被直接复制到构建输出目录

### 1.4.3 HTML与模块的关系

在Vite中，`index.html`是连接JavaScript模块的入口点：

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite App</title>
  </head>
  <body>
    <div id="app"></div>
    <!-- 直接引用JavaScript模块 -->
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

注意这里使用了`type="module"`属性，这表明该脚本是一个ES模块。

## 1.5 基本命令与使用

### 1.5.1 npm脚本命令

Vite项目默认包含以下npm脚本：

```json
{
  "scripts": {
    "dev": "vite",          // 启动开发服务器
    "build": "vite build",  // 构建生产版本
    "preview": "vite preview" // 预览生产构建
  }
}
```

### 1.5.2 开发服务器命令

```bash
# 启动开发服务器
npm run dev

# 指定端口
npm run dev -- --port 3000

# 启用HTTPS
npm run dev -- --https

# 自动打开浏览器
npm run dev -- --open
```

### 1.5.3 构建命令

```bash
# 构建生产版本
npm run build

# 指定构建环境
npm run build -- --mode production
npm run build -- --mode development

# 构建并分析包大小
npm run build -- --report
```

### 1.5.4 预览命令

构建生产版本后，可以使用预览命令在本地测试：

```bash
# 预览生产构建
npm run preview

# 指定预览端口
npm run preview -- --port 8080
```

## 1.6 实验：创建你的第一个Vite项目

### 1.6.1 实验目标

通过实际操作，创建一个基本的Vite项目，并理解其工作原理。

### 1.6.2 实验步骤

1. **创建项目**
   ```bash
   # 创建一个Vue项目
   npm create vite@latest vite-demo -- --template vue
   ```

2. **查看项目结构**
   ```bash
   cd vite-demo
   ls -la
   ```

3. **安装依赖**
   ```bash
   npm install
   ```

4. **启动开发服务器**
   ```bash
   npm run dev
   ```

5. **修改代码，体验热更新**
   - 打开`src/App.vue`文件
   - 修改一些文本内容，观察浏览器的变化

6. **构建生产版本**
   ```bash
   npm run build
   ```

7. **预览生产构建**
   ```bash
   npm run preview
   ```

### 1.6.3 实验观察

- 开发服务器启动速度有多快？
- 热更新反应有多迅速？
- 生产构建输出了什么文件？

## 1.7 常见问题与解决方案

### 1.7.1 端口被占用

**问题**：启动开发服务器时提示端口被占用。

**解决方案**：
```bash
# 使用不同的端口
npm run dev -- --port 3001
```

### 1.7.2 浏览器兼容性问题

**问题**：在较旧的浏览器中无法运行。

**解决方案**：
- 安装`@vitejs/plugin-legacy`插件
- 配置polyfills支持旧浏览器

### 1.7.3 依赖安装失败

**问题**：npm install 失败。

**解决方案**：
- 检查网络连接
- 清除npm缓存：`npm cache clean --force`
- 尝试使用yarn或pnpm：`yarn install` 或 `pnpm install`

## 1.8 本章小结

在本章中，我们介绍了Vite的基本概念、优势、安装方法和项目创建流程。Vite作为一种现代前端构建工具，通过利用浏览器原生的ES模块支持，提供了极速的开发体验。

关键要点：
- Vite在开发环境中使用原生ESM，实现快速的服务器启动和热更新
- 创建Vite项目可以使用模板或交互式方式
- Vite项目结构清晰，主要配置文件是`vite.config.js`
- 基本命令包括开发、构建和预览

在下一章中，我们将深入学习Vite的核心功能和配置选项，进一步掌握Vite的使用技巧。