# 第3章：PromQL查询语言

> **学习时长**: 6-8小时  
> **难度**: ⭐⭐⭐⭐  
> **重要性**: ⭐⭐⭐⭐⭐ (最核心的技能)

## 本章目标

学完本章后,你将能够:

- ✅ 理解PromQL的数据类型和基础语法
- ✅ 熟练使用选择器查询时间序列数据
- ✅ 掌握时间范围查询和偏移量操作
- ✅ 运用常用函数(rate、increase、histogram_quantile等)
- ✅ 执行聚合操作(sum、avg、max、min等)
- ✅ 理解向量匹配和运算规则
- ✅ 使用子查询解决复杂问题
- ✅ 优化查询性能

---

## 3.1 PromQL简介

### 3.1.1 什么是PromQL?

**PromQL** (Prometheus Query Language) 是Prometheus内置的数据查询语言,专门用于查询和分析时间序列数据。

**核心特点**:
- 🎯 **函数式语言**: 类似SQL但更强大,支持复杂的数学运算
- ⚡ **实时计算**: 查询时实时聚合计算,不依赖预聚合
- 📊 **向量化操作**: 可以同时操作多个时间序列
- 🔧 **灵活性高**: 支持即席查询(Ad-hoc Query)

### 3.1.2 PromQL的数据类型

PromQL中有4种数据类型:

| 数据类型 | 说明 | 示例 |
|---------|------|------|
| **Instant Vector** (瞬时向量) | 一组时间序列,每个序列包含单个样本值,共享同一时间戳 | `http_requests_total` |
| **Range Vector** (区间向量) | 一组时间序列,每个序列包含一段时间范围内的多个样本值 | `http_requests_total[5m]` |
| **Scalar** (标量) | 单一的数字值,没有时间序列 | `100` |
| **String** (字符串) | 简单的字符串值(目前使用较少) | `"hello"` |

**图解四种数据类型**:

```
Instant Vector (瞬时向量):
http_requests_total{method="GET"} → 245  (at t=10:00:00)
http_requests_total{method="POST"} → 123 (at t=10:00:00)

Range Vector (区间向量):
http_requests_total{method="GET"}[5m] → [245@10:00, 250@9:59, 248@9:58, ...]
http_requests_total{method="POST"}[5m] → [123@10:00, 120@9:59, 118@9:58, ...]

Scalar (标量):
100

String (字符串):
"server-01"
```

### 3.1.3 时间序列选择器

选择器用于从Prometheus中选择时间序列数据。

#### 标签匹配器

有4种标签匹配操作符:

| 操作符 | 说明 | 示例 |
|-------|------|------|
| `=` | 完全匹配 | `method="GET"` |
| `!=` | 不等于 | `method!="GET"` |
| `=~` | 正则匹配 | `method=~"GET|POST"` |
| `!~` | 正则不匹配 | `method!~"GET|POST"` |

**示例**:

```promql
# 1. 完全匹配 - 查询所有GET请求
http_requests_total{method="GET"}

# 2. 不等于 - 查询所有非GET请求
http_requests_total{method!="GET"}

# 3. 正则匹配 - 查询GET或POST请求
http_requests_total{method=~"GET|POST"}

# 4. 正则不匹配 - 查询method以P开头的所有请求
http_requests_total{method=~"P.*"}

# 5. 多条件组合 - 查询生产环境的GET请求
http_requests_total{environment="production", method="GET"}

# 6. 复杂正则 - 查询所有/api/开头的endpoint
http_requests_total{endpoint=~"/api/.*"}
```

---

## 3.2 时间范围查询

### 3.2.1 Range Vector (区间向量)

区间向量用于获取一段时间范围内的所有数据点。

**语法**:
```promql
metric_name[time_duration]
```

**时间单位**:
- `s` - 秒 (seconds)
- `m` - 分钟 (minutes)
- `h` - 小时 (hours)
- `d` - 天 (days)
- `w` - 周 (weeks)
- `y` - 年 (years)

**示例**:

