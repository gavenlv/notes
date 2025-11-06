# Grafana: From Zero to Expert (0基础到专家)

## 📚 Complete Grafana Learning Guide

A comprehensive, hands-on tutorial series that takes you from absolute beginner to Grafana expert. Every concept is explained in depth with practical examples and working code.

**适合人群 (Suitable for):**
- 0基础初学者 (Complete beginners)
- 运维工程师 (Operations engineers)
- SRE团队 (Site Reliability Engineers)
- 开发人员 (Developers)
- 数据分析师 (Data analysts)

---

## 🎯 Learning Path

```
Chapter 1-2: Fundamentals (入门基础)
    ↓
Chapter 3-5: Data & Queries (数据与查询)
    ↓
Chapter 6-8: Advanced Features (高级特性)
    ↓
Chapter 9-11: Production Ready (生产就绪)
    ↓
Chapter 12: Real-world Projects (实战项目)
```

---

## 📖 Table of Contents

### [Chapter 1: Installation and Environment Setup](chapter01-installation-setup.md)
**安装与环境配置**

Learn how to install and configure Grafana in various environments.

**Topics covered:**
- ✅ What is Grafana and its core concepts
- ✅ System requirements
- ✅ Installation methods (Docker, Linux, Windows, macOS)
- ✅ Initial configuration
- ✅ First login and setup
- ✅ Creating your first dashboard
- ✅ Hands-on lab with complete monitoring stack
- ✅ Troubleshooting common issues

**Code examples:** [`code/chapter01/`](code/chapter01/)

**Time to complete:** 2-3 hours

---

### [Chapter 2: Grafana Fundamentals](chapter02-fundamentals.md)
**Grafana 基础知识**

Master the Grafana interface and basic operations.

**Topics covered:**
- ✅ Understanding the Grafana interface
- ✅ Working with data sources (Prometheus, MySQL, TestData)
- ✅ Dashboard basics and management
- ✅ Panel types and configurations
- ✅ Query editor fundamentals
- ✅ Time range and refresh settings
- ✅ Sharing and collaboration
- ✅ Organizing dashboards (folders, tags, permissions)
- ✅ Best practices for dashboard design

**Code examples:** [`code/chapter02/`](code/chapter02/)

**Time to complete:** 4-5 hours

---

### [Chapter 3: Data Sources Deep Dive](chapter03-datasources-deep-dive.md)
**深入数据源**

Comprehensive guide to all major data source types.

**Topics covered:**
- ✅ **Prometheus**: Installation, configuration, PromQL basics
- ✅ **InfluxDB**: Setup, Flux query language
- ✅ **MySQL/PostgreSQL**: SQL queries for time series
- ✅ **Loki**: Log aggregation and LogQL
- ✅ Recording rules and query optimization
- ✅ Multiple data source integration

**Code examples:** [`code/chapter03/`](code/chapter03/)

**Time to complete:** 6-8 hours

---

### [Chapter 4: Visualization Mastery](chapter04-visualization-mastery.md)
**可视化大师**

Master all visualization types and create stunning dashboards.

**Topics covered:**
- ✅ Time series panel (graphs, trends)
- ✅ Stat panel (KPIs, single values)
- ✅ Gauge and bar gauge (ranges, capacity)
- ✅ Table panel (detailed data)
- ✅ Bar chart (comparisons)
- ✅ Pie chart (distributions)
- ✅ Heatmap (density visualization)
- ✅ Logs panel (log streams)
- ✅ State timeline (state changes)
- ✅ Geomap (geographic data)
- ✅ Node graph (relationships)
- ✅ Custom panels with plugins
- ✅ Visualization best practices

**Code examples:** [`code/chapter04/`](code/chapter04/)

**Time to complete:** 5-6 hours

---

### [Chapter 5: Query Languages](chapter05-query-languages.md)
**查询语言精通**

Deep dive into query languages for all major data sources.

**Topics covered:**
- ✅ **PromQL**: Advanced selectors, functions, aggregations, histograms
- ✅ **Flux**: InfluxDB queries and transformations
- ✅ **SQL**: Time series and table queries with Grafana macros
- ✅ **LogQL**: Log queries and metrics from logs
- ✅ Query optimization techniques
- ✅ Subqueries and advanced patterns

**Code examples:** [`code/chapter05/`](code/chapter05/)

**Time to complete:** 5-7 hours

---

### [Chapter 6: Variables and Templating](chapter06-variables-templating.md)
**变量与模板**

Create dynamic, reusable dashboards with variables.

