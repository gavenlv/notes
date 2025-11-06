# Chapter 4: Visualization Mastery

## 4.1 Introduction to Visualizations

Grafana offers 20+ visualization types. Choosing the right one is crucial for effective data communication.

### 4.1.1 Visualization Selection Guide

| Data Type | Best Visualization | When to Use |
|-----------|-------------------|-------------|
| Time-series trends | Time series | Metrics over time, trends |
| Single current value | Stat | KPIs, current status |
| Value in range | Gauge | Percentage, capacity |
| Multiple values in ranges | Bar gauge | Comparing multiple metrics |
| Comparing values | Bar chart | Categorical comparisons |
| Part-whole relationship | Pie chart | Distribution, percentages |
| Tabular data | Table | Lists, detailed data |
| Density over time | Heatmap | Latency distribution |
| Text output | Logs | Log streams |
| Geographic data | Geomap | Location-based data |
| Relationships | Node graph | Service dependencies |
| Events | State timeline | Status changes over time |

---

## 4.2 Time Series Panel

The most common visualization for time-based metrics.

### 4.2.1 Basic Configuration

**Query Setup (Prometheus):**
```promql
rate(http_requests_total[5m])
```

**Panel Title:** `HTTP Request Rate`

### 4.2.2 Graph Styles

**Line Graph:**
```yaml
Style: Line
Line interpolation: Linear
Line width: 1
Fill opacity: 10
Point size: 5
Show points: Auto
```

**Smooth Line:**
```yaml
Line interpolation: Smooth
Fill opacity: 20
Gradient mode: Opacity
```

**Stacked Area:**
```yaml
Stack: Normal (or Percent)
Fill opacity: 100
Line width: 0
```

**Bars:**
```yaml
Style: Bars
Line width: 1
Fill opacity: 80
```

### 4.2.3 Multiple Y-Axes

**Left Axis (Requests):**
```yaml
Unit: requests/sec (reqps)
Scale: Linear
Min: 0
Decimals: 2
```

**Right Axis (Latency):**
```yaml
Unit: milliseconds (ms)
Scale: Linear
Placement: Right
Series overrides:
  - Select series: latency
  - Y-axis: Right
```

### 4.2.4 Thresholds and Alert Zones

**Visual Thresholds:**
```yaml
Thresholds:
  - Base: Green (0)
  - Warning: Yellow (100)
  - Critical: Red (200)

Show thresholds: As filled regions
```

### 4.2.5 Advanced Time Series Features

**Connected nulls:**
```yaml
Null value: Connected
```

**Stack series:**
```yaml
Stack: Normal
Stack series:
  - By percentage: Show % of total
```

**Transform data:**
```yaml
Transform:
  - Add: Difference (show rate of change)
```

See examples: [code/chapter04/01-timeseries-advanced/](code/chapter04/01-timeseries-advanced/)

---

## 4.3 Stat Panel

Display single value with optional sparkline and trend.

### 4.3.1 Basic Stat

**Configuration:**
```yaml
Title: Current CPU Usage
Value:
  - Last (non-null)
Unit: percent (0-100)
Decimal: 1

Stat styles:
  Orientation: Horizontal
  Text mode: Value and name
  Color mode: Value
  Graph mode: Area (sparkline)
```

### 4.3.2 Value Calculation

**Options:**
- Last (non-null) - Most recent value
- First (non-null) - Oldest value
- Last - Most recent (including null)
- Mean - Average
- Sum - Total
- Min - Minimum
- Max - Maximum
- Count - Number of values
- Delta - Difference between first and last
- Step - Difference between last two values
- Diff - Difference between max and min
- Range - Max minus min

### 4.3.3 Color Modes

**Value:**
Color by threshold value
```yaml
Thresholds:
  0: Green (Good)
  70: Yellow (Warning)
  90: Red (Critical)
```

**Background:**
Color entire panel background
```yaml
Color mode: Background
```

**Gradient:**
Smooth color transition
```yaml
Color mode: Background gradient
```

### 4.3.4 Text Modes

**Value:**
Show only the number
```yaml
Text mode: Value
```

