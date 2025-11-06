# Chapter 1: Grafana Installation and Environment Setup

## 1.1 What is Grafana?

### 1.1.1 Introduction
Grafana is an open-source platform for monitoring and observability. It allows you to query, visualize, alert on, and understand your metrics no matter where they are stored.

**Key Features:**
- **Multi-datasource support**: Connect to Prometheus, InfluxDB, MySQL, PostgreSQL, Elasticsearch, and 100+ other data sources
- **Beautiful visualizations**: Create interactive and dynamic dashboards
- **Alerting**: Set up alerts and receive notifications
- **Plugin ecosystem**: Extend functionality with community and enterprise plugins
- **Open source**: Free and community-driven

### 1.1.2 Core Concepts

#### Dashboard
A dashboard is a set of one or more panels organized and arranged into one or more rows. It's the main view where you visualize your data.

#### Panel
A panel is a single visualization element (graph, table, stat, etc.) that displays data from a data source.

#### Data Source
A data source is the backend system that stores your metrics, logs, or traces (e.g., Prometheus, MySQL, InfluxDB).

#### Query
A query retrieves data from a data source. Each panel contains one or more queries.

#### Time Range
The time period for which data is displayed. Can be absolute or relative (e.g., "Last 6 hours").

---

## 1.2 System Requirements

### 1.2.1 Minimum Requirements
- **CPU**: 1 core
- **Memory**: 512 MB RAM
- **Storage**: 1 GB disk space
- **Network**: Internet connection for downloading Grafana

### 1.2.2 Recommended Requirements
- **CPU**: 2+ cores
- **Memory**: 2 GB+ RAM
- **Storage**: 10 GB+ disk space
- **Operating System**: 
  - Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
  - Windows 10/11 or Server 2016+
  - macOS 10.14+

### 1.2.3 Supported Databases (for Grafana metadata)
- SQLite (default, no installation needed)
- MySQL 5.7+
- PostgreSQL 10+

---

## 1.3 Installation Methods

### 1.3.1 Docker Installation (Recommended for Beginners)

Docker is the easiest way to get started with Grafana. It requires no system dependencies and can be removed cleanly.

#### Prerequisites
- Docker installed on your system
- Basic understanding of command line

#### Installation Steps

**Step 1: Pull the Grafana Docker Image**
```bash
docker pull grafana/grafana:latest
```

**Step 2: Run Grafana Container**
```bash
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana:latest
```

**Explanation:**
- `-d`: Run in detached mode (background)
- `--name=grafana`: Name the container "grafana"
- `-p 3000:3000`: Map port 3000 from container to host
- `-v grafana-storage:/var/lib/grafana`: Create a persistent volume for data
- `grafana/grafana:latest`: Use the latest Grafana image

**Step 3: Verify Installation**
```bash
docker ps | grep grafana
```

**Step 4: Access Grafana**
- Open browser: http://localhost:3000
- Default credentials:
  - **Username**: admin
  - **Password**: admin
  - You'll be prompted to change the password on first login

See practical example: [code/chapter01/01-docker-basic/docker-compose.yml](code/chapter01/01-docker-basic/docker-compose.yml)

---

### 1.3.2 Docker Compose Installation (Production-like)

Docker Compose allows you to define multi-container applications. We'll set up Grafana with Prometheus as a data source.

**File: docker-compose.yml**
```yaml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-storage:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  grafana-storage:
  prometheus-storage:

networks:
  monitoring:
    driver: bridge
```

**Start the stack:**
```bash
docker-compose up -d
```

See complete example: [code/chapter01/02-docker-compose/](code/chapter01/02-docker-compose/)

---

### 1.3.3 Linux Installation (Ubuntu/Debian)

#### Method 1: APT Repository (Recommended)

**Step 1: Add Grafana GPG Key**
```bash
sudo apt-get install -y apt-transport-https software-properties-common wget
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
```

**Step 2: Add Grafana Repository**
```bash
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
```