```promql
# 获取过去5分钟的所有请求数据
http_requests_total[5m]

# 获取过去1小时的CPU使用率数据
node_cpu_seconds_total[1h]

# 获取过去24小时的内存使用数据
node_memory_MemAvailable_bytes[24h]

# 获取过去1周的磁盘IO数据
node_disk_io_time_seconds_total[1w]
```

### 3.2.2 时间偏移 (Offset)

使用`offset`关键字可以查询过去某个时间点的数据。

**语法**:
```promql
metric_name offset <duration>
metric_name[range] offset <duration>
```

**示例**:

```promql
# 查询5分钟前的瞬时请求数
http_requests_total offset 5m

# 查询1小时前的5分钟区间数据
http_requests_total[5m] offset 1h

# 查询昨天同一时刻的CPU使用率
node_cpu_seconds_total offset 1d

# 查询上周同一时刻的请求数
http_requests_total offset 1w
```

**实战案例 - 对比当前和1小时前的请求速率**:

```promql
# 当前请求速率
rate(http_requests_total[5m])

# 1小时前的请求速率
rate(http_requests_total[5m] offset 1h)

# 计算增长率
(rate(http_requests_total[5m]) - rate(http_requests_total[5m] offset 1h)) 
/ rate(http_requests_total[5m] offset 1h) * 100
```

### 3.2.3 @ 修饰符 (指定查询时间)

从Prometheus 2.25.0开始,可以使用`@`指定查询的确切时间戳。

**语法**:
```promql
metric_name @ <timestamp>
metric_name[range] @ <timestamp>
```

**示例**:

```promql
# 查询Unix时间戳1609459200(2021-01-01 00:00:00 UTC)时刻的数据
http_requests_total @ 1609459200

# 查询特定时刻前5分钟的区间数据
http_requests_total[5m] @ 1609459200

# @ 和 offset 可以组合使用
http_requests_total @ 1609459200 offset 1h
```

---

## 3.3 常用函数详解

### 3.3.1 rate() - 计算增长率

`rate()`是PromQL中**最常用**的函数,用于计算Counter类型指标的每秒平均增长率。

**语法**:
```promql
rate(range-vector)
```

**工作原理**:
1. 获取时间范围内的第一个和最后一个样本
2. 计算差值
3. 除以时间跨度(秒)
4. 自动处理Counter重置(重启导致的归零)

**示例**:

```promql
# 计算过去5分钟的HTTP请求速率(QPS)
rate(http_requests_total[5m])

# 计算过去5分钟的CPU使用率
rate(node_cpu_seconds_total{mode="idle"}[5m])

# 计算每个endpoint的请求速率
rate(http_requests_total[5m]) by (endpoint)

# 计算网络接收字节速率(MB/s)
rate(node_network_receive_bytes_total[5m]) / 1024 / 1024
```

**⚠️ 重要注意事项**:

1. **时间范围选择**: 通常选择scrape_interval的4倍
   ```promql
   # scrape_interval=15s,建议使用1m
   rate(http_requests_total[1m])
   
   # scrape_interval=30s,建议使用2m
   rate(http_requests_total[2m])
   ```

2. **只能用于Counter**: rate()仅适用于单调递增的Counter指标

3. **返回值单位**: 返回的是"每秒"的速率

### 3.3.2 irate() - 瞬时增长率

`irate()`计算的是区间内最后两个样本的瞬时增长率,对变化更敏感。

**语法**:
```promql
irate(range-vector)
```

**rate() vs irate()**:

```promql
# rate() - 平滑的平均速率,适合告警和长期趋势
rate(http_requests_total[5m])

# irate() - 灵敏的瞬时速率,适合快速变化的场景
irate(http_requests_total[5m])
```

**对比图示**:
```
样本序列: [100, 110, 120, 130, 140, 150] (每15秒一个样本)

rate([5m]):  
  (150 - 100) / (5 * 60) = 50/300 = 0.167 req/s (平均值,平滑)

irate([5m]): 
  (150 - 140) / 15 = 10/15 = 0.667 req/s (最后两个点,灵敏)
```

**使用建议**:
- ✅ **告警和长期趋势**: 使用`rate()`
- ✅ **短期峰值检测**: 使用`irate()`
- ✅ **Grafana图表**: rate()通常更稳定,irate()可能有毛刺

