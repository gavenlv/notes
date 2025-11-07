# 第8章：Pushgateway推送网关

> **学习时长**: 3-4小时  
> **难度**: ⭐⭐⭐  
> **重要性**: ⭐⭐⭐

## 本章目标

学完本章后,你将能够:

- ✅ 理解Pushgateway的使用场景和限制
- ✅ 部署和配置Pushgateway
- ✅ 从批处理作业推送指标
- ✅ 掌握Pushgateway最佳实践
- ✅ 避免常见的使用陷阱

---

## 8.1 Pushgateway概述

### 8.1.1 什么是Pushgateway?

**Pushgateway**是Prometheus的中间推送网关,用于接收短期任务推送的指标。

**工作流程**:
```
批处理作业 → Push指标 → Pushgateway → Prometheus抓取 → 存储
   (主动推送)              (被动抓取)
```

### 8.1.2 适用场景

**✅ 适合使用**:
- 定时任务(Cron Jobs)
- 批处理作业
- 短期运行的脚本
- 无法被Prometheus直接抓取的作业

**❌ 不适合使用**:
- 长期运行的服务(应直接暴露/metrics)
- 高频推送(会成为单点瓶颈)
- 需要实时监控的场景

### 8.1.3 Pushgateway限制

⚠️ **重要限制**:

1. **单点故障**: Pushgateway宕机会丢失数据
2. **无自动过期**: 指标需要手动删除或推送时覆盖
3. **不适合实例监控**: up指标会一直显示为1
4. **性能瓶颈**: 大量推送会影响性能

---

## 8.2 部署Pushgateway

### 8.2.1 Docker部署

```bash
docker run -d \
  --name=pushgateway \
  -p 9091:9091 \
  prom/pushgateway:latest
```

### 8.2.2 二进制部署

```bash
VERSION=1.6.2
wget https://github.com/prometheus/pushgateway/releases/download/v${VERSION}/pushgateway-${VERSION}.linux-amd64.tar.gz
tar xvfz pushgateway-${VERSION}.linux-amd64.tar.gz
cd pushgateway-${VERSION}.linux-amd64
./pushgateway
```

### 8.2.3 systemd服务

创建`/etc/systemd/system/pushgateway.service`:

```ini
[Unit]
Description=Prometheus Pushgateway
After=network.target

[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/bin/pushgateway \
  --web.listen-address=:9091 \
  --web.telemetry-path=/metrics \
  --persistence.file=/var/lib/pushgateway/data.db \
  --persistence.interval=5m

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pushgateway
sudo systemctl start pushgateway
```

### 8.2.4 配置Prometheus抓取

在`prometheus.yml`中添加:

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true  # 保留推送的job和instance标签
    static_configs:
      - targets: ['localhost:9091']
```

**⚠️ `honor_labels: true`的重要性**:
- 保留推送时指定的`job`和`instance`标签
- 否则会被Prometheus的配置覆盖

---

## 8.3 推送指标

### 8.3.1 推送协议

**URL格式**:
```
http://pushgateway:9091/metrics/job/<JOB_NAME>{/<LABEL_NAME>/<LABEL_VALUE>}
```

**HTTP方法**:
- `POST`: 替换指定分组的所有指标
- `PUT`: 替换指定分组的所有指标(同POST)
- `DELETE`: 删除指定分组的所有指标

### 8.3.2 使用curl推送

**基础推送**:

```bash
# 推送单个指标
echo "backup_status 1" | curl --data-binary @- \
  http://localhost:9091/metrics/job/backup

# 推送多个指标
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/backup
# TYPE backup_status gauge
backup_status 1
# TYPE backup_size_bytes gauge
backup_size_bytes 123456789
# TYPE backup_duration_seconds gauge
backup_duration_seconds 120
EOF
```

**带标签推送**:

```bash
# 添加instance标签
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/backup/instance/server-01
# TYPE backup_status gauge
backup_status 1
# TYPE backup_size_bytes gauge
backup_size_bytes 123456789
EOF

