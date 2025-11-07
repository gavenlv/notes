# 第1章：Prometheus安装与环境配置

## 1.1 Prometheus简介

### 1.1.1 什么是Prometheus？

**Prometheus** 是一个开源的系统监控和告警工具包，最初由SoundCloud开发。它现在是Cloud Native Computing Foundation (CNCF)的毕业项目。

**核心特性：**
- **多维数据模型**：基于时间序列，由指标名称和键值对标签标识
- **灵活的查询语言**：PromQL允许对数据进行切片和切块
- **不依赖分布式存储**：单个服务器节点是自治的
- **通过HTTP拉取**：通过拉取模型收集时间序列数据
- **推送时间序列**：通过中间网关支持推送
- **服务发现**：支持多种服务发现机制
- **可视化**：内置表达式浏览器和Grafana集成

### 1.1.2 Prometheus架构

```
┌─────────────┐
│  应用程序    │ (暴露/metrics端点)
└──────┬──────┘
       │
       │ HTTP拉取
       ▼
┌─────────────┐
│ Prometheus  │ (收集&存储)
│   Server    │
└──────┬──────┘
       │
       ├──────────┐
       │          │
       ▼          ▼
┌─────────┐  ┌──────────┐
│ Grafana │  │Alertman- │
│         │  │ ager     │
└─────────┘  └──────────┘
```

**核心组件：**

1. **Prometheus Server**：核心组件，负责抓取和存储时间序列数据
2. **Client Libraries**：客户端库，用于检测应用程序代码
3. **Pushgateway**：推送网关，用于短期任务
4. **Exporters**：专用导出器，用于HAProxy、StatsD、Graphite等服务
5. **Alertmanager**：告警管理器，处理告警

### 1.1.3 核心概念

#### 指标（Metric）
Prometheus中的基本数据单位，如：
```
http_requests_total{method="GET", endpoint="/api/users"} 1234
```

#### 标签（Label）
键值对，用于多维度标识指标：
```
标签名称：method, endpoint, status_code
标签值：GET, /api/users, 200
```

#### 时间序列（Time Series）
由指标名称和标签集唯一标识的数据点序列：
```
时间戳1: http_requests_total{method="GET"} 100
时间戳2: http_requests_total{method="GET"} 105
时间戳3: http_requests_total{method="GET"} 112
```

#### 采样（Sample）
时间序列中的单个数据点，包含：
- 浮点值
- 毫秒精度的时间戳

---

## 1.2 系统要求

### 1.2.1 最低要求
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB可用空间（取决于数据保留策略）
- **网络**: 互联网连接（用于下载）

### 1.2.2 推荐配置
- **CPU**: 4+核心
- **内存**: 8GB+ RAM
- **磁盘**: 100GB+ SSD（高性能）
- **操作系统**: 
  - Linux（Ubuntu 20.04+、CentOS 7+、Debian 10+）
  - Windows 10/11或Server 2016+
  - macOS 10.14+

### 1.2.3 存储规划

**磁盘空间计算公式：**
```
所需磁盘空间 = 采集的时间序列数 × 每个样本字节数 × 采样频率 × 保留时间

示例：
- 时间序列数：10,000
- 每个样本：1-2字节
- 采样频率：每15秒
- 保留时间：15天

计算：10,000 × 1.5 × (4次/分钟 × 60分钟 × 24小时 × 15天) = 约130GB
```

---

## 1.3 安装方法

### 1.3.1 Docker安装（推荐新手）

Docker是最简单的Prometheus安装方式，无需系统依赖。

**前置条件：**
- Docker已安装
- 基本的命令行知识

**安装步骤：**

**步骤1：拉取Prometheus镜像**
```bash
docker pull prom/prometheus:latest
```

**步骤2：创建配置文件**

创建文件 `prometheus.yml`：
```yaml
# Prometheus全局配置
global:
  # 默认抓取间隔
  scrape_interval: 15s
  # 默认规则评估间隔
  evaluation_interval: 15s
  # 附加到所有时间序列的外部标签
  external_labels:
    cluster: 'demo-cluster'
    environment: 'development'

# 告警管理器配置
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - 'localhost:9093'

# 加载告警规则
rule_files:
  # - 'alerts/*.yml'

# 抓取配置
scrape_configs:
  # Prometheus自身监控
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          instance: 'prometheus-server'
```

**步骤3：运行Prometheus容器**
```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest
```

**Windows PowerShell：**
```powershell
docker run -d `
  --name prometheus `
  -p 9090:9090 `
  -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml `
  prom/prometheus:latest
```

**步骤4：验证安装**

访问：http://localhost:9090

你应该看到Prometheus Web界面。

**步骤5：检查目标**

访问：http://localhost:9090/targets

应该看到一个"prometheus"目标，状态为"UP"。

参见完整示例：[code/chapter01/01-docker-basic/](code/chapter01/01-docker-basic/)

---

### 1.3.2 Docker Compose安装（生产环境推荐）

Docker Compose允许定义完整的监控栈。

**创建 `docker-compose.yml`：**
```yaml
version: '3.8'

services:
  # Prometheus服务器
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

  # Node Exporter - 系统指标
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped
    networks:
      - monitoring

  # cAdvisor - 容器指标
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    restart: unless-stopped
    networks:
      - monitoring

  # Grafana - 可视化
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
```

**Prometheus配置文件 `prometheus/prometheus.yml`：**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'docker-cluster'

scrape_configs:
  # Prometheus自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
        labels:
          instance: 'docker-host'

  # cAdvisor
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Grafana
  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
```

**启动监控栈：**
```bash
docker-compose up -d
```

**访问服务：**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)
- Node Exporter: http://localhost:9100/metrics
- cAdvisor: http://localhost:8080

完整示例：[code/chapter01/02-docker-compose/](code/chapter01/02-docker-compose/)

---

### 1.3.3 Linux二进制安装

**适用于：** 生产环境、无Docker环境

**步骤1：下载Prometheus**
```bash
# 创建Prometheus用户
sudo useradd --no-create-home --shell /bin/false prometheus

# 创建目录
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

# 下载最新版本
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz

# 解压
tar -xvf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64
```

**步骤2：安装二进制文件**
```bash
# 复制二进制文件
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/

# 复制配置文件
sudo cp -r consoles /etc/prometheus
sudo cp -r console_libraries /etc/prometheus
sudo cp prometheus.yml /etc/prometheus/

# 设置权限
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

**步骤3：创建systemd服务**

创建文件 `/etc/systemd/system/prometheus.service`：
```ini
[Unit]
Description=Prometheus监控系统
Documentation=https://prometheus.io/docs/introduction/overview/
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --storage.tsdb.retention.time=15d \
  --web.enable-lifecycle

ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**步骤4：启动Prometheus**
```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动Prometheus
sudo systemctl start prometheus

# 设置开机自启
sudo systemctl enable prometheus

# 检查状态
sudo systemctl status prometheus
```

**步骤5：配置防火墙**
```bash
# Ubuntu/Debian
sudo ufw allow 9090/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload
```

---

### 1.3.4 Windows安装

**步骤1：下载Windows版本**

访问：https://prometheus.io/download/
下载：`prometheus-X.X.X.windows-amd64.zip`

**步骤2：解压到目标目录**
```powershell
# 解压到C:\Program Files\Prometheus
Expand-Archive -Path prometheus-*.zip -DestinationPath "C:\Program Files\Prometheus"
```

**步骤3：配置Prometheus**

编辑 `C:\Program Files\Prometheus\prometheus.yml`

**步骤4：作为服务运行（使用NSSM）**
```powershell
# 下载NSSM
# https://nssm.cc/download

# 安装服务
nssm install prometheus "C:\Program Files\Prometheus\prometheus.exe"
nssm set prometheus AppParameters "--config.file=C:\Program Files\Prometheus\prometheus.yml"
nssm set prometheus AppDirectory "C:\Program Files\Prometheus"
nssm set prometheus DisplayName "Prometheus监控系统"
nssm set prometheus Description "Prometheus时间序列数据库和监控系统"
nssm set prometheus Start SERVICE_AUTO_START

# 启动服务
nssm start prometheus
```

**或者直接运行：**
```powershell
cd "C:\Program Files\Prometheus"
.\prometheus.exe --config.file=prometheus.yml
```

---

### 1.3.5 macOS安装

**方法1：Homebrew（推荐）**
```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Prometheus
brew install prometheus

# 启动Prometheus服务
brew services start prometheus

# 或在前台运行
prometheus --config.file=/usr/local/etc/prometheus.yml
```

**方法2：二进制安装**
```bash
# 下载
curl -LO https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.darwin-amd64.tar.gz

# 解压
tar -xzf prometheus-2.45.0.darwin-amd64.tar.gz
cd prometheus-2.45.0.darwin-amd64

