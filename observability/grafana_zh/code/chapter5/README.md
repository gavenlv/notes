# 第5章：告警和通知配置 - 可运行代码示例

本章提供了完整的告警和通知配置示例，包括Grafana告警规则、Prometheus告警规则、Alertmanager配置等。

## 快速开始

### 1. 启动服务

```bash
# 进入chapter5目录
cd chapter5

# 启动所有服务
docker-compose up -d
```

### 2. 访问服务

- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### 3. 配置告警规则

1. 在Grafana中创建告警规则
2. 配置通知渠道（邮件、Slack、Webhook等）
3. 测试告警触发和通知

## 服务说明

### Grafana配置
- 预配置的数据源：Prometheus、Alertmanager、Loki
- 告警规则管理
- 通知渠道配置

### Prometheus配置
- 监控指标收集
- 告警规则定义（见`prometheus/alert_rules.yml`）
- Alertmanager集成

### Alertmanager配置
- 告警路由和分组
- 多级通知策略
- 邮件、Webhook通知

## 文件结构

```
chapter5/
├── docker-compose.yml          # 服务编排配置
├── prometheus/
│   ├── prometheus.yml          # Prometheus主配置
│   └── alert_rules.yml         # 告警规则定义
├── alertmanager/
│   └── alertmanager.yml        # Alertmanager配置
├── provisioning/
│   ├── datasources/
│   │   └── datasource.yml      # 数据源自动配置
│   ├── dashboards/
│   │   └── dashboard.yml       # 仪表板自动配置
│   └── alerting/
│       └── alerting.yml        # 告警配置
└── README.md                   # 说明文档
```

## 告警规则示例

本章包含以下告警规则：

### 系统监控告警
- **高CPU使用率**: CPU使用率超过80%持续2分钟
- **高内存使用率**: 内存使用率超过85%持续2分钟
- **磁盘空间不足**: 磁盘使用率超过90%持续5分钟
- **节点宕机**: 节点宕机超过1分钟
- **高网络流量**: 网络流量超过1Gbps持续2分钟

### 服务监控告警
- **Grafana服务宕机**: Grafana服务不可用超过1分钟
- **Prometheus服务宕机**: Prometheus服务不可用超过1分钟

## 通知配置

### 邮件通知
配置SMTP服务器发送邮件通知：
- 默认接收者: alerts@your-domain.com
- 严重告警接收者: critical-alerts@your-domain.com
- 警告接收者: warnings@your-domain.com

### Webhook通知
支持自定义Webhook通知：
- URL: http://webhook-server:8080/alerts
- 支持告警解决通知

## 测试告警

### 1. 模拟高CPU使用率
```bash
# 在node-exporter容器中执行压力测试
docker exec -it node-exporter-chapter5 bash
stress --cpu 2 --timeout 60s
```

### 2. 检查告警状态
- 访问Prometheus: http://localhost:9090/alerts
- 访问Alertmanager: http://localhost:9093
- 检查Grafana告警面板

## 最佳实践

1. **告警分级**: 根据严重程度设置不同的通知策略
2. **告警静默**: 使用Alertmanager的静默功能处理维护窗口
3. **告警聚合**: 合理设置告警分组和等待时间
4. **通知模板**: 自定义通知模板提高可读性
5. **告警测试**: 定期测试告警流程确保可靠性

## 故障排除

### 常见问题

1. **告警未触发**
   - 检查Prometheus配置中的`evaluation_interval`
   - 验证告警表达式是否正确
   - 检查指标数据是否正常收集

2. **通知未发送**
   - 验证SMTP配置是否正确
   - 检查网络连接和防火墙设置
   - 查看Alertmanager日志

3. **告警状态异常**
   - 检查告警规则的`for`持续时间
   - 验证标签匹配规则
   - 检查数据源连接状态

### 日志查看

```bash
# 查看Grafana日志
docker logs grafana-chapter5

# 查看Prometheus日志
docker logs prometheus-chapter5

# 查看Alertmanager日志
docker logs alertmanager-chapter5
```

## 扩展配置

### 添加新的告警规则
在`prometheus/alert_rules.yml`中添加新的告警组：

```yaml
- name: custom_alerts
  rules:
    - alert: CustomAlert
      expr: your_metric > threshold
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "自定义告警"
        description: "自定义告警描述"
```

### 配置新的通知渠道
在`alertmanager/alertmanager.yml`中添加新的receiver：

```yaml
- name: 'slack-receiver'
  slack_configs:
    - api_url: 'https://hooks.slack.com/services/...'
      channel: '#alerts'
      send_resolved: true
```