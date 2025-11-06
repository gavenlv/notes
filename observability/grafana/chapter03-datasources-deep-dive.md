# Chapter 3: Data Sources Deep Dive

## 3.1 Introduction to Data Sources

### 3.1.1 Data Source Categories

Grafana supports 150+ data source types, categorized as:

**Time Series Databases:**
- Prometheus (metrics)
- InfluxDB (metrics, events)
- Graphite (metrics)
- TimescaleDB (time-series SQL)

**Relational Databases:**
- MySQL
- PostgreSQL
- Microsoft SQL Server
- Oracle

**Logging Systems:**
- Loki (Grafana's log aggregation)
- Elasticsearch
- Splunk

**Cloud Monitoring:**
- AWS CloudWatch
- Azure Monitor
- Google Cloud Monitoring
- Datadog

**Tracing:**
- Jaeger
- Tempo
- Zipkin

**Others:**
- JSON API
- CSV
- TestData
- SimpleJSON

### 3.1.2 Data Source Selection Guide

**Choose based on your data type:**

| Data Type | Best Data Source | Why |
|-----------|------------------|-----|
| Time-series metrics | Prometheus, InfluxDB | Optimized for time-based queries |
| Application logs | Loki, Elasticsearch | Full-text search, filtering |
| Business data | MySQL, PostgreSQL | Complex queries, joins |
| Cloud infrastructure | CloudWatch, Azure Monitor | Native integration |
| Distributed tracing | Jaeger, Tempo | Trace visualization |
| Custom data | JSON API | Flexible integration |

---

## 3.2 Prometheus Deep Dive

Prometheus is the most popular data source for Grafana, especially for Kubernetes and cloud-native monitoring.

### 3.2.1 What is Prometheus?

**Prometheus** is an open-source monitoring system with:
- Time-series database
- Pull-based metric collection
- Powerful query language (PromQL)
- Built-in alerting
- Service discovery

**Architecture:**
```
┌──────────┐
│Exporters │ (expose metrics)
└────┬─────┘
     │
     │ scrape
     ▼
┌──────────┐
│Prometheus│ (collect & store)
└────┬─────┘
     │
     │ query
     ▼
┌──────────┐
│ Grafana  │ (visualize)
└──────────┘
```

### 3.2.2 Installing Prometheus

Using Docker Compose (add to existing stack):

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/rules:/etc/prometheus/rules
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus-data:

networks:
  monitoring:
    driver: bridge
```

**Prometheus Configuration** (`prometheus/prometheus.yml`):
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'my-cluster'
    environment: 'production'

# Load alerting rules
rule_files:
  - /etc/prometheus/rules/*.yml

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
        labels:
          env: 'production'
          datacenter: 'dc1'

  # cAdvisor (container metrics)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Application metrics (example)
  - job_name: 'app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: /metrics
    scrape_interval: 5s
```

See complete example: [code/chapter03/01-prometheus-setup/](code/chapter03/01-prometheus-setup/)

### 3.2.3 Configuring Prometheus in Grafana

**Step 1: Add Data Source**
1. Configuration → Data sources → Add data source
2. Select "Prometheus"

**Step 2: Configure Settings**
```yaml
Name: Prometheus
Default: ✓

HTTP:
  URL: http://prometheus:9090
  Access: Server (default)
  Timeout: 60

Auth:
  (leave unchecked for basic setup)

Prometheus Settings:
  Scrape interval: 15s
  Query timeout: 60s
  HTTP method: POST
  Disable metrics lookup: ☐
  Custom query parameters: (empty)

Misc:
  Exemplars:
    Internal link: ☐
  
  Performance:
    Prometheus type: Prometheus
    Prometheus version: 2.40+
    Cache level: Low
```

**Step 3: Save & Test**

### 3.2.4 PromQL Basics

**PromQL** (Prometheus Query Language) is used to query time-series data.

#### Metric Types

**1. Counter** - Always increasing value
```promql
# Total HTTP requests
http_requests_total

# Rate of increase (requests per second)
rate(http_requests_total[5m])
```

**2. Gauge** - Can go up or down
```promql
# Current CPU usage
node_cpu_usage_percent

# Memory available
node_memory_MemAvailable_bytes
```

**3. Histogram** - Distribution of values
```promql
# Request duration buckets
http_request_duration_seconds_bucket

# Calculate 95th percentile
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)
```

**4. Summary** - Pre-calculated percentiles
```promql
# 95th percentile from summary
http_request_duration_seconds{quantile="0.95"}
```

#### Basic Queries

**Select a metric:**
```promql
# All series for this metric
up

# Specific labels
up{job="prometheus"}

# Multiple label matching
up{job="prometheus", instance="localhost:9090"}

# Label regex matching
up{job=~"prom.*"}

# Negative matching
up{job!="node"}
```

**Operators:**
```promql
# Arithmetic
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

# Comparison (returns 0 or 1)
up == 1  # Is service up?

# Logical
up == 1 and rate(http_requests_total[5m]) > 100
```

**Functions:**
```promql
# rate() - per-second rate over time range
rate(http_requests_total[5m])

# irate() - instant rate (last 2 points)
irate(http_requests_total[5m])

# increase() - total increase over time range
increase(http_requests_total[1h])

# avg_over_time() - average over time
avg_over_time(cpu_usage[1h])

# max_over_time() - maximum over time
max_over_time(response_time[1h])
```

**Aggregation:**
```promql
# Sum across all instances
sum(rate(http_requests_total[5m]))

# Sum by label
sum by (job) (rate(http_requests_total[5m]))

# Average by instance
avg by (instance) (cpu_usage)

# Count number of series
count(up == 1)

# Top 5 instances by CPU
topk(5, cpu_usage)

# Bottom 3 by requests
bottomk(3, rate(http_requests_total[5m]))
```

### 3.2.5 Common Prometheus Queries

**System Metrics (Node Exporter):**

```promql
# CPU usage by mode
rate(node_cpu_seconds_total[5m])

# CPU usage percentage (idle)
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage percentage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Disk I/O rate (read)
rate(node_disk_read_bytes_total[5m])

# Network traffic (received)
rate(node_network_receive_bytes_total[5m])

# Load average
node_load1
node_load5  
node_load15

# Disk IOPS
rate(node_disk_reads_completed_total[5m])
rate(node_disk_writes_completed_total[5m])
```

**Container Metrics (cAdvisor):**

```promql
# Container CPU usage
rate(container_cpu_usage_seconds_total{name!=""}[5m])

# Container memory usage
container_memory_usage_bytes{name!=""}

# Container network I/O
rate(container_network_receive_bytes_total[5m])
rate(container_network_transmit_bytes_total[5m])
```

**HTTP Metrics:**

```promql
# Request rate
rate(http_requests_total[5m])

# Request rate by status code
sum by (status_code) (rate(http_requests_total[5m]))

# Error rate (5xx responses)
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# Request duration (p95, p99)
histogram_quantile(0.95, 
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

# Requests per minute
sum(rate(http_requests_total[1m])) * 60

# Slow requests (>1s)
sum(rate(http_request_duration_seconds_bucket{le="1"}[5m]))
```

**Database Metrics:**

```promql
# Query rate
rate(mysql_global_status_queries[5m])

# Connection count
mysql_global_status_threads_connected

# Slow queries
rate(mysql_global_status_slow_queries[5m])
```

See query examples: [code/chapter03/02-promql-examples/](code/chapter03/02-promql-examples/)

### 3.2.6 Prometheus Recording Rules

Pre-calculate expensive queries and store as new metrics.

**Create recording rules** (`prometheus/rules/recording.yml`):
```yaml
groups:
  - name: node_rules
    interval: 30s
    rules:
      # Pre-calculate CPU usage
      - record: instance:node_cpu:rate5m
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
      
      # Pre-calculate memory usage percentage
      - record: instance:node_memory_usage:percentage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
      
      # Pre-calculate disk usage
      - record: instance:node_disk_usage:percentage
        expr: |
          (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"} / 
           node_filesystem_size_bytes{fstype!~"tmpfs|fuse.lxcfs"})) * 100

  - name: http_rules
    interval: 15s
    rules:
      # Request rate per endpoint
      - record: endpoint:http_requests:rate5m
        expr: |
          sum by (endpoint) (rate(http_requests_total[5m]))
      
      # Error rate percentage
      - record: http_requests:error_rate:percentage
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) /
           sum(rate(http_requests_total[5m]))) * 100
```

**Use in Grafana:**
```promql
# Instead of complex query, use pre-calculated metric
instance:node_cpu:rate5m

# Much faster than calculating every time!
```

---

## 3.3 InfluxDB Deep Dive

InfluxDB is a time-series database optimized for fast, high-availability storage and retrieval of time series data.

### 3.3.1 InfluxDB vs Prometheus

| Feature | InfluxDB | Prometheus |
|---------|----------|------------|
| Data model | Tags + Fields | Labels + Values |
| Write | Push | Pull (scrape) |
| Query language | Flux / InfluxQL | PromQL |
| Retention | Per database | Global |
| Clustering | Enterprise | Federation |
| Best for | IoT, sensors, events | Metrics, monitoring |

### 3.3.2 Installing InfluxDB

**Docker Compose:**
```yaml
version: '3.8'

services:
  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword
      - DOCKER_INFLUXDB_INIT_ORG=myorg
      - DOCKER_INFLUXDB_INIT_BUCKET=mybucket
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=mytoken123456
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2
    networks:
      - monitoring

  # Telegraf - Metrics collection agent
  telegraf:
    image: telegraf:latest
    container_name: telegraf
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - influxdb
    networks:
      - monitoring

volumes:
  influxdb-data:
  influxdb-config:

networks:
  monitoring:
```

**Telegraf Configuration** (`telegraf/telegraf.conf`):
```toml
[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  flush_interval = "10s"

# Output to InfluxDB
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "mytoken123456"
  organization = "myorg"
  bucket = "mybucket"

# Input plugins
[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false

[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs", "devfs"]

[[inputs.mem]]

[[inputs.net]]

[[inputs.system]]

[[inputs.docker]]
  endpoint = "unix:///var/run/docker.sock"
```

### 3.3.3 Configuring InfluxDB in Grafana

**For InfluxDB 2.x:**

```yaml
Name: InfluxDB
Default: ☐

Query Language: Flux

HTTP:
  URL: http://influxdb:8086

Auth:
  Basic auth: ☐

InfluxDB Details:
  Organization: myorg
  Token: mytoken123456
  Default Bucket: mybucket
  Min time interval: 10s
```

**Test query:**
```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> filter(fn: (r) => r._field == "usage_system")
```

### 3.3.4 Flux Query Language

Flux is InfluxDB's functional query language.

**Basic Structure:**
```flux
from(bucket: "mybucket")          // Select data source
  |> range(start: -1h)            // Time range
  |> filter(fn: (r) =>            // Filter
      r._measurement == "cpu")
  |> filter(fn: (r) =>
      r._field == "usage_idle")
  |> aggregateWindow(             // Aggregate
      every: 1m,
      fn: mean)
```

**Common Flux Queries:**

**CPU Usage:**
```flux
from(bucket: "mybucket")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "cpu")
  |> filter(fn: (r) => r["_field"] == "usage_system")
  |> filter(fn: (r) => r["cpu"] == "cpu-total")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

**Memory Usage:**
```flux
from(bucket: "mybucket")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mem")
  |> filter(fn: (r) => r["_field"] == "used_percent")
  |> aggregateWindow(every: v.windowPeriod, fn: mean)
```

**Multiple Fields:**
```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "system")
  |> filter(fn: (r) => r._field =~ /load.*/)  // Regex
  |> aggregateWindow(every: 1m, fn: mean)
```

**Join Multiple Queries:**
```flux
cpu = from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> filter(fn: (r) => r._field == "usage_system")
  |> aggregateWindow(every: 1m, fn: mean)

mem = from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mem")
  |> filter(fn: (r) => r._field == "used_percent")
  |> aggregateWindow(every: 1m, fn: mean)

join(tables: {cpu: cpu, mem: mem}, on: ["_time"])
```

See Flux examples: [code/chapter03/03-influxdb-flux/](code/chapter03/03-influxdb-flux/)

---

## 3.4 MySQL/PostgreSQL Deep Dive

SQL databases are great for business metrics, application data, and custom reporting.

### 3.4.1 When to Use SQL Data Sources

**Use cases:**
- Business KPIs (sales, revenue, users)
- Application database queries
- Custom reports and analytics
- Data that doesn't fit time-series model
- Historical data analysis

### 3.4.2 Setting Up MySQL

**Docker Compose:**
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: grafana_data
      MYSQL_USER: grafana
      MYSQL_PASSWORD: grafanapassword
    volumes:
      - mysql-data:/var/lib/mysql
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - monitoring

volumes:
  mysql-data:
```

**Initialize with Sample Data** (`mysql/init.sql`):
```sql
USE grafana_data;

-- Create metrics table
CREATE TABLE metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name VARCHAR(100),
    value DECIMAL(10, 2),
    tags JSON,
    INDEX idx_timestamp (timestamp),
    INDEX idx_metric (metric_name)
);

-- Create application logs table
CREATE TABLE app_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
    message TEXT,
    service VARCHAR(50),
    INDEX idx_timestamp (timestamp),
    INDEX idx_level (level)
);

-- Create user activity table
CREATE TABLE user_activity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    action VARCHAR(100),
    duration_ms INT,
    success BOOLEAN,
    INDEX idx_timestamp (timestamp),
    INDEX idx_user (user_id)
);

-- Insert sample data
INSERT INTO metrics (metric_name, value, tags) VALUES
    ('cpu_usage', 45.2, '{"host": "server01", "core": "0"}'),
    ('memory_usage', 78.5, '{"host": "server01"}'),
    ('disk_usage', 62.3, '{"host": "server01", "mount": "/"}'),
    ('network_rx', 1250000, '{"host": "server01", "interface": "eth0"}');

-- Generate time series data
DELIMITER $$
CREATE PROCEDURE generate_metrics()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE ts TIMESTAMP;
    
    WHILE i < 1000 DO
        SET ts = DATE_SUB(NOW(), INTERVAL i MINUTE);
        
        INSERT INTO metrics (timestamp, metric_name, value, tags) VALUES
            (ts, 'cpu_usage', 30 + RAND() * 40, '{"host": "server01"}'),
            (ts, 'memory_usage', 60 + RAND() * 30, '{"host": "server01"}'),
            (ts, 'requests_per_sec', 100 + RAND() * 200, '{"endpoint": "/api/users"}');
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL generate_metrics();

-- Create view for aggregated metrics
CREATE VIEW hourly_metrics AS
SELECT 
    DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') AS hour,
    metric_name,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value
FROM metrics
GROUP BY hour, metric_name;
```

### 3.4.3 Configuring MySQL in Grafana

```yaml
Name: MySQL
Default: ☐

MySQL Connection:
  Host: mysql:3306
  Database: grafana_data
  User: grafana
  Password: grafanapassword
  
TLS/SSL Mode: Disable
Max open connections: 100
Max idle connections: 2
Max connection lifetime: 14400
```

### 3.4.4 SQL Queries for Time Series

**Basic Time Series Query:**
```sql
SELECT
  timestamp AS time,
  metric_name AS metric,
  value
FROM metrics
WHERE
  $__timeFilter(timestamp)
  AND metric_name = 'cpu_usage'
ORDER BY timestamp
```

**Grafana SQL Macros:**

| Macro | Description | Example |
|-------|-------------|---------|
| `$__timeFilter(column)` | Adds time range WHERE clause | `WHERE $__timeFilter(created_at)` |
| `$__timeFrom()` | Start of time range | `timestamp >= $__timeFrom()` |
| `$__timeTo()` | End of time range | `timestamp <= $__timeTo()` |
| `$__timeGroup(column, interval)` | Groups by time interval | `$__timeGroup(timestamp, '5m')` |
| `$__unixEpochFilter(column)` | Unix timestamp filter | `$__unixEpochFilter(ts)` |
| `$__unixEpochGroup(column, interval)` | Unix timestamp grouping | `$__unixEpochGroup(ts, '1h')` |

