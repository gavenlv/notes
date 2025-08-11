#!/bin/bash

# 数据质量框架 v2.0 示例运行脚本
# 展示各种使用场景和功能

echo "数据质量框架 v2.0 示例演示"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 错误处理函数
error_exit() {
    echo -e "${RED}错误: $1${NC}" >&2
    exit 1
}

# 成功信息函数
success_msg() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 警告信息函数
warning_msg() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 信息函数
info_msg() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查Python和依赖
check_dependencies() {
    info_msg "检查运行环境..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        error_exit "Python3 未安装"
    fi
    
    # 检查依赖包
    python3 -c "import yaml" 2>/dev/null || error_exit "PyYAML 未安装，请运行: pip install PyYAML"
    
    success_msg "运行环境检查通过"
}

# 1. 显示帮助信息
show_help() {
    info_msg "显示帮助信息..."
    python3 data_quality_runner.py --help
    echo ""
}

# 2. 列出可用场景
list_scenarios() {
    info_msg "列出所有可用的测试场景..."
    python3 data_quality_runner.py --list-scenarios
    echo ""
}

# 3. 列出支持的数据库
list_databases() {
    info_msg "列出支持的数据库类型..."
    python3 data_quality_runner.py --list-databases
    echo ""
}

# 4. 验证配置文件
validate_config() {
    info_msg "验证配置文件..."
    if python3 data_quality_runner.py --validate-config; then
        success_msg "配置文件验证通过"
    else
        warning_msg "配置文件验证失败，请检查配置"
    fi
    echo ""
}

# 5. 测试数据库连接
test_connection() {
    info_msg "测试数据库连接..."
    if python3 data_quality_runner.py --test-connection; then
        success_msg "数据库连接测试通过"
    else
        warning_msg "数据库连接失败，请检查数据库配置和服务状态"
    fi
    echo ""
}

# 6. 运行ClickHouse冒烟测试
run_clickhouse_smoke_test() {
    info_msg "运行ClickHouse冒烟测试..."
    if python3 data_quality_runner.py --scenario clickhouse_smoke_test --log-level INFO; then
        success_msg "ClickHouse冒烟测试完成"
    else
        warning_msg "ClickHouse冒烟测试失败"
    fi
    echo ""
}

# 7. 运行多环境测试示例
run_multi_env_test() {
    info_msg "演示多环境测试..."
    
    # 开发环境
    info_msg "在开发环境运行测试..."
    python3 data_quality_runner.py --scenario clickhouse_smoke_test --env dev --log-level DEBUG
    
    # 测试环境
    info_msg "在测试环境运行测试..."
    python3 data_quality_runner.py --scenario clickhouse_smoke_test --env test
    
    echo ""
}

# 8. 生成不同格式的报告
generate_different_reports() {
    info_msg "生成不同格式的报告..."
    
    # HTML报告
    info_msg "生成HTML报告..."
    python3 data_quality_runner.py --scenario clickhouse_smoke_test --output-dir reports/html_demo/
    
    # 显示生成的报告文件
    if [ -d "reports/html_demo" ]; then
        success_msg "报告已生成到 reports/html_demo/ 目录"
        ls -la reports/html_demo/
    fi
    echo ""
}

# 9. 并行执行测试
run_parallel_test() {
    info_msg "演示并行执行测试（最大3个并行任务）..."
    python3 data_quality_runner.py --scenario clickhouse_smoke_test --max-workers 3
    echo ""
}

# 10. 自定义规则示例
run_custom_rules() {
    info_msg "运行自定义规则示例..."
    
    # 检查自定义规则文件是否存在
    if [ -f "examples/custom_rule_example.yml" ]; then
        info_msg "找到自定义规则文件，创建临时场景..."
        
        # 创建临时场景配置
        cat > /tmp/custom_scenario.yml << EOF
name: "custom_example"
description: "自定义规则示例"
database:
  type: "clickhouse"
  host: "localhost"
  port: 9000
  database: "data_quality_test"
  user: "admin"
  password: "admin"
rules:
  paths:
    - "examples/"
execution:
  max_parallel_jobs: 2
report:
  formats: ["html", "json"]
  output_dir: "reports/custom_example/"
EOF
        
        # 注意：这需要修改框架以支持临时场景文件
        warning_msg "自定义规则示例需要实际的数据库和表结构"
    else
        warning_msg "自定义规则示例文件不存在"
    fi
    echo ""
}

