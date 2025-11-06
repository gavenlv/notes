# Chapter 5: Query Languages Mastery

## 5.1 PromQL Deep Dive

### 5.1.1 Advanced Selectors

```promql
# Regex matching
http_requests_total{job=~"api.*", status!~"[45].."}

# Multiple conditions
http_requests_total{job="api", status="200", method=~"GET|POST"}

# Empty label matching
http_requests_total{status=""}  # Has empty status
http_requests_total{status!=""}  # Has non-empty status
```

### 5.1.2 Range Vectors and Functions

```promql
# rate() - Average per-second rate
rate(http_requests_total[5m])

# irate() - Instant rate (last 2 points)
irate(http_requests_total[5m])

# increase() - Total increase
increase(http_requests_total[1h])

# delta() - Difference between first and last
delta(cpu_temp_celsius[1h])

# deriv() - Derivative (rate of change)
deriv(node_memory_MemFree_bytes[10m])

# predict_linear() - Linear prediction
predict_linear(node_filesystem_free_bytes[1h], 4*3600)
```

### 5.1.3 Aggregation Operators

```promql
# sum - Total across dimensions
sum(rate(http_requests_total[5m]))

# by - Group by labels
sum by (job, instance) (rate(http_requests_total[5m]))

# without - Group by all except
sum without (status) (rate(http_requests_total[5m]))

# avg - Average
avg by (instance) (node_cpu_usage)

# min/max - Minimum/Maximum
max by (job) (up)

# topk/bottomk - Top/Bottom K
topk(5, sum by (endpoint) (rate(http_requests_total[5m])))

# count - Count series
count by (status) (up == 1)

# stddev/stdvar - Standard deviation/variance
stddev(response_time)

# quantile - Calculate quantile
quantile(0.95, response_time)
```

### 5.1.4 Binary Operators

```promql
# Arithmetic
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

# Division (percentage)
(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# Comparison (returns 0 or 1)
node_cpu_usage > 80

# Logical AND
up == 1 and rate(http_requests_total[5m]) > 100

# Logical OR
http_errors_5xx > 10 or http_errors_4xx > 50

# Unless (remove matching)
metric_a unless metric_b
```

### 5.1.5 Vector Matching

```promql
# One-to-one matching
method_code:http_errors:rate5m / ignoring(code) group_left method:http_requests:rate5m

# Many-to-one matching
sum by (instance, job) (rate(node_cpu_seconds_total[5m])) 
  * on(instance, job) group_left(hostname) node_uname_info

# Many-to-many matching
label_replace(metric, "new_label", "$1", "old_label", "(.+)")
```

### 5.1.6 Histogram Functions

```promql
# histogram_quantile - Calculate percentiles
histogram_quantile(0.95, 
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

# Multiple percentiles
histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

### 5.1.7 Time Functions

```promql
# timestamp() - Unix timestamp of sample
timestamp(metric)

# day_of_month(), day_of_week(), hour(), minute()
hour() >= 9 and hour() < 17  # Business hours

# year(), month(), days_in_month()
month() == 12  # December only
```

### 5.1.8 Subqueries

```promql
# Query rate of rate
rate(rate(metric[5m])[5m:1m])

# Max over time
max_over_time(rate(http_requests_total[5m])[1h:])

# Average of p95 over last hour
avg_over_time(histogram_quantile(0.95, rate(latency_bucket[5m]))[1h:])
```

See PromQL examples: [code/chapter05/01-promql-advanced/](code/chapter05/01-promql-advanced/)

---

## 5.2 Flux for InfluxDB

### 5.2.1 Flux Basics

```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> filter(fn: (r) => r._field == "usage_system")
  |> aggregateWindow(every: 1m, fn: mean)
```

### 5.2.2 Common Functions

```flux
// Filtering
from(bucket: "mybucket")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "mem" and r._field == "used_percent")

// Aggregation
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)

// Math operations
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mem")
  |> map(fn: (r) => ({ r with _value: r._value / 1024.0 / 1024.0 }))

// Pivot (wide format)
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "system")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")

// Join
cpu = from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")

mem = from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mem")

join(tables: {cpu: cpu, mem: mem}, on: ["_time", "host"])
```

---

## 5.3 SQL for Relational Databases

### 5.3.1 Time Series Queries

```sql
-- MySQL time series
SELECT
  $__timeGroup(timestamp, '5m') AS time,
  AVG(cpu_usage) AS cpu,
  AVG(memory_usage) AS memory
