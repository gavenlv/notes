const express = require('express')
const cors = require('cors')
const app = express()
const port = 3001

// Middleware
app.use(cors())
app.use(express.json())

// Mock data
const users = [
  { id: 1, name: '张三', email: 'zhangsan@example.com', avatar: 'https://via.placeholder.com/150' },
  { id: 2, name: '李四', email: 'lisi@example.com', avatar: 'https://via.placeholder.com/150' },
  { id: 3, name: '王五', email: 'wangwu@example.com', avatar: 'https://via.placeholder.com/150' }
]

const chartData = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'bar'
    }
  ]
}

// Routes
app.get('/users', (req, res) => {
  setTimeout(() => {
    res.json(users)
  }, 500)
})

app.get('/users/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id))
  if (user) {
    setTimeout(() => {
      res.json(user)
    }, 300)
  } else {
    res.status(404).json({ error: 'User not found' })
  }
})

app.delete('/users/:id', (req, res) => {
  const userId = parseInt(req.params.id);
  const userIndex = users.findIndex(u => u.id === userId);
  
  if (userIndex !== -1) {
    const deletedUser = users.splice(userIndex, 1);
    setTimeout(() => {
      res.json({ message: 'User deleted successfully', user: deletedUser[0] });
    }, 300);
  } else {
    res.status(404).json({ error: 'User not found' });
  }
});

app.get('/chart-data', (req, res) => {
  setTimeout(() => {
    res.json(chartData)
  }, 500)
})

// 用户个人资料路由
app.get('/user/profile', (req, res) => {
  // 返回第一个用户作为当前用户
  setTimeout(() => {
    res.json(users[0])
  }, 300)
})

// 更新用户个人资料路由
app.put('/user/profile', (req, res) => {
  const updatedUser = req.body;
  const userIndex = users.findIndex(u => u.id === updatedUser.id);
  
  if (userIndex !== -1) {
    users[userIndex] = { ...users[userIndex], ...updatedUser };
    setTimeout(() => {
      res.json(users[userIndex])
    }, 300)
  } else {
    res.status(404).json({ error: 'User not found' })
  }
})

app.listen(port, () => {
  console.log(`Mock API server running at http://localhost:${port}`)
})