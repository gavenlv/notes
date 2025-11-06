#!/bin/bash

# Airflow 安装脚本
# 此脚本将设置 Python 虚拟环境并安装 Airflow

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 版本
check_python() {
    print_info "检查 Python 版本..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_info "Python 版本检查通过: $PYTHON_VERSION"
    else
        print_error "Python 版本过低: $PYTHON_VERSION，需要 3.8 或更高版本"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    print_info "创建 Python 虚拟环境..."
    
    VENV_DIR="airflow-env"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "虚拟环境 $VENV_DIR 已存在，跳过创建"
    else
        python3 -m venv $VENV_DIR
        print_info "虚拟环境创建成功: $VENV_DIR"
    fi
    
    # 激活虚拟环境
    source $VENV_DIR/bin/activate
    print_info "虚拟环境已激活"
}

# 升级 pip
upgrade_pip() {
    print_info "升级 pip..."
    pip install --upgrade pip
}

# 安装 Airflow
install_airflow() {
    print_info "安装 Apache Airflow..."
    
    # 安装 Airflow
    pip install apache-airflow
    
    print_info "安装 Airflow 提供者包..."
    # 安装常用的提供者包
    pip install apache-airflow-providers-postgres
    pip install apache-airflow-providers-amazon
    pip install apache-airflow-providers-docker
    
    print_info "Airflow 安装完成"
}

# 设置 Airflow 主目录
setup_airflow_home() {
    print_info "设置 Airflow 主目录..."
    
    AIRFLOW_HOME_DIR="$HOME/airflow"
    
    if [ ! -d "$AIRFLOW_HOME_DIR" ]; then
        mkdir -p $AIRFLOW_HOME_DIR
        print_info "创建 Airflow 主目录: $AIRFLOW_HOME_DIR"
    else
        print_warning "Airflow 主目录已存在: $AIRFLOW_HOME_DIR"
    fi
    
    export AIRFLOW_HOME=$AIRFLOW_HOME_DIR
    echo "export AIRFLOW_HOME=$AIRFLOW_HOME_DIR" >> ~/.bashrc
    
    # 创建必要的子目录
    mkdir -p $AIRFLOW_HOME_DIR/dags
    mkdir -p $AIRFLOW_HOME_DIR/logs
    mkdir -p $AIRFLOW_HOME_DIR/plugins
    
    print_info "Airflow 目录结构创建完成"
}

# 初始化 Airflow 数据库
init_airflow_db() {
    print_info "初始化 Airflow 数据库..."
    
    airflow db init
    
    print_info "Airflow 数据库初始化完成"
}

# 创建管理员用户
create_admin_user() {
    print_info "创建 Airflow 管理员用户..."
    
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com
    
    print_info "管理员用户创建完成 (用户名: admin)"
}

# 显示完成信息
show_completion_info() {
    print_info "Airflow 安装完成！"
    echo ""
    print_info "下一步操作："
    echo "1. 激活虚拟环境: source airflow-env/bin/activate"
    echo "2. 启动 Airflow Web 服务器: airflow webserver --port 8080"
    echo "3. 在新终端启动调度器: airflow scheduler"
    echo "4. 访问 Web UI: http://localhost:8080"
    echo "5. 使用管理员账户登录 (用户名: admin)"
    echo ""
    print_info "或者使用 standalone 模式同时启动 Web 服务器和调度器："
    echo "airflow standalone"
}

# 主函数
main() {
    print_info "开始安装 Apache Airflow..."
    
    check_python
    create_venv
    upgrade_pip
    install_airflow
    setup_airflow_home
    init_airflow_db
    create_admin_user
    show_completion_info
    
    print_info "安装脚本执行完成！"
}

# 执行主函数
main "$@"