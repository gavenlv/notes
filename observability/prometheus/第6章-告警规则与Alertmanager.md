# 第6章：告警规则与Alertmanager

> **学习时长**: 8-10小时  
> **难度**: ⭐⭐⭐⭐  
> **重要性**: ⭐⭐⭐⭐⭐ (生产环境必备)

## 本章目标

学完本章后,你将能够:

- ✅ 编写Prometheus告警规则
- ✅ 配置和部署Alertmanager
- ✅ 设置多种通知渠道(Email、Slack、钉钉、企业微信)
- ✅ 掌握告警路由和分组策略
- ✅ 使用告警抑制和静默功能
- ✅ 设计完整的告警体系
- ✅ 实施告警最佳实践

---

## 6.1 告警概述

### 6.1.1 告警工作流程

```
Prometheus → 评估告警规则 → 触发告警 → Alertmanager → 路由/分组/抑制 → 通知渠道
    ↓              ↓               ↓            ↓                ↓
  查询数据      每15秒评估      发送到AM      去重/聚合        Email/Slack等
```

### 6.1.2 告警状态

| 状态 | 说明 |
|------|------|
| **Inactive** | 未激活(未触发) |
| **Pending** | 已触发但未达到持续时间(`for`子句) |
| **Firing** | 已触发并发送到Alertmanager |

---

## 6.2 编写告警规则

### 6.2.1 告警规则语法

**基本结构**:

```yaml
groups:
  - name: <group_name>
    interval: <evaluation_interval>
    rules:
      - alert: <alert_name>
        expr: <promql_expression>
        for: <duration>
        labels:
          <label_name>: <label_value>
        annotations:
          <annotation_name>: <annotation_value>
```

**字段说明**:
- `alert`: 告警名称
- `expr`: PromQL表达式
- `for`: 持续时间(可选)
- `labels`: 告警标签
- `annotations`: 告警描述(支持模板)

### 6.2.2 基础告警规则示例

**创建规则文件**: `/etc/prometheus/rules/alerts.yml`

```yaml
groups:
  - name: node_alerts
    interval: 15s
    rules:
      # 节点宕机
      - alert: NodeDown
        expr: up{job="node-exporter"} == 0
        for: 1m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          summary: "节点{{ $labels.instance }}宕机"
          description: "节点{{ $labels.instance }}已宕机超过1分钟"

      # CPU使用率过高
      - alert: HighCpuUsage
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "节点{{ $labels.instance }}CPU使用率过高"
          description: "CPU使用率为{{ $value | humanize }}%,已持续5分钟"

      # 内存使用率过高
      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "节点{{ $labels.instance }}内存使用率过高"
          description: "内存使用率为{{ $value | humanize }}%"

      # 磁盘空间不足
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{fstype!~"tmpfs|devtmpfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|devtmpfs"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          summary: "节点{{ $labels.instance }}磁盘空间不足"
          description: "挂载点{{ $labels.mountpoint }}剩余空间{{ $value | humanize }}%"

      # 磁盘将在4小时内用完
      - alert: DiskWillFillIn4Hours
        expr: predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|devtmpfs"}[1h], 4*3600) < 0
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "节点{{ $labels.instance }}磁盘即将用完"
          description: "预计4小时后磁盘{{ $labels.mountpoint }}将用完"
```

### 6.2.3 应用程序告警规则

