# Chapter 2: Grafana Fundamentals

## 2.1 Understanding the Grafana Interface

### 2.1.1 Main Navigation (Side Menu)

When you log into Grafana, you'll see a collapsible side menu on the left. Let's explore each section:

#### Home (🏠)
- **Recent dashboards**: Quick access to your recently viewed dashboards
- **Starred dashboards**: Dashboards you've marked as favorites
- **Search**: Find dashboards by name or tags

#### Search (🔍)
- Search for dashboards, folders, and alerts
- Filter by tags, folders, or starred status
- Keyboard shortcut: `Ctrl+K` (Windows/Linux) or `Cmd+K` (Mac)

#### Dashboards
- **Browse**: Navigate through folders and dashboards
- **Playlists**: Create automatic rotation of dashboards
- **Snapshots**: Create shareable snapshots of dashboards
- **Library panels**: Reusable panels across dashboards
- **New dashboard**: Create a new dashboard
- **New folder**: Organize dashboards into folders

#### Explore (🧭)
- Ad-hoc querying and data exploration
- Test queries without creating dashboards
- Compare data from multiple sources
- Perfect for troubleshooting and investigation

#### Alerting (🔔)
- **Alert rules**: Define when alerts should fire
- **Notification policies**: Configure routing of alerts
- **Silences**: Temporarily mute alerts
- **Contact points**: Set up notification channels
- **Alert groups**: View active and firing alerts

#### Configuration (⚙️)
- **Data sources**: Add and manage data sources
- **Users**: Manage user accounts
- **Teams**: Organize users into teams
- **Plugins**: Install and configure plugins
- **Preferences**: Organization and dashboard preferences
- **API keys**: Generate API keys for automation

#### Server Admin (👤)
*Only visible to admin users*
- **Users**: Global user management
- **Organizations**: Manage organizations
- **Settings**: Server-wide settings
- **Stats**: Usage statistics and metrics

---

## 2.2 Working with Data Sources

### 2.2.1 What is a Data Source?

A data source is a storage backend for your metrics, logs, or traces. Grafana doesn't store data itself—it queries external systems.

**Common Data Source Types:**
- **Time series databases**: Prometheus, InfluxDB, Graphite
- **Relational databases**: MySQL, PostgreSQL, Microsoft SQL Server
- **Logging systems**: Loki, Elasticsearch
- **Cloud monitoring**: CloudWatch, Azure Monitor, Google Cloud Monitoring
- **Tracing systems**: Jaeger, Tempo, Zipkin
- **Others**: TestData, CSV, JSON API

### 2.2.2 Adding a Data Source

Let's add different types of data sources step by step.

#### Adding Prometheus Data Source

**Step 1: Navigate to Data Sources**
1. Click on ⚙️ Configuration → Data sources
2. Click "Add data source"
3. Search for "Prometheus"
4. Click on "Prometheus"

**Step 2: Configure Connection**
```yaml
Name: Prometheus
Default: ✓ (check this box)

HTTP:
  URL: http://localhost:9090
  Access: Server (default)
  
Auth:
  (leave all unchecked for basic setup)

Additional settings:
  Scrape interval: 15s
  Query timeout: 60s
  HTTP Method: POST
```

**Step 3: Test and Save**
1. Scroll down and click "Save & test"
2. Should see: "Data source is working"

**What each setting means:**

- **Name**: Identifier for this data source in Grafana
- **Default**: Makes this the default data source for new panels
- **URL**: Prometheus server address
- **Access**: 
  - **Server**: Grafana backend connects (use this for Docker/internal networks)
  - **Browser**: Your browser connects directly (use for external services)
- **Scrape interval**: How often Prometheus collects metrics (helps with query building)

#### Adding MySQL Data Source

**Prerequisites:**
- MySQL server running
- Database created
- User with SELECT permissions

**Configuration:**
```yaml
Name: MySQL Database
Default: ☐

MySQL Connection:
  Host: localhost:3306
  Database: mydb
  User: grafana_reader
  Password: ********
  
TLS/SSL:
  (optional) Enable TLS/SSL
  
Additional settings:
  Max open connections: 100
  Max idle connections: 2
  Max connection lifetime: 14400
```

