#!/usr/bin/env python3
"""
查询语言示例数据生成器 - 为第4章生成PromQL、Flux、SQL查询示例数据
"""

import time
import random
import json
from datetime import datetime, timedelta
import requests

def generate_prometheus_metrics():
    """生成Prometheus格式的指标数据"""
    
    # 模拟向Prometheus推送数据
    base_time = int(time.time()) - 3600  # 1小时前开始
    
    metrics_data = []
    
    # 生成CPU指标
    for i in range(60):  # 60个数据点，每分钟一个
        timestamp = base_time + i * 60
        
        # CPU使用率指标
        cpu_usage = random.uniform(10, 90)
        metrics_data.append({
            "metric": {
                "__name__": "node_cpu_seconds_total",
                "mode": "idle",
                "instance": "server-01",
                "job": "node"
            },
            "values": [timestamp, str(100 - cpu_usage)]
        })
        
        # 内存使用指标
        memory_usage = random.uniform(20, 80)
        metrics_data.append({
            "metric": {
                "__name__": "node_memory_usage_percentage",
                "instance": "server-01", 
                "job": "node"
            },
            "values": [timestamp, str(memory_usage)]
        })
        
        # 磁盘使用指标
        disk_usage = random.uniform(30, 85)
        metrics_data.append({
            "metric": {
                "__name__": "node_disk_usage_percentage",
                "device": "sda1",
                "instance": "server-01",
                "job": "node"
            },
            "values": [timestamp, str(disk_usage)]
        })
    
    return metrics_data

def generate_influxdb_data():
    """生成InfluxDB格式的数据"""
    
    data_points = []
    base_time = datetime.utcnow() - timedelta(hours=1)
    
    for i in range(60):  # 60个数据点
        timestamp = base_time + timedelta(minutes=i)
        
        # CPU测量数据
        data_points.append({
            "measurement": "cpu",
            "tags": {
                "host": "server-01",
                "region": "us-west"
            },
            "time": timestamp.isoformat() + "Z",
            "fields": {
                "usage": random.uniform(10, 90),
                "temperature": random.uniform(40, 80)
            }
        })
        
        # 内存测量数据
        data_points.append({
            "measurement": "memory", 
            "tags": {
                "host": "server-01",
                "region": "us-west"
            },
            "time": timestamp.isoformat() + "Z",
            "fields": {
                "used": random.randint(4, 16),
                "available": random.randint(16, 32)
            }
        })
    
    return data_points

def generate_sql_data():
    """生成SQL查询示例数据"""
    
    # 创建示例表结构
    table_definitions = {
        "system_metrics": """
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            hostname VARCHAR(50),
            metric_name VARCHAR(50),
            metric_value DECIMAL(10,4),
            tags JSON
        )
        """,
        
        "application_logs": """
        CREATE TABLE IF NOT EXISTS application_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            app_name VARCHAR(50),
            level VARCHAR(20),
            message TEXT,
            duration_ms INT
        )
        """
    }
    
    # 生成示例数据
    sample_data = {
        "system_metrics": [],
        "application_logs": []
    }
    
    base_time = datetime.utcnow() - timedelta(hours=24)
    
    # 生成系统指标数据
    metrics = ["cpu_usage", "memory_usage", "disk_usage", "network_rx", "network_tx"]
    hosts = ["web-01", "web-02", "db-01", "cache-01"]
    
    for i in range(100):
        timestamp = base_time + timedelta(minutes=i * 15)
        
        for host in hosts:
            for metric in metrics:
                value = random.uniform(0, 100) if "usage" in metric else random.randint(1000, 100000)
                
                sample_data["system_metrics"].append({
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "hostname": host,
                    "metric_name": metric,
                    "metric_value": round(value, 4),
                    "tags": json.dumps({"environment": "production", "team": "infra"})
                })
    
    # 生成应用日志数据
    levels = ["INFO", "WARN", "ERROR"]
    apps = ["web-api", "auth-service", "payment-service"]
    
    for i in range(50):
        timestamp = base_time + timedelta(minutes=i * 30)
        
        sample_data["application_logs"].append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "app_name": random.choice(apps),
            "level": random.choice(levels),
            "message": f"Sample log message {i}",
            "duration_ms": random.randint(10, 500)
        })
    
    return table_definitions, sample_data

