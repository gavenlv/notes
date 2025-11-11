import React, { useState, useEffect } from 'react';

const PerformanceMonitoringDemo = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // 模拟性能监控数据收集
  const collectPerformanceData = () => {
    setIsLoading(true);
    
    // 模拟收集性能数据的延迟
    setTimeout(() => {
      // 在实际应用中，这里会使用 Performance API 或其他监控工具
      const mockData = {
        fcp: 1200, // First Contentful Paint
        lcp: 2100, // Largest Contentful Paint
        fid: 50,   // First Input Delay
        cls: 0.05, // Cumulative Layout Shift
        tti: 3500, // Time to Interactive
        resourceTiming: [
          { name: 'main.js', duration: 300 },
          { name: 'styles.css', duration: 150 },
          { name: 'images/banner.jpg', duration: 800 }
        ]
      };
      
      setPerformanceData(mockData);
      setIsLoading(false);
    }, 1500);
  };

  // 组件挂载时收集性能数据
  useEffect(() => {
    // 检查浏览器是否支持 Performance API
    if (typeof window !== 'undefined' && window.performance) {
      // 收集初始性能数据
      collectPerformanceData();
    }
  }, []);

  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-icon">PM</div>
        <div className="demo-info">
          <h3>性能监控与优化</h3>
          <p>监控关键性能指标，持续优化用户体验</p>
        </div>
      </div>

      <div className="info-box">
        <p>性能监控是工程化的重要组成部分，可以帮助我们发现和解决性能瓶颈，提供更好的用户体验。</p>
      </div>

      <button 
        onClick={collectPerformanceData}
        className="demo-button"
        disabled={isLoading}
      >
        {isLoading ? '收集数据中...' : '重新收集性能数据'}
      </button>

      {isLoading && <p>正在收集性能指标...</p>}

      {performanceData && (
        <div className="performance-data">
          <h4>核心 Web 指标 (Core Web Vitals)</h4>
          <div className="metric-grid">
            <div className={`metric-item ${performanceData.lcp < 2500 ? 'good' : 'poor'}`}>
              <div className="metric-name">LCP (最大内容绘制)</div>
              <div className="metric-value">{performanceData.lcp}ms</div>
              <div className="metric-status">
                {performanceData.lcp < 2500 ? '良好' : '需要优化'}
              </div>
            </div>
            <div className={`metric-item ${performanceData.fid < 100 ? 'good' : 'poor'}`}>
              <div className="metric-name">FID (首次输入延迟)</div>
              <div className="metric-value">{performanceData.fid}ms</div>
              <div className="metric-status">
                {performanceData.fid < 100 ? '良好' : '需要优化'}
              </div>
            </div>
            <div className={`metric-item ${performanceData.cls < 0.1 ? 'good' : 'poor'}`}>
              <div className="metric-name">CLS (累积布局偏移)</div>
              <div className="metric-value">{performanceData.cls}</div>
              <div className="metric-status">
                {performanceData.cls < 0.1 ? '良好' : '需要优化'}
              </div>
            </div>
          </div>
        </div>
      )}

      <h4>性能监控实现示例</h4>
      <div className="code-block">
        <pre>
{`// performance-monitor.js
class PerformanceMonitor {
  constructor() {
    this.metrics = {}
    this.observers = []
  }

  // 初始化性能监控
  init() {
    this.setupLCPObserver()
    this.setupCLSObserver()
    this.setupFPObserver()
    this.collectResourceTiming()
  }

  // 监控 LCP (Largest Contentful Paint)
  setupLCPObserver() {
    const observer = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      const lastEntry = entries[entries.length - 1]
      this.metrics.lcp = lastEntry.startTime
      this.reportMetrics()
    })

    observer.observe({ type: 'largest-contentful-paint', buffered: true })
    this.observers.push(observer)
  }

  // 监控 CLS (Cumulative Layout Shift)
  setupCLSObserver() {
    let clsValue = 0
    let clsEntries = []

    const observer = new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      
      entries.forEach(entry => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value
          clsEntries.push(entry)
          this.metrics.cls = clsValue
          this.reportMetrics()
        }
      })
    })

    observer.observe({ type: 'layout-shift', buffered: true })
    this.observers.push(observer)
  }

  // 收集资源加载时间
  collectResourceTiming() {
    if (performance.getEntriesByType) {
      const resources = performance.getEntriesByType('resource')
      this.metrics.resourceTiming = resources.map(r => ({
        name: r.name,
        duration: r.duration
      }))
    }
  }

  // 报告性能指标
  reportMetrics() {
    console.log('性能指标:', this.metrics)
    // 这里可以将数据发送到监控服务器
    // fetch('/api/performance', { method: 'POST', body: JSON.stringify(this.metrics) })
  }

  // 清理监控
  cleanup() {
    this.observers.forEach(observer => observer.disconnect())
  }
}

// 使用方法
const monitor = new PerformanceMonitor()
monitor.init()

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
  monitor.cleanup()
})`}</pre>
      </div>

      <h4>常见性能优化技巧</h4>
      <ul className="feature-list">
        <li>使用 CDN 加速资源加载</li>
        <li>实现图片响应式加载和懒加载</li>
        <li>使用 WebP 格式图片减小体积</li>
        <li>压缩和最小化 JavaScript、CSS 文件</li>
        <li>使用 Service Worker 缓存静态资源</li>
        <li>优化关键渲染路径 (Critical Rendering Path)</li>
        <li>避免阻塞渲染的 CSS 和 JavaScript</li>
      </ul>

      <div className="success-box">
        <p>✅ 使用浏览器的 Performance 面板可以实时监控应用性能指标</p>
      </div>
    </div>
  );
};

export default PerformanceMonitoringDemo;