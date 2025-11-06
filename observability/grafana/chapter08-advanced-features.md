# Chapter 8: Advanced Features

## 8.1 Annotations

Mark events on graphs for correlation with metrics.

### 8.1.1 Manual Annotations

**Add annotation:**
1. Click on graph
2. Add annotation
3. Text: "Deployment v2.3.4"
4. Tags: deployment, backend

### 8.1.2 Query-based Annotations

**From Prometheus:**
```yaml
Name: Deployments
Data source: Prometheus
Query: changes(app_version[1m])
Title field: Deployment
Tags field: tags
Text field: version
```

**From MySQL:**
```sql
SELECT
  timestamp as time,
  title,
  text,
  tags
FROM events
WHERE $__timeFilter(timestamp)
```

### 8.1.3 Built-in Annotations

**Grafana Alerts:**
```yaml
Enable: Grafana alerts annotation
```

Shows when alerts fire/resolve on graphs.

See examples: [code/chapter08/01-annotations/](code/chapter08/01-annotations/)

---

## 8.2 Plugins

Extend Grafana functionality.

### 8.2.1 Installing Plugins

**Via CLI:**
```bash
grafana-cli plugins install <plugin-id>
grafana-cli plugins install grafana-clock-panel
```

**Docker:**
```yaml
environment:
  - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-worldmap-panel
```

**Verify:**
```bash
grafana-cli plugins ls
```

### 8.2.2 Plugin Categories

**Panel plugins** (visualizations):
- Worldmap
- Pie Chart (v1)
- Clock
- Diagram
- Flowcharting

**Data source plugins**:
- JSON API
- SimpleJSON
- CSV
- MongoDB
- Oracle

**App plugins**:
- Kubernetes
- AWS IoT SiteWise
- Azure Monitor
- Zabbix

### 8.2.3 Popular Plugins

```bash
# Worldmap
grafana-cli plugins install grafana-worldmap-panel

# Pie Chart
grafana-cli plugins install grafana-piechart-panel

# Clock
grafana-cli plugins install grafana-clock-panel

# Boom table
grafana-cli plugins install yesoreyeram-boomtable-panel
```

### 8.2.4 Developing Custom Plugins

**Create plugin:**
```bash
npx @grafana/create-plugin@latest
```

**Plugin structure:**
```
my-plugin/
├── src/
│   ├── module.ts
│   ├── plugin.json
│   └── components/
├── package.json
└── README.md
```

See plugin development: [code/chapter08/02-plugin-development/](code/chapter08/02-plugin-development/)

---

## 8.3 Grafana API

Automate dashboard management and queries.

### 8.3.1 Create API Key

1. Configuration → API keys
2. New API key
3. Name: "automation"
4. Role: Admin/Editor/Viewer
5. Time to live: 30d

### 8.3.2 Common API Calls

**Get all dashboards:**
```bash
curl -H "Authorization: Bearer <API-KEY>" \
  http://localhost:3000/api/search
```

**Get dashboard by UID:**
```bash
curl -H "Authorization: Bearer <API-KEY>" \
  http://localhost:3000/api/dashboards/uid/<dashboard-uid>
```

**Create dashboard:**
```bash
curl -X POST \
  -H "Authorization: Bearer <API-KEY>" \
  -H "Content-Type: application/json" \
  -d @dashboard.json \
  http://localhost:3000/api/dashboards/db
```

**Update dashboard:**
```bash
curl -X POST \
  -H "Authorization: Bearer <API-KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": {...},
    "overwrite": true
  }' \
  http://localhost:3000/api/dashboards/db
```

**Delete dashboard:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer <API-KEY>" \
  http://localhost:3000/api/dashboards/uid/<dashboard-uid>
```

**Query data source:**
```bash
curl -X POST \
  -H "Authorization: Bearer <API-KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [{
      "refId": "A",
      "datasource": {"type": "prometheus"},
      "expr": "up",
      "range": true
    }],
    "from": "now-1h",
    "to": "now"
  }' \
  http://localhost:3000/api/ds/query
