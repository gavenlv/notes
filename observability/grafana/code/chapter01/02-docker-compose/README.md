# Grafana + Prometheus + Node Exporter Stack

Complete monitoring stack with Grafana, Prometheus, and Node Exporter.

## Architecture

```
┌─────────────┐
│   Grafana   │ :3000 (Visualization)
└──────┬──────┘
       │
       │ queries
       ▼
┌─────────────┐
│ Prometheus  │ :9090 (Metrics Storage)
└──────┬──────┘
       │
       │ scrapes
       ▼
┌─────────────┐
│Node Exporter│ :9100 (System Metrics)
└─────────────┘
```

## What's Included

1. **Grafana** (Port 3000)
   - Admin user: `admin`
   - Password: `admin123`
   - Auto-configured with Prometheus datasource

2. **Prometheus** (Port 9090)
   - Scrapes metrics every 15 seconds
   - Stores data for 15 days
   - Monitors: itself, Node Exporter, Grafana

3. **Node Exporter** (Port 9100)
   - Exports system metrics (CPU, memory, disk, network)

## Quick Start

### 1. Start All Services

```bash
docker-compose up -d
```

### 2. Verify Services

```bash
# Check running containers
docker-compose ps

# Should show:
# - grafana (3000)
# - prometheus (9090)
# - node-exporter (9100)
```

### 3. Access Services

- **Grafana**: http://localhost:3000
  - Login: admin / admin123
  
- **Prometheus**: http://localhost:9090
  - Check targets: http://localhost:9090/targets
  
- **Node Exporter**: http://localhost:9100/metrics
  - Raw metrics endpoint

### 4. Verify Prometheus Data Source

In Grafana:
1. Go to Configuration → Data Sources
2. You should see "Prometheus" already configured
3. Click "Test" button - should show "Data source is working"

## Creating Your First Dashboard

### Method 1: Manual Creation

1. In Grafana, click **+ → Dashboard**
2. Click **Add new panel**
3. In the query editor:
   ```promql
   rate(node_cpu_seconds_total{mode="system"}[5m])
   ```
4. Title: "CPU Usage"
5. Click **Apply**
6. Click **Save dashboard**

### Method 2: Use Sample Queries

**CPU Usage by Mode:**
```promql
rate(node_cpu_seconds_total[5m])
```

**Memory Usage Percentage:**
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Disk I/O Rate:**
```promql
rate(node_disk_read_bytes_total[5m])
```

**Network Traffic:**
```promql
rate(node_network_receive_bytes_total[5m])
```

## Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f grafana
docker-compose logs -f prometheus
docker-compose logs -f node-exporter
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart grafana
```

### Stop Services

```bash
# Stop but keep data
docker-compose down

# Stop and remove volumes (delete all data)
docker-compose down -v
```

### Check Prometheus Targets

```bash
curl http://localhost:9090/api/v1/targets | jq
```

### Execute Commands Inside Containers

```bash
# Grafana
docker-compose exec grafana bash

# Prometheus
docker-compose exec prometheus sh

# Node Exporter
docker-compose exec node-exporter sh
```

## Directory Structure

```
02-docker-compose/
├── docker-compose.yml              # Main compose file
├── prometheus/
│   └── prometheus.yml              # Prometheus configuration
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml      # Auto-configure Prometheus datasource
│       └── dashboards/
│           └── (dashboard files)   # Auto-load dashboards
└── README.md                       # This file
```

## Provisioning Explained

### Data Sources Provisioning

The file `grafana/provisioning/datasources/prometheus.yml` automatically:
- Adds Prometheus as a data source
- Sets it as the default
- Configures the correct URL
- No manual setup needed!

### How It Works

When Grafana starts, it reads files from `/etc/grafana/provisioning/` and:
1. Creates data sources from `datasources/*.yml`
2. Imports dashboards from `dashboards/*.yml`

This is perfect for:
- Reproducible setups
- Version control
- Automated deployments
- Team collaboration

## Troubleshooting

### Prometheus Can't Scrape Targets

**Check Docker networks:**
```bash
docker network ls
docker network inspect 02-docker-compose_monitoring
```

All containers should be on the same network.

### Grafana Can't Connect to Prometheus

**Verify URL:**
- Use container name: `http://prometheus:9090` ✅
- NOT localhost: `http://localhost:9090` ❌

**Test from Grafana container:**
```bash
docker-compose exec grafana wget -O- http://prometheus:9090/api/v1/status/config
```

### Node Exporter Shows No Data

**On Linux**, Node Exporter needs access to host system:
```yaml
volumes:
  - /proc:/host/proc:ro
  - /sys:/host/sys:ro
  - /:/rootfs:ro
```

**On Windows/Mac**, some metrics won't be available (Docker Desktop limitation).

### Port Already in Use

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Grafana on 3001
  - "9091:9090"  # Prometheus on 9091
```

## Next Steps

1. **Import a Dashboard**
   - Go to https://grafana.com/grafana/dashboards/
   - Search for "Node Exporter Full"
   - Copy dashboard ID: 1860
   - In Grafana: + → Import → Enter ID → Load

2. **Create Alerts**
   - Create alert rules for CPU/memory thresholds
   - Configure notification channels (email, Slack, etc.)

3. **Add More Exporters**
   - MySQL Exporter for database metrics
   - Redis Exporter for cache metrics
   - Custom application metrics

## References

- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Node Exporter Metrics](https://github.com/prometheus/node_exporter)