# 运行
./prometheus --config.file=prometheus.yml
```

---

## 1.4 初始配置

### 1.4.1 配置文件结构

Prometheus主配置文件 `prometheus.yml` 采用YAML格式：

```yaml
# 全局配置
global:
  scrape_interval: 15s        # 抓取间隔
  evaluation_interval: 15s    # 规则评估间隔
  scrape_timeout: 10s         # 抓取超时
  external_labels:            # 外部标签
    cluster: 'production'
    region: 'us-east-1'

# 告警管理器配置
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'

# 规则文件
rule_files:
  - 'rules/*.yml'

# 抓取配置
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### 1.4.2 配置项详解

#### global配置块

```yaml
global:
  # 默认抓取间隔（可被job覆盖）
  scrape_interval: 15s
  
  # 规则评估间隔
  evaluation_interval: 15s
  
  # 抓取超时时间
  scrape_timeout: 10s
  
  # 外部标签（用于联邦和远程存储）
  external_labels:
    cluster: 'my-cluster'
    environment: 'production'
    datacenter: 'dc1'
```

#### scrape_configs配置块

```yaml
scrape_configs:
  # 任务名称
  - job_name: 'my-application'
    
    # 抓取间隔（覆盖global）
    scrape_interval: 30s
    
    # 抓取超时
    scrape_timeout: 10s
    
    # 指标路径
    metrics_path: /metrics
    
    # 协议
    scheme: http
    
    # 静态目标
    static_configs:
      - targets:
          - 'app1:8080'
          - 'app2:8080'
        labels:
          env: 'prod'
          team: 'backend'
```

### 1.4.3 验证配置

**使用promtool检查配置：**
```bash
# 检查配置文件语法
promtool check config prometheus.yml

# 检查规则文件
promtool check rules rules/*.yml
```

**重新加载配置（不重启）：**
```bash
# 发送SIGHUP信号
kill -HUP <prometheus-pid>

# 或使用API（需要启用--web.enable-lifecycle）
curl -X POST http://localhost:9090/-/reload
```

---

## 1.5 首次访问和基本使用

### 1.5.1 访问Web界面

打开浏览器访问：http://localhost:9090

**主要功能区域：**
- **Graph（图形）**：查询和可视化指标
- **Alerts（告警）**：查看告警状态
- **Status（状态）**：查看配置、目标、规则等
- **Help（帮助）**：文档链接

### 1.5.2 执行第一个查询

在Graph页面的查询框中输入：

**查询1：Prometheus自身的启动时间**
```promql
prometheus_build_info
```

点击"Execute"按钮，切换到"Table"视图查看结果。

**查询2：Prometheus抓取的样本数**
```promql
prometheus_tsdb_head_samples
```

**查询3：最近5分钟的抓取速率**
```promql
rate(prometheus_http_requests_total[5m])
```

### 1.5.3 查看目标状态

访问：http://localhost:9090/targets

这里显示所有配置的抓取目标及其状态：
- **UP**：目标健康
- **DOWN**：目标不可达
- **UNKNOWN**：未知状态

**目标信息：**
- Endpoint：抓取端点
- State：当前状态
- Labels：目标标签
- Last Scrape：最后抓取时间
- Scrape Duration：抓取耗时
- Error：错误信息（如果有）

### 1.5.4 查看配置

访问：http://localhost:9090/config

显示当前加载的完整配置文件。

### 1.5.5 查看服务发现

访问：http://localhost:9090/service-discovery

显示服务发现机制发现的所有目标。

---

## 1.6 实验：创建完整监控环境

让我们通过一个完整的实验来验证所有概念。

### 1.6.1 实验目标

搭建一个包含以下组件的监控环境：
- Prometheus（监控核心）
- Node Exporter（系统指标）
- cAdvisor（容器指标）
- Pushgateway（短期任务）
- Alertmanager（告警）
- Grafana（可视化）

### 1.6.2 实验步骤

**步骤1：创建项目目录**
```bash
mkdir -p prometheus-lab/{prometheus,grafana,alertmanager}
cd prometheus-lab
```

**步骤2：创建Prometheus配置**

文件：`prometheus/prometheus.yml`
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'lab-cluster'
    environment: 'learning'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager:9093'

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  # Prometheus自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          instance: 'prometheus-server'

  # Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
        labels:
          instance: 'lab-host'

  # cAdvisor
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Pushgateway
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']

  # Alertmanager
  - job_name: 'alertmanager'
    static_configs:
      - targets: ['alertmanager:9093']

  # Grafana
  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']
