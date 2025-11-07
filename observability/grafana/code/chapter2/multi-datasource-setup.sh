#!/bin/bash

# Grafana 多数据源配置实验脚本
# 适用于 Linux/macOS 系统

echo "=== Grafana 多数据源配置实验 ==="

# 配置 Prometheus 数据源
echo "配置 Prometheus 数据源..."
curl -X POST \
  http://admin:admin@localhost:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://localhost:9090",
    "access": "proxy",
    "isDefault": true
  }' | jq .

# 配置 InfluxDB 数据源
echo "配置 InfluxDB 数据源..."
curl -X POST \
  http://admin:admin@localhost:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "InfluxDB",
    "type": "influxdb",
    "url": "http://localhost:8086",
    "access": "proxy",
    "database": "mydb",
    "user": "grafana",
    "password": "password"
  }' | jq .

# 配置 MySQL 数据源
echo "配置 MySQL 数据源..."
curl -X POST \
  http://admin:admin@localhost:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "MySQL",
    "type": "mysql",
    "url": "localhost:3306",
    "access": "proxy",
    "database": "monitoring",
    "user": "grafana",
    "password": "password"
  }' | jq .

# 创建多数据源仪表盘
echo "创建多数据源仪表盘..."
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d '{
    "dashboard": {
      "id": null,
      "title": "多数据源仪表盘",
      "tags": ["实验"],
      "timezone": "browser",
      "panels": [
        {
          "title": "Prometheus 指标",
          "type": "graph",
          "targets": [
            {
              "expr": "up",
              "refId": "A",
              "legendFormat": "{{instance}}"
            }
          ],
          "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
          "datasource": "Prometheus"
        },
        {
          "title": "InfluxDB 指标",
          "type": "graph",
          "targets": [
            {
              "refId": "A",
              "query": "SELECT mean(\"value\") FROM \"cpu\" WHERE $timeFilter GROUP BY time($interval) fill(null)",
              "alias": "CPU使用率"
            }
          ],
          "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
          "datasource": "InfluxDB"
        },
        {
          "title": "MySQL 指标",
          "type": "table",
          "targets": [
            {
              "refId": "A",
              "rawSql": "SELECT hostname, cpu_usage, memory_usage FROM system_metrics WHERE time BETWEEN FROM_UNIXTIME($__unixFrom()) AND FROM_UNIXTIME($__unixTo()) ORDER BY time DESC LIMIT 100",
              "format": "table"
            }
          ],
          "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
          "datasource": "MySQL"
        }
      ],
      "time": {"from": "now-1h", "to": "now"},
      "refresh": "5s"
    },
    "overwrite": false
  }' | jq .

echo "实验完成！"
echo "请访问 http://localhost:3000 查看多数据源仪表盘"
echo "注意：确保 Prometheus、InfluxDB 和 MySQL 服务正在运行且可访问"