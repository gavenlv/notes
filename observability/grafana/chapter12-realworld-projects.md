# Chapter 12: Real-world Projects

## 12.1 Complete Monitoring Stack

### 12.1.1 Full Stack Architecture

```
┌─────────────┐
│ Application │ (instrumented with metrics)
└──────┬──────┘
       │
       │ expose /metrics
       ▼
┌─────────────┐
│ Prometheus  │ (scrape & store metrics)
└──────┬──────┘
       │
       │ query
       ▼
┌─────────────┐     ┌──────────┐
│   Grafana   │────▶│   Loki   │ (logs)
└─────────────┘     └──────────┘
       │
       │ traces
       ▼
┌─────────────┐
│   Tempo     │ (distributed tracing)
└─────────────┘
```

### 12.1.2 Docker Compose Stack

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring
    depends_on:
      - prometheus
      - loki
      - tempo

  # Prometheus - Metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    networks:
      - monitoring

  # Loki - Logs
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/loki-config.yml
    volumes:
      - ./loki:/etc/loki
      - loki-data:/loki
    networks:
      - monitoring

  # Promtail - Log collector
  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - ./promtail:/etc/promtail
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/log:/var/log:ro
    command: -config.file=/etc/promtail/promtail-config.yml
    networks:
      - monitoring
    depends_on:
      - loki

  # Tempo - Distributed tracing
  tempo:
    image: grafana/tempo:latest
    container_name: tempo
    ports:
      - "3200:3200"   # tempo
      - "4317:4317"   # otlp grpc
      - "4318:4318"   # otlp http
    command: -config.file=/etc/tempo/tempo.yml
    volumes:
      - ./tempo:/etc/tempo
      - tempo-data:/var/tempo
    networks:
      - monitoring

  # Node Exporter - System metrics
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
    networks:
      - monitoring

  # cAdvisor - Container metrics
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
    networks:
      - monitoring

  # AlertManager - Alert routing
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
    volumes:
      - ./alertmanager:/etc/alertmanager
      - alertmanager-data:/alertmanager
    networks:
      - monitoring

  # Sample application (instrumented)
  app:
    build: ./app
    container_name: sample-app
    ports:
      - "8000:8000"
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
    networks:
      - monitoring

volumes:
  grafana-data:
  prometheus-data:
  loki-data:
  tempo-data:
  alertmanager-data:

networks:
  monitoring:
    driver: bridge
```

See complete stack: [code/chapter12/01-complete-stack/](code/chapter12/01-complete-stack/)

---

## 12.2 Kubernetes Monitoring

### 12.2.1 Architecture

```
Kubernetes Cluster
├── Prometheus Operator
├── Grafana
├── Loki Stack
└── Metrics exporters
    ├── kube-state-metrics
    ├── node-exporter
    └── prometheus-adapter
```

### 12.2.2 Helm Installation

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus Stack (includes Grafana)
helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values values.yaml

# Install Loki Stack
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set prometheus.enabled=false
```

**values.yaml:**
```yaml
grafana:
  enabled: true
  adminPassword: admin123
  
  persistence:
    enabled: true
    size: 10Gi
  
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
        - name: Prometheus
          type: prometheus
          url: http://kube-prometheus-prometheus:9090
          isDefault: true
        
        - name: Loki
          type: loki
          url: http://loki:3100

prometheus:
  prometheusSpec:
    retention: 30d
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: 2000m
        memory: 4Gi
    
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi

alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 10Gi
```

### 12.2.3 Pre-built Dashboards

```bash
# Import community dashboards
# Kubernetes Cluster Monitoring: 7249
# Node Exporter Full: 1860
# Prometheus Stats: 2
```

**Import via provisioning:**
```yaml
# grafana/provisioning/dashboards/k8s.yml
apiVersion: 1

providers:
  - name: 'Kubernetes'
    orgId: 1
    folder: 'Kubernetes'
    type: file
    options:
      path: /var/lib/grafana/dashboards/k8s
```

See K8s setup: [code/chapter12/02-kubernetes-monitoring/](code/chapter12/02-kubernetes-monitoring/)

---

## 12.3 Application Performance Monitoring (APM)

### 12.3.1 Instrumented Application

