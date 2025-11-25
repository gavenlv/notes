#!/bin/bash

# Doris集群启动脚本
# 用于启动Doris FE和BE节点，并添加BE到集群

set -e

# 配置变量
DORIS_HOME="/opt/doris"
DORIS_USER="doris"
FE_HOST="127.0.0.1"  # FE主机地址，根据实际情况修改
BE_HOST="127.0.0.1"  # BE主机地址，根据实际情况修改
FE_PORT="9030"       # FE MySQL协议端口
BE_HEARTBEAT_PORT="9050"  # BE心跳端口

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Doris是否已安装
check_installation() {
    log_info "检查Doris安装状态..."
    
    if [[ ! -d "${DORIS_HOME}" ]]; then
        log_error "Doris未安装，请先运行install.sh进行安装"
        exit 1
    fi
    
    if [[ ! -f "${DORIS_HOME}/fe/bin/start_fe.sh" ]]; then
        log_error "FE节点未安装"
        exit 1
    fi
    
    if [[ ! -f "${DORIS_HOME}/be/bin/start_be.sh" ]]; then
        log_error "BE节点未安装"
        exit 1
    fi
    
    log_info "Doris安装检查通过"
}

# 检查Java环境
check_java() {
    log_info "检查Java环境..."
    
    if ! command -v java &> /dev/null; then
        log_error "Java未安装或未配置到PATH中"
        exit 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    log_info "Java版本: $JAVA_VERSION"
}

# 检查端口占用
check_ports() {
    log_info "检查端口占用情况..."
    
    # 检查FE端口
    if netstat -tlnp 2>/dev/null | grep -q ":$FE_PORT "; then
        log_warn "FE端口 $FE_PORT 已被占用"
        read -p "是否继续? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 检查BE端口
    if netstat -tlnp 2>/dev/null | grep -q ":$BE_HEARTBEAT_PORT "; then
        log_warn "BE心跳端口 $BE_HEARTBEAT_PORT 已被占用"
        read -p "是否继续? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "端口检查完成"
}

# 启动FE节点
start_fe() {
    log_info "启动FE节点..."
    
    # 检查FE是否已运行
    if pgrep -f "org.apache.doris.PaloFE" > /dev/null; then
        log_warn "FE节点已在运行"
        return
    fi
    
    # 启动FE
    sudo -u "${DORIS_USER}" "${DORIS_HOME}/fe/bin/start_fe.sh" --daemon
    
    # 等待FE启动
    log_info "等待FE节点启动..."
    local retry=0
    local max_retry=30
    while [[ $retry -lt $max_retry ]]; do
        if netstat -tlnp 2>/dev/null | grep -q ":$FE_PORT "; then
            log_info "FE节点启动成功"
            return
        fi
        
        sleep 2
        ((retry++))
        echo -n "."
    done
    
    echo
    log_error "FE节点启动超时"
    exit 1
}

# 启动BE节点
start_be() {
    log_info "启动BE节点..."
    
    # 检查BE是否已运行
    if pgrep -f "org.apache.doris.PaloBE" > /dev/null; then
        log_warn "BE节点已在运行"
        return
    fi
    
    # 启动BE
    sudo -u "${DORIS_USER}" "${DORIS_HOME}/be/bin/start_be.sh" --daemon
    
    # 等待BE启动
    log_info "等待BE节点启动..."
    local retry=0
    local max_retry=30
    while [[ $retry -lt $max_retry ]]; do
        if netstat -tlnp 2>/dev/null | grep -q ":$BE_HEARTBEAT_PORT "; then
            log_info "BE节点启动成功"
            return
        fi
        
        sleep 2
        ((retry++))
        echo -n "."
    done
    
    echo
    log_error "BE节点启动超时"
    exit 1
}