# 11. 演示错误处理
demo_error_handling() {
    info_msg "演示错误处理..."
    
    # 使用错误的数据库配置
    info_msg "测试数据库连接错误处理..."
    python3 data_quality_runner.py --test-connection --env nonexistent 2>/dev/null || warning_msg "预期的连接错误"
    
    # 使用不存在的场景
    info_msg "测试场景不存在错误处理..."
    python3 data_quality_runner.py --scenario nonexistent_scenario 2>/dev/null || warning_msg "预期的场景错误"
    
    echo ""
}

# 12. 查看生成的报告
view_reports() {
    info_msg "查看生成的报告文件..."
    
    if [ -d "reports" ]; then
        echo "报告目录结构:"
        find reports -name "*.html" -o -name "*.json" -o -name "*.txt" | head -10
        
        # 如果有HTML报告，提示如何查看
        if find reports -name "*.html" | head -1 > /dev/null; then
            success_msg "HTML报告已生成，可以用浏览器打开查看"
            info_msg "例如: firefox $(find reports -name "*.html" | head -1)"
        fi
    else
        warning_msg "没有找到报告目录"
    fi
    echo ""
}

# 13. 清理示例文件
cleanup() {
    info_msg "清理临时文件..."
    
    # 清理临时场景文件
    rm -f /tmp/custom_scenario.yml
    
    # 可选：清理示例报告
    read -p "是否清理示例报告文件？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf reports/html_demo/
        rm -rf reports/custom_example/
        success_msg "示例报告文件已清理"
    fi
    echo ""
}

# 主菜单函数
show_menu() {
    echo ""
    echo "请选择要运行的示例:"
    echo "1)  显示帮助信息"
    echo "2)  列出可用场景"
    echo "3)  列出支持的数据库"
    echo "4)  验证配置文件"
    echo "5)  测试数据库连接"
    echo "6)  运行ClickHouse冒烟测试"
    echo "7)  多环境测试示例"
    echo "8)  生成不同格式报告"
    echo "9)  并行执行测试"
    echo "10) 自定义规则示例"
    echo "11) 错误处理演示"
    echo "12) 查看生成的报告"
    echo "13) 清理临时文件"
    echo "0)  运行所有示例"
    echo "q)  退出"
    echo ""
}

# 运行所有示例
run_all_examples() {
    info_msg "运行所有示例..."
    
    check_dependencies
    show_help
    list_scenarios
    list_databases
    validate_config
    test_connection
    run_clickhouse_smoke_test
    run_multi_env_test
    generate_different_reports
    run_parallel_test
    run_custom_rules
    demo_error_handling
    view_reports
    
    success_msg "所有示例运行完成！"
}

# 主程序
main() {
    # 检查是否提供了命令行参数
    if [ $# -gt 0 ]; then
        case $1 in
            "all")
                run_all_examples
                ;;
            "help")
                show_help
                ;;
            "test")
                check_dependencies
                validate_config
                test_connection
                ;;
            *)
                echo "用法: $0 [all|help|test]"
                echo "  all  - 运行所有示例"
                echo "  help - 显示帮助"
                echo "  test - 快速测试"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # 交互式菜单
    while true; do
        show_menu
        read -p "请输入选择 [1-13/0/q]: " choice
        
        case $choice in
            1) show_help ;;
            2) list_scenarios ;;
            3) list_databases ;;
            4) validate_config ;;
            5) test_connection ;;
            6) run_clickhouse_smoke_test ;;
            7) run_multi_env_test ;;
            8) generate_different_reports ;;
            9) run_parallel_test ;;
            10) run_custom_rules ;;
            11) demo_error_handling ;;
            12) view_reports ;;
            13) cleanup ;;
            0) run_all_examples ;;
            q|Q) 
                info_msg "退出示例程序"
                exit 0
                ;;
            *)
                warning_msg "无效选择，请重新输入"
                ;;
        esac
        
        # 等待用户按键继续
        echo ""
        read -p "按回车键继续..." -r
    done
}

# 设置脚本目录为工作目录
cd "$(dirname "$0")"

# 运行主程序
main "$@"

