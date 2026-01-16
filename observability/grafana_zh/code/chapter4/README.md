# 第4章：查询语言和数据处理 - 代码示例

## 概述

本目录包含第4章教程的完整可运行代码示例，演示如何在Grafana中使用不同的查询语言（PromQL、Flux、SQL）进行数据处理和分析。

## 快速开始

### 1. 启动所有服务

```bash
# 进入chapter4目录
cd chapter4

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看数据生成器日志
docker-compose logs data-generator
```

### 2. 访问服务

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **InfluxDB**: http://localhost:8086 (admin/admin123)
- **MySQL**: localhost:3306 (root/root123)

### 3. 验证数据源连接

登录Grafana后，检查数据源是否自动配置：
1. 左侧菜单 → Configuration → Data sources
2. 应该看到预配置的Prometheus、InfluxDB、MySQL数据源
3. 点击每个数据源的"Save & Test"验证连接

## 查询语言示例

### PromQL (Prometheus查询语言)

#### 基础查询

```promql
# CPU使用率计算
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
node_memory_usage_percentage

# 磁盘使用率
node_disk_usage_percentage
```

#### 高级查询

```promql
# 95分位响应时间
histogram_quantile(0.95, 
  sum by(le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# 预测磁盘空间使用
predict_linear(node_filesystem_free_bytes[1h], 3600)

# 同比分析
(
  node_memory_usage_percentage
  -
  node_memory_usage_percentage offset 1d
)
```

### Flux (InfluxDB查询语言)

#### 基础查询管道

```flux
// 基础查询
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> filter(fn: (r) => r._field == "usage")
  |> aggregateWindow(every: 1m, fn: mean)
```

#### 数据转换

```flux
// 数据转换和计算
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "memory")
  |> map(fn: (r) => ({ 
    r with 
    usage_percentage: (r._value / 32.0) * 100.0 
  }))
  |> yield(name: "memory_usage")
```

### SQL (MySQL查询语言)

#### 基础查询

```sql
-- 系统指标查询
SELECT 
    timestamp as time,
    hostname,
    metric_name,
    metric_value as value
FROM system_metrics
WHERE timestamp >= NOW() - INTERVAL 1 HOUR
ORDER BY timestamp DESC
```

#### 聚合查询

```sql
-- 应用性能统计
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as time,
    app_name,
    level,
    COUNT(*) as log_count,
    AVG(duration_ms) as avg_duration
FROM application_logs
WHERE timestamp >= NOW() - INTERVAL 24 HOUR
GROUP BY time, app_name, level
ORDER BY time DESC
```

## 数据处理技术

### 数据聚合

#### 时间窗口聚合

```promql
# 5分钟平均值
avg_over_time(node_cpu_seconds_total[5m])

# 每小时最大值
max_over_time(node_memory_usage_percentage[1h])
```

```flux
// 时间窗口聚合
from(bucket: "mybucket")
  |> range(start: -1h)
  |> aggregateWindow(every: 5m, fn: mean)
```

```sql
-- 时间窗口聚合
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:00') as time_window,
    AVG(metric_value) as avg_value
FROM system_metrics
GROUP BY time_window
```

### 数据过滤

#### 条件过滤

```promql
# 过滤高负载实例
node_cpu_seconds_total > 80

# 多条件过滤
node_memory_usage_percentage > 70 and node_disk_usage_percentage > 80
```

```flux
// 多条件过滤
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu" and r._value > 80)
```

```sql
-- 复杂条件过滤
SELECT * FROM system_metrics
WHERE metric_value > 80
  AND hostname LIKE 'web-%'
  AND timestamp >= NOW() - INTERVAL 1 HOUR
```

### 数据转换

#### 单位转换

```promql
# 字节转MB
node_memory_MemTotal_bytes / (1024 * 1024)

# 百分比计算
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

```sql
-- 数据格式化
SELECT 
    hostname,
    metric_name,
    ROUND(metric_value, 2) as formatted_value,
    CASE 
        WHEN metric_value > 90 THEN 'CRITICAL'
        WHEN metric_value > 80 THEN 'WARNING'
        ELSE 'NORMAL'
    END as status
FROM system_metrics
```

## 高级查询技巧

### 多数据源联合查询

虽然Grafana本身不支持跨数据源联合查询，但可以通过以下方式实现：

1. **数据预处理**: 将不同数据源的数据统一到一个数据源
2. **面板级联**: 使用变量和面板链接实现数据关联
3. **外部处理**: 使用外部工具进行数据聚合

### 查询性能优化

#### 减少数据量

```promql
# 使用更短的时间范围
rate(http_requests_total[1m])  # 而不是 [5m]

# 增加采样间隔
avg_over_time(metric[5m])      # 而不是 [1m]
```

#### 使用索引

```sql
-- 确保查询使用索引
EXPLAIN SELECT * FROM system_metrics 
WHERE timestamp >= '2023-01-01' 
  AND hostname = 'web-01'

-- 创建复合索引
CREATE INDEX idx_timestamp_hostname ON system_metrics(timestamp, hostname);
```

## 示例仪表板

### 创建查询语言比较仪表板

1. **创建新仪表板**: 左侧菜单 → Create → Dashboard
2. **添加多个面板**: 每个面板使用不同的查询语言
3. **配置变量**: 创建时间范围、主机名等变量
4. **比较结果**: 观察不同查询语言的输出结果

### 面板配置示例

#### PromQL面板

```json
{
  "targets": [
    {
      "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
      "legendFormat": "{{instance}} CPU使用率",
      "refId": "A"
    }
  ]
}
```

#### Flux面板

```json
{
  "targets": [
    {
      "query": "from(bucket: \"mybucket\")\n  |> range(start: -1h)\n  |> filter(fn: (r) => r._measurement == \"cpu\")\n  |> aggregateWindow(every: 1m, fn: mean)",
      "refId": "A"
    }
  ]
}
```

#### SQL面板

```json
{
  "targets": [
    {
      "rawSql": "SELECT timestamp as time, metric_value as value FROM system_metrics WHERE metric_name = 'cpu_usage'",
      "refId": "A"
    }
  ]
}
```

## 故障排除

### 查询语法错误

- **PromQL**: 检查指标名称和标签匹配
- **Flux**: 验证管道语法和函数使用
- **SQL**: 确认表结构和字段名称

### 性能问题

- 减少查询时间范围
- 增加数据聚合级别
- 优化数据库索引
- 使用查询缓存

### 数据不一致

- 检查时间戳格式和时区设置
- 验证数据源连接状态
- 确认数据更新频率

## 生产环境建议

1. **查询优化**: 定期审查和优化查询性能
2. **监控**: 监控查询执行时间和资源使用
3. **安全**: 限制敏感数据的查询权限
4. **备份**: 定期备份重要查询和仪表板配置

## 清理环境

```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（谨慎操作）
docker-compose down -v
```

## 下一步

完成本章节后，您可以继续：
1. 学习第5章：告警和通知配置
2. 创建复杂的多数据源查询
3. 优化查询性能和资源使用
4. 探索高级数据处理技术