**Time Series with Grouping:**
```sql
SELECT
  $__timeGroup(timestamp, '5m') AS time,
  metric_name AS metric,
  AVG(value) AS value
FROM metrics
WHERE
  $__timeFilter(timestamp)
  AND metric_name IN ('cpu_usage', 'memory_usage')
GROUP BY time, metric
ORDER BY time
```

**Multiple Series:**
```sql
SELECT
  $__timeGroup(timestamp, '1m') AS time,
  CONCAT(metric_name, ' - ', JSON_EXTRACT(tags, '$.host')) AS metric,
  AVG(value) AS value
FROM metrics
WHERE
  $__timeFilter(timestamp)
GROUP BY time, metric
ORDER BY time
```

**Using Variables:**
```sql
SELECT
  $__timeGroup(timestamp, '$interval') AS time,
  metric_name AS metric,
  AVG(value) AS value
FROM metrics
WHERE
  $__timeFilter(timestamp)
  AND JSON_EXTRACT(tags, '$.host') = '$host'
  AND metric_name = '$metric'
GROUP BY time, metric
ORDER BY time
```

**Table Format Query:**
```sql
SELECT
  JSON_EXTRACT(tags, '$.host') AS Host,
  metric_name AS Metric,
  ROUND(AVG(value), 2) AS 'Avg Value',
  ROUND(MAX(value), 2) AS 'Max Value',
  ROUND(MIN(value), 2) AS 'Min Value',
  COUNT(*) AS Samples
FROM metrics
WHERE
  $__timeFilter(timestamp)
GROUP BY Host, Metric
ORDER BY Host, Metric
```

**Current Value (Stat Panel):**
```sql
SELECT
  value
FROM metrics
WHERE
  metric_name = 'cpu_usage'
  AND JSON_EXTRACT(tags, '$.host') = 'server01'
ORDER BY timestamp DESC
LIMIT 1
```

