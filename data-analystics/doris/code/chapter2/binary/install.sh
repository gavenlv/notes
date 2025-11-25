#!/bin/bash

# Doris二进制安装脚本
# 使用方法: ./install.sh [fe|be|all]

set -e

# 配置变量
DORIS_VERSION="2.1.0"
DORIS_HOME="/opt/doris"
FE_HOME="${DORIS_HOME}/fe"
BE_HOME="${DORIS_HOME}/be"
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

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统环境
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法确定操作系统类型"
        exit 1
    fi
    
    source /etc/os-release
    log_info "操作系统: $NAME $VERSION"
    
    # 检查Java环境
    if ! command -v java &> /dev/null; then
        log_error "Java未安装，请先安装Java 1.8或更高版本"
        exit 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1-2)
    log_info "Java版本: $JAVA_VERSION"
    
    # 检查Python环境
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python未安装，请先安装Python 2.7或3.6+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python --version 2>&1 | head -n 1 | cut -d' ' -f2)
    log_info "Python版本: $PYTHON_VERSION"
}

# 下载Doris二进制包
download_doris() {
    log_info "下载Doris二进制包..."
    
    # 检查是否已下载
    if [[ -f "apache-doris-${DORIS_VERSION}-bin-x86_64.tar.gz" ]]; then
        log_info "Doris二进制包已存在，跳过下载"
        return
    fi
    
    # 下载FE二进制包
    log_info "下载FE二进制包..."
    wget "https://dist.apache.org/repos/dist/release/doris/${DORIS_VERSION}/apache-doris-${DORIS_VERSION}-bin-x86_64.tar.gz"
    
    if [[ $? -ne 0 ]]; then
        log_error "下载Doris二进制包失败"
        exit 1
    fi
    
    log_info "下载完成"
}

# 解压Doris二进制包
extract_doris() {
    log_info "解压Doris二进制包..."
    
    if [[ -d "${DORIS_HOME}" ]]; then
        log_warn "Doris安装目录已存在，将备份后删除"
        sudo mv "${DORIS_HOME}" "${DORIS_HOME}.bak.$(date +%Y%m%d%H%M%S)"
    fi
    
    # 创建安装目录
    sudo mkdir -p "${DORIS_HOME}"
    
    # 解压
    tar -zxvf "apache-doris-${DORIS_VERSION}-bin-x86_64.tar.gz" -C "${DORIS_HOME}" --strip-components=1
    
    if [[ $? -ne 0 ]]; then
        log_error "解压失败"
        exit 1
    fi
    
    log_info "解压完成"
}

# 创建Doris用户
create_user() {
    log_info "创建Doris用户..."
    
    if ! id "${DORIS_USER}" &>/dev/null; then
        sudo useradd -r -d "${DORIS_HOME}" -s /sbin/nologin "${DORIS_USER}"
        log_info "创建用户 ${DORIS_USER} 成功"
    else
        log_info "用户 ${DORIS_USER} 已存在"
    fi
    
    # 设置目录权限
    sudo chown -R "${DORIS_USER}:${DORIS_USER}" "${DORIS_HOME}"
    log_info "设置目录权限完成"
}

# 配置FE节点
configure_fe() {
    log_info "配置FE节点..."
    
    # 创建必要目录
    sudo -u "${DORIS_USER}" mkdir -p "${FE_HOME}/doris-meta" "${FE_HOME}/log"
    
    # 复制配置文件
    if [[ -f "fe.conf" ]]; then
        cp fe.conf "${FE_HOME}/conf/fe.conf"
        log_info "复制FE配置文件完成"
    else
        log_warn "未找到fe.conf配置文件，使用默认配置"
    fi
    
    # 设置环境变量
    cat >> /etc/profile.d/doris.sh << EOF
export DORIS_HOME=${DORIS_HOME}
export PATH=\$PATH:\${DORIS_HOME}/fe/bin:\${DORIS_HOME}/be/bin
EOF
    
    log_info "FE节点配置完成"
}

