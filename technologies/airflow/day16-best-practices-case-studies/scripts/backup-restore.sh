#!/bin/bash

# Airflow备份恢复脚本
# 用于备份和恢复Airflow配置、数据和DAGs

set -e  # 遇到错误时退出

# 配置变量
AIRFLOW_HOME="/opt/airflow"
BACKUP_BASE_DIR="/backup/airflow"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/backup-$TIMESTAMP"
RESTORE_DIR=""
LOG_FILE="/var/log/airflow/backup-restore.log"
KUBE_NAMESPACE="airflow"
KUBE_CONTEXT="production"
S3_BUCKET=""
S3_PREFIX="airflow-backups"
ENCRYPTION_KEY=""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_info() {
    log "${GREEN}INFO${NC} - $1"
}

log_warn() {
    log "${YELLOW}WARN${NC} - $1"
}

log_error() {
    log "${RED}ERROR${NC} - $1"
}

log_debug() {
    log "${BLUE}DEBUG${NC} - $1"
}

# 检查必要命令
check_dependencies() {
    log_info "检查必要命令..."
    
    commands=("kubectl" "pg_dump" "tar" "gzip" "openssl" "aws")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 命令未找到，请安装后重试"
            exit 1
        fi
    done
    
    log_info "所有必要命令检查通过"
}

# 创建备份目录
create_backup_directory() {
    log_info "创建备份目录: $BACKUP_DIR"
    
    # 创建本地备份目录
    mkdir -p $BACKUP_DIR
    
    # 如果配置了S3，创建S3路径
    if [ -n "$S3_BUCKET" ]; then
        log_info "S3备份已启用: s3://$S3_BUCKET/$S3_PREFIX/"
    fi
    
    log_info "备份目录创建完成"
}

# 备份Airflow配置文件
backup_config_files() {
    log_info "备份Airflow配置文件..."
    
    # 创建配置备份目录
    mkdir -p $BACKUP_DIR/config
    
    # 备份主配置文件
    if [ -f "$AIRFLOW_HOME/airflow.cfg" ]; then
        cp $AIRFLOW_HOME/airflow.cfg $BACKUP_DIR/config/
        log_info "airflow.cfg 备份完成"
    else
        log_warn "未找到 airflow.cfg 文件"
    fi
    
    # 备份环境变量文件
    if [ -f "$AIRFLOW_HOME/.env" ]; then
        cp $AIRFLOW_HOME/.env $BACKUP_DIR/config/
        log_info ".env 文件备份完成"
    fi
    
    # 备份其他配置文件
    if [ -d "$AIRFLOW_HOME/config" ]; then
        cp -r $AIRFLOW_HOME/config $BACKUP_DIR/config/
        log_info "config 目录备份完成"
    fi
    
    log_info "Airflow配置文件备份完成"
}

