#!/bin/bash

# ClickHouse 性能基准测试脚本
# 作者: ClickHouse学习教程
# 版本: 1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置参数
CLICKHOUSE_HOST=${CLICKHOUSE_HOST:-localhost}
CLICKHOUSE_PORT=${CLICKHOUSE_PORT:-8123}
CLICKHOUSE_USER=${CLICKHOUSE_USER:-default}
CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD:-}
DATABASE_NAME="benchmark_test"

# 测试数据量
SMALL_DATASET=100000      # 10万条
MEDIUM_DATASET=1000000    # 100万条
LARGE_DATASET=10000000    # 1000万条

echo -e "${BLUE}🚀 ClickHouse 性能基准测试${NC}"
echo "================================================"

# 检查ClickHouse连接
check_connection() {
    echo "🔍 检查ClickHouse连接..."
    
    if [ -n "$CLICKHOUSE_PASSWORD" ]; then
        AUTH_PARAM="--user $CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD"
    else
        AUTH_PARAM=""
    fi
    
    if ! curl -s $AUTH_PARAM "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" --data-urlencode 'query=SELECT 1' >/dev/null; then
        echo -e "${RED}❌ 无法连接到ClickHouse服务器${NC}"
        echo "请检查服务器是否运行在 $CLICKHOUSE_HOST:$CLICKHOUSE_PORT"
        exit 1
    fi
    
    VERSION=$(curl -s $AUTH_PARAM "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" --data-urlencode 'query=SELECT version()')
    echo -e "${GREEN}✅ 连接成功！ClickHouse版本: $VERSION${NC}"
}

# 执行SQL查询并计时
execute_query() {
    local query="$1"
    local description="$2"
    
    echo -n "执行: $description ... "
    
    start_time=$(date +%s.%N)
    
    if [ -n "$CLICKHOUSE_PASSWORD" ]; then
        result=$(curl -s --user "$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD" \
            "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" \
            --data-urlencode "query=$query" 2>/dev/null)
    else
        result=$(curl -s "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" \
            --data-urlencode "query=$query" 2>/dev/null)
    fi
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    if [[ $result == *"Exception"* ]]; then
        echo -e "${RED}失败${NC}"
        echo "错误: $result"
        return 1
    else
        printf "${GREEN}%.3f秒${NC}\n" "$duration"
        return 0
    fi
}

# 创建测试数据库和表
setup_test_environment() {
    echo "🏗️  设置测试环境..."
    
    # 创建数据库
    execute_query "DROP DATABASE IF EXISTS $DATABASE_NAME" "删除旧测试数据库"
    execute_query "CREATE DATABASE $DATABASE_NAME" "创建测试数据库"
    
    # 创建不同类型的测试表
    
    # 1. 基础性能测试表
    execute_query "
    CREATE TABLE $DATABASE_NAME.performance_test (
        id UInt64,
        timestamp DateTime,
        user_id UInt32,
        event_type String,
        value Float64,
        category FixedString(10),
        properties String,
        created_date Date DEFAULT toDate(timestamp)
    ) ENGINE = MergeTree()
    ORDER BY (created_date, user_id, id)
    " "创建性能测试表"
    
    # 2. 时间序列测试表
    execute_query "
    CREATE TABLE $DATABASE_NAME.timeseries_test (
        timestamp DateTime64(3),
        metric_name String,
        value Float64,
        tags Map(String, String),
        host String
    ) ENGINE = MergeTree()
    ORDER BY (metric_name, timestamp)
    " "创建时间序列测试表"
    
    # 3. 日志分析测试表
    execute_query "
    CREATE TABLE $DATABASE_NAME.logs_test (
        timestamp DateTime,
        level Enum8('DEBUG'=1, 'INFO'=2, 'WARN'=3, 'ERROR'=4),
        message String,
        source String,
        user_id Nullable(UInt32),
        session_id String,
        ip IPv4,
        user_agent String
    ) ENGINE = MergeTree()
    ORDER BY (timestamp, level)
    " "创建日志分析测试表"
    
    # 4. 分析型测试表 (宽表)
    execute_query "
    CREATE TABLE $DATABASE_NAME.analytics_test (
        event_time DateTime,
        user_id UInt64,
        session_id String,
        page_url String,
        referrer String,
        utm_source String,
        utm_medium String,
        utm_campaign String,
        device_type Enum8('desktop'=1, 'mobile'=2, 'tablet'=3),
        browser String,
        os String,
        country String,
        region String,
        city String,
        duration UInt32,
        bounce Boolean,
        conversion Boolean,
        revenue Decimal(10,2)
    ) ENGINE = MergeTree()
    ORDER BY (event_time, user_id)
    SAMPLE BY user_id
    " "创建分析型测试表"
    
    echo -e "${GREEN}✅ 测试环境设置完成${NC}"
}

