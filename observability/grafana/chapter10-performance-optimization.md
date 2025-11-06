# Chapter 10: Performance Optimization

## 10.1 Query Optimization

### 10.1.1 PromQL Optimization

**❌ Inefficient:**
```promql
# Queries all series
rate(http_requests_total[5m])

# Too many series
histogram_quantile(0.95, http_request_duration_seconds_bucket)
```

**✅ Optimized:**
```promql
# Aggregate first
sum by (job) (rate(http_requests_total[5m]))

# Filter labels
histogram_quantile(0.95, 
  sum by (le, job) (rate(http_request_duration_seconds_bucket{job="api"}[5m]))
)
```

### 10.1.2 Recording Rules

Pre-calculate expensive queries in Prometheus.

```yaml
# prometheus/rules/recording.yml
groups:
  - name: http_rules
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
      
      - record: job:http_request_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum by (le, job) (rate(http_request_duration_seconds_bucket[5m]))
          )
```

**Use in Grafana:**
```promql
job:http_requests:rate5m
job:http_request_duration:p95
```

### 10.1.3 SQL Optimization

**❌ Inefficient:**
```sql
SELECT * FROM metrics WHERE timestamp > NOW() - INTERVAL 7 DAY
```

**✅ Optimized:**
```sql
SELECT 
  timestamp,
  metric_name,
  value
FROM metrics
WHERE
  timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND metric_name = '$metric'
  AND server_id IN ($server_id)
LIMIT 10000
```

**Indexes:**
```sql
CREATE INDEX idx_timestamp ON metrics(timestamp);
CREATE INDEX idx_metric ON metrics(metric_name, timestamp);
```

---

## 10.2 Dashboard Optimization

### 10.2.1 Reduce Panel Count

**Guidelines:**
- Max 20-30 panels per dashboard
- Use rows for organization
- Create drill-down dashboards

### 10.2.2 Query Limits

```yaml
Max data points: 1000 (default)
Min interval: 15s (match scrape interval)
Timeout: 60s
```

### 10.2.3 Disable Unused Features

**Per panel:**
```yaml
Legend: Hide if not needed
Tooltip: Single series only
Query inspector: Only for debugging
```

---

## 10.3 Caching

### 10.3.1 Query Result Caching

**Data source settings:**
```yaml
Cache timeout: 60s
Query timeout: 60s
```

**Configuration:**
```ini
[caching]
enabled = true

[caching.memory]
enabled = true
ttl = 1m
```

### 10.3.2 Dashboard Caching

**Browser caching:**
```ini
[server]
static_root_path = public
enable_gzip = true
```

### 10.3.3 Image Rendering Cache

```ini
[rendering]
concurrent_render_limit = 5
```

---

## 10.4 Resource Optimization

### 10.4.1 Grafana Configuration

```ini
[database]
# Connection pooling
max_open_conn = 100
max_idle_conn = 2
conn_max_lifetime = 14400

[server]
# Enable gzip
enable_gzip = true

[analytics]
# Reduce reporting
reporting_enabled = false
```

### 10.4.2 Docker Resources

```yaml
services:
  grafana:
    image: grafana/grafana:latest
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 10.5 Monitoring Grafana

### 10.5.1 Grafana Metrics

**Enable metrics endpoint:**
```ini
[metrics]
enabled = true
basic_auth_username = metrics
basic_auth_password = password
```

**Access:**
```
http://localhost:3000/metrics
```

**Key metrics:**
```promql
# Request duration
grafana_http_request_duration_seconds

# Active users
grafana_stat_active_users

# Dashboard load time
grafana_dashboard_load_milliseconds

# Database queries
grafana_database_queries_total
```

### 10.5.2 Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
    metrics_path: /metrics
    basic_auth:
      username: metrics
      password: password
```

### 10.5.3 Self-Monitoring Dashboard

Create dashboard to monitor Grafana itself:
```promql
# HTTP request rate
rate(grafana_http_request_duration_seconds_count[5m])

# Error rate
rate(grafana_http_request_duration_seconds_count{status_code=~"5.."}[5m])

# 95th percentile latency
histogram_quantile(0.95, 
  rate(grafana_http_request_duration_seconds_bucket[5m])
)

# Active users
grafana_stat_active_users

# Dashboard count
grafana_stat_total_dashboards
```

---

## 10.6 Troubleshooting

### 10.6.1 Slow Dashboards

**Diagnose:**
1. Open Query Inspector (Panel → Inspect → Stats)
2. Check query execution time
3. Look for queries taking >1s

**Solutions:**
- Add query caching
- Reduce time range
- Use recording rules
- Aggregate data first
- Add database indexes

### 10.6.2 High Memory Usage

**Check:**
```bash
docker stats grafana
```

**Solutions:**
- Reduce concurrent queries
- Limit data points
- Increase cache timeout
- Restart Grafana periodically

### 10.6.3 Database Issues

**SQLite limitations:**
- Not recommended for production
- Max ~100 users
- Limited concurrent writes

**Solution:**
```ini
[database]
type = postgres
host = postgres:5432
name = grafana
user = grafana
password = password
```

### 10.6.4 Network Timeouts

**Increase timeouts:**
```ini
[dataproxy]
timeout = 300
keep_alive_seconds = 30
```

**Per data source:**
```yaml
Timeout: 120s
```

---

## 10.7 Summary

✅ **Query optimization**: PromQL, SQL, recording rules  
✅ **Dashboard optimization**: Reduce panels, set limits  
✅ **Caching**: Query and dashboard caching  
✅ **Resources**: Docker limits, database config  
✅ **Monitoring**: Self-monitoring metrics  
✅ **Troubleshooting**: Common issues and solutions  

**Next Chapter**: [Chapter 11: Enterprise Features](chapter11-enterprise-features.md)
