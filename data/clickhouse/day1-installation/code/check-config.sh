#!/bin/bash

# ClickHouse 配置检查脚本
# 作者: ClickHouse学习教程
# 版本: 1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置参数
CLICKHOUSE_HOST=${CLICKHOUSE_HOST:-localhost}
CLICKHOUSE_PORT=${CLICKHOUSE_PORT:-8123}
CLICKHOUSE_USER=${CLICKHOUSE_USER:-default}
CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD:-}

echo -e "${BLUE}🔍 ClickHouse 配置检查工具${NC}"
echo "================================================"

# 检查ClickHouse服务状态
check_service_status() {
    echo -e "${CYAN}📋 检查服务状态${NC}"
    echo "----------------------------------------"
    
    # 检查进程
    echo -n "进程状态: "
    if pgrep -f clickhouse-server > /dev/null; then
        echo -e "${GREEN}✅ 运行中${NC}"
        ps aux | grep clickhouse-server | grep -v grep | head -1
    else
        echo -e "${RED}❌ 未运行${NC}"
        return 1
    fi
    
    # 检查端口
    echo -n "HTTP端口 (8123): "
    if netstat -tlnp 2>/dev/null | grep ":8123 " > /dev/null || ss -tlnp 2>/dev/null | grep ":8123 " > /dev/null; then
        echo -e "${GREEN}✅ 监听中${NC}"
    else
        echo -e "${RED}❌ 未监听${NC}"
    fi
    
    echo -n "TCP端口 (9000): "
    if netstat -tlnp 2>/dev/null | grep ":9000 " > /dev/null || ss -tlnp 2>/dev/null | grep ":9000 " > /dev/null; then
        echo -e "${GREEN}✅ 监听中${NC}"
    else
        echo -e "${RED}❌ 未监听${NC}"
    fi
    
    echo ""
}

# 检查ClickHouse连接
check_connection() {
    echo -e "${CYAN}🔌 检查连接${NC}"
    echo "----------------------------------------"
    
    # HTTP连接测试
    echo -n "HTTP连接: "
    if [ -n "$CLICKHOUSE_PASSWORD" ]; then
        AUTH_PARAM="--user $CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD"
    else
        AUTH_PARAM=""
    fi
    
    if curl -s $AUTH_PARAM "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" --data-urlencode 'query=SELECT 1' >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 正常${NC}"
    else
        echo -e "${RED}❌ 失败${NC}"
        return 1
    fi
    
    # 获取版本信息
    VERSION=$(curl -s $AUTH_PARAM "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" --data-urlencode 'query=SELECT version()' 2>/dev/null)
    echo "版本信息: $VERSION"
    
    # 获取服务器信息
    UPTIME=$(curl -s $AUTH_PARAM "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" --data-urlencode 'query=SELECT uptime()' 2>/dev/null)
    echo "运行时间: ${UPTIME}秒"
    
    echo ""
}

# 检查系统资源
check_system_resources() {
    echo -e "${CYAN}💻 检查系统资源${NC}"
    echo "----------------------------------------"
    
    # 内存检查
    echo "内存使用情况:"
    if command -v free >/dev/null 2>&1; then
        free -h
    elif command -v vm_stat >/dev/null 2>&1; then
        # macOS
        vm_stat | head -4
    fi
    echo ""
    
    # 磁盘检查
    echo "磁盘使用情况:"
    df -h | grep -E "(Filesystem|/dev/|tmpfs)" | head -10
    echo ""
    
    # CPU检查
    echo "CPU信息:"
    if [ -f /proc/cpuinfo ]; then
        grep -E "(processor|model name|cpu cores)" /proc/cpuinfo | head -6
    elif command -v sysctl >/dev/null 2>&1; then
        # macOS
        sysctl -n hw.ncpu
        sysctl -n machdep.cpu.brand_string
    fi
    echo ""
}

