#!/bin/bash

# ClickHouse + Prometheus + Grafana 监控系统启动脚本

echo "=========================================="
echo "ClickHouse + Prometheus + Grafana 监控系统"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p ./clickhouse
mkdir -p ./prometheus
mkdir -p ./grafana/provisioning/datasources
mkdir -p ./grafana/provisioning/dashboards
mkdir -p ./grafana/dashboards

# 启动服务
echo "启动监控服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
services=("clickhouse" "prometheus" "grafana" "clickhouse-exporter" "node-exporter")

for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        echo "✓ $service 运行正常"
    else
        echo "✗ $service 启动失败"
    fi
done

echo ""
echo "=========================================="
echo "服务访问地址:"
echo "=========================================="
echo "ClickHouse HTTP接口: http://localhost:8123"
echo "ClickHouse TCP接口: localhost:9000"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
echo "Node Exporter: http://localhost:9100"
echo "ClickHouse Exporter: http://localhost:9333"
echo ""
echo "Grafana登录信息:"
echo "用户名: admin"
echo "密码: admin123"
echo ""
echo "ClickHouse连接信息:"
echo "用户名: admin"
echo "密码: admin123"
echo "数据库: monitoring"
echo ""
echo "=========================================="
echo "常用命令:"
echo "=========================================="
echo "查看服务状态: docker-compose ps"
echo "查看日志: docker-compose logs [服务名]"
echo "停止服务: docker-compose down"
echo "重启服务: docker-compose restart"
echo "=========================================="