**Topics covered:**
- ✅ Variable types (Query, Custom, Text, Interval, etc.)
- ✅ Chained variables and dependencies
- ✅ Multi-value selection
- ✅ Global variables ($__from, $__to, $__interval)
- ✅ Using variables in queries
- ✅ Repeating panels and rows
- ✅ Advanced variable techniques
- ✅ Building dynamic multi-environment dashboards

**Code examples:** [`code/chapter06/`](code/chapter06/)

**Time to complete:** 4-5 hours

---

### [Chapter 7: Alerting System](chapter07-alerting-system.md)
**告警系统**

Comprehensive guide to Grafana's unified alerting system.

**Topics covered:**
- ✅ Alert rule creation and configuration
- ✅ Multi-condition alerts
- ✅ Notification policies and routing
- ✅ Contact points (Email, Slack, PagerDuty, Webhooks)
- ✅ Silences and mute timings
- ✅ Alert groups and states
- ✅ Template notifications
- ✅ Inhibition rules

**Code examples:** [`code/chapter07/`](code/chapter07/)

**Time to complete:** 4-5 hours

---

### [Chapter 8: Advanced Features](chapter08-advanced-features.md)
**高级特性**

Explore Grafana's advanced capabilities.

**Topics covered:**
- ✅ Annotations (manual and query-based)
- ✅ Plugins (installation and development)
- ✅ Grafana API (automation and integration)
- ✅ Provisioning (configuration as code)
- ✅ Library panels (reusable widgets)
- ✅ Explore (ad-hoc querying)
- ✅ Reporting and image rendering

**Code examples:** [`code/chapter08/`](code/chapter08/)

**Time to complete:** 4-5 hours

---

### [Chapter 9: Security and User Management](chapter09-security-user-management.md)
**安全与用户管理**

Secure your Grafana installation and manage users effectively.

**Topics covered:**
- ✅ Authentication methods (LDAP, OAuth, SAML, Basic)
- ✅ Authorization and roles
- ✅ User and team management
- ✅ Dashboard, folder, and data source permissions
- ✅ Organizations (multi-tenancy)
- ✅ API keys and service accounts
- ✅ Security best practices (HTTPS, secrets management)

**Code examples:** [`code/chapter09/`](code/chapter09/)

**Time to complete:** 3-4 hours

---

### [Chapter 10: Performance Optimization](chapter10-performance-optimization.md)
**性能优化**

Optimize Grafana for production workloads.

**Topics covered:**
- ✅ Query optimization (PromQL, SQL, recording rules)
- ✅ Dashboard optimization
- ✅ Caching strategies
- ✅ Resource configuration
- ✅ Monitoring Grafana itself
- ✅ Troubleshooting slow dashboards
- ✅ Database optimization

**Code examples:** [`code/chapter10/`](code/chapter10/)

**Time to complete:** 3-4 hours

---

### [Chapter 11: Enterprise Features](chapter11-enterprise-features.md)
**企业版功能**

Explore Grafana Enterprise capabilities.

**Topics covered:**
- ✅ Reporting (PDF/CSV exports)
- ✅ Role-Based Access Control (RBAC)
- ✅ Enterprise data sources (Oracle, MongoDB, Splunk, Snowflake)
- ✅ Auditing and compliance
- ✅ White labeling and branding
- ✅ Vault integration for secrets

**Code examples:** [`code/chapter11/`](code/chapter11/)

**Time to complete:** 3-4 hours

---

### [Chapter 12: Real-world Projects](chapter12-realworld-projects.md)
**实战项目**

Build complete, production-ready monitoring solutions.

**Topics covered:**
- ✅ Complete monitoring stack (Grafana + Prometheus + Loki + Tempo)
- ✅ Kubernetes monitoring (production-ready)
- ✅ Application Performance Monitoring (APM)
- ✅ Infrastructure monitoring (multi-cloud)
- ✅ Business metrics dashboards
- ✅ SRE dashboards (Golden Signals, SLI/SLO)
- ✅ Best practices summary

**Code examples:** [`code/chapter12/`](code/chapter12/)

**Time to complete:** 8-10 hours

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Basic command line knowledge
- 4GB+ RAM recommended

### Get Started in 5 Minutes

```bash
# Clone the repository
git clone <repo-url>
cd grafana

# Start the basic stack
cd code/chapter01/01-docker-basic
docker-compose up -d

# Access Grafana
open http://localhost:3000
# Login: admin / admin123
```

### Full Monitoring Stack

```bash
# Start complete stack (Grafana + Prometheus + Loki + Tempo)
cd code/chapter01/02-docker-compose
docker-compose up -d

# Access services
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
# Loki: http://localhost:3100
```

---

## 📁 Code Structure

All code examples are organized by chapter:

```
code/
├── chapter01/           # Installation and setup
│   ├── 01-docker-basic/         # Simple Grafana container
│   ├── 02-docker-compose/       # Full monitoring stack
│   ├── 03-windows-setup/        # Windows installation
│   └── 04-first-dashboard/      # First dashboard examples
│
├── chapter02/           # Fundamentals
│   ├── 01-datasources/          # Data source examples
│   ├── 02-dashboards/           # Dashboard templates
│   ├── 03-panels/               # Panel configurations
│   └── 04-transforms/           # Data transformations
│
├── chapter03/           # Data sources
│   ├── 01-prometheus-setup/     # Prometheus installation
│   ├── 02-promql-examples/      # PromQL queries
│   ├── 03-influxdb-flux/        # InfluxDB & Flux
│   ├── 04-mysql-queries/        # SQL examples
│   └── 05-loki-logql/           # Loki & LogQL
│
├── chapter04/           # Visualizations
│   ├── 01-timeseries-advanced/  # Advanced time series
│   ├── 02-table-advanced/       # Advanced tables
│   ├── 03-plugins/              # Plugin examples
│   └── 04-complete-dashboard/   # Multi-viz dashboard
│
├── chapter05/           # Query languages
│   ├── 01-promql-advanced/      # Advanced PromQL
│   └── 02-logql-advanced/       # Advanced LogQL
│
├── chapter06/           # Variables
│   └── dynamic-dashboard/       # Dynamic dashboard example
│
├── chapter07/           # Alerting
│   ├── 01-alert-rules/          # Alert rule examples
│   └── 02-advanced-alerting/    # Advanced alerting
│
├── chapter08/           # Advanced features
│   ├── 01-annotations/          # Annotation examples
│   ├── 02-plugin-development/   # Custom plugin
│   └── 03-api-examples/         # API usage examples
│
├── chapter09/           # Security
│   └── auth-configs/            # Authentication configs
│
├── chapter10/          # Performance
│   └── optimization-examples/   # Optimization techniques
│
├── chapter11/          # Enterprise
│   └── enterprise-configs/      # Enterprise configs
│
└── chapter12/          # Real-world projects
    ├── 01-complete-stack/       # Full monitoring stack
    ├── 02-kubernetes-monitoring/ # K8s monitoring
    └── 03-apm-monitoring/       # APM dashboard
```

---

## 🎓 Learning Approach

### For Beginners (0基础学习者)

**Recommended path:**
1. Start with Chapter 1 (Installation)
2. Complete hands-on labs in each chapter
3. Follow the code examples
4. Practice with provided Docker Compose stacks
5. Build your own dashboards as you learn

**Time commitment:**
- **Fast track**: 40-50 hours (intensive)
- **Recommended pace**: 2-3 months (2-3 hours/week)
- **Deep mastery**: 6 months (with real projects)

### For Experienced Users

Skip to relevant chapters:
- **DevOps Engineers**: Focus on Chapters 7-10, 12
- **SRE Teams**: Chapters 7, 10, 12
- **Developers**: Chapters 3-5, 8, 12
- **Data Analysts**: Chapters 3-6

---

## 💡 Key Features

### ✅ Hands-on Learning
- Every concept verified with working code
- Complete Docker Compose stacks ready to run
- Real-world examples and use cases

### ✅ Deep Coverage
- Comprehensive explanations for beginners
- Advanced techniques for experts
- Best practices from production experience

### ✅ Practical Focus
- Production-ready configurations
- Performance optimization tips
- Troubleshooting guides

### ✅ Complete Examples
- All code examples in [`code/`](code/) directory
- Copy-paste ready configurations
- Tested and verified

---

## 🛠️ Technologies Covered

### Monitoring Stack
- **Grafana** (latest version)
- **Prometheus** (metrics)
- **Loki** (logs)
- **Tempo** (traces)
- **Alertmanager** (alerting)

### Data Sources
- Prometheus
- InfluxDB
- MySQL / PostgreSQL
- Loki
- Elasticsearch
- TestData (for learning)

### Deployment
- Docker & Docker Compose
- Kubernetes (Helm)
- Cloud platforms (AWS, Azure, GCP)

---

## 📝 Prerequisites

### Required
- Basic understanding of monitoring concepts
- Command line familiarity
- Docker basics