### 3.3.3 increase() - 增长总量

`increase()`计算指定时间范围内Counter的增长总量。

**语法**:
```promql
increase(range-vector)
```

**等价关系**:
```promql
increase(http_requests_total[1h]) 
== 
rate(http_requests_total[1h]) * 3600
```

**示例**:

```promql
# 过去1小时的请求总数
increase(http_requests_total[1h])

# 过去24小时的错误请求数
increase(http_requests_total{status="500"}[24h])

# 过去5分钟的网络接收字节数(MB)
increase(node_network_receive_bytes_total[5m]) / 1024 / 1024
```

### 3.3.4 sum() - 求和

`sum()`对多个时间序列的值进行求和。

**语法**:
```promql
sum(instant-vector) [by|without (label_list)]
```

**示例**:

```promql
# 1. 计算所有实例的总请求数
sum(http_requests_total)

# 2. 按method分组求和
sum(http_requests_total) by (method)

# 3. 排除instance标签,对其他标签求和
sum(http_requests_total) without (instance)

# 4. 多标签分组
sum(http_requests_total) by (method, status)

# 5. 实战 - 计算集群总QPS
sum(rate(http_requests_total[5m]))

# 6. 实战 - 计算每个服务的总QPS
sum(rate(http_requests_total[5m])) by (service)
```

### 3.3.5 avg() - 平均值

**示例**:

```promql
# 计算所有节点的平均CPU使用率
avg(rate(node_cpu_seconds_total{mode!="idle"}[5m]))

# 按节点分组计算平均CPU
avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) by (instance)

# 计算平均响应时间
avg(http_request_duration_seconds)
```

### 3.3.6 max() / min() - 最大值/最小值

**示例**:

```promql
# 找出CPU使用率最高的节点
max(rate(node_cpu_seconds_total{mode!="idle"}[5m])) by (instance)

# 找出响应时间最长的endpoint
max(http_request_duration_seconds) by (endpoint)

# 找出内存使用率最低的节点
min(node_memory_MemAvailable_bytes) by (instance)
```

### 3.3.7 count() - 计数

**示例**:

```promql
# 统计有多少个实例
count(up)

# 统计有多少个实例在线
count(up == 1)

# 统计有多少个不同的method
count(http_requests_total) by (method)

# 统计每个服务有多少个实例
count(up) by (job)
```

### 3.3.8 topk() / bottomk() - Top N查询

**语法**:
```promql
topk(N, instant-vector)
bottomk(N, instant-vector)
```

**示例**:

```promql
# 查询QPS最高的5个endpoint
topk(5, rate(http_requests_total[5m]))

# 查询CPU使用率最高的3个节点
topk(3, rate(node_cpu_seconds_total{mode!="idle"}[5m]))

# 查询内存使用最少的5个Pod
bottomk(5, node_memory_MemAvailable_bytes)

# 按服务分组,找出每个服务QPS最高的3个实例
topk(3, rate(http_requests_total[5m])) by (service)
```

### 3.3.9 histogram_quantile() - 分位数计算

用于从Histogram类型指标计算分位数(如p50、p95、p99延迟)。

**语法**:
```promql
histogram_quantile(φ, rate(histogram_metric[range]))
```

其中φ是分位数,范围0-1:
- 0.5 = p50 (中位数)
- 0.95 = p95
- 0.99 = p99

**示例**:

```promql
# 计算p95响应时间
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# 计算p99响应时间,按endpoint分组
histogram_quantile(0.99, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# 计算p50响应时间(中位数)
histogram_quantile(0.5, 
  rate(http_request_duration_seconds_bucket[5m])
)
```

**⚠️ 注意事项**:

1. 必须包含`le`标签(histogram的bucket标签)
2. 必须使用`rate()`或`increase()`
3. 使用`sum()`时,`le`标签必须保留

**完整示例**:

```promql
# ❌ 错误 - 缺少rate()
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# ✅ 正确
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# ✅ 正确 - 带分组
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)
```

### 3.3.10 预测函数 - predict_linear()

基于线性回归预测未来某个时间点的值。