See SQL examples: [code/chapter03/04-mysql-queries/](code/chapter03/04-mysql-queries/)

### 3.4.5 PostgreSQL Configuration

PostgreSQL setup is similar to MySQL:

```yaml
Name: PostgreSQL
Default: ☐

PostgreSQL Connection:
  Host: postgres:5432
  Database: grafana_data
  User: grafana
  Password: grafanapassword
  SSL Mode: disable
  
PostgreSQL details:
  Version: 14+
  TimescaleDB: ☐
  Max open connections: 100
```

**PostgreSQL-specific Query:**
```sql
SELECT
  date_trunc('minute', timestamp) AS time,
  metric_name AS metric,
  AVG(value::numeric) AS value
FROM metrics
WHERE
  timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND metric_name = ANY($metric::text[])
GROUP BY time, metric
ORDER BY time
```

---

## 3.5 Loki for Logs

Loki is Grafana's horizontally-scalable, multi-tenant log aggregation system.

### 3.5.1 Loki Architecture

```
┌────────────┐
│Applications│
└─────┬──────┘
      │
      │ push logs
      ▼
┌────────────┐
│  Promtail  │ (log collector)
└─────┬──────┘
      │
      │ push
      ▼
┌────────────┐
│    Loki    │ (log storage)
└─────┬──────┘
      │
      │ query
      ▼
┌────────────┐
│  Grafana   │ (visualization)
└────────────┘
```

### 3.5.2 Installing Loki

**Docker Compose:**
```yaml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yml:/etc/loki/loki-config.yml
      - loki-data:/loki
    command: -config.file=/etc/loki/loki-config.yml
    networks:
      - monitoring

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - ./promtail/promtail-config.yml:/etc/promtail/promtail-config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/promtail-config.yml
    depends_on:
      - loki
    networks:
      - monitoring

volumes:
  loki-data:
```

**Loki Configuration** (`loki/loki-config.yml`):
```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2023-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

limits_config:
  retention_period: 744h  # 31 days
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

**Promtail Configuration** (`promtail/promtail-config.yml`):
```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Docker container logs
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'stream'

  # System logs
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog
```

### 3.5.3 Configuring Loki in Grafana

```yaml
Name: Loki
Default: ☐

HTTP:
  URL: http://loki:3100

Loki-specific settings:
  Maximum lines: 1000
  Derived fields:
    - Name: traceID
      Regex: traceID=(\w+)
      URL: http://tempo:3200/trace/${__value.raw}
      Internal link: ☑
```

### 3.5.4 LogQL Query Language

**Basic Query:**
```logql
# All logs from a job
{job="api"}

# Filter by label
{job="api", environment="production"}

# Multiple jobs
{job=~"api|worker"}

# Exclude
{job="api", level!="debug"}
```

**Log Filters:**
```logql
# Contains text
{job="api"} |= "error"

# Doesn't contain
{job="api"} != "debug"

# Regex match
{job="api"} |~ "error|failed|exception"

# Regex not match
{job="api"} !~ "GET /health"
```

**Parser:**
```logql
# JSON logs
{job="api"} | json

# Access JSON fields
{job="api"} | json | level="error"

# Logfmt logs
{job="app"} | logfmt

# Regex parsing
{job="nginx"} | regexp "(?P<method>\\w+) (?P<path>[^ ]+)"
```

**Metrics from Logs:**
```logql
# Count log lines
count_over_time({job="api"}[5m])

# Rate of logs
rate({job="api"}[5m])

# Count by level
sum by (level) (count_over_time({job="api"} | json [5m]))

# Error rate
sum(rate({job="api"} |= "error" [5m])) /
sum(rate({job="api"}[5m]))

# Bytes processed
sum(bytes_over_time({job="api"}[5m]))

# Quantile from extracted values
quantile_over_time(0.95, 
  {job="api"} | json | unwrap duration [5m]
)
```

See LogQL examples: [code/chapter03/05-loki-logql/](code/chapter03/05-loki-logql/)

---

## 3.6 Summary

In this chapter, you learned:

✅ **Data source categories** and selection guide  
✅ **Prometheus** installation, configuration, and PromQL  
✅ **InfluxDB** setup and Flux queries  
✅ **MySQL/PostgreSQL** for SQL-based data  
✅ **Loki** for log aggregation and LogQL  
✅ **Practical examples** for each data source  

### What's Next?

In **Chapter 4**, we'll master:
- All visualization types in detail
- Advanced panel configuration
- Custom styling and themes
- Plugin visualizations

---

**Next Chapter**: [Chapter 4: Visualization Mastery](chapter04-visualization-mastery.md)