```yaml
groups:
  - name: application_alerts
    rules:
      # 服务不可用
      - alert: ServiceDown
        expr: up{job="my-service"} == 0
        for: 2m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "服务{{ $labels.job }}不可用"
          description: "实例{{ $labels.instance }}已宕机超过2分钟"

      # 错误率过高
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (instance)
          /
          sum(rate(http_requests_total[5m])) by (instance) * 100 > 5
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "服务{{ $labels.instance }}错误率过高"
          description: "错误率为{{ $value | humanize }}%,已持续5分钟"

      # 响应时间过长
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "服务{{ $labels.instance }}响应延迟过高"
          description: "p95延迟为{{ $value | humanize }}秒"

      # QPS异常下降
      - alert: LowQPS
        expr: |
          sum(rate(http_requests_total[5m])) by (instance) < 10
          and
          sum(rate(http_requests_total[5m] offset 1h)) by (instance) > 100
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "服务{{ $labels.instance }}QPS异常下降"
          description: "当前QPS为{{ $value | humanize }},1小时前为100+"
```

### 6.2.4 数据库告警规则

```yaml
groups:
  - name: database_alerts
    rules:
      # MySQL宕机
      - alert: MysqlDown
        expr: mysql_up == 0
        for: 1m
        labels:
          severity: critical
          team: dba
        annotations:
          summary: "MySQL实例{{ $labels.instance }}宕机"

      # 慢查询过多
      - alert: MysqlSlowQueries
        expr: rate(mysql_global_status_slow_queries[5m]) > 10
        for: 5m
        labels:
          severity: warning
          team: dba
        annotations:
          summary: "MySQL实例{{ $labels.instance }}慢查询过多"
          description: "慢查询速率为{{ $value | humanize }}/s"

      # 连接数使用率过高
      - alert: MysqlConnectionsHigh
        expr: mysql_global_status_threads_connected / mysql_global_variables_max_connections * 100 > 80
        for: 5m
        labels:
          severity: warning
          team: dba
        annotations:
          summary: "MySQL实例{{ $labels.instance }}连接数过高"
          description: "连接数使用率为{{ $value | humanize }}%"

      # Redis内存使用率过高
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
          team: dba
        annotations:
          summary: "Redis实例{{ $labels.instance }}内存使用率过高"
          description: "内存使用率为{{ $value | humanize }}%"
```

### 6.2.5 配置Prometheus加载规则

在`prometheus.yml`中配置:

```yaml
rule_files:
  - "/etc/prometheus/rules/*.yml"
  - "/etc/prometheus/rules/alerts/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'
```

**重载配置**:

```bash
# 方式1: 发送SIGHUP信号
kill -HUP <prometheus_pid>

# 方式2: HTTP API
curl -X POST http://localhost:9090/-/reload

# 方式3: systemd
sudo systemctl reload prometheus
```

**验证规则**:

```bash
# 检查语法
promtool check rules /etc/prometheus/rules/alerts.yml

# 测试规则
promtool test rules test.yml
```

---

## 6.3 Alertmanager部署与配置

### 6.3.1 安装Alertmanager

**Docker方式**:

```bash
docker run -d \
  --name=alertmanager \
  -p 9093:9093 \
  -v /etc/alertmanager:/etc/alertmanager \
  prom/alertmanager:latest \
  --config.file=/etc/alertmanager/alertmanager.yml
```

**二进制安装**:

```bash
VERSION=0.26.0
wget https://github.com/prometheus/alertmanager/releases/download/v${VERSION}/alertmanager-${VERSION}.linux-amd64.tar.gz
tar xvfz alertmanager-${VERSION}.linux-amd64.tar.gz
cd alertmanager-${VERSION}.linux-amd64
./alertmanager --config.file=alertmanager.yml
```

### 6.3.2 Alertmanager配置文件

**基础配置** (`/etc/alertmanager/alertmanager.yml`):

```yaml
global:
  # SMTP配置(Email通知)
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'password'
  smtp_require_tls: true
  
  # 默认解析超时
  resolve_timeout: 5m

# 模板文件
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# 路由配置
route:
  # 默认接收者
  receiver: 'default'
  
  # 分组规则
  group_by: ['alertname', 'cluster', 'service']
  
  # 分组等待时间(首次告警)
  group_wait: 10s
  
  # 分组间隔时间(后续告警)
  group_interval: 10s
  
  # 重复告警间隔
  repeat_interval: 12h
  
  # 子路由
  routes:
    # critical级别告警 -> 电话通知
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true  # 继续匹配后续路由
    
    # 数据库告警 -> DBA团队
    - match:
        team: dba
      receiver: 'dba-team'
      group_by: ['alertname', 'instance']
    
    # 基础设施告警 -> 运维团队
    - match:
        team: infrastructure
      receiver: 'ops-team'
    
    # 后端服务告警 -> 后端团队
    - match:
        team: backend
      receiver: 'backend-team'

# 抑制规则
inhibit_rules:
  # 如果节点宕机,抑制该节点上的所有其他告警
  - source_match:
      alertname: 'NodeDown'
    target_match_re:
      alertname: '.*'
    equal: ['instance']
  
  # 如果服务完全宕机,抑制高错误率告警
  - source_match:
      alertname: 'ServiceDown'
    target_match:
      alertname: 'HighErrorRate'
    equal: ['instance']

# 接收者配置
receivers:
  # 默认接收者
  - name: 'default'
    email_configs:
      - to: 'team@example.com'
  
  # DBA团队
  - name: 'dba-team'
    email_configs:
      - to: 'dba@example.com'
        headers:
          Subject: '[DBA] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/XXX'
        channel: '#dba-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  # 运维团队
  - name: 'ops-team'
    email_configs:
      - to: 'ops@example.com'
    webhook_configs:
      - url: 'http://dingtalk-webhook/api/alert'
  
  # 后端团队
  - name: 'backend-team'
    email_configs:
      - to: 'backend@example.com'
    wechat_configs:
      - corp_id: 'ww1234567890'
        api_secret: 'secret'
        to_user: '@all'
        agent_id: '1000001'
  
  # PagerDuty (关键告警)
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-pagerduty-key'
```

### 6.3.3 告警模板

**创建模板文件** (`/etc/alertmanager/templates/email.tmpl`):

```
{{ define "email.default.subject" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .GroupLabels.SortedPairs.Values | join " " }}
{{ end }}

{{ define "email.default.html" }}
<!DOCTYPE html>
<html>
<head>
<style>
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  th { background-color: #f2f2f2; }
  .firing { background-color: #ffcccc; }
  .resolved { background-color: #ccffcc; }
</style>
</head>
<body>
<h2>告警通知</h2>

<h3>告警状态: {{ .Status }}</h3>
<p>分组: {{ .GroupLabels.SortedPairs }}</p>

{{ if gt (len .Alerts.Firing) 0 }}
<h3>🔥 触发中的告警 ({{ .Alerts.Firing | len }})</h3>
<table>
  <tr>
    <th>告警名称</th>
    <th>实例</th>
    <th>严重程度</th>
    <th>摘要</th>
    <th>触发时间</th>
  </tr>
  {{ range .Alerts.Firing }}
  <tr class="firing">
    <td>{{ .Labels.alertname }}</td>
    <td>{{ .Labels.instance }}</td>
    <td>{{ .Labels.severity }}</td>
    <td>{{ .Annotations.summary }}</td>
    <td>{{ .StartsAt.Format "2006-01-02 15:04:05" }}</td>
  </tr>
  {{ end }}
</table>
{{ end }}

{{ if gt (len .Alerts.Resolved) 0 }}
<h3>✅ 已恢复的告警 ({{ .Alerts.Resolved | len }})</h3>
<table>
  <tr>
    <th>告警名称</th>
    <th>实例</th>
    <th>恢复时间</th>
  </tr>
  {{ range .Alerts.Resolved }}
  <tr class="resolved">
    <td>{{ .Labels.alertname }}</td>
    <td>{{ .Labels.instance }}</td>
    <td>{{ .EndsAt.Format "2006-01-02 15:04:05" }}</td>
  </tr>
  {{ end }}
</table>
{{ end }}

<hr>
<p>Prometheus Alertmanager</p>
</body>
</html>
{{ end }}
```

---

## 6.4 通知渠道配置

### 6.4.1 Email通知

```yaml
receivers:
  - name: 'email-team'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'password'
        require_tls: true
        headers:
          Subject: '{{ template "email.default.subject" . }}'
        html: '{{ template "email.default.html" . }}'
```

### 6.4.2 Slack通知

```yaml
receivers:
  - name: 'slack-team'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
        channel: '#alerts'
        username: 'Prometheus'
        icon_emoji: ':prometheus:'
        title: '{{ .GroupLabels.alertname }}'
        title_link: 'http://prometheus.example.com'
        text: |
          {{ range .Alerts }}
          *严重程度:* `{{ .Labels.severity }}`
          *摘要:* {{ .Annotations.summary }}
          *描述:* {{ .Annotations.description }}
          {{ end }}
        color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
        send_resolved: true
```

### 6.4.3 钉钉通知

钉钉需要使用Webhook,需要中间转换器。

**钉钉Webhook转换器** (Python):

```python
#!/usr/bin/env python3
"""
Alertmanager钉钉Webhook转换器
"""

from flask import Flask, request
import requests
import json

app = Flask(__name__)

DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"

@app.route('/api/alert', methods=['POST'])
def dingtalk_alert():
    data = request.json
    
    # 构造钉钉消息
    alerts = data.get('alerts', [])
    status = data.get('status', 'unknown')
    
    if status == 'firing':
        title = f"🔥 告警触发 ({len(alerts)}条)"
        color = "#FF0000"
    else:
        title = f"✅ 告警恢复 ({len(alerts)}条)"
        color = "#00FF00"
    
    text = f"### {title}\n\n"
    
    for alert in alerts:
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        
        text += f"**告警名称:** {labels.get('alertname', 'N/A')}\n\n"
        text += f"**实例:** {labels.get('instance', 'N/A')}\n\n"
        text += f"**严重程度:** {labels.get('severity', 'N/A')}\n\n"
        text += f"**摘要:** {annotations.get('summary', 'N/A')}\n\n"
        text += f"**描述:** {annotations.get('description', 'N/A')}\n\n"
        text += "---\n\n"
    
    # 发送到钉钉
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        }
    }
    
    requests.post(DINGTALK_WEBHOOK, json=payload)
    
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Alertmanager配置**:

```yaml
receivers:
  - name: 'dingtalk'
    webhook_configs:
      - url: 'http://localhost:5000/api/alert'
        send_resolved: true
```

### 6.4.4 企业微信通知

```yaml
receivers:
  - name: 'wechat-team'
    wechat_configs:
      - corp_id: 'ww1234567890abcdef'
        api_secret: 'your-api-secret'
        to_user: '@all'  # 或指定用户ID
        agent_id: '1000001'
        api_url: 'https://qyapi.weixin.qq.com/cgi-bin/'
        message: |
          {{ range .Alerts }}
          告警: {{ .Labels.alertname }}
          实例: {{ .Labels.instance }}
          级别: {{ .Labels.severity }}
          摘要: {{ .Annotations.summary }}
          {{ end }}
        send_resolved: true
```

---

## 6.5 告警路由策略

### 6.5.1 基于标签的路由

```yaml
route:
  receiver: 'default'
  group_by: ['alertname']
  
  routes:
    # critical级别 -> 24x7值班
    - match:
        severity: critical
      receiver: 'oncall'
      group_wait: 0s
      group_interval: 1m
      repeat_interval: 1h
    
    # warning级别 -> 工作时间通知
    - match:
        severity: warning
      receiver: 'work-hours'
      group_wait: 5m
      group_interval: 10m
      repeat_interval: 4h
    
    # info级别 -> 仅记录
    - match:
        severity: info
      receiver: 'logger'
      group_interval: 1h
      repeat_interval: 24h
```

### 6.5.2 基于时间的路由

```yaml
route:
  receiver: 'default'
  
  routes:
    # 工作日白天 -> Slack
    - match:
        severity: warning
      receiver: 'slack'
      active_time_intervals:
        - weekdays_daytime
    
    # 非工作时间 -> Email
    - match:
        severity: warning
      receiver: 'email'
      active_time_intervals:
        - weekends
        - weekdays_night

# 时间区间定义
time_intervals:
  - name: weekdays_daytime
    time_intervals:
      - times:
          - start_time: '09:00'
            end_time: '18:00'
        weekdays: ['monday:friday']
  
  - name: weekdays_night
    time_intervals:
      - times:
          - start_time: '18:00'
            end_time: '09:00'
        weekdays: ['monday:friday']
  
  - name: weekends
    time_intervals:
      - weekdays: ['saturday', 'sunday']
```

### 6.5.3 多级路由

```yaml
route:
  receiver: 'default'
  group_by: ['cluster', 'alertname']
  
  routes:
    # 生产环境
    - match:
        env: production
      receiver: 'prod-team'
      group_wait: 10s
      
      routes:
        # 生产环境critical -> 立即通知
        - match:
            severity: critical
          receiver: 'prod-oncall'
          group_wait: 0s
        
        # 生产环境warning -> 延迟通知
        - match:
            severity: warning
          receiver: 'prod-team'
          group_wait: 5m
    
    # 测试环境 -> 低优先级
    - match:
        env: testing
      receiver: 'test-team'
      group_wait: 10m
      repeat_interval: 24h
```

---

## 6.6 告警抑制与静默

### 6.6.1 告警抑制 (Inhibition)

抑制规则用于在某个告警触发时,自动抑制其他相关告警。

```yaml
inhibit_rules:
  # 节点宕机时,抑制该节点的所有告警
  - source_match:
      alertname: 'NodeDown'
    target_match_re:
      alertname: '.*'
    equal: ['instance']
  
  # 服务完全宕机时,抑制性能告警
  - source_match:
      alertname: 'ServiceDown'
    target_match_re:
      alertname: '(HighLatency|HighErrorRate|HighCpuUsage)'
    equal: ['instance', 'job']
  
  # 磁盘空间严重不足时,抑制预测告警
  - source_match:
      alertname: 'DiskSpaceCritical'
      severity: critical
    target_match:
      alertname: 'DiskWillFillIn4Hours'
    equal: ['instance', 'mountpoint']
```

### 6.6.2 告警静默 (Silence)

静默用于临时屏蔽告警,常用于维护窗口。

**通过Web UI创建静默**:
1. 访问 http://alertmanager:9093
2. 点击"Silences"
3. 点击"New Silence"
4. 配置匹配器和持续时间

**通过amtool CLI创建静默**:

```bash
# 安装amtool
go install github.com/prometheus/alertmanager/cmd/amtool@latest

# 静默特定告警
amtool silence add \
  alertname=HighCpuUsage \
  instance=web-01:9100 \
  --duration=2h \
  --author="ops@example.com" \
  --comment="计划维护"

# 静默整个节点
amtool silence add \
  instance=web-01:9100 \
  --duration=4h \
  --comment="服务器维护"

# 查看所有静默
amtool silence query

# 删除静默
amtool silence expire <silence_id>
```

**通过API创建静默**:

```bash
curl -X POST http://alertmanager:9093/api/v2/silences \
  -H 'Content-Type: application/json' \
  -d '{
    "matchers": [
      {
        "name": "alertname",
        "value": "HighCpuUsage",
        "isRegex": false
      },
      {
        "name": "instance",
        "value": "web-01:9100",
        "isRegex": false
      }
    ],
    "startsAt": "2024-01-01T00:00:00Z",
    "endsAt": "2024-01-01T04:00:00Z",
    "createdBy": "ops@example.com",
    "comment": "计划维护"
  }'
```

---

## 6.7 告警最佳实践

### 6.7.1 告警命名规范

```
✅ 好的命名:
- NodeDown
- HighCpuUsage
- DiskSpaceLow
- ServiceLatencyHigh

❌ 差的命名:
- alert1
- node_problem
- check_cpu
```

### 6.7.2 告警级别定义

| 级别 | 含义 | 响应时间 | 示例 |
|------|------|---------|------|
| **critical** | 严重影响业务,需要立即处理 | 立即 | 服务宕机、数据丢失 |
| **warning** | 可能影响业务,需要关注 | 工作时间内 | CPU高、内存高 |
| **info** | 信息性告警,无需立即处理 | 可忽略 | 证书即将过期(30天) |

### 6.7.3 告警描述最佳实践

```yaml
annotations:
  # ✅ 好的描述
  summary: "节点{{ $labels.instance }}CPU使用率为{{ $value | humanize }}%"
  description: |
    节点{{ $labels.instance }}的CPU使用率已超过80%阈值,当前值为{{ $value | humanize }}%。
    
    可能原因:
    1. 应用负载增加
    2. 后台任务占用
    3. 病毒或恶意进程
    
    排查步骤:
    1. 登录服务器查看top命令
    2. 检查应用日志
    3. 查看定时任务
    
    Runbook: https://wiki.example.com/runbook/high-cpu

  # ❌ 差的描述
  summary: "CPU高"
  description: "CPU使用率过高"
```

### 6.7.4 避免告警疲劳

**问题**: 告警太多导致麻木

**解决方案**:

1. **合理设置阈值**:
```yaml
# ❌ 过于敏感
expr: node_cpu_usage > 50
for: 1m

# ✅ 合理设置
expr: node_cpu_usage > 80
for: 5m
```

2. **使用`for`子句避免抖动**:
```yaml
# ✅ 持续5分钟才告警
expr: http_requests_total{status="500"} > 100
for: 5m
```

3. **合理分组**:
```yaml
group_by: ['alertname', 'cluster']
group_wait: 30s
group_interval: 5m
```

4. **设置合理的重复间隔**:
```yaml
repeat_interval: 4h  # 不要太频繁
```

### 6.7.5 告警覆盖率

使用"四个黄金信号"(Google SRE):

1. **延迟** (Latency):
```yaml
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
```

2. **流量** (Traffic):
```yaml
- alert: LowTraffic
  expr: sum(rate(http_requests_total[5m])) < 10
```

3. **错误** (Errors):
```yaml
- alert: HighErrorRate
  expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
```

4. **饱和度** (Saturation):
```yaml
- alert: HighCpuSaturation
  expr: instance:node_cpu:ratio > 0.8
```

---

## 6.8 实验练习

实验环境位于`code/chapter06/`目录。

### 实验1: 编写基础告警规则
1. 创建节点监控告警
2. 测试告警触发
3. 验证告警恢复

### 实验2: 配置Alertmanager
1. 部署Alertmanager
2. 配置Email通知
3. 测试告警发送

### 实验3: 告警路由实战
1. 配置多级路由
2. 测试不同严重级别的告警
3. 验证路由分发

---

## 6.9 本章小结

### 核心知识点

✅ **告警规则**: expr、for、labels、annotations

✅ **Alertmanager**: 路由、分组、抑制、静默

✅ **通知渠道**: Email、Slack、钉钉、企业微信

✅ **路由策略**: 基于标签、基于时间、多级路由

✅ **最佳实践**: 合理阈值、避免告警疲劳、完善描述

### 下一章预告

**第7章 - Recording Rules记录规则**,将学习:
- 📊 Recording Rules原理
- ⚡ 预聚合查询优化
- 🎯 最佳实践和设计模式

---

**🎉 恭喜!** 你已经掌握了Prometheus告警系统的核心能力!