**语法**:
```promql
predict_linear(range-vector, t)
```

其中`t`是要预测的未来时间(秒)。

**示例**:

```promql
# 预测4小时后的磁盘使用量
predict_linear(node_filesystem_avail_bytes[1h], 4*3600)

# 预测1小时后内存是否会耗尽(小于1GB)
predict_linear(node_memory_MemAvailable_bytes[30m], 3600) < 1024*1024*1024

# 预测明天这个时候的请求数
predict_linear(http_requests_total[6h], 24*3600)
```

### 3.3.11 时间和日期函数

```promql
# 获取当前Unix时间戳
time()

# 获取一天中的小时(0-23)
hour()

# 获取星期几(0-6,0是周日)
day_of_week()

# 获取月份中的第几天(1-31)
day_of_month()

# 获取月份(1-12)
month()

# 获取年份
year()
```

**实战 - 只在工作时间(9-18点)触发告警**:

```promql
# CPU使用率超过80%,且当前时间在9-18点之间
rate(node_cpu_seconds_total{mode!="idle"}[5m]) > 0.8
and hour() >= 9
and hour() <= 18
```

---

## 3.4 运算符

### 3.4.1 算术运算符

支持: `+`, `-`, `*`, `/`, `%`, `^`

**示例**:

```promql
# 计算可用内存百分比
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100

# 计算磁盘使用率
(node_filesystem_size_bytes - node_filesystem_avail_bytes) 
/ node_filesystem_size_bytes * 100

# 计算CPU使用率(100% - idle%)
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 网络吞吐量(Mbps)
(rate(node_network_receive_bytes_total[5m]) + rate(node_network_transmit_bytes_total[5m])) 
* 8 / 1024 / 1024
```

### 3.4.2 比较运算符

支持: `==`, `!=`, `>`, `<`, `>=`, `<=`

**两种模式**:

1. **过滤模式**(默认): 返回符合条件的时间序列
2. **布尔模式**(`bool`关键字): 返回0或1

**示例**:

```promql
# 过滤模式 - 返回CPU使用率>80%的时间序列
rate(node_cpu_seconds_total{mode!="idle"}[5m]) > 0.8

# 布尔模式 - 返回0或1
rate(node_cpu_seconds_total{mode!="idle"}[5m]) > bool 0.8

# 查询所有宕机的实例
up == 0

# 查询HTTP 500错误的请求
http_requests_total{status="500"} > 0

# 查询内存使用率>90%的节点
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.9
```

### 3.4.3 逻辑运算符

支持: `and`, `or`, `unless`

**示例**:

```promql
# and - 两个条件都满足
rate(node_cpu_seconds_total{mode!="idle"}[5m]) > 0.8
and
rate(node_memory_MemAvailable_bytes[5m]) < 1024*1024*1024

# or - 任一条件满足
up == 0 or rate(http_requests_total{status="500"}[5m]) > 10

# unless - 排除满足条件的序列
rate(http_requests_total[5m]) 
unless 
http_requests_total{endpoint="/health"}
```

---

## 3.5 向量匹配

当对两个瞬时向量进行运算时,需要定义如何匹配两边的时间序列。

### 3.5.1 一对一匹配 (One-to-One)

**语法**:
```promql
vector1 <operator> vector2
vector1 <operator> ignoring(label_list) vector2
vector1 <operator> on(label_list) vector2
```

**示例**:

```promql
# 默认匹配 - 所有标签必须完全相同
method_code:http_errors:rate5m / method_code:http_requests:rate5m

# ignoring - 忽略指定标签
method:http_requests:rate5m / ignoring(code) method:http_requests:rate5m

# on - 只基于指定标签匹配
method_code:http_errors:rate5m / on(method) method:http_requests:rate5m
```

### 3.5.2 一对多/多对一匹配

**语法**:
```promql
vector1 <operator> on(label_list) group_left vector2
vector1 <operator> on(label_list) group_right vector2
```

**示例**:

```promql
# 计算每个实例的请求数占总数的百分比
rate(http_requests_total[5m])
/
on(job) group_left
sum(rate(http_requests_total[5m])) by (job)
* 100

# 为指标添加节点信息
rate(node_cpu_seconds_total[5m]) * on(instance) group_left(nodename)
node_uname_info
```

