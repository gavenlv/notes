# Ansible 监控与日志管理

监控和日志管理是现代 IT 基础设施运维的核心组成部分。通过 Ansible，我们可以自动化部署、配置和管理各种监控和日志解决方案。

## 1. Prometheus 监控系统

Prometheus 是一个开源的系统监控和告警工具包，特别适合云原生环境。

### 1.1 Prometheus Server 部署

```yaml
---
- name: Deploy Prometheus Server
  hosts: monitoring
  become: yes
  vars:
    prometheus_version: "2.45.0"
    prometheus_install_dir: "/opt/prometheus"
    prometheus_data_dir: "/var/lib/prometheus"
    
  tasks:
    # 创建必要的用户和目录
    - name: Create prometheus group
      group:
        name: prometheus
        state: present

    - name: Create prometheus user
      user:
        name: prometheus
        group: prometheus
        system: yes
        shell: /bin/false
        home: "{{ prometheus_install_dir }}"

    - name: Create directories
      file:
        path: "{{ item }}"
        state: directory
        owner: prometheus
        group: prometheus
        mode: '0755'
      loop:
        - "{{ prometheus_install_dir }}"
        - "{{ prometheus_data_dir }}"
        - "/etc/prometheus"
        - "/etc/prometheus/rules"

    # 下载并安装 Prometheus
    - name: Download Prometheus
      get_url:
        url: "https://github.com/prometheus/prometheus/releases/download/v{{ prometheus_version }}/prometheus-{{ prometheus_version }}.linux-amd64.tar.gz"
        dest: "/tmp/prometheus-{{ prometheus_version }}.linux-amd64.tar.gz"
        mode: '0644'

    - name: Extract Prometheus
      unarchive:
        src: "/tmp/prometheus-{{ prometheus_version }}.linux-amd64.tar.gz"
        dest: "/tmp"
        remote_src: yes

    - name: Copy Prometheus binaries
      copy:
        src: "/tmp/prometheus-{{ prometheus_version }}.linux-amd64/{{ item }}"
        dest: "{{ prometheus_install_dir }}/{{ item }}"
        owner: prometheus
        group: prometheus
        mode: '0755'
        remote_src: yes
      loop:
        - prometheus
        - promtool

    - name: Copy Prometheus console templates
      copy:
        src: "/tmp/prometheus-{{ prometheus_version }}.linux-amd64/{{ item }}"
        dest: "{{ prometheus_install_dir }}/{{ item }}"
        owner: prometheus
        group: prometheus
        mode: '0644'
        remote_src: yes
      loop:
        - consoles/
        - console_libraries/

    # 配置 Prometheus
    - name: Create Prometheus configuration
      template:
        src: prometheus.yml.j2
        dest: /etc/prometheus/prometheus.yml
        owner: prometheus
        group: prometheus
        mode: '0644'

    # 创建 systemd 服务
    - name: Create systemd service file
      template:
        src: prometheus.service.j2
        dest: /etc/systemd/system/prometheus.service
        mode: '0644'

    # 启动服务
    - name: Reload systemd and start Prometheus
      systemd:
        daemon_reload: yes
        name: prometheus
        state: started
        enabled: yes
```

### 1.2 Prometheus 配置模板

```yaml
# prometheus.yml.j2
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: {{ groups['webservers'] | map('regex_replace', '^(.*)$', '\1:9100') | list }}

  - job_name: 'application'
    static_configs:
      - targets: {{ groups['webservers'] | map('regex_replace', '^(.*)$', '\1:8080') | list }}
```

## 2. Node Exporter 部署

Node Exporter 用于暴露系统级别的指标给 Prometheus。

```yaml
---
- name: Deploy Node Exporter
  hosts: all
  become: yes
  vars:
    node_exporter_version: "1.6.1"
    node_exporter_install_dir: "/opt/node_exporter"
    
  tasks:
    - name: Create node_exporter group
      group:
        name: node_exporter
        state: present

    - name: Create node_exporter user
      user:
        name: node_exporter
        group: node_exporter
        system: yes
        shell: /bin/false
        home: "{{ node_exporter_install_dir }}"

    - name: Create installation directory
      file:
        path: "{{ node_exporter_install_dir }}"
        state: directory
        owner: node_exporter
        group: node_exporter
        mode: '0755'

    - name: Download Node Exporter
      get_url:
        url: "https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
        dest: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
        mode: '0644'

    - name: Extract Node Exporter
      unarchive:
        src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
        dest: "/tmp"
        remote_src: yes

    - name: Copy Node Exporter binary
      copy:
        src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64/node_exporter"
        dest: "{{ node_exporter_install_dir }}/node_exporter"
        owner: node_exporter
        group: node_exporter
        mode: '0755'
        remote_src: yes

    - name: Create systemd service file
      template:
        src: node_exporter.service.j2
        dest: /etc/systemd/system/node_exporter.service
        mode: '0644'

    - name: Start Node Exporter service
      systemd:
        name: node_exporter
        state: started
        enabled: yes
        daemon_reload: yes
```

