#!/bin/bash

# Airflow灾难恢复脚本
# 用于备份、恢复和故障转移操作

set -e  # 遇到错误时退出

# 配置变量
AIRFLOW_HOME="/opt/airflow"
BACKUP_DIR="/backup/airflow"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/airflow/disaster-recovery.log"
S3_BUCKET="s3://your-company-airflow-backups"
KUBE_CONTEXT="production"
KUBE_NAMESPACE="airflow"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查必要命令
check_dependencies() {
    log_info "检查必要命令..."
    
    commands=("kubectl" "aws" "pg_dump" "psql" "tar" "gzip")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 命令未找到，请安装后重试"
            exit 1
        fi
    done
    
    log_info "所有必要命令检查通过"
}

# 创建备份目录
create_backup_dirs() {
    log_info "创建备份目录..."
    
    mkdir -p $BACKUP_DIR/$DATE/{dags,logs,config,database}
    
    if [ $? -eq 0 ]; then
        log_info "备份目录创建成功: $BACKUP_DIR/$DATE"
    else
        log_error "备份目录创建失败"
        exit 1
    fi
}

# 备份DAGs
backup_dags() {
    log_info "开始备份DAGs..."
    
    if [ -d "$AIRFLOW_HOME/dags" ]; then
        tar -czf $BACKUP_DIR/$DATE/dags/dags.tar.gz -C $AIRFLOW_HOME dags
        if [ $? -eq 0 ]; then
            log_info "DAGs备份完成"
        else
            log_error "DAGs备份失败"
            exit 1
        fi
    else
        log_warn "DAGs目录不存在: $AIRFLOW_HOME/dags"
    fi
}

