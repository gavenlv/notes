# 第4章：Exporters与数据采集

> **学习时长**: 6-8小时  
> **难度**: ⭐⭐⭐  
> **重要性**: ⭐⭐⭐⭐⭐

## 本章目标

学完本章后,你将能够:

- ✅ 理解Exporter的工作原理和架构
- ✅ 熟练使用Node Exporter监控Linux系统
- ✅ 使用cAdvisor监控Docker容器
- ✅ 掌握常见中间件Exporters(MySQL、Redis、Nginx等)
- ✅ 开发自定义Exporter(Python、Go)
- ✅ 理解Pushgateway的使用场景
- ✅ 实现黑盒监控(Blackbox Exporter)
- ✅ 设计合理的监控指标体系

---

## 4.1 Exporter概述

### 4.1.1 什么是Exporter?

**Exporter**是一个独立的程序,负责:
1. 从目标系统采集数据(系统、应用、中间件等)
2. 将数据转换为Prometheus可识别的格式
3. 通过HTTP接口暴露指标供Prometheus抓取

**工作流程**:

```
目标系统 → Exporter → HTTP /metrics接口 → Prometheus抓取
   ↓
 数据源        ↓
 (系统、      转换为
  应用、      Prometheus
  中间件)      格式
```

### 4.1.2 Exporter类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **官方Exporter** | Prometheus官方维护 | Node Exporter, Blackbox Exporter |
| **第三方Exporter** | 社区/厂商维护 | MySQL Exporter, Redis Exporter |
| **内置Exporter** | 应用直接暴露指标 | Kubernetes, etcd |
| **自定义Exporter** | 根据业务需求开发 | 业务指标采集器 |

### 4.1.3 常见Exporters一览

| Exporter | 用途 | 端口 |
|----------|------|------|
| **Node Exporter** | Linux系统监控 | 9100 |
| **Windows Exporter** | Windows系统监控 | 9182 |
| **MySQL Exporter** | MySQL数据库监控 | 9104 |
| **Redis Exporter** | Redis监控 | 9121 |
| **Nginx Exporter** | Nginx监控 | 9113 |
| **PostgreSQL Exporter** | PostgreSQL监控 | 9187 |
| **Blackbox Exporter** | 黑盒探测(HTTP/HTTPS/TCP/ICMP) | 9115 |
| **cAdvisor** | 容器监控 | 8080 |
| **Pushgateway** | 短期任务指标推送 | 9091 |
| **JMX Exporter** | Java应用监控 | 自定义 |

---

## 4.2 Node Exporter - 系统监控

### 4.2.1 Node Exporter简介

**Node Exporter**是Prometheus官方提供的系统监控Exporter,可以采集:

- 📊 CPU使用率、负载
- 💾 内存使用情况
- 💿 磁盘IO、空间使用
- 🌐 网络流量、连接数
- ⏱️ 系统运行时间
- 📂 文件系统信息

### 4.2.2 安装Node Exporter

**方法1: Docker方式** (推荐用于学习)

```bash
docker run -d \
  --name=node-exporter \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  prom/node-exporter:latest \
  --path.rootfs=/host
```

**方法2: 二进制安装** (生产环境推荐)

```bash
# 下载
VERSION=1.7.0
wget https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/node_exporter-${VERSION}.linux-amd64.tar.gz

# 解压
tar xvfz node_exporter-${VERSION}.linux-amd64.tar.gz
cd node_exporter-${VERSION}.linux-amd64

# 运行
./node_exporter

# 访问指标
curl http://localhost:9100/metrics
```

**方法3: systemd服务**

创建服务文件`/etc/systemd/system/node-exporter.service`:

```ini
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/node_exporter \
  --collector.filesystem.mount-points-exclude=^/(dev|proc|sys|var/lib/docker/.+)($|/) \
  --collector.filesystem.fs-types-exclude=^(autofs|binfmt_misc|bpf|cgroup2?|configfs|debugfs|devpts|devtmpfs|fusectl|hugetlbfs|iso9660|mqueue|nsfs|overlay|proc|procfs|pstore|rpc_pipefs|securityfs|selinuxfs|squashfs|sysfs|tracefs)$

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable node-exporter
sudo systemctl start node-exporter
sudo systemctl status node-exporter
```