**Python Flask with OpenTelemetry:**
```python
from flask import Flask
from prometheus_client import Counter, Histogram, generate_latest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

# OpenTelemetry tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://tempo:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

@app.route('/api/users')
@REQUEST_LATENCY.labels('GET', '/api/users').time()
def get_users():
    with tracer.start_as_current_span("get_users"):
        # Business logic
        REQUEST_COUNT.labels('GET', '/api/users', '200').inc()
        return {"users": [{"id": 1, "name": "John"}]}

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 12.3.2 APM Dashboard

**Panels:**
1. Request rate (QPS)
2. Error rate
3. P50/P95/P99 latency
4. Service map (from traces)
5. Top slow endpoints
6. Error logs

**Queries:**
```promql
# Request rate
sum(rate(http_requests_total[5m])) by (endpoint)

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# P95 latency
histogram_quantile(0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

# Slow requests (>1s)
topk(10,
  sum by (endpoint) (http_request_duration_seconds_count > 1)
)
```

See APM example: [code/chapter12/03-apm-monitoring/](code/chapter12/03-apm-monitoring/)

---

## 12.4 Infrastructure Monitoring

### 12.4.1 Multi-Cloud Dashboard

**Data sources:**
- AWS CloudWatch
- Azure Monitor
- Google Cloud Monitoring
- Prometheus (on-prem)

**Dashboard structure:**
```
Row 1: Overview (all clouds)
  - Total VMs
  - Total CPU cores
  - Total memory
  - Monthly cost

Row 2: AWS
  - EC2 instances
  - RDS databases
  - Lambda invocations
  - ELB requests

Row 3: Azure
  - Virtual machines
  - SQL databases
  - App Service requests
  
Row 4: GCP
  - Compute instances
  - Cloud SQL
  - Cloud Run requests

Row 5: On-Premise
  - Physical servers
  - VMware VMs
  - Network devices
```

### 12.4.2 Network Monitoring

**SNMP Exporter configuration:**
```yaml
# Prometheus config
scrape_configs:
  - job_name: 'snmp'
    static_configs:
      - targets:
        - 192.168.1.1  # Switch
        - 192.168.1.2  # Router
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: snmp-exporter:9116
```

**Dashboard panels:**
```promql
# Interface bandwidth
rate(ifHCInOctets[5m]) * 8  # bits per second
rate(ifHCOutOctets[5m]) * 8

# Interface errors
rate(ifInErrors[5m])
rate(ifOutErrors[5m])

# Link status
ifOperStatus == 1  # Up
```

---

## 12.5 Business Metrics Dashboard

### 12.5.1 E-commerce Dashboard

**Data from MySQL:**
```sql
-- Revenue per hour
SELECT
  $__timeGroup(order_time, '1h') AS time,
  SUM(total_amount) AS revenue
FROM orders
WHERE $__timeFilter(order_time)
  AND status = 'completed'
GROUP BY time
ORDER BY time

-- Top products
SELECT
  product_name,
  SUM(quantity) AS units_sold,
  SUM(total_price) AS revenue
FROM order_items
WHERE $__timeFilter(created_at)
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10

-- Conversion rate
SELECT
  DATE(created_at) AS date,
  COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*) * 100 AS conversion_rate
FROM orders
WHERE $__timeFilter(created_at)
GROUP BY date
```

**Panels:**
1. Total revenue (today)
2. Orders count
3. Average order value
4. Conversion rate
5. Revenue trend (time series)
6. Top products (table)
7. Geographic distribution (geomap)
8. Customer segments (pie chart)

---

## 12.6 SRE Dashboard

### 12.6.1 Golden Signals

**Latency:**
```promql
histogram_quantile(0.95,
  sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
)
```

**Traffic:**
```promql
sum by (service) (rate(http_requests_total[5m]))
```

**Errors:**
```promql
sum by (service) (rate(http_requests_total{status=~"5.."}[5m])) /
sum by (service) (rate(http_requests_total[5m])) * 100
```

**Saturation:**
```promql
# CPU
avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100

# Memory
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

### 12.6.2 SLI/SLO Monitoring

**SLI: Availability**
```promql
# 99.9% uptime SLO
sum(up == 1) / count(up) * 100 >= 99.9
```

**SLI: Latency**
```promql
# 95% of requests < 200ms
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
) < 0.2
```

**Error budget:**
```promql
# Remaining error budget (30 days)
(1 - (
  sum(rate(http_requests_total{status=~"5.."}[30d])) /
  sum(rate(http_requests_total[30d]))
)) * 100 - 99.9  # SLO is 99.9%
```

---

## 12.7 Summary

✅ **Complete monitoring stack**: Grafana + Prometheus + Loki + Tempo  
✅ **Kubernetes**: Production-ready K8s monitoring  
✅ **APM**: Application performance monitoring  
✅ **Infrastructure**: Multi-cloud and network monitoring  
✅ **Business metrics**: Revenue, orders, conversions  
✅ **SRE**: Golden signals, SLI/SLO tracking  

---

## 12.8 Best Practices Summary

### 12.8.1 Dashboard Design
- Start with high-level KPIs
- Drill down to details
- Use consistent colors
- Add documentation panels
- Limit panels per dashboard

### 12.8.2 Alerting
- Alert on symptoms, not causes
- Use appropriate severity levels
- Include runbook links
- Set realistic thresholds
- Test alert routing

### 12.8.3 Performance
- Aggregate data before visualizing
- Use recording rules for expensive queries
- Set appropriate refresh intervals
- Cache when possible
- Monitor Grafana itself

### 12.8.4 Security
- Use HTTPS in production
- Enable authentication
- Implement RBAC
- Audit access logs
- Secure API keys

### 12.8.5 Maintenance
- Regular backups (dashboards as JSON)
- Version control configuration
- Document dashboard purposes
- Review and cleanup unused dashboards
- Keep Grafana updated

---

**🎉 Congratulations!** You've completed the Grafana guide from beginner to expert!

**Next Steps:**
1. Build your own monitoring stack
2. Create production dashboards
3. Contribute to Grafana community
4. Explore advanced plugins
5. Join Grafana community forums

**Resources:**
- [Grafana Documentation](https://grafana.com/docs/)
- [Grafana Community](https://community.grafana.com/)
- [Grafana GitHub](https://github.com/grafana/grafana)
- [Dashboard Library](https://grafana.com/grafana/dashboards/)