# 添加多个标签
cat <<EOF | curl --data-binary @- \
  http://localhost:9091/metrics/job/backup/instance/server-01/env/production
backup_status 1
backup_size_bytes 123456789
EOF
```

**删除指标**:

```bash
# 删除特定分组
curl -X DELETE http://localhost:9091/metrics/job/backup/instance/server-01

# 删除整个job
curl -X DELETE http://localhost:9091/metrics/job/backup
```

### 8.3.3 Shell脚本推送

**备份脚本示例**:

```bash
#!/bin/bash

PUSHGATEWAY_URL="http://localhost:9091"
JOB_NAME="database_backup"
INSTANCE_NAME="$(hostname)"

# 记录开始时间
START_TIME=$(date +%s)

# 执行备份
echo "开始备份..."
/usr/local/bin/backup.sh
BACKUP_STATUS=$?

# 计算耗时
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# 获取备份大小
BACKUP_SIZE=$(du -sb /backup/latest.tar.gz | awk '{print $1}')

# 推送指标
cat <<EOF | curl --data-binary @- \
  ${PUSHGATEWAY_URL}/metrics/job/${JOB_NAME}/instance/${INSTANCE_NAME}
# TYPE backup_last_run_timestamp gauge
backup_last_run_timestamp ${END_TIME}
# TYPE backup_status gauge
# HELP backup_status Backup job status (0=failed, 1=success)
backup_status ${BACKUP_STATUS}
# TYPE backup_duration_seconds gauge
backup_duration_seconds ${DURATION}
# TYPE backup_size_bytes gauge
backup_size_bytes ${BACKUP_SIZE}
EOF

if [ $BACKUP_STATUS -eq 0 ]; then
  echo "备份成功! 大小: $(numfmt --to=iec-i --suffix=B $BACKUP_SIZE), 耗时: ${DURATION}秒"
else
  echo "备份失败! 退出码: $BACKUP_STATUS"
fi
```

### 8.3.4 Python推送

**使用prometheus_client库**:

```python
#!/usr/bin/env python3
"""
批处理作业推送指标到Pushgateway
"""

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import time
import subprocess

# 创建Registry
registry = CollectorRegistry()

# 定义指标
job_status = Gauge('job_status', '作业状态(0=失败,1=成功)', registry=registry)
job_duration = Gauge('job_duration_seconds', '作业耗时(秒)', registry=registry)
job_processed_items = Gauge('job_processed_items', '处理的项目数', registry=registry)
job_last_success_timestamp = Gauge('job_last_success_timestamp', '上次成功时间戳', registry=registry)

def run_job():
    """执行批处理作业"""
    start_time = time.time()
    
    try:
        # 模拟作业执行
        result = subprocess.run(['/usr/local/bin/process_data.sh'], 
                                capture_output=True, check=True)
        
        # 作业成功
        job_status.set(1)
        job_last_success_timestamp.set(time.time())
        
        # 解析处理的项目数(假设脚本输出数字)
        processed_items = int(result.stdout.decode().strip())
        job_processed_items.set(processed_items)
        
        print(f"作业成功! 处理了{processed_items}个项目")
        
    except subprocess.CalledProcessError as e:
        # 作业失败
        job_status.set(0)
        print(f"作业失败! 错误: {e}")
    
    finally:
        # 记录耗时
        duration = time.time() - start_time
        job_duration.set(duration)
        
        # 推送指标到Pushgateway
        push_to_gateway('localhost:9091', 
                        job='batch_processing', 
                        registry=registry,
                        grouping_key={'instance': 'worker-01', 'env': 'production'})
        
        print(f"指标已推送到Pushgateway, 耗时: {duration:.2f}秒")

if __name__ == '__main__':
    run_job()
```

**高级用法 - 删除指标**:

```python
from prometheus_client import delete_from_gateway

# 删除指定分组的指标
delete_from_gateway('localhost:9091', 
                    job='batch_processing',
                    grouping_key={'instance': 'worker-01'})
```

### 8.3.5 Go推送

```go
package main

import (
    "fmt"
    "log"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/push"
)