```

### 8.3.3 API with Python

```python
import requests

GRAFANA_URL = "http://localhost:3000"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# List dashboards
response = requests.get(f"{GRAFANA_URL}/api/search", headers=headers)
dashboards = response.json()

for dash in dashboards:
    print(f"{dash['title']} - {dash['uid']}")

# Create dashboard
dashboard_json = {
    "dashboard": {
        "title": "API Created Dashboard",
        "panels": [],
        "tags": ["api", "automated"]
    },
    "overwrite": False
}

response = requests.post(
    f"{GRAFANA_URL}/api/dashboards/db",
    headers=headers,
    json=dashboard_json
)
print(response.json())
```

See API examples: [code/chapter08/03-api-examples/](code/chapter08/03-api-examples/)

---

## 8.4 Provisioning

Auto-configure Grafana from files.

### 8.4.1 Data Source Provisioning

**File: `provisioning/datasources/prometheus.yml`**
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: 15s
```

### 8.4.2 Dashboard Provisioning

**File: `provisioning/dashboards/dashboards.yml`**
```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards
```

**Place dashboard JSON files in path:**
```
provisioning/dashboards/
  ├── dashboards.yml
  ├── system-overview.json
  └── application-metrics.json
```

### 8.4.3 Alert Provisioning

**File: `provisioning/alerting/alerts.yml`**
```yaml
apiVersion: 1

groups:
  - name: system-alerts
    interval: 1m
    rules:
      - uid: high-cpu
        title: High CPU Usage
        condition: A
        data:
          - refId: A
            datasourceUid: prometheus-uid
            model:
              expr: avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100 > 80
```

---

## 8.5 Library Panels

Reusable panels across dashboards.

### 8.5.1 Create Library Panel

1. Create panel
2. Panel menu → Create library panel
3. Name: "CPU Usage Widget"
4. Folder: "Shared Widgets"

### 8.5.2 Use Library Panel

1. Add panel → Add from library
2. Select "CPU Usage Widget"
3. Changes sync across all dashboards!

### 8.5.3 Unlink Library Panel

Convert back to regular panel:
- Panel menu → Unlink library panel

---

## 8.6 Explore

Ad-hoc querying without dashboards.

### 8.6.1 Features

- Query any data source
- No dashboard needed
- Log correlation
- Trace integration
- Table/graph views

### 8.6.2 Usage

**Access:**
Explore icon (compass) in sidebar

**Query metrics:**
```promql
rate(http_requests_total[5m])
```

**Query logs:**
```logql
{job="api"} |= "error"
```

**Split view:**
- Compare different queries
- Correlate metrics and logs
- View multiple time ranges

---

## 8.7 Reporting

Export dashboards as PDFs (Enterprise feature, or with renderer).

### 8.7.1 Image Renderer

**Install:**
```bash
grafana-cli plugins install grafana-image-renderer
```

**Docker:**
```yaml
services:
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_RENDERING_SERVER_URL=http://renderer:8081/render
      - GF_RENDERING_CALLBACK_URL=http://grafana:3000/
    depends_on:
      - renderer

  renderer:
    image: grafana/grafana-image-renderer:latest
    ports:
      - "8081:8081"
```

### 8.7.2 Export Dashboard

**Manual:**
1. Dashboard → Share → Export
2. Save as PDF

**API:**
```bash
curl -H "Authorization: Bearer <API-KEY>" \
  "http://localhost:3000/render/d-solo/<uid>/<dash>?orgId=1&panelId=2&width=1000&height=500" \
  -o panel.png
```

---

## 8.8 Summary

✅ **Annotations**: Event markers on graphs  
✅ **Plugins**: Extend functionality  
✅ **API**: Automate management  
✅ **Provisioning**: Configuration as code  
✅ **Library Panels**: Reusable widgets  
✅ **Explore**: Ad-hoc querying  
✅ **Reporting**: PDF/image export  

**Next Chapter**: [Chapter 9: Security and User Management](chapter09-security-user-management.md)
