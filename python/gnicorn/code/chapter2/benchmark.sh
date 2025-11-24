#!/bin/bash
# benchmark.sh
# 用于测试不同Worker类型性能的脚本

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
echo "Gunicorn Worker Type Performance Comparison" | tee -a "${RESULTS_FILE}"
echo "=============================================" | tee -a "${RESULTS_FILE}"

# 测试函数
run_benchmark() {
    local worker_type=$1
    local endpoint=$2
    local description=$3
    
    echo "" | tee -a "${RESULTS_FILE}"
    echo "Testing: ${worker_type} - ${description}" | tee -a "${RESULTS_FILE}"
    echo "Endpoint: ${endpoint}" | tee -a "${RESULTS_FILE}"
    echo "----------------------------------------" | tee -a "${RESULTS_FILE}"
    
    # 使用ab进行基准测试
    ab -n "${REQUESTS}" -c "${CONCURRENCY}" "${APP_URL}${endpoint}" | \
        grep -E "(Requests per second|Time per request|Failed requests)" | \
        tee -a "${RESULTS_FILE}"
}

# 等待Gunicorn启动
wait_for_server() {
    echo "Waiting for server to start..."
    until curl -s "${APP_URL}" > /dev/null; do
        sleep 1
    done
    echo "Server is up!"
}

# 检查依赖
if ! command -v ab &> /dev/null; then
    echo "Apache Bench (ab) is not installed. Please install it to run benchmarks."
    echo "On Ubuntu/Debian: sudo apt-get install apache2-utils"
    echo "On CentOS/RHEL: sudo yum install httpd-tools"
    echo "On macOS: brew install apache2"
    exit 1
fi

echo "This script will test different Gunicorn worker types."
echo "Please ensure you have Gunicorn installed and ready to test."
echo ""
echo "Press Enter to continue..."
read -r

# 测试sync worker
echo "Testing sync worker..."
echo "Please run: gunicorn -w 4 -k sync worker_comparison:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

run_benchmark "sync" "/" "Simple request"
run_benchmark "sync" "/cpu-intensive" "CPU intensive task"
run_benchmark "sync" "/io-intensive" "I/O intensive task"

# 停止sync worker
echo "Please stop the current Gunicorn process (Ctrl+C)"

# 测试gevent worker
echo ""
echo "Testing gevent worker..."
echo "Please run: gunicorn -w 4 -k gevent worker_comparison:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

run_benchmark "gevent" "/" "Simple request"
run_benchmark "gevent" "/cpu-intensive" "CPU intensive task"
run_benchmark "gevent" "/io-intensive" "I/O intensive task"

# 停止gevent worker
echo "Please stop the current Gunicorn process (Ctrl+C)"

# 测试异步应用
echo ""
echo "Testing async application with different workers..."
echo "First, test with sync worker:"
echo "Please run: gunicorn -w 4 -k sync async_app:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

run_benchmark "sync" "/" "Simple async app request"
run_benchmark "sync" "/simultaneous-requests" "Simultaneous requests"

# 停止sync worker
echo "Please stop the current Gunicorn process (Ctrl+C)"

echo ""
echo "Now, test with gevent worker:"
echo "Please run: gunicorn -w 4 -k gevent async_app:application"
echo "Then press Enter to continue..."
read -r
wait_for_server

run_benchmark "gevent" "/" "Simple async app request"
run_benchmark "gevent" "/simultaneous-requests" "Simultaneous requests"

echo ""
echo "Benchmark completed! Results saved to ${RESULTS_FILE}"
echo "You can analyze the results to compare different worker types."