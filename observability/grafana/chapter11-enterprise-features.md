# Chapter 11: Enterprise Features

## 11.1 Grafana Enterprise Overview

Enterprise features for large organizations.

### 11.1.1 Key Features

- **Reporting**: Scheduled PDF/CSV reports
- **RBAC**: Fine-grained permissions
- **Data source permissions**: Per-team access
- **Enterprise plugins**: Oracle, MongoDB, Splunk, etc.
- **Auditing**: Complete audit logs
- **Support**: 24/7 SLA support
- **White labeling**: Custom branding
- **Vault integration**: Secret management

---

## 11.2 Reporting (Enterprise)

### 11.2.1 Create Report

1. Dashboard → Share → Reporting
2. Configure:
   ```yaml
   Name: Weekly Performance Report
   Recipients: team@company.com
   Schedule: Weekly, Monday 9:00 AM
   Time range: Last 7 days
   Format: PDF
   Layout: Portrait
   ```

### 11.2.2 Email Template

```html
<h2>Weekly Performance Report</h2>
<p>Attached is the performance report for {{ .From }} to {{ .To }}</p>

<ul>
  <li>Dashboard: {{ .DashboardName }}</li>
  <li>Generated: {{ .Time }}</li>
</ul>
```

### 11.2.3 CSV Export

Export panel data as CSV:
```yaml
Panel → More → Export CSV
```

---

## 11.3 Role-Based Access Control (RBAC)

### 11.3.1 Permissions

**Granular permissions:**
- Dashboard: Create, Edit, Delete, View
- Folder: Create, Edit, Delete, View
- Data source: Query, Edit, Delete
- Alert: Create, Edit, Delete, View

### 11.3.2 Custom Roles

```yaml
Role: DevOps Engineer

Permissions:
  Dashboards:
    - Production folder: Edit
    - Staging folder: Edit
  Data sources:
    - Prometheus Production: Query
    - Loki Production: Query
  Alerts:
    - Create and edit: ✓
    - Delete: ✗
```

### 11.3.3 Team RBAC

```yaml
Team: Platform Team

Members: 15 users

Permissions:
  - Can create dashboards in "Platform" folder
  - Can query all production data sources
  - Can create alerts
  - Cannot delete dashboards
  - Cannot edit data sources
```

---

## 11.4 Enterprise Data Sources

### 11.4.1 Oracle

```yaml
Type: Oracle
Host: oracle.company.com:1521
Service name: PROD
Username: grafana_reader
Password: ********
```

### 11.4.2 MongoDB

```yaml
Type: MongoDB
Connection string: mongodb://mongodb:27017
Database: analytics
Authentication: SCRAM-SHA-1
```

### 11.4.3 Splunk

```yaml
Type: Splunk
URL: https://splunk.company.com:8089
Token: <splunk-token>
```

### 11.4.4 ServiceNow

```yaml
Type: ServiceNow
URL: https://company.service-now.com
Username: grafana
Password: ********
```

### 11.4.5 Snowflake

```yaml
Type: Snowflake
Account: xy12345.us-east-1
Username: GRAFANA_USER
Password: ********
Database: ANALYTICS
Warehouse: COMPUTE_WH
Role: GRAFANA_ROLE
```

---

## 11.5 Auditing

### 11.5.1 Enable Audit Logs

```ini
[auditing]
enabled = true
log_dashboard_content = true
```

### 11.5.2 Audit Events

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "user": "john@company.com",
  "action": "dashboard.create",
  "resource": "Production Metrics",
  "ip_address": "192.168.1.100",
  "result": "success"
}
```

### 11.5.3 Audit Queries

**Most active users:**
```sql
SELECT user, COUNT(*) as actions
FROM audit_log
WHERE timestamp > NOW() - INTERVAL 7 DAY
GROUP BY user
ORDER BY actions DESC
LIMIT 10
```

**Failed login attempts:**
```sql
SELECT user, ip_address, timestamp
FROM audit_log
WHERE action = 'login.failed'
AND timestamp > NOW() - INTERVAL 1 DAY
```

---

## 11.6 White Labeling

### 11.6.1 Custom Branding

```ini
[white_labeling]
app_title = Company Monitoring
login_logo = /public/img/company-logo.svg
login_background = /public/img/company-bg.jpg
footer_links = [
  {text: "Support", href: "https://support.company.com"},
  {text: "Docs", href: "https://docs.company.com"}
]
```

### 11.6.2 Custom CSS

**File: `public/css/custom.css`**
```css
.login-page {
  background-color: #1a1a2e;
}

.navbar-brand-logo {
  content: url('/public/img/custom-logo.svg');
}
```

---

## 11.7 Vault Integration

### 11.7.1 HashiCorp Vault

```ini
[secrets]
provider = vault

[secrets.vault]
address = https://vault.company.com:8200
token = s.xxxxxxxxxxxx
namespace = grafana
```

**Store secrets:**
```bash
vault kv put secret/grafana/datasources/prometheus password="secret123"
```

**Use in data source:**
```yaml
Password: $__vault{secret/grafana/datasources/prometheus:password}
```

---

## 11.8 Summary

✅ **Reporting**: Automated PDF/CSV reports  
✅ **RBAC**: Granular permissions  
✅ **Enterprise data sources**: Oracle, MongoDB, Splunk  
✅ **Auditing**: Complete activity tracking  
✅ **White labeling**: Custom branding  
✅ **Vault**: Secret management  

**Next Chapter**: [Chapter 12: Real-world Projects](chapter12-realworld-projects.md)
