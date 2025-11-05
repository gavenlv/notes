# Monitoring Role

系统和应用监控角色，用于部署和配置监控解决方案。

## 功能特性

- Prometheus监控系统部署
- Grafana可视化面板配置
- Node Exporter节点监控
- 应用监控集成
- 告警规则配置
- 服务发现配置
- 监控数据持久化
- 性能指标收集

## 支持的监控组件

- Prometheus (默认)
- Grafana
- Node Exporter
- Alertmanager

## 变量

### 默认变量 (defaults/main.yml)

```yaml
# 监控组件配置
monitoring_components:
  - prometheus
  - grafana
  - node_exporter

# Prometheus配置
prometheus_version: "2.30.3"
prometheus_port: 9090
prometheus_retention: "15d"
```

## 使用示例

```yaml
- hosts: monitoring
  roles:
    - role: monitoring
      monitoring_components:
        - prometheus
        - grafana
      prometheus_scrape_configs:
        - job_name: 'web'
          static_configs:
            - targets: ['web1:8080', 'web2:8080']
```

## License

MIT