# 生成测试数据
generate_test_data() {
    echo "📊 生成测试数据..."
    
    # 1. 基础性能测试数据
    echo "生成基础性能测试数据 ($MEDIUM_DATASET 条)..."
    execute_query "
    INSERT INTO $DATABASE_NAME.performance_test
    SELECT 
        number as id,
        now() - number as timestamp,
        number % 100000 as user_id,
        ['login', 'logout', 'view', 'click', 'purchase'][number % 5 + 1] as event_type,
        rand() / 1000000000.0 as value,
        ['category_' || toString(number % 10)] as category,
        '{\"key1\":\"value1\",\"key2\":' || toString(number % 100) || '}' as properties
    FROM numbers($MEDIUM_DATASET)
    " "插入基础性能测试数据"
    
    # 2. 时间序列测试数据
    echo "生成时间序列测试数据 ($MEDIUM_DATASET 条)..."
    execute_query "
    INSERT INTO $DATABASE_NAME.timeseries_test
    SELECT 
        now() - number/1000 as timestamp,
        ['cpu_usage', 'memory_usage', 'disk_io', 'network_io'][number % 4 + 1] as metric_name,
        rand() % 100 as value,
        map('host', 'server-' || toString(number % 10), 'env', 'prod') as tags,
        'server-' || toString(number % 10) as host
    FROM numbers($MEDIUM_DATASET)
    " "插入时间序列测试数据"
    
    # 3. 日志分析测试数据
    echo "生成日志分析测试数据 ($MEDIUM_DATASET 条)..."
    execute_query "
    INSERT INTO $DATABASE_NAME.logs_test
    SELECT 
        now() - number as timestamp,
        ['DEBUG', 'INFO', 'WARN', 'ERROR'][number % 4 + 1] as level,
        'Log message ' || toString(number) as message,
        ['app', 'database', 'cache', 'api'][number % 4 + 1] as source,
        if(number % 10 = 0, NULL, number % 100000) as user_id,
        'session-' || toString(number % 10000) as session_id,
        toIPv4(rand() % 4294967295) as ip,
        'Mozilla/5.0 User Agent ' || toString(number % 100) as user_agent
    FROM numbers($MEDIUM_DATASET)
    " "插入日志分析测试数据"
    
    # 4. 分析型测试数据
    echo "生成分析型测试数据 ($MEDIUM_DATASET 条)..."
    execute_query "
    INSERT INTO $DATABASE_NAME.analytics_test
    SELECT 
        now() - number as event_time,
        number % 50000 as user_id,
        'session-' || toString(number % 10000) as session_id,
        'https://example.com/page/' || toString(number % 1000) as page_url,
        if(number % 3 = 0, '', 'https://google.com') as referrer,
        ['google', 'facebook', 'twitter', 'direct'][number % 4 + 1] as utm_source,
        ['cpc', 'social', 'email', 'organic'][number % 4 + 1] as utm_medium,
        'campaign-' || toString(number % 10) as utm_campaign,
        ['desktop', 'mobile', 'tablet'][number % 3 + 1] as device_type,
        ['Chrome', 'Firefox', 'Safari', 'Edge'][number % 4 + 1] as browser,
        ['Windows', 'macOS', 'Linux', 'iOS', 'Android'][number % 5 + 1] as os,
        ['China', 'USA', 'Germany', 'Japan', 'UK'][number % 5 + 1] as country,
        ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'][number % 4 + 1] as region,
        'City-' || toString(number % 100) as city,
        number % 3600 as duration,
        number % 10 = 0 as bounce,
        number % 50 = 0 as conversion,
        if(number % 50 = 0, (number % 1000) / 10.0, 0) as revenue
    FROM numbers($MEDIUM_DATASET)
    " "插入分析型测试数据"
    
    echo -e "${GREEN}✅ 测试数据生成完成${NC}"
}

