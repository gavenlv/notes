# 第2章：Vite核心功能与配置

## 2.1 开发服务器特性

### 2.1.1 即时服务器启动

Vite开发服务器的最大特点是启动速度极快。传统的构建工具需要在启动时处理和打包所有模块，而Vite采用了完全不同的方法：

1. **按需编译**：只有当浏览器请求某个模块时，Vite才会编译它
2. **依赖预构建**：在启动时只预构建第三方依赖，不处理应用代码
3. **原生ESM支持**：利用浏览器的ES模块功能，直接加载源码模块

这种方式使得即使是大型项目，Vite开发服务器也能在几秒钟内启动完成。

### 2.1.2 热模块替换（HMR）

热模块替换是开发过程中的关键特性，Vite的HMR实现具有以下优势：

1. **极速响应**：几乎实时的模块更新，无需刷新整个页面
2. **精确更新**：只更新修改的模块，保留应用状态
3. **框架感知**：与主流框架（Vue、React等）深度集成
4. **CSS热更新**：样式修改会立即生效，无需刷新页面

#### 2.1.2.1 HMR工作原理

```
┌─────────────┐      修改      ┌──────────────┐      检测变化     ┌──────────────┐
│ 开发者修改代码 │───────────→ │ 文件系统变化 │──────────────→ │ Vite开发服务器 │
└─────────────┘               └──────────────┘                 └────────┬─────┘
                                                                       │
                                                                       ▼
┌──────────────┐      推送更新     ┌──────────────┐      应用更新     ┌──────────────┐
│ 浏览器接收更新 │←────────────── │ WebSocket连接 │←────────────── │ 编译更新模块 │
└──────────────┘                  └──────────────┘                 └──────────────┘
```

### 2.1.3 模块热替换API

Vite提供了HMR API，允许你在应用中处理热更新：

```javascript
// 监听模块更新
if (import.meta.hot) {
  import.meta.hot.accept('./some-module.js', (newModule) => {
    // 处理模块更新
    console.log('模块已更新', newModule);
  });

  // 当模块需要完全替换时
  import.meta.hot.dispose(() => {
    // 清理副作用
  });
}
```

### 2.1.4 开发服务器配置选项

在`vite.config.js`中可以配置开发服务器：

```javascript
// vite.config.js
export default {
  server: {
    port: 3000,           // 服务器端口
    open: true,           // 自动打开浏览器
    https: false,         // 是否启用HTTPS
    cors: true,           // 启用CORS
    host: '0.0.0.0',      // 监听所有主机
    strictPort: true,     // 端口被占用时退出
    hmr: {
      overlay: true,      // 错误时显示全屏覆盖层
      clientPort: 24678   // WebSocket客户端端口
    },
    // 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
}
```

## 2.2 配置文件详解

### 2.2.1 配置文件类型

Vite支持多种格式的配置文件：

1. **JavaScript配置**：`vite.config.js`
2. **TypeScript配置**：`vite.config.ts`
3. **ESM配置**：使用ES模块语法导出配置
4. **CommonJS配置**：使用`module.exports`导出配置

推荐使用ES模块语法的JavaScript配置文件，简单直接：

```javascript
// vite.config.js
export default {
  // 配置选项
}
```

### 2.2.2 基本配置选项

#### 2.2.2.1 项目根目录

```javascript
export default {
  root: './src'  // 指定项目根目录
}
```

#### 2.2.2.2 构建输出目录

```javascript
export default {
  build: {
    outDir: 'dist',    // 输出目录
    assetsDir: 'assets' // 静态资源目录
  }
}
```

#### 2.2.2.3 静态资源处理

```javascript
export default {
  publicDir: 'public',  // 静态资源目录
  assetsInclude: ['**/*.gltf']  // 额外的静态资源类型
}
```

#### 2.2.2.4 解析选项

```javascript
export default {
  resolve: {
    alias: {
      '@': '/src',              // 路径别名
      'components': '/src/components'
    },
    extensions: ['.js', '.ts', '.vue', '.jsx', '.tsx']  // 导入时可省略的扩展名
  }
}
```

#### 2.2.2.5 CSS配置

```javascript
export default {
  css: {
    modules: {
      localsConvention: 'camelCase',  // CSS类名转换为驼峰
      scopeBehaviour: 'local'          // 作用域行为
    },
    preprocessorOptions: {
      scss: {
        additionalData: '@import "@/styles/variables.scss";'  // 全局SCSS变量
      }
    }
  }
}
```

### 2.2.3 环境变量配置

#### 2.2.3.1 环境变量文件

Vite支持创建不同环境的配置文件：
- `.env`：所有环境通用
- `.env.local`：所有环境通用，但不会提交到Git
- `.env.development`：开发环境
- `.env.production`：生产环境
- `.env.[mode]`：特定模式的环境变量

#### 2.2.3.2 环境变量使用

