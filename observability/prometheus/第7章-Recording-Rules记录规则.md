# 第7章：Recording Rules记录规则

> **学习时长**: 4-5小时  
> **难度**: ⭐⭐⭐  
> **重要性**: ⭐⭐⭐⭐

## 本章目标

学完本章后,你将能够:

- ✅ 理解Recording Rules的作用和原理
- ✅ 编写高效的Recording Rules
- ✅ 使用Recording Rules优化查询性能
- ✅ 掌握命名规范和最佳实践
- ✅ 实施分层聚合策略

---

## 7.1 Recording Rules概述

### 7.1.1 什么是Recording Rules?

**Recording Rules**用于预先计算复杂的PromQL查询,并将结果存储为新的时间序列。

**核心优势**:
- ⚡ **性能优化**: 复杂查询预计算,减少查询时间
- 📊 **简化查询**: 将复杂表达式封装为简单指标
- 🎯 **提高复用**: 多个告警和Dashboard可共用
- 💾 **降低负载**: 减少实时计算压力

### 7.1.2 Recording Rules vs 普通查询

**普通查询** (每次查询时计算):
```promql
sum(rate(http_requests_total[5m])) by (method, status)
```

**Recording Rule** (预先计算并存储):
```yaml
- record: method_status:http_requests:rate5m
  expr: sum(rate(http_requests_total[5m])) by (method, status)
```

使用时直接查询:
```promql
method_status:http_requests:rate5m
```

---

## 7.2 Recording Rules语法

### 7.2.1 基本语法

```yaml
groups:
  - name: <group_name>
    interval: <evaluation_interval>  # 评估间隔,默认global.evaluation_interval
    rules:
      - record: <metric_name>
        expr: <promql_expression>
        labels:
          <label_name>: <label_value>
```

**字段说明**:
- `record`: 新指标名称
- `expr`: PromQL表达式
- `labels`: 额外标签(可选)

### 7.2.2 基础示例

**文件**: `/etc/prometheus/rules/recording_rules.yml`

```yaml
groups:
  - name: http_recording_rules
    interval: 30s
    rules:
      # 计算HTTP请求速率
      - record: instance:http_requests:rate5m
        expr: rate(http_requests_total[5m])
      
      # 按job聚合的QPS
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)
      
      # 按method和status聚合的QPS
      - record: method_status:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (method, status)
      
      # HTTP错误率
      - record: job:http_requests:error_rate5m
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
          /
          sum(rate(http_requests_total[5m])) by (job)
```

### 7.2.3 Prometheus配置

在`prometheus.yml`中配置:

```yaml
global:
  evaluation_interval: 30s  # 默认评估间隔

rule_files:
  - "/etc/prometheus/rules/recording_rules.yml"
  - "/etc/prometheus/rules/alerts.yml"
```

**验证规则**:

```bash
# 检查语法
promtool check rules /etc/prometheus/rules/recording_rules.yml

# 单元测试
promtool test rules test_rules.yml
```

---

## 7.3 命名规范

### 7.3.1 命名格式

Prometheus官方推荐的命名格式:

```
level:metric:operations
```

**组成部分**:
- `level`: 聚合级别(如`instance`, `job`, `cluster`)
- `metric`: 原始指标名称
- `operations`: 操作(如`rate5m`, `sum`, `avg`)

### 7.3.2 命名示例

```yaml
# ✅ 好的命名
instance:node_cpu:ratio                    # 实例级别CPU使用率
job:http_requests:rate5m                   # job级别请求速率
cluster:memory:usage_bytes                 # 集群级别内存使用

# ❌ 差的命名
cpu_usage                                  # 不清楚聚合级别
requests                                   # 太简单
http_rate                                  # 缺少时间窗口信息
```

### 7.3.3 命名规范详解

**1. 单一聚合级别**:
```yaml
- record: instance:node_cpu:ratio
  expr: 1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)
```

**2. 多级聚合**:
```yaml
- record: instance_path:http_requests:rate5m
  expr: sum(rate(http_requests_total[5m])) by (instance, path)
```

**3. 带操作后缀**:
```yaml
- record: job:http_requests:rate5m           # 速率
- record: job:http_requests:sum              # 总和
- record: job:http_request_duration:p95      # p95分位数
```

---

## 7.4 性能优化案例

### 7.4.1 优化复杂查询

**场景**: 频繁查询p95响应时间

