import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  // 基础路径
  base: '/',
  
  // 插件配置
  plugins: [
    react({
      // React插件配置
      jsxRuntime: 'automatic', // 自动运行时
      jsxImportSource: 'react', // JSX导入源
      // 可以在这里配置Babel插件
      babel: {
        plugins: [
          // 可选的Babel插件
        ]
      }
    })
  ],
  
  // 服务器配置
  server: {
    port: 3000,
    open: true,
    host: true,
    // 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'esbuild',
    sourcemap: false,
    // 优化配置
    rollupOptions: {
      output: {
        // 自定义分块策略
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  
  // 解析配置
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@styles': resolve(__dirname, 'src/styles')
    },
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json', '.css', '.scss']
  },
  
  // CSS配置
  css: {
    modules: {
      localsConvention: 'camelCaseOnly', // 驼峰命名
      generateScopedName: '[name]__[local]__[hash:base64:5]'
    },
    preprocessorOptions: {
      scss: {
        // SCSS预处理器配置
        additionalData: '@import "@/styles/variables.scss";'
      }
    },
    devSourcemap: true // 开发环境源码映射
  },
  
  // 环境变量配置
  envDir: './env',
  envPrefix: 'VITE_',
  
  // 优化依赖预构建
  optimizeDeps: {
    include: ['react', 'react-dom']
  }
})