# 备份DAG文件
backup_dag_files() {
    log_info "备份DAG文件..."
    
    # 创建DAG备份目录
    mkdir -p $BACKUP_DIR/dags
    
    # 备份DAG文件
    if [ -d "$AIRFLOW_HOME/dags" ]; then
        cp -r $AIRFLOW_HOME/dags/* $BACKUP_DIR/dags/ 2>/dev/null || true
        log_info "DAG 文件备份完成"
    else
        log_warn "未找到 dags 目录"
    fi
    
    log_info "DAG文件备份完成"
}

# 备份插件文件
backup_plugin_files() {
    log_info "备份插件文件..."
    
    # 创建插件备份目录
    mkdir -p $BACKUP_DIR/plugins
    
    # 备份插件文件
    if [ -d "$AIRFLOW_HOME/plugins" ]; then
        cp -r $AIRFLOW_HOME/plugins/* $BACKUP_DIR/plugins/ 2>/dev/null || true
        log_info "插件文件备份完成"
    else
        log_warn "未找到 plugins 目录"
    fi
    
    log_info "插件文件备份完成"
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    # 创建数据库备份目录
    mkdir -p $BACKUP_DIR/database
    
    # 从环境变量获取数据库连接信息
    DB_HOST=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN#*://}
    DB_USER=${DB_HOST%@*}
    DB_HOST=${DB_HOST#*@}
    DB_NAME=${DB_HOST#*/} 
    DB_HOST=${DB_HOST%/*}
    DB_PORT=${DB_HOST#*:}
    if [ "$DB_HOST" = "$DB_PORT" ]; then
        DB_PORT="5432"
    fi
    
    # 备份数据库
    PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_DIR/database/airflow-db.sql
    
    if [ $? -eq 0 ]; then
        log_info "数据库备份完成"
    else
        log_error "数据库备份失败"
        return 1
    fi
    
    log_info "数据库备份完成"
}

# 备份Kubernetes资源
backup_kubernetes_resources() {
    log_info "备份Kubernetes资源..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 创建Kubernetes备份目录
    mkdir -p $BACKUP_DIR/kubernetes
    
    # 备份Deployment
    kubectl get deployment -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/deployments.yaml
    
    # 备份Service
    kubectl get service -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/services.yaml
    
    # 备份ConfigMap
    kubectl get configmap -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/configmaps.yaml
    
    # 备份Secret
    kubectl get secret -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/secrets.yaml
    
    # 备份PersistentVolumeClaim
    kubectl get pvc -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/pvcs.yaml
    
    # 备份Ingress
    kubectl get ingress -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/ingresses.yaml 2>/dev/null || true
    
    # 备份NetworkPolicy
    kubectl get networkpolicy -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/networkpolicies.yaml 2>/dev/null || true
    
    # 备份Role和RoleBinding
    kubectl get role -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/roles.yaml 2>/dev/null || true
    kubectl get rolebinding -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/kubernetes/rolebindings.yaml 2>/dev/null || true
    
    log_info "Kubernetes资源备份完成"
}

# 压缩备份
compress_backup() {
    log_info "压缩备份文件..."
    
    # 进入备份基目录
    cd $BACKUP_BASE_DIR
    
    # 创建tar.gz压缩包
    tar -czf backup-$TIMESTAMP.tar.gz backup-$TIMESTAMP
    
    if [ $? -eq 0 ]; then
        log_info "备份压缩完成: backup-$TIMESTAMP.tar.gz"
        
        # 删除未压缩的备份目录
        rm -rf $BACKUP_DIR
        
        # 如果配置了加密密钥，加密备份文件
        if [ -n "$ENCRYPTION_KEY" ]; then
            log_info "加密备份文件..."
            openssl enc -aes-256-cbc -salt -in backup-$TIMESTAMP.tar.gz -out backup-$TIMESTAMP.tar.gz.enc -k $ENCRYPTION_KEY
            
            if [ $? -eq 0 ]; then
                log_info "备份文件加密完成"
                # 删除未加密的备份文件
                rm backup-$TIMESTAMP.tar.gz
            else
                log_error "备份文件加密失败"
                return 1
            fi
        fi
    else
        log_error "备份压缩失败"
        return 1
    fi
    
    log_info "备份压缩完成"
}

# 上传到S3
upload_to_s3() {
    if [ -n "$S3_BUCKET" ]; then
        log_info "上传备份到S3..."
        
        # 确定要上传的文件
        if [ -f "$BACKUP_BASE_DIR/backup-$TIMESTAMP.tar.gz.enc" ]; then
            BACKUP_FILE="backup-$TIMESTAMP.tar.gz.enc"
        elif [ -f "$BACKUP_BASE_DIR/backup-$TIMESTAMP.tar.gz" ]; then
            BACKUP_FILE="backup-$TIMESTAMP.tar.gz"
        else
            log_error "未找到备份文件"
            return 1
        fi
        
        # 上传到S3
        aws s3 cp $BACKUP_BASE_DIR/$BACKUP_FILE s3://$S3_BUCKET/$S3_PREFIX/$BACKUP_FILE
        
        if [ $? -eq 0 ]; then
            log_info "备份上传到S3完成: s3://$S3_BUCKET/$S3_PREFIX/$BACKUP_FILE"
        else
            log_error "备份上传到S3失败"
            return 1
        fi
    else
        log_info "S3备份未配置，跳过上传"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份..."
    
    # 保留最近7天的备份
    find $BACKUP_BASE_DIR -name "backup-*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
    find $BACKUP_BASE_DIR -name "backup-*.tar.gz*" -type f -mtime +7 -exec rm -f {} \; 2>/dev/null || true
    
    log_info "旧备份清理完成"
}

# 执行完整备份
perform_backup() {
    log_info "开始执行完整备份..."
    
    check_dependencies
    create_backup_directory
    backup_config_files
    backup_dag_files
    backup_plugin_files
    backup_database
    backup_kubernetes_resources
    compress_backup
    upload_to_s3
    cleanup_old_backups
    
    log_info "完整备份执行完成"
}

# 从S3下载备份
download_from_s3() {
    if [ -n "$S3_BUCKET" ] && [ -n "$1" ]; then
        log_info "从S3下载备份: $1"
        
        # 创建恢复目录
        mkdir -p $RESTORE_DIR
        
        # 下载备份文件
        aws s3 cp s3://$S3_BUCKET/$S3_PREFIX/$1 $RESTORE_DIR/$1
        
        if [ $? -eq 0 ]; then
            log_info "备份下载完成: $RESTORE_DIR/$1"
        else
            log_error "备份下载失败"
            return 1
        fi
    else
        log_error "S3配置或备份文件名未提供"
        return 1
    fi
}

# 解压备份
extract_backup() {
    log_info "解压备份文件..."
    
    # 确定备份文件
    if [ -f "$RESTORE_DIR/backup-$TIMESTAMP.tar.gz.enc" ]; then
        BACKUP_FILE="backup-$TIMESTAMP.tar.gz.enc"
        # 解密备份文件
        if [ -n "$ENCRYPTION_KEY" ]; then
            log_info "解密备份文件..."
            openssl enc -d -aes-256-cbc -in $RESTORE_DIR/$BACKUP_FILE -out $RESTORE_DIR/backup-$TIMESTAMP.tar.gz -k $ENCRYPTION_KEY
            
            if [ $? -eq 0 ]; then
                log_info "备份文件解密完成"
                BACKUP_FILE="backup-$TIMESTAMP.tar.gz"
            else
                log_error "备份文件解密失败"
                return 1
            fi
        fi
    elif [ -f "$RESTORE_DIR/backup-$TIMESTAMP.tar.gz" ]; then
        BACKUP_FILE="backup-$TIMESTAMP.tar.gz"
    else
        log_error "未找到备份文件"
        return 1
    fi
    
    # 解压备份文件
    tar -xzf $RESTORE_DIR/$BACKUP_FILE -C $RESTORE_DIR
    
    if [ $? -eq 0 ]; then
        log_info "备份解压完成"
    else
        log_error "备份解压失败"
        return 1
    fi
    
    log_info "备份解压完成"
}

# 恢复配置文件
restore_config_files() {
    log_info "恢复配置文件..."
    
    # 恢复主配置文件
    if [ -f "$RESTORE_DIR/backup-$TIMESTAMP/config/airflow.cfg" ]; then
        cp $RESTORE_DIR/backup-$TIMESTAMP/config/airflow.cfg $AIRFLOW_HOME/
        log_info "airflow.cfg 恢复完成"
    fi
    
    # 恢复环境变量文件
    if [ -f "$RESTORE_DIR/backup-$TIMESTAMP/config/.env" ]; then
        cp $RESTORE_DIR/backup-$TIMESTAMP/config/.env $AIRFLOW_HOME/
        log_info ".env 文件恢复完成"
    fi
    
    # 恢复其他配置文件
    if [ -d "$RESTORE_DIR/backup-$TIMESTAMP/config/config" ]; then
        cp -r $RESTORE_DIR/backup-$TIMESTAMP/config/config $AIRFLOW_HOME/
        log_info "config 目录恢复完成"
    fi
    
    log_info "配置文件恢复完成"
}

# 恢复DAG文件
restore_dag_files() {
    log_info "恢复DAG文件..."
    
    # 恢复DAG文件
    if [ -d "$RESTORE_DIR/backup-$TIMESTAMP/dags" ]; then
        # 备份当前DAG文件
        if [ -d "$AIRFLOW_HOME/dags" ]; then
            mv $AIRFLOW_HOME/dags $AIRFLOW_HOME/dags.backup.$(date +%Y%m%d-%H%M%S)
        fi
        
        # 恢复DAG文件
        cp -r $RESTORE_DIR/backup-$TIMESTAMP/dags $AIRFLOW_HOME/
        log_info "DAG 文件恢复完成"
    else
        log_warn "备份中未找到 DAG 文件"
    fi
    
    log_info "DAG文件恢复完成"
}

# 恢复插件文件
restore_plugin_files() {
    log_info "恢复插件文件..."
    
    # 恢复插件文件
    if [ -d "$RESTORE_DIR/backup-$TIMESTAMP/plugins" ]; then
        # 备份当前插件文件
        if [ -d "$AIRFLOW_HOME/plugins" ]; then
            mv $AIRFLOW_HOME/plugins $AIRFLOW_HOME/plugins.backup.$(date +%Y%m%d-%H%M%S)
        fi
        
        # 恢复插件文件
        cp -r $RESTORE_DIR/backup-$TIMESTAMP/plugins $AIRFLOW_HOME/
        log_info "插件文件恢复完成"
    else
        log_warn "备份中未找到插件文件"
    fi
    
    log_info "插件文件恢复完成"
}

# 恢复数据库
restore_database() {
    log_info "恢复数据库..."
    
    # 从环境变量获取数据库连接信息
    DB_HOST=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN#*://}
    DB_USER=${DB_HOST%@*}
    DB_HOST=${DB_HOST#*@}
    DB_NAME=${DB_HOST#*/} 
    DB_HOST=${DB_HOST%/*}
    DB_PORT=${DB_HOST#*:}
    if [ "$DB_HOST" = "$DB_PORT" ]; then
        DB_PORT="5432"
    fi
    
    # 恢复数据库
    if [ -f "$RESTORE_DIR/backup-$TIMESTAMP/database/airflow-db.sql" ]; then
        # 警告用户数据库恢复将覆盖现有数据
        log_warn "数据库恢复将覆盖现有数据，请确认是否继续 (y/N)?"
        read -r REPLY
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $RESTORE_DIR/backup-$TIMESTAMP/database/airflow-db.sql
            
            if [ $? -eq 0 ]; then
                log_info "数据库恢复完成"
            else
                log_error "数据库恢复失败"
                return 1
            fi
        else
            log_info "数据库恢复已取消"
        fi
    else
        log_warn "备份中未找到数据库文件"
    fi
    
    log_info "数据库恢复完成"
}

# 恢复Kubernetes资源
restore_kubernetes_resources() {
    log_info "恢复Kubernetes资源..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 恢复各种Kubernetes资源
    resources=("deployments" "services" "configmaps" "secrets" "pvcs" "ingresses" "networkpolicies" "roles" "rolebindings")
    
    for resource in "${resources[@]}"; do
        if [ -f "$RESTORE_DIR/backup-$TIMESTAMP/kubernetes/$resource.yaml" ]; then
            # 应用资源配置
            kubectl apply -f $RESTORE_DIR/backup-$TIMESTAMP/kubernetes/$resource.yaml -n $KUBE_NAMESPACE
            
            if [ $? -eq 0 ]; then
                log_info "$resource 恢复完成"
            else
                log_error "$resource 恢复失败"
            fi
        fi
    done
    
    log_info "Kubernetes资源恢复完成"
}

# 执行完整恢复
perform_restore() {
    local backup_name=$1
    
    if [ -z "$backup_name" ]; then
        log_error "请提供要恢复的备份名称"
        return 1
    fi
    
    # 设置恢复目录
    RESTORE_DIR="/tmp/airflow-restore-$(date +%Y%m%d-%H%M%S)"
    
    log_info "开始执行完整恢复，备份名称: $backup_name"
    
    check_dependencies
    download_from_s3 $backup_name
    extract_backup
    restore_config_files
    restore_dag_files
    restore_plugin_files
    restore_database
    restore_kubernetes_resources
    
    # 清理临时恢复目录
    rm -rf $RESTORE_DIR
    
    log_info "完整恢复执行完成"
}

# 列出可用备份
list_backups() {
    log_info "列出可用备份..."
    
    # 列出本地备份
    echo "本地备份:"
    ls -la $BACKUP_BASE_DIR/backup-*.tar.gz* 2>/dev/null || echo "无本地备份"
    
    # 列出S3备份
    if [ -n "$S3_BUCKET" ]; then
        echo -e "\nS3备份:"
        aws s3 ls s3://$S3_BUCKET/$S3_PREFIX/ 2>/dev/null || echo "无法列出S3备份"
    fi
    
    log_info "备份列表完成"
}

# 显示帮助信息
show_help() {
    echo "Airflow备份恢复脚本"
    echo "用法: $0 [选项] [参数]"
    echo ""
    echo "选项:"
    echo "  backup             执行完整备份"
    echo "  restore <name>     从指定备份恢复"
    echo "  list               列出可用备份"
    echo "  help               显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  S3_BUCKET          S3存储桶名称（可选）"
    echo "  S3_PREFIX          S3路径前缀（可选）"
    echo "  ENCRYPTION_KEY     备份加密密钥（可选）"
    echo ""
    echo "示例:"
    echo "  $0 backup"
    echo "  S3_BUCKET=my-bucket $0 backup"
    echo "  $0 restore backup-20230101-120000.tar.gz"
    echo "  $0 list"
}

# 主函数
main() {
    case "$1" in
        backup)
            perform_backup
            ;;
        restore)
            if [ -n "$2" ]; then
                perform_restore "$2"
            else
                log_error "请提供要恢复的备份名称"
                show_help
                exit 1
            fi
            ;;
        list)
            list_backups
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

# 执行主函数
main "$@"