**Value and name:**
Show metric name and value
```yaml
Text mode: Value and name
```

**Name:**
Show only metric name
```yaml
Text mode: Name
```

**None:**
Hide text (show only color/graph)
```yaml
Text mode: None
```

### 4.3.5 Stat with Multiple Values

**Query multiple series:**
```promql
node_cpu_usage{instance=~"server.*"}
```

**Display:**
```yaml
Orientation: Vertical
Values: All values from result
Text mode: Value and name
```

**Result:** Multiple stat panels, one per series!

---

## 4.4 Gauge Panel

Show value within a min-max range.

### 4.4.1 Basic Gauge

**Configuration:**
```yaml
Title: Disk Usage
Min: 0
Max: 100
Unit: percent (0-100)

Thresholds:
  0: Green
  60: Yellow
  80: Orange
  90: Red

Show threshold labels: ✓
Show threshold markers: ✓
```

### 4.4.2 Gauge Orientations

**Vertical:**
```yaml
Orientation: Vertical
```

**Horizontal:**
```yaml
Orientation: Horizontal
```

**Auto:**
```yaml
Orientation: Auto (adapts to panel size)
```

### 4.4.3 Multiple Gauges

**Query:**
```promql
disk_usage{mount=~"/.*"}
```

**Result:** One gauge per mount point

**Layout:**
```yaml
Repeat: By variable
Repeat direction: Horizontal
Max per row: 4
```

---

## 4.5 Bar Gauge Panel

Horizontal or vertical bars showing values.

### 4.5.1 Configuration

```yaml
Title: Server CPU Usage
Orientation: Horizontal
Display mode: Basic

Thresholds:
  0: Green
  50: Yellow
  75: Red

Show threshold markers: ✓
```

### 4.5.2 Display Modes

**Basic:**
Simple bars
```yaml
Display mode: Basic
```

**Gradient:**
Color gradient based on value
```yaml
Display mode: Gradient
```

**LCD:**
Retro LCD style
```yaml
Display mode: LCD
```

### 4.5.3 Stacking

**Vertical stacking:**
```yaml
Orientation: Horizontal
Multiple values: Stacked
```

### 4.5.4 Use Cases

**Server Comparison:**
```promql
avg by (instance) (rate(node_cpu_seconds_total[5m]))
```

**Service Latency:**
```promql
histogram_quantile(0.95, service_latency_bucket)
```

---

## 4.6 Table Panel

Display data in rows and columns.

### 4.6.1 Basic Table

**Query (MySQL):**
```sql
SELECT
  server_name AS Server,
  cpu_usage AS 'CPU %',
  memory_usage AS 'Memory %',
  disk_usage AS 'Disk %',
  status AS Status
FROM server_metrics
WHERE $__timeFilter(timestamp)
  AND timestamp = (SELECT MAX(timestamp) FROM server_metrics)
```

**Configuration:**
```yaml
Show header: ✓
Sortable: ✓
Filterable: ✓
```

### 4.6.2 Column Formatting

**CPU % Column:**
```yaml
Override:
  - Match: Field name (CPU %)
  - Unit: percent (0-100)
  - Decimals: 1
  - Color mode: Cell background
  - Thresholds:
      0: Green
      70: Yellow
      90: Red
```

**Status Column:**
```yaml
Override:
  - Match: Field name (Status)
  - Value mappings:
      up → ✓ (green)
      down → ✗ (red)
      unknown → ? (yellow)
```

### 4.6.3 Cell Display Modes

**Color:**
```yaml
Cell display mode: Color background
```

**Gauge:**
```yaml
Cell display mode: Gauge (basic/gradient/LCD)
Min: 0
Max: 100
```

**JSON:**
```yaml
Cell display mode: JSON view (for JSON columns)
```

**Image:**
```yaml
Cell display mode: Image (for image URLs)
```

### 4.6.4 Time Series to Table

Transform time series data into table:

**Query:**
```promql
node_cpu_usage{instance=~"server.*"}
```

**Transform:**
```yaml
Transform:
  1. Reduce: By last (non-null)
  2. Organize fields:
      - Instance
      - CPU Usage
  3. Sort by: CPU Usage (descending)
```

**Result:**
| Instance | CPU Usage |
|----------|-----------|
| server03 | 87.5 |
| server01 | 65.2 |
| server02 | 45.1 |

### 4.6.5 Advanced Table Features

**Row highlighting:**
```yaml
Override:
  - Match: Row (all columns)
  - Condition: CPU > 80
  - Background color: Red (opacity 20%)
```

**Links:**
```yaml
Override:
  - Match: Field (Server)
  - Data links:
      Title: View details
      URL: /d/server-details?var-server=${__value.text}
```

**Formatting:**
```yaml
Override:
  - Match: Field (Uptime)
  - Unit: duration (s)
  - Display: Auto
```

See examples: [code/chapter04/02-table-advanced/](code/chapter04/02-table-advanced/)

---

## 4.7 Bar Chart Panel

Compare categorical values.

### 4.7.1 Basic Bar Chart

**Query (PromQL):**
```promql
sum by (status_code) (rate(http_requests_total[5m]))
```

**Configuration:**
```yaml
Title: Requests by Status Code
Orientation: Horizontal (or Vertical)
X-axis: Status Code
Y-axis: Requests/sec

Bar display:
  Stacking: Off
  Group width: 0.7
  Bar width: 0.97
```

### 4.7.2 Grouped Bars

**Query:**
```promql
sum by (service, status_code) (rate(http_requests_total[5m]))
```

**Result:** Bars grouped by service, colored by status

**Configuration:**
```yaml
Grouping: By field (status_code)
```

### 4.7.3 Stacked Bars

**Query:**
```promql
sum by (endpoint) (rate(http_requests_total[5m]))
```

**Configuration:**
```yaml
Stacking: Normal (absolute values)
# or
Stacking: Percent (100% stacked)
```

### 4.7.4 Horizontal vs Vertical

**Horizontal** (better for long labels):
```yaml
Orientation: Horizontal
X-axis label: Requests/sec
Y-axis label: Endpoint
```

**Vertical** (traditional):
```yaml
Orientation: Vertical
X-axis label: Endpoint
Y-axis label: Requests/sec
```

---

## 4.8 Pie Chart / Donut Chart

Show proportions.

### 4.8.1 Basic Pie Chart

**Query:**
```promql
sum by (service) (container_memory_usage_bytes)
```

**Configuration:**
```yaml
Title: Memory Usage by Service
Pie chart type: Pie (or Donut)

Legend:
  Display mode: Table
  Placement: Right
  Values:
    - Value
    - Percent
```

### 4.8.2 Donut Chart

**Configuration:**
```yaml
Pie chart type: Donut
Donut width: 20% (hole size)
```

### 4.8.3 Legend Values

**Show calculations:**
```yaml
Legend values:
  - Value
  - Percent
  - Min
  - Max
  - Total
```

### 4.8.4 Tooltip

**Configuration:**
```yaml
Tooltip mode: Single
Tooltip value: Percent
```

### 4.8.5 Best Practices

**Limit slices:**
```yaml
# Use topk to show top 5
topk(5, sum by (category) (sales))
```

**Others category:**
Create "Others" for remaining values using transforms.

---

## 4.9 Heatmap Panel

Visualize data density over time.

### 4.9.1 Use Cases

- Request latency distribution
- Error frequency patterns
- Temperature variations
- Resource utilization patterns

### 4.9.2 Basic Heatmap

**Query (Prometheus histogram):**
```promql
sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
```

**Configuration:**
```yaml
Title: Request Latency Distribution

Y-axis:
  Unit: seconds (s)
  Scale: Linear
  Decimals: 2

Color:
  Scheme: Spectrum
  Mode: Opacity
```

### 4.9.3 Color Schemes

**Spectrum:**
```yaml
Color scheme: Spectrum (blue → green → yellow → red)
```

**Single color:**
```yaml
Color scheme: Single color (opacity based)
```

**Custom:**
```yaml
Color scheme: Custom
Steps:
  - 0: Blue
  - 0.5: Yellow
  - 1.0: Red
```

