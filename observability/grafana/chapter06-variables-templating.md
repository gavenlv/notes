# Chapter 6: Variables and Templating

## 6.1 Introduction to Variables

Variables make dashboards interactive and reusable by allowing dynamic filtering and parameter substitution.

### 6.1.1 Benefits
- **Reusability**: One dashboard for all servers/environments
- **Interactivity**: Filter data without editing queries
- **Efficiency**: Reduce dashboard duplication
- **User-friendly**: Simple dropdown selection

---

## 6.2 Variable Types

### 6.2.1 Query Variable

Populate from data source query.

**Prometheus Example:**
```yaml
Name: server
Type: Query
Data source: Prometheus
Query: label_values(up, instance)
Regex: /(.+):.*/  # Extract before colon
Sort: Alphabetical
Multi-value: ✓
Include All option: ✓
```

**Usage in query:**
```promql
up{instance=~"$server"}
```

### 6.2.2 Custom Variable

Define static list of values.

```yaml
Name: environment
Type: Custom
Values: production,staging,development
```

**Usage:**
```promql
http_requests_total{env="$environment"}
```

### 6.2.3 Text Box Variable

User enters custom value.

```yaml
Name: threshold
Type: Text box
Default: 80
```

**Usage:**
```promql
cpu_usage > $threshold
```

### 6.2.4 Constant Variable

Hidden variable with fixed value.

```yaml
Name: datacenter
Type: Constant
Value: us-west-1
Hide: Variable
```

### 6.2.5 Data Source Variable

Select from available data sources.

```yaml
Name: datasource
Type: Data source
Type filter: Prometheus
Multi-value: ☐
Include All: ☐
```

**Usage:** Select data source in query dropdown

### 6.2.6 Interval Variable

Auto-calculated time interval.

```yaml
Name: interval
Type: Interval
Auto option: ✓
Values: 1m,5m,10m,30m,1h
```

**Usage:**
```promql
rate(http_requests_total[$interval])
```

### 6.2.7 Ad hoc Filters

Dynamic label filters (Prometheus/Loki).

```yaml
Name: filters
Type: Ad hoc filters
Data source: Prometheus
```

**Result:** User can add key=value filters on the fly!

---

## 6.3 Variable Configuration

### 6.3.1 Query Options

```yaml
# Refresh options
Refresh: On Dashboard Load
Refresh: On Time Range Change

# Sort
Sort: Disabled
Sort: Alphabetical (asc)
Sort: Alphabetical (desc)
Sort: Numerical (asc)
Sort: Numerical (desc)

# Multi-value
Multi-value: ✓ (allows selecting multiple values)

# Include All
Include All option: ✓
All value: .*  # Regex for all (or leave empty)
```

### 6.3.2 Chained Variables

Variables that depend on other variables.

**Example: Region → Datacenter → Server**

**Variable 1: region**
```yaml
Name: region
Type: Query
Query: label_values(node_uname_info, region)
```

**Variable 2: datacenter**
```yaml
Name: datacenter  
Type: Query
Query: label_values(node_uname_info{region="$region"}, datacenter)
```

**Variable 3: server**
```yaml
Name: server
Type: Query
Query: label_values(up{region="$region", datacenter="$datacenter"}, instance)
Multi-value: ✓
Include All: ✓
```

**Usage:**
```promql
up{region="$region", datacenter="$datacenter", instance=~"$server"}
```

### 6.3.3 Regular Expression Filtering

```yaml
Name: server
Query: label_values(up, instance)
Regex: /^prod-(.*)$/  # Only instances starting with "prod-"
```

**Common regex patterns:**
```regex
/^prod-/          # Starts with "prod-"
/-(prod|stg)-/    # Contains "-prod-" or "-stg-"
/(.+):\d+/        # Extract hostname before port
/([^\.]+)/        # First part before dot
```

---

## 6.4 Using Variables in Queries

### 6.4.1 Prometheus

**Single value:**
```promql
up{instance="$server"}
```

**Multi-value (regex):**
```promql
up{instance=~"$server"}
```

**In label value:**
```promql
node_cpu{instance=~"$server", cpu="$cpu"}
```

**In function:**
```promql
rate(http_requests_total{job="$job"}[$interval])
```

### 6.4.2 SQL

**String variable:**
```sql
WHERE server_name = '$server'
```

**Multi-value:**
```sql
WHERE server_name IN ($server:singlequote)
```

**Formatting options:**
- `$var` - as is: `value1,value2`
- `$var:singlequote` - quoted: `'value1','value2'`
- `$var:doublequote` - double quoted
- `$var:csv` - CSV format
- `$var:pipe` - pipe separated: `value1|value2`
- `$var:raw` - raw without escaping

**Example:**
```sql
SELECT *
FROM metrics
WHERE
  timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND server IN ($server:singlequote)
  AND metric_name = '$metric'
  AND value > $threshold
```

### 6.4.3 Flux (InfluxDB)

```flux
from(bucket: "$bucket")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r.host =~ /$server/)
  |> filter(fn: (r) => r._field == "$metric")
```

