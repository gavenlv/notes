# 第3章：Vite插件系统与高级配置

## 3.1 插件系统概述

### 3.1.1 插件系统架构

Vite的插件系统是基于Rollup插件API设计的，但增加了一些Vite特有的钩子。这种设计使Vite能够在开发和构建阶段实现灵活的扩展。

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Vite核心       │      │  Vite插件系统   │      │  Rollup插件系统 │
│                 │──────▶                 │──────▶                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                       │                        │
        ▼                       ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 开发服务器钩子   │      │ 构建钩子        │      │ 模块转换钩子     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### 3.1.2 插件工作流程

Vite插件在不同阶段执行不同的钩子函数：

1. **配置阶段**：修改Vite配置
2. **开发服务器阶段**：处理开发服务器相关逻辑
3. **构建阶段**：参与Rollup构建过程
4. **模块转换阶段**：处理和转换文件内容

### 3.1.3 插件执行顺序

Vite按以下规则确定插件执行顺序：

1. 按配置中插件数组的顺序执行
2. 相同钩子函数按`enforce`属性排序：
   - `pre`：在Vite核心插件之前执行
   - `normal`：默认，在Vite核心插件之后执行
   - `post`：在所有插件之后执行

## 3.2 常用内置插件

### 3.2.1 模块预热插件

Vite内置了模块预热插件，用于在开发服务器启动时预编译常用模块，提高首次加载性能。

```javascript
// vite.config.js
export default {
  server: {
    warmup: {
      clientFiles: [
        './src/components/*.vue',
        './src/utils/*.js'
      ]
    }
  }
}
```

### 3.2.2 依赖优化插件

自动处理和优化第三方依赖，将CommonJS/UMD格式转换为ESM格式。

```javascript
// vite.config.js
export default {
  optimizeDeps: {
    include: ['lodash-es', 'date-fns'],
    exclude: ['不需要优化的依赖'],
    esbuildOptions: {
      // 自定义esbuild配置
      plugins: [
        // esbuild插件
      ]
    }
  }
}
```

### 3.2.3 静态资源插件

处理各种静态资源文件，包括图片、字体、JSON等。

```javascript
// vite.config.js
export default {
  assetsInclude: ['**/*.gltf', '**/*.fbx'] // 添加额外的资源类型
}
```

## 3.3 常用社区插件

### 3.3.1 Vue支持插件

为Vue单文件组件提供编译支持。

```bash
npm install @vitejs/plugin-vue -D
```

```javascript
// vite.config.js
import vue from '@vitejs/plugin-vue'

export default {
  plugins: [vue()]
}
```

### 3.3.2 React支持插件

为React提供Fast Refresh等功能。

```bash
npm install @vitejs/plugin-react -D
```

```javascript
// vite.config.js
import react from '@vitejs/plugin-react'

export default {
  plugins: [react()]
}
```

### 3.3.3 路径别名插件

提供更灵活的路径别名功能。

```bash
npm install vite-aliases -D
```

```javascript
// vite.config.js
import { ViteAliases } from 'vite-aliases'

export default {
  plugins: [ViteAliases()]
}
```

### 3.3.4 组件自动导入插件

自动导入Vue/React组件。

```bash
npm install unplugin-vue-components -D  # Vue版本
npm install unplugin-auto-import -D     # 自动导入API
```

```javascript
// vite.config.js
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'

export default {
  plugins: [
    Components({
      dirs: ['src/components'],
      extensions: ['vue']
    }),
    AutoImport({
      imports: ['vue', 'vue-router']
    })
  ]
}
```

### 3.3.5 SVG处理插件

将SVG文件转换为组件或内联使用。

```bash
npm install vite-plugin-svg-icons -D
```

```javascript
// vite.config.js
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import path from 'path'

export default {
  plugins: [
    createSvgIconsPlugin({
      iconDirs: [path.resolve(process.cwd(), 'src/icons')],
      symbolId: 'icon-[dir]-[name]'
    })
  ]
}
```

## 3.4 自定义插件开发

### 3.4.1 插件基本结构

Vite插件是一个具有特定属性和钩子函数的对象：

```javascript
// 简单插件示例
function myPlugin(options = {}) {
  return {
    name: 'my-plugin', // 插件名称，必需
    enforce: 'pre',   // 执行顺序：'pre' | 'normal' | 'post'
    // 插件钩子
    config(config, { command, mode }) {
      // 修改配置
      return {
        resolve: { alias: { '@': '/src' } }
      }
    },
    // 其他钩子...
  }
}

export default myPlugin
```

### 3.4.2 Vite特有钩子

#### 3.4.2.1 配置钩子

```javascript
function myPlugin() {
  return {
    name: 'my-plugin',
    // 在解析配置前调用
    config(config, { command, mode }) {
      return { /* 返回修改的配置 */ }
    },
    // 在配置解析后调用
    configResolved(resolvedConfig) {
      // 使用解析后的配置
      console.log(resolvedConfig)
    }
  }
}
```