### 4.9.4 Data Bucketing

**Auto:**
```yaml
Bucket bound: Auto
Bucket size: Auto
```

**Manual:**
```yaml
Bucket bound: Upper
Bucket size: 0.1
```

### 4.9.5 Raw Data Format

**For non-histogram data:**
```yaml
Data format: Time series buckets
```

Transform data:
1. Group by time
2. Create buckets
3. Count values per bucket

---

## 4.10 Logs Panel

Display log streams from Loki or Elasticsearch.

### 4.10.1 Basic Logs

**Query (LogQL):**
```logql
{job="api", level="error"}
```

**Configuration:**
```yaml
Title: Application Errors
Show time: ✓
Show labels: ✓
Wrap lines: ✓
Prettify JSON: ✓
```

### 4.10.2 Log Level Coloring

**Automatic coloring:**
```yaml
Level colors:
  DEBUG: Blue
  INFO: Green
  WARNING: Yellow
  ERROR: Red
  CRITICAL: Purple
```

**Derived fields:**
```yaml
Derived fields:
  - Name: traceID
    Regex: traceID=(\w+)
    URL: /explore?...&trace=${__value.raw}
    Internal link: ✓
```

### 4.10.3 Log Volume

**Show histogram:**
```yaml
Show log volume: ✓
Volume query:
  sum by (level) (count_over_time({job="api"}[1m]))
```

### 4.10.4 Filtering

**In-panel filtering:**
```yaml
Enable filtering: ✓
```

Click on label to filter logs instantly!

---

## 4.11 State Timeline

Show state changes over time.

### 4.11.1 Configuration

**Query:**
```promql
up{job="api"}
```

**Configuration:**
```yaml
Title: Service Uptime
Value mappings:
  0 → Down (Red)
  1 → Up (Green)

Line width: 2
Fill opacity: 70
```

### 4.11.2 Multiple Services

**Query:**
```promql
up{job=~"api|worker|scheduler"}
```

**Result:** Timeline for each service showing up/down states

---

## 4.12 Geomap Panel

Display geographic data.

### 4.12.1 Basic Geomap

**Query (must return latitude/longitude):**
```sql
SELECT
  latitude,
  longitude,
  city_name,
  user_count
FROM user_locations
WHERE $__timeFilter(timestamp)
```

**Configuration:**
```yaml
Map view:
  Center: Auto (or specific coordinates)
  Zoom: Auto (or 1-22)
  
Base layer:
  - OpenStreetMap
  - CARTO Light/Dark
  - ArcGIS

Data layer:
  Type: Markers
  Size: Fixed (or by value)
  Color: By value
```

### 4.12.2 Marker Visualization

**Markers:**
```yaml
Type: Markers
Size field: user_count
Size range: 5-20

Color:
  Field: user_count
  Thresholds:
    0: Green
    100: Yellow
    500: Red
```

**Heatmap:**
```yaml
Type: Heatmap
Weight field: user_count
Opacity: 0.8
Radius: 15
```

**Route:**
```yaml
Type: Route
Style: Arrows
Line width: 2
```

---

## 4.13 Node Graph

Visualize service relationships and dependencies.

### 4.13.1 Data Format

**Nodes:**
```sql
SELECT 
  'node_' || id AS id,
  title,
  subtitle,
  arc__success AS success_rate
FROM services
```

**Edges:**
```sql
SELECT
  'edge_' || id AS id,
  source_id,
  target_id,
  mainstat AS request_rate,
  secondarystat AS error_rate
FROM service_connections
```

### 4.13.2 Configuration

```yaml
Title: Service Dependencies

Nodes:
  Main: Success rate
  Secondary: Response time
  Arc: Color by success rate

Edges:
  Main: Request rate
  Secondary: Error rate
  Color: By error rate
```

### 4.13.3 Layout

**Options:**
```yaml
Layout: Force-directed
Grid size: Auto
```

---

## 4.14 Custom Panels with Plugins

### 4.14.1 Installing Plugins

**Via Grafana CLI:**
```bash
grafana-cli plugins install <plugin-id>
```

