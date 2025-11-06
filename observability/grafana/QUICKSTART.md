# Grafana Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start Grafana with Docker

```bash
cd observability/grafana/code/chapter01/01-docker-basic
docker-compose up -d
```

### Step 2: Access Grafana

Open your browser: **http://localhost:3000**

**Login credentials:**
- Username: `admin`
- Password: `admin123`

### Step 3: Explore the Interface

You should see:
- ✅ Grafana welcome screen
- ✅ Left sidebar with navigation
- ✅ Home dashboard

### Step 4: Add Your First Data Source

1. Click **⚙️ Configuration** → **Data sources**
2. Click **Add data source**
3. Select **TestData DB**
4. Click **Save & test**

### Step 5: Create Your First Dashboard

1. Click **+ icon** → **Dashboard**
2. Click **Add new panel**
3. In query editor:
   - Data source: **TestData DB**
   - Scenario: **Random Walk**
4. Click **Apply**
5. Click **💾 Save dashboard**
   - Name: "My First Dashboard"
   - Click **Save**

🎉 **Congratulations!** You've created your first Grafana dashboard!

---

## 📚 What's Next?

### For Complete Beginners

Follow the chapters in order:

1. **[Chapter 1: Installation](chapter01-installation-setup.md)** (2-3 hours)
   - Complete installation guide
   - Multiple installation methods
   - First dashboard walkthrough

2. **[Chapter 2: Fundamentals](chapter02-fundamentals.md)** (4-5 hours)
   - Interface navigation
   - Data sources
   - Dashboard basics

3. **Continue with Chapters 3-12** as you progress

### For Experienced Users

Jump to specific topics:

- **DevOps/SRE**: Chapters 7 (Alerting), 10 (Performance), 12 (Projects)
- **Developers**: Chapters 3 (Data Sources), 5 (Query Languages), 8 (API)
- **Data Analysts**: Chapters 4 (Visualizations), 6 (Variables)

---

## 🛠️ Full Monitoring Stack

Want to set up a complete monitoring stack with Prometheus, Loki, and more?

```bash
cd observability/grafana/code/chapter01/02-docker-compose
docker-compose up -d
```

**Access:**
- Grafana: http://localhost:3000 (admin/admin123)
- Prometheus: http://localhost:9090
- Node Exporter: http://localhost:9100/metrics

**Pre-configured:**
- ✅ Prometheus data source auto-configured
- ✅ Node Exporter collecting system metrics
- ✅ cAdvisor collecting container metrics

---

## 📖 Learning Path

### Beginner Track (40-50 hours)

**Week 1-2:** Foundation
- Chapter 1: Installation
- Chapter 2: Fundamentals

**Week 3-4:** Data & Visualization
- Chapter 3: Data Sources
- Chapter 4: Visualizations

**Week 5-6:** Advanced Queries
- Chapter 5: Query Languages
- Chapter 6: Variables

**Week 7-8:** Production Features
- Chapter 7: Alerting
- Chapter 8: Advanced Features

**Week 9-10:** Security & Performance
- Chapter 9: Security
- Chapter 10: Performance

**Week 11-12:** Real-world
- Chapter 11: Enterprise
- Chapter 12: Projects

### Fast Track (1-2 weeks intensive)

**Day 1-2:** Chapters 1-2 (Basics)
**Day 3-4:** Chapters 3-4 (Data & Viz)
**Day 5-6:** Chapters 5-6 (Queries & Variables)
**Day 7-8:** Chapters 7-8 (Alerting & Advanced)
**Day 9-10:** Chapters 9-10 (Security & Performance)
**Day 11-14:** Chapters 11-12 (Enterprise & Projects)

---

## 💡 Study Tips

### 1. Hands-on is Key
- Don't just read, execute every example
- Modify code and see what happens
- Break things and fix them

### 2. Build As You Learn
- Create dashboards for your own use cases
- Monitor your personal projects
- Share with the community

### 3. Use the Code Examples
All examples are in the `code/` directory:
```
code/
├── chapter01/  # Basic setup examples
├── chapter02/  # Dashboard templates
├── chapter03/  # Data source configs
└── ... more
```

### 4. Join the Community
- [Grafana Community Forums](https://community.grafana.com/)
- [Discord](https://discord.gg/grafana)
- Share your dashboards at [grafana.com/dashboards](https://grafana.com/grafana/dashboards/)

---

## 🔧 Troubleshooting

### Port 3000 Already in Use?

**Linux/Mac:**
```bash
sudo lsof -i :3000
sudo kill -9 <PID>
```

**Windows:**
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Or change port:**
Edit `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Use port 3001 instead
```

### Can't Access Grafana?

1. Check if container is running:
   ```bash
   docker ps | grep grafana
   ```

2. Check logs:
   ```bash
   docker logs grafana
   ```

3. Verify network:
   ```bash
   docker network ls
   ```

### Forgot Admin Password?

```bash
docker exec -it grafana grafana-cli admin reset-admin-password newpassword
```

---

## 📊 Sample Dashboards

Try these queries in your first dashboard:

### CPU Usage (with Prometheus)
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Memory Usage (with Prometheus)
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

### Random Data (with TestData)
```
Data source: TestData DB
Scenario: Random Walk
```

---

## 🎯 Your First Real Dashboard

Create a system monitoring dashboard:

1. **Row 1: KPIs** (4 Stat panels)
   - Uptime
   - CPU Usage
   - Memory Usage
   - Disk Usage

2. **Row 2: Trends** (2 Time series)
   - CPU over time
   - Memory over time

3. **Row 3: Details** (1 Table)
   - Process list
   - Resource consumption

**Complete example:** `code/chapter02/05-complete-dashboard/`

---

## 📚 Quick Reference

### Useful Grafana URLs

| URL | Purpose |
|-----|---------|
| `/dashboards` | Browse dashboards |
| `/explore` | Ad-hoc queries |
| `/alerting` | Alert management |
| `/datasources` | Data source config |
| `/plugins` | Plugin management |
| `/admin` | Server admin (admin only) |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` / `Cmd+K` | Search |
| `Ctrl+S` / `Cmd+S` | Save dashboard |
| `e` | Edit panel |
| `v` | View panel |
| `Esc` | Close panel |

### Common PromQL Patterns

```promql
# Rate of increase
rate(metric[5m])

# Average
avg(metric)

# Sum by label
sum by (label) (metric)

# Percentage
(metric_a / metric_b) * 100

# Threshold
metric > 80
```

---

## 🎓 Next Steps

**After completing the Quick Start:**

1. ✅ Complete Chapter 1 for thorough understanding
2. ✅ Set up monitoring for your own application
3. ✅ Create 3-5 custom dashboards
4. ✅ Configure alerting for critical metrics
5. ✅ Share your dashboards with the community

---

## 📞 Need Help?

**Documentation Issues:**
- Re-read the relevant chapter
- Check code examples in `code/` directory
- Review troubleshooting sections

**Technical Problems:**
- Search [Grafana Community Forums](https://community.grafana.com/)
- Check [GitHub Issues](https://github.com/grafana/grafana/issues)
- Review [Official Docs](https://grafana.com/docs/)

**Still Stuck?**
- Post on community forums with:
  - Grafana version
  - Docker/system info
  - Error messages
  - Steps to reproduce

---

**Happy Monitoring! 📊📈**

**Start Learning:** [Chapter 1: Installation and Environment Setup](chapter01-installation-setup.md)
