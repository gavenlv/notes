#!/bin/bash

# Thanos环境依赖检查脚本
# 用于检查Thanos部署所需的基础依赖

echo "=== Thanos环境依赖检查 ==="
echo "检查时间: $(date)"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    local cmd=$1
    local name=$2
    local required=$3
    
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version 2>/dev/null | head -n1)
        echo -e "${GREEN}✓${NC} $name: $version"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $name: 未安装 (必需)"
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $name: 未安装 (可选)"
            return 0
        fi
    fi
}

# 检查端口占用
check_port() {
    local port=$1
    local service=$2
    
    if netstat -tuln 2>/dev/null | grep ":$port " &> /dev/null; then
        echo -e "${YELLOW}⚠${NC} 端口 $port 被占用 ($service)"
    else
        echo -e "${GREEN}✓${NC} 端口 $port 可用"
    fi
}

# 检查磁盘空间
check_disk_space() {
    local path=$1
    local required_gb=$2
    
    available_kb=$(df "$path" | awk 'NR==2 {print $4}')
    available_gb=$((available_kb / 1024 / 1024))
    
    if [ $available_gb -ge $required_gb ]; then
        echo -e "${GREEN}✓${NC} 磁盘空间: ${available_gb}GB可用 (需要${required_gb}GB)"
    else
        echo -e "${RED}✗${NC} 磁盘空间: ${available_gb}GB可用 (需要${required_gb}GB)"
    fi
}

# 检查内存
check_memory() {
    local required_mb=$1
    
    total_mb=$(free -m | awk 'NR==2{print $2}')
    
    if [ $total_mb -ge $required_mb ]; then
        echo -e "${GREEN}✓${NC} 内存: ${total_mb}MB (需要${required_mb}MB)"
    else
        echo -e "${YELLOW}⚠${NC} 内存: ${total_mb}MB (需要${required_mb}MB)"
    fi
}

# 检查操作系统
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        os_name=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
        kernel=$(uname -r)
        echo -e "${GREEN}✓${NC} 操作系统: $os_name"
        echo -e "${GREEN}✓${NC} 内核版本: $kernel"
    else
        echo -e "${YELLOW}⚠${NC} 操作系统: $OSTYPE (建议使用Linux)"
    fi
}

# 执行检查
echo "1. 操作系统检查:"
check_os
echo ""

echo "2. 必需软件检查:"
check_command "docker" "Docker" "true"
check_command "docker-compose" "Docker Compose" "true"
check_command "prometheus" "Prometheus" "false"
check_command "thanos" "Thanos" "false"
echo ""

echo "3. 可选软件检查:"
check_command "minio" "MinIO" "false"
check_command "grafana" "Grafana" "false"
check_command "nginx" "Nginx" "false"
check_command "jq" "jq" "false"
echo ""

echo "4. 系统资源检查:"
check_disk_space "/" 20
check_memory 4096
echo ""

echo "5. 端口占用检查:"
check_port 9000 "MinIO"
check_port 9090 "Prometheus"
check_port 19191 "Thanos Sidecar"
check_port 19192 "Thanos Query"
check_port 3000 "Grafana"
echo ""

# 总结
echo "=== 检查完成 ==="
echo ""
echo "建议:"
echo "1. 确保所有必需软件已安装"
echo "2. 检查端口占用情况，必要时修改配置"
echo "3. 确保有足够的磁盘空间和内存"
echo "4. 生产环境建议使用Linux操作系统"

# 退出码
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    exit 0
else
    exit 1
fi