### 4.2.3 配置Prometheus抓取

在`prometheus.yml`中添加:

```yaml
scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          instance: 'server-01'
          datacenter: 'dc1'
          role: 'web-server'
```

### 4.2.4 Node Exporter核心指标

#### CPU指标

```promql
# CPU使用时间(秒)
node_cpu_seconds_total{mode}

# CPU核心数
count(node_cpu_seconds_total{mode="idle"}) without (cpu, mode)

# CPU使用率
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 各模式CPU使用率
sum by (mode) (rate(node_cpu_seconds_total[5m])) * 100
```

**CPU模式说明**:
- `idle`: 空闲
- `user`: 用户态
- `system`: 内核态
- `iowait`: 等待IO
- `irq`: 硬件中断
- `softirq`: 软件中断
- `steal`: 虚拟化环境被偷走的CPU时间

#### 内存指标

```promql
# 总内存(字节)
node_memory_MemTotal_bytes

# 可用内存(字节)
node_memory_MemAvailable_bytes

# 已用内存(字节)
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

# 内存使用率
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# Swap总量
node_memory_SwapTotal_bytes

# Swap已用
node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes

# Swap使用率
(1 - node_memory_SwapFree_bytes / node_memory_SwapTotal_bytes) * 100

# Buffer缓存
node_memory_Buffers_bytes

# Page缓存
node_memory_Cached_bytes
```

#### 磁盘指标

```promql
# 磁盘总容量
node_filesystem_size_bytes{fstype!~"tmpfs|devtmpfs"}

# 磁盘可用空间
node_filesystem_avail_bytes{fstype!~"tmpfs|devtmpfs"}

# 磁盘使用率
(node_filesystem_size_bytes - node_filesystem_avail_bytes) 
/ node_filesystem_size_bytes * 100

# 磁盘读取字节数
node_disk_read_bytes_total

# 磁盘写入字节数
node_disk_written_bytes_total

# 磁盘读取速率(MB/s)
rate(node_disk_read_bytes_total[5m]) / 1024 / 1024

# 磁盘写入速率(MB/s)
rate(node_disk_written_bytes_total[5m]) / 1024 / 1024

# 磁盘IO时间占比
rate(node_disk_io_time_seconds_total[5m]) * 100

# 磁盘inode使用率
(node_filesystem_files - node_filesystem_files_free) 
/ node_filesystem_files * 100
```

#### 网络指标

```promql
# 网络接收字节数
node_network_receive_bytes_total{device!~"lo|docker.*|veth.*"}

# 网络发送字节数
node_network_transmit_bytes_total{device!~"lo|docker.*|veth.*"}

# 网络接收速率(Mbps)
rate(node_network_receive_bytes_total[5m]) * 8 / 1024 / 1024

# 网络发送速率(Mbps)
rate(node_network_transmit_bytes_total[5m]) * 8 / 1024 / 1024

# 网络错误包
node_network_receive_errs_total
node_network_transmit_errs_total

# 网络丢包
node_network_receive_drop_total
node_network_transmit_drop_total

# 网络错误率
rate(node_network_receive_errs_total[5m]) 
/ rate(node_network_receive_packets_total[5m]) * 100
```

#### 系统负载指标

```promql
# 1分钟负载
node_load1

# 5分钟负载
node_load5

# 15分钟负载
node_load15

# 系统运行时间(秒)
node_boot_time_seconds

# 系统启动时间戳
node_time_seconds - node_boot_time_seconds
```

### 4.2.5 Node Exporter高级配置

**启用/禁用特定采集器**:

```bash
# 只启用CPU和内存采集器
./node_exporter \
  --collector.disable-defaults \
  --collector.cpu \
  --collector.meminfo

# 禁用某些采集器
./node_exporter \
  --no-collector.arp \
  --no-collector.bcache \
  --no-collector.bonding
```

**文本文件采集器** (采集自定义指标):

```bash
# 启用textfile采集器
./node_exporter \
  --collector.textfile.directory=/var/lib/node_exporter/textfile_collector
```

创建自定义指标文件`/var/lib/node_exporter/textfile_collector/custom.prom`:

