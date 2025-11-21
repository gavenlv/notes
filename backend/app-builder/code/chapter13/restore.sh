#!/bin/bash

# Flask-AppBuilder 应用恢复脚本

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

# 默认配置
BACKUP_DIR="./backups"

# 显示使用帮助
show_help() {
    echo "Flask-AppBuilder 应用恢复脚本"
    echo ""
    echo "用法: $0 [选项] <备份名称>"
    echo ""
    echo "选项:"
    echo "  -d, --dir DIR        指定备份目录 (默认: ./backups)"
    echo "  --no-db              不恢复数据库"
    echo "  --no-files           不恢复应用文件"
    echo "  -y, --yes            自动确认恢复操作"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "参数:"
    echo "  <备份名称>           要恢复的备份名称"
    echo ""
    echo "示例:"
    echo "  $0 flask_appbuilder_backup_20230101_120000"
    echo "  $0 -d /path/to/backups --no-db backup_name"
    echo ""
}

# 检查依赖
check_dependencies() {
    log "检查恢复依赖..."
    
    local deps=("docker" "docker-compose" "tar" "gzip" "jq")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        exit 1
    fi
    
    log "恢复依赖检查通过"
}

# 验证备份
verify_backup() {
    local backup_name=$1
    
    if [ -z "$backup_name" ]; then
        log_error "请提供备份名称"
        exit 1
    fi
    
    local metadata_file="$BACKUP_DIR/${backup_name}_metadata.json"
    
    if [ ! -f "$metadata_file" ]; then
        log_error "备份元数据文件不存在: $metadata_file"
        exit 1
    fi
    
    log "找到备份: $backup_name"
    
    # 显示备份信息
    local backup_time=$(jq -r '.timestamp' "$metadata_file")
    local include_db=$(jq -r '.include_database' "$metadata_file")
    local include_files=$(jq -r '.include_files' "$metadata_file")
    
    log "备份时间: $backup_time"
    log "包含数据库: $include_db"
    log "包含应用文件: $include_files"
    
    # 检查备份文件是否存在
    local files_list=$(jq -r '.files[]' "$metadata_file")
    for file in $files_list; do
        if [ ! -f "$BACKUP_DIR/$file" ]; then
            log_error "备份文件不存在: $file"
            exit 1
        fi
    done
    
    log "备份验证通过"
}

# 停止服务
stop_services() {
    log "停止应用服务..."
    
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        log "服务已停止"
    else
        log_warn "服务未运行"
    fi
}

# 恢复数据库
restore_database() {
    local backup_name=$1
    
    log "开始恢复数据库..."
    
    local db_backup_file="$BACKUP_DIR/${backup_name}_database.sql"
    
    # 检查是否是压缩文件
    if [ -f "${db_backup_file}.gz" ]; then
        db_backup_file="${db_backup_file}.gz"
        log "检测到压缩的数据库备份文件"
    elif [ ! -f "$db_backup_file" ]; then
        log_error "数据库备份文件不存在: $db_backup_file"
        exit 1
    fi
    
    # 启动数据库服务
    log "启动数据库服务..."
    docker-compose up -d db
    
    # 等待数据库启动
    log "等待数据库启动..."
    sleep 10
    
    # 恢复数据库
    if [[ "$db_backup_file" == *.gz ]]; then
        # 解压并恢复
        gunzip -c "$db_backup_file" | docker-compose exec -T db psql -U flaskuser flaskdb
    else
        # 直接恢复
        docker-compose exec -T db psql -U flaskuser flaskdb < "$db_backup_file"
    fi
    
    if [ $? -eq 0 ]; then
        log "数据库恢复成功"
    else
        log_error "数据库恢复失败"
        exit 1
    fi
}

# 恢复应用文件
restore_app_files() {
    local backup_name=$1
    
    log "开始恢复应用文件..."
    
    local files_backup_file="$BACKUP_DIR/${backup_name}_files.tar.gz"
    
    if [ ! -f "$files_backup_file" ]; then
        log_error "应用文件备份不存在: $files_backup_file"
        exit 1
    fi
    
    # 创建临时目录用于解压
    local temp_dir="/tmp/flask_restore_$$"
    mkdir -p "$temp_dir"
    
    # 解压备份文件到临时目录
    if ! tar -xzf "$files_backup_file" -C "$temp_dir"; then
        log_error "解压应用文件备份失败"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    # 恢复文件
    log "恢复应用文件..."
    cp -rf "$temp_dir"/* ./
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    log "应用文件恢复成功"
}

# 启动服务
start_services() {
    log "启动应用服务..."
    
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

# 确认操作
confirm_operation() {
    if [ "$AUTO_CONFIRM" = "true" ]; then
        return 0
    fi
    
    echo ""
    log_warn "警告: 此操作将覆盖当前的应用数据！"
    read -p "是否继续恢复操作? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "操作已取消"
        exit 0
    fi
}

# 主函数
main() {
    # 默认选项
    INCLUDE_DB=true
    INCLUDE_FILES=true
    AUTO_CONFIRM=false
    BACKUP_NAME=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            --no-db)
                INCLUDE_DB=false
                shift
                ;;
            --no-files)
                INCLUDE_FILES=false
                shift
                ;;
            -y|--yes)
                AUTO_CONFIRM=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                if [ -z "$BACKUP_NAME" ]; then
                    BACKUP_NAME="$1"
                else
                    log_error "多余的参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查必需参数
    if [ -z "$BACKUP_NAME" ]; then
        log_error "请提供要恢复的备份名称"
        show_help
        exit 1
    fi
    
    # 如果既不恢复数据库也不恢复文件，则退出
    if [ "$INCLUDE_DB" = "false" ] && [ "$INCLUDE_FILES" = "false" ]; then
        log_warn "未选择任何恢复项，脚本将退出"
        exit 0
    fi
    
    log "开始执行Flask-AppBuilder应用恢复"
    log "备份名称: $BACKUP_NAME"
    log "备份目录: $BACKUP_DIR"
    
    # 执行恢复步骤
    check_dependencies
    verify_backup "$BACKUP_NAME"
    confirm_operation
    
    # 停止服务
    stop_services
    
    # 恢复选定的项
    if [ "$INCLUDE_DB" = "true" ]; then
        restore_database "$BACKUP_NAME"
    fi
    
    if [ "$INCLUDE_FILES" = "true" ]; then
        restore_app_files "$BACKUP_NAME"
    fi
    
    # 启动服务
    start_services
    
    log "恢复完成: $BACKUP_NAME"
}

# 运行主函数
main "$@"