---

## 3.6 聚合操作详解

### 3.6.1 by vs without

**`by`**: 保留指定标签,聚合其他标签
**`without`**: 删除指定标签,保留其他标签

**示例**:

```promql
# by - 只保留method标签
sum(rate(http_requests_total[5m])) by (method)
# 结果: {method="GET"}, {method="POST"}, ...

# without - 删除instance标签,保留其他
sum(rate(http_requests_total[5m])) without (instance)
# 结果: {method="GET", endpoint="/api/users"}, ...

# 多标签by
sum(rate(http_requests_total[5m])) by (method, status)

# 多标签without
sum(rate(http_requests_total[5m])) without (instance, job)
```

### 3.6.2 常见聚合模式

**1. 计算总和**:
```promql
sum(rate(http_requests_total[5m]))
```

**2. 分组求和**:
```promql
sum(rate(http_requests_total[5m])) by (service)
```

**3. 计算百分比**:
```promql
sum(rate(http_requests_total{status="200"}[5m])) 
/ 
sum(rate(http_requests_total[5m])) 
* 100
```

**4. 多级聚合**:
```promql
# 先按instance聚合,再计算总和
sum(
  sum(rate(http_requests_total[5m])) by (instance)
)
```

---

## 3.7 子查询 (Subquery)

子查询允许对区间向量执行函数操作。

**语法**:
```promql
<instant_query>[<range>:<resolution>]
```

**示例**:

```promql
# 计算过去1小时内,每5分钟的最大QPS
max_over_time(
  rate(http_requests_total[5m])[1h:1m]
)

# 计算过去30分钟内,CPU使用率的平均值
avg_over_time(
  rate(node_cpu_seconds_total{mode!="idle"}[5m])[30m:1m]
)

# 检测过去1小时是否有任何时刻CPU超过90%
max_over_time(
  (100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)[1h:1m]
) > 90
```

**常用子查询函数**:

- `max_over_time()`: 时间范围内的最大值
- `min_over_time()`: 时间范围内的最小值
- `avg_over_time()`: 时间范围内的平均值
- `sum_over_time()`: 时间范围内的总和
- `count_over_time()`: 时间范围内的样本数
- `stddev_over_time()`: 标准差
- `stdvar_over_time()`: 方差

---

## 3.8 实战查询案例

### 3.8.1 CPU监控

```promql
# 1. CPU总体使用率
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 2. 各模式CPU使用率分布
sum by (mode) (rate(node_cpu_seconds_total[5m])) * 100

# 3. 单个核心的CPU使用率
100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)

# 4. CPU使用率Top 5节点
topk(5, 
  100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
)

# 5. CPU使用率超过80%的节点数量
count(
  100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
)
```

### 3.8.2 内存监控

```promql
# 1. 内存使用率
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 2. 可用内存(GB)
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024

# 3. Swap使用率
(1 - node_memory_SwapFree_bytes / node_memory_SwapTotal_bytes) * 100

# 4. 内存使用最多的5个节点
topk(5, 
  (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
)

# 5. 预测4小时后内存耗尽的节点
predict_linear(node_memory_MemAvailable_bytes[1h], 4*3600) < 0
```

### 3.8.3 磁盘监控

```promql
# 1. 磁盘使用率
(node_filesystem_size_bytes - node_filesystem_avail_bytes) 
/ node_filesystem_size_bytes * 100

# 2. 可用磁盘空间(GB)
node_filesystem_avail_bytes / 1024 / 1024 / 1024

# 3. 磁盘IO使用率
rate(node_disk_io_time_seconds_total[5m]) * 100

# 4. 磁盘读写速率(MB/s)
rate(node_disk_read_bytes_total[5m]) / 1024 / 1024

# 5. 预测磁盘何时用满(小于10GB)
(predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[1h], 24*3600) 
/ 1024 / 1024 / 1024) < 10
```

### 3.8.4 网络监控