```
# HELP custom_backup_last_success_timestamp 上次备份成功时间戳
# TYPE custom_backup_last_success_timestamp gauge
custom_backup_last_success_timestamp 1699876543

# HELP custom_backup_files_total 备份文件总数
# TYPE custom_backup_files_total gauge
custom_backup_files_total 1250
```

---

## 4.3 cAdvisor - 容器监控

### 4.3.1 cAdvisor简介

**cAdvisor** (Container Advisor) 是Google开源的容器监控工具,可以采集:

- 📦 容器CPU、内存使用
- 💾 容器磁盘IO
- 🌐 容器网络流量
- 🔄 容器生命周期事件

### 4.3.2 安装cAdvisor

**Docker方式**:

```bash
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --publish=8080:8080 \
  --detach=true \
  gcr.io/cadvisor/cadvisor:latest
```

**Docker Compose**:

```yaml
version: '3.8'
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - 8080:8080
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
```

### 4.3.3 配置Prometheus抓取cAdvisor

```yaml
scrape_configs:
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8080']
```

### 4.3.4 cAdvisor核心指标

```promql
# 容器CPU使用率
rate(container_cpu_usage_seconds_total{name!=""}[5m]) * 100

# 容器内存使用量(MB)
container_memory_usage_bytes{name!=""} / 1024 / 1024

# 容器内存限制(MB)
container_spec_memory_limit_bytes{name!=""} / 1024 / 1024

# 容器内存使用率
container_memory_usage_bytes{name!=""} 
/ container_spec_memory_limit_bytes{name!=""} * 100

# 容器网络接收速率(MB/s)
rate(container_network_receive_bytes_total{name!=""}[5m]) / 1024 / 1024

# 容器网络发送速率(MB/s)
rate(container_network_transmit_bytes_total{name!=""}[5m]) / 1024 / 1024

# 容器磁盘读取速率
rate(container_fs_reads_bytes_total{name!=""}[5m]) / 1024 / 1024

# 容器磁盘写入速率
rate(container_fs_writes_bytes_total{name!=""}[5m]) / 1024 / 1024
```

---

## 4.4 中间件Exporters

### 4.4.1 MySQL Exporter

**安装**:

```bash
docker run -d \
  --name=mysql-exporter \
  -p 9104:9104 \
  -e DATA_SOURCE_NAME="user:password@(mysql-host:3306)/" \
  prom/mysqld-exporter:latest
```

**Prometheus配置**:

```yaml
scrape_configs:
  - job_name: 'mysql'
    static_configs:
      - targets: ['localhost:9104']
        labels:
          instance: 'mysql-prod-01'
```

**核心指标**:

```promql
# MySQL运行状态
mysql_up

# QPS (每秒查询数)
rate(mysql_global_status_questions[5m])

# TPS (每秒事务数)
rate(mysql_global_status_commands_total{command="commit"}[5m]) +
rate(mysql_global_status_commands_total{command="rollback"}[5m])

# 慢查询
rate(mysql_global_status_slow_queries[5m])

# 连接数
mysql_global_status_threads_connected

# 最大连接数
mysql_global_variables_max_connections

# 连接使用率
mysql_global_status_threads_connected 
/ mysql_global_variables_max_connections * 100

# InnoDB缓冲池命中率
(mysql_global_status_innodb_buffer_pool_read_requests 
 - mysql_global_status_innodb_buffer_pool_reads) 
/ mysql_global_status_innodb_buffer_pool_read_requests * 100

# 表锁等待
rate(mysql_global_status_table_locks_waited[5m])
```

### 4.4.2 Redis Exporter

**安装**:

```bash
docker run -d \
  --name=redis-exporter \
  -p 9121:9121 \
  oliver006/redis_exporter:latest \
  --redis.addr=redis://redis-host:6379
```

**核心指标**:

```promql
# Redis运行状态
redis_up

# 已用内存(MB)
redis_memory_used_bytes / 1024 / 1024

# 内存碎片率
redis_mem_fragmentation_ratio

# 连接的客户端数
redis_connected_clients

# 阻塞的客户端数
redis_blocked_clients

# Keys总数
redis_db_keys{db="db0"}

# 每秒命令数
rate(redis_commands_processed_total[5m])

# 命中率
rate(redis_keyspace_hits_total[5m]) 
/ (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100

# 过期Keys
redis_expired_keys_total

# 驱逐Keys
redis_evicted_keys_total
```

