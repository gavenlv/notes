import { defineConfig, loadEnv } from 'vite'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  return {
    // 基础路径
    base: env.VITE_BASE_PATH || '/',
    
    // 服务器配置
    server: {
      // 端口号
      port: 3000,
      // 是否自动打开浏览器
      open: true,
      // 主机名
      host: '0.0.0.0',
      // 跨域代理配置
      proxy: {
        // 代理API请求
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          // 配置HTTP请求头
          headers: {
            'X-Proxy-By': 'Vite'
          }
        },
        // 代理WebSocket
        '/ws': {
          target: env.VITE_WS_URL || 'ws://localhost:8080',
          ws: true,
          changeOrigin: true
        }
      },
      // 服务器优化
      optimizeDeps: {
        // 预构建的依赖
        include: ['axios', 'lodash-es']
      },
      // 是否启用https
      https: env.VITE_USE_HTTPS === 'true'
    },
    
    // 构建配置
    build: {
      // 输出目录
      outDir: 'dist',
      // 静态资源输出目录
      assetsDir: 'assets',
      // 生成源码映射
      sourcemap: env.VITE_SOURCEMAP === 'true',
      // 禁用CSS代码分割
      cssCodeSplit: true,
      // 小于此阈值的资源内联为base64
      assetsInlineLimit: 4096,
      // 清除输出目录
      emptyOutDir: true,
      // 配置rollup选项
      rollupOptions: {
        // 输入文件
        input: {
          main: resolve(__dirname, 'index.html')
        },
        // 输出配置
        output: {
          // 入口文件名称
          entryFileNames: 'assets/js/[name]-[hash].js',
          // 块文件名称
          chunkFileNames: 'assets/js/[name]-[hash].js',
          // 资源文件名称
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
        },
        // 代码分割配置
        manualChunks: {
          // 将第三方库单独打包
          vendor: ['axios', 'lodash-es']
        }
      },
      // 浏览器兼容性目标
      target: 'es2015'
    },
    
    // 解析配置
    resolve: {
      // 路径别名
      alias: {
        '@': resolve(__dirname, 'src'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@components': resolve(__dirname, 'src/components')
      },
      // 文件扩展名
      extensions: ['.js', '.jsx', '.ts', '.tsx', '.json', '.vue']
    },
    
    // CSS配置
    css: {
      // 预处理器配置
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/assets/styles/variables.scss";`
        }
      },
      // 启用CSS模块化
      modules: {
        // 生成的类名格式
        generateScopedName: '[name]__[local]___[hash:base64:5]'
      }
    },
    
    // 开发选项
    mode: mode,
    
    // 环境变量配置
    envPrefix: 'VITE_',
    
    // 日志级别
    logLevel: 'info'
  }
})