```promql
# 1. 网络接收速率(Mbps)
rate(node_network_receive_bytes_total[5m]) * 8 / 1024 / 1024

# 2. 网络发送速率(Mbps)
rate(node_network_transmit_bytes_total[5m]) * 8 / 1024 / 1024

# 3. 总网络吞吐量(Mbps)
(rate(node_network_receive_bytes_total[5m]) + 
 rate(node_network_transmit_bytes_total[5m])) * 8 / 1024 / 1024

# 4. 网络错误率
rate(node_network_receive_errs_total[5m]) / 
rate(node_network_receive_packets_total[5m]) * 100

# 5. 网络丢包率
rate(node_network_receive_drop_total[5m]) / 
rate(node_network_receive_packets_total[5m]) * 100
```

### 3.8.5 HTTP请求监控

```promql
# 1. QPS (每秒请求数)
sum(rate(http_requests_total[5m]))

# 2. 按method分组的QPS
sum(rate(http_requests_total[5m])) by (method)

# 3. 错误率
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100

# 4. p95响应时间
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# 5. 慢请求数量(>1s)
sum(rate(http_request_duration_seconds_count[5m])) 
- 
sum(rate(http_request_duration_seconds_bucket{le="1"}[5m]))

# 6. 成功率
sum(rate(http_requests_total{status=~"2.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100

# 7. 4xx错误率
sum(rate(http_requests_total{status=~"4.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100

# 8. 按endpoint排序的Top 10 QPS
topk(10, 
  sum(rate(http_requests_total[5m])) by (endpoint)
)
```

### 3.8.6 应用程序监控

```promql
# 1. 服务可用性
up{job="my-service"}

# 2. 所有实例的平均响应时间
avg(http_request_duration_seconds)

# 3. JVM堆内存使用率(Java应用)
jvm_memory_bytes_used{area="heap"} / jvm_memory_bytes_max{area="heap"} * 100

# 4. GC停顿时间
rate(jvm_gc_pause_seconds_sum[5m])

# 5. 线程数
jvm_threads_current

# 6. 数据库连接池使用率
hikaricp_connections_active / hikaricp_connections_max * 100

# 7. 消息队列积压量
rabbitmq_queue_messages{queue="my-queue"}
```

---

## 3.9 查询优化

### 3.9.1 性能优化原则

**1. 尽量减少查询的时间序列数量**

```promql
# ❌ 差 - 查询所有时间序列
rate(http_requests_total[5m])

# ✅ 好 - 先过滤再查询
rate(http_requests_total{service="api", environment="prod"}[5m])
```

**2. 避免使用正则表达式(如果可能)**

```promql
# ❌ 差 - 使用正则
http_requests_total{endpoint=~"/api/.*"}

# ✅ 好 - 使用精确匹配
http_requests_total{endpoint="/api/users"}
```

**3. 使用Recording Rules预聚合**

```promql
# ❌ 差 - 复杂查询实时计算
sum(rate(http_requests_total{job="api"}[5m])) by (method, status)

# ✅ 好 - 使用预聚合的recording rule
job_method_status:http_requests:rate5m
```

**4. 合理选择时间范围**

```promql
# ❌ 差 - 时间范围太小,结果不稳定
rate(http_requests_total[30s])

# ✅ 好 - 4倍scrape_interval
rate(http_requests_total[1m])
```

**5. 避免使用子查询(除非必要)**

```promql
# ❌ 差 - 性能消耗大
max_over_time(rate(http_requests_total[5m])[1h:1m])

# ✅ 好 - 如果可能,使用简单查询
max(rate(http_requests_total[5m]))
```

### 3.9.2 常见性能陷阱

**❌ 陷阱1: 高基数标签**

```promql
# 错误 - user_id是高基数标签(百万级)
sum(rate(http_requests_total[5m])) by (user_id)
```

**✅ 解决方案**: 在应用层聚合,不要将高基数数据作为标签。

**❌ 陷阱2: 过长的时间范围**

```promql
# 错误 - 查询30天数据
rate(http_requests_total[30d])
```

**✅ 解决方案**: 使用Recording Rules预聚合历史数据。

**❌ 陷阱3: 笛卡尔积**