var (
    jobStatus = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "job_status",
        Help: "作业状态(0=失败,1=成功)",
    })
    
    jobDuration = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "job_duration_seconds",
        Help: "作业耗时(秒)",
    })
)

func main() {
    startTime := time.Now()
    
    // 执行作业
    err := runJob()
    
    // 记录耗时
    duration := time.Since(startTime).Seconds()
    jobDuration.Set(duration)
    
    // 设置状态
    if err != nil {
        jobStatus.Set(0)
        log.Printf("作业失败: %v", err)
    } else {
        jobStatus.Set(1)
        log.Println("作业成功!")
    }
    
    // 推送到Pushgateway
    pusher := push.New("http://localhost:9091", "batch_job").
        Grouping("instance", "worker-01").
        Grouping("env", "production").
        Collector(jobStatus).
        Collector(jobDuration)
    
    if err := pusher.Push(); err != nil {
        log.Printf("推送失败: %v", err)
    } else {
        log.Printf("指标已推送, 耗时: %.2fs", duration)
    }
}

func runJob() error {
    // 模拟作业执行
    time.Sleep(2 * time.Second)
    return nil
}
```

---

## 8.4 监控批处理作业

### 8.4.1 标准指标集

推荐为批处理作业推送以下指标:

```promql
# 1. 作业状态
job_status{job="backup", instance="server-01"} 1

# 2. 上次运行时间戳
job_last_run_timestamp{job="backup", instance="server-01"} 1699876543

# 3. 上次成功时间戳
job_last_success_timestamp{job="backup", instance="server-01"} 1699876543

# 4. 作业耗时
job_duration_seconds{job="backup", instance="server-01"} 120

# 5. 处理的记录数
job_processed_records{job="backup", instance="server-01"} 10000

# 6. 业务指标
backup_size_bytes{job="backup", instance="server-01"} 123456789
```

### 8.4.2 告警规则

```yaml
groups:
  - name: batch_job_alerts
    rules:
      # 作业失败
      - alert: BatchJobFailed
        expr: job_status == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "批处理作业{{ $labels.job }}失败"
          description: "实例{{ $labels.instance }}的作业{{ $labels.job }}执行失败"
      
      # 作业未按时执行
      - alert: BatchJobNotRun
        expr: time() - job_last_run_timestamp > 3600 * 26  # 26小时未运行
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "批处理作业{{ $labels.job }}未按时运行"
          description: "作业{{ $labels.job }}已{{ $value | humanizeDuration }}未运行"
      
      # 作业耗时过长
      - alert: BatchJobTooSlow
        expr: job_duration_seconds > 3600  # 超过1小时
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "批处理作业{{ $labels.job }}耗时过长"
          description: "作业耗时{{ $value | humanizeDuration }}"
      
      # 作业处理量异常
      - alert: BatchJobLowProcessing
        expr: |
          job_processed_records < 1000
          and
          job_processed_records offset 1d > 10000
        labels:
          severity: warning
        annotations:
          summary: "批处理作业{{ $labels.job }}处理量异常低"
          description: "当前处理{{ $value }}条,昨天处理10000+条"
```

### 8.4.3 Grafana Dashboard查询

```promql
# Panel 1: 作业状态
job_status

# Panel 2: 最近运行时间
time() - job_last_run_timestamp

# Panel 3: 作业耗时趋势
job_duration_seconds

# Panel 4: 处理量趋势
job_processed_records

# Panel 5: 成功率(24小时)
avg_over_time(job_status[24h]) * 100
```

---

## 8.5 Pushgateway最佳实践

### 8.5.1 使用唯一分组键

**✅ 推荐**:

```bash
# 包含job和instance
curl --data-binary @- \
  http://localhost:9091/metrics/job/backup/instance/server-01
```

**❌ 不推荐**:

```bash
# 只有job,不同实例会互相覆盖
curl --data-binary @- \
  http://localhost:9091/metrics/job/backup
```

### 8.5.2 添加时间戳指标

```bash
cat <<EOF | curl --data-binary @- \
  http://localhost:9091/metrics/job/backup/instance/server-01
# 作业状态
backup_status 1
# 上次运行时间
backup_last_run_timestamp $(date +%s)
# 上次成功时间(仅成功时更新)
backup_last_success_timestamp $(date +%s)
EOF
```

### 8.5.3 作业结束后清理指标

**成功时覆盖,失败时删除**:

```python
def run_job():
    try:
        # 执行作业
        execute_job()
        
        # 成功 - 推送最新指标
        job_status.set(1)
        push_to_gateway('localhost:9091', job='my_job', registry=registry)
        
    except Exception as e:
        # 失败 - 删除旧指标,推送失败状态
        job_status.set(0)
        push_to_gateway('localhost:9091', job='my_job', registry=registry)
```

### 8.5.4 使用持久化存储

```bash
# 启用持久化,避免重启丢失数据
./pushgateway \
  --persistence.file=/var/lib/pushgateway/data.db \
  --persistence.interval=5m
```

### 8.5.5 高可用部署

**方案1: 多Pushgateway + 负载均衡**

```yaml
# Prometheus配置
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets:
          - pushgateway-01:9091
          - pushgateway-02:9091
```

**方案2: 双推送**

```python
# 同时推送到两个Pushgateway
for gateway in ['pushgateway-01:9091', 'pushgateway-02:9091']:
    push_to_gateway(gateway, job='my_job', registry=registry)
```

---

## 8.6 常见问题

### 8.6.1 指标不过期怎么办?

**问题**: Pushgateway的指标不会自动过期

**解决方案1**: 作业结束后删除指标

```bash
# 作业结束后删除
curl -X DELETE http://localhost:9091/metrics/job/backup/instance/server-01
```

**解决方案2**: 使用时间戳指标判断

```promql
# 告警: 指标超过26小时未更新
time() - job_last_run_timestamp > 3600 * 26
```

### 8.6.2 如何避免标签冲突?

**问题**: 不同作业使用相同的job和instance标签

**解决方案**: 使用明确的命名

```bash
# ✅ 好的命名
job=database_backup/instance=mysql-prod-01
job=log_rotation/instance=web-server-01

# ❌ 差的命名
job=backup/instance=server-01  # 不明确是什么备份
```

### 8.6.3 大量作业如何管理?

**解决方案**: 使用额外标签分类

```bash
curl --data-binary @- \
  http://localhost:9091/metrics/job/backup/instance/server-01/type/database/env/production
```

查询:
```promql
# 按类型查询
job_status{type="database"}

# 按环境查询
job_status{env="production"}
```

---

## 8.7 实验练习

实验环境位于`code/chapter08/`目录。

### 实验1: 部署Pushgateway
1. 启动Pushgateway
2. 配置Prometheus抓取
3. 验证连通性

### 实验2: 推送指标
1. 使用curl推送指标
2. 查看Prometheus中的数据
3. 测试删除指标

### 实验3: 监控批处理作业
1. 编写备份脚本
2. 推送作业指标
3. 配置告警规则
4. 创建Grafana Dashboard

---

## 8.8 本章小结

### 核心知识点

✅ **Pushgateway**: 用于短期任务的指标推送网关

✅ **适用场景**: 定时任务、批处理作业、短期脚本

✅ **推送方式**: Shell、Python、Go

✅ **最佳实践**: 唯一分组键、时间戳指标、及时清理

✅ **告警**: 作业失败、未按时运行、耗时过长

### 关键配置

| 配置项 | 说明 |
|-------|------|
| `honor_labels: true` | 保留推送的标签 |
| `persistence.file` | 持久化存储路径 |
| 分组键 | job + instance + 其他标签 |

### 下一章预告

**第9章 - 高可用与联邦集群**,将学习:
- 🔄 Prometheus高可用部署
- 🌐 联邦集群架构
- 📦 远程存储(Thanos、Cortex、M3DB)
- 💾 长期存储方案

---

**🎉 恭喜!** 你已经掌握了Pushgateway的使用方法!