**原始查询** (每次计算):
```promql
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job, method)
)
```

**优化方案**:

**Step 1**: 预计算rate
```yaml
- record: job_method:http_request_duration_seconds_bucket:rate5m
  expr: sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job, method)
```

**Step 2**: 计算分位数
```yaml
- record: job_method:http_request_duration:p95
  expr: histogram_quantile(0.95, job_method:http_request_duration_seconds_bucket:rate5m)
```

**使用**:
```promql
# 直接查询预计算的p95
job_method:http_request_duration:p95

# 性能提升: 从数秒降低到毫秒级
```

### 7.4.2 优化Dashboard查询

**原始Dashboard查询**:
```promql
# Panel 1: 总QPS
sum(rate(http_requests_total[5m]))

# Panel 2: 按服务分组的QPS
sum(rate(http_requests_total[5m])) by (service)

# Panel 3: 成功率
sum(rate(http_requests_total{status="200"}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100
```

**优化后的Recording Rules**:
```yaml
groups:
  - name: dashboard_recording_rules
    interval: 30s
    rules:
      # 实例级别QPS
      - record: instance:http_requests:rate5m
        expr: rate(http_requests_total[5m])
      
      # 服务级别QPS
      - record: service:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (service)
      
      # 总QPS
      - record: :http_requests:rate5m
        expr: sum(rate(http_requests_total[5m]))
      
      # 成功率
      - record: :http_requests:success_rate5m
        expr: |
          sum(rate(http_requests_total{status="200"}[5m])) 
          / 
          sum(rate(http_requests_total[5m])) * 100
```

**Dashboard使用**:
```promql
# Panel 1: 总QPS
:http_requests:rate5m

# Panel 2: 按服务分组的QPS
service:http_requests:rate5m

# Panel 3: 成功率
:http_requests:success_rate5m
```

---

## 7.5 分层聚合策略

### 7.5.1 聚合金字塔

```
              集群级别 (最粗粒度)
                    ↑
              服务/Job级别
                    ↑
              实例级别
                    ↑
        原始指标 (最细粒度)
```

### 7.5.2 分层示例 - CPU监控

```yaml
groups:
  - name: cpu_recording_rules
    interval: 30s
    rules:
      # Level 1: 实例级别CPU使用率
      - record: instance:node_cpu:ratio
        expr: |
          1 - avg by (instance) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
          )
      
      # Level 2: Job级别平均CPU使用率
      - record: job:node_cpu:ratio
        expr: avg by (job) (instance:node_cpu:ratio)
      
      # Level 3: 集群级别平均CPU使用率
      - record: cluster:node_cpu:ratio
        expr: avg by (cluster) (instance:node_cpu:ratio)
      
      # Level 3: 集群级别最大CPU使用率
      - record: cluster:node_cpu:max_ratio
        expr: max by (cluster) (instance:node_cpu:ratio)
```

### 7.5.3 分层示例 - HTTP请求监控

```yaml
groups:
  - name: http_layered_rules
    interval: 30s
    rules:
      # Level 1: 原始速率 (保留所有标签)
      - record: instance_method_status:http_requests:rate5m
        expr: rate(http_requests_total[5m])
      
      # Level 2: 按实例和method聚合
      - record: instance_method:http_requests:rate5m
        expr: sum by (instance, method) (instance_method_status:http_requests:rate5m)
      
      # Level 3: 按method聚合
      - record: method:http_requests:rate5m
        expr: sum by (method) (instance_method:http_requests:rate5m)
      
      # Level 4: 总QPS
      - record: :http_requests:rate5m
        expr: sum(method:http_requests:rate5m)
      
      # 错误率 (Level 2)
      - record: instance:http_requests:error_rate5m
        expr: |
          sum by (instance) (instance_method_status:http_requests:rate5m{status=~"5.."})
          /
          sum by (instance) (instance_method_status:http_requests:rate5m)
      
      # 错误率 (Level 4 - 全局)
      - record: :http_requests:error_rate5m
        expr: |
          sum(instance_method_status:http_requests:rate5m{status=~"5.."})
          /
          sum(instance_method_status:http_requests:rate5m)
```

---

## 7.6 实战Recording Rules

### 7.6.1 系统监控Recording Rules