```promql
# 错误 - 可能产生大量结果
sum(metric1) * sum(metric2)
```

**✅ 解决方案**: 明确指定匹配标签。

```promql
sum(metric1) * on(instance) sum(metric2)
```

### 3.9.3 查询分析工具

在Prometheus UI中,可以使用以下方式分析查询性能:

1. **查看查询统计**: Status → Query Stats
2. **使用`--log.level=debug`**: 查看详细日志
3. **检查`prometheus_engine_query_duration_seconds`**: 查询执行时间

---

## 3.10 实验练习

### 实验1: 基础查询练习

在本章code目录下,我们提供了一个完整的实验环境。

**启动实验环境**:

```bash
cd code/chapter03/01-basic-queries
docker-compose up -d
```

**练习题**:

1. 查询Prometheus的所有指标
2. 查询过去5分钟的HTTP请求数
3. 计算QPS
4. 计算CPU使用率
5. 查询内存使用率超过80%的节点

**参考答案**:

```promql
# 1. 查询所有指标(在Graph页面执行)
{__name__!=""}

# 2. 过去5分钟的HTTP请求数
http_requests_total[5m]

# 3. 计算QPS
rate(http_requests_total[5m])

# 4. CPU使用率
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 5. 内存使用率>80%
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 80
```

### 实验2: 复杂聚合练习

**练习题**:

1. 计算每个method的QPS,并按从高到低排序
2. 计算错误率(status 5xx)
3. 找出QPS最高的Top 3 endpoint
4. 计算p95响应时间
5. 对比当前QPS与1小时前的增长率

**参考答案**:

```promql
# 1. 每个method的QPS,降序
sort_desc(
  sum(rate(http_requests_total[5m])) by (method)
)

# 2. 错误率
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100

# 3. Top 3 endpoint
topk(3, 
  sum(rate(http_requests_total[5m])) by (endpoint)
)

# 4. p95响应时间
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# 5. QPS增长率
(sum(rate(http_requests_total[5m])) 
 - sum(rate(http_requests_total[5m] offset 1h))) 
/ sum(rate(http_requests_total[5m] offset 1h)) * 100
```

### 实验3: 实际场景演练

**场景**: 你的服务出现性能问题,需要排查

**任务**:
1. 检查服务是否在线
2. 查看当前QPS
3. 检查错误率
4. 分析响应时间(p50、p95、p99)
5. 查看CPU和内存使用情况
6. 找出最慢的endpoint

**排查脚本**:

```promql
# 1. 服务状态
up{job="my-service"}

# 2. 当前QPS
sum(rate(http_requests_total{job="my-service"}[5m]))

# 3. 错误率
sum(rate(http_requests_total{job="my-service", status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total{job="my-service"}[5m])) * 100

# 4. 响应时间分位数
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{job="my-service"}[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="my-service"}[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{job="my-service"}[5m]))

# 5. CPU使用率
100 - (avg(rate(node_cpu_seconds_total{instance=~"my-service.*", mode="idle"}[5m])) * 100)

# 6. 内存使用率
(1 - node_memory_MemAvailable_bytes{instance=~"my-service.*"} 
     / node_memory_MemTotal_bytes{instance=~"my-service.*"}) * 100

# 7. 最慢的endpoint (p99响应时间)
topk(5, 
  histogram_quantile(0.99, 
    sum(rate(http_request_duration_seconds_bucket{job="my-service"}[5m])) by (le, endpoint)
  )
)
```

---

## 3.11 本章小结

### 核心知识点回顾

✅ **PromQL数据类型**: Instant Vector、Range Vector、Scalar、String

✅ **时间序列选择器**: 标签匹配(`=`, `!=`, `=~`, `!~`)和时间范围(`[5m]`, `offset`)

✅ **核心函数**:
- `rate()` / `irate()`: 计算增长率
- `increase()`: 计算增长总量
- `sum()` / `avg()` / `max()` / `min()` / `count()`: 聚合函数
- `topk()` / `bottomk()`: Top N查询
- `histogram_quantile()`: 分位数计算

✅ **运算符**: 算术、比较、逻辑运算

✅ **向量匹配**: `on`, `ignoring`, `group_left`, `group_right`

