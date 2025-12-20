# 第2章：数据源配置和连接 - 代码示例

## 概述

本目录包含第2章教程的完整可运行代码示例，演示如何配置和连接多种数据源到Grafana。

## 快速开始

### 1. 启动所有服务

```bash
# 进入chapter2目录
cd chapter2

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
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

## 服务说明

### Prometheus

- **用途**: 时间序列数据收集和存储
- **配置**: `prometheus/prometheus.yml`
- **监控目标**: Node Exporter、Grafana自身
- **数据**: 系统指标、容器指标

### InfluxDB

- **用途**: 时间序列数据库
- **版本**: InfluxDB 2.x
- **组织**: myorg
- **存储桶**: mybucket
- **认证**: Token认证

### MySQL

- **用途**: 关系型数据库示例
- **数据库**: grafana_demo
- **包含**: 系统指标、应用指标、业务指标表
- **视图**: 聚合视图用于仪表板

### Node Exporter

- **用途**: 系统指标收集器
- **数据**: CPU、内存、磁盘、网络指标
- **端口**: 9100

## 数据源配置详解

### Prometheus数据源

```yaml
- name: Prometheus
  type: prometheus
  url: http://prometheus:9090
  jsonData:
    timeInterval: 15s  # 查询时间间隔
    httpMethod: GET    # HTTP方法
```

### InfluxDB数据源

```yaml
- name: InfluxDB
  type: influxdb
  url: http://influxdb:8086
  jsonData:
    version: Flux      # 使用Flux查询语言
    organization: myorg
    defaultBucket: mybucket
```

### MySQL数据源

```yaml
- name: MySQL
  type: mysql
  url: mysql:3306
  database: grafana_demo
  jsonData:
    maxOpenConns: 10     # 最大连接数
    maxIdleConns: 10     # 空闲连接数
    connMaxLifetime: 14400  # 连接生命周期
```

## 示例查询

### PromQL查询示例

```promql
# CPU使用率
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# 磁盘使用率
(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100
```

### Flux查询示例

```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> filter(fn: (r) => r._field == "usage")
  |> aggregateWindow(every: 1m, fn: mean)
```

### SQL查询示例

```sql
-- 系统指标查询
SELECT 
    timestamp as time,
    hostname,
    cpu_usage as value
FROM system_metrics
WHERE timestamp >= NOW() - INTERVAL 1 HOUR
ORDER BY timestamp DESC

-- 应用性能查询
SELECT 
    hour as time,
    app_name,
    avg_response_time as value
FROM application_performance
WHERE hour >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
```

## 仪表板示例

### 创建系统监控仪表板

1. 左侧菜单 → Create → Dashboard
2. 添加新的Panel
3. 选择Prometheus数据源
4. 使用上面的PromQL查询
5. 配置可视化选项

### 导入预配置仪表板

```bash
# 使用API导入示例仪表板
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(curl -X POST -H "Content-Type: application/json" -d '{"name":"apikey","role":"Admin"}' http://admin:admin123@localhost:3000/api/auth/keys | jq -r .key)" \
  -d @sample-dashboard.json
```

## 故障排除

### 数据源连接失败

检查服务状态：
```bash
docker-compose logs prometheus
docker-compose logs influxdb
docker-compose logs mysql
```

### 端口冲突

修改`docker-compose.yml`中的端口映射：
```yaml
ports:
  - "3001:3000"  # Grafana
  - "9091:9090"  # Prometheus
  - "8087:8086"  # InfluxDB
  - "3307:3306"  # MySQL
```

### 内存不足

限制容器内存使用：
```yaml
deploy:
  resources:
    limits:
      memory: 512M
```

## 生产环境建议

1. **安全配置**: 修改默认密码，启用TLS
2. **数据持久化**: 配置数据备份策略
3. **监控**: 监控数据源健康状态
4. **性能**: 优化查询和索引
5. **高可用**: 配置集群和负载均衡

## 清理环境

```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（谨慎操作）
docker-compose down -v
```

## 下一步

完成本章节后，您可以继续：
1. 学习第3章：仪表板创建和面板配置
2. 创建自定义查询和可视化
3. 探索不同数据源的特性
4. 优化查询性能