# 检查配置文件
check_config_files() {
    echo -e "${CYAN}📄 检查配置文件${NC}"
    echo "----------------------------------------"
    
    # 常见配置文件路径
    CONFIG_PATHS=(
        "/etc/clickhouse-server/config.xml"
        "/opt/homebrew/etc/clickhouse-server/config.xml"
        "/usr/local/etc/clickhouse-server/config.xml"
        "./configs/single/config.xml"
    )
    
    USERS_PATHS=(
        "/etc/clickhouse-server/users.xml"
        "/opt/homebrew/etc/clickhouse-server/users.xml"  
        "/usr/local/etc/clickhouse-server/users.xml"
        "./configs/single/users.xml"
    )
    
    # 检查主配置文件
    echo "主配置文件 (config.xml):"
    for path in "${CONFIG_PATHS[@]}"; do
        if [ -f "$path" ]; then
            echo -e "  ${GREEN}✅ 找到: $path${NC}"
            CONFIG_FILE="$path"
            break
        fi
    done
    
    if [ -z "$CONFIG_FILE" ]; then
        echo -e "  ${RED}❌ 未找到 config.xml${NC}"
    else
        # 检查配置文件权限
        ls -la "$CONFIG_FILE"
        
        # 检查关键配置项
        echo "  关键配置项:"
        if grep -q "<listen_host>" "$CONFIG_FILE"; then
            LISTEN_HOST=$(grep "<listen_host>" "$CONFIG_FILE" | sed 's/.*<listen_host>\(.*\)<\/listen_host>.*/\1/')
            echo "    监听地址: $LISTEN_HOST"
        fi
        
        if grep -q "<http_port>" "$CONFIG_FILE"; then
            HTTP_PORT=$(grep "<http_port>" "$CONFIG_FILE" | sed 's/.*<http_port>\(.*\)<\/http_port>.*/\1/')
            echo "    HTTP端口: $HTTP_PORT"
        fi
        
        if grep -q "<tcp_port>" "$CONFIG_FILE"; then
            TCP_PORT=$(grep "<tcp_port>" "$CONFIG_FILE" | sed 's/.*<tcp_port>\(.*\)<\/tcp_port>.*/\1/')
            echo "    TCP端口: $TCP_PORT"
        fi
    fi
    
    echo ""
    
    # 检查用户配置文件
    echo "用户配置文件 (users.xml):"
    for path in "${USERS_PATHS[@]}"; do
        if [ -f "$path" ]; then
            echo -e "  ${GREEN}✅ 找到: $path${NC}"
            USERS_FILE="$path"
            break
        fi
    done
    
    if [ -z "$USERS_FILE" ]; then
        echo -e "  ${RED}❌ 未找到 users.xml${NC}"
    else
        ls -la "$USERS_FILE"
    fi
    
    echo ""
}

# 检查数据目录
check_data_directories() {
    echo -e "${CYAN}📁 检查数据目录${NC}"
    echo "----------------------------------------"
    
    # 常见数据目录路径
    DATA_PATHS=(
        "/var/lib/clickhouse"
        "/opt/homebrew/var/lib/clickhouse"
        "/usr/local/var/lib/clickhouse"
        "$HOME/clickhouse/data"
    )
    
    LOG_PATHS=(
        "/var/log/clickhouse-server"
        "/opt/homebrew/var/log/clickhouse-server"
        "/usr/local/var/log/clickhouse-server"
        "$HOME/clickhouse/logs"
    )
    
    # 检查数据目录
    echo "数据目录:"
    for path in "${DATA_PATHS[@]}"; do
        if [ -d "$path" ]; then
            echo -e "  ${GREEN}✅ 找到: $path${NC}"
            du -sh "$path" 2>/dev/null || echo "    无法获取大小"
            ls -la "$path" 2>/dev/null | head -5
            DATA_DIR="$path"
            break
        fi
    done
    
    if [ -z "$DATA_DIR" ]; then
        echo -e "  ${RED}❌ 未找到数据目录${NC}"
    fi
    
    echo ""
    
    # 检查日志目录
    echo "日志目录:"
    for path in "${LOG_PATHS[@]}"; do
        if [ -d "$path" ]; then
            echo -e "  ${GREEN}✅ 找到: $path${NC}"
            ls -la "$path" 2>/dev/null | head -5
            LOG_DIR="$path"
            break
        fi
    done
    
    if [ -z "$LOG_DIR" ]; then
        echo -e "  ${RED}❌ 未找到日志目录${NC}"
    fi
    
    echo ""
}