在环境变量文件中定义变量：

```
# .env
VITE_APP_TITLE=My Vite App
VITE_API_URL=http://api.example.com
```

在代码中使用：

```javascript
// 在JavaScript中访问环境变量
console.log(import.meta.env.VITE_APP_TITLE);
console.log(import.meta.env.VITE_API_URL);

// 内置环境变量
console.log(import.meta.env.MODE);        // 当前模式\console.log(import.meta.env.BASE_URL);    // 基础URL
console.log(import.meta.env.PROD);        // 是否生产环境
console.log(import.meta.env.DEV);         // 是否开发环境
```

### 2.2.4 多环境配置

可以根据不同的环境创建不同的配置：

```javascript
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig(({ command, mode }) => {
  // command: 'serve' 或 'build'
  // mode: 当前模式（development/production等）
  
  return {
    // 基础配置
    base: mode === 'production' ? '/production/' : '/',
    // 根据环境配置不同选项
    server: command === 'serve' ? {
      port: 3000,
      open: true
    } : undefined,
    build: command === 'build' ? {
      // 构建配置
    } : undefined
  }
})
```

## 2.3 模块解析机制

### 2.3.1 ES模块与原生支持

Vite在开发环境中充分利用浏览器对ES模块的原生支持，这是其性能优势的关键：

1. **浏览器原生ESM**：现代浏览器可以直接加载和解析ES模块（使用`type="module"`的script标签）
2. **请求拦截**：Vite开发服务器拦截浏览器的模块请求，动态编译和返回内容
3. **依赖优化**：第三方依赖会被预构建成ESM格式，提高加载效率

### 2.3.2 路径解析规则

Vite的模块解析遵循以下规则：

1. **绝对路径**：以`/`开头，从项目根目录解析
   ```javascript
   import App from '/src/App.vue'
   ```

2. **相对路径**：以`.`或`..`开头，相对于当前文件解析
   ```javascript
   import Button from './components/Button.vue'
   ```

3. **裸模块导入**：直接导入包名，解析node_modules
   ```javascript
   import { ref } from 'vue'
   ```

4. **别名解析**：使用配置的别名进行解析
   ```javascript
   // 配置了 alias: { '@': '/src' }
   import utils from '@/utils'
   ```

### 2.3.3 依赖预构建

依赖预构建是Vite的重要特性，解决了以下问题：

1. **CommonJS/UMD依赖转换**：将CommonJS或UMD格式的依赖转换为ESM格式
2. **依赖合并**：将多个内部依赖合并为单个模块，减少网络请求
3. **缓存优化**：预构建结果缓存到`node_modules/.vite`目录

#### 2.3.3.1 依赖预构建配置

```javascript
export default {
  optimizeDeps: {
    include: ['lodash-es', 'vue'],  // 强制预构建的依赖
    exclude: ['不需要预构建的依赖'],  // 排除预构建的依赖
    esbuildOptions: {
      // esbuild配置选项
    }
  }
}
```

### 2.3.4 导入类型与解析

#### 2.3.4.1 JavaScript/TypeScript导入

```javascript
// 导入默认导出
import App from './App.vue'

// 导入命名导出
import { ref, computed } from 'vue'

// 导入全部内容
import * as utils from './utils'

// 动态导入
const module = await import('./dynamic.js')
```

#### 2.3.4.2 CSS导入

```javascript
// 导入CSS
import './styles.css'

// 导入CSS模块
import styles from './component.module.css'

// 使用CSS模块
console.log(styles.className)
```

#### 2.3.4.3 静态资源导入

```javascript
// 导入图片
import logo from './logo.png'

// 使用导入的资源
img.src = logo

// 导入JSON
import data from './data.json'

// 导入Worker
import MyWorker from './worker.js?worker'

// 导入WebAssembly
import init from './module.wasm'
```

## 2.4 构建优化基础

### 2.4.1 生产构建配置

```javascript
export default {
  build: {
    target: 'modules',       // 构建目标
    minify: 'esbuild',       // 代码压缩方式
    sourcemap: false,        // 是否生成源码映射
    brotliSize: true,        // 是否计算brotli压缩大小
    chunkSizeWarningLimit: 500, // 代码块大小警告阈值
    cssCodeSplit: true,      // CSS代码分割
    rollupOptions: {
      // Rollup配置
    }
  }
}
```

### 2.4.2 Rollup配置集成

Vite在生产构建中使用Rollup，可以通过`rollupOptions`配置Rollup：

```javascript
export default {
  build: {
    rollupOptions: {
      input: {
        // 多入口配置
        main: resolve(__dirname, 'index.html'),
        nested: resolve(__dirname, 'nested/index.html')
      },
      output: {
        // 输出配置
        manualChunks: {
          // 手动代码分割
          vendor: ['vue', 'vue-router'],
          utils: ['lodash-es']
        }
      }
    }
  }
}
```

