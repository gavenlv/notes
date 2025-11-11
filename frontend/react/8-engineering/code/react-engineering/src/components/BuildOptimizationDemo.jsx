import React from 'react';

const BuildOptimizationDemo = () => {
  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-icon">BO</div>
        <div className="demo-info">
          <h3>构建优化</h3>
          <p>使用 Vite 进行高效构建和优化配置</p>
        </div>
      </div>

      <div className="info-box">
        <p>构建优化可以显著提高应用性能，减小包体积，提升加载速度，为用户提供更好的体验。</p>
      </div>

      <h4>Vite 构建优化配置示例</h4>
      <div className="code-block">
        <pre>
{`// vite.config.js 中的构建优化配置
build: {
  sourcemap: true,
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react', 'react-dom', 'react-router-dom'],
        utilities: []
      }
    }
  },
  minify: 'esbuild', // 使用 esbuild 进行代码压缩
  chunkSizeWarningLimit: 1000, // 警告的块大小限制
  cssCodeSplit: true, // CSS 代码分割
  assetsInlineLimit: 4096, // 小于此值的资源将内联
  outDir: 'dist', // 输出目录
  assetsDir: 'assets' // 静态资源目录
};`}</pre>
      </div>

      <h4>构建优化的关键策略</h4>
      <ul className="feature-list">
        <li>代码分割 (Code Splitting)</li>
        <li>Tree Shaking 去除未使用的代码</li>
        <li>压缩 JavaScript 和 CSS</li>
        <li>图片和静态资源优化</li>
        <li>缓存策略配置</li>
        <li>预加载和预连接资源</li>
      </ul>

      <h4>常见的性能优化指标</h4>
      <div className="info-box">
        <p>• First Contentful Paint (FCP): 首次内容绘制时间</p>
        <p>• Largest Contentful Paint (LCP): 最大内容绘制时间，建议小于2.5秒</p>
        <p>• First Input Delay (FID): 首次输入延迟，建议小于100毫秒</p>
        <p>• Cumulative Layout Shift (CLS): 累积布局偏移，建议小于0.1</p>
      </div>

      <h4>构建命令和分析工具</h4>
      <div className="code-block">
        <pre>
{`# 构建项目
npm run build

# 预览构建结果
npm run preview

# 分析构建体积（需要安装 vite-bundle-analyzer）
npm install --save-dev rollup-plugin-visualizer

# 在 vite.config.js 中配置
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    // ...其他插件
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
});`}</pre>
      </div>

      <div className="success-box">
        <p>✅ 使用 npm run build 命令可以构建优化后的生产版本</p>
      </div>
    </div>
  );
};

export default BuildOptimizationDemo;