## 3. Grafana 部署与配置

Grafana 是一个开源的可视化平台，用于展示监控数据。

```yaml
---
- name: Deploy Grafana
  hosts: monitoring
  become: yes
  vars:
    grafana_version: "10.0.3"
    grafana_install_dir: "/opt/grafana"
    
  tasks:
    - name: Install prerequisites
      package:
        name:
          - wget
          - tar
        state: present

    - name: Download Grafana
      get_url:
        url: "https://dl.grafana.com/oss/release/grafana-{{ grafana_version }}.linux-amd64.tar.gz"
        dest: "/tmp/grafana-{{ grafana_version }}.linux-amd64.tar.gz"
        mode: '0644'

    - name: Create installation directory
      file:
        path: "{{ grafana_install_dir }}"
        state: directory
        mode: '0755'

    - name: Extract Grafana
      unarchive:
        src: "/tmp/grafana-{{ grafana_version }}.linux-amd64.tar.gz"
        dest: "{{ grafana_install_dir }}"
        remote_src: yes
        extra_opts: [--strip-components=1]

    - name: Create grafana group
      group:
        name: grafana
        state: present

    - name: Create grafana user
      user:
        name: grafana
        group: grafana
        system: yes
        shell: /bin/false
        home: "{{ grafana_install_dir }}"

    - name: Set ownership
      file:
        path: "{{ grafana_install_dir }}"
        state: directory
        owner: grafana
        group: grafana
        recurse: yes

    - name: Create systemd service file
      template:
        src: grafana.service.j2
        dest: /etc/systemd/system/grafana-server.service
        mode: '0644'

    - name: Start Grafana service
      systemd:
        name: grafana-server
        state: started
        enabled: yes
        daemon_reload: yes
```

## 4. ELK Stack 部署

ELK Stack (Elasticsearch, Logstash, Kibana) 是一个强大的日志分析平台。

### 4.1 Elasticsearch 部署

```yaml
---
- name: Deploy Elasticsearch
  hosts: logging
  become: yes
  vars:
    es_version: "8.8.1"
    es_heap_size: "2g"
    
  tasks:
    - name: Install Java
      package:
        name: openjdk-17-jdk
        state: present

    - name: Add Elasticsearch GPG key
      apt_key:
        url: https://artifacts.elastic.co/GPG-KEY-elasticsearch
        state: present

    - name: Add Elasticsearch repository
      apt_repository:
        repo: deb https://artifacts.elastic.co/packages/8.x/apt stable main
        state: present

    - name: Install Elasticsearch
      package:
        name: elasticsearch={{ es_version }}
        state: present

    - name: Configure Elasticsearch
      template:
        src: elasticsearch.yml.j2
        dest: /etc/elasticsearch/elasticsearch.yml
        mode: '0644'
      notify: restart elasticsearch

    - name: Configure JVM options
      lineinfile:
        path: /etc/elasticsearch/jvm.options
        regexp: '^-Xms'
        line: "-Xms{{ es_heap_size }}"
      notify: restart elasticsearch

    - name: Start Elasticsearch service
      systemd:
        name: elasticsearch
        state: started
        enabled: yes

  handlers:
    - name: restart elasticsearch
      systemd:
        name: elasticsearch
        state: restarted
```

### 4.2 Logstash 配置

```yaml
---
- name: Configure Logstash
  hosts: logging
  become: yes
  tasks:
    - name: Install Logstash
      package:
        name: logstash
        state: present

    - name: Create Logstash configuration
      template:
        src: logstash.conf.j2
        dest: /etc/logstash/conf.d/logstash.conf
        mode: '0644'
      notify: restart logstash

    - name: Start Logstash service
      systemd:
        name: logstash
        state: started
        enabled: yes

  handlers:
    - name: restart logstash
      systemd:
        name: logstash
        state: restarted
```