# 执行基准测试
run_benchmarks() {
    echo "🏃 执行基准测试..."
    echo "================================================"
    
    # 1. 基础查询性能测试
    echo -e "${YELLOW}📈 基础查询性能测试${NC}"
    echo "----------------------------------------"
    
    execute_query "SELECT COUNT(*) FROM $DATABASE_NAME.performance_test" "统计总行数"
    execute_query "SELECT DISTINCT event_type FROM $DATABASE_NAME.performance_test" "查询唯一值"
    execute_query "SELECT user_id, COUNT(*) FROM $DATABASE_NAME.performance_test GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 10" "分组聚合查询"
    execute_query "SELECT * FROM $DATABASE_NAME.performance_test WHERE user_id = 12345 ORDER BY timestamp DESC LIMIT 100" "条件查询"
    execute_query "SELECT event_type, AVG(value), MIN(value), MAX(value) FROM $DATABASE_NAME.performance_test GROUP BY event_type" "聚合函数测试"
    
    # 2. 时间序列查询测试
    echo -e "${YELLOW}📊 时间序列查询测试${NC}"
    echo "----------------------------------------"
    
    execute_query "SELECT metric_name, AVG(value) FROM $DATABASE_NAME.timeseries_test WHERE timestamp >= now() - INTERVAL 1 HOUR GROUP BY metric_name" "时间范围聚合"
    execute_query "SELECT toStartOfMinute(timestamp) as minute, metric_name, AVG(value) FROM $DATABASE_NAME.timeseries_test GROUP BY minute, metric_name ORDER BY minute DESC LIMIT 100" "时间窗口聚合"
    execute_query "SELECT host, MAX(value) as max_value FROM $DATABASE_NAME.timeseries_test WHERE metric_name = 'cpu_usage' GROUP BY host ORDER BY max_value DESC" "主机维度分析"
    
    # 3. 日志分析测试
    echo -e "${YELLOW}📝 日志分析测试${NC}"
    echo "----------------------------------------"
    
    execute_query "SELECT level, COUNT(*) FROM $DATABASE_NAME.logs_test GROUP BY level ORDER BY COUNT(*) DESC" "日志级别统计"
    execute_query "SELECT source, COUNT(*) as cnt FROM $DATABASE_NAME.logs_test WHERE level = 'ERROR' GROUP BY source ORDER BY cnt DESC LIMIT 10" "错误日志分析"
    execute_query "SELECT toStartOfHour(timestamp) as hour, COUNT(*) FROM $DATABASE_NAME.logs_test WHERE timestamp >= now() - INTERVAL 24 HOUR GROUP BY hour ORDER BY hour" "按小时统计日志"
    execute_query "SELECT user_id, COUNT(*) FROM $DATABASE_NAME.logs_test WHERE user_id IS NOT NULL GROUP BY user_id HAVING COUNT(*) > 100 ORDER BY COUNT(*) DESC LIMIT 20" "活跃用户分析"
    
    # 4. 复杂分析查询测试
    echo -e "${YELLOW}🔍 复杂分析查询测试${NC}"
    echo "----------------------------------------"
    
    execute_query "SELECT utm_source, COUNT(*) as visits, SUM(revenue) as total_revenue FROM $DATABASE_NAME.analytics_test GROUP BY utm_source ORDER BY total_revenue DESC" "渠道分析"
    execute_query "SELECT device_type, COUNT(*) as sessions, AVG(duration) as avg_duration, SUM(conversion) as conversions FROM $DATABASE_NAME.analytics_test GROUP BY device_type" "设备类型分析"
    execute_query "SELECT country, COUNT(DISTINCT user_id) as unique_users, SUM(revenue) as revenue FROM $DATABASE_NAME.analytics_test GROUP BY country ORDER BY unique_users DESC LIMIT 10" "地理位置分析"
    execute_query "
    SELECT 
        toStartOfHour(event_time) as hour,
        COUNT(*) as page_views,
        COUNT(DISTINCT user_id) as unique_users,
        SUM(bounce) as bounces,
        SUM(conversion) as conversions,
        SUM(revenue) as revenue
    FROM $DATABASE_NAME.analytics_test 
    WHERE event_time >= now() - INTERVAL 24 HOUR 
    GROUP BY hour 
    ORDER BY hour DESC
    " "综合时间维度分析"
    
    # 5. JOIN查询测试
    echo -e "${YELLOW}🔗 JOIN查询测试${NC}"
    echo "----------------------------------------"
    
    execute_query "
    SELECT 
        p.event_type,
        COUNT(*) as event_count,
        AVG(a.duration) as avg_duration
    FROM $DATABASE_NAME.performance_test p
    JOIN $DATABASE_NAME.analytics_test a ON p.user_id = a.user_id
    WHERE p.timestamp >= now() - INTERVAL 1 HOUR
    GROUP BY p.event_type
    ORDER BY event_count DESC
    " "表关联查询"
    
    # 6. 窗口函数测试
    echo -e "${YELLOW}🪟 窗口函数测试${NC}"
    echo "----------------------------------------"
    
    execute_query "
    SELECT 
        user_id,
        event_time,
        revenue,
        SUM(revenue) OVER (PARTITION BY user_id ORDER BY event_time) as cumulative_revenue,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY revenue DESC) as revenue_rank
    FROM $DATABASE_NAME.analytics_test 
    WHERE revenue > 0 
    ORDER BY user_id, event_time 
    LIMIT 1000
    " "窗口函数性能"
}

