#!/bin/bash

# Flask-AppBuilder 应用备份脚本

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
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="flask_appbuilder_backup_$TIMESTAMP"

# 显示使用帮助
show_help() {
    echo "Flask-AppBuilder 应用备份脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --dir DIR        指定备份目录 (默认: ./backups)"
    echo "  -n, --name NAME      指定备份名称 (默认: flask_appbuilder_backup_TIMESTAMP)"
    echo "  --no-db              不备份数据库"
    echo "  --no-files           不备份应用文件"
    echo "  --compress           使用更高压缩比"
    echo "  -h, --help           显示此帮助信息"
    echo ""
}

# 检查依赖
check_dependencies() {
    log "检查备份依赖..."
    
    local deps=("docker" "docker-compose" "tar" "gzip")
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
    
    log "备份依赖检查通过"
}

# 创建备份目录
create_backup_dir() {
    log "创建备份目录: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
}

# 备份数据库
backup_database() {
    log "开始备份数据库..."
    
    local db_backup_file="$BACKUP_DIR/${BACKUP_NAME}_database.sql"
    
    # 使用docker-compose执行数据库备份
    if docker-compose exec db pg_dump -U flaskuser flaskdb > "$db_backup_file"; then
        log "数据库备份成功: $db_backup_file"
        
        # 如果需要更高压缩比
        if [ "$COMPRESS" = "true" ]; then
            log "压缩数据库备份..."
            gzip -9 "$db_backup_file"
            log "数据库备份已压缩: ${db_backup_file}.gz"
        fi
    else
        log_error "数据库备份失败"
        exit 1
    fi
}

# 备份应用文件
backup_app_files() {
    log "开始备份应用文件..."
    
    local files_backup_file="$BACKUP_DIR/${BACKUP_NAME}_files.tar.gz"
    
    # 创建应用文件备份
    # 排除不必要的文件和目录
    if tar --exclude='*.pyc' \
       --exclude='__pycache__' \
       --exclude='.git' \
       --exclude='backups' \
       --exclude='*.log' \
       -czf "$files_backup_file" \
       app/ \
       config.py \
       requirements.txt \
       run.py \
       .env; then
        log "应用文件备份成功: $files_backup_file"
    else
        log_error "应用文件备份失败"
        exit 1
    fi
}

# 创建备份元数据
create_metadata() {
    log "创建备份元数据..."
    
    local metadata_file="$BACKUP_DIR/${BACKUP_NAME}_metadata.json"
    
    # 获取系统信息
    local system_info=$(uname -a)
    local docker_info=$(docker --version)
    local compose_info=$(docker-compose --version)
    
    # 创建JSON格式的元数据文件
    cat > "$metadata_file" << EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$TIMESTAMP",
  "system_info": "$system_info",
  "docker_version": "$docker_info",
  "docker_compose_version": "$compose_info",
  "include_database": $INCLUDE_DB,
  "include_files": $INCLUDE_FILES,
  "compressed": $([ "$COMPRESS" = "true" ] && echo "true" || echo "false"),
  "files": [
EOF

    # 添加备份文件列表
    if [ "$INCLUDE_DB" = "true" ]; then
        if [ "$COMPRESS" = "true" ]; then
            echo "    \"${BACKUP_NAME}_database.sql.gz\"," >> "$metadata_file"
        else
            echo "    \"${BACKUP_NAME}_database.sql\"," >> "$metadata_file"
        fi
    fi
    
    if [ "$INCLUDE_FILES" = "true" ]; then
        echo "    \"${BACKUP_NAME}_files.tar.gz\"" >> "$metadata_file"
    fi
    
    # 移除最后一行的逗号并关闭数组和对象
    sed -i '$ s/,$//' "$metadata_file"
    echo "  ]" >> "$metadata_file"
    echo "}" >> "$metadata_file"
    
    log "备份元数据已创建: $metadata_file"
}

# 验证备份完整性
verify_backup() {
    log "验证备份完整性..."
    
    local metadata_file="$BACKUP_DIR/${BACKUP_NAME}_metadata.json"
    
    # 检查元数据文件是否存在
    if [ ! -f "$metadata_file" ]; then
        log_error "元数据文件不存在: $metadata_file"
        exit 1
    fi
    
    # 检查备份文件是否存在
    if [ "$INCLUDE_DB" = "true" ]; then
        local db_file="${BACKUP_NAME}_database.sql"
        if [ "$COMPRESS" = "true" ]; then
            db_file="${db_file}.gz"
        fi
        
        if [ ! -f "$BACKUP_DIR/$db_file" ]; then
            log_error "数据库备份文件不存在: $db_file"
            exit 1
        fi
    fi
    
    if [ "$INCLUDE_FILES" = "true" ]; then
        local files_file="${BACKUP_NAME}_files.tar.gz"
        if [ ! -f "$BACKUP_DIR/$files_file" ]; then
            log_error "应用文件备份不存在: $files_file"
            exit 1
        fi
    fi
    
    log "备份完整性验证通过"
}

# 列出备份
list_backups() {
    log "列出所有备份..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warn "备份目录不存在: $BACKUP_DIR"
        return
    fi
    
    echo "----------------------------------------"
    echo "备份列表 ($BACKUP_DIR):"
    echo "----------------------------------------"
    
    # 查找备份文件
    local backups_found=false
    
    for meta_file in "$BACKUP_DIR"/*_metadata.json; do
        if [ -f "$meta_file" ]; then
            backups_found=true
            local backup_name=$(basename "$meta_file" _metadata.json)
            local backup_time=$(stat -c %y "$meta_file" 2>/dev/null || stat -f %Sm -t "%Y-%m-%d %H:%M:%S" "$meta_file")
            
            echo "备份名称: $backup_name"
            echo "创建时间: $backup_time"
            
            # 读取元数据中的文件列表
            local files_list=$(jq -r '.files[]' "$meta_file" 2>/dev/null || echo "无法读取文件列表")
            echo "包含文件:"
            echo "$files_list" | sed 's/^/  - /'
            echo "----------------------------------------"
        fi
    done
    
    if [ "$backups_found" = false ]; then
        echo "没有找到备份文件"
        echo "----------------------------------------"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    local days=${1:-30}  # 默认保留30天内的备份
    log "清理 $days 天前的旧备份..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warn "备份目录不存在: $BACKUP_DIR"
        return
    fi
    
    # 查找并删除指定天数之前的备份文件
    find "$BACKUP_DIR" -name "*.sql*" -type f -mtime +$days -delete
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$days -delete
    find "$BACKUP_DIR" -name "*_metadata.json" -type f -mtime +$days -delete
    
    log "旧备份清理完成"
}

# 主函数
main() {
    # 默认包含所有备份项
    INCLUDE_DB=true
    INCLUDE_FILES=true
    COMPRESS=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            -n|--name)
                BACKUP_NAME="$2"
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
            --compress)
                COMPRESS=true
                shift
                ;;
            -h|--help)
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
    
    # 如果既不备份数据库也不备份文件，则退出
    if [ "$INCLUDE_DB" = "false" ] && [ "$INCLUDE_FILES" = "false" ]; then
        log_warn "未选择任何备份项，脚本将退出"
        exit 0
    fi
    
    log "开始执行Flask-AppBuilder应用备份"
    log "备份名称: $BACKUP_NAME"
    log "备份目录: $BACKUP_DIR"
    
    # 执行备份步骤
    check_dependencies
    create_backup_dir
    
    if [ "$INCLUDE_DB" = "true" ]; then
        backup_database
    fi
    
    if [ "$INCLUDE_FILES" = "true" ]; then
        backup_app_files
    fi
    
    create_metadata
    verify_backup
    
    log "备份完成: $BACKUP_NAME"
    log "备份位置: $BACKUP_DIR"
}

# 全局变量用于list和cleanup命令
COMMAND=""
CLEANUP_DAYS=""

# 检查是否有特殊命令
if [[ "${1:-}" == "list" ]]; then
    list_backups
    exit 0
elif [[ "${1:-}" == "cleanup" ]]; then
    CLEANUP_DAYS="${2:-30}"
    cleanup_old_backups "$CLEANUP_DAYS"
    exit 0
else
    # 正常执行备份流程
    main "$@"
fi