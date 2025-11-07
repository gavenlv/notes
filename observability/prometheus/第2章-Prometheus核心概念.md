# 第2章：Prometheus核心概念

## 2.1 指标类型详解

Prometheus定义了四种核心指标类型，每种类型适用于不同的监控场景。

### 2.1.1 Counter（计数器）

**定义：**
Counter是一个只增不减的累积型指标（除非重启归零）。

**使用场景：**
- HTTP请求总数
- 错误总数
- 任务完成数
- 发送的字节数

**示例：**
```promql
# 指标名称
http_requests_total

# 带标签的完整指标
http_requests_total{method="GET", endpoint="/api/users", status="200"}

# 当前值
http_requests_total{method="GET"} 1547
```

**重要特性：**
1. **只增不减**：值永远增长或保持不变
2. **重启归零**：应用重启后从0开始
3. **需要rate/increase函数**：查询时需要计算速率

**常用查询：**
```promql
# 每秒请求速率（最近5分钟平均）
rate(http_requests_total[5m])

# 最近1小时总增量
increase(http_requests_total[1h])

# 错误率（错误请求/总请求）
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m]) * 100
```

**代码示例（Go）：**
```go
package main

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "HTTP请求总数",
        },
        []string{"method", "endpoint", "status"},
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
}

func handler(w http.ResponseWriter, r *http.Request) {
    // 增加计数器
    httpRequestsTotal.WithLabelValues(
        r.Method,
        r.URL.Path,
        "200",
    ).Inc()
    
    w.Write([]byte("Hello World"))
}

func main() {
    http.HandleFunc("/", handler)
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

---

### 2.1.2 Gauge（仪表盘）

**定义：**
Gauge是可增可减的瞬时值指标，表示当前状态。

**使用场景：**
- CPU使用率
- 内存使用量
- 当前连接数
- 队列大小
- 温度

**示例：**
```promql
# CPU使用率
node_cpu_usage_percent 45.2

# 内存使用量（字节）
node_memory_used_bytes 8589934592

# 活跃连接数
http_connections_active 127
```

**重要特性：**
1. **可增可减**：值可以任意变化
2. **表示瞬时状态**：反映当前时刻的值
3. **直接使用**：查询时不需要rate函数

**常用查询：**
```promql
# 当前CPU使用率
node_cpu_usage_percent

# 内存使用率
(node_memory_used_bytes / node_memory_total_bytes) * 100

# 平均值（最近5分钟）
avg_over_time(cpu_usage_percent[5m])

# 最大值
max_over_time(cpu_usage_percent[1h])
```

**代码示例（Python）：**
```python
from prometheus_client import Gauge, start_http_server
import psutil
import time

# 创建Gauge指标
cpu_usage = Gauge('cpu_usage_percent', 'CPU使用率百分比')
memory_usage = Gauge('memory_used_bytes', '已使用内存字节数')

def collect_metrics():
    while True:
        # 设置CPU使用率
        cpu_usage.set(psutil.cpu_percent())
        
        # 设置内存使用量
        memory_usage.set(psutil.virtual_memory().used)
        
        time.sleep(15)

if __name__ == '__main__':
    start_http_server(8000)
    collect_metrics()
```

---

### 2.1.3 Histogram（直方图）

**定义：**
Histogram对观察值进行采样，并在可配置的桶（bucket）中计数。

**使用场景：**
- 请求延迟分布
- 响应大小分布
- 查询执行时间

**指标组成：**
```promql
# 1. 累积计数器（每个桶）
http_request_duration_seconds_bucket{le="0.1"} 1000
http_request_duration_seconds_bucket{le="0.5"} 1450
http_request_duration_seconds_bucket{le="1.0"} 1480
http_request_duration_seconds_bucket{le="+Inf"} 1500

# 2. 总和
http_request_duration_seconds_sum 523.7

# 3. 计数
http_request_duration_seconds_count 1500
```

**重要概念：**
- **le（less than or equal）**：小于等于该值的观察计数
- **桶是累积的**：每个桶包含所有更小桶的计数
- **+Inf桶**：包含所有观察值

**计算百分位数：**
```promql
# 计算p95延迟（95%的请求延迟小于此值）
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)

# 计算p50（中位数）
histogram_quantile(0.50,
  rate(http_request_duration_seconds_bucket[5m])
)

# 计算p99
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)
```

**平均延迟：**
```promql
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])
```

**代码示例（Go）：**
```go
var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP请求延迟直方图",
            Buckets: []float64{0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0},
        },
        []string{"method", "endpoint"},
    )
)

func init() {
    prometheus.MustRegister(requestDuration)
}

func timedHandler(w http.ResponseWriter, r *http.Request) {
    start := time.Now()
    
    // 处理请求
    processRequest(w, r)
    
    // 记录延迟
    duration := time.Since(start).Seconds()
    requestDuration.WithLabelValues(r.Method, r.URL.Path).Observe(duration)
}
```

---

### 2.1.4 Summary（摘要）

**定义：**
Summary类似Histogram，但直接在客户端计算分位数。

**使用场景：**
- 与Histogram类似，但：
  - 需要精确的分位数
  - 客户端计算能力充足
  - 不需要聚合多个实例

**指标组成：**
```promql
# 1. 预计算的分位数
http_request_duration_seconds{quantile="0.5"} 0.12
http_request_duration_seconds{quantile="0.9"} 0.45
http_request_duration_seconds{quantile="0.99"} 1.2

# 2. 总和
http_request_duration_seconds_sum 523.7

# 3. 计数
http_request_duration_seconds_count 1500
```

**Histogram vs Summary对比：**

| 特性 | Histogram | Summary |
|------|-----------|---------|
| 分位数计算 | 服务端（PromQL） | 客户端 |
| 聚合能力 | 可聚合多实例 | 不可聚合 |
| 精确度 | 近似值 | 精确值 |
| 性能开销 | 较低 | 较高 |
| 灵活性 | 可任意查询分位数 | 只能查询预定义分位数 |

**推荐使用：**
- **优先使用Histogram**：大多数场景
- **使用Summary**：需要精确分位数且单实例监控

**代码示例（Python）：**
```python
from prometheus_client import Summary
import time

request_latency = Summary(
    'request_processing_seconds',
    '请求处理时间',
    ['method', 'endpoint']
)

@request_latency.labels('GET', '/api/users').time()
def get_users():
    time.sleep(0.1)  # 模拟处理
    return "users"
```

---

## 2.2 数据模型深度解析

### 2.2.1 时间序列标识

Prometheus中的每个时间序列由以下部分唯一标识：
```
指标名称{标签1="值1", 标签2="值2", ...}
```

**示例：**
```promql
# 不同的时间序列
http_requests_total{method="GET", endpoint="/api"}
http_requests_total{method="POST", endpoint="/api"}
http_requests_total{method="GET", endpoint="/login"}
```

**唯一性规则：**
```
指标名称 + 标签集合（完全相同） = 唯一时间序列
```

### 2.2.2 样本结构

每个样本包含：
1. **指标名称**：字符串
2. **标签集合**：键值对
3. **时间戳**：毫秒级Unix时间戳
4. **值**：float64数值

**内部表示：**
```
{
  __name__: "http_requests_total",
  method: "GET",
  endpoint: "/api",
  instance: "localhost:8080",
  job: "web-app"
}  ->  (timestamp: 1699012345678, value: 1547.0)
```

### 2.2.3 指标命名规范

**基本格式：**
```
<namespace>_<subsystem>_<name>_<unit>
```

**示例：**
```promql
# 好的命名
http_requests_total                    # HTTP请求总数
http_request_duration_seconds          # 请求延迟（秒）
node_cpu_seconds_total                 # CPU使用时间（秒）
process_resident_memory_bytes          # 进程内存（字节）

# 不好的命名
requests                               # 太模糊
httpRequestsTotal                      # 不应使用驼峰命名
http_requests_count                    # 应使用_total后缀
http_request_duration_ms               # 应使用基本单位（秒）
```

**命名规则：**

1. **使用蛇形命名法**：`snake_case`，不用驼峰命名
2. **添加单位后缀**：
   - 时间：`_seconds`（不要用ms、minutes）
   - 字节：`_bytes`（不要用kb、mb）
   - 百分比：`_ratio`（0-1）或`_percent`（0-100）
3. **Counter后缀**：使用`_total`
4. **Histogram/Summary后缀**：
   - Histogram：`_bucket`, `_sum`, `_count`
   - Summary：`{quantile="..."}`, `_sum`, `_count`

---

## 2.3 标签系统

### 2.3.1 标签的作用

标签（Labels）是Prometheus多维数据模型的核心，用于：
1. **区分不同维度**：同一指标的不同实例
2. **过滤和聚合**：PromQL查询的基础
3. **路由告警**：Alertmanager使用标签路由

**标签示例：**
```promql
http_requests_total{
  method="GET",           # HTTP方法
  endpoint="/api/users",  # API端点
  status="200",           # 状态码
  instance="web-1:8080",  # 实例
  job="web-app"          # 任务
}
```

### 2.3.2 标签类型

**1. 目标标签（Target Labels）**

由Prometheus配置添加：
```yaml
scrape_configs:
  - job_name: 'web-app'
    static_configs:
      - targets: ['localhost:8080']
        labels:
          env: 'production'
          datacenter: 'us-east-1'
```

**2. 实例标签（Instance Labels）**

自动添加：
- `instance`：抓取目标地址
- `job`：job_name

**3. 导出器标签（Exporter Labels）**

由导出器添加：
```promql
node_cpu_seconds_total{
  cpu="0",        # CPU核心编号
  mode="idle"     # CPU模式
}
```

**4. 保留标签（Reserved Labels）**

以`__`开头的内部标签：
```promql
__name__          # 指标名称
__address__       # 抓取地址（内部使用）
__scheme__        # 协议（http/https）
__metrics_path__  # 指标路径
```

### 2.3.3 标签基数（Cardinality）

**定义：**
基数 = 标签所有可能值的组合数

**示例：**
```promql
http_requests_total{
  method=[GET, POST, PUT, DELETE],     # 4个值
  endpoint=[/, /api, /login, /admin],  # 4个值
  status=[200, 404, 500]               # 3个值
}

总基数 = 4 × 4 × 3 = 48 个时间序列
```

**高基数问题：**

❌ **避免高基数标签：**
```promql
# 不要使用：
- user_id="user123456"        # 用户ID（百万级）
- request_id="abc-def-ghi"    # 请求ID（无限）
- email="user@example.com"    # 电子邮件
- ip_address="192.168.1.1"    # IP地址（大量）
```

✅ **使用合理基数：**
```promql
# 好的标签：
- method="GET"                # HTTP方法（少量）
- status="200"                # 状态码（有限）
- endpoint="/api/users"       # API端点（可控）
- region="us-east-1"          # 区域（少量）
```

**基数计算查询：**
```promql
# 查看指标的时间序列数
count(http_requests_total)

# 查看某个标签的唯一值数量
count(count by (endpoint) (http_requests_total))
```

### 2.3.4 标签最佳实践

**1. 选择合适的标签**
```promql
# ✅ 好的标签设计
http_requests_total{
  method="GET",
  endpoint="/api/users",
  status_class="2xx"  # 而不是精确的status="200"
}

# ❌ 过度细化
http_requests_total{
  method="GET",
  endpoint="/api/users/123456",  # 包含用户ID
  status="200",
  timestamp="2024-01-15-10:30:45"  # 时间应该是维度，不是标签
}
```

**2. 标签命名规范**
```promql
# 使用蛇形命名
status_code  ✅
statusCode   ❌

# 简短清晰
env     ✅  (environment)
dc      ✅  (datacenter)
svc     ✅  (service)
```

**3. 标签值规范**
```promql
# 使用小写
method="get"  ✅
method="GET"  ❌（除非约定俗成）

# 避免空格
env="production"  ✅
env="prod env"    ❌
```

---

## 2.4 时间序列存储

### 2.4.1 TSDB存储原理

Prometheus使用自定义的时间序列数据库（TSDB）。

**存储结构：**
```
data/
├── 01ABCDEF0123456/      # 2小时块
│   ├── chunks/           # 压缩的样本数据
│   │   └── 000001
│   ├── index             # 倒排索引
│   ├── meta.json         # 元数据
│   └── tombstones        # 删除标记
├── 01ABCDEF7890ABC/      # 另一个2小时块
└── wal/                  # 预写日志
    ├── 00000000
    └── 00000001
```

**数据组织：**
1. **2小时块**：数据按2小时划分
2. **压缩**：旧块合并压缩
3. **索引**：快速标签查询
4. **WAL**：保证数据持久性

### 2.4.2 数据压缩

Prometheus使用高效的压缩算法：

**压缩比例：**
```
原始数据：16字节/样本（时间戳8字节 + 值8字节）
压缩后：1.37字节/样本（平均）
压缩比：约12:1
```

**存储计算：**
```
每秒样本数 = 时间序列数 × (1 / 采集间隔)

示例：
- 10,000个时间序列
- 15秒采集间隔
- 保留15天

每秒样本 = 10,000 / 15 ≈ 667
每天样本 = 667 × 86,400 = 57,628,800
存储需求 = 57,628,800 × 1.37字节 × 15天 ≈ 1.1GB
```

### 2.4.3 数据保留策略

**配置保留时间：**
```bash
# 命令行参数
--storage.tsdb.retention.time=15d    # 保留15天
--storage.tsdb.retention.size=10GB   # 或最大10GB

# 二者取较小值
```

**清理策略：**
- Prometheus定期检查旧块
- 删除超过保留期的数据
- 自动压缩和合并块

---

## 2.5 实战：设计监控指标体系

### 2.5.1 Web应用监控指标

**1. 请求指标（Counter）**
```go
// 请求总数
http_requests_total{method, endpoint, status}

// 字节发送
http_response_size_bytes{method, endpoint}
```

**2. 延迟指标（Histogram）**
```go
// 请求延迟分布
http_request_duration_seconds{method, endpoint}
// 桶：[0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
```

**3. 并发指标（Gauge）**
```go
// 活跃连接数
http_connections_active

// 活跃请求数
http_requests_in_flight
```

### 2.5.2 数据库监控指标

**1. 连接池（Gauge）**
```python
db_connections_active         # 活跃连接
db_connections_idle           # 空闲连接
db_connections_max            # 最大连接
```

**2. 查询性能（Histogram）**
```python
db_query_duration_seconds{operation}  # 查询延迟
```

**3. 操作计数（Counter）**
```python
db_queries_total{operation, status}   # 查询总数
db_rows_affected_total{operation}     # 影响行数
```

### 2.5.3 业务指标

**1. 用户行为（Counter）**
```python
user_registrations_total              # 注册数
user_logins_total{status}            # 登录数
orders_created_total{product_type}    # 订单数
```

**2. 业务状态（Gauge）**
```python
active_users_count                    # 活跃用户
shopping_cart_items                   # 购物车商品
inventory_stock{product_id}           # 库存数量
```

**3. 收入指标（Counter）**
```python
revenue_total{currency, payment_method}  # 总收入
```

---

## 2.6 实验：指标类型实战

### 实验1：Counter使用

**创建简单HTTP服务器（Python）：**

文件：`code/chapter02/01-counter-demo/app.py`
```python
from prometheus_client import Counter, start_http_server
from flask import Flask
import time

app = Flask(__name__)

# 定义Counter
request_count = Counter(
    'http_requests_total',
    'HTTP请求总数',
    ['method', 'endpoint', 'status']
)

@app.route('/')
def index():
    request_count.labels('GET', '/', '200').inc()
    return 'Hello World'

@app.route('/api/users')
def users():
    request_count.labels('GET', '/api/users', '200').inc()
    return 'Users List'

if __name__ == '__main__':
    start_http_server(8000)  # Prometheus metrics端口
    app.run(port=5000)        # 应用端口
```

**运行：**
```bash
pip install prometheus_client flask
python app.py

# 访问应用
curl http://localhost:5000/
curl http://localhost:5000/api/users

# 查看指标
curl http://localhost:8000/metrics
```

### 实验2：Histogram使用

**测量请求延迟：**

文件：`code/chapter02/02-histogram-demo/app.py`
```python
from prometheus_client import Histogram, start_http_server
from flask import Flask
import time
import random

app = Flask(__name__)

# 定义Histogram
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP请求延迟',
    ['method', 'endpoint'],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0]
)

@app.route('/')
@request_duration.labels('GET', '/').time()
def index():
    time.sleep(random.uniform(0, 0.5))  # 模拟延迟
    return 'Hello'

@app.route('/slow')
@request_duration.labels('GET', '/slow').time()
def slow():
    time.sleep(random.uniform(1, 3))  # 模拟慢请求
    return 'Slow response'

if __name__ == '__main__':
    start_http_server(8000)
    app.run(port=5000)
```

**查询示例：**
```promql
# p95延迟
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)

# 平均延迟
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])
```

完整代码：[code/chapter02/](code/chapter02/)

---

## 2.7 总结

本章学习了：

✅ **四种指标类型**：Counter、Gauge、Histogram、Summary  
✅ **数据模型**：时间序列、样本结构、唯一性  
✅ **指标命名**：规范和最佳实践  
✅ **标签系统**：类型、基数、最佳实践  
✅ **存储原理**：TSDB、压缩、保留策略  
✅ **实战设计**：Web、数据库、业务指标体系  

### 下一步

在 **第3章** 中，我们将深入学习：
- PromQL查询语言基础
- 选择器和过滤器
- 函数和聚合操作
- 复杂查询技巧

---

**下一章**：[第3章：PromQL查询语言](第3章-PromQL查询语言.md)
