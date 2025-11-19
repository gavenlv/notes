// Yarn依赖管理演示
// 展示如何使用和管理项目依赖

const express = require('express');
const axios = require('axios');

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());

// 路由
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>Yarn依赖管理演示</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          .container { max-width: 800px; margin: 0 auto; }
          .demo { background-color: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
          .command { background-color: #f0f0f0; padding: 10px; font-family: monospace; margin: 10px 0; border-radius: 3px; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Yarn依赖管理演示</h1>
          <p>这个演示项目展示了Yarn的依赖管理功能。</p>
          
          <div class="demo">
            <h2>基本依赖管理命令</h2>
            <div class="command">yarn add lodash</div>
            <p>添加一个生产依赖</p>
            
            <div class="command">yarn add nodemon --dev</div>
            <p>添加一个开发依赖</p>
            
            <div class="command">yarn remove lodash</div>
            <p>移除一个依赖</p>
          </div>
          
          <div class="demo">
            <h2>查询命令</h2>
            <div class="command">yarn list</div>
            <p>列出所有已安装的依赖</p>
            
            <div class="command">yarn info lodash</div>
            <p>查看特定依赖的信息</p>
            
            <div class="command">yarn outdated</div>
            <p>检查过时的依赖</p>
          </div>
          
          <div class="demo">
            <h2>版本控制</h2>
            <div class="command">yarn add react@17.0.2</div>
            <p>安装特定版本</p>
            
            <div class="command">yarn add react --exact</div>
            <p>安装精确版本（不使用范围符号）</p>
            
            <div class="command">yarn upgrade lodash</div>
            <p>更新依赖到最新兼容版本</p>
          </div>
          
          <div class="demo">
            <h2>当前项目依赖</h2>
            <ul>
              <li><strong>express</strong>: ${require('express/package.json').version} (生产依赖)</li>
              <li><strong>axios</strong>: ${require('axios/package.json').version} (生产依赖)</li>
            </ul>
          </div>
        </div>
      </body>
    </html>
  `);
});

// API路由 - 检查依赖
app.get('/api/dependencies', (req, res) => {
  try {
    // 读取package.json
    const fs = require('fs');
    const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
    
    const dependencies = packageJson.dependencies || {};
    const devDependencies = packageJson.devDependencies || {};
    
    // 获取实际安装的版本
    const installedDependencies = {};
    const installedDevDependencies = {};
    
    Object.keys(dependencies).forEach(dep => {
      try {
        const pkg = require(`${dep}/package.json`);
        installedDependencies[dep] = {
          requested: dependencies[dep],
          installed: pkg.version
        };
      } catch (e) {
        installedDependencies[dep] = {
          requested: dependencies[dep],
          installed: 'Not installed'
        };
      }
    });
    
    Object.keys(devDependencies).forEach(dep => {
      try {
        const pkg = require(`${dep}/package.json`);
        installedDevDependencies[dep] = {
          requested: devDependencies[dep],
          installed: pkg.version
        };
      } catch (e) {
        installedDevDependencies[dep] = {
          requested: devDependencies[dep],
          installed: 'Not installed'
        };
      }
    });
    
    res.json({
      status: 'success',
      dependencies: installedDependencies,
      devDependencies: installedDevDependencies
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: '获取依赖信息失败',
      error: error.message
    });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log('\n=== Yarn依赖管理演示 ===');
  console.log('尝试以下命令来管理依赖:');
  console.log('- yarn add lodash      # 添加生产依赖');
  console.log('- yarn add nodemon -D  # 添加开发依赖');
  console.log('- yarn list             # 列出依赖');
  console.log('- yarn remove lodash    # 移除依赖');
  console.log('- yarn outdated         # 检查过时依赖');
  console.log('- yarn info lodash      # 查看依赖信息');
  console.log('- yarn upgrade lodash   # 更新依赖');
});

module.exports = app;