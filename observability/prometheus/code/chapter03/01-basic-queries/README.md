# 第3章 - PromQL查询语言实验环境

本目录包含第3章PromQL学习的完整实验环境。

## 📦 环境组成

- **Prometheus**: 核心监控系统 (端口9090)
- **Node Exporter**: 提供系统指标 (端口9100)
- **Demo App**: 模拟应用,生成HTTP请求指标 (端口8000)

## 🚀 快速开始

### 1. 启动环境

```bash
# 进入实验目录
cd code/chapter03/01-basic-queries

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 访问服务

- **Prometheus UI**: http://localhost:9090
- **Demo App**: http://localhost:8000
- **Demo App Metrics**: http://localhost:8000/metrics
- **Node Exporter**: http://localhost:9100/metrics

### 3. 验证数据采集

等待1-2分钟后,在Prometheus UI中执行:

```promql
# 检查所有targets是否UP
up

# 查看Demo App指标
http_requests_total

# 查看Node Exporter指标
node_cpu_seconds_total
```

## 📚 练习指标说明

### HTTP请求指标

```promql
# HTTP请求总数 (Counter)
http_requests_total{method, endpoint, status}

# HTTP请求延迟 (Histogram)
http_request_duration_seconds_bucket{method, endpoint, le}
http_request_duration_seconds_sum{method, endpoint}
http_request_duration_seconds_count{method, endpoint}

# 当前活跃请求数 (Gauge)
http_active_requests
```

### 业务指标

```promql
# 订单总数
order_total{status}

# 支付总金额
payment_amount_total

# 用户登录次数
user_login_total{method}
```

### 系统指标 (Node Exporter)

```promql
# CPU
node_cpu_seconds_total{mode, cpu}

# 内存
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes

# 磁盘
node_filesystem_size_bytes
node_filesystem_avail_bytes

# 网络
node_network_receive_bytes_total
node_network_transmit_bytes_total
```

## 🎯 基础练习题

### 练习1: 基础查询

```promql
# 1. 查询所有指标名称
{__name__!=""}

# 2. 查询所有GET请求
http_requests_total{method="GET"}

# 3. 查询/api/users的所有请求
http_requests_total{endpoint="/api/users"}

# 4. 查询状态码为500的请求
http_requests_total{status="500"}

# 5. 使用正则匹配所有/api/开头的endpoint
http_requests_total{endpoint=~"/api/.*"}
```

### 练习2: 速率计算

```promql
# 1. 计算整体QPS
rate(http_requests_total[5m])

# 2. 按method分组的QPS
sum(rate(http_requests_total[5m])) by (method)

# 3. 按endpoint分组的QPS
sum(rate(http_requests_total[5m])) by (endpoint)

# 4. 计算错误率
sum(rate(http_requests_total{status="500"}[5m])) 
/ 
sum(rate(http_requests_total[5m])) 
* 100

# 5. 对比rate()和irate()
rate(http_requests_total[5m])
irate(http_requests_total[5m])
```

### 练习3: 聚合操作

```promql
# 1. 总QPS
sum(rate(http_requests_total[5m]))

# 2. 平均响应时间
avg(http_request_duration_seconds)

# 3. QPS最高的Top 3 endpoint
topk(3, sum(rate(http_requests_total[5m])) by (endpoint))

# 4. 按status分组统计请求数
sum(rate(http_requests_total[5m])) by (status)

# 5. 统计有多少个不同的endpoint
count(sum(http_requests_total) by (endpoint))
```

### 练习4: 响应时间分析

```promql
# 1. p50响应时间
histogram_quantile(0.5, 
  rate(http_request_duration_seconds_bucket[5m])
)

# 2. p95响应时间
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# 3. p99响应时间
histogram_quantile(0.99, 
  rate(http_request_duration_seconds_bucket[5m])
)

# 4. 按endpoint分组的p95响应时间
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# 5. 找出响应最慢的endpoint
topk(3, 
  histogram_quantile(0.99, 
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
  )
)
```

### 练习5: 系统监控查询

```promql
# 1. CPU使用率
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 2. 内存使用率
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 3. 各CPU模式的使用率
sum(rate(node_cpu_seconds_total[5m])) by (mode) * 100

# 4. 网络接收速率(MB/s)
rate(node_network_receive_bytes_total[5m]) / 1024 / 1024

# 5. 网络发送速率(MB/s)
rate(node_network_transmit_bytes_total[5m]) / 1024 / 1024
```

### 练习6: 业务指标查询

```promql
# 1. 订单创建速率
rate(order_total[5m])

# 2. 订单成功率
sum(rate(order_total{status="success"}[5m])) 
/ 
sum(rate(order_total[5m])) 
* 100

# 3. 每分钟支付金额
rate(payment_amount_total[1m]) * 60

# 4. 用户登录速率(按登录方式)
sum(rate(user_login_total[5m])) by (method)

# 5. 最常用的登录方式
topk(1, sum(rate(user_login_total[5m])) by (method))
```

### 练习7: 时间操作

```promql
# 1. 5分钟前的QPS
rate(http_requests_total[5m]) offset 5m

# 2. 对比当前和5分钟前的QPS
rate(http_requests_total[5m]) - rate(http_requests_total[5m] offset 5m)

# 3. 计算QPS增长率
(rate(http_requests_total[5m]) - rate(http_requests_total[5m] offset 5m)) 
/ 
rate(http_requests_total[5m] offset 5m) 
* 100

# 4. 只在工作时间(9-18点)显示告警
rate(http_requests_total{status="500"}[5m]) > 0.1
and hour() >= 9
and hour() < 18

# 5. 过去1小时的最大QPS
max_over_time(sum(rate(http_requests_total[5m]))[1h:1m])
```

## 🎓 进阶挑战

### 挑战1: 综合性能分析

编写一个查询,同时展示:
- 当前QPS
- 错误率
- p95响应时间
- 与10分钟前的对比

### 挑战2: 服务健康度评分

基于以下指标计算服务健康度(0-100分):
- 可用性 (up状态)
- 错误率 (<5% = 满分)
- 响应时间 (p95 <500ms = 满分)

### 挑战3: 容量规划

基于当前QPS趋势,预测1小时后的QPS,并计算需要的实例数。

## 🛑 停止环境

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

## 📖 相关文档

- [Prometheus官方文档](https://prometheus.io/docs/)
- [PromQL查询示例](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Node Exporter指标说明](https://github.com/prometheus/node_exporter)

---

**提示**: 建议在Grafana中将这些查询可视化,可以更直观地理解数据变化!
