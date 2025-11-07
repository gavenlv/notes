#!/bin/bash

# Grafana 基础设置实验脚本
# 适用于 Linux/macOS 系统

echo "=== Grafana 基础设置实验 ==="

# 检查Grafana是否已安装
if ! command -v grafana-server &> /dev/null; then
    echo "Grafana 未安装，请先按照教程 1.2 安装 Grafana"
    exit 1
fi

# 启动Grafana服务
echo "启动 Grafana 服务..."
sudo systemctl start grafana-server

# 检查服务状态
echo "检查 Grafana 服务状态..."
sudo systemctl status grafana-server --no-pager

# 等待服务完全启动
echo "等待 Grafana 服务启动..."
sleep 5

# 检查端口是否开放
echo "检查端口 3000 是否开放..."
if command -v netstat &> /dev/null; then
    netstat -tlnp | grep :3000
elif command -v ss &> /dev/null; then
    ss -tlnp | grep :3000
fi

# 显示访问信息
echo "=== 访问信息 ==="
echo "URL: http://localhost:3000"
echo "默认用户名: admin"
echo "默认密码: admin"
echo ""
echo "请按照教程 1.3 创建第一个仪表盘"

# 提供一些测试命令
echo "=== 有用的测试命令 ==="
echo "查看 Grafana 日志: sudo journalctl -u grafana-server -f"
echo "停止 Grafana 服务: sudo systemctl stop grafana-server"
echo "重启 Grafana 服务: sudo systemctl restart grafana-server"