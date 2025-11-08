# 企业级监控仪表板示例

## 概述

这个示例展示了如何为Skaffold管理的应用配置完整的监控解决方案，包括：
- Prometheus指标收集
- Grafana仪表板
- 应用性能监控
- 日志聚合

## 目录结构

```
monitoring-dashboard/
├── README.md
├── skaffold.yaml
├── k8s/
│   ├── monitoring/
│   │   ├── prometheus.yaml
│   │   ├── grafana.yaml
│   │   ├── service-monitor.yaml
│   │   └── kustomization.yaml
│   ├── logging/
│   │   ├── fluentd.yaml
│   │   └── elasticsearch.yaml
│   └── app/
│       ├── deployment.yaml
│       └── service.yaml
├── grafana-dashboards/
│   ├── application-metrics.json
│   └── business-metrics.json
└── scripts/
    ├── setup-monitoring.sh
    └── import-dashboards.py
```

## 快速开始

### 1. 部署监控栈

```bash
# 部署完整的监控解决方案
skaffold run --profile=monitoring

# 验证部署
kubectl get pods -n monitoring
kubectl get services -n monitoring
```

### 2. 访问监控界面

```bash
# 获取Grafana访问地址
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# 在浏览器中访问 http://localhost:3000
# 默认用户名/密码: admin/admin
```

### 3. 导入仪表板

```bash
# 导入预配置的仪表板
python scripts/import-dashboards.py
```

## 监控功能

### 应用性能监控
- **响应时间监控**：API请求延迟分布
- **错误率监控**：HTTP错误率和异常检测
- **资源使用监控**：CPU、内存、网络使用情况
- **业务指标监控**：关键业务指标和KPI

### 基础设施监控
- **集群健康状态**：节点状态和资源使用
- **网络性能**：网络延迟和带宽使用
- **存储性能**：存储IOPS和容量使用

### 日志分析
- **结构化日志**：应用日志的收集和分析
- **错误追踪**：错误日志的聚合和追踪
- **性能分析**：慢查询和性能瓶颈分析

## 配置说明

### Prometheus配置

```yaml
# prometheus.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 2
  serviceAccountName: prometheus
  serviceMonitorSelector: {}
  resources:
    requests:
      memory: 400Mi
  ruleSelector:
    matchLabels:
      role: alert-rules
  alerting:
    alertmanagers:
    - namespace: monitoring
      name: alertmanager
      port: web
```

### Grafana配置

```yaml
# grafana.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:9.0.0
        ports:
        - name: http
          containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana
              key: admin-password
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-dashboards
          mountPath: /etc/grafana/provisioning/dashboards
      volumes:
      - name: grafana-storage
        emptyDir: {}
      - name: grafana-dashboards
        configMap:
          name: grafana-dashboards
```

## 高级功能

### 自定义指标

```yaml
# 自定义业务指标
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-metrics
  namespace: monitoring
data:
  custom-metrics.yaml: |
    groups:
    - name: business_metrics
      rules:
      - record: business:revenue_per_minute
        expr: sum(rate(business_revenue_total[5m]))
      - record: business:error_rate
        expr: business_errors_total / business_requests_total
```

### 告警规则

```yaml
# 应用告警规则
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: app-alerts
  namespace: monitoring
spec:
  groups:
  - name: app.rules
    rules:
    - alert: HighErrorRate
      expr: job:http_requests:rate5m{code=~"5.."} > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }}%"
```

## 故障排除

### 常见问题

1. **Prometheus无法抓取指标**
   ```bash
   # 检查ServiceMonitor配置
   kubectl get servicemonitors -n monitoring
   
   # 检查目标发现
   kubectl port-forward svc/prometheus 9090:9090 -n monitoring
   # 访问 http://localhost:9090/targets
   ```

2. **Grafana无法连接数据源**
   ```bash
   # 检查数据源配置
   kubectl logs deployment/grafana -n monitoring
   ```

3. **指标数据缺失**
   ```bash
   # 验证应用指标端点
   kubectl exec -it <pod> -- curl http://localhost:8080/metrics
   ```

这个监控解决方案为企业级应用提供了完整的可观测性能力，帮助团队实时监控应用性能和业务指标。