### 4.4.3 Nginx Exporter

Nginx需要先启用`stub_status`模块。

**Nginx配置**:

```nginx
server {
    listen 8080;
    location /stub_status {
        stub_status on;
        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
```

**安装Exporter**:

```bash
docker run -d \
  --name=nginx-exporter \
  -p 9113:9113 \
  nginx/nginx-prometheus-exporter:latest \
  -nginx.scrape-uri=http://nginx-host:8080/stub_status
```

**核心指标**:

```promql
# Nginx运行状态
nginx_up

# 活跃连接数
nginx_connections_active

# 每秒接受的连接数
rate(nginx_connections_accepted[5m])

# 每秒处理的连接数
rate(nginx_connections_handled[5m])

# 每秒请求数
rate(nginx_http_requests_total[5m])

# Reading状态的连接数
nginx_connections_reading

# Writing状态的连接数
nginx_connections_writing

# Waiting状态的连接数
nginx_connections_waiting
```

---

## 4.5 Blackbox Exporter - 黑盒监控

### 4.5.1 Blackbox Exporter简介

**Blackbox Exporter**用于黑盒探测,支持:

- 🌐 HTTP/HTTPS探测 (可用性、响应时间、证书过期检查)
- 🔌 TCP探测 (端口连通性)
- 📡 ICMP探测 (Ping)
- 📧 DNS探测

### 4.5.2 安装Blackbox Exporter

**Docker方式**:

```bash
docker run -d \
  --name=blackbox-exporter \
  -p 9115:9115 \
  prom/blackbox-exporter:latest
```

### 4.5.3 配置文件

创建`blackbox.yml`:

```yaml
modules:
  # HTTP 2xx探测
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []  # 默认2xx为成功
      method: GET
      preferred_ip_protocol: "ip4"

  # HTTP POST探测
  http_post_2xx:
    prober: http
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: '{"key":"value"}'

  # HTTPS证书检查
  http_2xx_with_tls:
    prober: http
    timeout: 5s
    http:
      fail_if_ssl: false
      fail_if_not_ssl: true
      tls_config:
        insecure_skip_verify: false

  # TCP探测
  tcp_connect:
    prober: tcp
    timeout: 5s

  # ICMP探测(Ping)
  icmp:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"

  # DNS探测
  dns_query:
    prober: dns
    timeout: 5s
    dns:
      query_name: "example.com"
      query_type: "A"
```

### 4.5.4 Prometheus配置

```yaml
scrape_configs:
  # HTTP探测
  - job_name: 'blackbox-http'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://www.example.com
          - https://api.example.com
          - http://internal-service:8080
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115

  # TCP探测
  - job_name: 'blackbox-tcp'
    metrics_path: /probe
    params:
      module: [tcp_connect]
    static_configs:
      - targets:
          - mysql-host:3306
          - redis-host:6379
          - postgres-host:5432
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115

  # ICMP探测(Ping)
  - job_name: 'blackbox-icmp'
    metrics_path: /probe
    params:
      module: [icmp]
    static_configs:
      - targets:
          - 8.8.8.8
          - 1.1.1.1
          - gateway.example.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
```

### 4.5.5 Blackbox核心指标

```promql
# 探测成功(1=成功, 0=失败)
probe_success

# HTTP状态码
probe_http_status_code

# HTTP响应时间(秒)
probe_http_duration_seconds

# SSL证书过期时间(秒)
probe_ssl_earliest_cert_expiry

# SSL证书剩余天数
(probe_ssl_earliest_cert_expiry - time()) / 86400

# TCP连接时间
probe_tcp_duration_seconds

# DNS解析时间
probe_dns_lookup_time_seconds

# ICMP RTT(往返时间)
probe_icmp_duration_seconds
```

**实战告警规则**:

```yaml
groups:
  - name: blackbox_alerts
    rules:
      # 服务不可用
      - alert: ServiceDown
        expr: probe_success == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "服务{{ $labels.instance }}不可用"

      # HTTP状态码异常
      - alert: HttpStatusCodeError
        expr: probe_http_status_code >= 400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }}返回{{ $value }}状态码"

      # SSL证书即将过期(30天内)
      - alert: SslCertExpiringSoon
        expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 30
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }}的SSL证书将在{{ $value }}天后过期"

      # 响应时间过长(>5s)
      - alert: SlowResponse
        expr: probe_http_duration_seconds > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }}响应时间{{ $value }}秒"
```