**Test Query:**
After saving, test with this query in Explore:
```sql
SELECT NOW() as time, 1 as value
```

#### Adding TestData Data Source (Built-in)

TestData is perfect for learning and testing without external dependencies.

**Step 1: Add TestData**
1. Configuration → Data sources → Add data source
2. Search "TestData"
3. Click on "TestData DB"
4. Click "Save & test"

**Step 2: Available Scenarios**

TestData provides several scenarios:
- **Random Walk**: Random time series data
- **CSV Content**: Parse CSV data
- **Streaming Client**: Live streaming data
- **Logs**: Sample log entries
- **Live**: Real-time data with configurable interval
- **Simulation**: Sine wave, square wave patterns
- **USA generated data**: US-based fake data
- **Grafana API**: Internal Grafana metrics
- **Arrow**: Apache Arrow format data

See example: [code/chapter02/01-datasources/testdata-examples.md](code/chapter02/01-datasources/testdata-examples.md)

### 2.2.3 Data Source Permissions

You can control who can query which data sources:

1. Go to Configuration → Data sources
2. Click on a data source
3. Go to "Permissions" tab
4. Click "Enable"
5. Add users or teams with query permissions

---

## 2.3 Understanding Dashboards

### 2.3.1 Dashboard Basics

A **dashboard** is a collection of panels arranged in rows and columns that visualize your data.

**Dashboard Components:**
- **Panels**: Individual visualizations (graphs, tables, stats)
- **Rows**: Horizontal containers for panels (can be collapsed)
- **Variables**: Dynamic filters for the entire dashboard
- **Time range**: Applies to all panels (unless overridden)
- **Annotations**: Event markers on graphs
- **Links**: Navigate between dashboards

### 2.3.2 Creating a Dashboard from Scratch

Let's create a comprehensive dashboard step by step.

**Step 1: Create Dashboard**
1. Click + icon → Dashboard
2. You'll see an empty dashboard

**Step 2: Add First Panel - Time Series**
1. Click "Add new panel"
2. Configure query:
   - Data source: TestData DB
   - Scenario: Random Walk
   - Series count: 3
3. Configure visualization:
   - Panel type: Time series
   - Title: "Server Response Time"
   - Unit: milliseconds (ms)
   - Legend: Show, As table, To the right
4. Click "Apply"

**Step 3: Add Second Panel - Gauge**
1. Click "+ Add" → Visualization
2. Configure query:
   - Data source: TestData DB
   - Scenario: Random Walk (single series)
3. Change visualization to **Gauge**:
   - Min: 0
   - Max: 100
   - Title: "CPU Usage"
   - Unit: percent (0-100)
   - Thresholds:
     - Green: 0 to 50
     - Yellow: 50 to 75
     - Red: 75 to 100
4. Click "Apply"

**Step 4: Add Third Panel - Table**
1. Click "+ Add" → Visualization
2. Configure query:
   - Data source: TestData DB
   - Scenario: CSV Content
   - Content:
     ```csv
     time,host,status,latency
     now-1h,server01,up,45
     now-1h,server02,up,38
     now-1h,server03,down,0
     now-1h,server04,up,52
     ```
3. Change visualization to **Table**:
   - Title: "Server Status"
4. Configure columns:
   - Add field override for "status":
     - Value mappings:
       - up → ✓ (green)
       - down → ✗ (red)
5. Click "Apply"

**Step 5: Arrange Panels**
- Drag panels to resize and reposition
- Create a layout like:
  ```
  ┌────────────────────┬──────┐
  │ Response Time      │ CPU  │
  │ (Time Series)      │(Gauge│
  ├────────────────────┴──────┤
  │ Server Status (Table)     │
  └───────────────────────────┘
  ```

**Step 6: Save Dashboard**
1. Click 💾 Save (top-right)
2. Name: "System Overview"
3. Folder: "General"
4. Click "Save"

See complete example: [code/chapter02/02-dashboards/system-overview.json](code/chapter02/02-dashboards/system-overview.json)

### 2.3.3 Dashboard Settings

Click on ⚙️ (gear icon) next to dashboard name to access settings:

#### General
```yaml
Name: My Dashboard
Description: System monitoring dashboard
Tags: monitoring, system, production
Folder: General
Timezone: Browser time
```

**Tags** help with:
- Dashboard organization
- Searching and filtering
- Grouping related dashboards

#### Variables
Create dashboard-wide filters (covered in detail in Chapter 6).

Example:
```yaml
Variable name: server
Type: Query
Query: label_values(up, instance)
Multi-value: ✓
Include all: ✓
```

Usage in queries: `up{instance="$server"}`

#### Annotations
Display events on graphs:
```yaml
Name: Deployments
Data source: Prometheus
Query: changes(deployment_version[1m])
Color: Green
```

#### Links
Link to related dashboards:
```yaml
Title: Go to Database Dashboard
Type: Dashboards
Tags: database
```

#### JSON Model
View and edit dashboard as JSON:
- Useful for version control
- Copy dashboards between instances
- Programmatic dashboard creation

---

## 2.4 Working with Panels

### 2.4.1 Panel Types Overview

Grafana offers many visualization types. Let's understand when to use each:

#### Time Series (formerly Graph)
**Use for**: Time-based data trends
- Server metrics over time
- Application performance
- Network traffic
- Temperature readings

**Features:**
- Multiple Y-axes
- Multiple series
- Fill opacity, line width
- Stacking, gradient
- Thresholds and alert states

#### Bar Chart
**Use for**: Comparing discrete values
- Request counts by endpoint
- Error rates by service
- Sales by region

#### Stat
**Use for**: Single value with change indication
- Current CPU usage
- Total requests today
- Active user count

**Features:**
- Shows current value
- Sparkline (mini graph)
- Color by thresholds
- Trend arrow

#### Gauge
**Use for**: Value within a range
- Disk usage (0-100%)
- Temperature (min-max)
- Progress indicators

#### Bar Gauge
**Use for**: Multiple gauges
- Multiple server CPU usage
- Team velocity metrics

#### Table
**Use for**: Tabular data
- Server inventory
- Log entries
- List of alerts

**Features:**
- Sortable columns
- Cell coloring
- Value mappings
- Column filtering

#### Pie Chart / Donut Chart
**Use for**: Part-to-whole relationships
- Resource distribution
- Error type breakdown
- Cost allocation

#### Heatmap
**Use for**: Density of values over time
- Request latency distribution
- Error occurrence patterns
- Server load patterns

#### Logs
**Use for**: Log data from Loki or Elasticsearch
- Application logs
- Error logs
- Audit logs

**Features:**
- Log level coloring
- Search and filter
- Context display
- Live tailing

#### Node Graph
**Use for**: Service relationships
- Microservices topology
- Network connections
- Dependency graphs

#### Geomap
**Use for**: Geographic data
- Server locations
- User distribution
- Sensor networks

### 2.4.2 Detailed Panel Configuration

Let's create a comprehensive panel with all options explained.

**Example: Advanced Time Series Panel**

**Step 1: Create Panel**
1. Add new panel to dashboard
2. Select Time series visualization

**Step 2: Query Configuration**

For Prometheus data source:
```promql
# Query A: Response time (p95)
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# Query B: Response time (p50)  
histogram_quantile(0.50,
  rate(http_request_duration_seconds_bucket[5m])
)

# Query C: Request rate
rate(http_requests_total[5m])
```

**Query Options:**
- **Legend**: `{{instance}} - {{handler}}`
- **Min step**: 15s (align with scrape interval)
- **Format**: Time series
- **Type**: Range

**Step 3: Panel Options**

```yaml
Title: HTTP Request Performance
Description: 95th and 50th percentile response times
Links:
  - Title: View Logs
    URL: /explore?...
```

**Step 4: Tooltip**

```yaml
Mode: All series
Sort order: Descending
```

**Tooltip modes:**
- **Single**: Show only hovered series
- **All**: Show all series
- **Hidden**: No tooltip

**Step 5: Legend**

```yaml
Visibility: Show
Mode: List (or Table for detailed stats)
Placement: Bottom (or Right)
Values to show:
  - Last
  - Min
  - Max
  - Mean
```

**Step 6: Graph Styles**