### 2.4.3 代码分割策略

代码分割是优化性能的重要手段，可以将代码分割为多个较小的块：

1. **动态导入**：使用`import()`函数进行按需加载
   ```javascript
   // 动态导入组件
   const LazyComponent = () => import('./LazyComponent.vue')
   ```

2. **手动代码分割**：在构建配置中定义
   ```javascript
   // vite.config.js
   export default {
     build: {
       rollupOptions: {
         output: {
           manualChunks: {
             vendor: ['vue'],
             common: ['lodash-es']
           }
         }
       }
     }
   }
   ```

3. **自动代码分割**：基于动态导入自动分割

### 2.4.4 静态资源处理

#### 2.4.4.1 资源类型与内联

```javascript
export default {
  build: {
    assetsInlineLimit: 4096, // 小于4KB的资源会内联
    outDir: 'dist',
    assetsDir: 'assets',
    // 文件命名规则
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js'
      }
    }
  }
}
```

#### 2.4.4.2 资源处理规则

| 资源类型 | 处理方式 | 导入示例 |
|---------|---------|--------|
| 图片 (jpg, png, gif等) | 复制或内联 | `import img from './image.png'` |
| SVG | 转换为组件或URL | `import Icon from './icon.svg'` |
| CSS | 注入到页面或提取为文件 | `import './styles.css'` |
| JSON | 转换为JavaScript | `import data from './data.json'` |
| Web Worker | 转换为Worker | `import Worker from './worker.js?worker'` |
| 字体文件 | 复制到输出目录 | `import font from './font.ttf'` |

## 2.5 实验：配置Vite项目

### 2.5.1 实验目标

通过实际操作，学习如何配置Vite项目，包括基本配置、路径别名、开发服务器等。

### 2.5.2 实验步骤

1. **创建基础项目**
   ```bash
   npm create vite@latest vite-config-demo -- --template vanilla
   cd vite-config-demo
   npm install
   ```

2. **创建配置文件**
   - 创建`vite.config.js`文件
   - 配置基本选项

3. **配置路径别名**
   ```javascript
   // vite.config.js
   import { defineConfig } from 'vite'
   import { resolve } from 'path'
   
   export default defineConfig({
     resolve: {
       alias: {
         '@': resolve(__dirname, 'src')
       }
     }
   })
   ```

4. **创建src目录和文件**
   ```bash
   mkdir -p src/utils
   touch src/main.js
   touch src/utils/helper.js
   ```

5. **编写代码测试别名**
   ```javascript
   // src/utils/helper.js
export const greet = (name) => {
  return `Hello, ${name}!`
}

// src/main.js
import { greet } from '@/utils/helper.js'

console.log(greet('Vite'))
```

6. **修改index.html**
   ```html
   <script type="module" src="/src/main.js"></script>
   ```

7. **启动开发服务器**
   ```bash
   npm run dev
   ```

8. **配置开发服务器代理**
   ```javascript
   // vite.config.js
   export default defineConfig({
     // 其他配置...
     server: {
       proxy: {
         '/api': {
           target: 'http://jsonplaceholder.typicode.com',
           changeOrigin: true,
           rewrite: (path) => path.replace(/^\/api/, '')
         }
       }
     }
   })
   ```

9. **测试代理**
   ```javascript
   // src/main.js
   fetch('/api/todos/1')
     .then(response => response.json())
     .then(data => console.log(data))
   ```

## 2.6 常见配置问题与解决方案

### 2.6.1 路径别名不生效

**问题**：配置了路径别名但在代码中使用时提示找不到模块。

**解决方案**：
- 确保正确配置了resolve.alias
- 如果使用TypeScript，需要同时配置tsconfig.json中的paths

```javascript
// vite.config.js
import { resolve } from 'path'

export default {
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
}

// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### 2.6.2 开发服务器启动慢

**问题**：开发服务器启动时间较长。

**解决方案**：
- 检查依赖预构建是否正确配置
- 排除不需要预构建的依赖
- 清理缓存：删除`node_modules/.vite`目录

### 2.6.3 构建产物过大

**问题**：生产构建后的文件体积过大。

**解决方案**：
- 配置代码分割
- 使用动态导入进行懒加载
- 优化第三方依赖，只导入需要的模块
- 启用压缩和Tree-shaking

## 2.7 本章小结

在本章中，我们深入学习了Vite的核心功能和配置选项。Vite通过其创新的开发服务器实现和灵活的配置系统，为前端开发提供了卓越的体验。

关键要点：
- Vite开发服务器利用原生ESM实现快速启动和热更新
- 配置文件支持多种格式和丰富的配置选项
- 模块解析机制包括绝对路径、相对路径、裸模块和别名等
- 构建优化包括代码分割、静态资源处理和Rollup集成

通过合理配置Vite，可以显著提高开发效率和应用性能。在下一章中，我们将学习Vite的插件系统和高级配置技巧。