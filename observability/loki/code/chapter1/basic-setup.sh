#!/bin/bash

# Loki 基础设置实验脚本
# 适用于 Linux/macOS 系统

echo "=== Loki 基础设置实验 ==="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建配置目录
mkdir -p data config

# 下载配置文件
echo "下载Loki配置文件..."
curl -o config/loki-local-config.yaml https://raw.githubusercontent.com/grafana/loki/v2.9.0/cmd/loki/loki-local-config.yaml

# 创建Promtail配置文件
echo "创建Promtail配置文件..."
cat > config/promtail-local-config.yaml << EOF
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://host.docker.internal:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log
EOF

# 创建docker-compose.yaml文件
echo "创建Docker Compose配置..."
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
      - ./config/promtail-local-config.yaml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
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
echo "启动Loki服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 显示访问信息
echo "=== 访问信息 ==="
echo "Loki API: http://localhost:3100"
echo "Grafana: http://localhost:3000"
echo "默认用户名/密码: admin/admin"
echo ""
echo "使用以下命令测试Loki健康状态:"
echo "curl http://localhost:3100/ready"

# 提供测试命令
echo "=== 有用的测试命令 ==="
echo "查看Loki日志: docker-compose logs -f loki"
echo "查看Promtail日志: docker-compose logs -f promtail"
echo "查看Grafana日志: docker-compose logs -f grafana"
echo "停止服务: docker-compose down"