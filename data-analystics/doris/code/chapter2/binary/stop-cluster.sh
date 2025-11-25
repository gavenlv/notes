#!/bin/bash

# Doris集群停止脚本
# 用于停止Doris FE和BE节点

set -e

# 配置变量
DORIS_HOME="/opt/doris"
DORIS_USER="doris"

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
        log_error "Doris未安装"
        exit 1
    fi
    
    log_info "Doris安装检查通过"
}

# 停止FE节点
stop_fe() {
    log_info "停止FE节点..."
    
    # 检查FE是否在运行
    if ! pgrep -f "org.apache.doris.PaloFE" > /dev/null; then
        log_warn "FE节点未运行"
        return
    fi
    
    # 停止FE
    sudo -u "${DORIS_USER}" "${DORIS_HOME}/fe/bin/stop_fe.sh"
    
    # 等待FE停止
    log_info "等待FE节点停止..."
    local retry=0
    local max_retry=30
    while [[ $retry -lt $max_retry ]]; do
        if ! pgrep -f "org.apache.doris.PaloFE" > /dev/null; then
            log_info "FE节点已停止"
            return
        fi
        
        sleep 1
        ((retry++))
        echo -n "."
    done
    
    echo
    log_warn "FE节点停止超时，尝试强制终止"
    pkill -9 -f "org.apache.doris.PaloFE" || true
}

# 停止BE节点
stop_be() {
    log_info "停止BE节点..."
    
    # 检查BE是否在运行
    if ! pgrep -f "org.apache.doris.PaloBE" > /dev/null; then
        log_warn "BE节点未运行"
        return
    fi
    
    # 停止BE
    sudo -u "${DORIS_USER}" "${DORIS_HOME}/be/bin/stop_be.sh"
    
    # 等待BE停止
    log_info "等待BE节点停止..."
    local retry=0
    local max_retry=30
    while [[ $retry -lt $max_retry ]]; do
        if ! pgrep -f "org.apache.doris.PaloBE" > /dev/null; then
            log_info "BE节点已停止"
            return
        fi
        
        sleep 1
        ((retry++))
        echo -n "."
    done
    
    echo
    log_warn "BE节点停止超时，尝试强制终止"
    pkill -9 -f "org.apache.doris.PaloBE" || true
}

# 显示帮助信息
show_help() {
    echo "Doris集群停止脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --fe-only     只停止FE节点"
    echo "  --be-only     只停止BE节点"
    echo "  --help, -h    显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                # 停止完整集群"
    echo "  $0 --fe-only      # 只停止FE节点"
    echo "  $0 --be-only      # 只停止BE节点"
}

# 主函数
main() {
    local fe_only=false
    local be_only=false
    
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
    
    log_info "停止Doris集群..."
    
    # 检查安装状态
    check_installation
    
    # 停止节点
    if [[ "$be_only" != true ]]; then
        stop_fe
    fi
    
    if [[ "$fe_only" != true ]]; then
        stop_be
    fi
    
    log_info "Doris集群已停止!"
}

# 执行主函数
main "$@"