```yaml
Style: Line (or Bars, Points)
Line interpolation: Linear (or Smooth, Step)
Line width: 1
Fill opacity: 10
Gradient mode: Opacity
Point size: 5
Show points: Auto
```

**Step 7: Axis**

```yaml
Left Y-Axis:
  Unit: seconds (s)
  Scale: Linear (or Logarithmic)
  Min: 0
  Max: Auto
  Decimals: 2
  Label: Response Time

Right Y-Axis:
  (for Query C)
  Unit: requests/sec (reqps)
```

**Step 8: Standard Options**

```yaml
Unit: seconds (s)
Min: 0
Max: 100
Decimals: 2
Display name: ${__field.name}
Color scheme: From thresholds (By value)
No value: N/A
```

**Step 9: Thresholds**

```yaml
Mode: Absolute
Thresholds:
  - Base: Green (0)
  - Warning: Yellow (0.5)
  - Critical: Red (1.0)
```

**Step 10: Value Mappings**

Convert values to text:
```yaml
Value: 0 → Text: "No Data"
Range: 0.5 to 1.0 → Text: "Degraded"
```

**Step 11: Data Links**

Create clickable data points:
```yaml
Title: View logs for ${__field.labels.instance}
URL: /explore?queries=...&from=${__from}&to=${__to}
Open in new tab: ✓
```

See complete example: [code/chapter02/03-panels/advanced-timeseries.json](code/chapter02/03-panels/advanced-timeseries.json)

### 2.4.3 Panel Repeating

Create multiple panels from a variable.

**Example: CPU per Server**

**Step 1: Create Variable**
```yaml
Name: server
Query: label_values(node_cpu_seconds_total, instance)
Multi-value: ✗
```

**Step 2: Configure Panel**
Query:
```promql
rate(node_cpu_seconds_total{instance="$server"}[5m])
```

**Step 3: Enable Repeat**
Panel settings → Repeat options:
```yaml
Repeat by variable: server
Repeat direction: Horizontal
Max per row: 4
```

**Result**: One panel for each server value!

---

## 2.5 Understanding Queries

### 2.5.1 Query Editor Basics

The query editor is where you fetch data. It varies by data source type.

#### Prometheus Query Editor

**Builder Mode** (visual):
```
Metric: http_requests_total
Label filters:
  - job = "api"
  - status = "200"
Operations:
  - rate (range: 5m)
  - sum by (instance)
```

**Code Mode** (PromQL):
```promql
sum by (instance) (
  rate(http_requests_total{job="api", status="200"}[5m])
)
```

**Switch**: Toggle between Builder and Code with button in editor

#### SQL Query Editors (MySQL, PostgreSQL)

**Time series format:**
```sql
SELECT
  $__timeGroup(time_column, '1m') AS time,
  metric_name AS metric,
  AVG(value) AS value
FROM metrics_table
WHERE
  $__timeFilter(time_column)
  AND server = '$server'
GROUP BY time, metric
ORDER BY time
```

**Grafana Macros:**
- `$__timeFilter(column)`: Adds time range filter
- `$__timeGroup(column, interval)`: Groups by time interval
- `$__timeFrom()`: Start of time range
- `$__timeTo()`: End of time range

**Table format:**
```sql
SELECT
  hostname,
  status,
  cpu_usage,
  memory_usage,
  disk_usage
FROM server_status
WHERE last_updated > NOW() - INTERVAL 5 MINUTE
ORDER BY cpu_usage DESC
```

### 2.5.2 Query Options

Available for all data sources:

#### Query Inspector
- **Stats**: Query execution time, data size
- **JSON**: Raw request/response
- **Error**: Query errors and debugging

**Access**: Panel → Inspect → Query

#### Transform Data
Modify query results before visualization:

**Common transforms:**

1. **Merge**: Combine multiple queries
   ```
   Query A + Query B → Single result
   ```

2. **Filter by name**: Keep only certain fields
   ```
   Keep: cpu_usage, memory_usage
   Drop: disk_*
   ```

3. **Filter by value**: Row-level filtering
   ```
   cpu_usage > 50
   ```

4. **Organize fields**: Reorder and rename
   ```
   cpu_usage → CPU (%)
   memory_usage → Memory (%)
   ```