✅ **聚合操作**: `by` vs `without`

✅ **子查询**: `[range:resolution]`

✅ **查询优化**: 减少时间序列、避免正则、使用Recording Rules

### 常用查询速查表

| 监控场景 | PromQL查询 |
|---------|-----------|
| QPS | `rate(http_requests_total[5m])` |
| 错误率 | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100` |
| p95延迟 | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| CPU使用率 | `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| 内存使用率 | `(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100` |
| 磁盘使用率 | `(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100` |
| 网络流量 | `rate(node_network_receive_bytes_total[5m]) / 1024 / 1024` |

### 下一章预告

在**第4章 - Exporters与数据采集**中,我们将学习:

- 📦 Node Exporter监控Linux系统
- 🐳 cAdvisor监控容器
- 🔧 自定义Exporter开发
- 📊 常见中间件Exporters(MySQL、Redis、Nginx等)
- 🎯 Pushgateway使用场景

---

## 附录A: PromQL函数速查

### 聚合函数
- `sum()` - 求和
- `avg()` - 平均值
- `max()` - 最大值
- `min()` - 最小值
- `count()` - 计数
- `stddev()` - 标准差
- `stdvar()` - 方差
- `topk()` - Top K
- `bottomk()` - Bottom K
- `quantile()` - 分位数
- `count_values()` - 统计值分布

### 速率函数
- `rate()` - 平均增长率(Counter)
- `irate()` - 瞬时增长率(Counter)
- `increase()` - 增长总量(Counter)
- `delta()` - 差值(Gauge)
- `idelta()` - 瞬时差值(Gauge)
- `deriv()` - 导数(Gauge)

### 时间函数
- `time()` - 当前Unix时间戳
- `timestamp()` - 样本时间戳
- `hour()` - 小时
- `minute()` - 分钟
- `day_of_week()` - 星期
- `day_of_month()` - 月中第几天
- `month()` - 月份
- `year()` - 年份

### 预测函数
- `predict_linear()` - 线性预测
- `holt_winters()` - Holt-Winters预测

### 数学函数
- `abs()` - 绝对值
- `ceil()` - 向上取整
- `floor()` - 向下取整
- `round()` - 四舍五入
- `sqrt()` - 平方根
- `exp()` - 指数
- `ln()` - 自然对数
- `log2()` - 以2为底的对数
- `log10()` - 以10为底的对数

### 标签操作
- `label_replace()` - 替换标签
- `label_join()` - 连接标签

### 排序函数
- `sort()` - 升序
- `sort_desc()` - 降序

### 缺失值处理
- `absent()` - 检测指标是否不存在
- `absent_over_time()` - 检测时间范围内是否一直不存在

### 其他函数
- `vector()` - 将标量转换为向量
- `scalar()` - 将向量转换为标量
- `histogram_quantile()` - Histogram分位数
- `clamp_max()` - 限制最大值
- `clamp_min()` - 限制最小值
- `changes()` - 统计变化次数
- `resets()` - 统计Counter重置次数

---

## 附录B: 正则表达式速查

PromQL使用RE2正则语法:

```promql
# 匹配以api开头
{endpoint=~"^/api/.*"}

# 匹配多个值
{method=~"GET|POST|PUT"}

# 匹配所有5xx状态码
{status=~"5.."}

# 不匹配health和metrics
{endpoint!~".*(health|metrics).*"}

# 匹配prod或production
{env=~"prod(uction)?"}

# 匹配所有以-01到-09结尾的实例
{instance=~".*-0[1-9]$"}
```

**常用元字符**:
- `.` - 任意字符
- `*` - 0次或多次
- `+` - 1次或多次
- `?` - 0次或1次
- `^` - 行首
- `$` - 行尾
- `[]` - 字符集
- `|` - 或
- `()` - 分组

---

**🎉 恭喜!** 你已经掌握了PromQL查询语言的核心知识!

PromQL是Prometheus最重要的技能之一,建议多做实验练习,熟能生巧。

**下一步**: 继续学习[第4章 - Exporters与数据采集](./第4章-Exporters与数据采集.md)