# 系统性能监控
monitor_system_performance() {
    echo -e "${YELLOW}💻 系统性能监控${NC}"
    echo "----------------------------------------"
    
    # 获取系统指标
    execute_query "
    SELECT 
        metric,
        value,
        description
    FROM system.metrics 
    WHERE metric IN (
        'Query', 'SelectQuery', 'InsertQuery',
        'MemoryTracking', 'BackgroundPoolTask',
        'TCPConnection', 'HTTPConnection'
    )
    ORDER BY metric
    " "系统指标监控"
    
    # 查看当前运行的查询
    execute_query "
    SELECT 
        query_id,
        user,
        elapsed,
        memory_usage,
        query
    FROM system.processes 
    WHERE query != ''
    " "当前运行查询"
    
    # 查看表的统计信息
    execute_query "
    SELECT 
        database,
        table,
        formatReadableSize(total_bytes) as size,
        formatReadableQuantity(total_rows) as rows,
        total_parts as parts
    FROM system.parts 
    WHERE database = '$DATABASE_NAME'
    ORDER BY total_bytes DESC
    " "表统计信息"
}

# 生成测试报告
generate_report() {
    echo ""
    echo "📋 生成测试报告..."
    
    REPORT_FILE="benchmark_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "ClickHouse 性能基准测试报告"
        echo "=========================="
        echo "测试时间: $(date)"
        echo "ClickHouse版本: $(curl -s "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/" --data-urlencode 'query=SELECT version()')"
        echo "测试数据库: $DATABASE_NAME"
        echo "测试数据量: $MEDIUM_DATASET 条记录"
        echo ""
        echo "测试完成！详细结果请查看控制台输出。"
    } > "$REPORT_FILE"
    
    echo -e "${GREEN}✅ 测试报告已保存到: $REPORT_FILE${NC}"
}

# 清理测试环境
cleanup() {
    echo "🧹 清理测试环境..."
    execute_query "DROP DATABASE IF EXISTS $DATABASE_NAME" "删除测试数据库"
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 显示帮助信息
show_help() {
    echo "ClickHouse 性能基准测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --host HOST       ClickHouse服务器地址 (默认: localhost)"
    echo "  -p, --port PORT       ClickHouse端口 (默认: 8123)"
    echo "  -u, --user USER       用户名 (默认: default)"
    echo "  -P, --password PASS   密码"
    echo "  -d, --database DB     测试数据库名 (默认: benchmark_test)"
    echo "  -s, --size SIZE       数据集大小 [small|medium|large] (默认: medium)"
    echo "  --no-cleanup         测试完成后不清理数据"
    echo "  --help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                                    # 使用默认配置"
    echo "  $0 -h clickhouse.example.com -u admin -P password123"
    echo "  $0 --size large --no-cleanup"
}

# 主函数
main() {
    local no_cleanup=false
    
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
            -d|--database)
                DATABASE_NAME="$2"
                shift 2
                ;;
            -s|--size)
                case $2 in
                    small)  MEDIUM_DATASET=$SMALL_DATASET ;;
                    medium) MEDIUM_DATASET=$MEDIUM_DATASET ;;
                    large)  MEDIUM_DATASET=$LARGE_DATASET ;;
                    *) echo -e "${RED}错误: 无效的数据集大小 '$2'${NC}"; exit 1 ;;
                esac
                shift 2
                ;;
            --no-cleanup)
                no_cleanup=true
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
    
    # 执行测试流程
    check_connection
    setup_test_environment
    generate_test_data
    run_benchmarks
    monitor_system_performance
    generate_report
    
    if [ "$no_cleanup" = false ]; then
        cleanup
    else
        echo -e "${YELLOW}⚠️  测试数据保留在数据库 '$DATABASE_NAME' 中${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 基准测试完成！${NC}"
}

# 检查依赖
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ 错误: 需要安装 curl${NC}"
        exit 1
    fi
    
    if ! command -v bc &> /dev/null; then
        echo -e "${RED}❌ 错误: 需要安装 bc (用于计算)${NC}"
        exit 1
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    main "$@"
fi 