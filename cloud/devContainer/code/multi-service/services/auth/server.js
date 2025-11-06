const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
const port = 3001;

app.use(express.json());

// 模拟用户数据
const users = [
  { id: 1, username: 'admin', password: 'admin123' },
  { id: 2, username: 'user', password: 'user123' }
];

// 登录接口
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  
  const user = users.find(u => u.username === username && u.password === password);
  
  if (user) {
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      process.env.JWT_SECRET || 'secret',
      { expiresIn: '1h' }
    );
    
    res.json({
      success: true,
      token,
      user: { id: user.id, username: user.username }
    });
  } else {
    res.status(401).json({
      success: false,
      message: '用户名或密码错误'
    });
  }
});

// 验证token接口
app.post('/verify', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ valid: false });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret');
    res.json({ valid: true, user: decoded });
  } catch (error) {
    res.status(401).json({ valid: false });
  }
});

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    service: 'auth',
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

app.listen(port, () => {
  console.log(`🔐 认证服务运行在 http://localhost:${port}`);
});