```

**步骤3：创建告警规则**

文件：`prometheus/rules/system_alerts.yml`
```yaml
groups:
  - name: system_alerts
    interval: 30s
    rules:
      # CPU使用率告警
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "高CPU使用率 (实例 {{ $labels.instance }})"
          description: "CPU使用率超过80%，当前值：{{ $value | humanize }}%"

      # 内存使用率告警
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          summary: "高内存使用率 (实例 {{ $labels.instance }})"
          description: "内存使用率超过90%，当前值：{{ $value | humanize }}%"

      # 磁盘空间告警
      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.*"} / node_filesystem_size_bytes{fstype!~"tmpfs|fuse.*"})) * 100 > 85
        for: 10m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "磁盘空间不足 (实例 {{ $labels.instance }}，挂载点 {{ $labels.mountpoint }})"
          description: "磁盘使用率超过85%，当前值：{{ $value | humanize }}%"
```

**步骤4：创建Alertmanager配置**

文件：`alertmanager/alertmanager.yml`
```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'default-receiver'
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  
  routes:
    # 关键告警
    - match:
        severity: critical
      receiver: 'critical-receiver'
      continue: true
    
    # 警告告警
    - match:
        severity: warning
      receiver: 'warning-receiver'

receivers:
  - name: 'default-receiver'
    webhook_configs:
      - url: 'http://webhook-example:8080/alert'
        send_resolved: true

  - name: 'critical-receiver'
    webhook_configs:
      - url: 'http://webhook-example:8080/critical'

  - name: 'warning-receiver'
    webhook_configs:
      - url: 'http://webhook-example:8080/warning'

inhibit_rules:
  # 抑制规则：当节点宕机时，抑制该节点的其他告警
  - source_match:
      alertname: 'InstanceDown'
    target_match_re:
      alertname: '.*'
    equal: ['instance']
```

**步骤5：创建Grafana数据源配置**

文件：`grafana/provisioning/datasources/prometheus.yml`
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
      queryTimeout: 60s
      httpMethod: POST
```

**步骤6：创建Docker Compose文件**

文件：`docker-compose.yml`
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    restart: unless-stopped
    networks:
      - monitoring

  pushgateway:
    image: prom/pushgateway:latest
    container_name: pushgateway
    ports:
      - "9091:9091"
    restart: unless-stopped
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager:/etc/alertmanager
      - alertmanager-data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus-data:
  alertmanager-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
```

**步骤7：启动监控环境**
```bash
docker-compose up -d
```

**步骤8：验证所有服务**

访问以下URL验证：
- Prometheus: http://localhost:9090
- Prometheus Targets: http://localhost:9090/targets
- Prometheus Alerts: http://localhost:9090/alerts
- Node Exporter: http://localhost:9100/metrics
- cAdvisor: http://localhost:8080
- Pushgateway: http://localhost:9091
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000 (admin/admin123)

**步骤9：测试推送指标**

使用Pushgateway推送自定义指标：
```bash
# 推送单个指标
echo "test_metric 42" | curl --data-binary @- http://localhost:9091/metrics/job/test_job

# 推送多个指标
cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/batch_job/instance/job1
# TYPE batch_records_processed counter
batch_records_processed 1234
# TYPE batch_duration_seconds gauge
batch_duration_seconds 45.5
EOF
```

在Prometheus中查询：
```promql
test_metric
batch_records_processed
```

**步骤10：查看告警**

访问 http://localhost:9090/alerts 查看配置的告警规则状态。

完整实验代码：[code/chapter01/03-complete-lab/](code/chapter01/03-complete-lab/)

---

## 1.7 故障排查

### 1.7.1 常见问题

#### 问题1：端口9090已被占用

**错误信息：**
```
Error: bind: address already in use
```

**解决方案：**
```bash
# Linux/Mac：查找占用端口的进程
sudo lsof -i :9090
sudo kill -9 <PID>

# Windows：
netstat -ano | findstr :9090
taskkill /PID <PID> /F

# 或更改端口
# 在docker-compose.yml中：
ports:
  - "9091:9090"  # 使用9091端口
```

#### 问题2：无法访问目标

**检查清单：**
1. 目标服务是否运行
2. 网络连接是否正常
3. 防火墙规则
4. Docker网络配置

**Docker网络问题：**
```bash
# 检查容器是否在同一网络
docker network inspect monitoring

