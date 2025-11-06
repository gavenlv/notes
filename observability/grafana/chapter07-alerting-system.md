# Chapter 7: Alerting System

## 7.1 Grafana Alerting Overview

Grafana Unified Alerting system monitors your metrics and sends notifications when conditions are met.

### 7.1.1 Architecture

```
Alert Rules → Evaluation → Alert Instances → Notification Policies → Contact Points → Notifications
```

---

## 7.2 Creating Alert Rules

### 7.2.1 Basic Alert Rule

**Step 1: Create Rule**
1. Alerting → Alert rules → New alert rule

**Step 2: Configure Query**
```yaml
Rule name: High CPU Usage
Data source: Prometheus

Query A:
  avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100

Expression B (Reduce):
  Function: Last
  Mode: Strict

Expression C (Threshold):
  IS ABOVE: 80
```

**Step 3: Set Evaluation**
```yaml
Folder: Production Alerts
Evaluation group: System Alerts
Evaluation interval: 1m
Pending period: 5m  # Alert after 5min continuous breach
```

**Step 4: Add Details**
```yaml
Summary: CPU usage is {{ $values.B.Value }}% on {{ $labels.instance }}
Description: |
  Instance {{ $labels.instance }} has high CPU usage.
  
  Current: {{ $values.B.Value | humanize }}%
  Threshold: 80%
  
  Runbook: https://wiki.company.com/runbooks/high-cpu

Labels:
  severity: warning
  team: infrastructure
  service: {{ $labels.instance }}
```

### 7.2.2 Multi-Condition Alerts

```yaml
# Query A: CPU usage
avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100

# Query B: Memory usage  
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Expression C: Math (both high)
$A > 80 AND $B > 80

# Expression D: Threshold
IS ABOVE: 0
```

### 7.2.3 Template Annotations

```yaml
{{ $labels.instance }}     # Instance label
{{ $values.A.Value }}      # Query A value
{{ $values.A | humanize }} # Formatted value
{{ $labels }}              # All labels
{{ $values }}              # All values

# Conditionals
{{ if gt $values.A.Value 90 }}CRITICAL{{ else }}WARNING{{ end }}

# Formatting
{{ printf "%.2f" $values.A.Value }}
```

See alert examples: [code/chapter07/01-alert-rules/](code/chapter07/01-alert-rules/)

---

## 7.3 Notification Policies

Route alerts to correct teams/channels.

### 7.3.1 Default Policy

```yaml
Group by: [alertname]
Group wait: 30s
Group interval: 5m
Repeat interval: 4h

Contact point: default-email
```

### 7.3.2 Nested Policies

```yaml
Root Policy:
  Contact point: ops-team

  ├─ Match: severity=critical
  │  Contact point: pagerduty-oncall
  │  Continue: ✓
  │
  ├─ Match: team=database
  │  Contact point: dba-slack
  │  Mute timings: business-hours
  │
  └─ Match: team=frontend
     Contact point: frontend-email
```

### 7.3.3 Label Matching

```yaml
Matchers:
  - Label: severity
    Operator: =
    Value: critical

  - Label: environment
    Operator: =~
    Value: prod.*

  - Label: team
    Operator: !=
    Value: test
```

---

## 7.4 Contact Points

### 7.4.1 Email

```yaml
Name: ops-email
Type: Email

Addresses: ops@company.com, alerts@company.com
Single email: ☐
Message: |
  {{ template "email.default.subject" . }}
  
  {{ range .Alerts }}
  Alert: {{ .Labels.alertname }}
  Instance: {{ .Labels.instance }}
  Value: {{ .Values.B }}
  {{ end }}
```

### 7.4.2 Slack

```yaml
Name: ops-slack
Type: Slack

Webhook URL: https://hooks.slack.com/services/XXX/YYY/ZZZ
Channel: #alerts
Username: Grafana
Icon: https://grafana.com/icon.png

Title: {{ template "slack.default.title" . }}
Text: |
  {{ range .Alerts }}
  *{{ .Labels.severity | toUpper }}*: {{ .Labels.alertname }}
  Instance: {{ .Labels.instance }}
  Value: {{ .Values.B | humanize }}
  {{ end }}
```

