#!/bin/bash

# Flask-AppBuilder 应用部署脚本

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# 检查是否以root权限运行
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warn "不建议以root用户运行此脚本"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查依赖
check_dependencies() {
    log "检查系统依赖..."
    
    local deps=("python3" "pip3" "git" "docker" "docker-compose")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        log_error "请先安装这些依赖再运行此脚本"
        exit 1
    fi
    
    log "所有依赖检查通过"
}

# 设置环境变量
setup_environment() {
    log "设置环境变量..."
    
    # 创建环境变量文件（如果不存在）
    if [ ! -f ".env" ]; then
        log_warn ".env 文件不存在，将创建示例文件"
        cat > .env << EOF
# 应用配置
SECRET_KEY=your-production-secret-key-change-this
FLASK_CONFIG=production

# 数据库配置
DATABASE_URL=postgresql://flaskuser:flaskpass@localhost:5432/flaskdb

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/flask-appbuilder/app.log
EOF
        log "已创建 .env 示例文件，请根据实际情况修改"
    fi
    
    # 加载环境变量
    if [ -f ".env" ]; then
        export $(cat .env | xargs)
    fi
}

# 构建应用
build_app() {
    log "构建应用..."
    
    # 安装Python依赖
    log "安装Python依赖..."
    pip3 install -r requirements.txt
    
    # 数据库迁移
    log "运行数据库迁移..."
    python3 run.py db upgrade
    
    # 初始化应用
    log "初始化应用..."
    python3 run.py init
    
    log "应用构建完成"
}

# 构建Docker镜像
build_docker() {
    log "构建Docker镜像..."
    
    docker-compose build
    
    log "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log "启动服务..."
    
    docker-compose up -d
    
    # 等待服务启动
    log "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log "服务启动成功"
    else
        log_error "服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 停止服务
stop_services() {
    log "停止服务..."
    
    docker-compose down
    
    log "服务已停止"
}

# 重启服务
restart_services() {
    log "重启服务..."
    
    docker-compose restart
    
    log "服务已重启"
}

# 查看日志
view_logs() {
    log "查看服务日志..."
    
    docker-compose logs -f
}

# 备份数据库
backup_database() {
    log "备份数据库..."
    
    local backup_dir="./backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/backup_$timestamp.sql"
    
    # 创建备份目录
    mkdir -p "$backup_dir"
    
    # 执行备份
    docker-compose exec db pg_dump -U flaskuser flaskdb > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log "数据库备份成功: $backup_file"
    else
        log_error "数据库备份失败"
        exit 1
    fi
}

# 恢复数据库
restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "请提供备份文件路径"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log "恢复数据库: $backup_file"
    
    # 停止应用服务
    docker-compose stop web
    
    # 恢复数据库
    docker-compose exec -T db psql -U flaskuser flaskdb < "$backup_file"
    
    if [ $? -eq 0 ]; then
        log "数据库恢复成功"
    else
        log_error "数据库恢复失败"
        exit 1
    fi
    
    # 重启应用服务
    docker-compose start web
}

# 显示服务状态
show_status() {
    log "服务状态:"
    docker-compose ps
}

# 显示使用帮助
show_help() {
    echo "Flask-AppBuilder 应用部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build        构建应用和Docker镜像"
    echo "  start        启动服务"
    echo "  stop         停止服务"
    echo "  restart      重启服务"
    echo "  status       显示服务状态"
    echo "  logs         查看服务日志"
    echo "  backup       备份数据库"
    echo "  restore <file> 从备份文件恢复数据库"
    echo "  help         显示此帮助信息"
    echo ""
}

# 主函数
main() {
    case "$1" in
        build)
            check_dependencies
            setup_environment
            build_app
            build_docker
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            view_logs
            ;;
        backup)
            backup_database
            ;;
        restore)
            restore_database "$2"
            ;;
        help)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"