5. **Join by field**: Combine based on common field
   ```
   Join Query A and B on "hostname"
   ```

6. **Add field from calculation**:
   ```
   New field: total = cpu + memory
   ```

7. **Group by**: Aggregate data
   ```
   Group by: server
   Calculate: mean(cpu_usage)
   ```

8. **Series to rows**: Pivot time series
   ```
   Before: time | server1 | server2
   After:  time | server | value
   ```

See examples: [code/chapter02/04-transforms/](code/chapter02/04-transforms/)

### 2.5.3 Mixed Data Sources

Query multiple data sources in one panel!

**Example: Correlate Metrics and Logs**

**Query A** (Prometheus):
```promql
rate(http_errors_total[5m])
```

**Query B** (Loki):
```logql
{job="api"} |= "error"
```

**Result**: See error rate graph with log entries below

**Use cases:**
- Metrics from Prometheus + logs from Loki
- Application metrics + infrastructure metrics
- Multiple Prometheus instances
- Combining cloud providers (AWS + Azure)

---

## 2.6 Time Range and Refresh

### 2.6.1 Time Range Selector

Located in top-right corner of dashboard.

**Relative Ranges:**
```
Last 5 minutes   → now-5m  to now
Last 1 hour      → now-1h  to now
Last 24 hours    → now-24h to now
Last 7 days      → now-7d  to now
Last 30 days     → now-30d to now
Last 90 days     → now-90d to now
Last 6 months    → now-6M  to now
Last 1 year      → now-1y  to now
Last 2 years     → now-2y  to now
Last 5 years     → now-5y  to now
```

**Absolute Ranges:**
```
2024-01-01 00:00:00 to 2024-01-31 23:59:59
```

**Fiscal Ranges:**
```
This fiscal year
This fiscal quarter
```

**Zoom In:**
- Click and drag on any graph to zoom
- Click "Zoom out" to return

**Quick Ranges in URL:**
```
?from=now-6h&to=now
?from=1704067200000&to=1704153600000
```

### 2.6.2 Auto-Refresh

Automatically update dashboard at intervals.

**Available Intervals:**
```
Off (no refresh)
5s, 10s, 30s
1m, 5m, 15m, 30m
1h, 2h, 1d
```

**Set as Default:**
Dashboard settings → Time options:
```yaml
Timezone: Browser time
Auto refresh: 5s, 10s, 30s, 1m, 5m, 15m
Refresh live dashboards: ✓
Now delay: (leave empty)
Hide time picker: ☐
```

**Disable refresh on panel:**
Panel → Query options:
```yaml
Max data points: 1000
Min interval: 15s
Relative time: (override dashboard time)
Time shift: (shift time range)
Cache timeout: (override default)
Query timeout: 60s
```

### 2.6.3 Time Zone Handling

**Dashboard-level:**
Dashboard settings → General:
```
Timezone: Browser time (default)
Timezone: UTC
Timezone: America/New_York
```

**User-level:**
Profile → Preferences:
```
Timezone: Browser time
```

**In Queries:**
Most databases support timezone conversion:
```sql
-- MySQL
CONVERT_TZ(timestamp, '+00:00', 'America/New_York')

-- PostgreSQL  
timestamp AT TIME ZONE 'America/New_York'
```

---

## 2.7 Dashboard Sharing and Collaboration

### 2.7.1 Sharing Dashboards

Click "Share" button (top of dashboard):

#### Link
Share URL to dashboard:
```
Options:
  - Lock time range ✓
  - Theme: Current/Light/Dark
  - Shortened URL ✓
```

**Copy Link:**
```
https://grafana.example.com/d/abc123/my-dashboard?from=now-6h&to=now
```

#### Snapshot
Create static snapshot (no live data):
```
Snapshot name: Production Incident 2024-01-15
Expire: Never, 1 hour, 1 day, 1 week
Timeout: 4 seconds
External Snapshot: ☐
```

**Use cases:**
- Share with people without Grafana access
- Preserve state for incident reports
- Share publicly without exposing data source

**Note**: Snapshots contain actual data, consider security!

#### Export
Download dashboard JSON:
```
Export for sharing externally:
  - Removes dashboard ID
  - Removes panel IDs
  - Removes version info
```