### Recommended
- Linux/Unix basics
- SQL knowledge
- HTTP/REST understanding
- YAML syntax

### Not Required
- Prior Grafana experience
- Programming skills (helpful but not necessary)
- Advanced DevOps knowledge

---

## 🎯 Learning Objectives

By the end of this guide, you will be able to:

✅ Install and configure Grafana in any environment  
✅ Connect to multiple data source types  
✅ Create beautiful, interactive dashboards  
✅ Write efficient queries (PromQL, SQL, Flux, LogQL)  
✅ Implement alerting and notifications  
✅ Secure Grafana for production use  
✅ Optimize performance for large-scale deployments  
✅ Build complete monitoring solutions  
✅ Troubleshoot common issues  
✅ Integrate Grafana with existing infrastructure  

---

## 🔧 Setup Instructions

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB
- OS: Windows 10+, macOS 10.14+, Linux

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ (for data retention)
- OS: Linux (Ubuntu 20.04+)

### Installation

See [Chapter 1](chapter01-installation-setup.md) for detailed installation instructions for your platform.

**Quick Docker setup:**
```bash
# Pull images
docker pull grafana/grafana:latest
docker pull prom/prometheus:latest

# Start basic Grafana
docker run -d -p 3000:3000 --name=grafana grafana/grafana:latest

# Access: http://localhost:3000
# Login: admin / admin
```

---

## 📚 Additional Resources

### Official Documentation
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)

### Community
- [Grafana Community Forums](https://community.grafana.com/)
- [Grafana GitHub](https://github.com/grafana/grafana)
- [Discord Server](https://discord.gg/grafana)

### Practice Environments
- [Grafana Play](https://play.grafana.org/) - Free online instance
- [Killercoda Scenarios](https://killercoda.com/grafana)

### Dashboard Library
- [Grafana Dashboard Library](https://grafana.com/grafana/dashboards/)
- 15,000+ community dashboards

---

## 🤝 Contributing

This is a learning resource. If you find issues or want to improve content:

1. Report issues with specific chapter/section
2. Suggest improvements via pull requests
3. Share your success stories and custom dashboards

---

## 📖 Study Tips

### For Best Results

1. **Follow in order**: Chapters build on previous knowledge
2. **Run all code**: Don't just read, execute examples
3. **Experiment**: Modify examples and see what happens
4. **Build projects**: Apply knowledge to real scenarios
5. **Take notes**: Document what you learn
6. **Join community**: Ask questions, share knowledge

### Time Blocking

**Recommended schedule:**
- **Week 1-2**: Chapters 1-2 (Fundamentals)
- **Week 3-4**: Chapters 3-4 (Data Sources & Visualization)
- **Week 5-6**: Chapters 5-6 (Query Languages & Variables)
- **Week 7-8**: Chapters 7-8 (Alerting & Advanced)
- **Week 9-10**: Chapters 9-10 (Security & Performance)
- **Week 11-12**: Chapters 11-12 (Enterprise & Projects)

---

## 🎓 Certification & Career

### Skills You'll Gain
- Grafana Dashboard Design
- PromQL Mastery
- Monitoring Strategy
- Observability Best Practices
- SRE Principles

### Career Paths
- **DevOps Engineer**: Build monitoring infrastructure
- **SRE**: Implement SLI/SLO monitoring
- **Platform Engineer**: Manage observability platforms
- **Data Analyst**: Create business dashboards

---

## 📄 License

This educational content is provided for learning purposes.

---

## 🌟 What's Next?

After completing this guide:

1. **Build Your Portfolio**: Create unique dashboards
2. **Contribute**: Share dashboards with community
3. **Explore Plugins**: Develop custom visualizations
4. **Stay Updated**: Follow Grafana releases
5. **Teach Others**: Share your knowledge

---

## 📞 Support

**Questions about content?**
- Review the specific chapter
- Check code examples in `code/` directory
- Search Grafana community forums

**Technical issues?**
- Verify Docker/prerequisites
- Check system requirements
- Review troubleshooting sections in chapters

---

## 🎉 Start Your Journey!

Ready to become a Grafana expert?

**👉 Begin with [Chapter 1: Installation and Environment Setup](chapter01-installation-setup.md)**

**Good luck and happy monitoring! 📊📈**

---

**Last Updated:** 2024-11-06  
**Grafana Version:** 10.2+  
**Difficulty:** Beginner to Expert  
**Total Time:** 40-60 hours  
**Language:** English (with Chinese notes)
