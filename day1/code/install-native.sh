#!/bin/bash

# ClickHouse 原生安装脚本
# 支持 Ubuntu/Debian, CentOS/RHEL, macOS
# 作者: ClickHouse学习教程
# 版本: 1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
CLICKHOUSE_VERSION=${CLICKHOUSE_VERSION:-latest}
INSTALL_CLIENT=${INSTALL_CLIENT:-true}
INSTALL_SERVER=${INSTALL_SERVER:-true}
START_SERVICE=${START_SERVICE:-true}
CREATE_USER=${CREATE_USER:-true}

echo -e "${BLUE}🚀 ClickHouse 原生安装脚本${NC}"
echo "================================================"

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            if grep -q "Ubuntu" /etc/os-release; then
                DISTRO="ubuntu"
            else
                DISTRO="debian"
            fi
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            if grep -q "CentOS" /etc/redhat-release; then
                DISTRO="centos"
            elif grep -q "Red Hat" /etc/redhat-release; then
                DISTRO="rhel"
            elif grep -q "Fedora" /etc/redhat-release; then
                DISTRO="fedora"
            else
                DISTRO="redhat"
            fi
        else
            echo -e "${RED}❌ 不支持的Linux发行版${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        echo -e "${RED}❌ 不支持的操作系统: $OSTYPE${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 检测到操作系统: $DISTRO${NC}"
}

# 检查系统要求
check_requirements() {
    echo "🔍 检查系统要求..."
    
    # 检查内存
    if [[ "$OS" == "linux-gnu" ]]; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    elif [[ "$OS" == "macos" ]]; then
        MEMORY_GB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    fi
    
    if [ "$MEMORY_GB" -lt 2 ]; then
        echo -e "${YELLOW}⚠️  警告: 系统内存少于2GB，可能影响性能${NC}"
    else
        echo -e "${GREEN}✅ 内存检查通过: ${MEMORY_GB}GB${NC}"
    fi
    
    # 检查磁盘空间
    DISK_FREE=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
    if [ "$DISK_FREE" -lt 5 ]; then
        echo -e "${YELLOW}⚠️  警告: 可用磁盘空间少于5GB${NC}"
    else
        echo -e "${GREEN}✅ 磁盘空间检查通过: ${DISK_FREE}GB可用${NC}"
    fi
    
    # 检查架构
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" && "$ARCH" != "aarch64" ]]; then
        echo -e "${RED}❌ 不支持的架构: $ARCH${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 架构检查通过: $ARCH${NC}"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装依赖包..."
    
    case $DISTRO in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y \
                apt-transport-https \
                ca-certificates \
                dirmngr \
                gnupg \
                curl \
                wget
            ;;
        centos|rhel)
            sudo yum install -y \
                yum-utils \
                curl \
                wget \
                gnupg2
            ;;
        fedora)
            sudo dnf install -y \
                curl \
                wget \
                gnupg2
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                echo "安装Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            ;;
    esac
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 添加ClickHouse仓库
add_repository() {
    echo "📋 添加ClickHouse官方仓库..."
    
    case $DISTRO in
        ubuntu|debian)
            # 添加GPG密钥
            sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754
            
            # 添加仓库
            echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
            
            # 更新包列表
            sudo apt-get update
            ;;
        centos|rhel|fedora)
            # 添加仓库配置
            cat << EOF | sudo tee /etc/yum.repos.d/clickhouse.repo
[clickhouse-stable]
name=ClickHouse - Stable Repository
baseurl=https://packages.clickhouse.com/rpm/stable/
gpgcheck=1
enabled=1
gpgkey=https://packages.clickhouse.com/rpm/stable/repodata/repomd.xml.key
EOF
            ;;
        macos)
            # Homebrew会自动处理仓库
            echo "macOS使用Homebrew仓库"
            ;;
    esac
    
    echo -e "${GREEN}✅ 仓库添加完成${NC}"
}

# 安装ClickHouse
install_clickhouse() {
    echo "⬇️  安装ClickHouse..."
    
    case $DISTRO in
        ubuntu|debian)
            if [ "$INSTALL_SERVER" = true ]; then
                sudo apt-get install -y clickhouse-server
            fi
            if [ "$INSTALL_CLIENT" = true ]; then
                sudo apt-get install -y clickhouse-client
            fi
            ;;
        centos|rhel|fedora)
            if [ "$INSTALL_SERVER" = true ]; then
                sudo yum install -y clickhouse-server
            fi
            if [ "$INSTALL_CLIENT" = true ]; then
                sudo yum install -y clickhouse-client
            fi
            ;;
        macos)
            brew install clickhouse
            ;;
    esac
    
    echo -e "${GREEN}✅ ClickHouse安装完成${NC}"
}