**Step 3: Update and Install**
```bash
sudo apt-get update
sudo apt-get install grafana
```

**Step 4: Start Grafana Service**
```bash
# Start Grafana
sudo systemctl start grafana-server

# Enable auto-start on boot
sudo systemctl enable grafana-server

# Check status
sudo systemctl status grafana-server
```

**Step 5: Configure Firewall (if needed)**
```bash
sudo ufw allow 3000/tcp
```

#### Method 2: Download DEB Package

```bash
# Download latest version
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_10.2.0_amd64.deb

# Install
sudo dpkg -i grafana-enterprise_10.2.0_amd64.deb

# Start service
sudo systemctl start grafana-server
```

---

### 1.3.4 Windows Installation

#### Method 1: Windows Installer (Easiest)

**Step 1: Download Installer**
- Visit: https://grafana.com/grafana/download
- Download Windows installer (.msi file)

**Step 2: Run Installer**
- Double-click the .msi file
- Follow installation wizard
- Choose installation directory (default: C:\Program Files\GrafanaLabs\grafana)

**Step 3: Start Grafana**
- Grafana runs as a Windows service automatically
- Or run manually: `C:\Program Files\GrafanaLabs\grafana\bin\grafana-server.exe`

**Step 4: Access Grafana**
- Browser: http://localhost:3000

#### Method 2: Standalone Binary

**Step 1: Download ZIP**
```powershell
# Download from https://dl.grafana.com/enterprise/release/grafana-10.2.0.windows-amd64.zip
```

**Step 2: Extract and Run**
```powershell
# Extract to desired location
Expand-Archive -Path grafana-10.2.0.windows-amd64.zip -DestinationPath C:\grafana

# Navigate to bin directory
cd C:\grafana\grafana-10.2.0\bin

# Run Grafana
.\grafana-server.exe
```

See Windows setup script: [code/chapter01/03-windows-setup/install.ps1](code/chapter01/03-windows-setup/install.ps1)

---

### 1.3.5 macOS Installation

#### Method 1: Homebrew (Recommended)

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Grafana
brew install grafana

# Start Grafana service
brew services start grafana

# Or run in foreground
grafana-server --config=/usr/local/etc/grafana/grafana.ini --homepath=/usr/local/share/grafana
```

#### Method 2: Download Binary

```bash
# Download
curl -O https://dl.grafana.com/enterprise/release/grafana-10.2.0.darwin-amd64.tar.gz

# Extract
tar -zxvf grafana-10.2.0.darwin-amd64.tar.gz

# Run
cd grafana-10.2.0
./bin/grafana-server
```

---

## 1.4 Initial Configuration

### 1.4.1 Configuration File Location

The main configuration file is `grafana.ini`:

- **Linux**: `/etc/grafana/grafana.ini`
- **Docker**: `/etc/grafana/grafana.ini` (inside container)
- **Windows**: `C:\Program Files\GrafanaLabs\grafana\conf\grafana.ini`
- **macOS**: `/usr/local/etc/grafana/grafana.ini`

### 1.4.2 Important Configuration Options

#### Server Settings
```ini
[server]
# Protocol (http, https, h2, socket)
protocol = http

# The IP address to bind to (0.0.0.0 = all interfaces)
http_addr = 0.0.0.0

# The http port to use
http_port = 3000

# The public facing domain name
domain = localhost

# The full public facing url
root_url = %(protocol)s://%(domain)s:%(http_port)s/
```

#### Security Settings
```ini
[security]
# Default admin user
admin_user = admin

# Default admin password
admin_password = admin

# Secret key for signing (change in production!)
secret_key = SW2YcwTIb9zpOOhoPsMm

# Disable creation of admin user on first start
disable_initial_admin_creation = false
```

#### Database Settings
```ini
[database]
# Database type (sqlite3, mysql, postgres)
type = sqlite3

# For sqlite3, the database path
path = grafana.db

