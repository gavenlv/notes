import express from 'express';
import cors from 'cors';
import { Pool } from 'pg';

const app = express();
const port = 5000;

// 中间件
app.use(cors());
app.use(express.json());

// 数据库连接
const pool = new Pool({
  user: 'user',
  host: 'db',
  database: 'devcontainer_db',
  password: 'password',
  port: 5432,
});

// 健康检查端点
app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ 
      status: 'healthy', 
      timestamp: new Date().toISOString(),
      database: 'connected'
    });
  } catch (error) {
    res.status(503).json({ 
      status: 'unhealthy', 
      error: error.message 
    });
  }
});

// API路由
app.get('/api/todos', async (req, res) => {
  try {
    const result = await pool.query(`
      CREATE TABLE IF NOT EXISTS todos (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    const todos = await pool.query('SELECT * FROM todos ORDER BY created_at DESC');
    res.json(todos.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/todos', async (req, res) => {
  try {
    const { title } = req.body;
    const result = await pool.query(
      'INSERT INTO todos (title) VALUES ($1) RETURNING *',
      [title]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.put('/api/todos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { completed } = req.body;
    const result = await pool.query(
      'UPDATE todos SET completed = $1 WHERE id = $2 RETURNING *',
      [completed, id]
    );
    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.delete('/api/todos/:id', async (req, res) => {
  try {
    const { id } = req.params;
    await pool.query('DELETE FROM todos WHERE id = $1', [id]);
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 启动服务器
app.listen(port, () => {
  console.log(`🚀 后端服务器运行在 http://localhost:${port}`);
  console.log(`📊 健康检查: http://localhost:${port}/health`);
  console.log(`🗄️ 数据库连接: postgresql://db:5432/devcontainer_db`);
});