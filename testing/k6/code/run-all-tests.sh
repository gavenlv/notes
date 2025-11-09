#!/bin/bash

# k6测试脚本 - 批量运行所有测试
# 作者：k6学习指南
# 描述：运行所有章节的测试脚本

echo "=== k6性能测试套件 ==="
echo "开始时间: $(date)"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查k6是否安装
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}错误: k6未安装，请先安装k6${NC}"
    echo "安装方法: https://k6.io/docs/getting-started/installation/"
    exit 1
fi

echo -e "${GREEN}✓ k6已安装，版本: $(k6 version)${NC}"
echo ""

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 运行测试函数
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo -e "${BLUE}▶ 运行测试: ${test_name}${NC}"
    echo "文件: ${test_file}"
    
    if [ ! -f "${test_file}" ]; then
        echo -e "${YELLOW}⚠ 测试文件不存在: ${test_file}${NC}"
        return 1
    fi
    
    # 运行测试（限制时间为2分钟，避免长时间运行）
    timeout 120s k6 run "${test_file}" --no-summary --no-usage-report
    local exit_code=$?
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ 测试通过: ${test_name}${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    elif [ $exit_code -eq 124 ]; then
        echo -e "${YELLOW}⚠ 测试超时: ${test_name} (2分钟限制)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    else
        echo -e "${RED}✗ 测试失败: ${test_name}${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
    return $exit_code
}

# 第1章测试
echo "=== 第1章：基础概念与环境搭建 ==="
run_test "chapter1/1-first-test.js" "第一个k6测试"
run_test "chapter1/experiment1-basic-validation.js" "基础环境验证实验"

# 第2章测试
echo "=== 第2章：脚本编写基础 ==="
run_test "chapter2/basic-script-structure.js" "脚本基本结构"
run_test "chapter2/http-requests.js" "HTTP请求示例"
run_test "chapter2/checks-and-validations.js" "检查点和验证"
run_test "chapter2/groups.js" "分组功能"
run_test "chapter2/experiment2-api-scenario.js" "完整API测试场景"

# 第3章测试
echo "=== 第3章：高级功能与性能测试 ==="
run_test "chapter3/custom-metrics.js" "自定义指标"
run_test "chapter3/scenarios-executors.js" "场景和执行器"

# 注意：以下测试文件可能运行时间较长，可根据需要取消注释
# run_test "chapter3/experiment3-ecommerce-scenario.js" "电商网站综合性能测试"

# 第4章测试
echo "=== 第4章：最佳实践与生产环境部署 ==="
# 生产环境测试需要特定配置，这里只运行基础测试
run_test "chapter4/production-framework.js" "生产级测试框架"

# 显示测试结果
echo "=== 测试结果汇总 ==="
echo "总测试数: ${TOTAL_TESTS}"
echo -e "${GREEN}通过: ${PASSED_TESTS}${NC}"
echo -e "${RED}失败: ${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
else
    echo -e "${YELLOW}⚠ 有 ${FAILED_TESTS} 个测试失败${NC}"
fi

echo ""
echo "结束时间: $(date)"

# 退出码
if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi