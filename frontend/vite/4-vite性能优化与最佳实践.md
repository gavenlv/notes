# 第4章：Vite性能优化与最佳实践

## 4.1 构建优化策略

### 4.1.1 构建输出优化

Vite在生产构建时提供了多种优化选项，可以显著减少构建产物的体积和提升加载性能。

```javascript
// vite.config.js
export default {
  build: {
    // 目标浏览器
    target: 'modules',
    // 代码压缩方式
    minify: 'terser',
    // 启用CSS代码分割
    cssCodeSplit: true,
    // 生成sourcemap
    sourcemap: false,
    // 块大小警告限制
    chunkSizeWarningLimit: 500,
    // 资源内联限制
    assetsInlineLimit: 4096,
    // 启用brotli压缩大小报告
    brotliSize: true
  }
}
```

### 4.1.2 代码分割优化

合理的代码分割可以大大提升应用的加载性能，特别是对于大型应用。

#### 4.1.2.1 自动代码分割

Vite会根据动态导入自动进行代码分割：

```javascript
// 动态导入会自动创建单独的代码块
const LazyComponent = () => import('./LazyComponent.vue')
```

#### 4.1.2.2 手动代码分割

通过配置可以实现更精细的代码分割控制：

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 将Vue相关库打包到一个单独的chunk
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // 将UI组件库打包到一个单独的chunk
          'ui-lib': ['ant-design-vue', 'element-plus'],
          // 将工具库打包到一个单独的chunk
          'utils': ['lodash-es', 'axios']
        }
      }
    }
  }
}
```

### 4.1.3 依赖优化

依赖预构建是Vite的重要优化特性，可以显著提升开发体验和构建性能。

```javascript
// vite.config.js
export default {
  optimizeDeps: {
    // 强制包含在优化依赖中的模块
    include: [
      'lodash-es',
      'ant-design-vue/es/locale/zh_CN',
      'date-fns/esm',
      'vue-i18n'
    ],
    // 排除不需要优化的依赖
    exclude: ['不需要预构建的依赖'],
    // esbuild配置
    esbuildOptions: {
      target: 'es2020',
      // 配置treeshaking
      treeShaking: true
    }
  }
}
```

## 4.2 开发性能优化

### 4.2.1 开发服务器优化

优化开发服务器配置可以提升开发体验和热更新速度。

```javascript
// vite.config.js
export default {
  server: {
    // 预热常用模块
    warmup: {
      clientFiles: [
        './src/components/*.vue',
        './src/pages/*.vue',
        './src/utils/*.js'
      ]
    },
    // 优化文件监听
    watch: {
      ignored: ['**/node_modules/**', '**/dist/**', '**/.git/**'],
      usePolling: false
    },
    // 增加服务器内存限制
    maxMemoryUsageInMB: 4096
  },
  // 优化缓存
  cacheDir: './node_modules/.vite'
}
```

### 4.2.2 热更新优化

热更新（HMR）性能对开发体验至关重要，以下配置可以提升HMR性能：

```javascript
// vite.config.js
export default {
  server: {
    hmr: {
      // 禁用HMR客户端的日志
      clientPort: 24678,
      // 错误时显示全屏覆盖
      overlay: {
        warnings: true,
        errors: true
      },
      // 增加HMR超时时间
      timeout: 30000
    }
  },
  // 优化依赖构建缓存
  optimizeDeps: {
    // 强制重新构建依赖
    force: false
  }
}
```

### 4.2.3 大型项目优化策略

对于大型项目，可以采用以下策略提升开发性能：

1. **文件系统缓存**：利用Vite的文件系统缓存机制
2. **模块预热**：预编译常用模块
3. **配置文件拆分**：将复杂的配置拆分为多个文件
4. **选择性监听**：减少需要监听的文件数量
5. **依赖管理**：合理使用依赖，避免过多的第三方库

## 4.3 资源优化

### 4.3.1 静态资源优化

合理处理静态资源可以减少构建产物大小和提升加载性能。

```javascript
// vite.config.js
export default {
  build: {
    // 静态资源文件命名
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    },
    // 资源内联配置
    assetsInlineLimit: 4096 // 4KB以下的资源会内联
  },
  // 静态资源目录
  publicDir: 'public',
  // 额外的资源类型
  assetsInclude: ['**/*.gltf', '**/*.wasm', '**/*.worker.js']
}
```

### 4.3.2 图片优化

图片是Web应用中常见的性能瓶颈，以下是图片优化的最佳实践：

1. **使用现代图片格式**：WebP、AVIF等
2. **响应式图片**：提供不同尺寸的图片版本
3. **延迟加载**：只在需要时加载图片
4. **使用CDN**：利用内容分发网络加速图片加载

#### 4.3.2.1 使用vite-plugin-imagemin插件

```bash
npm install vite-plugin-imagemin -D
```

```javascript
// vite.config.js
import viteImagemin from 'vite-plugin-imagemin'

