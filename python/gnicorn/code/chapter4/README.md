# 第4章代码示例：Gunicorn性能优化

本章包含用于演示Gunicorn性能优化的代码示例，包括性能测试应用和基准测试脚本。

## 文件说明

- `performance_app.py` - 用于测试不同Worker类型性能的应用
- `benchmark_test.sh` - 用于测试不同Worker类型性能的脚本
- `requirements.txt` - 项目依赖列表

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行性能测试

1. **启动测试应用**：
   ```bash
   # 使用sync worker
   gunicorn -w 4 -k sync performance_app:application
   
   # 使用gevent worker
   gunicorn -w 4 -k gevent performance_app:application
   ```

2. **运行基准测试**：
   ```bash
   # 使脚本可执行（Linux/macOS）
   chmod +x benchmark_test.sh
   
   # 运行测试
   ./benchmark_test.sh
   ```

## 测试端点

- `/` - 简单响应，用于基本性能测试
- `/cpu-intensive` - CPU密集型任务，用于测试CPU使用情况
- `/io-intensive` - I/O密集型任务，用于测试异步Worker优势
- `/mixed` - 混合型任务，包含CPU计算和I/O等待
- `/cached-data` - 缓存数据端点，用于测试缓存效果
- `/expensive-computation` - 昂贵的计算任务，用于测试算法优化
- `/memory-test` - 内存测试端点，用于测试内存使用

## 性能优化技巧

### 1. Worker类型选择

根据应用特性选择合适的Worker类型：

- **CPU密集型应用**：使用sync Worker
- **I/O密集型应用**：使用gevent或eventlet Worker
- **混合型应用**：根据瓶颈分析选择

### 2. Worker数量优化

使用以下公式计算Worker数量：

```python
import multiprocessing

# CPU密集型应用
workers = multiprocessing.cpu_count() * 2 + 1

# I/O密集型应用
workers = multiprocessing.cpu_count() * 4
```

### 3. 内存管理

- 设置`max_requests`定期重启Worker
- 使用`preload_app`减少内存碎片
- 监控内存使用，防止内存泄漏

### 4. 连接优化

- 调整`worker_connections`参数
- 优化`keepalive`和`timeout`设置
- 使用连接池减少连接开销

### 5. 缓存策略

- 实现应用级缓存
- 使用Redis等外部缓存系统
- 配置Nginx缓存

## 性能测试结果分析

基准测试脚本会生成包含以下指标的报告：

- **Requests per second**：每秒处理的请求数
- **Time per request**：每个请求的平均时间
- **Failed requests**：失败请求数量

根据这些指标，可以评估不同配置下的性能表现，选择最优配置。

## 实践建议

1. **逐步优化**：一次只改变一个参数，观察效果
2. **多次测试**：运行多次测试以获得更准确的结果
3. **监控资源**：使用top、htop等工具监控系统资源使用
4. **生产环境验证**：在测试环境验证后，再在生产环境应用
5. **持续监控**：部署后持续监控系统性能，及时调整

## 高级技巧

### 异步代码优化

对于I/O密集型应用，可以考虑使用异步代码：

```python
# 使用异步框架
from fastapi import FastAPI
import aiohttp

app = FastAPI()

@app.get("/async-request")
async def async_request():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com") as response:
            return await response.json()
```

### 数据库优化

使用连接池和查询优化：

```python
# 使用SQLAlchemy连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:password@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

## 注意事项

1. **测试环境**：在类似生产环境的测试环境中进行性能测试
2. **负载一致性**：确保测试负载一致
3. **资源限制**：注意测试环境的资源限制
4. **网络因素**：考虑网络延迟对测试结果的影响
5. **应用优化**：Gunicorn优化应与应用优化结合进行