**Use for:**
- Version control (Git)
- Moving between Grafana instances
- Dashboard templates

#### Library Panel
Make panel reusable across dashboards:
1. Click panel title → More → Create library panel
2. Name: "CPU Usage Widget"
3. Folder: "Shared Panels"
4. Save

**Use in other dashboards:**
- Add panel → Add from panel library
- Select your panel
- Changes sync across all dashboards!

### 2.7.2 Permissions

Control who can view and edit dashboards.

**Dashboard permissions:**
1. Dashboard settings → Permissions
2. Click "Add permission"
3. Select user, team, or role
4. Choose permission level:
   - **View**: Can view only
   - **Edit**: Can edit and save
   - **Admin**: Can change permissions

**Example:**
```
Role: Viewer → View
Team: DevOps → Edit
User: john@company.com → Admin
```

**Folder permissions:**
Permissions → Manage:
```
Folder: Production Dashboards
  Role: Viewer → View
  Team: SRE → Edit
```

All dashboards in folder inherit these permissions!

### 2.7.3 Playlists

Rotate through multiple dashboards automatically.

**Create Playlist:**
1. Dashboards → Playlists → New playlist
2. Name: "NOC Display"
3. Interval: 30s
4. Add dashboards:
   - System Overview
   - Application Metrics
   - Database Status
   - Network Traffic
5. Save

**Start Playlist:**
- Dashboards → Playlists → Click Play
- Or visit: `/playlists/play/<id>`

**Playlist URL:**
```
https://grafana.example.com/playlists/play/1?kiosk
```

**Kiosk Mode:**
Hides all UI elements (perfect for TVs):
```
?kiosk            # Full kiosk
?kiosk=tv         # TV mode (hide only top nav)
```

---

## 2.8 Organizing Dashboards

### 2.8.1 Folders

**Create Folder:**
1. Dashboards → Browse
2. Click "New Folder"
3. Name: "Production Monitoring"
4. Save

**Move Dashboard to Folder:**
1. Dashboard settings → General
2. Folder: Select folder
3. Save

**Folder Structure Example:**
```
├── General (default)
├── Production
│   ├── Application
│   ├── Infrastructure
│   └── Databases
├── Staging
├── Development
└── Templates
```

### 2.8.2 Tags

Add tags to dashboards for easy filtering:

Dashboard settings → General:
```
Tags: monitoring, production, application, nodejs
```

**Search by tags:**
- Home → Filter by tags
- Or: `/dashboards?tag=production&tag=monitoring`

**Best practices:**
```
Environment: production, staging, development
Team: backend, frontend, devops
Type: application, infrastructure, business
Technology: kubernetes, mysql, redis
```

### 2.8.3 Starred Dashboards

Mark important dashboards:
- Click ⭐ next to dashboard name
- Access from Home → Starred

---

## 2.9 Dashboard Best Practices

### 2.9.1 Design Principles

**1. Tell a Story**
Arrange panels to flow logically:
```
Top: High-level KPIs
Middle: Detailed metrics
Bottom: Troubleshooting info
```

**2. Use Consistent Colors**
```yaml
Green: Good/Normal
Yellow: Warning
Red: Critical/Error
Blue: Informational
```

**3. Limit Panel Count**
- Max 20-30 panels per dashboard
- Use drill-down links for details
- Create focused dashboards

**4. Descriptive Names**
❌ Bad: "Graph 1", "Panel 2"
✅ Good: "API Response Time (p95)", "Active Users"

**5. Add Context**
Use text panels for:
- Dashboard description
- Metric explanations
- Link to runbooks
- Alert thresholds

### 2.9.2 Performance Optimization

**1. Limit Time Range**
```
Default: Last 6 hours (not Last 30 days)
```

**2. Use Appropriate Intervals**
```promql
# Don't:
rate(http_requests[1s])  # Too granular

# Do:
rate(http_requests[5m])  # Appropriate
```

**3. Minimize Queries**
- Combine related queries
- Use dashboard variables
- Cache when possible

**4. Use Query Inspector**
Check query performance:
- Panel → Inspect → Stats
- Look for slow queries (>1s)

### 2.9.3 Naming Conventions

