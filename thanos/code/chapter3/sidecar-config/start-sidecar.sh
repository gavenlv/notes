#!/bin/bash

# Thanos Sidecar启动脚本
# 用于自动化启动和配置Thanos Sidecar

set -e

# 配置参数
SIDECAR_HTTP_PORT="19191"
SIDECAR_GRPC_PORT="19090"
PROMETHEUS_URL="http://localhost:9090"
TSDB_PATH="/prometheus"
CONFIG_FILE="/etc/thanos/minio-bucket.yaml"
LOG_LEVEL="info"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 启动Thanos Sidecar ===${NC}"

# 函数：检查服务状态
check_service() {
    local service_url=$1
    local service_name=$2
    
    echo -n "检查${service_name}服务..."
    if curl -s "${service_url}/-/ready" > /dev/null; then
        echo -e "${GREEN}✓ 就绪${NC}"
        return 0
    else
        echo -e "${RED}✗ 未就绪${NC}"
        return 1
    fi
}

# 函数：等待服务就绪
wait_for_service() {
    local service_url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "等待${service_name}服务就绪..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_service "$service_url" "$service_name"; then
            return 0
        fi
        
        echo "尝试 ${attempt}/${max_attempts}，等待5秒..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}错误: ${service_name}服务在指定时间内未就绪${NC}"
    return 1
}

# 函数：检查配置文件
check_config_file() {
    local config_file=$1
    
    echo -n "检查配置文件 ${config_file}..."
    if [ -f "$config_file" ]; then
        echo -e "${GREEN}✓ 存在${NC}"
        
        # 验证YAML格式
        if command -v yq &> /dev/null; then
            if yq e '.' "$config_file" > /dev/null 2>&1; then
                echo -e "${GREEN}✓ YAML格式正确${NC}"
            else
                echo -e "${RED}✗ YAML格式错误${NC}"
                return 1
            fi
        else
            echo "⚠ 跳过YAML验证 (yq工具未安装)"
        fi
        
        return 0
    else
        echo -e "${RED}✗ 不存在${NC}"
        return 1
    fi
}

# 函数：检查TSDB路径
check_tsdb_path() {
    local tsdb_path=$1
    
    echo -n "检查TSDB路径 ${tsdb_path}..."
    if [ -d "$tsdb_path" ]; then
        # 检查是否有wal目录
        if [ -d "${tsdb_path}/wal" ]; then
            echo -e "${GREEN}✓ 有效 (包含wal目录)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ 存在但可能不是有效的TSDB路径${NC}"
            return 0
        fi
    else
        echo -e "${RED}✗ 不存在${NC}"
        return 1
    fi
}

# 主执行流程

# 1. 检查依赖
echo "1. 检查系统依赖..."
if ! command -v thanos &> /dev/null; then
    echo -e "${RED}错误: thanos命令未找到${NC}"
    echo "请先安装Thanos或确保其在PATH中"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo -e "${RED}错误: curl命令未找到${NC}"
    exit 1
fi

# 2. 检查Prometheus服务
echo ""
echo "2. 检查Prometheus服务..."
wait_for_service "$PROMETHEUS_URL" "Prometheus" || exit 1

# 3. 检查配置文件
echo ""
echo "3. 检查配置文件..."
check_config_file "$CONFIG_FILE" || exit 1

# 4. 检查TSDB路径
echo ""
echo "4. 检查TSDB路径..."
check_tsdb_path "$TSDB_PATH" || exit 1

# 5. 检查端口占用
echo ""
echo "5. 检查端口占用..."
for port in $SIDECAR_HTTP_PORT $SIDECAR_GRPC_PORT; do
    echo -n "检查端口 ${port}..."
    if netstat -tuln 2>/dev/null | grep ":$port " &> /dev/null; then
        echo -e "${RED}✗ 被占用${NC}"
        echo "请修改端口配置或停止占用该端口的服务"
        exit 1
    else
        echo -e "${GREEN}✓ 可用${NC}"
    fi
done

# 6. 启动Sidecar
echo ""
echo "6. 启动Thanos Sidecar..."

# 构建启动命令
sidecar_command="thanos sidecar \\
    --http-address=0.0.0.0:${SIDECAR_HTTP_PORT} \\
    --grpc-address=0.0.0.0:${SIDECAR_GRPC_PORT} \\
    --prometheus.url=${PROMETHEUS_URL} \\
    --tsdb.path=${TSDB_PATH} \\
    --objstore.config-file=${CONFIG_FILE} \\
    --log.level=${LOG_LEVEL} \\
    --reloader.config-file=/etc/prometheus/prometheus.yml \\
    --reloader.rule-dir=/etc/prometheus/rules/ \\
    --reloader.watch-interval=5s"

echo "启动命令:"
echo "$sidecar_command"
echo ""

# 执行启动命令
if [ "$1" = "--dry-run" ]; then
    echo "干燥运行模式，不实际启动服务"
    exit 0
fi

echo "启动Sidecar服务..."
eval $sidecar_command &
SIDECAR_PID=$!

# 等待Sidecar启动
echo "等待Sidecar服务启动..."
sleep 10

# 检查Sidecar健康状态
if check_service "http://localhost:${SIDECAR_HTTP_PORT}" "Thanos Sidecar"; then
    echo -e "${GREEN}✓ Sidecar启动成功 (PID: $SIDECAR_PID)${NC}"
    
    # 保存PID到文件
    echo $SIDECAR_PID > /tmp/thanos-sidecar.pid
    echo "PID已保存到 /tmp/thanos-sidecar.pid"
    
    # 显示服务信息
    echo ""
    echo "=== 服务信息 ==="
    echo "HTTP端点: http://localhost:${SIDECAR_HTTP_PORT}"
    echo "gRPC端点: localhost:${SIDECAR_GRPC_PORT}"
    echo "健康检查: http://localhost:${SIDECAR_HTTP_PORT}/-/healthy"
    echo "就绪检查: http://localhost:${SIDECAR_HTTP_PORT}/-/ready"
    echo "指标端点: http://localhost:${SIDECAR_HTTP_PORT}/metrics"
    
else
    echo -e "${RED}✗ Sidecar启动失败${NC}"
    
    # 尝试获取错误信息
    if ps -p $SIDECAR_PID > /dev/null 2>&1; then
        echo "Sidecar进程仍在运行，但健康检查失败"
        echo "请检查日志获取详细信息"
    else
        echo "Sidecar进程已退出"
    fi
    
    exit 1
fi

echo ""
echo -e "${GREEN}=== Sidecar启动完成 ===${NC}"

# 提示信息
echo ""
echo "使用以下命令停止Sidecar:"
echo "kill $(cat /tmp/thanos-sidecar.pid)"
echo ""
echo "查看Sidecar日志:"
echo "tail -f /var/log/thanos-sidecar.log  # 如果配置了日志文件"
echo ""
echo "监控Sidecar指标:"
echo "curl http://localhost:${SIDECAR_HTTP_PORT}/metrics | grep thanos_sidecar"