### 7.4.3 PagerDuty

```yaml
Name: pagerduty-oncall
Type: PagerDuty

Integration Key: <your-integration-key>
Severity: {{ .Labels.severity }}
Class: {{ .Labels.alertname }}
Component: {{ .Labels.service }}
```

### 7.4.4 Webhook

```yaml
Name: custom-webhook
Type: Webhook

URL: https://api.company.com/alerts
HTTP Method: POST
Authorization: Bearer <token>

Message:
{
  "alert": "{{ .Labels.alertname }}",
  "severity": "{{ .Labels.severity }}",
  "instance": "{{ .Labels.instance }}",
  "value": {{ .Values.B }},
  "timestamp": "{{ .StartsAt }}"
}
```

### 7.4.5 Multiple Contact Points

```yaml
Contact point: critical-alerts

Integrations:
  1. PagerDuty (oncall team)
  2. Slack (#incidents channel)
  3. Email (management)
  4. Webhook (ticketing system)
```

---

## 7.5 Silences

Temporarily mute alerts.

### 7.5.1 Create Silence

```yaml
Matchers:
  - alertname = DiskSpaceLow
  - instance =~ server01.*

Duration: 2 hours
Comment: Planned maintenance - disk cleanup in progress
Creator: john@company.com
```

### 7.5.2 Silence Patterns

**Specific alert:**
```yaml
alertname = HighCPU
instance = server01
```

**All alerts from instance:**
```yaml
instance = server01
```

**All critical alerts:**
```yaml
severity = critical
```

**Regex matching:**
```yaml
instance =~ prod-.*
```

---

## 7.6 Alert Groups

View active alerts organized by label groups.

### 7.6.1 Grouping

```yaml
Group by:
  - alertname
  - instance
  - severity
```

### 7.6.2 States

- **Inactive**: Not firing
- **Pending**: Condition met, waiting for pending period
- **Firing**: Alert is active
- **Suppressed**: Silenced or inhibited

---

## 7.7 Advanced Alerting

### 7.7.1 Template Notifications

**Create template:**
```yaml
Name: custom-email-template
Content: |
  {{ define "email.custom.subject" }}
  [{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}
  {{ end }}

  {{ define "email.custom.html" }}
  <h2>Alert Details</h2>
  {{ range .Alerts }}
  <p>
    <strong>Alert:</strong> {{ .Labels.alertname }}<br>
    <strong>Instance:</strong> {{ .Labels.instance }}<br>
    <strong>Severity:</strong> {{ .Labels.severity }}<br>
    <strong>Value:</strong> {{ .Values.B | humanize }}<br>
    <strong>Started:</strong> {{ .StartsAt }}<br>
  </p>
  {{ end }}
  {{ end }}
```

**Use template:**
```yaml
Contact point → Email → Message:
  {{ template "email.custom.html" . }}
```

### 7.7.2 Mute Timings

Suppress alerts during specific times.

```yaml
Name: business-hours
Time intervals:
  - Weekdays: Monday-Friday
    Times: 09:00-17:00
    Location: America/New_York
```

**Apply to policy:**
```yaml
Notification policy:
  Mute timings: [business-hours]
```

### 7.7.3 Inhibition Rules

Suppress alerts when other alerts fire.

```yaml
# Suppress node alerts when node is down
Source matchers:
  - alertname = NodeDown

Target matchers:
  - alertname =~ Node.*

Equal:
  - instance
```

See advanced alerting: [code/chapter07/02-advanced-alerting/](code/chapter07/02-advanced-alerting/)

---

## 7.8 Summary

✅ **Alert rules**: Query-based conditions  
✅ **Notification policies**: Route alerts to teams  
✅ **Contact points**: Email, Slack, PagerDuty, webhooks  
✅ **Silences**: Temporary muting  
✅ **Templates**: Custom notification formats  
✅ **Mute timings**: Time-based suppression  

**Next Chapter**: [Chapter 8: Advanced Features](chapter08-advanced-features.md)