---

## 4.6 Pushgateway - 短期任务监控

### 4.6.1 Pushgateway简介

**适用场景**:
- ✅ 批处理作业(定时任务)
- ✅ 短期运行的脚本
- ✅ 无法被Prometheus主动抓取的任务

**⚠️ 不适用场景**:
- ❌ 长期运行的服务(应该直接暴露/metrics)
- ❌ 高频率推送(会影响Prometheus性能)
- ❌ 需要实时监控的场景

### 4.6.2 安装Pushgateway

```bash
docker run -d \
  --name=pushgateway \
  -p 9091:9091 \
  prom/pushgateway:latest
```

### 4.6.3 推送指标

**Shell脚本推送**:

```bash
#!/bin/bash

# 批处理任务开始
echo "backup_job_start_timestamp $(date +%s)" | curl --data-binary @- \
  http://localhost:9091/metrics/job/backup/instance/server-01

# 执行备份
backup_result=$?
backup_size=$(du -sb /backup | awk '{print $1}')
backup_files=$(find /backup -type f | wc -l)

# 推送结果指标
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/backup/instance/server-01
# TYPE backup_status gauge
backup_status $backup_result
# TYPE backup_size_bytes gauge
backup_size_bytes $backup_size
# TYPE backup_files_total gauge
backup_files_total $backup_files
# TYPE backup_duration_seconds gauge
backup_duration_seconds $SECONDS
EOF
```

**Python推送**:

```python
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

registry = CollectorRegistry()

# 定义指标
backup_status = Gauge('backup_status', '备份状态(0=失败,1=成功)', registry=registry)
backup_size = Gauge('backup_size_bytes', '备份大小(字节)', registry=registry)
backup_duration = Gauge('backup_duration_seconds', '备份耗时(秒)', registry=registry)

# 设置指标值
backup_status.set(1)
backup_size.set(1024*1024*500)  # 500MB
backup_duration.set(120)  # 120秒

# 推送到Pushgateway
push_to_gateway('localhost:9091', job='backup', registry=registry, 
                grouping_key={'instance': 'server-01'})
```

### 4.6.4 Prometheus配置

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true  # 保留推送的job和instance标签
    static_configs:
      - targets: ['localhost:9091']
```

### 4.6.5 最佳实践

**1. 使用唯一的job和instance标识**:

```bash
# ✅ 好
curl --data-binary @- http://localhost:9091/metrics/job/backup/instance/server-01

# ❌ 差 - 缺少instance
curl --data-binary @- http://localhost:9091/metrics/job/backup
```

**2. 任务结束后清理指标** (避免陈旧数据):

```bash
# 删除特定instance的指标
curl -X DELETE http://localhost:9091/metrics/job/backup/instance/server-01