# For MySQL/PostgreSQL
;host = 127.0.0.1:3306
;name = grafana
;user = root
;password = 
```

#### User Settings
```ini
[users]
# Disable user signup / registration
allow_sign_up = false

# Allow users to create organizations
allow_org_create = false

# Default role for new users
auto_assign_org_role = Viewer
```

### 1.4.3 Environment Variables

You can override configuration with environment variables:

```bash
# Format: GF_<SECTION>_<KEY>
export GF_SERVER_HTTP_PORT=3000
export GF_SECURITY_ADMIN_PASSWORD=secure_password
export GF_DATABASE_TYPE=postgres
export GF_DATABASE_HOST=postgres:5432
```

**Docker Example:**
```bash
docker run -d \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=secret" \
  -e "GF_USERS_ALLOW_SIGN_UP=false" \
  grafana/grafana:latest
```

---

## 1.5 First Login and Setup

### 1.5.1 Access Grafana Web Interface

1. **Open Browser**: Navigate to http://localhost:3000
2. **Login Screen**: You'll see the Grafana login page
3. **Default Credentials**:
   - Username: `admin`
   - Password: `admin` (or what you configured)

### 1.5.2 Change Default Password

**Important**: Always change the default password on first login!

1. After login, you'll be prompted to change password
2. Enter new password (minimum 4 characters)
3. Click "Save"

### 1.5.3 Explore the Interface

**Main Navigation (Left Sidebar):**
- **Home**: Homepage with search and recent dashboards
- **Dashboards**: Browse and manage dashboards
- **Explore**: Query data sources ad-hoc
- **Alerting**: Manage alert rules and notifications
- **Configuration**: Data sources, plugins, users, teams
- **Server Admin**: System settings (admin only)

### 1.5.4 Configure Your First Data Source

We'll add a TestData data source (built-in, no setup needed):

**Step 1: Navigate to Data Sources**
1. Click on ⚙️ Configuration (gear icon) in left sidebar
2. Click on "Data sources"
3. Click "Add data source"

**Step 2: Select TestData DB**
1. Search for "TestData"
2. Click on "TestData DB"
3. Click "Save & Test"

**What is TestData?**
TestData is a built-in data source that generates random data. Perfect for learning Grafana without setting up external databases.

See screenshot guide: [code/chapter01/04-first-setup/screenshots/](code/chapter01/04-first-setup/screenshots/)

---

## 1.6 Create Your First Dashboard

Let's create a simple dashboard to visualize data from TestData.

### 1.6.1 Create New Dashboard

1. Click on **+ icon** in left sidebar
2. Select "Dashboard"
3. Click "Add new panel"

### 1.6.2 Configure Your First Panel

**Step 1: Select Data Source**
- In the query editor, select "TestData DB" as data source

**Step 2: Choose Scenario**
- Scenario: Select "Random Walk"
- Series count: 1
- This generates a random time series

**Step 3: Configure Visualization**
- Panel type: Time series (default)
- Title: "My First Panel"

**Step 4: Customize Panel**
- In the right panel settings:
  - Panel options → Title: "Random Walk Data"
  - Graph styles → Line width: 2
  - Legend → Visibility: Show
  
**Step 5: Apply**
- Click "Apply" button in top-right corner

### 1.6.3 Save Dashboard

1. Click **💾 Save dashboard** icon (top-right)
2. Dashboard name: "My First Dashboard"
3. Folder: "General"
4. Click "Save"

**Congratulations!** You've created your first Grafana dashboard! 🎉

See complete example: [code/chapter01/05-first-dashboard/](code/chapter01/05-first-dashboard/)

---

## 1.7 Understanding the Dashboard Interface

### 1.7.1 Top Navigation Bar

- **Dashboard name**: Click to edit dashboard settings
- **Star icon**: Mark dashboard as favorite
- **Share**: Share dashboard via link or snapshot
- **Save**: Save dashboard changes
- **Settings**: Dashboard settings and JSON model
- **Add panel**: Add new visualization panel

### 1.7.2 Time Range Picker

Located in top-right corner:
- **Quick ranges**: Last 5m, 15m, 1h, 6h, 24h, 7d, 30d, 90d
- **Absolute ranges**: Specify exact start and end times
- **Refresh interval**: Auto-refresh dashboard (5s, 10s, 30s, 1m, etc.)
- **Zoom**: Use time picker or drag on graph to zoom

**Examples:**
```
Last 6 hours     → now-6h to now
Yesterday        → now-1d/d to now-1d/d
This month       → now/M to now/M
Custom range     → 2024-01-01 00:00:00 to 2024-01-31 23:59:59
```

### 1.7.3 Panel Menu

Click on panel title to access:
- **View**: Full-screen panel view
- **Edit**: Edit panel configuration
- **Share**: Share or embed panel
- **Explore**: Query data in Explore view
- **Inspect**: View raw data and query
- **More**: Duplicate, copy, remove panel

---

## 1.8 Hands-on Lab: Complete Setup

Let's put everything together in a practical lab.

### Lab Objective
Set up a complete Grafana environment with Docker Compose, including:
- Grafana
- Prometheus (metrics data source)
- Node Exporter (system metrics)
- Create a system monitoring dashboard

### Lab Steps

**Step 1: Create Project Directory**
```bash
mkdir -p grafana-lab
cd grafana-lab
mkdir -p prometheus grafana/provisioning/datasources grafana/provisioning/dashboards
```

**Step 2: Create Prometheus Configuration**

File: `prometheus/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