# 配置BE节点
configure_be() {
    log_info "配置BE节点..."
    
    # 创建必要目录
    sudo -u "${DORIS_USER}" mkdir -p "${BE_HOME}/storage" "${BE_HOME}/log"
    
    # 复制配置文件
    if [[ -f "be.conf" ]]; then
        cp be.conf "${BE_HOME}/conf/be.conf"
        log_info "复制BE配置文件完成"
    else
        log_warn "未找到be.conf配置文件，使用默认配置"
    fi
    
    log_info "BE节点配置完成"
}

# 创建启动脚本
create_start_scripts() {
    log_info "创建启动脚本..."
    
    # FE启动脚本
    cat > "${DORIS_HOME}/start-fe.sh" << EOF
#!/bin/bash
# Doris FE启动脚本

source /etc/profile.d/doris.sh

echo "Starting Doris FE..."
su - ${DORIS_USER} -c "\${DORIS_HOME}/fe/bin/start_fe.sh --daemon"

echo "Doris FE started successfully!"
EOF
    
    # BE启动脚本
    cat > "${DORIS_HOME}/start-be.sh" << EOF
#!/bin/bash
# Doris BE启动脚本

source /etc/profile.d/doris.sh

echo "Starting Doris BE..."
su - ${DORIS_USER} -c "\${DORIS_HOME}/be/bin/start_be.sh --daemon"

echo "Doris BE started successfully!"
EOF
    
    # 停止脚本
    cat > "${DORIS_HOME}/stop-all.sh" << EOF
#!/bin/bash
# Doris停止脚本

source /etc/profile.d/doris.sh

echo "Stopping Doris BE..."
su - ${DORIS_USER} -c "\${DORIS_HOME}/be/bin/stop_be.sh"

echo "Stopping Doris FE..."
su - ${DORIS_USER} -c "\${DORIS_HOME}/fe/bin/stop_fe.sh"

echo "Doris stopped successfully!"
EOF
    
    # 设置执行权限
    chmod +x "${DORIS_HOME}/start-fe.sh" "${DORIS_HOME}/start-be.sh" "${DORIS_HOME}/stop-all.sh"
    
    log_info "启动脚本创建完成"
}

# 安装FE节点
install_fe() {
    log_info "安装FE节点..."
    configure_fe
    create_start_scripts
    log_info "FE节点安装完成"
}

# 安装BE节点
install_be() {
    log_info "安装BE节点..."
    configure_be
    create_start_scripts
    log_info "BE节点安装完成"
}

# 安装所有节点
install_all() {
    log_info "安装所有节点..."
    configure_fe
    configure_be
    create_start_scripts
    log_info "所有节点安装完成"
}

# 显示帮助信息
show_help() {
    echo "Doris二进制安装脚本"
    echo ""
    echo "使用方法: $0 [fe|be|all]"
    echo ""
    echo "选项:"
    echo "  fe    只安装FE节点"
    echo "  be    只安装BE节点"
    echo "  all   安装所有节点(默认)"
    echo ""
    echo "示例:"
    echo "  $0 fe     # 安装FE节点"
    echo "  $0 be     # 安装BE节点"
    echo "  $0 all    # 安装所有节点"
    echo "  $0        # 安装所有节点"
}

# 主函数
main() {
    local component=${1:-all}
    
    log_info "开始安装Doris ${DORIS_VERSION}..."
    
    check_root
    check_system
    download_doris
    extract_doris
    create_user
    
    case "$component" in
        fe)
            install_fe
            ;;
        be)
            install_be
            ;;
        all)
            install_all
            ;;
        help|--help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "未知选项: $component"
            show_help
            exit 1
            ;;
    esac
    
    log_info "Doris安装完成!"
    log_info "使用以下命令启动Doris:"
    log_info "  启动FE: ${DORIS_HOME}/start-fe.sh"
    log_info "  启动BE: ${DORIS_HOME}/start-be.sh"
    log_info "  停止所有: ${DORIS_HOME}/stop-all.sh"
    log_info ""
    log_info "启动后使用MySQL客户端连接:"
    log_info "  mysql -h <FE_IP> -P 9030 -uroot"
}

# 执行主函数
main "$@"