**Dashboards:**
```
[Team/Area] - [Purpose] - [Environment]

Examples:
DevOps - System Metrics - Production
Backend - API Performance - Staging
Frontend - User Analytics - Production
```

**Panels:**
```
[Metric] - [Aggregation] - [Context]

Examples:
Response Time - p95 - API Gateway
CPU Usage - Average - App Servers
Error Rate - Total - Payment Service
```

**Variables:**
```
Lowercase with underscores:
$server_name
$environment
$time_range
```

---

## 2.10 Hands-on Lab: Build a Complete Dashboard

Let's build a real-world monitoring dashboard.

### Lab Objective
Create a comprehensive application monitoring dashboard with:
- KPI summary at top
- Resource usage metrics
- Application performance metrics
- Error tracking
- Interactive filtering

### Prerequisites
- Docker Compose stack from Chapter 1 running
- Prometheus + Node Exporter
- TestData (for simulation)

### Lab Steps

**Step 1: Create Dashboard**
1. New Dashboard
2. Dashboard settings:
   - Name: "Application Monitoring"
   - Description: "Production application health dashboard"
   - Tags: production, monitoring, application
   - Folder: "Production"

**Step 2: Create Variables**

**Variable 1: Environment**
```yaml
Name: environment
Type: Custom
Values: production,staging,development
Multi-value: ☐
```

**Variable 2: Server**
```yaml
Name: server
Type: Query
Data source: Prometheus
Query: label_values(node_cpu_seconds_total, instance)
Multi-value: ✓
Include all: ✓
```

**Step 3: Row 1 - KPIs (Top)**

Create 4 Stat panels in a row:

**Panel 1: Uptime**
```
Visualization: Stat
Query (TestData): Random Walk (50-100 range)
Title: Uptime
Unit: percent (0-100)
Thresholds: Base=Green, 95=Yellow, 90=Red
```

**Panel 2: Requests/sec**
```
Query (TestData): Random Walk (1000-5000 range)
Title: Requests per Second
Unit: short
Sparkline: Show
Color: Blue
```

**Panel 3: Error Rate**
```
Query (TestData): Random Walk (0-5 range)
Title: Error Rate
Unit: percent (0.0-1.0)
Thresholds: 0=Green, 1=Yellow, 3=Red
```

**Panel 4: Avg Response Time**
```
Query (TestData): Random Walk (50-200 range)
Title: Avg Response Time
Unit: milliseconds (ms)
Thresholds: 0=Green, 100=Yellow, 150=Red
```

Arrange in single row at top.

**Step 4: Row 2 - Resource Usage**

**Panel 5: CPU Usage**
```
Visualization: Time series
Query (Prometheus):
  rate(node_cpu_seconds_total{instance=~"$server"}[5m])
Title: CPU Usage by Server
Legend: Show table, Last, Max, Mean
Fill: 10%
```

**Panel 6: Memory Usage**
```
Query (Prometheus):
  (1 - (node_memory_MemAvailable_bytes{instance=~"$server"} / 
   node_memory_MemTotal_bytes{instance=~"$server"})) * 100
Title: Memory Usage %
Unit: percent (0-100)
Thresholds: 0=Green, 70=Yellow, 85=Red
```

**Step 5: Row 3 - Application Metrics**

**Panel 7: Request Duration**
```
Query (TestData): Multiple random walks
  - p50: 50-100ms
  - p95: 100-200ms
  - p99: 150-300ms
Title: Request Duration (Percentiles)
Legend: p50, p95, p99
```

**Panel 8: Request Rate by Endpoint**
```
Visualization: Bar chart
Query (TestData): CSV Content
CSV:
  endpoint,requests
  /api/users,1500
  /api/orders,1200
  /api/products,800
  /api/search,600
Title: Top Endpoints by Request Count
```

**Step 6: Row 4 - Errors & Logs**

**Panel 9: Error Types**
```
Visualization: Pie chart
Query (TestData): CSV
CSV:
  type,count
  Timeout,45
  500 Error,23
  404 Not Found,67
  403 Forbidden,12
Title: Error Distribution
```