# 配置ClickHouse
configure_clickhouse() {
    echo "⚙️  配置ClickHouse..."
    
    # 获取配置文件路径
    case $DISTRO in
        ubuntu|debian|centos|rhel|fedora)
            CONFIG_DIR="/etc/clickhouse-server"
            DATA_DIR="/var/lib/clickhouse"
            LOG_DIR="/var/log/clickhouse-server"
            ;;
        macos)
            if command -v brew &> /dev/null; then
                BREW_PREFIX=$(brew --prefix)
                CONFIG_DIR="$BREW_PREFIX/etc/clickhouse-server"
                DATA_DIR="$BREW_PREFIX/var/lib/clickhouse"
                LOG_DIR="$BREW_PREFIX/var/log/clickhouse-server"
            else
                CONFIG_DIR="/usr/local/etc/clickhouse-server"
                DATA_DIR="/usr/local/var/lib/clickhouse"
                LOG_DIR="/usr/local/var/log/clickhouse-server"
            fi
            ;;
    esac
    
    # 创建必要目录
    sudo mkdir -p "$DATA_DIR" "$LOG_DIR"
    
    # 复制配置模板（如果存在）
    if [ -f "configs/single/config.xml" ]; then
        echo "使用自定义配置模板..."
        sudo cp configs/single/config.xml "$CONFIG_DIR/"
        sudo cp configs/single/users.xml "$CONFIG_DIR/"
        echo -e "${GREEN}✅ 配置文件已更新${NC}"
    else
        echo "使用默认配置..."
    fi
    
    # 设置文件权限
    if [[ "$DISTRO" != "macos" ]]; then
        sudo chown -R clickhouse:clickhouse "$DATA_DIR" "$LOG_DIR" 2>/dev/null || true
        sudo chmod 755 "$CONFIG_DIR"
        sudo chmod 644 "$CONFIG_DIR"/*.xml 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ 配置完成${NC}"
    echo "配置目录: $CONFIG_DIR"
    echo "数据目录: $DATA_DIR"
    echo "日志目录: $LOG_DIR"
}

# 创建用户和设置权限
setup_user() {
    if [ "$CREATE_USER" = true ] && [[ "$DISTRO" != "macos" ]]; then
        echo "👤 设置用户和权限..."
        
        # 创建clickhouse用户（如果不存在）
        if ! id "clickhouse" &>/dev/null; then
            sudo useradd -r -s /bin/false clickhouse
            echo -e "${GREEN}✅ 创建clickhouse用户${NC}"
        fi
        
        # 设置目录权限
        sudo chown -R clickhouse:clickhouse /var/lib/clickhouse /var/log/clickhouse-server 2>/dev/null || true
        
        echo -e "${GREEN}✅ 用户权限设置完成${NC}"
    fi
}

# 启动服务
start_service() {
    if [ "$START_SERVICE" = true ]; then
        echo "🚀 启动ClickHouse服务..."
        
        case $DISTRO in
            ubuntu|debian|centos|rhel|fedora)
                # 启动并启用服务
                sudo systemctl start clickhouse-server
                sudo systemctl enable clickhouse-server
                
                # 检查服务状态
                if sudo systemctl is-active --quiet clickhouse-server; then
                    echo -e "${GREEN}✅ ClickHouse服务启动成功${NC}"
                else
                    echo -e "${RED}❌ ClickHouse服务启动失败${NC}"
                    sudo systemctl status clickhouse-server
                    return 1
                fi
                ;;
            macos)
                # 使用Homebrew服务管理
                if command -v brew &> /dev/null; then
                    brew services start clickhouse
                    echo -e "${GREEN}✅ ClickHouse服务启动成功${NC}"
                else
                    echo "手动启动ClickHouse服务..."
                    clickhouse-server --config-file=/usr/local/etc/clickhouse-server/config.xml &
                fi
                ;;
        esac
    fi
}

# 测试安装
test_installation() {
    echo "🧪 测试安装..."
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 5
    
    # 测试连接
    for i in {1..30}; do
        if clickhouse-client --query "SELECT 1" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 连接测试成功${NC}"
            break
        fi
        
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ 连接测试失败${NC}"
            return 1
        fi
        
        sleep 2
    done
    
    # 显示版本信息
    VERSION=$(clickhouse-client --query "SELECT version()")
    echo "ClickHouse版本: $VERSION"
    
    # 创建测试数据库
    clickhouse-client --query "CREATE DATABASE IF NOT EXISTS test_install"
    clickhouse-client --query "CREATE TABLE test_install.test (id UInt32, name String) ENGINE = Memory"
    clickhouse-client --query "INSERT INTO test_install.test VALUES (1, 'Hello ClickHouse')"
    
    RESULT=$(clickhouse-client --query "SELECT * FROM test_install.test")
    echo "测试查询结果: $RESULT"
    
    # 清理测试数据
    clickhouse-client --query "DROP DATABASE test_install"
    
    echo -e "${GREEN}✅ 安装测试完成${NC}"
}

# 显示安装信息
show_installation_info() {
    echo ""
    echo "🎉 ClickHouse安装完成！"
    echo ""
    echo "📋 安装信息:"
    echo "   操作系统: $DISTRO"
    echo "   架构: $ARCH"
    echo "   版本: $(clickhouse-client --query "SELECT version()" 2>/dev/null || echo "未知")"
    echo ""
    echo "📁 重要路径:"
    case $DISTRO in
        ubuntu|debian|centos|rhel|fedora)
            echo "   配置文件: /etc/clickhouse-server/"
            echo "   数据目录: /var/lib/clickhouse/"
            echo "   日志目录: /var/log/clickhouse-server/"
            ;;
        macos)
            if command -v brew &> /dev/null; then
                BREW_PREFIX=$(brew --prefix)
                echo "   配置文件: $BREW_PREFIX/etc/clickhouse-server/"
                echo "   数据目录: $BREW_PREFIX/var/lib/clickhouse/"
                echo "   日志目录: $BREW_PREFIX/var/log/clickhouse-server/"
            fi
            ;;
    esac
    echo ""
    echo "🔧 常用命令:"
    echo "   # 连接ClickHouse"
    echo "   clickhouse-client"
    echo ""
    echo "   # 查看服务状态"
    if [[ "$DISTRO" == "macos" ]]; then
        echo "   brew services list | grep clickhouse"
    else
        echo "   sudo systemctl status clickhouse-server"
    fi
    echo ""
    echo "   # 重启服务"
    if [[ "$DISTRO" == "macos" ]]; then
        echo "   brew services restart clickhouse"
    else
        echo "   sudo systemctl restart clickhouse-server"
    fi
    echo ""
    echo "   # 查看日志"
    case $DISTRO in
        ubuntu|debian|centos|rhel|fedora)
            echo "   sudo tail -f /var/log/clickhouse-server/clickhouse-server.log"
            ;;
        macos)
            if command -v brew &> /dev/null; then
                echo "   tail -f $(brew --prefix)/var/log/clickhouse-server/clickhouse-server.log"
            fi
            ;;
    esac
    echo ""
    echo "📚 下一步:"
    echo "   1. 阅读 notes/week1/day2-installation.md"
    echo "   2. 运行 code/setup/check-config.sh 检查配置"
    echo "   3. 运行 code/examples/basic-queries.sql 学习基础查询"
}

# 显示帮助信息
show_help() {
    echo "ClickHouse 原生安装脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --version VERSION     指定ClickHouse版本 (默认: latest)"
    echo "  --no-server          不安装服务器组件"
    echo "  --no-client          不安装客户端组件"
    echo "  --no-start           安装后不启动服务"
    echo "  --no-user            不创建clickhouse用户"
    echo "  --help               显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  CLICKHOUSE_VERSION   ClickHouse版本"
    echo "  INSTALL_SERVER       是否安装服务器 (true/false)"
    echo "  INSTALL_CLIENT       是否安装客户端 (true/false)"
    echo "  START_SERVICE        是否启动服务 (true/false)"
    echo "  CREATE_USER          是否创建用户 (true/false)"
    echo ""
    echo "示例:"
    echo "  $0                           # 标准安装"
    echo "  $0 --version 23.8           # 安装指定版本"
    echo "  $0 --no-server              # 只安装客户端"
    echo "  INSTALL_SERVER=false $0     # 使用环境变量"
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                CLICKHOUSE_VERSION="$2"
                shift 2
                ;;
            --no-server)
                INSTALL_SERVER=false
                shift
                ;;
            --no-client)
                INSTALL_CLIENT=false
                shift
                ;;
            --no-start)
                START_SERVICE=false
                shift
                ;;
            --no-user)
                CREATE_USER=false
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}错误: 未知参数 '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查权限
    if [[ $EUID -eq 0 && "$DISTRO" != "macos" ]]; then
        echo -e "${RED}❌ 请不要使用root用户运行此脚本${NC}"
        exit 1
    fi
    
    # 执行安装流程
    detect_os
    check_requirements
    install_dependencies
    add_repository
    install_clickhouse
    setup_user
    configure_clickhouse
    start_service
    test_installation
    show_installation_info
    
    echo ""
    echo -e "${GREEN}🎊 安装完成！祝学习愉快！${NC}"
}

# 错误处理
trap 'echo -e "${RED}❌ 安装过程中出现错误${NC}"; exit 1' ERR

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 