# 删除整个job的指标
curl -X DELETE http://localhost:9091/metrics/job/backup
```

**3. 添加时间戳指标**:

```bash
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/backup/instance/server-01
# TYPE backup_last_success_timestamp gauge
backup_last_success_timestamp $(date +%s)
EOF
```

---

## 4.7 自定义Exporter开发

### 4.7.1 Python Exporter示例

**场景**: 监控业务订单系统

```python
#!/usr/bin/env python3
"""
自定义Exporter - 订单系统监控
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import random
import mysql.connector

# 定义指标
order_total = Gauge('order_total', '订单总数', ['status'])
order_amount = Gauge('order_amount_total', '订单总金额')
order_creation_time = Histogram('order_creation_duration_seconds', '订单创建耗时')
order_errors = Counter('order_errors_total', '订单错误数', ['error_type'])

def collect_order_metrics():
    """从数据库采集订单指标"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(
            host='localhost',
            user='user',
            password='password',
            database='orders'
        )
        cursor = conn.cursor()
        
        # 查询订单状态分布
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM orders
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            GROUP BY status
        """)
        for status, count in cursor.fetchall():
            order_total.labels(status=status).set(count)
        
        # 查询订单总金额
        cursor.execute("""
            SELECT SUM(amount) as total
            FROM orders
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """)
        total_amount = cursor.fetchone()[0] or 0
        order_amount.set(total_amount)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        order_errors.labels(error_type='database_error').inc()
        print(f"采集失败: {e}")

if __name__ == '__main__':
    # 启动HTTP服务器
    start_http_server(8000)
    print("Exporter running on http://localhost:8000/metrics")
    
    # 定期采集指标
    while True:
        collect_order_metrics()
        time.sleep(15)  # 每15秒采集一次
```

### 4.7.2 Go Exporter示例

```go
package main

import (
    "database/sql"
    "log"
    "net/http"
    "time"

    _ "github.com/go-sql-driver/mysql"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    orderTotal = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "order_total",
            Help: "订单总数",
        },
        []string{"status"},
    )
    
    orderAmount = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "order_amount_total",
            Help: "订单总金额",
        },
    )
)

func init() {
    prometheus.MustRegister(orderTotal)
    prometheus.MustRegister(orderAmount)
}

func collectMetrics(db *sql.DB) {
    // 查询订单状态分布
    rows, err := db.Query(`
        SELECT status, COUNT(*) as count
        FROM orders
        WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
        GROUP BY status
    `)
    if err != nil {
        log.Printf("查询失败: %v", err)
        return
    }
    defer rows.Close()
    
    for rows.Next() {
        var status string
        var count float64
        if err := rows.Scan(&status, &count); err != nil {
            log.Printf("扫描失败: %v", err)
            continue
        }
        orderTotal.WithLabelValues(status).Set(count)
    }
    
    // 查询订单总金额
    var totalAmount float64
    err = db.QueryRow(`
        SELECT COALESCE(SUM(amount), 0) as total
        FROM orders
        WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    `).Scan(&totalAmount)
    if err != nil {
        log.Printf("查询失败: %v", err)
        return
    }
    orderAmount.Set(totalAmount)
}

func main() {
    // 连接数据库
    db, err := sql.Open("mysql", "user:password@tcp(localhost:3306)/orders")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()
    
    // 定期采集指标
    go func() {
        for {
            collectMetrics(db)
            time.Sleep(15 * time.Second)
        }
    }()
    
    // 启动HTTP服务器
    http.Handle("/metrics", promhttp.Handler())
    log.Println("Exporter running on :8000/metrics")
    log.Fatal(http.ListenAndServe(":8000", nil))
}
```

---

## 4.8 实验练习

完整实验环境位于`code/chapter04/`目录。

### 实验1: Node Exporter监控

1. 启动Node Exporter
2. 配置Prometheus抓取
3. 查询CPU、内存、磁盘指标
4. 创建系统监控告警规则

### 实验2: Blackbox Exporter探测

1. 配置HTTP、TCP、ICMP探测
2. 监控网站可用性
3. 检查SSL证书过期
4. 创建探测告警

### 实验3: 自定义Exporter开发

1. 开发Python Exporter
2. 暴露业务指标
3. Prometheus采集验证
4. Grafana可视化

---

## 4.9 本章小结

### 核心知识点

✅ **Exporter类型**: 官方、第三方、内置、自定义

✅ **Node Exporter**: 系统监控(CPU、内存、磁盘、网络)

✅ **cAdvisor**: 容器监控

✅ **中间件Exporters**: MySQL、Redis、Nginx等

✅ **Blackbox Exporter**: 黑盒探测(HTTP/TCP/ICMP)

✅ **Pushgateway**: 短期任务指标推送

✅ **自定义Exporter**: Python/Go开发

### 常用Exporters端口速查

| Exporter | 端口 |
|----------|------|
| Node Exporter | 9100 |
| cAdvisor | 8080 |
| MySQL Exporter | 9104 |
| Redis Exporter | 9121 |
| Nginx Exporter | 9113 |
| Blackbox Exporter | 9115 |
| Pushgateway | 9091 |

### 下一章预告

**第5章 - 服务发现机制**,将学习:
- 📡 静态配置 vs 动态服务发现
- ☸️ Kubernetes服务发现
- 🔍 Consul服务发现
- 🐳 Docker服务发现
- 📂 基于文件的服务发现

---

**🎉 恭喜!** 你已经掌握了Prometheus数据采集的核心技能!
