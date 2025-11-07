# Loki 基础设置实验脚本
# 适用于 Windows 系统

Write-Host "=== Loki 基础设置实验 ==="

# 检查Docker是否安装
try {
    $dockerVersion = docker --version
    Write-Host "Docker已安装: $dockerVersion"
} catch {
    Write-Host "Docker 未安装，请先安装 Docker Desktop"
    exit 1
}

# 检查Docker Compose是否安装
try {
    $composeVersion = docker-compose --version
    Write-Host "Docker Compose已安装: $composeVersion"
} catch {
    Write-Host "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
}

# 创建配置目录
New-Item -ItemType Directory -Force -Path "data", "config" | Out-Null

# 下载配置文件
Write-Host "下载Loki配置文件..."
try {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/grafana/loki/v2.9.0/cmd/loki/loki-local-config.yaml" -OutFile "config\loki-local-config.yaml"
    Write-Host "Loki配置文件下载完成"
} catch {
    Write-Host "下载Loki配置文件失败"
    exit 1
}

# 创建Promtail配置文件
Write-Host "创建Promtail配置文件..."
@"
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
"@ | Out-File -FilePath "config\promtail-local-config.yaml" -Encoding UTF8
Write-Host "Promtail配置文件创建完成"

# 创建docker-compose.yaml文件
Write-Host "创建Docker Compose配置..."
@"
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
"@ | Out-File -FilePath "docker-compose.yaml" -Encoding UTF8
Write-Host "Docker Compose配置文件创建完成"

# 启动服务
Write-Host "启动Loki服务..."
docker-compose up -d

# 等待服务启动
Write-Host "等待服务启动..."
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "检查服务状态..."
docker-compose ps

# 显示访问信息
Write-Host "=== 访问信息 ==="
Write-Host "Loki API: http://localhost:3100"
Write-Host "Grafana: http://localhost:3000"
Write-Host "默认用户名/密码: admin/admin"
Write-Host ""
Write-Host "使用以下命令测试Loki健康状态:"
Write-Host "curl http://localhost:3100/ready"

# 提供测试命令
Write-Host "=== 有用的测试命令 ==="
Write-Host "查看Loki日志: docker-compose logs -f loki"
Write-Host "查看Promtail日志: docker-compose logs -f promtail"
Write-Host "查看Grafana日志: docker-compose logs -f grafana"
Write-Host "停止服务: docker-compose down"