---

## 6.5 Global Variables

Grafana provides built-in variables:

### 6.5.1 Time Range Variables

```yaml
$__from          # Start of time range (epoch ms)
$__to            # End of time range (epoch ms)
$__interval      # Auto-calculated interval
$__interval_ms   # Interval in milliseconds
```

**Usage:**
```promql
rate(metric[$__interval])
```

```sql
WHERE timestamp >= $__timeFrom() AND timestamp < $__timeTo()
```

### 6.5.2 Dashboard Variables

```yaml
$__dashboard     # Dashboard name
$__user.id       # Current user ID
$__user.login    # Current username  
$__user.email    # Current user email
$__org.id        # Organization ID
$__org.name      # Organization name
```

**Usage in links:**
```
https://example.com/api?user=$__user.login&dashboard=$__dashboard
```

### 6.5.3 Data Variables

```yaml
$__series.name   # Series name
$__field.name    # Field name
$__value.raw     # Raw value
$__value.text    # Text representation
$__value.numeric # Numeric value
$__value.time    # Timestamp
```

**Usage in data links:**
```
/d/details?server=${__field.labels.instance}&time=$__value.time
```

---

## 6.6 Variable Display Options

### 6.6.1 Label

```yaml
Label: Environment
```

**Result:** Shows "Environment" instead of variable name

### 6.6.2 Hide Variable

```yaml
Hide: (empty) - Show in dashboard
Hide: Label - Hide label, show value
Hide: Variable - Completely hide
```

### 6.6.3 Preview of Values

```yaml
Preview of values: Shows current values
```

---

## 6.7 Advanced Variable Techniques

### 6.7.1 Repeating Panels

Create multiple panels from variable values.

**Example: CPU per Server**

**1. Create variable:**
```yaml
Name: server
Query: label_values(node_cpu_seconds_total, instance)
Multi-value: ✗  # Single value for repeat
```

**2. Create panel:**
```promql
rate(node_cpu_seconds_total{instance="$server"}[5m])
```

**3. Enable repeat:**
```yaml
Panel → Repeat options:
  Repeat by variable: server
  Repeat direction: Horizontal
  Max per row: 4
```

**Result:** One panel per server automatically!

### 6.7.2 Repeating Rows

```yaml
Row settings → Repeat for: $server
```

**Result:** Entire row duplicated per server

### 6.7.3 Conditional Display

Use variable in panel display condition:

```yaml
Panel → Overrides:
  Hide: $environment != "production"
```

### 6.7.4 Variable in Panel Title

```yaml
Title: CPU Usage - $server [$environment]
```

**Result:** "CPU Usage - web01 [production]"

### 6.7.5 Value Groups

Group values in dropdowns:

**Query:**
```promql
label_values(up{env=~"prod.*"}, instance)
```

**Regex:**
```
/^(?P<group>[^-]+)-.*/
```

**Result:** Grouped by prefix before first dash

---

## 6.8 Lab: Dynamic Multi-Environment Dashboard

### Objective
Create a single dashboard that works for all environments and servers using variables.

### Variables Setup

**1. Environment:**
```yaml
Name: env
Type: Custom
Values: production,staging,development
Default: production
```

**2. Region:**
```yaml
Name: region
Type: Query
Query: label_values(up{env="$env"}, region)
All option: ✓
```

**3. Server:**
```yaml
Name: server
Type: Query
Query: label_values(up{env="$env", region=~"$region"}, instance)
Multi-value: ✓
All option: ✓
```

**4. Metric:**
```yaml
Name: metric
Type: Custom
Values: cpu,memory,disk,network
Multi-value: ✓
```

**5. Interval:**
```yaml
Name: interval
Type: Interval
Auto: ✓
Values: 30s,1m,5m,10m,30m,1h
```

### Panel Configuration

**Panel 1: Resource Usage**
```promql
# Dynamic metric selection
avg by (instance) (
  node_${metric}_usage{env="$env", region=~"$region", instance=~"$server"}
)
```

**Panel 2: Request Rate**
```promql
sum by (instance) (
  rate(http_requests_total{env="$env", instance=~"$server"}[$interval])
)
```

**Panel 3: Detailed Table**
```sql
SELECT
  server_name,
  cpu_usage,
  memory_usage,
  disk_usage
FROM server_metrics
WHERE
  environment = '$env'
  AND region IN ($region:singlequote)
  AND server_name IN ($server:singlequote)
  AND $__timeFilter(timestamp)
```

See complete example: [code/chapter06/dynamic-dashboard/](code/chapter06/dynamic-dashboard/)

---

## 6.9 Summary

✅ **Variable types**: Query, Custom, Text, Constant, Interval  
✅ **Chained variables**: Dependent dropdowns  
✅ **Multi-value**: Select multiple values  
✅ **Repeating**: Auto-generate panels  
✅ **Global variables**: Built-in time and user variables  
✅ **Advanced techniques**: Grouping, filtering, conditional display  

**Next Chapter**: [Chapter 7: Alerting System](chapter07-alerting-system.md)
