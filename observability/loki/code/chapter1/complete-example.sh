#!/bin/bash

# Loki 完整示例实验脚本
# 适用于 Linux/macOS 系统

echo "=== Loki 完整示例实验 ==="

# 创建测试日志目录
mkdir -p logs

# 生成测试日志
echo "生成测试日志..."

# 生成应用程序日志
cat > logs/app.log << EOF
2023-10-01T10:00:00.000Z [INFO] Application started
2023-10-01T10:01:00.000Z [INFO] User login: user123
2023-10-01T10:02:00.000Z [WARN] Slow query detected: SELECT * FROM users
2023-10-01T10:03:00.000Z [INFO] User logout: user123
2023-10-01T10:04:00.000Z [ERROR] Database connection failed
2023-10-01T10:05:00.000Z [INFO] Application restarted
EOF

# 生成Web服务器日志
cat > logs/web.log << EOF
192.168.1.100 - - [01/Oct/2023:10:00:00 +0000] "GET / HTTP/1.1" 200 1234
192.168.1.101 - - [01/Oct/2023:10:01:00 +0000] "GET /api/users HTTP/1.1" 200 567
192.168.1.102 - - [01/Oct/2023:10:02:00 +0000] "POST /api/login HTTP/1.1" 401 89
192.168.1.100 - - [01/Oct/2023:10:03:00 +0000] "GET /dashboard HTTP/1.1" 200 2345
192.168.1.103 - - [01/Oct/2023:10:04:00 +0000] "DELETE /api/users/123 HTTP/1.1" 200 12
EOF

# 创建高级Promtail配置文件
echo "创建高级Promtail配置..."
cat > promtail-advanced-config.yaml << EOF
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push

scrape_configs:
  # 收集应用程序日志（带解析）
  - job_name: application-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: application
          __path__: /var/log/app.log

    pipeline_stages:
      - regex:
          expression: '(?P<time>\S+) \[(?P<level>\w+)\] (?P<message>.*)'
      - timestamp:
          format: RFC3339Nano
          source: time
      - labels:
          level:
          - output:
              source: message

  # 收集Web服务器日志（带解析）
  - job_name: web-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: webserver
          __path__: /var/log/web.log

    pipeline_stages:
      - regex:
          expression: '(?P<client_ip>\S+) - - \[(?P<timestamp>.+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<size>\d+)'
      - labels:
          method:
          status:
      - output:
          source: message
EOF

# 创建Docker Compose文件
echo "创建Docker Compose文件..."
cat > docker-compose.yaml << EOF
version: "3.8"

services:
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./config/loki-local-config.yaml:/etc/loki/local-config.yaml
      - ./data:/loki
    networks:
      - loki

  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    volumes:
      - ./promtail-advanced-config.yaml:/etc/promtail/config.yml
      - ./logs:/var/log:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-storage:/var/lib/grafana
    networks:
      - loki

volumes:
  grafana-storage:

networks:
  loki:
    driver: bridge
EOF

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 检查Promtail目标状态
echo "检查Promtail目标状态..."
curl -s http://localhost:9080/targets | jq .

# 检查Loki标签
echo "检查Loki标签..."
curl -G -s "http://localhost:3100/loki/api/v1/label" --data-urlencode 'start=' --data-urlencode 'end=' --data-urlencode 'match[]={job=~".+"}' | jq .

# 添加日志到容器中的日志文件
echo "添加测试日志到容器..."
docker exec promtail sh -c "echo '2023-10-01T10:06:00.000Z [INFO] New log entry' >> /var/log/app.log"
docker exec promtail sh -c "echo '192.168.1.104 - - [01/Oct/2023:10:05:00 +0000] \"GET /api/status HTTP/1.1\" 200 34' >> /var/log/web.log"

# 显示访问信息
echo "=== 访问信息 ==="
echo "Loki API: http://localhost:3100"
echo "Grafana: http://localhost:3000"
echo "默认用户名/密码: admin/admin"
echo ""
echo "在Grafana中，添加Loki数据源："
echo "1. 转到 Configuration > Data Sources"
echo "2. 点击 Add data source"
echo "3. 选择 Loki"
echo "4. 设置 URL: http://loki:3100"
echo "5. 点击 Save & Test"
echo ""
echo "尝试以下查询："
echo "{job=\"application\"}"
echo "{job=\"webserver\"}"
echo "{job=\"application\"} |= \"error\""
echo "{job=\"webserver\"} |~ \"GET|POST\""

# 提供测试命令
echo "=== 有用的测试命令 ==="
echo "查看Loki日志: docker-compose logs -f loki"
echo "查看Promtail日志: docker-compose logs -f promtail"
echo "停止服务: docker-compose down"
echo "清理数据: docker-compose down -v"