**Docker:**
```yaml
environment:
  - GF_INSTALL_PLUGINS=<plugin-id>
```

### 4.14.2 Popular Visualization Plugins

**Clock Panel:**
```bash
grafana-cli plugins install grafana-clock-panel
```

**Worldmap Panel:**
```bash
grafana-cli plugins install grafana-worldmap-panel
```

**Plotly Panel:**
```bash
grafana-cli plugins install natel-plotly-panel
```

**Diagram Panel:**
```bash
grafana-cli plugins install jdbranham-diagram-panel
```

See plugin examples: [code/chapter04/03-plugins/](code/chapter04/03-plugins/)

---

## 4.15 Visualization Best Practices

### 4.15.1 Color Usage

**Semantic colors:**
```yaml
Green: Good, success, up
Yellow: Warning, degraded
Red: Error, critical, down
Blue: Informational, neutral
```

**Accessibility:**
- Use colorblind-friendly palettes
- Don't rely solely on color
- Add text/icons for states

### 4.15.2 Panel Sizing

**Dashboard grid:**
- 24 columns wide
- Height in grid units (30px each)

**Recommended sizes:**
```yaml
KPI stats: 4x4 (small)
Charts: 12x8 (medium)
Tables: 24x10 (full width)
Details: 6x6 (quarter)
```

### 4.15.3 Data Density

**Too sparse:**
- Wastes space
- Looks empty
- Hard to see trends

**Too dense:**
- Overwhelming
- Hard to read
- Slow performance

**Just right:**
- Clear trends
- Readable labels
- Fast loading

### 4.15.4 Performance

**Optimize queries:**
```promql
# ❌ Slow: Too many series
rate(http_requests_total[5m])

# ✅ Fast: Aggregated
sum by (status) (rate(http_requests_total[5m]))
```

**Limit time range:**
```yaml
Default: Last 6 hours (not Last 30 days)
```

**Use query caching:**
```yaml
Cache timeout: 60s (for relatively stable data)
```

---

## 4.16 Lab: Build Multi-Visualization Dashboard

### Objective
Create a comprehensive dashboard using all major visualization types.

### Requirements
- 1 Text panel (description)
- 4 Stat panels (KPIs)
- 1 Time series (trends)
- 1 Bar chart (comparison)
- 1 Pie chart (distribution)
- 1 Table (details)
- 1 Gauge (capacity)
- 1 Heatmap (distribution over time)

### Steps

**1. Create Dashboard**
```yaml
Name: Visualization Showcase
Tags: demo, visualizations
```

**2. Add Text Panel (Header)**
```markdown
# System Monitoring Dashboard

Real-time overview of system health and performance.

**Last updated:** $__from to $__to
```

**3. Row 1: KPIs (4 Stat Panels)**

Stat 1: Uptime
Stat 2: Total Requests
Stat 3: Error Rate
Stat 4: Avg Response Time

**4. Row 2: Trends**

Time Series: Request rate over time (multiple services)

**5. Row 3: Comparisons**

Left: Bar Chart - Requests by endpoint
Right: Pie Chart - Traffic by service

**6. Row 4: Details**

Full width: Table - Top 10 slowest requests

**7. Row 5: Advanced**

Left: Gauge - Disk usage
Right: Heatmap - Latency distribution

**Complete dashboard**: [code/chapter04/04-complete-dashboard/](code/chapter04/04-complete-dashboard/)

---

## 4.17 Summary

✅ **Time Series**: Trends over time  
✅ **Stat/Gauge/Bar Gauge**: Single/multiple values  
✅ **Table**: Detailed tabular data  
✅ **Bar Chart**: Categorical comparisons  
✅ **Pie Chart**: Proportions  
✅ **Heatmap**: Density visualization  
✅ **Logs**: Log streams  
✅ **State Timeline**: State changes  
✅ **Geomap**: Geographic data  
✅ **Node Graph**: Relationships  
✅ **Best Practices**: Color, sizing, performance  

**Next Chapter**: [Chapter 5: Query Languages](chapter05-query-languages.md)
