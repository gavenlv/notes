const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const port = 3000;

// 代理配置
app.use('/auth', createProxyMiddleware({
  target: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
  changeOrigin: true,
  pathRewrite: {
    '^/auth': ''
  }
}));

app.use('/api', createProxyMiddleware({
  target: process.env.API_SERVICE_URL || 'http://localhost:3002',
  changeOrigin: true,
  pathRewrite: {
    '^/api': ''
  }
}));

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    service: 'gateway',
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

app.listen(port, () => {
  console.log(`🚀 网关服务运行在 http://localhost:${port}`);
});