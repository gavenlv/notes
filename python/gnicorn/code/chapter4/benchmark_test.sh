#!/bin/bash
# benchmark_test.sh
# 用于测试Gunicorn性能的脚本

set -e

APP_HOST="localhost"
APP_PORT="8000"
APP_URL="http://${APP_HOST}:${APP_PORT}"
RESULTS_FILE="benchmark_results.txt"

# 测试参数
REQUESTS=1000
CONCURRENCY=10

# 清空结果文件
> "${RESULTS_FILE}"
echo "Gunicorn Performance Test Results" | tee -a "${RESULTS_FILE}"
echo "=================================" | tee -a "${RESULTS_FILE}"
echo "Date: $(date)" | tee -a "${RESULTS_FILE}"
echo "" | tee -a "${RESULTS_FILE}"

# 测试函数
run_benchmark() {
    local endpoint=$1
    local description=$2
    
    echo "" | tee -a "${RESULTS_FILE}"
    echo "Testing: ${description}" | tee -a "${RESULTS_FILE}"
    echo "Endpoint: ${endpoint}" | tee -a "${RESULTS_FILE}"
    echo "----------------------------------------" | tee -a "${RESULTS_FILE}"
    
    # 使用ab进行基准测试
    ab -n "${REQUESTS}" -c "${CONCURRENCY}" "${APP_URL}${endpoint}" | \
        grep -E "(Requests per second|Time per request|Failed requests|Complete requests)" | \
        tee -a "${RESULTS_FILE}"
}

# 检查依赖
if ! command -v ab &> /dev/null; then
    echo "Apache Bench (ab) is not installed. Please install it to run benchmarks."
    exit 1
fi

# 等待Gunicorn启动
wait_for_server() {
    echo "Waiting for server to start..."
    until curl -s "${APP_URL}" > /dev/null; do
        sleep 1
    done
    echo "Server is up!"
}

echo "This script will test Gunicorn performance with different worker types and configurations."
echo ""

echo "Testing sync workers..."
echo "Please run: gunicorn -w 4 -k sync performance_app:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

run_benchmark "/" "Simple request"
run_benchmark "/cpu-intensive" "CPU intensive task"
run_benchmark "/io-intensive" "I/O intensive task"
run_benchmark "/mixed" "Mixed task"

# 停止sync worker
echo "Please stop the current Gunicorn process (Ctrl+C)"

# 测试gevent worker
echo ""
echo "Testing gevent workers..."
echo "Please run: gunicorn -w 4 -k gevent performance_app:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

run_benchmark "/" "Simple request"
run_benchmark "/cpu-intensive" "CPU intensive task"
run_benchmark "/io-intensive" "I/O intensive task"
run_benchmark "/mixed" "Mixed task"

# 停止gevent worker
echo "Please stop the current Gunicorn process (Ctrl+C)"

# 测试缓存效果
echo ""
echo "Testing caching effect..."
echo "Please run: gunicorn -w 4 -k sync performance_app:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

echo "" | tee -a "${RESULTS_FILE}"
echo "Testing: Caching effect (first request)" | tee -a "${RESULTS_FILE}"
echo "Endpoint: /cached-data" | tee -a "${RESULTS_FILE}"
echo "----------------------------------------" | tee -a "${RESULTS_FILE}"
time curl -s "${APP_URL}/cached-data" > /dev/null

echo "" | tee -a "${RESULTS_FILE}"
echo "Testing: Caching effect (cached request)" | tee -a "${RESULTS_FILE}"
echo "Endpoint: /cached-data" | tee -a "${RESULTS_FILE}"
echo "----------------------------------------" | tee -a "${RESULTS_FILE}"
time curl -s "${APP_URL}/cached-data" > /dev/null

# 停止worker
echo "Please stop the current Gunicorn process (Ctrl+C)"

echo ""
echo "Benchmark completed! Results saved to ${RESULTS_FILE}"
echo "You can analyze results to compare different worker types and configurations."