```yaml
groups:
  - name: node_recording_rules
    interval: 30s
    rules:
      # CPU使用率
      - record: instance:node_cpu:ratio
        expr: |
          1 - avg by (instance) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
          )
      
      # 内存使用率
      - record: instance:node_memory:ratio
        expr: |
          1 - (
            node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
          )
      
      # 磁盘使用率
      - record: instance_device:node_disk:ratio
        expr: |
          (
            node_filesystem_size_bytes{fstype!~"tmpfs|devtmpfs"} 
            - node_filesystem_avail_bytes{fstype!~"tmpfs|devtmpfs"}
          ) / node_filesystem_size_bytes{fstype!~"tmpfs|devtmpfs"}
      
      # 磁盘IO使用率
      - record: instance_device:node_disk_io:ratio
        expr: rate(node_disk_io_time_seconds_total[5m])
      
      # 网络接收速率(MB/s)
      - record: instance_device:node_network_receive:rate5m
        expr: rate(node_network_receive_bytes_total[5m]) / 1024 / 1024
      
      # 网络发送速率(MB/s)
      - record: instance_device:node_network_transmit:rate5m
        expr: rate(node_network_transmit_bytes_total[5m]) / 1024 / 1024
      
      # 系统负载
      - record: instance:node_load1:ratio
        expr: node_load1 / count by (instance) (node_cpu_seconds_total{mode="idle"})
```

### 7.6.2 应用监控Recording Rules

```yaml
groups:
  - name: application_recording_rules
    interval: 30s
    rules:
      # QPS (所有级别)
      - record: instance:http_requests:rate5m
        expr: rate(http_requests_total[5m])
      
      - record: job:http_requests:rate5m
        expr: sum by (job) (instance:http_requests:rate5m)
      
      - record: :http_requests:rate5m
        expr: sum(job:http_requests:rate5m)
      
      # 错误率
      - record: job:http_requests:error_rate5m
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))
      
      # 响应时间分位数
      - record: job:http_request_duration:p50
        expr: |
          histogram_quantile(0.50,
            sum by (le, job) (rate(http_request_duration_seconds_bucket[5m]))
          )
      
      - record: job:http_request_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum by (le, job) (rate(http_request_duration_seconds_bucket[5m]))
          )
      
      - record: job:http_request_duration:p99
        expr: |
          histogram_quantile(0.99,
            sum by (le, job) (rate(http_request_duration_seconds_bucket[5m]))
          )
      
      # 平均响应时间
      - record: job:http_request_duration:avg
        expr: |
          sum by (job) (rate(http_request_duration_seconds_sum[5m]))
          /
          sum by (job) (rate(http_request_duration_seconds_count[5m]))
```

### 7.6.3 业务指标Recording Rules

```yaml
groups:
  - name: business_recording_rules
    interval: 60s  # 业务指标可以降低评估频率
    rules:
      # 订单创建速率
      - record: service:order_created:rate5m
        expr: sum by (service) (rate(order_created_total[5m]))
      
      # 订单成功率
      - record: service:order:success_rate5m
        expr: |
          sum by (service) (rate(order_created_total{status="success"}[5m]))
          /
          sum by (service) (rate(order_created_total[5m]))
      
      # 支付金额速率(每分钟)
      - record: service:payment_amount:rate1m
        expr: sum by (service) (rate(payment_amount_total[1m]) * 60)
      
      # 用户活跃数
      - record: service:active_users:count
        expr: sum by (service) (active_users_gauge)
```

---

## 7.7 Recording Rules单元测试

### 7.7.1 测试文件格式

**文件**: `test_recording_rules.yml`

```yaml
rule_files:
  - recording_rules.yml

evaluation_interval: 1m

tests:
  # Test Case 1: 测试CPU使用率计算
  - interval: 1m
    input_series:
      - series: 'node_cpu_seconds_total{instance="node-01", mode="idle"}'
        values: '0+10x10'  # 0, 10, 20, ..., 100
      - series: 'node_cpu_seconds_total{instance="node-01", mode="user"}'
        values: '0+5x10'   # 0, 5, 10, ..., 50
    
    promql_expr_test:
      - expr: instance:node_cpu:ratio
        eval_time: 5m
        exp_samples:
          - labels: 'instance:node_cpu:ratio{instance="node-01"}'
            value: 0.333  # 约33%
  
  # Test Case 2: 测试HTTP QPS
  - interval: 1m
    input_series:
      - series: 'http_requests_total{job="api", instance="api-01"}'
        values: '0+100x10'  # 每分钟增加100
      - series: 'http_requests_total{job="api", instance="api-02"}'
        values: '0+200x10'  # 每分钟增加200
    
    promql_expr_test:
      - expr: job:http_requests:rate5m
        eval_time: 5m
        exp_samples:
          - labels: 'job:http_requests:rate5m{job="api"}'
            value: 5  # (100+200)/60 = 5 req/s
```

