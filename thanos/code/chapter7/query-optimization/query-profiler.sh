#!/bin/bash

# Thanos查询性能分析工具
# 用于测试和优化Thanos查询性能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
QUERY_ENDPOINT="${THANOS_QUERY_ENDPOINT:-http://localhost:10902}"
TEST_COUNT="${TEST_COUNT:-10}"
WARMUP_COUNT="${WARMUP_COUNT:-3}"
OUTPUT_FILE="${OUTPUT_FILE:-query-profile-$(date +%Y%m%d-%H%M%S).csv}"

# 常用测试查询
QUERIES=(
    "up"
    "rate(http_requests_total[5m])"
    "sum(up) by (job)"
    "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
    "sum(rate(node_cpu_seconds_total{mode!=\"idle\"}[5m])) by (instance)"
    "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes"
)

# 显示帮助信息
show_help() {
    cat << EOF
Thanos查询性能分析工具

用法: $0 [选项]

选项:
    -e, --endpoint URL      Thanos Query端点 (默认: $QUERY_ENDPOINT)
    -c, --count NUM         测试次数 (默认: $TEST_COUNT)
    -w, --warmup NUM        预热次数 (默认: $WARMUP_COUNT)
    -o, --output FILE       输出文件 (默认: $OUTPUT_FILE)
    -q, --query QUERY       自定义查询语句
    -l, --list              列出预定义查询
    -h, --help              显示此帮助信息

示例:
    $0 -e http://thanos-query:10902 -c 20
    $0 -q 'rate(http_requests_total[5m])' -c 5
    $0 --list

环境变量:
    THANOS_QUERY_ENDPOINT   设置默认查询端点
    TEST_COUNT              设置默认测试次数
    WARMUP_COUNT            设置默认预热次数
    OUTPUT_FILE             设置默认输出文件
EOF
}

# 列出预定义查询
list_queries() {
    echo -e "${BLUE}预定义查询列表:${NC}"
    for i in "${!QUERIES[@]}"; do
        echo "  $((i+1)). ${QUERIES[$i]}"
    done
    echo
}

# 检查端点连通性
check_endpoint() {
    echo -e "${BLUE}检查Thanos Query端点连通性...${NC}"
    if curl -s "$QUERY_ENDPOINT/api/v1/query?query=up" | grep -q '"status":"success"'; then
        echo -e "${GREEN}✓ 端点连通性正常${NC}"
    else
        echo -e "${RED}✗ 无法连接到Thanos Query端点: $QUERY_ENDPOINT${NC}"
        exit 1
    fi
}

# 执行单个查询测试
run_query_test() {
    local query="$1"
    local test_num="$2"
    local total_tests="$3"
    
    echo -e "${YELLOW}[$test_num/$total_tests] 测试查询: ${query:0:60}...${NC}"
    
    # 执行查询并测量时间
    local start_time=$(date +%s%3N)
    local response=$(curl -s -w "%{http_code}" "$QUERY_ENDPOINT/api/v1/query?query=$(echo "$query" | sed 's/ /%20/g')")
    local end_time=$(date +%s%3N)
    local http_code="${response: -3}"
    local response_body="${response%???}"
    
    local duration=$((end_time - start_time))
    
    # 检查响应状态
    if [ "$http_code" = "200" ] && echo "$response_body" | grep -q '"status":"success"'; then
        echo -e "${GREEN}  成功 - 耗时: ${duration}ms${NC}"
        echo "$query,$duration,success,$(date -Iseconds)" >> "$OUTPUT_FILE"
    else
        echo -e "${RED}  失败 - HTTP代码: $http_code, 耗时: ${duration}ms${NC}"
        echo "$query,$duration,failed,$(date -Iseconds)" >> "$OUTPUT_FILE"
    fi
    
    return $duration
}

# 预热查询缓存
warmup_cache() {
    echo -e "${BLUE}预热查询缓存 ($WARMUP_COUNT 次)...${NC}"
    for ((i=1; i<=WARMUP_COUNT; i++)); do
        echo "预热第 $i 次..."
        for query in "${QUERIES[@]}"; do
            curl -s "$QUERY_ENDPOINT/api/v1/query?query=$(echo "$query" | sed 's/ /%20/g')" > /dev/null
        done
        sleep 1
    done
    echo -e "${GREEN}✓ 缓存预热完成${NC}"
}