#### 3.4.2.2 开发服务器钩子

```javascript
function myPlugin() {
  return {
    name: 'my-plugin',
    // 开发服务器配置钩子
    configureServer(server) {
      // 添加中间件
      server.middlewares.use((req, res, next) => {
        // 自定义中间件逻辑
        next()
      })
      // 服务器已准备就绪
      server.httpServer.once('listening', () => {
        console.log('服务器已启动')
      })
    },
    // 转换HTML
    transformIndexHtml(html) {
      return html.replace('\u003ctitle\u003e', '\u003ctitle\u003eMy App - ')
    }
  }
}
```

#### 3.4.2.3 模块转换钩子

```javascript
function myPlugin() {
  return {
    name: 'my-plugin',
    // 转换模块内容
    transform(code, id) {
      // id是文件路径
      if (id.endsWith('.js')) {
        // 转换JavaScript文件
        return code.replace('console.log', 'console.warn')
      }
    },
    // 解析文件路径
    resolveId(source, importer) {
      if (source === 'virtual-module') {
        // 返回虚拟模块ID
        return source
      }
    },
    // 加载模块内容
    load(id) {
      if (id === 'virtual-module') {
        // 返回虚拟模块内容
        return 'export const hello = "Hello from virtual module!"'
      }
    }
  }
}
```

### 3.4.3 插件生命周期

Vite插件的典型生命周期如下：

1. **初始化**：插件被加载
2. **配置阶段**：`config`和`configResolved`钩子被调用
3. **开发服务器启动**（开发模式）：`configureServer`钩子被调用
4. **模块处理**：`resolveId`、`load`、`transform`等钩子处理模块
5. **构建**（生产模式）：Rollup钩子参与构建过程
6. **清理**：`closeBundle`钩子执行清理工作

## 3.5 开发一个简单的Vite插件

### 3.5.1 插件需求分析

假设我们需要开发一个插件，为JavaScript文件添加版权信息注释。

### 3.5.2 插件实现

创建一个名为`vite-plugin-copyright`的插件：

```javascript
// vite-plugin-copyright.js
function copyrightPlugin(options = {}) {
  const defaultOptions = {
    author: 'Unknown',
    year: new Date().getFullYear(),
    pattern: /\.(js|ts|jsx|tsx)$/
  }
  
  const opts = { ...defaultOptions, ...options }
  const banner = `/**
 * @author ${opts.author}
 * @copyright © ${opts.year}
 */\n`
  
  return {
    name: 'vite-plugin-copyright',
    transform(code, id) {
      if (opts.pattern.test(id)) {
        // 检查是否已经有版权信息
        if (!/\*\s*@copyright/.test(code)) {
          return banner + code
        }
      }
      return null
    }
  }
}

export default copyrightPlugin
```

### 3.5.3 使用自定义插件

在Vite配置中使用我们的插件：

```javascript
// vite.config.js
import copyrightPlugin from './vite-plugin-copyright.js'

export default {
  plugins: [
    copyrightPlugin({
      author: 'Vite User',
      year: '2023'
    })
  ]
}
```

## 3.6 高级配置技巧

### 3.6.1 条件配置

根据环境或命令配置不同的选项：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig(({ command, mode }) => {
  const isDev = command === 'serve'
  const isProd = command === 'build'
  
  return {
    // 通用配置
    plugins: [
      // 根据环境加载不同插件
      isDev && require('vite-plugin-inspect')(),
      isProd && require('vite-plugin-minify')()
    ].filter(Boolean),
    
    // 开发环境配置
    server: isDev ? {
      port: 3000,
      open: true,
      hmr: true
    } : undefined,
    
    // 生产环境配置
    build: isProd ? {
      minify: 'terser',
      sourcemap: false
    } : undefined
  }
})
```

### 3.6.2 多页面应用配置

配置Vite支持多个HTML入口：

```javascript
// vite.config.js
import { resolve } from 'path'

export default {
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin/index.html'),
        user: resolve(__dirname, 'user/index.html')
      },
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]'
      }
    }
  }
}
```

### 3.6.3 深度集成Rollup

自定义Rollup构建配置：

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import { visualizer } from 'rollup-plugin-visualizer'
import { terser } from 'rollup-plugin-terser'

export default defineConfig({
  build: {
    rollupOptions: {
      plugins: [
        // 添加Rollup插件
        visualizer({
          filename: './stats.html',
          gzipSize: true,
          brotliSize: true
        }),
        terser({
          compress: {
            drop_console: true,
            drop_debugger: true
          }
        })
      ],
      // 自定义输出配置
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          common: ['lodash-es', 'axios'],
          ui: ['ant-design-vue']
        }
      }
    }
  }
})
```

### 3.6.4 环境特定配置文件

可以创建针对特定环境的配置文件：

- `vite.config.js`：默认配置
- `vite.config.production.js`：生产环境配置
- `vite.config.development.js`：开发环境配置
- `vite.config.ci.js`：CI环境配置