### 7.7.2 运行测试

```bash
# 运行测试
promtool test rules test_recording_rules.yml

# 输出示例
Unit Testing: test_recording_rules.yml
  SUCCESS
```

---

## 7.8 Recording Rules最佳实践

### 7.8.1 何时使用Recording Rules

**✅ 适合使用**:
- 复杂查询被多次使用(Dashboard、告警)
- 查询计算耗时较长(>1秒)
- 需要预聚合数据以支持长期存储

**❌ 不建议使用**:
- 简单的查询(如直接读取指标)
- 一次性查询或很少使用的查询
- 标签基数会爆炸的聚合

### 7.8.2 性能考虑

**1. 控制Recording Rules数量**:
```yaml
# ❌ 过度使用
- record: instance_method_path_status:http_requests:rate5m
  expr: rate(http_requests_total[5m])  # 可能产生上万个序列

# ✅ 合理使用
- record: instance_method:http_requests:rate5m
  expr: sum by (instance, method) (rate(http_requests_total[5m]))
```

**2. 选择合适的评估间隔**:
```yaml
groups:
  # 关键指标 - 高频评估
  - name: critical_rules
    interval: 30s
    rules: [...]
  
  # 业务指标 - 低频评估
  - name: business_rules
    interval: 5m
    rules: [...]
```

**3. 避免循环依赖**:
```yaml
# ❌ 错误 - 循环依赖
- record: a
  expr: b + 1
- record: b
  expr: a + 1

# ✅ 正确 - 单向依赖
- record: level1
  expr: rate(metric[5m])
- record: level2
  expr: sum(level1)
```

### 7.8.3 存储优化

**1. 保留标签**:
```yaml
# 保留有用的标签,删除不必要的标签
- record: job:http_requests:rate5m
  expr: sum without (instance_id, pod_id) (rate(http_requests_total[5m]))
```

**2. 控制基数**:
```yaml
# ❌ 高基数 - 可能产生百万级序列
- record: user:http_requests:rate5m
  expr: sum by (user_id) (rate(http_requests_total[5m]))

# ✅ 低基数 - 合理聚合
- record: service:http_requests:rate5m
  expr: sum by (service) (rate(http_requests_total[5m]))
```

---

## 7.9 故障排查

### 7.9.1 检查Recording Rules执行

**查看规则状态**:
- 访问: http://prometheus:9090/rules
- 查看每个规则的评估时间、样本数

**检查规则指标**:
```promql
# 规则评估耗时
prometheus_rule_evaluation_duration_seconds

# 规则评估失败次数
prometheus_rule_evaluation_failures_total

# 规则评估次数
prometheus_rule_evaluations_total
```

### 7.9.2 常见问题

**问题1: Recording Rule未生成数据**

检查:
1. 规则语法是否正确
2. 源指标是否存在
3. 评估间隔是否合理

**问题2: 查询Recording Rule返回空**

检查:
1. 标签是否匹配
2. 时间范围是否正确
3. 是否刚创建(需要等待一个评估周期)

**问题3: Recording Rule占用过多资源**

优化:
1. 减少规则数量
2. 增加评估间隔
3. 降低标签基数

---

## 7.10 本章小结

### 核心知识点

✅ **Recording Rules**: 预计算复杂查询,提升性能

✅ **命名规范**: `level:metric:operations`

✅ **分层聚合**: 实例 → Job → 集群

✅ **最佳实践**: 控制数量、合理间隔、单元测试

### 性能对比

| 查询类型 | 执行时间 | 适用场景 |
|---------|---------|---------|
| 复杂PromQL | 2-5秒 | 一次性查询 |
| Recording Rule | 10-50ms | Dashboard、告警 |

### 下一章预告

**第8章 - Pushgateway推送网关**,将学习:
- 📤 Pushgateway使用场景
- 🔧 批处理作业监控
- ⚠️ 最佳实践和注意事项

---

**🎉 恭喜!** 你已经掌握了Recording Rules的核心知识!