**Step 3: Create Grafana Datasource Provisioning**

File: `grafana/provisioning/datasources/prometheus.yml`
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

**Step 4: Create Docker Compose File**

File: `docker-compose.yml`
```yaml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring
    depends_on:
      - prometheus

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-storage:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    networks:
      - monitoring

volumes:
  grafana-storage:
  prometheus-storage:

networks:
  monitoring:
    driver: bridge
```

**Step 5: Start the Stack**
```bash
docker-compose up -d
```

**Step 6: Verify Services**
```bash
# Check running containers
docker-compose ps

# Check Grafana logs
docker-compose logs grafana

# Check Prometheus logs
docker-compose logs prometheus
```

**Step 7: Access Services**
- Grafana: http://localhost:3000 (admin/admin123)
- Prometheus: http://localhost:9090
- Node Exporter: http://localhost:9100/metrics

**Step 8: Create System Metrics Dashboard**

1. Login to Grafana
2. Create new dashboard
3. Add panel with query:
   ```promql
   rate(node_cpu_seconds_total{mode="system"}[5m])
   ```
4. Title: "CPU System Usage"
5. Add another panel:
   ```promql
   node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100
   ```
6. Title: "Memory Available %"
7. Save dashboard as "System Monitoring"

**Complete lab code**: [code/chapter01/06-complete-lab/](code/chapter01/06-complete-lab/)

---

## 1.9 Troubleshooting Common Issues

### Issue 1: Port 3000 Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using port 3000
# Linux/Mac:
sudo lsof -i :3000
sudo kill -9 <PID>

# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
docker run -p 3001:3000 grafana/grafana
```

### Issue 2: Cannot Connect to Data Source

**Error:**
```
HTTP Error Bad Gateway
```

**Checklist:**
1. Verify data source URL is correct
2. Check network connectivity
3. Ensure data source service is running
4. Check firewall rules
5. Review Grafana logs

**Docker-specific:**
```bash
# Use container name, not localhost
url: http://prometheus:9090  # ✅ Correct
url: http://localhost:9090   # ❌ Wrong in Docker
```

### Issue 3: Dashboard Not Saving

**Possible Causes:**
1. Insufficient permissions
2. Disk space full
3. Database connection issue

**Solution:**
```bash
# Check Grafana logs
docker logs grafana

# Check disk space
df -h