然后在命令中使用特定配置文件：

```bash
vite build --config vite.config.production.js
```

## 3.7 高级插件组合

### 3.7.1 创建插件集合

将多个常用插件组合成一个插件集合，便于复用：

```javascript
// vite-plugins.js
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { ViteAliases } from 'vite-aliases'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import path from 'path'

export function createVuePlugins() {
  return [
    vue(),
    ViteAliases(),
    Components({
      dirs: ['src/components'],
      extensions: ['vue'],
      dts: 'src/components.d.ts'
    }),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts'
    }),
    createSvgIconsPlugin({
      iconDirs: [path.resolve(process.cwd(), 'src/icons')],
      symbolId: 'icon-[dir]-[name]'
    })
  ]
}
```

在配置中使用：

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import { createVuePlugins } from './vite-plugins.js'

export default defineConfig({
  plugins: [...createVuePlugins()]
})
```

### 3.7.2 插件优先级管理

合理设置插件的执行顺序：

```javascript
// vite.config.js
export default {
  plugins: [
    // 预处理插件，在核心插件前执行
    {
      name: 'pre-plugin',
      enforce: 'pre',
      transform(code, id) {
        // 预处理代码
      }
    },
    
    // 核心插件，默认顺序
    vue(),
    
    // 后处理插件，在所有插件后执行
    {
      name: 'post-plugin',
      enforce: 'post',
      transform(code, id) {
        // 后处理代码
      }
    }
  ]
}
```

## 3.8 实验：开发自定义Vite插件

### 3.8.1 实验目标

开发一个简单的Vite插件，用于在构建时生成版本信息文件。

### 3.8.2 实验步骤

1. **创建插件文件**
   ```bash
   mkdir -p plugins
   touch plugins/vite-plugin-version.js
   ```

2. **实现插件功能**
   ```javascript
   // plugins/vite-plugin-version.js
   import fs from 'fs'
   import path from 'path'
   
   function versionPlugin(options = {}) {
     const defaultOptions = {
       outputPath: 'version.json',
       version: process.env.npm_package_version || '1.0.0',
       includeBuildDate: true
     }
     
     const opts = { ...defaultOptions, ...options }
     
     return {
       name: 'vite-plugin-version',
       generateBundle(outputOptions, bundle) {
         // 构建时生成版本信息
         const versionInfo = {
           version: opts.version,
           buildDate: opts.includeBuildDate ? new Date().toISOString() : undefined
         }
         
         // 添加到输出文件
         this.emitFile({
           type: 'asset',
           fileName: opts.outputPath,
           source: JSON.stringify(versionInfo, null, 2)
         })
       }
     }
   }
   
   export default versionPlugin
   ```

3. **创建测试项目**
   ```bash
   mkdir -p version-demo
   cd version-demo
   npm create vite@latest . -- --template vanilla
   npm install
   ```

4. **配置插件**
   ```javascript
   // version-demo/vite.config.js
   import { defineConfig } from 'vite'
   import versionPlugin from '../plugins/vite-plugin-version.js'
   
   export default defineConfig({
     plugins: [
       versionPlugin({
         outputPath: 'assets/version.json'
       })
     ]
   })
   ```

5. **构建项目**
   ```bash
   npm run build
   ```

6. **验证结果**
   检查`dist/assets/version.json`文件是否生成，内容是否包含版本信息和构建日期。

## 3.9 插件系统最佳实践

### 3.9.1 插件开发最佳实践

1. **命名规范**：使用`vite-plugin-`前缀命名插件
2. **明确的API**：提供清晰的配置选项和文档
3. **错误处理**：妥善处理可能的错误情况
4. **性能优化**：避免不必要的转换和计算
5. **类型支持**：提供TypeScript类型定义
6. **测试覆盖**：编写单元测试确保插件稳定性

### 3.9.2 插件使用建议

1. **按需使用**：只使用必要的插件，避免性能开销
2. **插件顺序**：注意插件的执行顺序，避免冲突
3. **版本锁定**：锁定插件版本，避免兼容性问题
4. **社区插件**：优先使用成熟的社区插件，而非自行开发
5. **定期更新**：定期更新插件到最新版本

## 3.10 本章小结

在本章中，我们深入学习了Vite的插件系统和高级配置技巧。Vite的插件系统为开发者提供了极大的灵活性，可以通过插件扩展Vite的功能，适应各种开发场景。

关键要点：
- Vite插件系统基于Rollup插件API，但增加了Vite特有钩子
- 了解插件的执行顺序和生命周期对于插件开发至关重要
- 可以通过自定义插件来扩展Vite的功能，满足特定需求
- 高级配置技巧如条件配置、多页面应用配置等可以提升开发体验
- 合理使用插件和配置可以显著提高开发效率和构建性能

在下一章中，我们将学习Vite的性能优化技巧和最佳实践，进一步提升项目性能。