def push_to_prometheus(metrics_data):
    """将数据推送到Prometheus（模拟）"""
    print("模拟向Prometheus推送数据...")
    print(f"生成 {len(metrics_data)} 个指标数据点")
    
    # 在实际环境中，这里会使用Prometheus的remote_write API
    # 为了演示，我们只打印示例数据
    for i, metric in enumerate(metrics_data[:3]):  # 只显示前3个示例
        print(f"示例指标 {i+1}: {metric}")

def push_to_influxdb(data_points):
    """将数据推送到InfluxDB（模拟）"""
    print("模拟向InfluxDB推送数据...")
    print(f"生成 {len(data_points)} 个数据点")
    
    # 在实际环境中，这里会使用InfluxDB的write API
    for i, point in enumerate(data_points[:3]):  # 只显示前3个示例
        print(f"示例数据点 {i+1}: {point}")

def setup_mysql_tables(table_definitions, sample_data):
    """设置MySQL表结构和示例数据"""
    print("设置MySQL表结构...")
    
    for table_name, create_sql in table_definitions.items():
        print(f"创建表 {table_name}:")
        print(create_sql)
        print()
    
    print("生成示例数据:")
    for table_name, data in sample_data.items():
        print(f"表 {table_name}: {len(data)} 条记录")

def main():
    """主函数"""
    print("开始生成查询语言示例数据...")
    
    # 生成Prometheus数据
    print("\n1. 生成Prometheus指标数据")
    prometheus_data = generate_prometheus_metrics()
    push_to_prometheus(prometheus_data)
    
    # 生成InfluxDB数据
    print("\n2. 生成InfluxDB时间序列数据")
    influxdb_data = generate_influxdb_data()
    push_to_influxdb(influxdb_data)
    
    # 生成SQL数据
    print("\n3. 生成SQL关系型数据")
    table_defs, sql_data = generate_sql_data()
    setup_mysql_tables(table_defs, sql_data)
    
    # 保存示例查询
    print("\n4. 生成示例查询语句")
    
    queries = {
        "promql": [
            "# CPU使用率查询\n100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "# 内存使用率查询\nnode_memory_usage_percentage",
            "# 磁盘使用率预测\npredict_linear(node_disk_usage_percentage[1h], 3600)"
        ],
        "flux": [
            """# 基础查询管道
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "cpu")
  |> filter(fn: (r) => r._field == "usage")
  |> aggregateWindow(every: 1m, fn: mean)""",
            """# 数据转换和计算
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "memory")
  |> map(fn: (r) => ({ r with usage_percentage: r._value / 32.0 * 100.0 }))"""
        ],
        "sql": [
            """-- 系统指标聚合查询
SELECT 
    hostname,
    metric_name,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value
FROM system_metrics 
WHERE timestamp >= NOW() - INTERVAL 1 HOUR
GROUP BY hostname, metric_name
ORDER BY avg_value DESC""",
            """-- 应用错误率统计
SELECT 
    app_name,
    COUNT(*) as total_logs,
    SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) as error_count,
    ROUND(SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as error_rate
FROM application_logs 
WHERE timestamp >= NOW() - INTERVAL 24 HOUR
GROUP BY app_name
HAVING error_count > 0"""
        ]
    }
    
    # 保存查询示例
    with open('query_examples.json', 'w') as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    
    print("\n数据生成完成!")
    print("示例查询已保存到 query_examples.json")
    print("\n下一步:")
    print("1. 启动所有服务: docker-compose up -d")
    print("2. 访问Grafana: http://localhost:3000")
    print("3. 使用示例查询创建仪表板")

if __name__ == "__main__":
    main()