FROM metrics
WHERE $__timeFilter(timestamp)
  AND server_id = $server_id
GROUP BY time
ORDER BY time

-- PostgreSQL with advanced functions
SELECT
  date_trunc('minute', timestamp) AS time,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY response_time) AS p95,
  percentile_cont(0.99) WITHIN GROUP (ORDER BY response_time) AS p99
FROM requests
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY time
ORDER BY time
```

### 5.3.2 Table Queries

```sql
-- Current status
SELECT
  server_name,
  ROUND(cpu_usage, 1) AS 'CPU %',
  ROUND(memory_usage, 1) AS 'Memory %',
  CASE 
    WHEN status = 'up' THEN '✓'
    WHEN status = 'down' THEN '✗'
    ELSE '?'
  END AS Status,
  last_check AS 'Last Check'
FROM server_status
WHERE last_check > NOW() - INTERVAL 5 MINUTE
ORDER BY cpu_usage DESC

-- Aggregated stats
SELECT
  DATE(timestamp) AS Date,
  COUNT(*) AS 'Total Requests',
  SUM(CASE WHEN status >= 500 THEN 1 ELSE 0 END) AS '5xx Errors',
  ROUND(AVG(response_time), 2) AS 'Avg Response (ms)',
  ROUND(MAX(response_time), 2) AS 'Max Response (ms)'
FROM http_logs
WHERE $__timeFilter(timestamp)
GROUP BY Date
ORDER BY Date DESC
```

### 5.3.3 Using Variables

```sql
SELECT
  $__timeGroup(timestamp, '$interval') AS time,
  endpoint,
  COUNT(*) AS requests
FROM http_logs
WHERE
  $__timeFilter(timestamp)
  AND endpoint IN ($endpoint)
  AND status_code IN ($status_code)
  AND server_name = '$server'
GROUP BY time, endpoint
ORDER BY time
```

---

## 5.4 LogQL for Loki

### 5.4.1 Log Stream Selectors

```logql
# Basic selector
{job="api"}

# Multiple labels
{job="api", env="production", level="error"}

# Regex matching
{job=~"api|worker"}

# Negative matching
{job="api", level!="debug"}
```

### 5.4.2 Line Filters

```logql
# Contains
{job="api"} |= "error"

# Doesn't contain
{job="api"} != "GET /health"

# Regex match
{job="api"} |~ "error|failed|exception"

# Regex not match
{job="api"} !~ "GET (/_health|/metrics)"

# Multiple filters
{job="api"} |= "error" != "timeout" |~ "database|connection"
```

### 5.4.3 Parser Expressions

```logql
# JSON logs
{job="api"} | json

# Access fields
{job="api"} | json | level="error"

# Logfmt
{job="app"} | logfmt

# Regex pattern
{job="nginx"} | regexp "(?P<method>\\w+) (?P<path>[^ ]+) (?P<status>\\d+)"

# Unpack
{job="api"} | json | line_format "{{.level}}: {{.message}}"
```

### 5.4.4 Metrics from Logs

```logql
# Count log lines
count_over_time({job="api"}[5m])

# Rate of logs
rate({job="api"}[5m])

# Count by level
sum by (level) (count_over_time({job="api"} | json [5m]))

# Bytes per second
sum(bytes_over_time({job="api"}[5m])) / 300

# Quantile from extracted value
quantile_over_time(0.95,
  {job="api"} | json | unwrap duration [5m]
)

# avg/min/max/sum over time
avg_over_time({job="api"} | json | unwrap response_time [5m])
```

### 5.4.5 Label Filters After Parsing

```logql
# Parse then filter
{job="api"} 
  | json 
  | level="error" 
  | status_code >= 500

# Multiple conditions
{job="api"} 
  | json 
  | level="error" and user_id != "" 
  | line_format "User {{.user_id}}: {{.message}}"
```

See LogQL examples: [code/chapter05/02-logql-advanced/](code/chapter05/02-logql-advanced/)

---

## 5.5 Summary

✅ **PromQL**: Advanced functions, aggregations, histograms  
✅ **Flux**: InfluxDB queries and transformations  
✅ **SQL**: Time series and table queries  
✅ **LogQL**: Log queries and metrics from logs  

**Next Chapter**: [Chapter 6: Variables and Templating](chapter06-variables-templating.md)