# 使用容器名称而不是localhost
targets: ['node-exporter:9100']  # ✅ 正确
targets: ['localhost:9100']       # ❌ 错误（Docker内）
```

#### 问题3：配置文件格式错误

**验证配置：**
```bash
# 检查配置语法
promtool check config prometheus.yml

# 检查规则文件
promtool check rules rules/*.yml
```

**常见YAML错误：**
```yaml
# ❌ 错误：缩进不一致
scrape_configs:
  - job_name: 'test'
   static_configs:  # 缩进错误

# ✅ 正确：
scrape_configs:
  - job_name: 'test'
    static_configs:  # 正确缩进
```

#### 问题4：数据未持久化

**Docker容器数据丢失：**
```bash
# 使用命名卷
volumes:
  - prometheus-data:/prometheus  # ✅ 持久化

# 不要使用匿名卷
volumes:
  - /prometheus  # ❌ 数据会丢失
```

#### 问题5：内存不足

**症状：**
```
OOM killed
Prometheus crashed
```

**解决方案：**
```yaml
# 限制内存使用
command:
  - '--storage.tsdb.retention.time=7d'  # 减少保留时间
  - '--storage.tsdb.retention.size=10GB'  # 限制存储大小

# Docker资源限制
deploy:
  resources:
    limits:
      memory: 4G
```

---

## 1.8 最佳实践

### 1.8.1 配置管理

1. **版本控制**：将配置文件纳入Git管理
2. **环境分离**：使用不同的配置文件区分环境
3. **配置验证**：部署前使用promtool验证
4. **文档化**：为自定义配置添加注释

### 1.8.2 安全建议

1. **更改默认端口**：在生产环境使用非默认端口
2. **启用身份验证**：使用反向代理添加认证
3. **网络隔离**：使用防火墙限制访问
4. **HTTPS**：使用TLS加密通信
5. **最小权限**：Prometheus进程使用专用用户

### 1.8.3 性能优化

1. **合理设置采集间隔**：
   ```yaml
   scrape_interval: 15s  # 默认
   scrape_interval: 30s  # 低优先级目标
   ```

2. **限制时间序列数**：使用relabel_configs过滤不需要的标签
3. **使用本地SSD**：提高存储性能
4. **监控Prometheus自身**：关注CPU、内存、磁盘使用

---

## 1.9 总结

在本章中，你学习了：

✅ **Prometheus架构**：核心组件和工作原理  
✅ **多种安装方式**：Docker、二进制、系统服务  
✅ **配置文件结构**：global、scrape_configs等配置块  
✅ **Web界面使用**：查询、目标状态、配置查看  
✅ **完整实验环境**：包含监控栈的所有组件  
✅ **故障排查**：常见问题和解决方案  
✅ **最佳实践**：配置、安全、性能建议  

### 下一步学习

在 **第2章** 中，我们将深入学习：
- Prometheus的四种指标类型
- 数据模型和标签系统
- 时间序列的唯一性
- 指标命名规范

---

## 1.10 练习题

### 练习1：基础安装
1. 使用Docker安装Prometheus
2. 修改配置文件添加自定义标签
3. 访问Web界面并执行查询

### 练习2：监控栈搭建
1. 使用Docker Compose部署完整监控栈
2. 验证所有服务正常运行
3. 查看Node Exporter收集的系统指标

### 练习3：配置验证
1. 创建一个包含语法错误的配置文件
2. 使用promtool检查并修复错误
3. 重新加载配置

### 练习4：Pushgateway测试
1. 启动Pushgateway
2. 推送自定义指标
3. 在Prometheus中查询推送的指标

**练习答案**：[code/chapter01/04-exercises/](code/chapter01/04-exercises/)

---

## 1.11 参考资源

### 官方文档
- [Prometheus官方文档](https://prometheus.io/docs/introduction/overview/)
- [安装指南](https://prometheus.io/docs/prometheus/latest/installation/)
- [配置说明](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)

### 社区资源
- [Prometheus GitHub](https://github.com/prometheus/prometheus)
- [CNCF Prometheus](https://www.cncf.io/projects/prometheus/)
- [Prometheus邮件列表](https://groups.google.com/g/prometheus-users)

### 在线工具
- [PromLens](https://promlens.com/) - PromQL查询构建器
- [Prometheus演示](https://demo.promlabs.com/) - 在线演示环境

---

**下一章**：[第2章：Prometheus核心概念](第2章-Prometheus核心概念.md)