### 4.3 Kibana 部署

```yaml
---
- name: Deploy Kibana
  hosts: logging
  become: yes
  tasks:
    - name: Install Kibana
      package:
        name: kibana
        state: present

    - name: Configure Kibana
      template:
        src: kibana.yml.j2
        dest: /etc/kibana/kibana.yml
        mode: '0644'
      notify: restart kibana

    - name: Start Kibana service
      systemd:
        name: kibana
        state: started
        enabled: yes

  handlers:
    - name: restart kibana
      systemd:
        name: kibana
        state: restarted
```

## 5. Fluentd 部署

Fluentd 是一个开源的数据收集器，用于统一日志记录层。

```yaml
---
- name: Deploy Fluentd
  hosts: all
  become: yes
  tasks:
    - name: Install prerequisites
      package:
        name:
          - ruby
          - ruby-dev
          - build-essential
        state: present

    - name: Install Fluentd
      gem:
        name: fluentd
        state: present
        user_install: no

    - name: Install fluent-plugin-elasticsearch
      gem:
        name: fluent-plugin-elasticsearch
        state: present
        user_install: no

    - name: Generate Fluentd configuration
      command: fluentd --setup /etc/fluent
      args:
        creates: /etc/fluent/fluent.conf

    - name: Create Fluentd configuration
      template:
        src: fluentd.conf.j2
        dest: /etc/fluent/fluent.conf
        mode: '0644'

    - name: Create Fluentd service file
      template:
        src: fluentd.service.j2
        dest: /etc/systemd/system/fluentd.service
        mode: '0644'

    - name: Start Fluentd service
      systemd:
        name: fluentd
        state: started
        enabled: yes
        daemon_reload: yes
```

## 6. 自定义监控脚本

创建自定义监控脚本以收集特定应用程序指标。

```yaml
---
- name: Deploy Custom Monitoring Scripts
  hosts: webservers
  become: yes
  tasks:
    - name: Create monitoring scripts directory
      file:
        path: /opt/monitoring/scripts
        state: directory
        mode: '0755'

    - name: Deploy application health check script
      template:
        src: app_health_check.sh.j2
        dest: /opt/monitoring/scripts/app_health_check.sh
        mode: '0755'

    - name: Deploy system metrics collection script
      template:
        src: system_metrics.sh.j2
        dest: /opt/monitoring/scripts/system_metrics.sh
        mode: '0755'

    - name: Create cron jobs for monitoring scripts
      cron:
        name: "{{ item.name }}"
        minute: "{{ item.minute }}"
        job: "{{ item.job }}"
        user: root
      loop:
        - { name: "Application Health Check", minute: "*/5", job: "/opt/monitoring/scripts/app_health_check.sh" }
        - { name: "System Metrics Collection", minute: "*/10", job: "/opt/monitoring/scripts/system_metrics.sh" }
```

## 7. 日志轮转配置

配置日志轮转以防止日志文件过大。

```yaml
---
- name: Configure Log Rotation
  hosts: all
  become: yes
  tasks:
    - name: Install logrotate
      package:
        name: logrotate
        state: present

    - name: Create application logrotate configuration
      template:
        src: app_logrotate.j2
        dest: /etc/logrotate.d/myapp
        mode: '0644'

    - name: Create system logrotate configuration
      template:
        src: system_logrotate.j2
        dest: /etc/logrotate.d/system
        mode: '0644'
```

## 8. 告警规则配置

配置 Prometheus 告警规则。

```yaml
# alert_rules.yml
groups:
- name: example-alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected on {{ $labels.instance }}"
      description: "{{ $labels.instance }} CPU usage is above 80% for more than 5 minutes."

  - alert: LowDiskSpace
    expr: (node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes < 10
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Low disk space on {{ $labels.instance }}"
      description: "{{ $labels.instance }} has less than 10% disk space available."

  - alert: ApplicationDown
    expr: up{job="application"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Application is down on {{ $labels.instance }}"
      description: "Application on {{ $labels.instance }} is not responding."
```

通过今天的练习，您已经学会了如何使用 Ansible 来部署和配置各种监控和日志解决方案。这些技能对于维护生产环境的稳定性和可观察性至关重要。