**Panel 10: Recent Errors (Table)**
```
Visualization: Table
Query (TestData): CSV
CSV:
  time,level,message,service
  now-5m,error,Connection timeout,api
  now-10m,error,Database unavailable,db
  now-15m,warning,High latency detected,api
Title: Recent Application Errors
```

**Step 7: Add Text Panel (Description)**

At very top of dashboard:
```markdown
# Application Monitoring Dashboard

**Environment:** ${environment}  
**Servers:** ${server}

This dashboard provides real-time monitoring of application health and performance.

**Key Metrics:**
- ✅ Uptime and availability
- 📊 Request rates and performance
- 💾 Resource utilization
- ❌ Error tracking and debugging

**Alerts:** Check the Alerting page for active alerts.

**Runbook:** [Incident Response Guide](#)
```

**Step 8: Save and Test**
1. Save dashboard
2. Test variable filtering
3. Test time range changes
4. Test auto-refresh

### Lab Result

You now have a production-ready dashboard with:
- ✅ High-level KPIs
- ✅ Resource monitoring
- ✅ Application metrics
- ✅ Error tracking
- ✅ Interactive filtering
- ✅ Documentation

**Complete dashboard JSON**: [code/chapter02/05-complete-dashboard/application-monitoring.json](code/chapter02/05-complete-dashboard/application-monitoring.json)

---

## 2.11 Summary

In this chapter, you learned:

✅ **Grafana Interface**: Navigation, menus, and features  
✅ **Data Sources**: Adding and configuring various data sources  
✅ **Dashboards**: Creating, organizing, and managing dashboards  
✅ **Panels**: Understanding visualization types and configuration  
✅ **Queries**: Building queries and transforming data  
✅ **Time Ranges**: Managing time selection and refresh  
✅ **Sharing**: Collaboration, permissions, and export  
✅ **Best Practices**: Design principles and optimization  
✅ **Hands-on**: Built a complete monitoring dashboard  

### What's Next?

In **Chapter 3**, we'll explore:
- Deep dive into specific data sources
- Prometheus configuration and PromQL
- InfluxDB and Flux queries
- SQL data sources (MySQL, PostgreSQL)
- Elasticsearch and log analysis
- Cloud monitoring integrations

---

## 2.12 Practice Exercises

### Exercise 1: Dashboard Creation
1. Create a dashboard with 6 panels using TestData
2. Include: Time series, Gauge, Table, Stat, Bar chart, Pie chart
3. Organize in rows
4. Add appropriate titles and units
5. Set meaningful thresholds

### Exercise 2: Data Transformation
1. Create a panel with 2 queries
2. Use "Merge" transformation to combine them
3. Use "Filter by value" to show only high values
4. Use "Add field from calculation" to create derived metric
5. Export and examine the JSON

### Exercise 3: Variables and Filtering
1. Create a dashboard with variables:
   - Environment (custom values)
   - Server (query from Prometheus)
   - Time range (interval)
2. Use variables in panel queries
3. Test filtering functionality

### Exercise 4: Dashboard Library
1. Create a reusable library panel (CPU usage)
2. Use it in 2 different dashboards
3. Modify the library panel
4. Verify changes appear in both dashboards

### Exercise 5: Permissions and Sharing
1. Create a folder "Production"
2. Set folder permissions (Viewer: View only)
3. Create a dashboard in the folder
4. Create a snapshot and share it
5. Export dashboard JSON

**Solutions**: [code/chapter02/06-exercises/](code/chapter02/06-exercises/)

---

## 2.13 Additional Resources

### Official Documentation
- [Dashboard Guide](https://grafana.com/docs/grafana/latest/dashboards/)
- [Panel Documentation](https://grafana.com/docs/grafana/latest/panels/)
- [Data Sources](https://grafana.com/docs/grafana/latest/datasources/)

### Community Dashboards
- [Grafana Dashboard Library](https://grafana.com/grafana/dashboards/)
- Search for pre-built dashboards for your data source

### Video Tutorials
- [Dashboard Best Practices](https://www.youtube.com/watch?v=videoid)
- [Effective Grafana Panels](https://www.youtube.com/watch?v=videoid)

---

**Next Chapter**: [Chapter 3: Data Sources Deep Dive](chapter03-datasources-deep-dive.md)