# Verify database
docker exec -it grafana sqlite3 /var/lib/grafana/grafana.db ".tables"
```

### Issue 4: Forgot Admin Password

**Solution - Docker:**
```bash
# Reset admin password
docker exec -it grafana grafana-cli admin reset-admin-password newpassword
```

**Solution - Linux:**
```bash
sudo grafana-cli admin reset-admin-password newpassword
sudo systemctl restart grafana-server
```

---

## 1.10 Best Practices

### 1.10.1 Security

1. **Change default credentials immediately**
2. **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
3. **Enable HTTPS** in production
4. **Restrict network access** (firewall, VPN)
5. **Regularly update** Grafana to latest version
6. **Use environment variables** for secrets (not config files)
7. **Enable audit logging** for compliance

### 1.10.2 Performance

1. **Use persistent storage** for Docker volumes
2. **Configure retention policies** for data sources
3. **Limit query time ranges** to prevent overload
4. **Use caching** for frequently accessed dashboards
5. **Monitor Grafana itself** (CPU, memory, disk)

### 1.10.3 Organization

1. **Use folders** to organize dashboards
2. **Naming conventions**: 
   - Dashboards: `[Team] - [Purpose] - [Environment]`
   - Example: `DevOps - System Metrics - Production`
3. **Tag dashboards** for easy search
4. **Document dashboards** with text panels
5. **Version control** dashboard JSON files

---

## 1.11 Summary

In this chapter, you learned:

✅ **What Grafana is** and its core concepts  
✅ **System requirements** for running Grafana  
✅ **Multiple installation methods**: Docker, Linux, Windows, macOS  
✅ **Initial configuration** and important settings  
✅ **First login** and interface navigation  
✅ **Creating your first dashboard** with TestData  
✅ **Hands-on lab** with complete monitoring stack  
✅ **Troubleshooting** common issues  
✅ **Best practices** for security and organization  

### What's Next?

In **Chapter 2**, we'll dive deeper into:
- Grafana UI navigation and features
- Understanding data sources in detail
- Panel types and visualization options
- Dashboard management and sharing
- User and permission management

---

## 1.12 Practice Exercises

### Exercise 1: Basic Setup
1. Install Grafana using Docker
2. Change the default admin password
3. Configure Grafana to run on port 3001
4. Access Grafana UI and explore the interface

### Exercise 2: TestData Dashboard
1. Add TestData data source
2. Create a dashboard with 4 panels:
   - Random Walk (time series)
   - CSV Content (table)
   - Logs (logs panel)
   - Flame Graph (flame graph)
3. Save and share the dashboard

### Exercise 3: Complete Stack
1. Set up Docker Compose with Grafana + Prometheus
2. Configure auto-provisioning for Prometheus data source
3. Create a dashboard querying Prometheus metrics
4. Set up auto-refresh every 30 seconds

### Exercise 4: Configuration
1. Modify `grafana.ini` to change:
   - Server port to 3001
   - Disable user signup
   - Change organization name
2. Restart Grafana and verify changes
3. Use environment variables instead of config file

**Solutions**: [code/chapter01/07-exercises/](code/chapter01/07-exercises/)

---

## 1.13 Additional Resources

### Official Documentation
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Installation Guide](https://grafana.com/docs/grafana/latest/setup-grafana/installation/)
- [Configuration](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/)

### Community Resources
- [Grafana Community Forums](https://community.grafana.com/)
- [Grafana GitHub](https://github.com/grafana/grafana)
- [Grafana Play (Demo)](https://play.grafana.org/)

### Video Tutorials
- [Grafana Beginner Tutorial](https://grafana.com/tutorials/)
- [Official YouTube Channel](https://www.youtube.com/c/Grafana)

### Practice Environments
- [Grafana Play](https://play.grafana.org/) - Free online Grafana instance
- [Killercoda Grafana Scenarios](https://killercoda.com/grafana)

---

**Next Chapter**: [Chapter 2: Grafana Fundamentals](chapter02-fundamentals.md)