# 执行性能测试
run_performance_test() {
    local test_queries=("$@")
    
    echo -e "${BLUE}开始性能测试...${NC}"
    echo "查询语句,耗时(ms),状态,时间戳" > "$OUTPUT_FILE"
    
    local total_duration=0
    local success_count=0
    local results=()
    
    for query in "${test_queries[@]}"; do
        local query_durations=()
        
        for ((i=1; i<=TEST_COUNT; i++)); do
            run_query_test "$query" "$i" "$TEST_COUNT"
            local duration=$?
            query_durations+=($duration)
            total_duration=$((total_duration + duration))
            
            if [ $duration -gt 0 ]; then
                ((success_count++))
            fi
            
            # 测试间隔
            sleep 0.5
        done
        
        # 计算统计信息
        local sorted=($(printf "%s\n" "${query_durations[@]}" | sort -n))
        local count=${#sorted[@]}
        local min=${sorted[0]}
        local max=${sorted[-1]}
        
        # 计算平均值
        local sum=0
        for d in "${sorted[@]}"; do
            sum=$((sum + d))
        done
        local avg=$((sum / count))
        
        # 计算中位数
        local mid=$((count / 2))
        if [ $((count % 2)) -eq 0 ]; then
            local median=$(( (sorted[mid-1] + sorted[mid]) / 2 ))
        else
            local median=${sorted[mid]}
        fi
        
        # 计算P95
        local p95_index=$((count * 95 / 100))
        local p95=${sorted[p95_index]}
        
        results+=("$query|$min|$max|$avg|$median|$p95")
        
        echo -e "${BLUE}  统计信息 - 最小值: ${min}ms, 最大值: ${max}ms, 平均值: ${avg}ms, 中位数: ${median}ms, P95: ${p95}ms${NC}"
        echo
    done
    
    # 输出汇总报告
    echo -e "${GREEN}性能测试完成${NC}"
    echo "========================================"
    echo -e "${BLUE}汇总报告:${NC}"
    echo "总测试次数: $((TEST_COUNT * ${#test_queries[@]}))"
    echo "成功次数: $success_count"
    echo "总耗时: ${total_duration}ms"
    echo "平均每次查询耗时: $((total_duration / success_count))ms"
    echo "输出文件: $OUTPUT_FILE"
    echo
    
    # 输出详细统计表
    echo -e "${BLUE}详细统计信息:${NC}"
    printf "%-60s %-8s %-8s %-8s %-8s %-8s\n" "查询语句" "最小值" "最大值" "平均值" "中位数" "P95"
    echo "========================================================================================================"
    
    for result in "${results[@]}"; do
        IFS='|' read -r query min max avg median p95 <<< "$result"
        printf "%-60s %-8s %-8s %-8s %-8s %-8s\n" "${query:0:58}.." "${min}ms" "${max}ms" "${avg}ms" "${median}ms" "${p95}ms"
    done
}

# 生成性能报告
generate_report() {
    echo -e "${BLUE}生成性能优化建议...${NC}"
    
    if [ -f "$OUTPUT_FILE" ]; then
        # 分析查询性能数据
        local slow_queries=$(awk -F, '$2 > 1000 {print $1 " - " $2 "ms"}' "$OUTPUT_FILE" | head -5)
        local avg_duration=$(awk -F, '$3=="success" {sum+=$2; count++} END {if(count>0) print sum/count}' "$OUTPUT_FILE")
        
        echo "========================================"
        echo -e "${YELLOW}性能优化建议:${NC}"
        echo
        
        if [ -n "$slow_queries" ]; then
            echo -e "${RED}需要优化的慢查询:${NC}"
            echo "$slow_queries"
            echo
            echo "优化建议:"
            echo "1. 检查查询语句是否使用了合适的标签过滤"
            echo "2. 优化时间范围设置，避免扫描过多数据"
            echo "3. 考虑使用预聚合规则减少实时计算"
            echo "4. 启用查询缓存和索引缓存"
            echo
        fi
        
        if [ $(echo "$avg_duration > 500" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
            echo -e "${YELLOW}平均查询延迟较高: ${avg_duration}ms${NC}"
            echo "优化建议:"
            echo "1. 增加Thanos Query组件的资源分配"
            echo "2. 优化Store组件的网络连接"
            echo "3. 检查对象存储的性能"
            echo "4. 考虑增加缓存层"
            echo
        else
            echo -e "${GREEN}查询性能良好，平均延迟: ${avg_duration}ms${NC}"
        fi
    fi
}

# 主函数
main() {
    local custom_query=""
    local list_queries_flag=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--endpoint)
                QUERY_ENDPOINT="$2"
                shift 2
                ;;
            -c|--count)
                TEST_COUNT="$2"
                shift 2
                ;;
            -w|--warmup)
                WARMUP_COUNT="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -q|--query)
                custom_query="$2"
                shift 2
                ;;
            -l|--list)
                list_queries_flag=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}未知参数: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [ "$list_queries_flag" = true ]; then
        list_queries
        exit 0
    fi
    
    # 检查端点连通性
    check_endpoint
    
    # 确定测试查询
    local test_queries=()
    if [ -n "$custom_query" ]; then
        test_queries=("$custom_query")
        echo -e "${BLUE}使用自定义查询: $custom_query${NC}"
    else
        test_queries=("${QUERIES[@]}")
        echo -e "${BLUE}使用预定义查询集 (${#QUERIES[@]}个查询)${NC}"
    fi
    
    # 预热缓存
    warmup_cache
    
    # 执行性能测试
    run_performance_test "${test_queries[@]}"
    
    # 生成报告
    generate_report
    
    echo -e "${GREEN}性能分析完成!${NC}"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi