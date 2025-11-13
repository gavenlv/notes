import { defineConfig } from 'vite'

export default defineConfig({
  // 基础路径配置，用于生产环境部署
  base: '/',
  // 开发服务器配置
  server: {
    port: 3000,
    open: true
  },
  // 构建配置
  build: {
    // 输出目录
    outDir: 'dist'
  }
})