# 备份配置文件
backup_config() {
    log_info "开始备份配置文件..."
    
    # 备份主配置文件
    if [ -f "$AIRFLOW_HOME/airflow.cfg" ]; then
        cp $AIRFLOW_HOME/airflow.cfg $BACKUP_DIR/$DATE/config/
    fi
    
    # 备份环境变量文件
    if [ -f "$AIRFLOW_HOME/.env" ]; then
        cp $AIRFLOW_HOME/.env $BACKUP_DIR/$DATE/config/
    fi
    
    # 备份其他配置文件
    find $AIRFLOW_HOME -name "*.cfg" -o -name "*.conf" | while read file; do
        rel_path=${file#$AIRFLOW_HOME/}
        mkdir -p "$(dirname "$BACKUP_DIR/$DATE/config/$rel_path")"
        cp "$file" "$BACKUP_DIR/$DATE/config/$rel_path"
    done
    
    # 压缩配置备份
    tar -czf $BACKUP_DIR/$DATE/config.tar.gz -C $BACKUP_DIR/$DATE config
    rm -rf $BACKUP_DIR/$DATE/config
    
    if [ $? -eq 0 ]; then
        log_info "配置文件备份完成"
    else
        log_error "配置文件备份失败"
        exit 1
    fi
}

# 备份数据库
backup_database() {
    log_info "开始备份数据库..."
    
    # 从环境变量获取数据库连接信息
    DB_HOST=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN#*://}
    DB_USER=${DB_HOST%@*}
    DB_HOST=${DB_HOST#*@}
    DB_NAME=${DB_HOST#*/} 
    DB_HOST=${DB_HOST%/*}
    DB_PORT=${DB_HOST#*:}
    DB_HOST=${DB_HOST%:*}
    
    # 如果端口不存在，使用默认端口
    if [ "$DB_HOST" = "$DB_PORT" ]; then
        DB_PORT="5432"
    fi
    
    # 导出数据库
    pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_DIR/$DATE/database/airflow_backup.sql
    
    if [ $? -eq 0 ]; then
        # 压缩数据库备份
        gzip $BACKUP_DIR/$DATE/database/airflow_backup.sql
        log_info "数据库备份完成"
    else
        log_error "数据库备份失败"
        exit 1
    fi
}

# 备份日志
backup_logs() {
    log_info "开始备份日志..."
    
    if [ -d "$AIRFLOW_HOME/logs" ]; then
        tar -czf $BACKUP_DIR/$DATE/logs/logs.tar.gz -C $AIRFLOW_HOME logs
        if [ $? -eq 0 ]; then
            log_info "日志备份完成"
        else
            log_error "日志备份失败"
            exit 1
        fi
    else
        log_warn "日志目录不存在: $AIRFLOW_HOME/logs"
    fi
}

# 备份Kubernetes资源
backup_k8s_resources() {
    log_info "开始备份Kubernetes资源..."
    
    # 设置Kubernetes上下文
    kubectl config use-context $KUBE_CONTEXT
    
    # 创建K8s资源备份目录
    mkdir -p $BACKUP_DIR/$DATE/k8s
    
    # 备份Airflow相关的资源
    resources=("deployments" "services" "configmaps" "secrets" "pvcs" "ingresses" "serviceaccounts" "roles" "rolebindings")
    
    for resource in "${resources[@]}"; do
        kubectl get $resource -n $KUBE_NAMESPACE -o yaml > $BACKUP_DIR/$DATE/k8s/${resource}.yaml 2>/dev/null || true
    done
    
    # 备份Helm发布信息
    helm get all airflow -n $KUBE_NAMESPACE > $BACKUP_DIR/$DATE/k8s/helm-release.yaml 2>/dev/null || true
    
    # 压缩K8s备份
    tar -czf $BACKUP_DIR/$DATE/k8s.tar.gz -C $BACKUP_DIR/$DATE k8s
    rm -rf $BACKUP_DIR/$DATE/k8s
    
    if [ $? -eq 0 ]; then
        log_info "Kubernetes资源备份完成"
    else
        log_warn "Kubernetes资源备份可能不完整"
    fi
}

# 上传备份到S3
upload_to_s3() {
    log_info "开始上传备份到S3..."
    
    # 创建备份元数据
    cat > $BACKUP_DIR/$DATE/metadata.json << EOF
{
  "backup_time": "$(date)",
  "airflow_version": "$(airflow version 2>/dev/null || echo 'unknown')",
  "backup_size": "$(du -sh $BACKUP_DIR/$DATE | cut -f1)",
  "components": ["dags", "config", "database", "logs", "k8s"],
  "kubernetes_context": "$KUBE_CONTEXT",
  "kubernetes_namespace": "$KUBE_NAMESPACE"
}
EOF
    
    # 压缩整个备份
    tar -czf $BACKUP_DIR/airflow-backup-$DATE.tar.gz -C $BACKUP_DIR $DATE
    
    # 上传到S3
    aws s3 cp $BACKUP_DIR/airflow-backup-$DATE.tar.gz $S3_BUCKET/backups/
    
    if [ $? -eq 0 ]; then
        log_info "备份上传到S3成功: $S3_BUCKET/backups/airflow-backup-$DATE.tar.gz"
        
        # 清理本地备份文件
        rm -rf $BACKUP_DIR/$DATE
        rm $BACKUP_DIR/airflow-backup-$DATE.tar.gz
        
        # 记录备份信息
        echo "$DATE" >> $BACKUP_DIR/backup_history.txt
    else
        log_error "备份上传到S3失败"
        exit 1
    fi
}

# 列出可用备份
list_backups() {
    log_info "可用备份列表:"
    
    aws s3 ls $S3_BUCKET/backups/ | grep airflow-backup
}

# 恢复指定备份
restore_backup() {
    local backup_date=$1
    
    if [ -z "$backup_date" ]; then
        log_error "请提供要恢复的备份日期"
        exit 1
    fi
    
    log_info "开始恢复备份: $backup_date"
    
    # 停止Airflow服务
    log_info "停止Airflow服务..."
    kubectl scale deployment airflow-webserver --replicas=0 -n $KUBE_NAMESPACE
    kubectl scale deployment airflow-scheduler --replicas=0 -n $KUBE_NAMESPACE
    kubectl scale deployment airflow-worker --replicas=0 -n $KUBE_NAMESPACE
    
    # 下载备份
    log_info "下载备份文件..."
    aws s3 cp $S3_BUCKET/backups/airflow-backup-$backup_date.tar.gz $BACKUP_DIR/
    
    if [ $? -ne 0 ]; then
        log_error "备份文件下载失败"
        exit 1
    fi
    
    # 解压备份
    log_info "解压备份文件..."
    tar -xzf $BACKUP_DIR/airflow-backup-$backup_date.tar.gz -C $BACKUP_DIR
    
    # 恢复DAGs
    if [ -f "$BACKUP_DIR/$backup_date/dags/dags.tar.gz" ]; then
        log_info "恢复DAGs..."
        tar -xzf $BACKUP_DIR/$backup_date/dags/dags.tar.gz -C $AIRFLOW_HOME
    fi
    
    # 恢复配置文件
    if [ -f "$BACKUP_DIR/$backup_date/config.tar.gz" ]; then
        log_info "恢复配置文件..."
        tar -xzf $BACKUP_DIR/$backup_date/config.tar.gz -C /tmp
        cp -r /tmp/config/* $AIRFLOW_HOME/
        rm -rf /tmp/config
    fi
    
    # 恢复数据库
    if [ -f "$BACKUP_DIR/$backup_date/database/airflow_backup.sql.gz" ]; then
        log_info "恢复数据库..."
        
        # 获取数据库连接信息
        DB_HOST=${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN#*://}
        DB_USER=${DB_HOST%@*}
        DB_HOST=${DB_HOST#*@}
        DB_NAME=${DB_HOST#*/} 
        DB_HOST=${DB_HOST%/*}
        DB_PORT=${DB_HOST#*:}
        if [ "$DB_HOST" = "$DB_PORT" ]; then
            DB_PORT="5432"
        fi
        
        # 解压并恢复数据库
        gunzip -c $BACKUP_DIR/$backup_date/database/airflow_backup.sql.gz | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
    fi
    
    # 恢复日志
    if [ -f "$BACKUP_DIR/$backup_date/logs/logs.tar.gz" ]; then
        log_info "恢复日志..."
        tar -xzf $BACKUP_DIR/$backup_date/logs/logs.tar.gz -C $AIRFLOW_HOME
    fi
    
    # 清理临时文件
    rm -rf $BACKUP_DIR/$backup_date
    rm $BACKUP_DIR/airflow-backup-$backup_date.tar.gz
    
    # 启动Airflow服务
    log_info "启动Airflow服务..."
    kubectl scale deployment airflow-webserver --replicas=3 -n $KUBE_NAMESPACE
    kubectl scale deployment airflow-scheduler --replicas=2 -n $KUBE_NAMESPACE
    kubectl scale deployment airflow-worker --replicas=5 -n $KUBE_NAMESPACE
    
    log_info "备份恢复完成"
}

# 故障转移操作
failover_to_standby() {
    log_info "开始故障转移操作..."
    
    # 检查备用环境状态
    log_info "检查备用环境..."
    kubectl config use-context standby
    
    # 部署Airflow到备用环境
    log_info "部署Airflow到备用环境..."
    helm upgrade --install airflow ./airflow-chart \
        -f values-standby.yaml \
        -n airflow-standby \
        --create-namespace
    
    # 等待部署完成
    log_info "等待部署完成..."
    kubectl wait --for=condition=available deployment/airflow-webserver -n airflow-standby --timeout=300s
    
    # 更新DNS记录
    log_info "更新DNS记录..."
    # 这里应该调用DNS提供商的API来更新记录
    # aws route53 change-resource-record-sets --hosted-zone-id ZXXXXXXXXXXXXXX --change-batch file://dns-change-batch.json
    
    log_info "故障转移完成"
}

# 验证恢复
verify_restore() {
    log_info "验证恢复结果..."
    
    # 检查服务状态
    kubectl get pods -n $KUBE_NAMESPACE
    
    # 检查数据库连接
    # 这里应该添加数据库连接测试
    
    # 检查DAGs是否加载正常
    airflow dags list 2>/dev/null || log_warn "无法验证DAGs状态"
    
    log_info "恢复验证完成"
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份..."
    
    # 保留最近30天的备份
    find $BACKUP_DIR -name "airflow-backup-*" -mtime +30 -delete
    
    # 清理S3上的旧备份
    aws s3 ls $S3_BUCKET/backups/ | awk '{print $4}' | grep airflow-backup | while read backup; do
        backup_date=$(echo $backup | sed 's/airflow-backup-\(.*\)\.tar\.gz/\1/')
        backup_timestamp=$(date -d "$backup_date" +%s 2>/dev/null || echo 0)
        current_timestamp=$(date -d "30 days ago" +%s)
        
        if [ $backup_timestamp -lt $current_timestamp ]; then
            aws s3 rm $S3_BUCKET/backups/$backup
        fi
    done
    
    log_info "旧备份清理完成"
}

# 主备份函数
perform_backup() {
    log_info "开始执行完整备份..."
    
    check_dependencies
    create_backup_dirs
    backup_dags
    backup_config
    backup_database
    backup_logs
    backup_k8s_resources
    upload_to_s3
    cleanup_old_backups
    
    log_info "完整备份执行完成"
}

# 显示帮助信息
show_help() {
    echo "Airflow灾难恢复脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  backup             执行完整备份"
    echo "  restore <date>     恢复指定日期的备份"
    echo "  failover           执行故障转移"
    echo "  list               列出可用备份"
    echo "  verify             验证恢复结果"
    echo "  help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 backup"
    echo "  $0 restore 20231201_143022"
    echo "  $0 failover"
}

# 主函数
main() {
    case "$1" in
        backup)
            perform_backup
            ;;
        restore)
            restore_backup "$2"
            ;;
        failover)
            failover_to_standby
            ;;
        list)
            list_backups
            ;;
        verify)
            verify_restore
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