export default {
  plugins: [
    viteImagemin({
      gifsicle: {
        optimizationLevel: 7,
        interlaced: false
      },
      optipng: {
        optimizationLevel: 7
      },
      mozjpeg: {
        quality: 80
      },
      pngquant: {
        quality: [0.8, 0.9],
        speed: 4
      },
      svgo: {
        plugins: [
          {
            name: 'removeViewBox'
          },
          {
            name: 'removeEmptyAttrs',
            active: false
          }
        ]
      }
    })
  ]
}
```

### 4.3.3 CSS优化

优化CSS可以减少样式加载时间和渲染阻塞。

```javascript
// vite.config.js
export default {
  css: {
    // CSS模块化配置
    modules: {
      localsConvention: 'camelCase',
      scopeBehaviour: 'local'
    },
    // 预处理器配置
    preprocessorOptions: {
      scss: {
        additionalData: '@import "@/styles/variables.scss";'
      }
    },
    // 构建时CSS提取
    extract: true
  },
  build: {
    // CSS代码分割
    cssCodeSplit: true,
    // 最小化CSS
    minify: 'terser'
  }
}
```

## 4.4 网络性能优化

### 4.4.1 构建产物压缩

启用压缩可以显著减少传输大小：

```javascript
// vite.config.js
import viteCompression from 'vite-plugin-compression'

export default {
  plugins: [
    viteCompression({
      // 使用gzip压缩
      algorithm: 'gzip',
      // 压缩的文件类型
      ext: '.gz',
      // 仅压缩大于1024字节的文件
      threshold: 1024,
      // 压缩率，从0到9
      compressionOptions: {
        level: 9
      },
      // 是否删除原始文件
      deleteOriginFile: false
    })
  ]
}
```

### 4.4.2 预加载和预缓存

使用预加载可以提升关键资源的加载优先级：

```javascript
// 通过HTML中的link标签添加预加载
// index.html
<head>
  <!-- 预加载关键CSS -->
  <link rel="preload" href="/assets/main.css" as="style">
  <!-- 预加载关键JavaScript -->
  <link rel="preload" href="/assets/vendor.js" as="script">
  <!-- 预连接到CDN -->
  <link rel="preconnect" href="https://cdn.example.com">
  <!-- 预取可能需要的资源 -->
  <link rel="prefetch" href="/assets/lazy.js">
</head>
```

### 4.4.3 服务端渲染(SSR)优化

对于需要更好首屏加载性能的应用，可以考虑使用Vite的SSR功能：

```javascript
// vite.config.js
export default {
  // SSR配置
  ssr: {
    // 外部化不会在运行时变化的依赖
    external: ['vue', 'vue-router'],
    // 不外部化的依赖
    noExternal: ['@vueuse/core'],
    // SSR优化选项
    optimizeDeps: {
      include: ['vue/server-renderer']
    }
  }
}
```

## 4.5 代码质量与性能

### 4.5.1 Tree-shaking优化

Tree-shaking是移除未使用代码的重要技术，以下配置可以优化Tree-shaking效果：

```javascript
// vite.config.js
export default {
  build: {
    // 启用terser进行更高级的压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        dead_code: true,
        drop_console: true,
        drop_debugger: true
      }
    },
    // 配置rollup优化
    rollupOptions: {
      treeshake: {
        // 启用严格模式的tree-shaking
        moduleSideEffects: false,
        // 分析模块的副作用
        preset: 'smallest'
      }
    }
  }
}
```

### 4.5.2 减少JavaScript包体积

JavaScript包体积是影响加载性能的关键因素，以下是减少包体积的策略：

1. **按需导入**：只导入需要的模块
   ```javascript
   // 不推荐
   import _ from 'lodash'
   
   // 推荐
   import { debounce, throttle } from 'lodash-es'
   ```

2. **使用ES模块**：优先使用ES模块格式的依赖

3. **代码分割**：合理使用动态导入

4. **移除未使用的依赖**：定期清理项目依赖

5. **使用轻量级替代方案**：寻找更小的功能替代库

### 4.5.3 代码分割最佳实践

代码分割的最佳实践包括：

1. **按路由分割**：每个路由组件单独分割
2. **按功能分割**：将不同功能的代码分开
3. **按依赖类型分割**：将第三方依赖与业务代码分开
4. **避免过度分割**：过多的小文件会增加HTTP请求数量

## 4.6 实验：性能优化实践

### 4.6.1 实验目标

通过实际操作，学习如何优化Vite项目的构建性能和运行性能。

### 4.6.2 实验步骤

1. **创建测试项目**
   ```bash
   mkdir -p performance-demo
   cd performance-demo
   npm create vite@latest . -- --template vue
   npm install
   ```

2. **安装性能监控工具**
   ```bash
   npm install vite-bundle-visualizer -D
   ```

3. **配置构建分析**
   ```javascript
   // vite.config.js
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'
   import { visualizer } from 'rollup-plugin-visualizer'
   
   export default defineConfig({
     plugins: [
       vue(),
       visualizer({
         filename: './stats.html',
         gzipSize: true,
         brotliSize: true
       })
     ],
     build: {
       sourcemap: true
     }
   })
   ```

4. **添加一些依赖**
   ```bash
   npm install lodash-es axios moment
   ```

5. **创建一些组件**
   ```bash
   mkdir -p src/components
   touch src/components/LazyComponent.vue
   touch src/components/LargeComponent.vue
   ```

6. **编写组件代码**
   ```vue
   <!-- src/components/LargeComponent.vue -->
   <template>
     <div class="large-component">
       <h2>大型组件</h2>
       <p v-for="n in 1000" :key="n">这是第 {{ n }} 个段落</p>
     </div>
   </template>
   
   <script>
   import moment from 'moment'
   
   export default {
     name: 'LargeComponent',
     data() {
       return {
         time: moment().format('YYYY-MM-DD HH:mm:ss')
       }
     },
     mounted() {
       // 添加一些复杂计算
       const result = []
       for (let i = 0; i < 1000000; i++) {
         result.push(Math.sqrt(i))
       }
       console.log('计算完成', result.length)
     }
   }
   </script>
   ```

7. **优化导入**
   ```javascript
   // src/main.js - 优化前
   import { createApp } from 'vue'
   import App from './App.vue'
   import moment from 'moment'
   
   const app = createApp(App)
   app.mount('#app')
   
   // src/main.js - 优化后
   import { createApp } from 'vue'
   import App from './App.vue'
   // 移除未使用的导入
   
   const app = createApp(App)
   app.mount('#app')
   ```

8. **配置代码分割**
   ```javascript
   // vite.config.js - 添加代码分割配置
   export default defineConfig({
     // 其他配置...
     build: {
       rollupOptions: {
         output: {
           manualChunks: {
             'vue-vendor': ['vue'],
             'utils': ['lodash-es', 'axios'],
             'date': ['moment']
           }
         }
       }
     }
   })
   ```

9. **执行构建并分析**
   ```bash
   npm run build
   ```

10. **查看性能报告**
    打开生成的`stats.html`文件，分析构建产物的组成和大小。

11. **优化前后对比**
    记录优化前后的构建产物大小，对比优化效果。

## 4.7 常见性能问题与解决方案

### 4.7.1 构建速度慢

**问题**：项目构建时间过长。

**解决方案**：
- 优化依赖预构建配置
- 减少不必要的插件
- 优化babel配置（如果使用）
- 增加并行构建
- 使用缓存加速构建

### 4.7.2 构建产物过大

**问题**：生产环境构建后的文件体积过大。

**解决方案**：
- 配置代码分割
- 使用Tree-shaking
- 按需导入依赖
- 压缩静态资源
- 移除未使用的代码

### 4.7.3 开发服务器启动慢

**问题**：开发服务器启动时间过长。

**解决方案**：
- 优化依赖预构建
- 减少项目复杂度
- 配置合理的模块预热
- 清理node_modules/.vite缓存

## 4.8 性能监控与分析

### 4.8.1 构建性能分析

使用构建分析工具可以帮助识别性能瓶颈：

```javascript
// vite.config.js
import { visualizer } from 'rollup-plugin-visualizer'