# 添加BE到集群
add_be_to_cluster() {
    log_info "添加BE节点到集群..."
    
    # 等待FE完全就绪
    log_info "等待FE完全就绪..."
    local retry=0
    local max_retry=30
    while [[ $retry -lt $max_retry ]]; do
        if mysql -h "$FE_HOST" -P "$FE_PORT" -uroot -e "SELECT 1" &>/dev/null; then
            break
        fi
        
        sleep 2
        ((retry++))
        echo -n "."
    done
    
    echo
    
    if [[ $retry -eq $max_retry ]]; then
        log_error "FE节点未就绪，无法添加BE节点"
        exit 1
    fi
    
    # 检查BE是否已在集群中
    local be_count=$(mysql -h "$FE_HOST" -P "$FE_PORT" -uroot -sN -e "SELECT COUNT(*) FROM information_schema.backends WHERE host = '$BE_HOST' AND heartbeat_port = $BE_HEARTBEAT_PORT;" 2>/dev/null || echo "0")
    
    if [[ $be_count -gt 0 ]]; then
        log_warn "BE节点已在集群中"
        return
    fi
    
    # 添加BE节点
    mysql -h "$FE_HOST" -P "$FE_PORT" -uroot -e "ALTER SYSTEM ADD BACKEND '$BE_HOST:$BE_HEARTBEAT_PORT';" 2>/dev/null
    
    if [[ $? -eq 0 ]]; then
        log_info "BE节点添加成功"
    else
        log_error "BE节点添加失败"
        exit 1
    fi
    
    # 等待BE状态变为alive
    log_info "等待BE节点状态变为alive..."
    retry=0
    max_retry=60
    while [[ $retry -lt $max_retry ]]; do
        local be_status=$(mysql -h "$FE_HOST" -P "$FE_PORT" -uroot -sN -e "SELECT alive FROM information_schema.backends WHERE host = '$BE_HOST' AND heartbeat_port = $BE_HEARTBEAT_PORT;" 2>/dev/null || echo "false")
        
        if [[ "$be_status" == "true" ]]; then
            log_info "BE节点状态为alive，集群启动完成"
            return
        fi
        
        sleep 2
        ((retry++))
        echo -n "."
    done
    
    echo
    log_warn "BE节点状态检查超时，但集群可能仍在启动中"
}

# 显示集群状态
show_cluster_status() {
    log_info "集群状态:"
    echo ""
    
    echo "FE节点:"
    mysql -h "$FE_HOST" -P "$FE_PORT" -uroot -e "SHOW FRONTENDS;" 2>/dev/null || log_error "无法获取FE状态"
    echo ""
    
    echo "BE节点:"
    mysql -h "$FE_HOST" -P "$FE_PORT" -uroot -e "SHOW BACKENDS;" 2>/dev/null || log_error "无法获取BE状态"
    echo ""
}

# 显示连接信息
show_connection_info() {
    log_info "连接信息:"
    echo "  MySQL协议连接: mysql -h $FE_HOST -P $FE_PORT -uroot"
    echo "  Web UI: http://$FE_HOST:8030"
    echo ""
}

# 显示帮助信息
show_help() {
    echo "Doris集群启动脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --fe-only     只启动FE节点"
    echo "  --be-only     只启动BE节点"
    echo "  --no-add-be   启动但不添加BE到集群"
    echo "  --help, -h    显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                # 启动完整集群"
    echo "  $0 --fe-only      # 只启动FE节点"
    echo "  $0 --be-only      # 只启动BE节点"
    echo "  $0 --no-add-be    # 启动但不添加BE到集群"
}

# 主函数
main() {
    local fe_only=false
    local be_only=false
    local no_add_be=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --fe-only)
                fe_only=true
                shift
                ;;
            --be-only)
                be_only=true
                shift
                ;;
            --no-add-be)
                no_add_be=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查参数组合
    if [[ "$fe_only" == true && "$be_only" == true ]]; then
        log_error "--fe-only和--be-only不能同时使用"
        exit 1
    fi
    
    log_info "启动Doris集群..."
    
    # 检查安装状态
    check_installation
    
    # 检查Java环境
    check_java
    
    # 检查端口占用
    check_ports
    
    # 启动节点
    if [[ "$be_only" != true ]]; then
        start_fe
    fi
    
    if [[ "$fe_only" != true ]]; then
        start_be
    fi
    
    # 添加BE到集群
    if [[ "$fe_only" != true && "$be_only" != true && "$no_add_be" != true ]]; then
        add_be_to_cluster
    fi
    
    # 显示集群状态
    if [[ "$fe_only" != true && "$be_only" != true ]]; then
        show_cluster_status
    fi
    
    # 显示连接信息
    show_connection_info
    
    log_info "Doris集群启动完成!"
}

# 执行主函数
main "$@"