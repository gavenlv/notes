const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello from DevContainer! 🚀');
});

app.get('/info', (req, res) => {
  res.json({
    message: 'Node.js开发环境运行正常',
    nodeVersion: process.version,
    platform: process.platform,
    timestamp: new Date().toISOString()
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
  console.log('开发环境已成功启动！');
});