export default {
  plugins: [
    visualizer({
      filename: './stats.html',
      gzipSize: true,
      brotliSize: true
    })
  ]
}
```

### 4.8.2 运行时性能监控

可以使用Performance API和Web Vitals来监控运行时性能：

```javascript
// src/utils/performance.js
import { onCLS, onFID, onLCP } from 'web-vitals'

export function monitorPerformance() {
  // 监控核心Web指标
  onCLS(metric => {
    console.log('CLS:', metric.value)
    // 发送到分析服务
  })
  
  onFID(metric => {
    console.log('FID:', metric.value)
    // 发送到分析服务
  })
  
  onLCP(metric => {
    console.log('LCP:', metric.value)
    // 发送到分析服务
  })
}

// src/main.js
import { monitorPerformance } from './utils/performance'

// 应用挂载后启动性能监控
app.mount('#app')
monitorPerformance()
```

## 4.9 最佳实践总结

### 4.9.1 项目结构最佳实践

1. **合理组织代码**：按功能或模块组织代码结构
2. **使用路径别名**：简化导入路径，避免相对路径的复杂性
3. **分离关注点**：将组件、逻辑、样式等分离到不同文件
4. **模块化设计**：将功能拆分为可复用的模块

### 4.9.2 配置最佳实践

1. **环境区分**：为不同环境配置不同的优化策略
2. **渐进式优化**：从基础优化开始，逐步应用高级优化
3. **定期清理**：定期清理和更新依赖
4. **监控构建**：使用构建分析工具监控构建性能

### 4.9.3 团队协作最佳实践

1. **统一配置**：团队使用统一的Vite配置
2. **性能规范**：制定性能优化规范
3. **代码审查**：在代码审查中关注性能问题
4. **自动化检查**：使用自动化工具检查性能问题

## 4.10 本章小结

在本章中，我们深入学习了Vite的性能优化技术和最佳实践。通过合理的配置和优化策略，可以显著提升Vite项目的构建性能和运行性能。

关键要点：
- 构建优化包括代码分割、依赖优化和输出优化
- 开发性能优化关注开发服务器配置和热更新性能
- 资源优化涉及静态资源、图片和CSS的处理
- 网络性能优化可以通过压缩和预加载等技术实现
- 代码质量与性能密切相关，良好的代码组织有助于性能优化
- 定期进行性能监控和分析，持续优化项目性能

通过本章学习的优化技术，可以构建出高性能、高质量的Vite应用。在下一章中，我们将学习Vite与主流框架的集成方法。