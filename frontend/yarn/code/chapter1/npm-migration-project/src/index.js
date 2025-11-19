// NPM迁移到Yarn的示例项目
// 演示如何将使用NPM的项目迁移到Yarn

const express = require('express');
const axios = require('axios');

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 路由
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>NPM到Yarn迁移示例</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          .container { max-width: 800px; margin: 0 auto; }
          .success { color: green; }
          .info { color: blue; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>NPM到Yarn迁移示例</h1>
          <p class="info">这是一个演示如何将NPM项目迁移到Yarn的示例应用。</p>
          
          <h2>迁移步骤：</h2>
          <ol>
            <li>保留原有的 <code>package.json</code> 文件</li>
            <li>运行 <code>yarn install</code> 替代 <code>npm install</code></li>
            <li>将生成的 <code>yarn.lock</code> 添加到版本控制</li>
            <li>删除 <code>package-lock.json</code>（可选）</li>
            <li>使用 <code>yarn add</code> 替代 <code>npm install</code></li>
            <li>使用 <code>yarn remove</code> 替代 <code>npm uninstall</code></li>
            <li>使用 <code>yarn run</code> 替代 <code>npm run</code></li>
          </ol>
          
          <h2>已安装的依赖：</h2>
          <ul>
            <li><strong>express</strong>: ${require('express/package.json').version}</li>
            <li><strong>axios</strong>: ${require('axios/package.json').version}</li>
          </ul>
          
          <h2>API端点：</h2>
          <ul>
            <li><a href="/api/status">/api/status</a> - 检查应用状态</li>
            <li><a href="/api/data">/api/data</a> - 获取示例数据</li>
          </ul>
          
          <p class="success">迁移成功！现在您正在使用Yarn作为包管理器。</p>
        </div>
      </body>
    </html>
  `);
});

// API路由 - 检查状态
app.get('/api/status', (req, res) => {
  res.json({
    status: 'success',
    message: '应用正常运行',
    packageManager: 'Yarn',
    dependencies: {
      express: require('express/package.json').version,
      axios: require('axios/package.json').version
    },
    timestamp: new Date().toISOString()
  });
});

// API路由 - 获取数据
app.get('/api/data', async (req, res) => {
  try {
    // 使用axios获取示例数据
    const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1');
    res.json({
      status: 'success',
      data: response.data
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: '获取数据失败',
      error: error.message
    });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log('\n=== NPM到Yarn迁移成功 ===');
  console.log('使用Yarn命令:');
  console.log('- yarn start   # 启动应用');
  console.log('- yarn add    # 添加依赖');
  console.log('- yarn remove # 删除依赖');
  console.log('- yarn install # 安装依赖');
});

module.exports = app;