# 执行数据库查询检查
execute_query_check() {
    local query="$1"
    local description="$2"
    
    echo -n "  $description: "
    
    if [ -n "$CLICKHOUSE_PASSWORD" ]; then
        result=$(curl -s --user "$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD" \
            "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" \
            --data-urlencode "query=$query" 2>/dev/null)
    else
        result=$(curl -s "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" \
            --data-urlencode "query=$query" 2>/dev/null)
    fi
    
    if [[ $result == *"Exception"* ]]; then
        echo -e "${RED}❌ 失败${NC}"
        echo "    错误: $result"
        return 1
    else
        echo -e "${GREEN}✅ 成功${NC}"
        if [ -n "$result" ] && [ ${#result} -lt 100 ]; then
            echo "    结果: $result"
        fi
        return 0
    fi
}

# 检查数据库功能
check_database_functionality() {
    echo -e "${CYAN}🗄️  检查数据库功能${NC}"
    echo "----------------------------------------"
    
    # 基础查询测试
    execute_query_check "SELECT 1" "基础查询"
    execute_query_check "SELECT version()" "版本查询"
    execute_query_check "SELECT now()" "时间查询"
    execute_query_check "SHOW DATABASES" "列出数据库"
    execute_query_check "SELECT count() FROM system.tables" "系统表查询"
    
    # 创建测试
    execute_query_check "CREATE DATABASE IF NOT EXISTS test_check" "创建数据库"
    execute_query_check "CREATE TABLE IF NOT EXISTS test_check.test_table (id UInt32, name String) ENGINE = Memory" "创建表"
    execute_query_check "INSERT INTO test_check.test_table VALUES (1, 'test')" "插入数据"
    execute_query_check "SELECT * FROM test_check.test_table" "查询数据"
    execute_query_check "DROP TABLE test_check.test_table" "删除表"
    execute_query_check "DROP DATABASE test_check" "删除数据库"
    
    echo ""
}

# 检查系统配置
check_system_settings() {
    echo -e "${CYAN}⚙️  检查系统配置${NC}"
    echo "----------------------------------------"
    
    # 获取重要系统设置
    execute_query_check "
    SELECT name, value 
    FROM system.settings 
    WHERE name IN (
        'max_memory_usage',
        'max_threads',
        'max_execution_time',
        'max_result_rows',
        'distributed_aggregation_memory_efficient'
    )
    ORDER BY name
    " "系统设置检查"
    
    # 检查表引擎
    execute_query_check "SELECT name FROM system.table_engines ORDER BY name" "可用表引擎"
    
    # 检查函数
    execute_query_check "SELECT count() FROM system.functions" "可用函数数量"
    
    echo ""
}

# 检查性能指标
check_performance_metrics() {
    echo -e "${CYAN}📊 检查性能指标${NC}"
    echo "----------------------------------------"
    
    # 获取系统指标
    execute_query_check "
    SELECT 
        metric,
        value,
        description
    FROM system.metrics 
    WHERE metric IN (
        'Query',
        'SelectQuery', 
        'InsertQuery',
        'MemoryTracking',
        'BackgroundPoolTask'
    )
    ORDER BY metric
    " "系统性能指标"
    
    # 检查当前进程
    execute_query_check "SELECT count() FROM system.processes" "当前运行进程数"
    
    # 检查内存使用
    execute_query_check "
    SELECT 
        formatReadableSize(value) as memory_usage
    FROM system.metrics 
    WHERE metric = 'MemoryTracking'
    " "内存使用情况"
    
    echo ""
}

# 检查日志文件
check_log_files() {
    echo -e "${CYAN}📋 检查日志文件${NC}"
    echo "----------------------------------------"
    
    if [ -n "$LOG_DIR" ]; then
        # 检查主日志文件
        if [ -f "$LOG_DIR/clickhouse-server.log" ]; then
            echo "主日志文件:"
            echo "  路径: $LOG_DIR/clickhouse-server.log"
            echo "  大小: $(du -sh "$LOG_DIR/clickhouse-server.log" | cut -f1)"
            echo "  最后修改: $(stat -c %y "$LOG_DIR/clickhouse-server.log" 2>/dev/null || stat -f %Sm "$LOG_DIR/clickhouse-server.log" 2>/dev/null)"
            echo "  最新10行:"
            tail -10 "$LOG_DIR/clickhouse-server.log" | sed 's/^/    /'
        fi
        
        echo ""
        
        # 检查错误日志文件
        if [ -f "$LOG_DIR/clickhouse-server.err.log" ]; then
            echo "错误日志文件:"
            echo "  路径: $LOG_DIR/clickhouse-server.err.log"
            echo "  大小: $(du -sh "$LOG_DIR/clickhouse-server.err.log" | cut -f1)"
            if [ -s "$LOG_DIR/clickhouse-server.err.log" ]; then
                echo -e "  ${YELLOW}⚠️  包含错误信息${NC}"
                echo "  最新错误:"
                tail -5 "$LOG_DIR/clickhouse-server.err.log" | sed 's/^/    /'
            else
                echo -e "  ${GREEN}✅ 无错误信息${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  未找到日志目录，跳过日志检查${NC}"
    fi
    
    echo ""
}

# 生成检查报告
generate_report() {
    echo -e "${CYAN}📋 生成检查报告${NC}"
    echo "----------------------------------------"
    
    REPORT_FILE="clickhouse_check_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ClickHouse 配置检查报告"
        echo "======================"
        echo "检查时间: $(date)"
        echo "检查主机: $CLICKHOUSE_HOST:$CLICKHOUSE_PORT"
        echo "检查用户: $CLICKHOUSE_USER"
        echo ""
        echo "检查项目:"
        echo "- 服务状态检查"
        echo "- 连接测试"
        echo "- 系统资源检查"
        echo "- 配置文件检查"
        echo "- 数据目录检查"
        echo "- 数据库功能检查"
        echo "- 系统配置检查"
        echo "- 性能指标检查"
        echo "- 日志文件检查"
        echo ""
        echo "详细结果请查看控制台输出。"
        echo ""
        echo "建议:"
        echo "1. 定期检查日志文件中的错误信息"
        echo "2. 监控系统资源使用情况"
        echo "3. 及时更新ClickHouse版本"
        echo "4. 根据业务需求调整配置参数"
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}✅ 检查报告已保存到: $REPORT_FILE${NC}"
}

# 显示帮助信息
show_help() {
    echo "ClickHouse 配置检查脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --host HOST       ClickHouse服务器地址 (默认: localhost)"
    echo "  -p, --port PORT       ClickHouse端口 (默认: 8123)"
    echo "  -u, --user USER       用户名 (默认: default)"
    echo "  -P, --password PASS   密码"
    echo "  --report-only        只生成报告，不显示详细输出"
    echo "  --help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                                    # 检查本地ClickHouse"
    echo "  $0 -h clickhouse.example.com -u admin -P password123"
    echo "  $0 --report-only                     # 静默模式，只生成报告"
}

# 主函数
main() {
    local report_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host)
                CLICKHOUSE_HOST="$2"
                shift 2
                ;;
            -p|--port)
                CLICKHOUSE_PORT="$2"
                shift 2
                ;;
            -u|--user)
                CLICKHOUSE_USER="$2"
                shift 2
                ;;
            -P|--password)
                CLICKHOUSE_PASSWORD="$2"
                shift 2
                ;;
            --report-only)
                report_only=true
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
    
    # 执行检查流程
    if [ "$report_only" = false ]; then
        check_service_status
        check_connection
        check_system_resources
        check_config_files
        check_data_directories
        check_database_functionality
        check_system_settings
        check_performance_metrics
        check_log_files
    fi
    
    generate_report
    
    echo ""
    echo -e "${GREEN}🎉 配置检查完成！${NC}"
}

# 检查依赖
check_dependencies() {
    if ! command -v curl >/dev/null 2>&1; then
        echo -e "${RED}❌ 错误: 需要安装 curl${NC}"
        exit 1
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    main "$@"
fi 